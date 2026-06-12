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
  ical: files/CS357.ics
  course_prerequisites: "Prerequisites: CS-170 or CS-173 or DATA-201, or permission from the instructor."
  course_start_date: "2026/08/24"
  course_end_date: "2026/12/07"
  course_description: "A technical introduction to the tools and practices that have evolved from artificial intelligence (AI) and large language models that considers the role of technology through the lens of the Ursinus Questions. This course prepares students to create and interact with conversational virtual assistants and multi-agent systems that achieve goal-oriented outcomes. Students will explore the foundations and history of artificial intelligence that enabled the technical underpinnings of generative AI, with a particular emphasis on the ethical, social, and intellectual property implications of the nature of the training data sets used to form large language models. The course includes a practical discussion of responsible AI from the perspective of creators and of consumers and stakeholders. Students will apply current design patterns in AI with respect to large language models to create and present a technical project using generative AI, and will lead a discussion focused on practices for responsible AI within the context of their chosen project. Prerequisites: CS-170 or CS-173 or DATA-201, or permission from the instructor. Four hours per week. Four semester hours."
  questions: |
    This semester, we organize the course around a single guiding idea: an agent is a system that perceives, plans, and acts toward a goal. We will collectively consider questions like:
    <ul>
    <li>What does it mean for a machine to act on our behalf, and how does delegation to an agent differ from using a tool?</li>
    <li>How do the foundations of generative AI (embeddings, attention, retrieval) enable, and limit, what agents can reliably do?</li>
    <li>How do the assumptions embedded in training datasets influence the behavior of agents, and what responsibilities do creators and users have in mitigating these effects?</li>
    <li>When should an agent run locally and privately, and when is it appropriate to rely on hosted services?</li>
    <li>How can multi-agent designs (debate, critique and refine, consensus) improve reliability, and what new failure modes do they introduce?</li>
    <li>How can system design align agent outcomes with ethical principles, and who is accountable when an autonomous system errs?</li>
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
  midtermexam: 
    - mdate: "N/A"
      mstarttime: "N/A"
      mendtime: "N/A"
      mroom: "N/A"       
  finalexam: 
    - fdate: "TBD"
      fstarttime: "TBD"
      fendtime: "TBD"
      froom: "Pfahler 107" 
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
    starttime: "10:00 AM"
    endtime: "12:00 PM"
    location: "Pfahler Hall 101L"  
  - day: "R"
    starttime: "10:00 AM"
    endtime: "12:00 PM"
    location: "Pfahler Hall 101L"           
    
textbooks:
- title: "Artificial Intelligence: A Guide for Thinking Humans"
  authors: "Melanie Mitchell"
  edition: "Revised Edition"
  isbn: "978-1-250-40485-5"
  link: false
  isrequired: true 
  freelyavailable: false
- title: "AI by Hand"
  authors: "Tom Yeh"
  link: "https://www.scribd.com/document/726922630/AI-by-Hand-Vol-1"
  isrequired: true
  freelyavailable: "https://www.scribd.com/document/726922630/AI-by-Hand-Vol-1"
- title: "The Philosophy of Artificial Intelligence"
  authors: "Margaret A. Boden, editor"
  isbn: "978-0198248545"
  link: false
  isrequired: false 
  freelyavailable: false
  
objectives:
- objective: "Analyze the ethical implications of AI agents acting on behalf of people, using case studies, governance frameworks, and design justice principles."
- objective: "Design agentic AI systems, including prompts, retrieval pipelines, tools, and multi-agent orchestrations, that augment human capabilities while adhering to ethical guidelines."
- objective: "Evaluate the reliability of AI agents across tasks and disciplines, identifying best practices, failure modes, and risks associated with their use."
- objective: "Create documentation, evaluations, and governance plans for the responsible deployment of agentic AI technologies."

goals:
- goal: "Implement the perceive, plan, act loop of an agent using a locally hosted language model."
- goal: "Explain how tokens, embeddings, attention, and sampling parameters shape the behavior of generative models, and verify these explanations with by-hand calculations."
- goal: "Construct a retrieval-augmented generation pipeline over a personal knowledge base, and evaluate its retrieval and grounding quality."
- goal: "Compose multi-agent systems using orchestration patterns including pipelines, critique and refine, debate, and stochastic consensus, while keeping each agent's context window small and focused."
- goal: "Evaluate agent outputs using human rubrics and LLM-as-judge pipelines, and articulate the limits of each."
- goal: "Author a governance and responsible-use analysis for an agentic system of your own design, and present it to a public audience."

grade_breakdown:
- category: "Labs (5)"
  weight: "35%"
- category: "Written Assignments (3)"
  weight: "20%"
- category: "Final Project: Custom Agent Team"
  weight: "25%"
- category: "Class Activities and Participation"
  weight: "10%"
- category: "Reflection Notebook"
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
- week: "1"
  date: "0"
  title: "Welcome: What Is AI, and What Is an Agent?"
  link: "https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-welcomeagents.md"
  deliverables:
  - dtitle: "Warmup Assignment Handed Out"
    dlink: "Assignments/Warmup"
    points: "25"
    rubricpath: "_pages/Assignments/asmt-warmup.md"
  readings:
  - rtitle: "Mitchell, Prologue and Chapter 1"
