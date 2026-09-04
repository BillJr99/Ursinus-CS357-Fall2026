---
layout: syllabus
permalink: /
title: "CS357: Foundations of Artificial Intelligence"

info:
  course_number: CS357
  course_sections:
  - section: "A"
  course_title: "Foundations of Artificial Intelligence"
  credit_hours: "4 Semester Hours"
  course_homepage: "https://www.billmongan.com/Ursinus-CS357-Fall2026/"
  teamshelproom: "https://teams.microsoft.com/l/team/19%3AwLG9HyqYOj7K3bd_6-rTi9L_ctuc35ppB9WK-ObSTpw1%40thread.tacv2/conversations?groupId=79df3988-c03f-46f1-b2fc-51e4539a7c94&tenantId=921f1c03-8689-4e60-a722-f5ea581e00fe"
  class_notebook: https://ursinuscollege365-my.sharepoint.com/personal/wmongan_ursinus_edu/Documents/Class%20Notebooks/CS357%20Fall%202026
  ical: files/CS357.ics
  course_prerequisites: "Prerequisites: CS-170 or CS-173 or DATA-201, or permission from the instructor."
  course_start_date: "2026/08/24"
  course_end_date: "2026/12/08"
  course_description: "A technical introduction to the tools and practices that have evolved from artificial intelligence (AI) and large language models that considers the role of technology through the lens of the Ursinus Questions.  This course prepares students to create and interact with conversational virtual assistants and multi-agent systems that achieve goal-oriented outcomes.  Students will explore the foundations and history of artificial intelligence that enabled the technical underpinnings of generative AI, with a particular emphasis on the ethical, social, and intellectual property implications of the nature of the training data sets used to form large language models.  The course includes a practical discussion of responsible AI from the perspective of creators and of consumers and stakeholders.  Students will apply current design patterns in AI with respect to large language models to create and present a technical project using generative AI, and will lead a discussion focused on practices for responsible AI within the context of their chosen project.  Prerequisites: CS-170 or CS-173 or DATA-201, or permission from the instructor.  Four hours per week.  Four semester hours."
  questions: |
    This semester, we organize the course around a single guiding idea: an agent is a system that perceives, plans, and acts toward a goal. We will collectively consider questions like:
    <ul>
    <li>What does it mean for a machine to act on our behalf, and how does delegation to an agent differ from using a tool?</li>
    <li>How do the foundations of generative AI (embeddings, attention, retrieval) enable, and limit, what agents can reliably do?</li>
    <li>How do the assumptions embedded in training datasets influence the behavior of agents, and what responsibilities do creators and users have in mitigating these effects?</li>
    <li>When should an agent run locally and privately, and when is it appropriate to rely on hosted services?</li>
    <li>How can multi-agent designs (debate, critique and refine, consensus) improve reliability, and what new failure modes do they introduce?</li>
    <li>How can system design align agent outcomes with ethical principles, and who is accountable when an autonomous system errs?</li>
    <li>How do coding agents like OpenCode, Plandex, and Hermes reshape software development, and what review discipline do their generated diffs demand?</li>
    <li>What is the carbon and water cost of AI computation, and how should environmental impact influence our design choices for agents?</li>
    <li>Does it matter whether an AI system genuinely understands, or only whether it behaves as if it does, and what are the ethical implications of our answer?</li>
    <li>How do containers, filesystems, network policies, and OAuth scopes create the safety boundaries that allow us to deploy autonomous agents responsibly?</li>
    </ul>
  welcome_message: "Welcome to CS357!"
  class_meets_days:
    isM: false
    isT: true
    isW: false
    isR: true
    isF: false
    isS: false
    isU: false
  class_meets_locations:
  - section:
    - day: "T"
      starttime: "12:00 PM"
      endtime: "1:15 PM"
      place: "Pfahler 107"
    - day: "R"
      starttime: "12:00 PM"
      endtime: "1:15 PM"
      place: "Pfahler 107"
  # No midterm/final in this course.  "TBD" dates are the sentinel that suppresses
  # rendering and .ics events for these blocks, so do not delete them.
  midtermexam:
    - mdate: "TBD"
      mstarttime: "N/A"
      mendtime: "N/A"
      mroom: "N/A"       
  finalexam:
    - fdate: "TBD"
      fstarttime: "TBD"
      fendtime: "TBD"
      froom: "N/A"
  flexible_submission_policy: "In the absence of <a href=\"#accommodations\">accommodations</a> arranged in advance with the instructor or college, all assignments are due at 11:59 PM Eastern Time on the date(s) stated on the schedule.  With prior permission and a reasonable first draft submission by the deliverable deadline, any student may request a three day extension on any deliverable, as often as needed.  Assignments will be accepted without prior permission following the original deadline, or, if requested, following the three-day extension deadline, with a points deduction of 10% per day if submitted before 11:59 PM Eastern Time on the day submitted.  If a student adds the course late, deliverables due prior to or on the day of that student's registration will be due twice the number of days following the first day of the semester that they registered (for example, a student who registers on the third day of the semester shall receive six days to submit assignments from the first three days, and then the remainder of this policy takes effect for those and for all other deliverables).  Under no circumstances (including accommodations) can late work be accepted after the final class meeting, nor during final exams week, nor after the exam."
  late_penalty_per_period: 10
  late_penalty_period: "day"
  attendance: "Students may miss up to 4 classes without justification, although students are encouraged to communicate with me prior to missing class (or immediately after) so that we can discuss what was missed and how to catch up.  Any student who misses more than 4 classes will receive a full letter grade reduction for each subsequent class missed from the final letter grade.  A lateness to class shall count as one-half of an absence for purposes of this policy."  
  banner: |
    <div style="width: 100%; display: table; border-collapse:separate; border-spacing:5px;">
    <div style="width: 100%; display: table-row;">
        <div style="display: table-cell; padding:5px; width:33%;">
            <a title="Lwneal, CC0, via Wikimedia Commons" href="https://commons.wikimedia.org/wiki/File:Discriminative_vs_Generative_Neural_Networks.png"><img width="100%" alt="Above: Schematic example of a discriminative neural network performing image recognition. Below: Example of a generative neural network performing text-to-image generation" src="https://commons.wikimedia.org/w/index.php?title=Special:Redirect/file/Discriminative_vs_Generative_Neural_Networks.png"></a>
        </div>
        <div style="display: table-cell; padding:5px; width:33%;">
            <img src="https://encompass.mathematicalthinking.org/assets/images/workspaces_feedback-27ffa61b958051049ac3a8493c09c849.png" alt="An AI assisted feedback generator web frontend" width="100%"></img>
        </div>
        <div style="display: table-cell; padding:5px; width:33%;">
            <a title="Midjourney, Public domain, via Wikimedia Commons" href="https://commons.wikimedia.org/wiki/File:Th%C3%A9%C3%A2tre_D%E2%80%99op%C3%A9ra_Spatial.png"><img width="100%" alt="Théâtre D'opéra Spatial, an image made using generative artificial intelligence" src="https://commons.wikimedia.org/w/index.php?title=Special:Redirect/file/Th%C3%A9%C3%A2tre_D%E2%80%99op%C3%A9ra_Spatial.png"></a>
        </div>
    </div>
    </div>
    
