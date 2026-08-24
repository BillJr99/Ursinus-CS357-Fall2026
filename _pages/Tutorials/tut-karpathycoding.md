---
layout: default-standard
permalink: /Tutorials/VibeCoding
title: 'CS357: Foundations of Artificial Intelligence - AI-Assisted Development and Vibe Coding'
info:
  coursenum: CS357
  purpose: "To separate working from correct when an agent writes your program from a few sentences of English, and to build the review discipline that tells them apart."
tags:
- coding-agents
- review
- discipline
---
# CS357: Foundations of Artificial Intelligence - AI-Assisted Development and Vibe Coding

## Purpose

To separate working from correct when an agent writes your program from a few sentences of English, and to build the review discipline that tells them apart.

## About This Tutorial

Coding agents can now write working programs from a few sentences of English, but "working" and "correct" are not the same thing.  Researcher Andrej Karpathy coined the term **vibe coding** for the practice of giving an agent full latitude to implement a feature while you focus on the specification and the review.  We move from **the spectrum of AI assistance $\rightarrow$ specification-first development $\rightarrow$ rigorous diff review $\rightarrow$ the red-green-refactor-agent repair cycle**.

## Key Concepts

| Term | Plain-English Definition | Where You'll Meet It |
|------|--------------------------|--------------------------|
| **Vibe Coding** | Describing the desired outcome to a coding agent in natural language and letting it produce the full implementation, then reviewing the result rather than writing code line-by-line. | "Implement `search_memory` to pass these five tests", then reviewing what the agent produces |
| **Specification-First Development** | Writing a clear natural-language spec, acceptance criteria, and failing tests *before* any code exists, so there is an objective standard the implementation must meet. | Writing five `pytest` cases for `search_memory` before prompting the agent to implement it |
| **Test-Driven Development (TDD)** | A discipline in which every new behavior is defined by a failing test first; code is written to make the test pass; then the code is refactored. Often summarized as **red -> green -> refactor**. | A test that asserts `len(results) <= k` fails before the agent writes any code; it passes after |
| **Diff Review** | Examining the exact line-by-line changes an agent produced (insertions and deletions) rather than reading the final file from scratch, so you catch what the agent *changed* rather than what it *left alone*. | Spotting `eval(query)` in a 30-line diff that would otherwise be easy to miss |
| **Red-Green-Refactor** | The three TDD phases: **Red**, write a test that fails because the code does not yet exist; **Green**, write the minimum code that makes the test pass; **Refactor**, clean up the code without breaking the test. | A `pytest` run showing `FAILED` (red), then the agent's code making it `PASSED` (green) |
| **Agent Supervision Level** | How closely a human monitors and reviews the agent's output, ranging from autocomplete (every token supervised) to pair (every file reviewed) to vibe (only the final result reviewed). | Choosing "pair" for a security-sensitive module vs. "vibe" for a low-stakes utility script |

---

# Part I: The Spectrum of AI Assistance

In this part, you will map the range of ways AI can assist with coding (from autocomplete you review line by line, to autonomous agents that open PRs while you sleep) and practice choosing the right supervision level for a given risk profile.

## 1.  Three Supervision Levels

**Why this matters:** Handing an agent a task without thinking about supervision level is like handing a contractor your house keys and leaving for a month: maybe fine, maybe catastrophic, depending on how well you specified the job and how much you trust the contractor.  Karpathy makes the point that humans are better at writing specs than at reviewing arbitrary code, while models are better at writing code than at writing specs.  This suggests a division of labor: you own the specification, the agent owns the implementation, and the diff is the handoff artifact.

**The three levels exist on a continuum**, and the right choice depends on the stakes, the clarity of the spec, and how much you trust the existing test suite.

| Supervision Level | Description | Appropriate For | Risk Level | What the Human Reviews |
|-------------------|-------------|-----------------|------------|------------------------|
| **Autocomplete** | Agent suggests the next token, line, or block; human accepts or rejects inline | Boilerplate, well-understood APIs, single-function completions | Low | Every token as it is accepted |
| **Pair** | Human describes a task; agent produces a full file or function; human reads every line before accepting | New features in production code, security-sensitive modules | Medium | Every changed file, every line |
| **Vibe** | Human writes a spec and tests; agent implements the whole feature; human reviews only the diff | Well-tested utility code, prototypes, features with complete acceptance criteria | High (without tests) / Medium (with tests) | The diff against the spec and the test results |

---

## Supervision and the Diff

At vibe supervision level, the agent has autonomy over *how* to implement; the human retains authority over *what* to accept by reviewing the diff.

### Questions to Work Through

