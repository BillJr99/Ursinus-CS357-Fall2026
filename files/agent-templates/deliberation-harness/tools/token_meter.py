#!/usr/bin/env python3
"""Measure what a request actually cost, instead of estimating it.

Everything else in this course that talks about token cost reads a number off a
table.  This module reads it off the response.  Ollama returns
``prompt_eval_count`` and ``eval_count`` on every non-streaming call, to both
``/api/generate`` and ``/api/chat``, so the measurement is free, local, and
available to anyone who has the core lab running.

Three steps, in the order you use them:

    usage  = read_usage(response_json)         # tokens, measured
    carbon = grams_co2e(usage, profile)        # grams CO2eq, operational + training
    human  = equivalents(carbon["total"], cfg) # car miles, burgers, streaming hours

The second step is where the additive training term lives.  A request does not
only cost the energy to serve it; it also carries a share of the one-time cost
of training the model that serves it:

    total = operational + training_share

    operational   = in_tokens * g_per_in + out_tokens * g_per_out
    training_share = training_total_gco2e / assumed_lifetime_requests

That denominator is an assumption and the code says so at every opportunity,
because the term moves by orders of magnitude with it.  For the offline profile
in the shipped config it is large enough that a local request's training share
exceeds its operational cost, which is worth sitting with before you call local
inference free.

Nothing that matters is hardcoded here.  Every rate, total, denominator, and
anchor lives in ``config/energy-profiles.json``.
"""

import json
import logging
import traceback
from pathlib import Path

LOG = logging.getLogger("token_meter")

DEFAULT_CONFIG = Path(__file__).resolve().parent.parent / "config" / "energy-profiles.json"


# --------------------------------------------------------------------------- #
# Config
# --------------------------------------------------------------------------- #

def load_config(path=None):
    """Read energy-profiles.json and set the log level it asks for.

    Returns the parsed config, or None if it could not be read. A caller that
    gets None should say so rather than silently falling back to invented
    constants; there are no constants in this file to fall back to.
    """
    path = Path(path) if path else DEFAULT_CONFIG
    try:
        with open(path, encoding="utf-8") as fh:
            cfg = json.load(fh)
        level = (cfg.get("logging") or {}).get("level", "INFO")
        logging.basicConfig(level=getattr(logging, str(level).upper(), logging.INFO))
        LOG.debug("loaded %s", path)
        return cfg
    except Exception as e:                                          # noqa: BLE001
        print(f"[token_meter:load_config] {e}")
        traceback.print_exc()
        return None


# --------------------------------------------------------------------------- #
# Step 1: the measurement
# --------------------------------------------------------------------------- #

def read_usage(response_json, prompt_text=None, completion_text=None):
    """Pull measured token counts out of an Ollama response.

    ``prompt_eval_count`` is the input side and ``eval_count`` is the output
    side.  When they are absent (a streaming response, a different provider, a
    request that errored) this falls back to counting with ``tiktoken`` and
    sets ``measured`` to False.

    The ``measured`` flag is the important field.  A tiktoken count is an
    estimate made with the wrong tokenizer: ``cl100k_base`` is OpenAI's, not the
    one your local model uses, so the two agree to within a few percent on
    ordinary English and diverge on code, rare words, and anything non-Latin.
    An estimate reported as a measurement is the failure mode this flag exists
    to prevent, so carry it through to your writeup and say which rows were
    measured.
    """
    usage = {"input_tokens": 0, "output_tokens": 0, "measured": False, "source": "none"}
    try:
        if isinstance(response_json, dict):
            in_tok = response_json.get("prompt_eval_count")
            out_tok = response_json.get("eval_count")
            if in_tok is not None or out_tok is not None:
                usage.update(input_tokens=int(in_tok or 0),
                             output_tokens=int(out_tok or 0),
                             measured=True, source="ollama")
                LOG.debug("measured %d in / %d out", usage["input_tokens"], usage["output_tokens"])
                return usage

        LOG.warning("no usage counters in the response; estimating instead")
        in_tok, method = _estimate_tokens(prompt_text)
        out_tok, _ = _estimate_tokens(completion_text)
        usage.update(input_tokens=in_tok, output_tokens=out_tok,
                     measured=False, source=method)
        return usage
    except Exception as e:                                          # noqa: BLE001
        print(f"[token_meter:read_usage] {e}")
        traceback.print_exc()
        return usage


_TIKTOKEN_WARNED = False


def _estimate_tokens(text):
    """Count tokens with tiktoken, or fall back to the four-characters rule.

    Returns ``(count, method)``. The method name travels all the way into the
    report, because "estimated with tiktoken" and "estimated by dividing the
    character count by four" are not the same claim and should not print the
    same way. The four-characters-per-token rule is the one the Tokens,
    Embeddings, and Attention activity uses; it is a rule of thumb and the
    least reliable number this module can produce, which is why it is last.
    """
    global _TIKTOKEN_WARNED
    if not text:
        return 0, "empty"
    try:
        import tiktoken
        return len(tiktoken.get_encoding("cl100k_base").encode(text)), "tiktoken"
    except Exception as e:                                          # noqa: BLE001
        if not _TIKTOKEN_WARNED:
            # Once per process. A missing optional dependency is worth saying
            # loudly the first time and not on every call thereafter.
            print(f"[token_meter:_estimate_tokens] {e}")
            traceback.print_exc()
            LOG.warning("tiktoken unavailable; using the four-characters-per-token rule. "
                        "pip install tiktoken for a closer estimate.")
            _TIKTOKEN_WARNED = True
        return len(text) // 4, "chars/4"


# --------------------------------------------------------------------------- #
# Step 2: tokens to grams, operational plus the additive training term
# --------------------------------------------------------------------------- #