university:
  semester: "Fall"
  academicyear: "2026-27"
  fall:
  - kname: "Add Deadline"
    kdate: "2026/09/02"
    kdisplay: true
  - kname: "Mid Semester Grades Posted"
    kdate: "2026/10/09"
    kdisplay: false
  - kname: "Drop with a W Deadline"
    kdate: "2026/11/17"
    kdisplay: true
  - kname: "Reading Day"
    kdate: "2026/12/09"
    kdisplay: true
  - kname: "Finals Week Begins"
    kdate: "2026/12/10"
    kdisplay: false
  - kname: "Finals Week Ends"
    kdate: "2026/12/16"
    kdisplay: false
  spring: []
  fallholidays:
  - date: "2026/09/07"
  - date: "2026/10/08"
  - date: "2026/10/12"
  - date: "2026/10/13"
  - date: "2026/11/25"
  - date: "2026/11/26"
  - date: "2026/11/27"
  springholidays: []

instructors:
- name: William Mongan
  title: Professor
  email: wmongan@ursinus.edu
  phone: "610-409-3268"
  office: "Pfahler Hall 101L"
  webpage_url: "http://www.billmongan.com"
  picture: /images/profile.png
  officehourssignup: "https://cal.com/billmongan/10min"
  officehours:
  - day: "T"
    starttime: "3:00 PM"
    endtime: "5:30 PM"
    location: "Pfahler Hall 101L"
  - day: "W"
    starttime: "3:00 PM"
    endtime: "5:30 PM"
    location: "Pfahler Hall 101L"
  - day: "R"
    starttime: "11:20 AM"
    endtime: "11:50 AM"
    location: "Pfahler Hall 101L"
  - day: "R"
    starttime: "3:00 PM"
    endtime: "3:30 PM"
    location: "Pfahler Hall 101L"
- name: AJ Luthra
  title: Teaching Assistant
  officehours: [] # TBD
textbooks:
- title: "Artificial Intelligence: A Guide for Thinking Humans"
  authors: "Melanie Mitchell"
  edition: "Revised Edition"
  isbn: "978-1-250-40485-5"
  link: false
  isrequired: true
  freelyavailable: false
- title: "The Philosophy of Artificial Intelligence"
  authors: "Margaret A. Boden, editor"
  isbn: "978-0198248545"
  link: false
  isrequired: true
  freelyavailable: false
- title: "AI by Hand"
  authors: "Tom Yeh"
  link: "https://www.scribd.com/document/726922630/AI-by-Hand-Vol-1"
  isrequired: false
  freelyavailable: "https://www.scribd.com/document/726922630/AI-by-Hand-Vol-1"
- title: "Race After Technology: Abolitionist Tools for the New Jim Code"
  authors: "Ruha Benjamin"
  isbn: "978-1509526406"
  link: false
  isrequired: false
  freelyavailable: false
- title: "Weapons of Math Destruction"
  authors: "Cathy O'Neil"
  isbn: "978-0553418835"
  link: false
  isrequired: false
  freelyavailable: false
- title: "Atlas of AI: Power, Politics, and the Planetary Costs of Artificial Intelligence"
  authors: "Kate Crawford"
  isbn: "978-0300264630"
  link: false
  isrequired: false
  freelyavailable: false
- title: "The Alignment Problem: Machine Learning and Human Values"
  authors: "Brian Christian"
  isbn: "978-0393868333"
  link: false
  isrequired: false
  freelyavailable: false
- title: "The Glass Cage: How Our Computers Are Changing Us"
  authors: "Nicholas Carr"
  isbn: "978-0393351243"
  link: false
  isrequired: false
  freelyavailable: false
- title: "Magnifica Humanitas: On Safeguarding the Human Person in the Time of Artificial Intelligence (encyclical letter, 15 May 2026)"
  authors: "Pope Leo XIV"
  link: "https://www.vatican.va/content/leo-xiv/en/encyclicals/documents/20260515-magnifica-humanitas.html"
  isrequired: false
  freelyavailable: "https://www.vatican.va/content/leo-xiv/en/encyclicals/documents/20260515-magnifica-humanitas.html"
objectives:
- objective: "Analyze the ethical implications of AI agents acting on behalf of people, using case studies, governance frameworks, and design justice principles."
- objective: "Design agentic AI systems, including prompts, retrieval pipelines, tools, and multi-agent orchestrations, that augment human capabilities while adhering to ethical guidelines."
- objective: "Evaluate the reliability of AI agents across tasks and disciplines, identifying best practices, failure modes, and risks associated with their use."
- objective: "Create documentation, evaluations, and governance plans for the responsible deployment of agentic AI technologies."
- objective: "Evaluate the environmental impact of AI deployments and propose design choices that reduce energy and carbon costs without sacrificing core capability."
- objective: "Engage with the philosophical and psychological dimensions of artificial intelligence, analyzing questions of understanding, responsibility, anthropomorphism, and the ethics of machine agency."

goals:
- goal: "Implement the perceive, plan, act loop of an agent using a locally hosted language model."
- goal: "Explain how tokens, embeddings, attention, and sampling parameters shape the behavior of generative models, and verify these explanations with by-hand calculations."
- goal: "Construct a retrieval-augmented generation pipeline over a personal knowledge base, and evaluate its retrieval and grounding quality."
- goal: "Compose multi-agent systems using orchestration patterns including pipelines, critique and refine, debate, and stochastic consensus, while keeping each agent's context window small and focused."
- goal: "Evaluate agent outputs using human rubrics and LLM-as-judge pipelines, and articulate the limits of each."
- goal: "Author a governance and responsible-use analysis for an agentic system of your own design, and present it to a public audience."
- goal: "Apply containerization and filesystem isolation principles to deploy AI agents with defined trust boundaries, non-root execution, read-only mounts, and minimal blast radius."
- goal: "Design, implement, and secure a working MCP server with OAuth 2.0 client credentials flow, and connect it to a local agent to demonstrate tool discovery, invocation, and token lifecycle management."
- goal: "Analyze the carbon and water footprint of an AI deployment and propose concrete efficiency improvements grounded in right-sizing, caching, and local-first inference choices."
- goal: "Use a coding agent (OpenCode, Plandex, or Claude Code) to implement a feature from a written spec, then critique the generated diff for correctness, security, and test coverage."
- goal: "Identify and research an issue, question, or practical problem"
- goal: "Develop a multi-disciplinary understanding of the problem to explore how it could be addressed"
- goal: "Collaborate to develop a strategic intervention that constructively addresses the issue"
- goal: "Communicate effectively with a variety of audiences through multiple modalities"
- goal: "Use the Open Questions to assess the learning process throughout, describing new understandings and specific areas of growth and skill development"