1.  At autocomplete supervision level, what is the primary artifact the human reviews before accepting work?  At vibe level?

   > *Hint: At autocomplete, you see each suggestion as it appears in your editor.  At vibe, you see the final output, but what specific representation of "what changed" is most useful for a human reviewer?*

2.  Karpathy's claim is that LLMs are better at writing code than writing specs, and humans are better at writing specs than reviewing arbitrary code.  If that is true, what does it imply about where human effort should be concentrated in the vibe coding workflow?

   > *Hint: If you are worse at reviewing 500 lines of arbitrary code than the agent is at writing them, where does your comparative advantage actually lie?  And what artifact does that produce that the agent can then act on?*

3.  Suppose you choose vibe supervision for a login authentication module.  What is the specific risk, and how could a complete test suite mitigate (but not eliminate) that risk?

   > *Hint: Tests check the behaviors you thought to test.  What categories of security behavior might a developer forget to write tests for?  Name at least two.*

> **Common Misconception:** "Vibe coding means you do not have to understand what the agent did."  At vibe supervision level the agent writes the code, but *you* are responsible for every line that ships.  The diff review and the test suite are not optional extras; they are what makes the "let me cook" approach safe rather than reckless.

At which supervision level is the diff the primary artifact you review before accepting the agent's work?

- Autocomplete, you review token-by-token suggestions in your editor
- Pair, you read every changed line in every file the agent touched
- Vibe, you have given the agent autonomy over implementation and now inspect what changed
- All three levels equally, the diff is always the primary review artifact

<details markdown="1"><summary>Answer</summary>

Vibe, you have given the agent autonomy over implementation and now inspect what changed

</details>

---

# Part II: Specification-First Development

In this part, you will practice the spec-first workflow: writing a clear function contract before touching any code, then using that spec to drive AI generation and verify correctness, the discipline that separates supervised AI development from "vibe coding."

## 2.  Writing the Spec Before the Code

**Why this matters:** The worst outcome in vibe coding is shipping code that passes all your tests but does not do what you actually wanted, because your tests were incomplete.  Specification-first development is the discipline that prevents this: you write down what the code must do, in plain English, before you write a single test.  The tests then operationalize the spec, and the agent's code is measured against the tests.  If you write tests first, you are forced to confront every ambiguity in the spec before the implementation distracts you.

**The three artifacts of specification-first development**, in order:

1.  A one-paragraph natural-language spec: the "what and why," not the "how."
2.  A list of acceptance criteria: specific, testable statements in the form "given X, the function must do Y."
3.  A failing test per acceptance criterion: executable Python (`pytest`) that fails *before any implementation exists* (the **red** phase).

---

## The `search_memory` Spec

**Natural-language spec:** `search_memory(query, k)` takes a user query string and a positive integer `k`, searches an in-memory list of text documents by cosine similarity of their embeddings, and returns the `k` most relevant documents as a list of strings.  It must reject invalid inputs gracefully and must never return more than `k` results.  It must raise a clear error rather than silently failing.

**Acceptance criteria:**

| # | Criterion |
|---|-----------|
| AC-1 | Given a query and `k=2`, the function returns exactly 2 strings. |
| AC-2 | The returned strings are drawn from the corpus; no hallucinated text is returned. |
| AC-3 | Given `k` larger than the corpus size, the function raises `ValueError`. |
| AC-4 | Given an empty string query, the function raises `ValueError`. |
| AC-5 | Given `k=0`, the function raises `ValueError`. |

**Failing tests (red phase):**

> **Runs on your machine, not here.**  This is a test file: save it in your repository and run it with `pytest`.

```python
import pytest

CORPUS = [
    "The Myrin Library closes at midnight on weekdays.",
    "First-year students may not bring vehicles to campus.",
    "Wismer Center serves continuous dining from 7am to 8pm.",
    "All students must complete a writing seminar in their first year.",
    "The Bakes Center is open to all students with a valid ID.",
]

def search_memory(query, k):
    raise NotImplementedError  # agent will replace this

def test_returns_k_results():
    results = search_memory("library hours", k=2)
    assert len(results) == 2

def test_results_are_from_corpus():
    results = search_memory("library hours", k=2)
    for r in results:
        assert r in CORPUS

def test_k_exceeds_corpus_raises():
    with pytest.raises(ValueError):
        search_memory("dining", k=100)

def test_empty_query_raises():
    with pytest.raises(ValueError):
        search_memory("", k=2)

def test_k_zero_raises():
    with pytest.raises(ValueError):
        search_memory("library", k=0)
```

Running `pytest` on this file before any implementation shows five `FAILED` lines, the **red** phase.