- week: "1"
  date: "1"
  title: "The Agent Loop: Perceive, Plan, Act"
  link: "https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-agentloop.md"
  readings:
  - rtitle: "Mitchell, Chapter 2"
  - rtitle: "Supplemental Tutorial: Shell Fundamentals for Agent Supervision"
    rlink: "https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-shellbasics.md"
- week: "2"
  date: "0"
  title: "Prompt Engineering as Agent Design: Personas and System Prompts"
  link: "https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-promptengineering.md"
  readings:
  - rtitle: "Supplemental Tutorial: Agentic CLI Tools (Claude Code, Codex, Gemini CLI, and Friends)"
    rlink: "https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-agentclis.md"
- week: "2"
  date: "1"
  title: "Running Your Own AI: Ollama, OpenWebUI, and Private Local Models"
  link: "https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-localai.md"
  deliverables:
  - dtitle: "Warmup Assignment Due"
    dlink: "Assignments/Warmup"
    points: "25"
    rubricpath: "_pages/Assignments/asmt-warmup.md"
  - dtitle: "Lab 1: Your First Local Agent Handed Out"
    dlink: "Assignments/LocalAgent"
    points: "100"
    rubricpath: "_pages/Assignments/lab-localagent.md"
  readings:
  - rtitle: "Supplemental Tutorial: Docker from First Principles"
    rlink: "https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-docker.md"
- week: "3"
  date: "0"
  title: "Why Different Answers Every Time? Sampling, Temperature, and Generation"
  link: "https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-samplinggeneration.md"
- week: "3"
  date: "1"
  title: "Hallucinations and Evaluating Agent Outputs"
  link: "https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-evaluatingoutputs.md"
  readings:
  - rtitle: "Mitchell, Chapter 3"
- week: "4"
  date: "0"
  title: "Tokens and Embeddings: How Agents Represent Meaning"
  link: "https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-tokensembeddings.md"
  deliverables:
  - dtitle: "Lab 1: Your First Local Agent Due"
    dlink: "Assignments/LocalAgent"
    points: "100"
    rubricpath: "_pages/Assignments/lab-localagent.md"
  - dtitle: "Written Assignment: Prompt Patterns and AI by Hand Handed Out"
    dlink: "Assignments/PromptPatterns"
    points: "100"
    rubricpath: "_pages/Assignments/asmt-promptpatterns.md"
- week: "4"
  date: "1"
  title: "Attention and Transformers, Conceptually and by Hand"
  link: "https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-attentiontransformers.md"
  readings:
  - rtitle: "AI by Hand, Attention worksheets"
- week: "5"
  date: "0"
  title: "Retrieval-Augmented Generation with Chroma"
  link: "https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-rag.md"
- week: "5"
  date: "1"
  title: "RAG Quality: Chunking, Clustering, and Reranking"
  link: "https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-ragquality.md"
  deliverables:
  - dtitle: "Written Assignment: Prompt Patterns and AI by Hand Due"
    dlink: "Assignments/PromptPatterns"
    points: "100"
    rubricpath: "_pages/Assignments/asmt-promptpatterns.md"
  - dtitle: "Lab 2: A RAG Knowledge Base of Your Own Handed Out"
    dlink: "Assignments/RAGKnowledgeBase"
    points: "100"
    rubricpath: "_pages/Assignments/lab-ragknowledgebase.md"
  readings:
  - rtitle: "Supplemental Tutorial: The LLM Wiki Pattern (Wikis versus RAG)"
    rlink: "https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-llmwiki.md"
- week: "6"
  date: "0"
  title: "Memory and the Small Context Window Principle"
  link: "https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-memorycontext.md"
  readings:
  - rtitle: "Supplemental Tutorial: An Obsidian Second Brain with Agent Sync"
    rlink: "https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-secondbrain.md"
- week: "6"
  date: "1"
  title: "Tool Use and Function Calling"
  link: "https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-tooluse.md"
- week: "7"
  date: "0"
  title: "Connecting Agents to the World: MCP and APIs"
  link: "https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-mcp.md"
  deliverables:
  - dtitle: "Lab 2: A RAG Knowledge Base of Your Own Due"
    dlink: "Assignments/RAGKnowledgeBase"
    points: "100"
    rubricpath: "_pages/Assignments/lab-ragknowledgebase.md"
  readings:
  - rtitle: "Supplemental Tutorial: The Local Agent Stack (Tiers, Ports, and Compose)"
    rlink: "https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-agentstack.md"
  - rtitle: "Optional Lab: Compose and Verify a Local Agent Stack"
    rlink: "https://www.billmongan.com/Ursinus-CS357/Assignments/AgentStack"
- week: "7"
  date: "1"
  title: "No Class: APEX Experiential Learning Day"
- week: "8"
  date: "0"
  title: "No Class: Fall Break"