grade_breakdown:
- category: "Labs"
  weight: "35%"
- category: "Written Assignments"
  weight: "10%"
- category: "Responsible AI Capstone"
  weight: "10%"
- category: "Final Project and Project Thread Milestones"
  weight: "35%"
- category: "Class Activities and Participation"
  weight: "10%"

letter_grades:
- letter: "A+"
  range: "96.9-100"
- letter: "A"
  range: "93-96.89"
- letter: "A-"
  range: "89.5-92.99"
- letter: "B+"
  range: "87-89.49"
- letter: "B"
  range: "83-86.99"
- letter: "B-"
  range: "79.5-82.99"
- letter: "C+"
  range: "77-79.49"
- letter: "C"
  range: "73-76.99"
- letter: "C-"
  range: "69.5-72.99"
- letter: "D+"
  range: "67-69.49"
- letter: "D"
  range: "63-66.99"
- letter: "D-"
  range: "59.5-62.99"
- letter: "F"
  range: "0-59.49"

schedule:
- week: "0"
  date: "0"
  title: "Welcome: What Is AI, and What Is an Agent?"
  link: "https://www.billmongan.com/Ursinus-CS357-Overview"
  deliverables:
  - dtitle: "Participation: Warmup Assignment Handed Out"
    dlink: "Assignments/Warmup"
    points: "10"
  readings:
  - rtitle: "Mitchell, Prologue and Chapter 1"
  - rtitle: "Teachable Machine: train an image, sound, or pose classifier in the browser, with no code, to see what \"learning from examples\" actually means"
    rlink: "https://teachablemachine.withgoogle.com/"
  - rtitle: "AI Capabilities and Limitations (Anthropic Skilljar), a short self-paced course that covers the same ground as today's Capabilities and Limitations Framework"
    rlink: "https://anthropic.skilljar.com/ai-capabilities-and-limitations"
- week: "0"
  date: "1"
  title: "The Agent Loop: Perceive, Plan, Act"
  link: "Activities/liascript-agentloop.md"
  liapage: true
  deliverables:
  - dtitle: "Project: Team Formation Survey Handed Out"
    dlink: "Assignments/TeamSurvey"
    points: "10"
    rubricpath: "_pages/Assignments/asmt-teamsurvey.md"
  - dtitle: "Participation: Reading Group Handed Out"
    dlink: "Assignments/ReadingGroup"
    points: "10"
    rubricpath: "_pages/Assignments/asmt-readinggroup.md"
    module: overarching
  - dtitle: "Participation: Reading Responses Handed Out"
    dlink: "Participation/ReadingResponses"
    points: "10"
    rubricpath: "_pages/Participation/reading-responses.md"
    module: overarching
  readings:
  - rtitle: "Mitchell, Chapter 2"
  - rtitle: "The Token Prediction Playground, an in-browser simulator you drive yourself to see what next-token prediction can and cannot do"
    rlink: "TokenPredictor"
- week: "1"
  date: "0"
  title: "Your AI Workbench: Shell, Git, Containers, and Your First Coding Agent"
  link: "Activities/liascript-devenvironment.md"
  liapage: true
  deliverables:
  - dtitle: "Participation: Warmup Assignment Due"
    dlink: "Assignments/Warmup"
    points: "10"
  - dtitle: "Participation: Overview Assignment Handed Out"
    dlink: "Assignments/Overview"
    points: "100"
    rubricpath: "_pages/Assignments/asmt-overview.md"
  - dtitle: "Project: Team Formation Survey Due"
    dlink: "Assignments/TeamSurvey"
    points: "10"
    rubricpath: "_pages/Assignments/asmt-teamsurvey.md"
  readings:
  - rtitle: "Please bring a laptop with Docker Desktop already installed.  The download alone can eat the session.  If Docker will not run on your machine, that is fine; come anyway and we will set up the native route together."
    rlink: false
  - rtitle: "The Shell, in Full: pipes, redirection, background jobs, signals, and the PATH mechanics behind \"command not found\".  Step 0 of today's activity is the ten-minute version of this"
    rlink: "Tutorials/Shell"
  - rtitle: "Docker from Zero: how containers, images, and mounts actually work underneath today's build"
    rlink: "Tutorials/Docker"
- week: "1"
  date: "1"
  title: "Running Your Own AI: Ollama, OpenWebUI, and Private Local Models"
  link: "Activities/liascript-localai.md"
  liapage: true
  readings:
  - rtitle: "Mitchell, Chapter 3, part 1 of 4: what models do and do not understand (we spread this chapter across four sessions)"
  - rtitle: "Reading Response / Discussion: post a short response before class, what changed once the model ran on your own machine?"
  - rtitle: "The Local Model Landscape: Llama, Mistral, Phi, Gemma, and their relatives, for deciding what to pull next"
    rlink: "Tutorials/LocalModels"
  - rtitle: "The Hardware Behind AI: GPUs, quantization, and running models at the edge.  Read this if today's speeds surprised you"
    rlink: "Tutorials/Hardware"
- week: "2"
  date: "0"
  title: "Coding Agents: OpenCode, Spec-First Development, Hooks, and Reading the Diff"
  link: "Activities/liascript-codingagents.md"
  liapage: true
  deliverables:
  - dtitle: "Participation: Overview Assignment Due"
    dlink: "Assignments/Overview"
    points: "100"
    rubricpath: "_pages/Assignments/asmt-overview.md"
  - dtitle: "Lab: OpenCode Studio Handed Out"
    dlink: "Assignments/OpenCodeStudio"
    points: "100"
    rubricpath: "_pages/Assignments/lab-opencodestudio.md"
  - dtitle: "Project: Team Charter Handed Out"
    dlink: "Projects/PBLThread"
    points: "3"
    rubricpath: "_pages/Projects/proj-pblthread.md"
  readings:
  - rtitle: "Reading Response / Discussion: post a short response before class.  Describe one time you accepted AI-generated code or text without really reading it.  What would you check now, and what would have caught the thing you missed?"
  - rtitle: "Bring your cs357-work repository and the working opencode install from Week 1 (Step 8).  Today you drive the agent against a written specification and read its diff, so a broken setup costs you the session."
    rlink: false
  - rtitle: "OpenCode Studio, the lab handed out today.  Read Part 1 and the Before You Start section before class so the charter questions are familiar"
    rlink: "Assignments/OpenCodeStudio"
  - rtitle: "Agentic CLI Tools: Claude Code, Codex, Gemini CLI, and pi, and how each one differs from the opencode you drive today"
    rlink: "Tutorials/AgentCLIs"
  - rtitle: "AI Coding Agent Security: poisoned repositories and the software supply chain, the risk that arrives with the convenience"
    rlink: "Tutorials/CodingAgentSecurity"
  - rtitle: "What a container isolates, and how to size an agent's blast radius before you hand it your machine.  This is the background section of the Local Agent Lab's containerization direction"
    rlink: "Assignments/LocalAgent/Direction3"
