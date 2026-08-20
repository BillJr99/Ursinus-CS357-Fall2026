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

Agentic tools have collapsed the distance between an idea and a working artifact, for professional engineers and for people who have never written a line of code. What they have *not* collapsed is the distance between "it ran once" and "it deserves someone's trust," and that distance is crossed by the same three disciplines in both cases: **testing**, **continuous integration**, and **human-centric design**. This module runs in two parallel tracks (choose yours by background, and read both: the other track is your future collaborator). The arc: **the trust gap → Track A for software engineers → Track B for non-coders → the shared discipline of CI → designing for the humans on the other end**.

---

## Directions and Group Roles

Work in your POGIL team with rotated roles (**Manager**, **Recorder**, **Presenter**, **Reflector**). Today's teams deliberately mix backgrounds: each team needs at least one member working each track, because the jigsaw at the end depends on the contrast. Prerequisites: the agent CLI module; Track A also wants the shell module fresh. After class, respond to the reflective prompt individually in your notebook.

---

## Key Concepts

Before diving in, keep this reference table handy. Every term below appears in today's models and exercises.

| Term | Plain-English Definition | Example You'll See Today |
|------|--------------------------|--------------------------|
| **Maker mindset** | The orientation of someone who builds things to solve real problems for real people — not just to demonstrate that something is technically possible, but to deliver something trustworthy and useful | Choosing a simple, reliable tip calculator over a flashy app that crashes on edge cases, because the person using it is standing at a restaurant |
| **Rapid prototyping** | Building the smallest possible working version of something quickly, then iterating based on what you learn — the goal is to fail fast and cheaply rather than late and expensively | Asking an agent to generate a first draft of a web page so you can see what is wrong with your spec before investing hours of refinement |
| **Minimum Viable Agent (MVA)** | The simplest agent that actually does the job reliably: one clear task, one tool, well-defined input and output, tested against real inputs — no more moving parts than the problem requires | A single-tool agent that scrubs PII from text, tested on 20 sentences, is more production-ready than a six-tool orchestration that has never been tested on bad input |
| **Scope creep** | The tendency for a project to grow beyond its original intent as new features are added without removing corresponding complexity — especially dangerous when an agent can generate new capabilities in seconds | Starting with "write a tip calculator" and ending up with a multi-currency restaurant booking assistant because each agent response suggested a new feature |
| **API integration** | Connecting your agent or application to an external service through its published interface — the point where your code sends a request and someone else's service responds | Calling a weather API to retrieve real forecast data for Collegeville rather than having the agent hallucinate weather information |
| **"Hello World" equivalent for AI systems** | The simplest possible working AI pipeline that proves your environment is set up correctly and your mental model of the system is right — before adding any real complexity | An agent that reads one file, summarizes it in one sentence, and prints the result: if this works, your model, your tools, and your permissions are all configured correctly |

---

# Part I: The Trust Gap

In this part, you will examine the gap between a working demo and a trustworthy artifact — the central challenge of AI-assisted making. Understanding this gap is what separates someone who ran a demo from someone who built something worth trusting.

## 1. Generation Is Cheap; Verification Is the Product

Think of the difference between a draft email and a sent email. Your email client lets you draft anything in seconds, but the moment you click Send, you are responsible for every word. An agentic tool puts you in the same position, but the "Send" button is "Approve," and the email goes to your entire filesystem. The economics of making changed: an agent produces a plausible artifact in minutes, so plausible artifacts are no longer scarce, and the scarce thing is *justified confidence* that an artifact does what it claims under conditions its maker did not happen to try. Every pathology this course has named (specification gaps, reward hacking, the happy-path demo, confident hallucination) reappears here as a making problem: the agent satisfied your words, not your intent, and only verification reveals the difference. So the maker's identity shifts. You are less the producer of the artifact and more its **specifier, verifier, and accountable owner**: you decide what "correct" means, you arrange for that meaning to be checked mechanically and repeatedly, and your name absorbs the consequences either way. Both tracks below are that identity, practiced at different altitudes.

---

## Model 1: The Demo That Lied Politely

