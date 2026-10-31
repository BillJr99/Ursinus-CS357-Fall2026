# TODO

- [ ] Break the assignments and labs into smaller, digestible steps, done one at a time rather than in large parts.  Explain the tools as they come up, including git, hooks, and permissions, instead of assuming them.  Build the charter files and the agent files (AGENTS.md and the rest) from scratch with the students rather than handing them a scaffold. (added 2026-09-22)
- [ ] Teach each concept in isolation first, one at a time: hooks, skills, MCP, permissions, and the rest, each one small enough to run on its own and see what it does.  Then write a tutorial that puts them together into one working system, so students see how the pieces compose only after each piece is already familiar. (added 2026-09-22)
- [ ] Break each assignment down the way the OpenCode Studio and Local Agent labs need to be broken down: into smaller pieces, each completed and checked in one iteration, so that students take one small step at a time rather than working through a large part before seeing any result. (added 2026-09-24)
- [ ] Improve materials and tutorials on using the shell and configuring applications. (added 2026-09-25)
- [ ] Eliminate "bring with you" items from the readings
- [ ] Slow down the first half of the course: spread the early units (workbench and coding agents, local AI, skills, prompt engineering, the Karpathy and Gauntlet loops, tool use, and MCP) across more meetings, and shift the first-half deliverable dates to match, so each concept gets its own small, runnable step before the next begins. (added 2026-09-30)
- [ ] Consider an assignment in which students fine-tune a small model with LoRA or build a RAG system over a corpus of their own, then compare the two on held-out questions (the Offline RAG and LoRA tutorial is a possible starting point). (added 2026-10-07)
- [ ] Consider an opencode only environment possibly with Docker for isolation; look into Docker Sandbox
- [ ] Restructure lecture and assignment topics to be more focused; consolidate material to "do less and be awesome"
- [ ] Have a separate dev docker container that runs as the root user and runs opencode in auto mode, but that is isolated to a workspace subdirectory of the current directory
- [ ] Simplify software environment setup to OpenCode and a docker container with the required software including TUI OpencCode
- [ ] Consider continued use of Jetstream2 (added 2026-10-19)
- [ ] Make sure we talk about specific skills at the project level: name the skills (the SKILL.md files, how they are scoped and triggered) that each team's final project uses, and discuss them explicitly when the project is introduced and at its checkpoints, not only in the Skills unit. (added 2026-10-22)
- [ ] Improve student accountability through firm deliverable schedules and clearer late policies: publish a deliverable calendar students can plan against, state the late penalty and any grace or extension mechanism in plain terms up front, and apply it consistently. (added 2026-10-22)

- [ ] Simplify the language across the course so each page is concise and easy to scan:
  - **Syllabus table:** shorten the wording in the schedule table (titles, reading entries, and deliverable descriptions) to the minimum a student needs; move any longer explanation to the linked page instead of the table.
  - **Assignments:** tighten the assignment pages' wording. Where an assignment has multiple parts or multiple options (for example, a choice of tracks, topics, or deliverables), give each part or option its own page and link to it from the parent assignment page, so no single page has to carry all of them.
  - **Lecture decks:** simplify the language in the LiaScript decks (shorter sentences, fewer asides per slide), and split any deck that covers several distinct topics into focused decks that the syllabus links to individually.
  - When splitting pages, keep the syllabus `dlink` / `rlink` entries, the Canvas deploy (`ursinus_canvas.py` and the inline-change script), and the rubric `rubricpath` references pointing at the right pages, and update the Canvas shell with a dry-run-first inline change if titles or links move.