- week: "2"
  date: "1"
  title: "Skills: Design One, Then Measure It"
  link: "Activities/liascript-skills.md"
  liapage: true
  deliverables:
  - dtitle: "Written Assignment: Skill Design Study Handed Out"
    dlink: "Assignments/SkillDesignStudy"
    points: "100"
    rubricpath: "_pages/Assignments/asmt-skilldesignstudy.md"
  readings:
  - rtitle: "Mitchell, Chapter 3, part 2 of 4: what the model is doing when it takes in your prompt"
  - rtitle: "Writing, configuring, and publishing skills for opencode and pi.ai, in the background section of Local Agent Lab Direction 5.  Today's deck builds the first skill with you; read this so the file layout is not new"
    rlink: "Assignments/LocalAgent/Direction5"
  - rtitle: "Bring your working Ollama setup and your opencode install.  The second half of class runs the same task with and without a skill and compares the results."
    rlink: false
- week: "3"
  date: "0"
  title: "Prompt Engineering as Agent Design: System Prompts, Personas, and Comparing Models"
  link: "Activities/liascript-promptengineering.md"
  liapage: true
  deliverables:
  - dtitle: "Project: Signed Team Charter (Forming) Due"
    dlink: "Projects/PBLThread"
    points: "3"
    rubricpath: "_pages/Projects/proj-pblthread.md"
  readings:
  - rtitle: "Mitchell, Chapter 3, part 3 of 4: continue the chapter with today's system-prompt and sampling behavior in mind"
  - rtitle: "Chalmers, David J. \"What We Talk to When We Talk to Language Models\""
    rlink: "https://philarchive.org/rec/CHAWWT-8"
  - rtitle: "Why Different Answers Every Time?  Sampling, Temperature, and Generation.  Read Parts I and II before class; Part IIc of today's deck uses the temperature and seed settings it explains"
    rlink: "Tutorials/SamplingAndTemperature"
  - rtitle: "Tokens, Embeddings, and Attention: How Models Represent Meaning.  Optional background for the persona and comparison work; read Part I at minimum"
    rlink: "Tutorials/TokensEmbeddingsAttention"
  - rtitle: "AI by Hand: Tokens, Cosine, Attention, Softmax, and a Forward Pass.  Optional worked arithmetic for anyone who wants to see the numbers behind temperature and similarity"
    rlink: "Tutorials/AIByHand"
  - rtitle: "Bring your working Ollama setup from Week 1 and the charter, contract, and skills you have written so far for the OpenCode Studio lab.  Today is that lab's mid-flight checkpoint, and the workshop edits system prompts against a live model."
    rlink: false
- week: "3"
  date: "1"
  title: "The Karpathy Loop and the Gauntlet Loop: Iterating With an Agent"
  link: "Activities/liascript-iterationloops.md"
  liapage: true
  readings:
  - rtitle: "AI-Assisted Development and Vibe Coding: the three supervision levels and the spec-first habit that today's loops build on"
    rlink: "Tutorials/VibeCoding"
  - rtitle: "Governing Coding Agents: the charter, Karpathy's rules, and the handoff directory"
    rlink: "Tutorials/AgentGovernance"
  - rtitle: "Bring the OpenCode Studio artifact you have so far.  Today's second half runs it through one gauntlet round."
    rlink: false
- week: "4"
  date: "0"
  title: "Hallucinations and Evaluating Agent Outputs"
  link: "Activities/liascript-evaluatingoutputs.md"
  liapage: true
  deliverables:
  - dtitle: "Lab: OpenCode Studio Due"
    dlink: "Assignments/OpenCodeStudio"
    points: "100"
    rubricpath: "_pages/Assignments/lab-opencodestudio.md"
  - dtitle: "Lab: Local Agent Handed Out"
    dlink: "Assignments/LocalAgent"
    points: "100"
    rubricpath: "_pages/Assignments/lab-localagent.md"
  - dtitle: "Project: Stakeholder Brief Handed Out"
    dlink: "Assignments/StakeholderBrief"
    points: "100"
    rubricpath: "_pages/Assignments/asmt-stakeholderbrief.md"
  readings:
  - rtitle: "Mitchell, Chapter 3, part 4 of 4: finish the chapter, hallucination, evaluation, and what the model cannot check for itself"
  - rtitle: "Please bring three prompts where a model gave you a confidently wrong answer.  We triage real examples here, not invented ones."
    rlink: false
- week: "4"
  date: "1"
  title: "Tool Use and Function Calling"
  link: "Activities/liascript-tooluse.md"
  liapage: true
  deliverables:
  - dtitle: "Lab: Tools and MCP Handed Out"
    dlink: "Assignments/ToolsMCP"
    points: "100"
    rubricpath: "_pages/Assignments/lab-toolsmcp.md"
  readings:
  - rtitle: "Ollama Structured Outputs, on schema-constrained JSON.  The Local Agent Lab's required structured-output segment uses this, so read it before the lab"
    rlink: "https://docs.ollama.com/capabilities/structured-outputs"
  - rtitle: "Structured outputs in depth: JSON mode, tool schemas, and output validation, in the background section of the Tools and MCP lab"
    rlink: "Assignments/ToolsMCP"
  - rtitle: "Instructor with Pydantic and Ollama, for typed and grammar-constrained generation: validity by construction rather than by retry"
    rlink: "https://python.useinstructor.com/integrations/ollama/"