**Why this matters:** Every project has a demo moment and a real-use moment, and the distance between them is where failures live. Think of a map app that works perfectly on the highway but routes you into a one-way street in an unfamiliar city. The app was not wrong in its own testing; it just was not tested on your city. An agent-generated artifact has exactly this property: it works on the examples the developer tried, and fails on the inputs the developer did not imagine. Understanding this gap — and taking responsibility for closing it — is what separates a maker from someone who ran a demo.

A student asks an agent for a unit-converter web page; it works beautifully in the demo. Later: entering `-40` crashes it, pasting `1,000` (with the comma) silently converts the wrong number, and a screen-reader user cannot operate it at all.

### Critical Thinking Questions

1. Classify each failure: which is a specification gap, which a missing test, and which a design failure? Defend the classifications; they overlap, and the overlap is the point.

   > *Hint: A specification gap means the maker's original request did not address this case — if you never said "handle negative numbers," the agent had no reason to. A missing test means the case was implied or obvious but no check was written to catch it before shipping. A design failure means the artifact does not serve all intended users — accessibility is not an edge case, it is a requirement for any public-facing tool. For the comma bug, ask: whose job was it to think of "what if the user types a comma"? The answer tells you which category it falls in.*

2. Write the three sentences the student *should* have included in the original request to prevent each failure. Notice which sentence required no technical knowledge whatsoever.

   > *Hint: For the crash on negative numbers: one sentence about valid input range and what to do when input is out of range. For the comma bug: one sentence about what input formats are expected and what to do with unexpected formats. For the accessibility failure: one sentence about who will use this tool and on what devices — you do not need to know what ARIA labels are to say "a screen-reader user should be able to operate every control." Which of those three required the most technical knowledge to write?*

3. The agent was never wrong by its own lights. Whose job was each failure, in the maker identity from Section 1?

   > *Hint: The maker identity from Section 1 assigns three responsibilities: specifying what "correct" means, verifying that the artifact meets that specification, and owning the consequences. Map each failure to one of these responsibilities. The agent produced what you asked for — the question is whether you asked for the right thing and checked that you got it. If you did not specify negative-number handling, whose job was it to know that a unit converter might receive negative temperatures?*

The trust gap is the same regardless of your background — the next two tracks show what closing it looks like in practice, from two different starting points.

---

# Part II: Track A, for Software Engineers

In this part, you will apply software-engineering discipline — tests, small diffs, and CI — to agent-generated code. These habits are what prevent the "it worked in the demo" failure from reaching real users.

## 2. The Agent as a Junior Colleague with Infinite Stamina

**Why this matters:** Imagine hiring someone who can write code faster than you can read it, never gets tired, and has read every Stack Overflow answer ever posted — but has never shipped anything to real users and does not know your codebase's conventions. That is the agent. The question is not whether to use it; the question is what review discipline you apply to its output. The same discipline you would apply to a junior colleague's pull request applies here, and skipping it because "the agent is smart" is the same mistake as merging without reviewing because "the contributor is experienced." Speed of generation does not substitute for correctness of review.

Treat agent output exactly as you would a pull request from a bright, fast, context-poor new hire, which yields the working rules. **Small diffs only**: ask for one function, one fix, one test at a time, because review quality collapses with diff size, and your review *is* the safety system. **Tests precede or accompany every change**: the strongest pattern is writing (or having the agent write, then you verifying) the failing test first, so the specification exists in executable form before the implementation does; an agent aimed at a failing test cannot reward-hack you nearly as easily as an agent aimed at prose. **Read every line before it merges**: the permission gate taught you to read commands; this is the same discipline for diffs, and "it passed the tests" does not excuse you, because the tests are also under review. **Pin everything**: dependency versions, model versions, seeds; an unpinned project is an unreproducible one, and you have a lab rubric line that already says so.

The code below illustrates the "test first" pattern: notice that the tests exist before any implementation does, and each test case is a precise contract the agent must satisfy — look for how the `test_rejects_nonnumeric` test pre-decides the comma-bug behavior that would otherwise be a specification gap.

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