- [ ] Instructional design pass on the notes and LiaScript templating: shift detailed explanations from the notes into fully worked tutorials, keep the notes concise for live in-class use, and link each tutorial from its notes page (and possibly from the syllabus); structure the notes for learning (objectives up front, short checks for understanding, consistent layout); incorporate Universal Design for Learning (UDL) principles (multiple means of engagement, representation, and action and expression); meet WCAG accessibility guidelines and check each page with the WebAIM WAVE evaluation tool; and improve the LiaScript templates (shared macros and reusable components, consistent deck structure) so new and existing decks stay consistent. (added 2026-10-29)
  - From the session "Access by Design: AI Strategies for Inclusive Course Design in Higher Education" by Loffert and Xie (2026 AAC&U Conference on AI and Higher Education), slide "AI-powered content organization": use AI to organize content clearly, logically, and in multiple formats, with a consistent, predictable layout for course materials and assignment deadlines. Starter prompt: "I am [role] teaching a [specific course, size, level, meeting lengths/times per week] and need help designing a consistent, predictable layout for my course materials and deadlines, with a focus on accessibility and Universal Design for Learning (UDL) principles. Please create a template that I can use for each week of the course. This template should include sections for the following: weekly overview, learning objectives, readings, assignments, etc."
  - From the session "Access by Design: AI Strategies for Inclusive Course Design in Higher Education" by Loffert and Xie (2026 AAC&U Conference on AI and Higher Education), slide "AI-powered scaffolding": use AI to provide clear, step-by-step instructions for existing assignments or projects. Starter prompt: "[copy and paste or attach existing assignment] Rewrite this assignment into a clear, student-facing brief that supports Universal Design for Learning (UDL). Focus on clarity, accessibility, and step-by-step guidance. Use plain, direct language that anticipates confusion and avoids jargon."
  - Consider an autoresearch loop: an agent that audits each notes page, tutorial, and LiaScript deck against WCAG (checked with WAVE) and the UDL principles, applies fixes, re-evaluates, and iterates until the pages pass. (added 2026-10-29)

- [ ] Investigate GitHub Codespaces as the course development environment (setup, devcontainer, cost and student quotas, fit with the OpenCode and Docker workflow). (added 2026-10-29)

- [ ] Consider proficiency-based grading standards (for example, standards- or specifications-based grading) that reward on-time submissions and consistent, sustained effort across the term. (added 2026-10-29)

- [ ] Consider LangChain Managed Deep Agents (LangSmith) for the course: https://docs.langchain.com/langsmith/python/managed-deep-agents-overview (added 2026-10-30)

- [ ] Consider building a tutoring agent for the course, from the session "Building AI Agents for Teaching and Learning: Purpose, Design, and Human Judgment" by Sen and Khodarahmi (2026 AAC&U Conference on AI and Higher Education), slide "How do we ensure effective learning and guardrails?": a tutor (Claude Code in the assignment repo, following a tutor's-rules CLAUDE.md that I write) talks with a simulated student (Claude playing a student from a persona sheet of who they are and what they get wrong); a grader (Claude reading the transcript against a rubric of what the tutor must and must not do) produces a scorecard, and I revise the tutor's rules and repeat. (added 2026-10-30)

- [ ] Grade the sprint boundaries: move points from the 75-point Demo Day submission onto the three sprint boundaries, or grade each boundary complete or not yet, in step with the accountability and proficiency-based grading entries above. (added 2026-10-31)

- [ ] Let a team marked not yet at a sprint check show the item by the next class meeting for credit, in step with the proficiency-based grading entry above. (added 2026-10-31)

- [ ] Put a recurring 20-minute project studio block on Thursdays in weeks 11 to 13, so the sprints have class time between the sprint checks. (added 2026-10-31)

- [ ] Rebalance the sprint boundaries: Sprint 2 runs only from the Project Sprint session to the gallery walk (two class days), yet it carries all agents implemented (Direction A) and a 4-6 page risk analysis (Direction B). (added 2026-10-31)

- [ ] Schedule the Direction A 10-minute class discussion on responsible use (Final Project, Direction A build requirements) into named sprint-week sessions; no session holds it this term. (added 2026-10-31)

- [ ] Collapse the two role sets (Manager, Recorder, Presenter, Reflector in class; Coordinator, Builder, Evaluator, Scribe on the project) into one, and keep standups, decisions, and roles on one team board or PROJECT.md. (added 2026-10-31)

- [ ] Run the CATME-style peer pulse at every sprint boundary, not only at check-ins 2 and 3. (added 2026-10-31)

- [ ] Replace the Canvas rubric on the charter and the intra-team check-ins at the next deploy: it still carries the old Professionalism and Process wording, because replacing it this term would delete scores already recorded. (added 2026-10-31)