- week: "5"
  date: "0"
  title: "MCP: Connecting Agents to Tools and Your Obsidian Vault"
  link: "Activities/liascript-mcp.md"
  liapage: true
  deliverables:
  - dtitle: "Project: Stakeholder Brief, Individual Unassisted Problem Statement Due"
    dlink: "Assignments/StakeholderBrief"
    points: "3"
    rubricpath: "_pages/Assignments/asmt-stakeholderbrief.md"
  readings:
  - rtitle: "Hugging Face MCP Course (built with Anthropic): protocol, building a server, connecting clients.  Supports the Local Agent Lab's MCP work"
    rlink: "https://huggingface.co/learn/mcp-course/"
  - rtitle: "Bring your half-page unassisted problem statement, written individually and without AI, before your team drafts the brief."
    rlink: false
  - rtitle: "Optional, five minutes: install Obsidian before class.  Model 3 puts an MCP server in front of a vault, and it is more useful on your own notes"
    rlink: "https://obsidian.md"
  - rtitle: "Syncing Obsidian to GitHub and wiring agents to your vault: the read path and write path that today's Model 3 exposes as tools"
    rlink: "Tutorials/ObsidianSync"
  - rtitle: "MCP, REST APIs, and OAuth 2.0 together, in the background section of Local Agent Lab Direction 4"
    rlink: "Assignments/LocalAgent/Direction4"
  - rtitle: "GitHub Superpowers for AI Developers: gitingest, getmcp.io, deepwiki, gdagram, and github.dev, for turning a repository into something an agent can read"
    rlink: "Tutorials/GitHubPowerTools"
- week: "5"
  date: "1"
  title: "RAG Knowledge Base: Code and No-Code Routes"
  link: "Activities/liascript-rag.md"
  liapage: true
  deliverables:
  - dtitle: "Written Assignment: Skill Design Study Due"
    dlink: "Assignments/SkillDesignStudy"
    points: "100"
    rubricpath: "_pages/Assignments/asmt-skilldesignstudy.md"
  readings:
  - rtitle: "Mitchell, Chapter 4"
  - rtitle: "Reading Response / Discussion: post a short response before class connecting RAG to a corpus of your own"
  - rtitle: "LangChain RAG from Scratch (video)"
    rlink: "https://www.youtube.com/watch?v=rz40ukZ3krQ&t=10s"
  - rtitle: "Tokens, Embeddings, and Attention: Part II, semantic search in twenty lines, is the retrieval step of today's pipeline"
    rlink: "Tutorials/TokensEmbeddingsAttention"
- week: "6"
  date: "0"
  title: "RAG Quality: Chunking and Measuring Retrieval"
  link: "Activities/liascript-ragquality.md"
  liapage: true
  deliverables:
  - dtitle: "Lab: Local Agent Due"
    dlink: "Assignments/LocalAgent"
    points: "100"
    rubricpath: "_pages/Assignments/lab-localagent.md"
  - dtitle: "Lab: RAG Knowledge Base Handed Out"
    dlink: "Assignments/RAGKnowledgeBase"
    points: "200"
    rubricpath: "_pages/Assignments/lab-ragknowledgebase.md"
  readings:
  - rtitle: "Mitchell, Chapter 4"
  - rtitle: "Please bring your team's Stakeholder Brief draft, because the peer review round works on real drafts."
    rlink: false
  - rtitle: "The RAG Quality Checkup pathway of the RAG Knowledge Base lab, handed out today: the golden set, the checkup worksheet, and the regression harness that today's metrics feed"
    rlink: "Assignments/RAGKnowledgeBase"
- week: "7"
  date: "1"
  title: "How I AI: A Vault, a Charter, and Agents That Talk Through GitHub and Dropbox"
  link: "Activities/liascript-howiai.md"
  liapage: true
  deliverables:
  - dtitle: "Project: Final Project Handed Out"
    dlink: "Projects/FinalProject"
    points: "100"
    rubricpath: "_pages/Projects/proj-finalproject.md"
  - dtitle: "Project: Final Project Proposal Handed Out"
    dlink: "Projects/FinalProjectProposal"
    points: "25"
    rubricpath: "_pages/Projects/proj-finalprojectproposal.md"
  - dtitle: "Project: Intra-Team Check-In (Storming into Norming) Due"
    dlink: "Projects/PBLThread"
    points: "3"
    rubricpath: "_pages/Projects/proj-pblthread.md"
  - dtitle: "Project: Stakeholder Brief Due"
    dlink: "Assignments/StakeholderBrief"
    points: "100"
    rubricpath: "_pages/Assignments/asmt-stakeholderbrief.md"
  readings:
  - rtitle: "Bring your stuck points and your pipeline-in-progress.  Part III is an open studio and it is only as useful as the problems you bring to it."
  - rtitle: "The Second Brain in depth: Obsidian, gitless GitHub sync, and the metadata protocol that makes agent writes safe"
    rlink: "Tutorials/SecondBrain"
  - rtitle: "Syncing Obsidian to GitHub and wiring agents to your vault: the full read path and write path"
    rlink: "Tutorials/ObsidianSync"
- week: "8"
  date: "0"
  title: "Observability, Traceability, and Handoff Protocols"
  link: "Activities/liascript-observability.md"
  liapage: true
  deliverables:
  - dtitle: "Lab: Tools and MCP Due"
    dlink: "Assignments/ToolsMCP"
    points: "100"
    rubricpath: "_pages/Assignments/lab-toolsmcp.md"
  readings:
  - rtitle: "Reading Response / Discussion: post a short response before class.  What is the longest-running piece of work you have done with an AI tool, and where did it start losing the thread?"
  - rtitle: "Memory and the Small Context Window Principle: why an agent that remembers everything gets worse, and the four kinds of memory today's protocols write down"
    rlink: "Tutorials/MemoryAndContext"
  - rtitle: "Agent Observability and Tracing: the three pillars and OpenTelemetry, which today's deck applies to your own agents"
    rlink: "Tutorials/Observability"
- week: "8"
  date: "1"
  title: "Design First: Plan Your Agent System Before You Build It"
  link: "Activities/liascript-designfirst.md"
  liapage: true
  deliverables:
  - dtitle: "Written Assignment: Design Your Agent System Handed Out"
    dlink: "Assignments/AgentSystemDesign"
    points: "100"
    rubricpath: "_pages/Assignments/asmt-agentsystemdesign.md"
  readings:
  - rtitle: "The handoff skill from Local Agent Lab Direction 5, Part C: the claim protocol your design document must specify"
    rlink: "Assignments/LocalAgent/Direction5"
- week: "9"
  date: "0"
  title: "Orchestration and Multi-Agent Patterns"
  link: "Activities/liascript-orchestration.md"
  liapage: true
  deliverables:
  - dtitle: "Project: Intra-Team Check-In (Norming into Performing) Due"
    dlink: "Projects/PBLThread"
    points: "3"
    rubricpath: "_pages/Projects/proj-pblthread.md"
  readings:
  - rtitle: "Agent Frameworks: LangChain, CrewAI, AutoGen, and Agno, and when a framework earns its weight"
    rlink: "Tutorials/AgentFrameworks"