The same rigor applies when you are not writing tests at all — Part III shows the equivalent discipline for makers who work without code.

---

# Part III: Track B, for Makers Who Do Not Code

In this part, you will practice the two core non-coder skills — writing concrete specifications and systematically verifying the result — that turn AI generation from guesswork into a reliable process. These same skills underpin professional product development at every level.

## 4. You Are Not "Using AI Instead of Coding"; You Are Specifying and Verifying

**Why this matters:** Think of the difference between telling a contractor "make my kitchen nice" and handing them a blueprint with exact measurements, materials, and a list of what you will inspect before you pay. The contractor can do excellent work either way, but only one of those instructions makes you a client with leverage and the other makes you someone who hopes for the best. The non-coder's relationship with an agent is exactly the same: the quality of your specification is the quality of your outcome, and systematic verification is how you know you got what you asked for — not hope, not re-running until it looks right.

The non-coder's track is not a lesser version of Track A; it is the same two skills with different instruments. **Specification** for you means writing what you want with the concreteness of a recipe: who the user is, what they see first, what every button does, what happens when input is empty or wrong or hostile, and what "done" looks like as a checklist you could hand a stranger. The single most powerful sentence available to you is: *"Before writing anything, ask me five questions about what I have not specified."* It converts the agent from a guesser into an interviewer and surfaces the gaps while they are still free to fix.

**Verification** for you means systematic trying, not coding: maintain a checklist of behaviors (drawn from your spec) and walk it after every change; deliberately misuse your artifact (empty inputs, absurd inputs, the back button, a phone screen); and recruit one person who was not in the room to attempt the main task while you watch silently, which will teach you more in five minutes than an afternoon of self-testing. When something breaks, your bug report is itself a specification act: *what I did, what I expected, what happened instead*, pasted verbatim to the agent, which fixes from that triplet far better than from "it's broken."

The checklist below is a real engineering artifact — notice that every item is binary (pass/fail), concrete enough for a stranger to test, and grounded in the actual user experience rather than the developer's intent:

```markdown
## Acceptance checklist: tip calculator (v0.2)     <- this artifact IS engineering
- [ ] Entering 50 and choosing 20% shows 10.00 and total 60.00
- [ ] Entering 0 shows 0.00, not an error
- [ ] Entering letters shows a friendly message, not a crash
- [ ] Works on my phone's screen without sideways scrolling
- [ ] My roommate completed a tip without any instruction from me
```

One boundary completes the track: know what you are accountable for shipping. A page that handles no one's personal data and takes no payments is yours to publish (the Cloudflare module showed how); anything touching credentials, money, or other people's private information needs a Track A partner or a reviewer, and recognizing that line *is* the engineering judgment this track teaches.

A non-coding maker's strongest defense against an agent's specification gaps is:

[( )] Asking the agent to double-check its own work — a model that made a specification error will typically affirm the same error when asked to review its own output
[( )] Choosing the largest available model — a bigger model follows the same ambiguous specification more fluently, but fluentness is not correctness
[(X)] Writing concrete acceptance criteria first and instructing the agent to ask clarifying questions before generating, then verifying against the criteria after every change
[( )] Regenerating until the output looks right — if the specification is ambiguous, regenerating produces different plausible-looking artifacts, not a correct one

Both tracks now converge on the same institutional mechanism: a system that runs every check automatically, every time, so that verification does not depend on anyone remembering to do it.

---

# Part IV: The Shared Discipline of CI

In this part, you will set up Continuous Integration — the mechanism that runs your checks automatically on every change so that verification never depends on human memory or goodwill. CI is the referee that no agent can charm.

## 5. Continuous Integration: Your Standards, Running While You Sleep

**Why this matters:** Imagine if every time you pushed a change to a shared project, a robot immediately ran every check you had ever written and emailed you the results before anyone else saw the change. That is CI, and it means the question "did I break anything?" has an answer in two minutes rather than two days. For agent-assisted projects specifically, CI is the referee that the agent cannot charm: a persuasive agent can convince you its change is correct, but a failing CI run simply reports the test result, with no negotiation.