def grams_co2e(usage, profile_name="offline", config=None, lifetime_requests=None):
    """Convert measured tokens into grams of CO2eq for one request.

    Returns the two terms separately as well as their sum, because the whole
    point of the training term is that you can see how big it is next to the
    operational one. ``lifetime_requests`` overrides the config's denominator so
    you can rerun the same measurement under your own assumption and report both.
    """
    result = {"operational": 0.0, "training_share": 0.0, "total": 0.0,
              "profile": profile_name, "lifetime_requests": None, "ok": False}
    try:
        cfg = config or load_config()
        if cfg is None:
            raise ValueError("no config; refusing to invent conversion constants")

        profile = cfg["profiles"][profile_name]
        rates = profile["operational"]
        training = profile["training"]

        operational = (usage["input_tokens"] * rates["gco2e_per_input_token"]
                       + usage["output_tokens"] * rates["gco2e_per_output_token"])

        denominator = lifetime_requests or training["assumed_lifetime_requests"]
        if denominator <= 0:
            raise ValueError(f"lifetime_requests must be positive, got {denominator}")
        training_share = training["total_gco2e"] / denominator

        LOG.debug("operational = %d in * %g + %d out * %g = %g g",
                  usage["input_tokens"], rates["gco2e_per_input_token"],
                  usage["output_tokens"], rates["gco2e_per_output_token"], operational)
        LOG.debug("training_share = %g g / %g requests = %g g",
                  training["total_gco2e"], denominator, training_share)

        result.update(operational=operational, training_share=training_share,
                      total=operational + training_share,
                      lifetime_requests=denominator, ok=True)
        return result
    except Exception as e:                                          # noqa: BLE001
        print(f"[token_meter:grams_co2e] {e}")
        traceback.print_exc()
        return result


# --------------------------------------------------------------------------- #
# Step 3: grams to something a person can picture
# --------------------------------------------------------------------------- #

def equivalents(grams, config=None):
    """Express a figure in grams as everyday activities of similar frequency.

    Daily-frequency anchors on purpose. A flight comparison is arithmetically
    correct and rhetorically useless: it makes any amount of AI use look like
    nothing, which tells you nothing about whether the habit is worth its cost.
    """
    out = {}
    try:
        cfg = config or load_config()
        if cfg is None:
            raise ValueError("no config; refusing to invent anchors")
        anchors = cfg["equivalents"]
        out = {
            "car_miles": grams / anchors["gco2e_per_car_mile"],
            "hamburgers": grams / anchors["gco2e_per_hamburger"],
            "streaming_hours": grams / anchors["gco2e_per_streaming_hour"],
            "smartphone_charges": grams / anchors["gco2e_per_smartphone_charge"],
        }
        return out
    except Exception as e:                                          # noqa: BLE001
        print(f"[token_meter:equivalents] {e}")
        traceback.print_exc()
        return out


# --------------------------------------------------------------------------- #
# Reporting
# --------------------------------------------------------------------------- #

def format_report(usage, carbon, human, scale=1):
    """One block of markdown you can paste into a writeup.

    ``scale`` projects a single measured request out to a realistic volume, which
    is the only way the per-request numbers become legible: one request is
    always negligible, and that is exactly why nobody optimizes it.
    """
    lines = []
    try:
        how = "measured" if usage.get("measured") else f"ESTIMATED via {usage.get('source')}"
        lines.append(f"- Tokens ({how}): {usage['input_tokens']} in, {usage['output_tokens']} out")
        lines.append(f"- Profile: {carbon['profile']}")

        if not carbon.get("ok"):
            # The conversion failed. Report the tokens, which are real, and say
            # plainly that the carbon figures are not available. A zero here
            # would read as "this cost nothing," which is the one thing it
            # must never say.
            lines.append("- Carbon: NOT COMPUTED. The conversion failed; see the error above. "
                         "Report the token counts and say the conversion was unavailable "
                         "rather than reporting zero.")
            return "\n".join(lines)

        lines.append(f"- Operational: {carbon['operational'] * scale:.6g} g CO2eq")
        lines.append(f"- Training share: {carbon['training_share'] * scale:.6g} g CO2eq "
                     f"(total training cost divided by an assumed "
                     f"{carbon['lifetime_requests']:.0g} lifetime requests)")
        lines.append(f"- Total: {carbon['total'] * scale:.6g} g CO2eq")
        if scale != 1:
            lines.append(f"- Scaled to {scale:,} requests")
        for name, value in human.items():
            lines.append(f"  - {value * scale:.4g} {name.replace('_', ' ')}")
        if not usage.get("measured"):
            lines.append("- NOTE: token counts are estimated, not measured. Say so in the writeup.")
        return "\n".join(lines)
    except Exception as e:                                          # noqa: BLE001
        print(f"[token_meter:format_report] {e}")
        traceback.print_exc()
        return "\n".join(lines)


def measure(response_json, profile_name="offline", prompt_text=None,
            completion_text=None, config=None, lifetime_requests=None):
    """Run all three steps. The one call most code wants."""
    cfg = config or load_config()
    usage = read_usage(response_json, prompt_text, completion_text)
    carbon = grams_co2e(usage, profile_name, cfg, lifetime_requests)
    return {"usage": usage, "carbon": carbon, "equivalents": equivalents(carbon["total"], cfg)}


if __name__ == "__main__":
    # A worked example with no model server: the shape of a real Ollama reply.
    fake = {"prompt_eval_count": 337, "eval_count": 200}
    for profile in ("commercial", "offline"):
        m = measure(fake, profile)
        print(f"\n=== {profile} ===")
        print(format_report(m["usage"], m["carbon"], m["equivalents"], scale=100_000))