- week: "9"
  date: "1"
  title: "Critique, Consensus, and the LLM Judge: One Loop, Three Uses"
  link: "Activities/liascript-critiqueconsensusjudge.md"
  liapage: true
  deliverables:
  - dtitle: "Lab: Multi-Agent Patterns Handed Out"
    dlink: "Assignments/MultiAgentDebate"
    points: "100"
    rubricpath: "_pages/Assignments/lab-multiagentdebate.md"
  - dtitle: "Project: Literature Review Handed Out"
    dlink: "Assignments/LitReview"
    points: "100"
    rubricpath: "_pages/Assignments/asmt-litreview.md"
  - dtitle: "Project: Final Project Proposal Due"
    dlink: "Projects/FinalProjectProposal"
    points: "25"
    rubricpath: "_pages/Projects/proj-finalprojectproposal.md"
  - dtitle: "Lab: RAG Knowledge Base Due"
    dlink: "Assignments/RAGKnowledgeBase"
    points: "200"
    rubricpath: "_pages/Assignments/lab-ragknowledgebase.md"
  readings:
  - rtitle: "From Second Brain to Chief of Staff: one personal agent followed into production"
    rlink: "Tutorials/ProductionAssistant"
  - rtitle: "Stochastic multi-agent consensus: sampling, clustering by meaning, and synthesis, in Part 2 of the Multi-Agent Patterns Lab handed out today"
    rlink: "Assignments/MultiAgentDebate"
- week: "10"
  date: "0"
  title: "Agents That Talk: Multi-Agent Communication Through GitHub and Dropbox, and Threat Modeling"
  link: "Activities/liascript-agentcommunication.md"
  liapage: true
  readings:
  - rtitle: "Reading Response / Discussion: post a short response before class.  When does a multi-agent design help, and when does it just cost tokens?"
  - rtitle: "Agentic Case Studies: Migration, Browsing, and Research Agents.  Read the two cases and the threat-modeling part; today's second half runs the incident simulation on your own project"
    rlink: "Tutorials/AgentCaseStudies"
  - rtitle: "Benjamin, Race After Technology, Chapters 1-2: case studies in discriminatory design"
- week: "10"
  date: "1"
  title: "Evaluating Agents With a Rubric: The Judge Pipeline Workshop"
  link: "Activities/liascript-rubricworkshop.md"
  liapage: true
  deliverables:
  - dtitle: "Written Assignment: Design Your Agent System Due"
    dlink: "Assignments/AgentSystemDesign"
    points: "100"
    rubricpath: "_pages/Assignments/asmt-agentsystemdesign.md"
  - dtitle: "Lab: Rubric Pipeline Handed Out"
    dlink: "Assignments/RubricPipeline"
    points: "100"
    rubricpath: "_pages/Assignments/lab-rubricpipeline.md"
  readings:
  - rtitle: "promptfoo, for declarative LLM and agent evaluation.  One of the two supported harnesses for the Rubric Pipeline Lab, and it runs against Ollama"
    rlink: "https://www.promptfoo.dev/docs/intro/"
  - rtitle: "Hamel Husain, \"Your AI Product Needs Evals\": the error-analysis-first approach to evaluation"
    rlink: "https://hamel.dev/blog/posts/evals/"
  - rtitle: "Inspect AI (UK AI Security Institute): the Dataset, Solver, and Scorer framework, the other supported Rubric Pipeline harness"
    rlink: "https://inspect.aisi.org.uk/"
- week: "11"
  date: "0"
  title: "Training Data, Bias, and Explainability"
  link: "Activities/liascript-biasdata.md"
  liapage: true
  deliverables:
  - dtitle: "Project: Literature Review, Individual Annotated Bibliographies Due"
    dlink: "Assignments/LitReview"
    points: "3"
    rubricpath: "_pages/Assignments/asmt-litreview.md"
  - dtitle: "Responsible AI Capstone Handed Out"
    dlink: "Assignments/ResponsibleAI"
    points: "200"
    rubricpath: "_pages/Assignments/lab-responsibleai.md"
  readings:
  - rtitle: "Reading Response / Discussion: post a short response before class, one design choice you would make differently in a system you deploy"
  - rtitle: "Coded Bias (film), watch before class"
    rlink: "https://www.codedbias.com/"
  - rtitle: "O'Neil, Weapons of Math Destruction: the chapter on predictive models in education"
  - rtitle: "Carr, The Glass Cage, Chapters 2-3: automation, deskilling, and automation bias"
  - rtitle: "Gandalf (Lakera), a prompt-injection game you play in the browser, and the shared warm-up for the Responsible AI Capstone handed out today"
    rlink: "https://gandalf.lakera.ai/"
  - rtitle: "Tensor Trust, where you attack and defend against prompt injection, and the other capstone warm-up"
    rlink: "https://tensortrust.ai/"
- week: "11"
  date: "1"
  title: "Intellectual Property, Privacy, and the Case for Local AI"
  link: "Activities/liascript-ipprivacy.md"
  liapage: true
  readings:
  - rtitle: "Crawford, Atlas of AI, Chapter 6: Affect / the politics of data"
- week: "12"
  date: "0"
  title: "Governance, Policy, and the Cost of Inference"
  link: "Activities/liascript-governancecost.md"
  liapage: true
  deliverables:
  - dtitle: "Lab: Multi-Agent Patterns Due"
    dlink: "Assignments/MultiAgentDebate"
    points: "100"
    rubricpath: "_pages/Assignments/lab-multiagentdebate.md"
  readings:
  - rtitle: "Crawford, Atlas of AI, Chapter 1, Earth: the mineral and energy costs of computation"
  - rtitle: "Reading Response / Discussion: post a short response before class on the carbon and water cost of a deployment you would run"
  - rtitle: "Christian, The Alignment Problem: any one chapter (for example, the section on reward and reinforcement)"
  - rtitle: "AI for Accessibility: Opportunity, Gaps, and Universal Design.  Optional; the accessibility audit is one of the policy sections you may draft today"
    rlink: "Tutorials/AIAccessibility"
- week: "12"
  date: "1"
  title: "Evaluation Workshop II: Run Your Rubric Against Your Project"
  link: "Activities/liascript-evalworkshop2.md"
  liapage: true
  deliverables:
  - dtitle: "Project: Literature Review, Team Synthesis Due"
    dlink: "Assignments/LitReview"
    points: "100"
    rubricpath: "_pages/Assignments/asmt-litreview.md"
  readings:
  - rtitle: "Bring your Rubric Pipeline judge as it stands and three artifacts from your final project for it to grade.  Today's workshop runs the judge against your own work and audits the disagreements."
    rlink: false