CI is the mechanization of everything above: a service (GitHub Actions, in our course) that runs your checks automatically on every push, so the question "did anything break?" gets answered by a machine, every time, before a human ever trusts the change. A complete, real workflow — read the `on: [push, pull_request]` trigger and the `run: python -m pytest tests/ -v` step carefully, because those two lines are where your automated checks attach to the development process:

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

Commit that file and the green check or red X appears on every push and pull request, including the agent's. For Track B the same idea applies one level up: connect your project to Pages or a similar service so every change produces a *preview deployment*, and your acceptance checklist runs against the preview before anything reaches the real URL. In both tracks, CI is also the referee between you and your agent: an agent's change that turns the build red is rejected by the system itself, with no negotiation, which is a deterministic checker in exactly the sense your pre-mortems demanded. And note where the human gates survive: CI *verifies* on every push, but *publishing* still triggers only on a deliberate human act (a tag, a merge), the design the publishing module called the gate moving rather than vanishing.

All of this verification infrastructure ultimately serves one purpose: ensuring that a real person, using your artifact under real conditions, has a good experience — which is what Part V examines.

---

# Part V: Human-Centric Design

In this part, you will shift from technical verification to user-centered thinking — designing for the person who will actually use your artifact under real conditions, not the ideal conditions of your demo. This is the last mile most projects never finish.

## 6. The Artifact Meets a Person

**Why this matters:** Every artifact you build eventually meets a person who is not you, under conditions you did not test, on a device you did not try, in a mood you did not anticipate. The student who built the unit converter tested it at a desk, on a laptop, with a stable internet connection, knowing exactly what the app was supposed to do. The person who eventually uses it may be standing in a lab, on a phone, with a screen reader, in a hurry. Designing for that person — not just for the demo — is the last mile that most projects never finish.

Both tracks converge on the user, and four commitments cover most of the distance for course-scale work. **Know one user concretely**: a one-paragraph persona (who, on what device, under what pressure, with what alternative if you fail them) outperforms a vague "users," and every design dispute gets settled by asking what serves that person. **Design the failure paths as carefully as the success path**: error states, empty states, and slow states are where trust is actually won; "something went wrong" is a design abdication, while "couldn't reach the model server; your draft is saved; retry?" is engineering kindness. **Accessibility is a floor, not a feature**: keyboard operability, sufficient contrast, labeled controls, and alt text are minimums, agents produce them readily *when asked*, and asking is your job. **Close the feedback loop**: a visible way for users to tell you something is wrong, and evidence you act on it, which for AI-backed artifacts includes the course's honesty requirements: disclose the AI's role, surface uncertainty, and never let a confident interface launder an unconfident model.

---

## Model 2: The Jigsaw Review

**Why this matters:** Every engineering discipline has a code review culture for a reason: the person who wrote the code is the worst person to find its flaws, because they know what it was supposed to do and their eyes fill in what is missing. The jigsaw here forces the same cross-perspective review that professional teams rely on — except the two perspectives are not "senior" and "junior," they are "people who think in tests" and "people who think in user stories," and each sees something the other is structurally blind to.

Pair across tracks: each Track A member brings a tested change with its CI run; each Track B member brings an artifact with its acceptance checklist and one observed stranger-test.

### Critical Thinking Questions

4. Track B reviews Track A's tests against the persona: which *human* consequence has no test? Track A reviews Track B's checklist: which item should become automated, and what would that take?

   > *Hint: For Track B reviewing Track A: look at the test file and ask "which failure would harm a real user but would not cause a test to fail?" — accessibility failures, misleading error messages, and confusing UI states often fall into this gap. For Track A reviewing Track B: look at the acceptance checklist and identify any item that could be expressed as a boolean check (pass/fail) that could be run by a script — "works on my phone's screen without sideways scrolling" can be approximated by a responsive layout check; "my roommate completed a tip without instruction" cannot. Which items are automatable, and what would you need to write to automate them?*

