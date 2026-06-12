# The AI Maker: Agents, Engineering Discipline, and Human-Centric Design
<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?https://github.com/BillJr99/Ursinus-CS357/blob/gh-pages/_pages/Activities/liascript-aimaker.md or locally via https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-aimaker.md

import: https://raw.githubusercontent.com/liascript/CodeRunner/master/README.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-Boilerplate-Assets@main/css/liascript-custom.css?v=2025-08-23-4
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap

-->

# The AI Maker: Agents, Engineering Discipline, and Human-Centric Design

Agentic tools have collapsed the distance between an idea and a working artifact, for professional engineers and for people who have never written a line of code. What they have *not* collapsed is the distance between "it ran once" and "it deserves someone's trust," and that distance is crossed by the same three disciplines in both cases: **testing**, **continuous integration**, and **human-centric design**. This module runs in two parallel tracks (choose yours by background, and read both: the other track is your future collaborator). The arc: **the trust gap $\rightarrow$ Track A for software engineers $\rightarrow$ Track B for non-coders $\rightarrow$ the shared discipline of CI $\rightarrow$ designing for the humans on the other end**.

---

## Directions and Group Roles

Work in your POGIL team with rotated roles (**Manager**, **Recorder**, **Presenter**, **Reflector**). Today's teams deliberately mix backgrounds: each team needs at least one member working each track, because the jigsaw at the end depends on the contrast. Prerequisites: the agent CLI module; Track A also wants the shell module fresh. After class, respond to the reflective prompt individually in your notebook.

---

# Part I: The Trust Gap

## 1. Generation Is Cheap; Verification Is the Product

The economics of making changed: an agent produces a plausible artifact in minutes, so plausible artifacts are no longer scarce, and the scarce thing is *justified confidence* that an artifact does what it claims under conditions its maker did not happen to try. Every pathology this course has named (specification gaps, reward hacking, the happy-path demo, confident hallucination) reappears here as a making problem: the agent satisfied your words, not your intent, and only verification reveals the difference. So the maker's identity shifts. You are less the producer of the artifact and more its **specifier, verifier, and accountable owner**: you decide what "correct" means, you arrange for that meaning to be checked mechanically and repeatedly, and your name absorbs the consequences either way. Both tracks below are that identity, practiced at different altitudes.

---

## Model 1: The Demo That Lied Politely

A student asks an agent for a unit-converter web page; it works beautifully in the demo. Later: entering `-40` crashes it, pasting `1,000` (with the comma) silently converts the wrong number, and a screen-reader user cannot operate it at all.

### Critical Thinking Questions

1. Classify each failure: which is a specification gap, which a missing test, and which a design failure? Defend the classifications; they overlap, and the overlap is the point.
2. Write the three sentences the student *should* have included in the original request to prevent each failure. Notice which sentence required no technical knowledge whatsoever.
3. The agent was never wrong by its own lights. Whose job was each failure, in the maker identity from Section 1?

---

# Part II: Track A, for Software Engineers

## 2. The Agent as a Junior Colleague with Infinite Stamina

Treat agent output exactly as you would a pull request from a bright, fast, context-poor new hire, which yields the working rules. **Small diffs only**: ask for one function, one fix, one test at a time, because review quality collapses with diff size, and your review *is* the safety system. **Tests precede or accompany every change**: the strongest pattern is writing (or having the agent write, then you verifying) the failing test first, so the specification exists in executable form before the implementation does; an agent aimed at a failing test cannot reward-hack you nearly as easily as an agent aimed at prose. **Read every line before it merges**: the permission gate taught you to read commands; this is the same discipline for diffs, and "it passed the tests" does not excuse you, because the tests are also under review. **Pin everything**: dependency versions, model versions, seeds; an unpinned project is an unreproducible one, and you have a lab rubric line that already says so.

```python
# The pattern in miniature: the spec exists as a failing test first.
import unittest, traceback
from converter import to_celsius

class TestConverter(unittest.TestCase):
    def test_freezing(self):  self.assertEqual(to_celsius(32), 0)
    def test_negative_forty(self): self.assertEqual(to_celsius(-40), -40)
    def test_rejects_nonnumeric(self):
        with self.assertRaises(ValueError):   # the comma bug, pre-decided
            to_celsius("1,000")

if __name__ == "__main__":
    try:
        unittest.main()
    except Exception as e:
        print(f"[test_converter:main] {e}")
        traceback.print_exc()
```

Hand the agent *this file* and the request "make these pass without modifying the tests," and you have converted a vague wish into a checkable contract, with the no-modification clause closing the most obvious hack. That clause should sound familiar: it is your rubric-patching lab, transplanted.

## 3. Where Agents Genuinely Excel for Engineers

Steer the horsepower toward its best uses: generating test cases you would not have bothered writing (edge cases, property-based sketches, regression tests from bug reports); mechanical refactors under test protection; reading unfamiliar codebases and drafting the documentation nobody wrote; and first drafts of CI configuration, which Part IV shows. The common thread is work where verification is cheap relative to generation, which is precisely where the new economics pay you instead of ambushing you.

---

# Part III: Track B, for Makers Who Do Not Code

## 4. You Are Not "Using AI Instead of Coding"; You Are Specifying and Verifying

The non-coder's track is not a lesser version of Track A; it is the same two skills with different instruments. **Specification** for you means writing what you want with the concreteness of a recipe: who the user is, what they see first, what every button does, what happens when input is empty or wrong or hostile, and what "done" looks like as a checklist you could hand a stranger. The single most powerful sentence available to you is: *"Before writing anything, ask me five questions about what I have not specified."* It converts the agent from a guesser into an interviewer and surfaces the gaps while they are still free to fix.