- week: "13"
  date: "0"
  title: "Project Studio: Sprint and Threat Model"
  link: "Activities/liascript-projectsprint.md"
  liapage: true
  deliverables:
  - dtitle: "Lab: Rubric Pipeline Due"
    dlink: "Assignments/RubricPipeline"
    points: "100"
    rubricpath: "_pages/Assignments/lab-rubricpipeline.md"
  readings:
  - rtitle: "Bring your integrated project and your proposal.  The peer review of proposals and the threat-model checklist both run on what you bring."
    rlink: false
- week: "14"
  date: "0"
  title: "Project Studio and Gallery Walk"
  link: "Activities/liascript-projectstudio.md"
  liapage: true
  deliverables:
  - dtitle: "Responsible AI Capstone Due"
    dlink: "Assignments/ResponsibleAI"
    points: "200"
    rubricpath: "_pages/Assignments/lab-responsibleai.md"
  readings:
  - rtitle: "Bring your gallery-walk artifact ready to display, and your SQR cards."
    rlink: false
- week: "14"
  date: "1"
  title: "Project Studio: Final Integration and Demo Rehearsal"
  link: "Activities/liascript-projectstudio.md"
  liapage: true
  deliverables:
  - dtitle: "Project: Intra-Team Check-In (Performing into Adjourning) Due"
    dlink: "Projects/PBLThread"
    points: "3"
    rubricpath: "_pages/Projects/proj-pblthread.md"
  readings:
  - rtitle: "Bring your integrated system and your demo script.  Today is a rehearsal rather than a work session.  If it does not run end to end at the start of class, that is the thing to fix."
- week: "15"
  date: "0"
  title: "Demo Day: Final Project Presentations (Class Switch Day: follows a Thursday schedule)"
  deliverables:
  - dtitle: "Project: Demo Day Presentations Due"
    dlink: "Projects/FinalProject"
    points: "75"
    rubricpath: "_pages/Projects/proj-finalproject.md"
  - dtitle: "Participation: Reading Group Due"
    dlink: "Assignments/ReadingGroup"
    points: "10"
    rubricpath: "_pages/Assignments/asmt-readinggroup.md"
  - dtitle: "Participation: Reading Responses Due"
    dlink: "Participation/ReadingResponses"
    points: "10"
    rubricpath: "_pages/Participation/reading-responses.md"
  readings:
  - rtitle: "Demo Day.  Bring the running system, the governance one-pager, and the contribution statements.  Nothing is due after today."
---

This course is about building agents you understand and can run yourself.  The sections below explain how the course gives you real choice over your path, how to read an assignment, how to prepare for each hands-on session, and how I value and evaluate the day-to-day work of participating, including engaging with your classmates' work.  Please read them now, and come back to the participation and preparation guides throughout the term.

## How This Course Works: Choice and Universal Design

I have designed this course around deliberate choices, in the spirit of Universal Design for Learning.  There are many routes through it and several ways to demonstrate what you have learned, and none of them is the "remedial" path.  You have real authorship over your semester.

- **Choose your direction.**  Everyone completes the same **6 labs**, **3 written assignments**, and **1 team final project** (nothing on the schedule is optional), and every one of them offers **directions** you choose inside the assignment, so you build the same core skill as your classmates, then extend it toward what interests you.  Written Assignment 2 offers a design-document or agent-operating-system direction; Written Assignment 3 offers philosophy, model-cards, governance, regulation, or carbon-cost directions; the final project offers three (a Custom Agent Team, a Responsible AI Audit, or an Open-Source Agent).  The hands-on routes and the analytical routes are equally valid ways to earn your grade, so please build the balance that fits how you learn.
- **Every lab is within reach, on more than one road.**  Every lab has a programming pathway that asks for only intro-level Python, with starter code provided: you extend a working scaffold, never start from a blank page.  **Every lab also has a supported no-code or low-code pathway**, graded on the same rubric, for the same credit: OpenWebUI configuration for the Local Agent and Tools and MCP labs, a Langflow canvas for the RAG Knowledge Base, declarative promptfoo YAML for the Rubric Pipeline, chat windows and a spreadsheet for the Multi-Agent Patterns lab and its Critique and Refine part, a spreadsheet-and-Open-WebUI run sheet for the RAG Quality Checkup pathway inside the RAG Knowledge Base lab, and an attack-and-policy track for the Responsible AI Capstone.  Each lab opens with a **Choose Your Path** table so the decision is in front of you before you start rather than after, and each rubric row states how it is earned on each route, so "equal credit" is something you can check rather than something I assert.
- **Analytical routes are real routes.**  Written Assignments 2 and 3 and Final Project Direction B (the Responsible AI Audit) are fully non-programming paths.  Taking one of them is a real choice about how you want to work, and I do not read it as avoidance.
- **A shared spine.**  The semester-long **Project Thread** is the one path everyone walks together, so that individual choice never means working alone.  It carries the team milestones (charter, stakeholder brief, literature review, proposal, and demo) and the peer review that ties the section together.
- **Depth inside every lab.**  Each of the 6 labs opens with a shared core that everyone builds, then a menu of **directions**: instruction design and agent governance, handoffs between sessions, local model internals, containerization, MCP and OAuth, coding agents, fine-tuning, observability, prompt-injection defense, privacy, explainability, and more.  Pick the direction that pulls you; if the one you want is not on the menu, propose it.
- **Scaffolding you can hold your own work against.**  Every lab and written assignment opens with **Before You Start**, which tells you what it builds on, what to install, and what order to do things in, and closes with a **Self-Check** drawn from its own rubric's *proficient* column, so you can grade your draft before I do.  The labs also carry worked examples and a **Troubleshooting** table, because the most common reason a lab takes twice as long as it should is a setup problem with a known fix.
- **The depth is in the activity, not in a list of links.**  Each session's activity carries the theory, the worked example, and the code, and where a topic runs past the seventy-five minutes we have together, it continues in an extension section at the end of that same activity, clearly marked as self-paced.  Nothing graded assumes those sections.  The readings on the schedule are books, papers, tutorials, and the occasional thing you play with in a browser, and each one says plainly what it is.

If a path you want is not on the menu, please propose it.  The choices are here so you leave this course able to stand up, operate, and reason about an AI system of your own.

## A Note on the Use of Generative AI

In this course we will use generative AI tools extensively, and deliberately.  We will do it in the course of exploring both the capabilities and the risks of these systems, so that you leave prepared to have a highly informed conversation about their merits and their drawbacks for human flourishing, whatever your personal opinion of them turns out to be.  That preparation is the point.  An informed critic and an informed builder need the same working knowledge, and you cannot pick it up from a distance.