5. Both inspect each other's failure paths by deliberately breaking things for two minutes. Record the kindest and the most abandoning failure message found, verbatim.

   > *Hint: To find failure messages, try: submitting an empty form, entering letters where numbers are expected, disconnecting from the network mid-operation, pressing the browser back button at the wrong moment, and resizing the window to a very narrow width. The "kindest" message tells the user specifically what went wrong, what to do next, and reassures them that their work is not lost. The "most abandoning" message either crashes silently, shows a raw error code, or says nothing at all. Quote both verbatim — the contrast is the lesson.*

6. As a team, write the one-sentence answer: what did the other track see that yours was structurally blind to?

   > *Hint: "Structurally blind" means not just "missed by accident" but "could not have seen, given how our track trained us to look." Track A is trained to ask "does this pass a test?" — a question that can miss failures that don't throw exceptions. Track B is trained to ask "does this feel right to a user?" — a question that can miss failures that are invisible to casual use but catastrophic at scale. Your one sentence should name the structural blind spot, not just a specific thing that was missed.*

---

> **⚠️ Common Misconception:** A complex multi-tool agent is more impressive than a simple one that works reliably — so building something with many moving parts signals more skill. In practice, the opposite is true in deployment. Complexity is where failures hide: every additional tool is an additional failure mode, every additional API call is an additional network dependency, and every additional model invocation is an additional opportunity for hallucination to compound. The most trusted production AI systems are often the simplest ones that do one thing well with measurable reliability. Scope creep — adding features because the agent can generate them in seconds — is one of the most common ways student projects fail at the verification stage. Build the Minimum Viable Agent first, verify it thoroughly, and only then add complexity if the problem genuinely requires it.

---

## 7. Exercises

**Exercise 1: Spec First**

- *What to do*: Before your next agent session (for any project in this course), write the complete specification first: Track A writes failing tests, Track B writes an acceptance checklist with the five-questions instruction prepended. Run the agent session against it and submit the spec, the transcript, and the verification evidence showing that the artifact meets the spec.
- *Starter hint*: For Track B, your very first message to the agent should be exactly: "Before writing anything, ask me five questions about what I have not specified." Copy the five questions and your answers into your submission — those questions are part of your deliverable, because they show what the spec was missing before you were asked. For Track A, write the test file first, run it to confirm it fails, then hand it to the agent with "make these pass without modifying the tests."
- *You've succeeded when*: Every item in your spec (test or checklist item) has a corresponding piece of evidence in the transcript or verification run showing it was checked — and you can identify at least one thing the agent would have gotten wrong if you had not specified it.

**Exercise 2: Red to Green to Guarded (Track A) / The Stranger Test (Track B)**

- *What to do*: Track A — take a small bug from any course lab, write the failing regression test, have an agent fix it under the no-test-modification rule, and merge only on a green CI run. Track B — recruit an observed user, watch silently while they attempt the main task of your artifact, log every hesitation and failure, and convert the worst two observations into specific change requests for your agent.
- *Starter hint*: Track A: the failing test must fail for the right reason before you hand it to the agent — run `pytest` and confirm the output names the bug, not a syntax error. Track B: tell your observer "I want to see how someone uses this for the first time" and say nothing else; do not help them, do not explain what the controls do. Log timestamps and quotes, not summaries — "she said 'what does this button do?' at 0:47" is better evidence than "she was confused."
- *You've succeeded when*: Track A — you have a PR-style trail showing the test failing, the agent's fix, and CI green; Track B — you have two before-and-after pairs showing the original failure observation and the verified fix.

**Exercise 3: CI from Zero**

- *What to do*: Add the CI workflow from Section 5 (or a Pages preview pipeline) to a project that does not yet have one. Make one deliberate change that fails the CI check, screenshot the red X, then fix it and screenshot the green check.
- *Starter hint*: The easiest way to trigger a failing CI run intentionally is to introduce a known-failing test: add `assert False, "intentional failure for exercise"` to any test file, commit and push, and watch the red X appear. Then remove that line and push again. This confirms the CI is actually running your tests and not just reporting green by default.
- *You've succeeded when*: You have two screenshots (one red X, one green check) and one sentence answering: "What decision did the red X take out of human hands, and was that good?"