**Verification** for you means systematic trying, not coding: maintain a checklist of behaviors (drawn from your spec) and walk it after every change; deliberately misuse your artifact (empty inputs, absurd inputs, the back button, a phone screen); and recruit one person who was not in the room to attempt the main task while you watch silently, which will teach you more in five minutes than an afternoon of self-testing. When something breaks, your bug report is itself a specification act: *what I did, what I expected, what happened instead*, pasted verbatim to the agent, which fixes from that triplet far better than from "it's broken."

```markdown
## Acceptance checklist: tip calculator (v0.2)     <- this artifact IS engineering
- [ ] Entering 50 and choosing 20% shows 10.00 and total 60.00
- [ ] Entering 0 shows 0.00, not an error
- [ ] Entering letters shows a friendly message, not a crash
- [ ] Works on my phone's screen without sideways scrolling
- [ ] My roommate completed a tip without any instruction from me
```

One honest boundary completes the track: know what you are accountable for shipping. A page that handles no one's personal data and takes no payments is yours to publish (the Cloudflare module showed how); anything touching credentials, money, or other people's private information needs a Track A partner or a reviewer, and recognizing that line *is* the engineering judgment this track teaches.

[[MC]]
A non-coding maker's strongest defense against an agent's specification gaps is:
- ( ) Asking the agent to double-check its own work
- ( ) Choosing the largest available model
- (x) Writing concrete acceptance criteria first and instructing the agent to ask clarifying questions before generating, then verifying against the criteria after every change
- ( ) Regenerating until the output looks right

---

# Part IV: The Shared Discipline of CI

## 5. Continuous Integration: Your Standards, Running While You Sleep

CI is the mechanization of everything above: a service (GitHub Actions, in our course) that runs your checks automatically on every push, so the question "did anything break?" gets answered by a machine, every time, before a human ever trusts the change. A complete, real workflow:

```yaml
# .github/workflows/ci.yml
name: CI
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: pip install -r requirements.txt
      - run: python -m pytest tests/ -v
```

Commit that file and the green check or red X appears on every push and pull request, including the agent's. For Track B the same idea applies one level up: connect your project to Pages or a similar service so every change produces a *preview deployment*, and your acceptance checklist runs against the preview before anything reaches the real URL. In both tracks, CI is also the honest referee between you and your agent: an agent's change that turns the build red is rejected by the system itself, with no negotiation, which is a deterministic checker in exactly the sense your pre-mortems demanded. And note where the human gates survive: CI *verifies* on every push, but *publishing* still triggers only on a deliberate human act (a tag, a merge), the design the publishing module called the gate moving rather than vanishing.

---

# Part V: Human-Centric Design

## 6. The Artifact Meets a Person

Both tracks converge on the user, and four commitments cover most of the distance for course-scale work. **Know one user concretely**: a one-paragraph persona (who, on what device, under what pressure, with what alternative if you fail them) outperforms a vague "users," and every design dispute gets settled by asking what serves that person. **Design the failure paths as carefully as the success path**: error states, empty states, and slow states are where trust is actually won; "something went wrong" is a design abdication, while "couldn't reach the model server; your draft is saved; retry?" is engineering kindness. **Accessibility is a floor, not a feature**: keyboard operability, sufficient contrast, labeled controls, and alt text are minimums, agents produce them readily *when asked*, and asking is your job. **Close the feedback loop**: a visible way for users to tell you something is wrong, and evidence you act on it, which for AI-backed artifacts includes the course's honesty requirements: disclose the AI's role, surface uncertainty, and never let a confident interface launder an unconfident model.

---

## Model 2: The Jigsaw Review

Pair across tracks: each Track A member brings a tested change with its CI run; each Track B member brings an artifact with its acceptance checklist and one observed stranger-test.

### Critical Thinking Questions

4. Track B reviews Track A's tests against the persona: which *human* consequence has no test? Track A reviews Track B's checklist: which item should become automated, and what would that take?
5. Both inspect each other's failure paths by deliberately breaking things for two minutes. Record the kindest and the most abandoning failure message found, verbatim.
6. As a team, write the one-sentence answer: what did the other track see that yours was structurally blind to?

---

## 7. Exercises

1. *(Both tracks) Spec first.* Before your next agent session, write the specification (Track A: failing tests; Track B: acceptance checklist plus the five-questions instruction). Run the session against it and submit the spec, the transcript, and the verification evidence.
2. *(Track A) Red to green to guarded.* Take a small bug from any course lab, write the failing regression test, have an agent fix it under the no-test-modification rule, and merge only on green CI. Submit the PR-style trail.
3. *(Track B) The stranger test.* Recruit your observed user, watch silently, and log every hesitation. Convert the worst two into change requests for your agent, verify, and report before-and-after.
4. *(Both) CI from zero.* Add the workflow above (or a Pages preview pipeline) to a project, make one change that fails it and one that passes, and screenshot both verdicts. One sentence: what decision did the red X take out of human hands, and was that good?
5. *(Both) The kindness audit.* Inventory every failure state your artifact can reach and rewrite its worst message per the failure-path commitments. Submit before and after, with the persona who deserved better.

---

## Reflection Prompt

In your notebook: this module argued that AI moved the maker's value from producing artifacts to specifying, verifying, and owning them. Which of those three is currently weakest in you, what concrete habit from your track addresses it, and what would change about your answer if you imagine teaching this module instead of taking it?

---

## 8. Further Reading

- Martin Fowler, "Continuous Integration" (martinfowler.com): the canonical statement, brief and readable.
- Don Norman. *The Design of Everyday Things*: the human-centric design floor, especially the chapters on errors.
- GitHub Docs, "Quickstart for GitHub Actions": the workflow syntax this module's YAML uses.
