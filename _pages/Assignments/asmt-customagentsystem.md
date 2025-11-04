---
layout: assignment
permalink: Labs/CustomAgentSystem
title: "Lab: Custom Agent Systems — AutoGen (Part 1) + Platform‑Agnostic Multi‑Agent (Part 2)"

info:
  points: 100
  goals:
    - "Experiment with building, defining, and customizing AI agents and skills in AutoGen Studio."
    - "Create and run a session in AutoGen Studio's Playground using a predefined workflow."
    - "Comprehend the principles and methods of creating custom agents programmatically using the AutoGen library."
    - "Implement a custom AI solution using AutoGen, focusing on a specific application."
    - "Evaluate the capabilities and limitations of retrieval-augmented generation agents within the AutoGen framework."
    
  rubric:
    - weight: 15
      description: Implementation and Functionality of Code Solution
      preemerging: The code solution is non-functional or demonstrates significant errors.
      beginning: The code solution is functional but lacks complexity and shows minimal customization.
      progressing: The code solution is well-implemented with good functionality and some level of customization.
      proficient: The code solution is excellently implemented, showing high functionality, customization, and innovation.
    - weight: 20 
      description: Human-Centric Design
      preemerging: A trivial application of the modality is provided without regard to proper signifiers or affordances to facilitate human interaction
      beginning: Some consideration is given to the manner by which the modality is incorporated into the program, but it is not clear at all times to the user what to do and how to interact
      progressing: The user is able to interact with the program using the modality in most cases, with a few minor ambiguities that could be identified through additional testing
      proficient: The user experience is enhanced by the use of the modality
    - weight: 20
      description: Design Report      
      preemerging: No design report is included
      beginning: A design report is included that describes the approach taken to solving the problem and incorporating the modality in a trivial way
      progressing: A design report is included that describes the approach taken to solving the problem and incorporating the modality in a manner that carefully considers the problem from the perspective of one stakeholder
      proficient: A design report is included that describes the approach taken to solving the problem and incorporating the modality through documented discussions and test cases with a variety of stakeholders      
    - weight: 15
      description: Reflective Write-Up on Personalization and Usability
      preemerging: Reflective write-up lacks insight into personalization and usability aspects of the solution.
      beginning: Basic reflection on personalization and usability, but lacks depth and critical analysis.
      progressing: Good reflection, providing insights into personalization and usability with relevant examples.
      proficient: In-depth and insightful reflection on personalization and usability, demonstrating comprehensive understanding.
    - weight: 10
      description: Reflection on Ethical Considerations of Automated Systems
      preemerging: Minimal or no reflection on the ethical implications of using automated systems.
      beginning: Basic understanding of ethical considerations, but lacks depth and practical insights.
      progressing: Good reflection on ethical considerations, showing understanding of implications and responsibilities.
      proficient: In-depth reflection on ethical considerations, demonstrating a comprehensive and responsible approach to automated systems.
    - weight: 20
      description: Creation and Customization of Agents and Skills
      preemerging: Shows minimal understanding and ability in creating or customizing agents and skills.
      beginning: Can create basic agents and skills but lacks customization depth.
      progressing: Good competency in creating and customizing agents and skills with some complexity.
      proficient: Excels in creating highly customized and complex agents and skills, demonstrating innovative thinking.

  readings:
    - rtitle: "AutoGen Studio - Interactively Explore Multi-Agent Workflows"
      rlink: "https://microsoft.github.io/autogen/blog/2023/12/01/AutoGenStudio/"
    - rtitle: "AutoGen Studio"
      rlink: "https://github.com/microsoft/autogen/tree/main/python/packages/autogen-studio"
    - rlink: "https://microsoft.github.io/autogen/docs/Use-Cases/agent_chat/#diverse-applications-implemented-with-autogen"
      rtitle: "Multi-agent Conversation Framework"
    - rlink: "https://www.mlq.ai/building-ai-agents-autogen/"
      rtitle: "Building AI Agents with AutoGen"
    - rlink: "https://microsoft.github.io/autogen/blog/2023/10/18/RetrieveChat/"
      rtitle: "Retrieval-Augmented Generation (RAG) Applications with AutoGen"
    - rlink: "https://github.com/microsoft/autogen/blob/main/notebook/agentchat_groupchat.ipynb"
      rtitle: "Auto Generated Agent Chat: Group Chat"
    - rlink: "https://github.com/microsoft/autogen/blob/main/notebook/agentchat_langchain.ipynb"
      rtitle: "Auto Generated Agent Chat: Task Solving with Langchain Provided Tools as Functions"
      