### Questions to Work Through

4.  AC-1 says the function returns "exactly 2 strings."  Is this a testable acceptance criterion?  What would make an acceptance criterion *un*testable?

   > *Hint: A testable criterion can be checked by a program without human judgment.  Words like "good," "appropriate," "reasonable," or "fast" make criteria untestable unless you define a measurement.  Is "returns exactly 2 strings" unambiguous enough to write `assert len(results) == 2`?*

5.  AC-2 says results must be "drawn from the corpus."  Write the `assert` statement that checks this for a single result string `r`.  (You have already seen it in the test above; what does it do?)

   > *Hint: The check is `assert r in CORPUS`.  What Python operation is `in` performing here, and why does this check fail if the agent returns a synthesized paraphrase instead of a verbatim document?*

6.  The spec says the function must "raise a clear error rather than silently failing."  AC-3 through AC-5 operationalize this.  What behavior would a *silently failing* implementation exhibit instead?

   > *Hint: "Silent failure" means the function returns without raising an exception, but returns a wrong, empty, or nonsensical value.  For example: returning `[]` when `k` exceeds the corpus size, instead of raising `ValueError`.  Why is silent failure dangerous in a system that other code depends on?*

> **Common Misconception:** "TDD means you write tests after you write code to make sure it works."  In true TDD the tests come first and they must *fail* before any implementation exists.  A test that passes before the implementation is written either tests the wrong thing or has a bug in the test itself.  The "red" phase is not a formality; it confirms that your test is actually measuring something.

In the TDD cycle, what does "red" mean?

- The code compiles but has a runtime error
- The test file has a syntax error that prevents it from loading
- The test runs but fails because the implementation does not yet exist or is incorrect
- The test passes but the code has poor performance

<details markdown="1"><summary>Answer</summary>

The test runs but fails because the implementation does not yet exist or is incorrect

</details>

---

# Part III: Synthesis and Practice

In this part, you will read a realistic AI-generated diff with a planted bug, practice the diff-review discipline that catches subtle errors, and apply the full spec -> generate -> review -> test loop on a problem of your own.

## 3.  Reviewing AI-Generated Diffs

**Why this matters:** When you ask a coding agent to "implement `search_memory` to pass these tests," the agent may produce code that passes every test and still be dangerous.  Tests are not a complete specification of correct behavior; they are a sample of behaviors you thought to check.  Diff review is how you find the behaviors you forgot to test.

**What to look for in a diff review:**

1.  **Spec fidelity:** Does the implementation match the spec, or does it satisfy only the letter of the tests?
2.  **Hidden assumptions:** Does the code assume sorted input, single-threaded access, ASCII-only text, or other preconditions not stated in the spec?
3.  **Security issues:** Does the code use `eval()`, shell injection via `subprocess`, or other patterns that allow arbitrary code execution from user input?
4.  **Resource issues:** Does the code leave files open, create unbounded data structures, or loop without an exit condition?

---

## A Planted-Bug Diff

Below is a 35-line implementation of `search_memory` that an agent might plausibly produce.  It passes all five tests above.  It contains **three deliberate issues**.  Read it carefully before answering the questions.

> **Runs on your machine, not here.**  This cell talks to the Ollama server on your own laptop at `localhost:11434`, which a web page has no route to.  Copy it into your course container and run it there.

```python
import requests
import math

CORPUS = [
    "The Myrin Library closes at midnight on weekdays.",
    "First-year students may not bring vehicles to campus.",
    "Wismer Center serves continuous dining from 7am to 8pm.",
    "All students must complete a writing seminar in their first year.",
    "The Bakes Center is open to all students with a valid ID.",
]

def embed(text):
    try:
        r = requests.post("http://localhost:11434/api/embeddings",
                          json={"model": "nomic-embed-text", "prompt": text},
                          timeout=120)
        return r.json()["embedding"]
    except Exception as e:
        print(f"[search_memory:embed] {e}")
        import traceback; traceback.print_exc()
        return []

def cosine(a, b):
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(x * x for x in b))
    return dot / (na * nb) if na and nb else 0.0

def search_memory(query, k):
    # BUG 1: eval() on user-controlled input
    processed_query = eval(f'"{query}"')

    if k <= 0:
        raise ValueError("k must be positive")
    if not query:
        raise ValueError("query must not be empty")
    if k > len(CORPUS):
        raise ValueError("k exceeds corpus size")

    q_vec = embed(processed_query)

    # BUG 2: silently returns [] on embedding failure
    if not q_vec:
        return []

    scored = [(cosine(q_vec, embed(doc)), doc) for doc in CORPUS]
    scored.sort(reverse=True)

    # BUG 3: no upper bound on k, caller could request millions of results
    return [doc for _, doc in scored[:k]]
```