- week: "8"
  date: "1"
  title: "Orchestration Patterns: Pipelines, Routers, and Planners"
  link: "https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-orchestration.md"
  deliverables:
  - dtitle: "Lab 3: Critique and Refine Handed Out"
    dlink: "Assignments/CritiqueRefine"
    points: "100"
    rubricpath: "_pages/Assignments/lab-critiquerefine.md"
- week: "9"
  date: "0"
  title: "The Critique and Refine Pattern"
  link: "https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-critiquerefine.md"
- week: "9"
  date: "1"
  title: "Multi-Agent Debate"
  link: "https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-multiagentdebate.md"
- week: "10"
  date: "0"
  title: "Stochastic Multi-Agent Consensus"
  link: "https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-consensus.md"
  deliverables:
  - dtitle: "Lab 3: Critique and Refine Due"
    dlink: "Assignments/CritiqueRefine"
    points: "100"
    rubricpath: "_pages/Assignments/lab-critiquerefine.md"
  - dtitle: "Lab 4: Multi-Agent Debate and Consensus Handed Out"
    dlink: "Assignments/MultiAgentDebate"
    points: "100"
    rubricpath: "_pages/Assignments/lab-multiagentdebate.md"
- week: "10"
  date: "1"
  title: "Agent Teams: Specialists over Monoliths"
  link: "https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-agentteams.md"
  deliverables:
  - dtitle: "Final Project: Custom Agent Team Handed Out"
    dlink: "Projects/AgentTeam"
    points: "100"
    rubricpath: "_pages/Projects/proj-agentteam.md"
  readings:
  - rtitle: "Supplemental Tutorial: Publishing Artifacts (GHCR, Docker Hub, and npm)"
    rlink: "https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-publishing.md"
  - rtitle: "Optional Capstone: ShipIt (Build, Test, CI, and Publish an Artifact)"
    rlink: "https://www.billmongan.com/Ursinus-CS357/Assignments/ShipIt"
- week: "11"
  date: "0"
  title: "Visual Agent Building with Langflow"
  link: "https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-visualagents.md"
  readings:
  - rtitle: "Supplemental Tutorial: Cloudflare Workers and Pages with Wrangler"
    rlink: "https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-cloudflare.md"
- week: "11"
  date: "1"
  title: "Evaluating Agents: LLM-as-Judge and Rubric Pipelines"
  link: "https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-llmasjudge.md"
  deliverables:
  - dtitle: "Lab 4: Multi-Agent Debate and Consensus Due"
    dlink: "Assignments/MultiAgentDebate"
    points: "100"
    rubricpath: "_pages/Assignments/lab-multiagentdebate.md"
  - dtitle: "Lab 5: An LLM Rubric-Grading Pipeline Handed Out"
    dlink: "Assignments/RubricPipeline"
    points: "100"
    rubricpath: "_pages/Assignments/lab-rubricpipeline.md"
- week: "12"
  date: "0"
  title: "Agentic Case Studies: Migration, Browsing, and Research Agents"
  link: "https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-agentcasestudies.md"
  deliverables:
  - dtitle: "Final Project Proposal Due"
    dlink: "Projects/AgentTeam"
    points: "100"
    rubricpath: "_pages/Projects/proj-agentteam.md"
- week: "12"
  date: "1"
  title: "Training Data and Bias"
  link: "https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-biasdata.md"
  readings:
  - rtitle: "Coded Bias (film), watch before class"
    rlink: "https://www.codedbias.com/"
- week: "13"
  date: "0"
  title: "Intellectual Property, Privacy, and the Case for Local AI"
  link: "https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-ipprivacy.md"
  deliverables:
  - dtitle: "Lab 5: An LLM Rubric-Grading Pipeline Due"
    dlink: "Assignments/RubricPipeline"
    points: "100"
    rubricpath: "_pages/Assignments/lab-rubricpipeline.md"
- week: "13"
  date: "1"
  title: "Governance and Policy Writing"
  link: "https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-governance.md"
  deliverables:
  - dtitle: "Written Assignment: Governance and Policy Handed Out"
    dlink: "Assignments/Governance"
    points: "100"
    rubricpath: "_pages/Assignments/asmt-governance.md"
- week: "14"
  date: "0"
  title: "Explainability and Human-Centric Design"
  link: "https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-explainability.md"
  readings:
  - rtitle: "Supplemental Tutorial: The AI Maker Module (Testing, CI, and Human-Centric Design)"
    rlink: "https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-aimaker.md"
- week: "14"
  date: "1"
  title: "No Class: Thanksgiving Break"
- week: "15"
  date: "0"
  title: "Project Studio and Gallery Walk"
  link: "https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-projectstudio.md"
  deliverables:
  - dtitle: "Written Assignment: Governance and Policy Due"
    dlink: "Assignments/Governance"
    points: "100"
    rubricpath: "_pages/Assignments/asmt-governance.md"
- week: "15"
  date: "1"
  title: "Final Project Presentations"
  deliverables:
  - dtitle: "Final Project: Custom Agent Team Due"
    dlink: "Projects/AgentTeam"
    points: "100"
    rubricpath: "_pages/Projects/proj-agentteam.md"
---