tags:
  - ai
  - gpt
  - psychology
  
---

In recent years, AI has transformed from an estimator/predictor to a creator with the advent of generative AI.  With the progression of agent systems, AI has become a "doer" capable of engaging multiple personas (or "agents") in conversatios oriented around problem solving.  In this assignment, we will explore the creation of custom AI agents, and develop our own personalized AI solution. 

## Part 1 - Introduction to AutoGen

[AutoGen](https://github.com/microsoft/autogen) is a Microsoft framework that allows you to define various agents that can interact with one another to solve problems using AI.  They can prompt the user for context and input that they use to work together to solve a problem according to a workflow that you can customize.  For example, whereas traditional Chat GPT can create text to respond to questions, an agent can take a problem statement and call functions, invoke APIs, and converse with other agents to provide custom solutions to your inquiry.  

### Part 1.1 - AutoGen Studio - A No-Code Solution

You can specify AutoGen agent behaviors, and invoke those behaviors, in Python.  However, there is also a no-code solution called [AutoGen Studio](https://github.com/microsoft/autogen/tree/main/samples/apps/autogen-studio) in which you can add skills, define agents, and chat with the resulting system using a web interface.  You can install this web interface directly within your local environment.  To do this, run:

```
export HISTIGNORE='*' # skip on Windows
pip install autogenstudio autogen
pip uninstall pyautogen
pip install pyautogen
pip install pyautogen[retrievechat] # pip install pyautogen\[retrievechat\] on zsh shells (mac)
export AUTOGEN_USE_DOCKER=0 # set AUTOGEN_USE_DOCKER=0 on Windows, or $env:AUTOGEN_USE_DOCKER=0 on PowerShell (VSCode)
export OPENAI_API_KEY=<your key here> # replace export with set on Windows, or with $env: on PowerShell as above
autogenstudio ui --port 8081
```

An API key will be provided to you for use in this class.  Please shut down your applications when you're not using them, to avoid incurring additional charges against this API key!  Your instructor is funding this API key directly, and is sharing it with the entire class.  Please be judicious about its usage.  You are welcome to create an account and key for yourself for further exploration, but this is not required for this class.

Once this executes, you can open the autogen tool using a web browser by navigating to [http://localhost:8081](http://localhost:8081).

To try it out, click on the **Build** tab and select **Skills** from the left menu.  You can click on the sample skills to view the code that drives each.  Notice that each invokes a custom API to answer your question (such as scraping a web page, or writing code to create visualizations in `matplotlib`, etc.).  Agents can invoke these skills, which you can think of as functions, to answer questions.

In the **Agents** menu, you can create your own custom agents.  It's possible to do this directly from the **Workflows** section, so just take a look at some of the provided agents for now.  Notice that they can import skills as well as language models like `gpt-4` to answer questions.

In the **Workflows** menu, you can connect an agent to skills by selecting each through the menu.  Try creating one of your own that uses some of the example skills provided.  In this example, we'll use the **Visualization Workflow** which uses the **Visualization Agent** to generate plots using `matplotlib` in Python.

#### Part 1.1.1 - Creating a Session

Click on the **Playground** Tab, and click **New** under **Sessions** on the left menu.  Choose the **Visualization Workflow**, and ask it the following query (from the [Microsoft autogen GitHub repository tutorial page](https://github.com/microsoft/autogen/tree/main/samples/apps/autogen-studio)):

```
Plot a chart of NVDA and TESLA stock price YTD from January 1 of this year to the current date. Save the result to a file named nvda_tesla.png
```

Simply paste this query into the workflow chat page, and give it a few moments to execute.  The chatbot will install Python dependencies for `matplotlib` and other libraries, so this will take a few minutes, but you'll see a plot of the stock when it is finished!

Click below the image to expand the messages.  It provides not only the image that it saved to your session, but also the code that it generated to execute your request.  The agent ran that code automatically.  Sometimes, agents will require more information from the user, and it will ask you questions that you can type in just as with a traditional GPT.  In this case, no such additional information should be needed to answer your query, so you should just see the result.

#### Part 1.1.2 - Creating Custom Skills

Go back to the **Skills** menu under the **Build** tab.  You can click **New** to create a new Skill, which provides the agent additional functionality that it can execute.

Here is a simple example that generates a random story given a theme.  It's not terribly creative as this is a deliberately minimal example, but you could imagine substituting API calls here to execute outside functionality.  Try pasting this into a new Skill definition, and give your Skill a name.

```python
import random

def generate_story(theme):
    """
    Generates a short story based on the given theme.

    Args:
    theme (str): The theme of the story.

    Returns:
    str: A short story.
    """

    # Sample beginnings, middles, and endings for the story
    beginnings = [
        "Once upon a time, in a distant land, ",
        "In a small village, surrounded by mountains, ",
        "In a futuristic city, where technology ruled, "
    ]

    middles = [
        "a young hero decided to embark on a journey, ",
        "an unexpected event turned everything upside down, ",
        "a mysterious figure appeared, offering a challenge, "
    ]

    endings = [
        "and thus, the adventure came to a joyful end.",
        "which led to unexpected friendships and lessons learned.",
        "and the hero's courage changed their world forever."
    ]

    # Randomly select parts of the story
    beginning = random.choice(beginnings)
    middle = random.choice(middles)
    ending = random.choice(endings)

    # Combine the parts to form the story
    story = f"{beginning}when {theme}, {middle}{ending}"

    return story
```

Now, create a new workflow, and when it asks you to specify the Agent, click on the button to customize the Agent.  Under the list of skills you will see an **Add** button, and you can add this new Skill to the list that it can execute.

Go back to the **Playground** and set up a Session with this new workflow.  Tell it to tell you a story about something (you can make up what it is).  The chatbot will take your theme, pass it as a parameter to the skill, and provide you with the response!

### Part 1.2 - Creating Custom Agents with AutoGen

AutoGen Studio is a front-end user interface to AutoGen, but you can create these agents programmatically directly through the AutoGen library.  To do this, we will first provide our OpenAI API key similar to the way we did before.  This time, we'll add the key to a dictionary file, which we'll load in our Python program.  Create a file called `OAI_CONFIG_LIST` and populate it as follows:

```
[
    {
        "model": "gpt-4",
        "api_key": "<your api key here>"
    }
]
```

In addition, create a working directory for the chatbot to store files.  We'll call ours `work`:

```
mkdir work
```

Now, your Python program can do the following:

```python
from autogen import AssistantAgent, UserProxyAgent, config_list_from_json
import autogen

config_list = autogen.config_list_from_json(
    env_or_file="OAI_CONFIG_LIST",
    file_location=".",
    filter_dict={
        "model": {
            "gpt-4",
            "gpt4",
            "gpt-4-32k",
            "gpt-4-32k-0314",
            "gpt-35-turbo",
            "gpt-3.5-turbo",
        }
    },
)
assistant = AssistantAgent("assistant", llm_config={"config_list": config_list})
user_proxy = UserProxyAgent("user_proxy", code_execution_config={"work_dir": "work"})
user_proxy.initiate_chat(assistant, message="Plot a chart of NVDA and TESLA stock price YTD from January 1 of this year to the current date.")
```

This creates the agent (`assistant`), configured with our API key by passing it the filename in which the key is provided, and the user proxy agent (`user_proxy`) which acts as the user typing in questions to the chatbot agent.  Calling `initiate_chat` will pass the message to the chatbot agent, and any followup questions will be prompted to you by the `user_proxy` agent.  Otherwise, the result will appear on-screen.  Of course, this is a console application, so the plot won't appear like it did with AutoGen Studio.  Instead, it will provide you the code that you can execute to generate the plot for yourself, and if the agent is able to execute that code, it will output the plot file to your working directory (called `work`).

### Part 1.3 - Creating Custom Skills

These agents can also provide custom functionality similar to the "Skills" we saw in the AutoGen Studio UI.  Here, they're just functions.

Start out by defining your `config_list` as before to specify your OpenAI API key, and import the following packages:

```python
import json
import os
from typing_extensions import Annotated

import autogen
from autogen import AssistantAgent, UserProxyAgent
```

This time, we'll specify an LLM configuration dictionary that specifies a timeout for calling these custom functions, and we'll pass our `config_list` to that to initialize this particular agent (from the [Microsoft autogen documentation](https://microsoft.github.io/autogen/docs/Use-Cases/agent_chat/#diverse-applications-implemented-with-autogen)):

```python
llm_config = {
    "config_list": config_list,
    "cache_seed": 42,
    "timeout": 120,
}
```

Now, you can create an assistant agent and a user proxy agent, just like before, but we'll specify some custom behaviors (from the [Microsoft autogen documentation](https://microsoft.github.io/autogen/docs/Use-Cases/agent_chat/#diverse-applications-implemented-with-autogen)):

```python
chatbot = autogen.AssistantAgent(
        name="chatbot",
        system_message="You are a chatbot assistant that generates a random number using only the function provided.  Reply with TERMINATE when your task is done.",
        llm_config=llm_config
)

user_proxy = autogen.UserProxyAgent(
        name="user_proxy",
        is_termination_msg=lambda x: x.get("content", "") and x.get("content", "").rstrip().endswith("TERMINATE"),
        human_input_mode="NEVER", # or ALWAYS by default
        max_consecutive_auto_reply=10
)
```

The `system_message` allows you to tell the chatbot more about itself.  You could make it a professor, a student, a travel agent, or anything you can imagine.  Here, we'll tell the agent that it should execute a custom function that we will provide it in order to answer questions.  To help us determine when the response has ended, we'll tell it to respond with the word "TERMINATE" when it has finished.

The `user_proxy` specifies an `is_termination_msg` function that returns true when the message ends with the word `TERMINATE`.  Since we told the agent to respond with `TERMINATE` when it is finished, this gives us an easy way to know when to stop providing input to the chatbot agent.  We also tell it that it can converse with the user agent up to 10 times before finishing.  In this simple example, we will likely never reach that limit.

Additionally, there is a parameter `human_input_mode` which is set to `NEVER`.  This can be changed to `ALWAYS` (or removed as `ALWAYS` is the default) to allow the chatbot to prompt the user with questions for feedback or additional context.

Next, let's provide a custom function to the chatbot, to give it a "Skill" like we did earlier:

```python
@user_proxy.register_for_execution()
@chatbot.register_for_llm(description="Random number generator.")
def gen_random(n: Annotated[int, "Upper limit for random number generation"]) -> str:
    import random
    value = random.randint(0, n)
    return f"{value}"
```

This minimal example tells the agent that it can call the `gen_random` function to compute a random number up to a certain threshold, given as a parameter.  The agent will extract this parameter from your input message, and pass it to the function automatically.

Finally, initiate the chatbot as follows:

```python
user_proxy.initiate_chat(
        chatbot,
        message="Generate 5 random numbers up to 100"
)
```

### Part 1.4 - Retrieval-Augmented Generation Agents with AutoGen

You can also provide your own knowledge base documents that the agent can use to formulate its responses.  For example, we could download the [Ursinus course catalog](https://www.ursinus.edu/live/files/5040-catalog-2023) as a PDF, and save it in a `docs` subdirectory of our project, and our agent would read that document and use it to formulate responses.  We could populate this directory with other documents as well (for example, past course catalogs).

As before, set up your `config_list` and `llm_config` variables, and import the following packages:

```python
import json
import os

import autogen
from autogen.agentchat.contrib.retrieve_assistant_agent import RetrieveAssistantAgent
from autogen.agentchat.contrib.retrieve_user_proxy_agent import RetrieveUserProxyAgent
```

And, as before, create your chatbot and user proxy agents (from the [Microsoft autogen blog post about Retrieval-Augmented Generation (RAG)](https://microsoft.github.io/autogen/docs/Use-Cases/agent_chat/#diverse-applications-implemented-with-autogen)):

```python
assistant = RetrieveAssistantAgent(
    name="assistant",
    system_message="You are a helpful assistant.",
    llm_config=llm_config,
)

ragproxyagent = RetrieveUserProxyAgent(
    name="ragproxyagent",
    max_consecutive_auto_reply=3,
    retrieve_config={
        "task": "qa",
        "docs_path": [
            os.path.join(os.path.abspath(""), "docs"),
        ]
    }
)
```

This agent reads documents from the `docs` directory, under the current directory.  Now, you can interact with the agent like before:

```python
assistant.reset()
ragproxyagent.initiate_chat(assistant, message=ragproxyagent.message_generator, problem="Recommend courses based on my interest in Machine Learning and Biomedicine")
```

Since the catalog knows when courses are generally offered, and what prerequisites courses have, etc., you could ask it more interesting questions like "Suggest courses for the Fall Semester of 2024 for a Computer Science major."  Additionally, you could add documents to the knowledge base repository that provide information about major requirements.  `docs_path` supports URL's, so you could provide it the URL of the course major page itself and create a "virtual advisor" agent.

### Part 1.5 - Multi-Agent Collaborations

You can create multiple agents by providing custom personas via the agent `system_message` (from the [Microsoft autogen GroupChat Documentation](https://github.com/microsoft/autogen/blob/main/notebook/agentchat_groupchat.ipynb)):

```python
import autogen
from autogen import AssistantAgent, UserProxyAgent, config_list_from_json

coder = autogen.AssistantAgent(
    name="Coder",
    llm_config=llm_config,
)

pm = autogen.AssistantAgent(
    name="Product_manager",
    system_message="Creative in software product ideas.",
    llm_config=llm_config,
)

qa = autogen.AssistantAgent(
    name="Tester",
    system_message="QA expert in unit, regression, and user acceptance testing.",
    llm_config=llm_config,
)

rq = autogen.AssistantAgent(
    name="Requirements_Engineer",
    system_message="Software requirements expert capable of interfacing between the product manager, tester, and user proxy agent to ensure software meets user needs.",
    llm_config=llm_config,
)
```

To create the group of agents, pass an array to the `GroupChat` constructor:

```python
groupchat = autogen.GroupChat(agents=[user_proxy, coder, pm, qa, rq], messages=[], max_round=100)
manager = autogen.GroupChatManager(groupchat=groupchat, llm_config=llm_config)
```

And initiate with a user proxy agent as usual:

```python
user_proxy = autogen.UserProxyAgent(
    name="User_proxy",
    system_message="A human admin.",
    code_execution_config={
        "last_n_messages": 2,
        "work_dir": "groupchat",
        "use_docker": False,
    },  # Please set use_docker=True if docker is available to run the generated code. Using docker is safer than running the generated code directly.
    human_input_mode="TERMINATE",
)

user_proxy.initiate_chat(
    manager, message="Work with the requirements engineer to propose a new software product that allows students to identify courses according to their interests, and work with the coder a solution in Python and flask using the MVC framework that queries a relational database in sqlite to allow students to identify such courses.  Specify detailed requirements to be implemented by the coder.  Include API URL endpoints in REST that use the CRUD pattern, and write classes that will be written to the database.  Create unit tests for all code modules via the testing agent.  It is not necessary to execute the code locally, so there is no need to run python or install any libraries directly; just write and save the code to the workng directory.  When finished, reply with the word TERMINATE to end your interaction with the other agents.  When you receive TERMINATE from an agent, stop communicatig with that agent."
)
```

Don't forget your `config_list` and `llm_config` configuration objects as before, and create a directory called `work` and called `groupchat` to save the intermediate files created by the agents.

### Part 1.6 - Invoking Langchain Tools As Custom Functions

[LangChain](https://www.langchain.com/) provides toolchain [integrations](https://python.langchain.com/docs/integrations/tools) to connect to API and search functionality such as Google, StackExchange, and others.  You can integrate these into your autogen agents by providing these as custom functions that the agents can invoke, just as we did in Part 1.3 above.

Install langchain and the Stack Exchange integration as follows:

```
pip install Langchain stackapi
```

Set up your agents and configuration like you did in Part 1.3:

```python
import json
import os
from typing_extensions import Annotated

import autogen
from autogen import AssistantAgent, UserProxyAgent

chatbot = autogen.AssistantAgent(
        name="chatbot",
        system_message="You are a chatbot assistant that searches Stack Exchange using the provided function to answer coding questions.  Reply with TERMINATE when your task is done.",
        llm_config=llm_config
)

user_proxy = autogen.UserProxyAgent(
        name="user_proxy",
        is_termination_msg=lambda x: x.get("content", "") and x.get("content", "").rstrip().endswith("TERMINATE"),
        human_input_mode="NEVER", # or ALWAYS by default
        max_consecutive_auto_reply=10
)
```

This time, we'll map a function that invokes the langchain functionality to query StackExchange:

```python
@user_proxy.register_for_execution()
@chatbot.register_for_llm(description="Stack Exchange query.")
def query_stackexchange(q: Annotated[str, "Query for Stack Exchange"]) -> str:
    import stackapi
    from langchain_community.utilities import StackExchangeAPIWrapper
    stackexchange = StackExchangeAPIWrapper()
    result = stackexchange.run(q)
    return result
```

And, as usual, kick off the agent:

```python
user_proxy.initiate_chat(
        chatbot,
        message="Help me figure out what no module named pycrypto means."
)
```

## Part 2 - Developing Your own AI Solution

Using the AutoGen AI Studio or the AutoGen library, create a custom agent with skills for a personalized solution (for example, a "virtual academic advisor," or a programming tutor, etc.).  

You may select from this non-exhaustive list of possibilities:

* A tutor for Introduction to Java students
* A video game that does not feature text-based signifier instructions
* Learning another language

Write up a tutorial to re-create your solution.  In addition, reflect upon the ethical considerations of using your solution.  For example, what could go wrong by replacing a faculty advisor with a virtual one; does this mean one should not use a virtual advising solution at all?


## Part 3 - Coding a Custom Agent system

Using the the Ollama API, create a custom agent system with skills for a personalized solution such as the one you developed in Part 2 above. 

Below is a minimal Python template for building a small agent team using **Ollama**. This example shows how to create a Planner and a Solver that collaborate. You should extend this by adding more agents (e.g., Researcher, Reviewer) and customizing their system prompts.


```python
import requests, json


class OllamaAgent:
    def __init__(self, name, system_prompt, model="llama3"):
        self.name = name
        self.system_prompt = system_prompt
        self.model = model
        self.memory = []


    def chat(self, message):
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": self.system_prompt},
                    *self.memory,
                {"role": "user", "content": message}
            ]
        }

        r = requests.post("http://localhost:11434/api/chat", json=payload)
        r.raise_for_status()
        data = r.json()
        reply = data.get("message", {}).get("content", "")
        self.memory.append({"role": "user", "content": message})
        self.memory.append({"role": "assistant", "content": reply})

        return reply


# Example usage
planner = OllamaAgent("Planner", "You are a Planner agent. Break problems into steps and assign to Solver.")
solver = OllamaAgent("Solver", "You are a Solver agent. Perform calculations and return results clearly.")


plan = planner.chat("We need to calculate the break-even point: price=15, fixed=2000, var=4")
print("Planner:", plan)


solution = solver.chat("Calculate attendees = fixed/(price - var). Use 2000, 15, 4.")
print("Solver:", solution)
```

- Run `ollama pull llama3` first to download the model.
- Extend this by creating additional `OllamaAgent` instances with custom system prompts.
- Add a simple orchestrator loop to coordinate communication between agents.