### Questions to Work Through

7.  **Bug 1:** Find the line containing `eval()`.  Explain why calling `eval()` on `query` (a string provided by the user) is a security issue.  What would happen if a user passed `query = "__import__('os').system('rm -rf /')"` to this function?

   > *Hint: Python's `eval()` executes arbitrary Python expressions.  If `query` comes from an HTTP request, a form field, or any external source, the caller controls what gets executed.  What is the correct way to handle the string without `eval()`?*

8.  **Bug 2:** Find the block that begins `if not q_vec`.  The spec says the function must "raise a clear error rather than silently failing."  Does this line follow the spec?  What should it do instead, and write the one-line fix.

   > *Hint: Returning `[]` on embedding failure means the caller receives an empty result and has no idea why.  The list of acceptance criteria does not include "return empty list on error."  What exception should be raised, and with what message?*

9.  **Bug 3:** The `k > len(CORPUS)` check guards against `k` exceeding the corpus, so the `[:k]` slice is always bounded.  But there is still an issue with the size of intermediate computations.  What is it, and under what conditions would it matter?

   > *Hint: For this five-document corpus the issue is invisible.  Imagine `CORPUS` has 10 million documents.  The line `scored = [(cosine(q_vec, embed(doc)), doc) for doc in CORPUS]` does what to all 10 million documents before slicing?  How could you bound this computation?*

10.  For each of the three bugs, describe one `pytest` test case that would catch it.  You do not need to write full Python; a one-sentence description of what the test does is enough.

    > *Hint: Bug 1: what input to `search_memory` would trigger code execution if `eval()` is present? Bug 2: how would you simulate an embedding failure and check that an exception (not an empty list) is raised? Bug 3: what corpus size would make the full-scan computation visible as a performance problem?*

> **Common Misconception:** "If all tests pass, the code is correct."  Tests can only verify the behaviors you thought to test.  A function can pass 100 tests and still contain a security vulnerability, a resource leak, or an incorrect behavior on an input the tests did not cover.  Passing tests are necessary but not sufficient for correctness, which is precisely why diff review exists alongside testing.

A coding agent produces an implementation that passes all five acceptance-criterion tests.  A diff reviewer then notices `eval(query)` on line 4.  What does this finding demonstrate?

- The tests were poorly written and should be discarded
- The agent made a mistake that the test suite should have prevented automatically
- Tests verify sampled behaviors; diff review catches behaviors outside the test's scope, such as security properties
- The reviewer is being overly cautious; if all tests pass, the code is safe to ship

<details markdown="1"><summary>Answer</summary>

Tests verify sampled behaviors; diff review catches behaviors outside the test's scope, such as security properties

</details>

---

## 4.  Exercises

1.  *Find and fix the three bugs.*

   - *What to do:* Copy the `search_memory` implementation above into a local file.  Fix Bug 1 (remove `eval`, use the query string directly), Bug 2 (raise `RuntimeError` on empty embedding), and Bug 3 (add a note about why this is only a problem at scale; no code change required, just a comment).  Run `pytest` to confirm all five original tests still pass.
   - *Starter hint:* For Bug 1, the fix is simply `processed_query = query`; the `eval(f'"{query}"')` call adds nothing useful and opens the security hole.  For Bug 2, replace `return []` with `raise RuntimeError(f"Embedding failed for query: {query!r}")`.
   - *You've succeeded when:* All five original tests pass, `eval` no longer appears in the file, and your fixed function raises `RuntimeError` instead of returning `[]` when embedding fails.

2.  *Write the three "missing" tests.*

   - *What to do:* Add three new `pytest` test cases to your test file: one that checks `eval` injection is not possible (pass a query like `"__import__('os')"` and assert no `OSError` or side effect occurs), one that checks that an embedding failure raises an exception rather than returning an empty list, and one that checks the function raises `ValueError` when `k` equals `len(CORPUS) + 1`.
   - *Starter hint:* For the injection test, simply call `search_memory('__import__(\"os\")', k=1)` and assert the result is a list of strings; if `eval` were present, this would execute the import.  For the embedding failure test, use `unittest.mock.patch` to make `embed` return `[]` and confirm `RuntimeError` is raised.
   - *You've succeeded when:* Your three new tests pass against the fixed implementation and, if you temporarily re-introduce the bugs, the corresponding new tests fail.