**Exercise 4: The Kindness Audit**

- *What to do*: Inventory every failure state your artifact can reach — empty input, network error, invalid format, server timeout, unexpected browser — and rewrite its worst failure message to meet the failure-path commitments from Section 6: tell the user what went wrong, what to do next, and that their work is safe.
- *Starter hint*: To find all failure states, ask your agent: "List every condition under which this artifact could show an error, produce a blank result, or behave unexpectedly. For each condition, quote the current user-facing message." The agent's list is probably incomplete — add to it by trying each failure mode manually. Then for the worst message (the one that helps the user least), write a replacement that answers three questions: what happened, what can I do now, and is my work safe?
- *You've succeeded when*: You have a before-and-after table with at least three failure states, and your "after" messages each answer all three questions above, tested against the real artifact.

**Exercise 5: The Minimum Viable Agent**

- *What to do*: Design and build a Minimum Viable Agent for a real task you actually want to solve. Start by writing what the agent should do in one sentence. Implement only what that sentence describes. Test it on at least 10 real inputs. Only after it passes all 10 may you consider adding one additional feature.
- *Starter hint*: Your one-sentence description should follow this template: "An agent that takes [specific input] and produces [specific output] for [specific user] in [specific context]." If you cannot fill in all four blanks, you do not have a clear enough spec to build from. Examples: "An agent that takes a Python error message and produces a one-paragraph diagnosis for a CS101 student who is new to Python." "An agent that takes a restaurant name and produces a 3-sentence summary for someone deciding where to eat lunch."
- *You've succeeded when*: You have documented your one-sentence spec, 10 test inputs with expected and actual outputs, a pass/fail result for each, and a one-paragraph reflection on what you learned about the task from the 10 tests that you did not know when you wrote the spec.

---

## Reflection Prompt

In your notebook, respond at three levels:

**Personal level:** This module argued that AI moved the maker's value from producing artifacts to specifying, verifying, and owning them. Of those three — specifying, verifying, owning — which is currently weakest in you, and why? What concrete artifact from today's exercises revealed that weakness most clearly? What would you build differently in your next project because of what you noticed?

**Technical level:** The module introduced the Minimum Viable Agent as a design principle: do one thing reliably before adding complexity. How would you test whether an agent is truly "minimum"? Is there a principled way to decide when an agent is ready to have a second tool added, or is it always a judgment call? Describe the specific tests you would run before expanding an MVA — be concrete enough that someone else could follow your checklist.

**Societal level:** The maker projects you build in this course affect only yourself (and perhaps a few observers). But the same disciplines — specification, verification, CI, human-centric design — apply at scale to AI systems that affect millions of people. Who else could benefit from the maker project you built or imagined today? What would you have to change about your spec, your tests, or your failure paths to make it safe and useful for a population that is nothing like you — different devices, different languages, different levels of technical fluency, different trust in AI systems?

---

## → Coming Up Next

In the next module you will encounter the governance and policy layer that sits above individual maker decisions: what institutions, regulations, and professional norms shape what you are allowed to build, how you must document it, and who is accountable when it fails. The maker disciplines from today — specification as a contractual artifact, testing as an accountability mechanism, CI as an institutional check — reappear in that layer as professional and legal requirements. Make sure your Exercise 3 CI workflow is running and your Exercise 1 spec is documented: both will be reference material for the governance module.

---

## 8. Further Reading

- Martin Fowler, "Continuous Integration" (martinfowler.com): the canonical statement, brief and readable, on why running checks on every change is a discipline rather than a convenience.
- Don Norman. *The Design of Everyday Things*: the human-centric design floor, especially the chapters on errors — Chapter 5's treatment of human error as a design failure rather than a user failure is the philosophical foundation of Section 6.
- GitHub Docs, "Quickstart for GitHub Actions": the workflow syntax this module's YAML uses, with examples for Python, Node, and other languages.
- Ziegler et al., "Productivity Assessment of Neural Code Completion" (2022): empirical data on when AI code assistance helps and when it slows engineers down — the study that grounds the "small diffs only" rule in evidence.