We will seek to model best practices for using these systems through the lens of the four Ursinus Questions: *What should matter to me?  How should we live together?  How can we understand the world?  What will I do?*  Those questions are not decoration on a technical course.  They are the questions that decide what you build, who you build it for, and what you refuse to build.

One way we will hold to that is by using AI systems to enhance and elevate our creative and critical capabilities rather than to substitute for them.  Pope Leo XIV takes up exactly this question in his encyclical letter [*Magnifica Humanitas: On Safeguarding the Human Person in the Time of Artificial Intelligence*](https://www.vatican.va/content/leo-xiv/en/encyclicals/documents/20260515-magnifica-humanitas.html) (15 May 2026), which argues that technology "should not be considered, in itself, as a force antagonistic to humanity," that human work is where people "bring their freedom, creativity and capacity for cooperation into play, contributing to the cultural and moral elevation of society" (&para;37), and that the splendor of human dignity is something "no machine can ever replace" (&para;15).  Read alongside the four Questions, that is a useful standard to hold our own work to.

So, to avoid the risk of AI replacing the creative pursuits it should be extending, I ask that you **not use AI tools or systems to simply generate the work you do in this class**.  Use them instead to execute plans that you thoughtfully designed.  That distinction is most of what this course teaches.  The design-first discipline running through the written assignments, and the AI-use disclosure that every assignment asks for, both exist to keep the thinking yours.  We will discuss and debate these questions as a class throughout the semester, and you are not expected to arrive at my answer.

## A Project-Based Course: Process, Teams, and Community Partners

This course is **project-based** on purpose.  The semester-long team project is how the learning happens, and it is not the destination.  I put as much graded emphasis on the *process*, meaning how your team frames a problem, works with stakeholders, manages itself, and communicates, as on the product you demo.  Five process goals run through every Project-Thread milestone:

- **Collaborative inquiry:** team coordination, shared decision-making, and productive disagreement.
- **Problem framing and scoping:** defining an ill-structured problem, identifying its stakeholders, and iterating on the question.
- **Evidence-based communication:** synthesizing sources and tailoring your argument to technical and non-technical audiences.
- **Structured reflection:** metacognitive awareness of your own learning and your team's dynamics.
- **Stakeholder engagement:** grounding the work in a real community partner's needs and translating your system for them.

**Community partners.**  Each team anchors its project in the needs of a real community stakeholder.  Your Stakeholder Brief, proposal, gallery-walk feedback pass, and Demo Day partner-facing artifact all build on that relationship.  Demo Day itself is a multi-audience presentation, for your technical peers and for the stakeholders your project serves.

**Community partner roster.**  Partners are confirmed each semester and shared in class before the Stakeholder Brief kickoff (week 2), rather than published on this page.  If no partner fits your team's interests, ask: I will broker an introduction within one week of the request.  No team's Stakeholder Brief is blocked by the roster.

This semester the section runs as **4 teams of 4 students**.  That is large enough to rotate roles and small enough that everyone has to carry real work.

I form the teams; you do not have to find each other.  I build project teams from the Team Formation Survey, balancing schedules, work styles, and deadline habits, and every team writes and signs a charter with rotating roles, psychological-safety ground rules, and a conflict repair process.  The intra-team check-ins are where we keep that charter honest.  If your team is struggling, please say so early, either in the confidential pulse of any check-in or in office hours, and we'll work through it together.

There is no midterm or final exam.  Demo Day (Tuesday, December 8) and the registrar's final-exam slot host the final presentations; the project, labs, written assignments, and participation carry the grade.  Our four teams present for about fifteen minutes each during our class meeting; guests attending CS374's Demo Day (same day) are welcome at both.

## How Assignments Are Structured: Purpose, Task, and Criteria

I write every assignment to be transparent about three things, so you are never guessing about what I am asking or how I will judge it:

- **Purpose:** *why* the assignment exists and what capability it builds toward.
- **Task:** *what* you will actually do, in concrete steps.
- **Criteria:** *how* your work will be evaluated.  Every graded assignment carries a rubric with four levels (pre-emerging, beginning, progressing, proficient), so you can see what proficient work looks like before you begin, and can hold your own draft against it.

Please read the Purpose first.  It tells you what the assignment is really for, and that is the fastest way to make good decisions when the task gets open-ended.  Much of this course is open-ended on purpose, because operating real systems is.  Every assignment also asks you to reflect and to disclose your use of AI tools honestly, and I count both as part of the work, for the reasons set out in *A Note on the Use of Generative AI* above.

## Class Activities and Participation (10%)

Our meetings are hands-on POGIL sessions.  You work in your team through activities that build the concepts and run the systems, rather than sitting through lectures.  Class works best when you arrive ready, having worked through the activity, attempted the reading response, and brought a question or something you got stuck on, often something you tried to run on your own machine that did not behave.  Bringing that is how I know the preparation happened, and it is usually where the best discussion starts.

This is a course you do rather than one you watch.  This component values the daily work of showing up prepared, contributing to the shared build, and engaging seriously with your classmates' work.  I assess it across four dimensions: **preparation, contribution, collaboration, and reflection.**  It takes several forms on purpose:

- **In-class activities.**  Your team rotates the POGIL roles (**Manager, Recorder, Presenter, and Reflector**) so that on different days you facilitate, capture the group's thinking, report out, or synthesize.  Posting your team's answers to the class discussion board is participation the whole class learns from.
- **Reading responses and discussion.**  From time to time the agenda sets aside time to discuss a reading or a result, prepared by a short **[reading response](Participation/ReadingResponses)** you write beforehand.  These are marked on the schedule.
- **The student-led Reading Group.**  When a classmate leads a [Reading Group]({{ site.baseurl }}/Assignments/ReadingGroup) discussion, the *audience* has a job too: engaging with the presenter's source and question is part of your participation grade, and the [reading response](Participation/ReadingResponses) guide explains the brief pre-read note or in-session question that earns it.  (Leading a session remains separately available for extra credit.)
- **Project-Thread peer review.**  The structured **SQR** peer reviews (one concrete Strength with evidence, one genuine Question, one Risk with a suggested mitigation) that you give other teams at the stakeholder-brief, proposal, and gallery-walk stages are participation of the most professional kind, and they count here.

The first-week onboarding assignments (the **Overview**, the **Warmup**, and the **Team Formation Survey**) are assessed within this Class Activities and Participation category.

Participation takes more than one form on purpose.  If the spoken room is hard for you, the written channels (the discussion board, reading responses, and SQR cards) are real ways to earn this component.  Being confused is part of learning this material, so please talk with me early and we'll find the path that fits.