3.  *Design a three-test minimum suite.*

   - *What to do:* For any function of your choice (not `search_memory`), write exactly three `pytest` tests: (a) a happy-path test that checks the common case, (b) a boundary test that checks an edge input (empty, zero, maximum, minimum), and (c) a security-property test that checks the function does not execute user input, leak data, or accept unreasonably large inputs.
   - *Starter hint:* Choose a function you wrote earlier in the course, for example, your embedding function, your RAG `rag_answer`, or a utility you built in the lab.  The security test does not need to simulate a real attack; it just needs to assert a property (e.g., the return type is always `list`, the return length is always `<= k`, the function never calls `eval`).
   - *You've succeeded when:* You can explain in one sentence why each of your three tests guards against a distinct category of failure (correctness, boundary behavior, security property).

---

## Group Discussion: Ensuring Code Quality in a World of AI-Generated Code

When a human wrote every line, code review, tests, and architecture reviews were the quality gates.  When an agent can generate hundreds of lines in seconds (faster than anyone can read them) *which* gates still work, and which have to change?  Discuss the following as a team.  There is no single right answer; the goal is to reason about where quality actually comes from when the author is a model.

**Prompt.**  Your team is about to let a coding agent implement a real feature.  You cannot review every line as carefully as if you had written it yourself.  Design the quality regime you would trust, arguing through each of these levers:

- **Tests before code (TDD), and *secret* tests.**  Why is a test *written before* the agent generates code a stronger quality signal than one written after?  Now push further: why might you keep a set of **held-out ("secret") acceptance tests the agent never sees**, and what specifically does that defend against that agent-visible tests do not?  (Connect to the "missing tests" and security-property test exercises above, and to held-out evaluation in `liascript-testingagents.md`.)
- **Charter-first architecting.**  Fixing the architecture, invariants, and interfaces *before* generation constrains what the agent is even able to build.  How does deciding the design up front reduce the blast radius of an AI error, compared to letting the agent invent structure as it goes?  (Connect to the charter in `liascript-agentgovernance.md`.)
- **Verification vs. trust, and accountability.**  You will approve a diff you did not fully read.  What is the minimum you must verify yourself for that approval to be responsible, and if a defect ships anyway, who is accountable: the person who wrote the spec, the agent, the reviewer who approved, or the team that deployed?

**Deliverable.**  Produce a short "quality checklist" (5-7 items) your team would actually apply to an AI-generated pull request, and mark each item as a gate that runs *before* generation, *during* review, or *after* merge.

> *Hint: The strongest regimes combine all three levers rather than relying on one.  A held-out test the agent cannot see is uncheatable; a charter written first bounds what can go wrong; and a human who verifies the security-critical and irreversible paths (even without reading every line) catches what tests miss.  Ask which lever catches which category of failure.*

---

## Reflection Prompt

*Personal:* Looking back at the planted-bug diff in Model 3, did you spot all three issues before reading the questions?  Be honest.  What made the dangerous ones easy or hard to see?

*Technical:* In your notebook: how does TDD change the *cost* of an AI error?  If the agent introduces a bug that violates an acceptance criterion, at what point in the workflow is that bug caught, and how does that compare to a workflow with no pre-written tests?

*Societal:* Suppose a team uses vibe coding to ship a student-facing grade portal and a bug causes incorrect grades to display.  Who is responsible: the developer who wrote the spec, the agent that wrote the code, the reviewer who approved the diff, or the institution that deployed it?  Argue for one answer and identify the weakest link in the chain.

---

## Where This Goes Next

Your vibe-coded feature is working and tested locally.  The next challenge is making every push trigger automated testing and deploying the result without manual steps.  The next module introduces **CI/CD and Publishing**: how to wire GitHub Actions (or a local pipeline) to run your `pytest` suite on every commit, catch regressions before they reach users, and publish a working artifact automatically.

---

## 5.  Further Reading

- Andrej Karpathy.  "Software 2.0."  *Medium* (2017).  The essay that introduced the framing of neural networks as a new programming paradigm.
- Kent Beck.  *Test-Driven Development: By Example*.  Addison-Wesley (2002).  The canonical TDD reference; the red-green-refactor cycle is defined here.
- OWASP. "OWASP Top 10 for Large Language Model Applications." https://owasp.org/www-project-top-10-for-large-language-model-applications/, see especially "Prompt Injection" and "Insecure Output Handling."
- Google Project Zero.  "0day In the Wild." https://googleprojectzero.blogspot.com, illustrates real-world consequences of the categories of bugs introduced in this tutorial.
- This course: [Governing Coding Agents: Charters, Handoffs, and Durable Memory](https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357-Fall2026/gh-pages/_pages/Activities/liascript-agentgovernance.md), a production case study of these rules governing a multi-month, multi-agent project.
