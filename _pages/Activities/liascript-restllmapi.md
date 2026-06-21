# RESTful LLM Access: The api/v1 Paradigm
<!--
author:   William Mongan
language: en
narrator: US English Male

comment: Render with https://liascript.github.io/course/?https://github.com/BillJr99/Ursinus-CS357/blob/gh-pages/_pages/Activities/liascript-restllmapi.md or locally via https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-restllmapi.md

import: https://raw.githubusercontent.com/liascript/CodeRunner/master/README.md

link:   https://cdn.jsdelivr.net/gh/BillJr99/Ursinus-Boilerplate-Assets@main/css/liascript-custom.css?v=2025-08-23-4
        https://fonts.googleapis.com/css2?family=Lexend+Deca&display=swap

-->

# RESTful LLM Access: The api/v1 Paradigm

This module develops the mechanics of talking to a language model over HTTP — the protocol that all provider-agnostic AI code uses under the hood. We move from **what REST is $\rightarrow$ the two key LLM endpoints $\rightarrow$ writing the same request three ways $\rightarrow$ tool calling over the API $\rightarrow$ switching providers by changing one line**.

---

## Directions and Group Roles

Work in your POGIL team with rotated roles (**Manager**, **Recorder**, **Presenter**, **Reflector**). Consider each model and question individually first, then discuss with your group. The Recorder posts answers to the Class Activity Questions discussion board; the Presenter reports out areas of disagreement or alternative approaches. After class, respond to the reflective prompt individually in your notebook.

---

## Key Concepts

| Term | Plain-English Definition | Example You'll See Today |
|------|--------------------------|--------------------------|
| **REST API** | A web interface where you send an HTTP request to a URL with a JSON body and receive a JSON response; no SDK required | `POST http://localhost:11434/v1/chat/completions` with a JSON body |
| **Endpoint** | A specific URL + HTTP method combination that performs one action | `POST /v1/chat/completions` for inference, `GET /v1/models` for listing |
| **OpenAI-compatible** | A server that accepts the same JSON request format as the `/v1/chat/completions` endpoint, regardless of which model it actually runs | Ollama, LiteLLM, vLLM, LocalAI all accept the same request body |
| **`base_url`** | The root address that an SDK prepends to every endpoint path; changing it redirects all calls to a different server | `base_url="http://localhost:11434/v1"` points the SDK at a local Ollama instance |
| **Tool call** | A structured JSON object the model returns instead of plain text when it wants to invoke a function; the surrounding program executes the function and sends back the result | `{"tool_calls": [{"function": {"name": "get_weather", "arguments": "{\"city\": \"Collegeville\"}"}}]}` |
| **Streaming** | Sending the model's response one token at a time as it is generated, rather than waiting for the full response | `"stream": true` in the request body; response arrives as a series of `data: {...}` lines |
| **LiteLLM** | A proxy server and Python library that accepts OpenAI-format requests and translates them to the format required by 100+ different providers | `litellm.completion(model="ollama/llama3.2", messages=[...])` |

---

## 0. Environment Check

This activity uses a locally running Ollama instance. Verify it is running before Part I.

---

## Code Cell

```python
import requests

def check_ollama():
    try:
        r = requests.get("http://localhost:11434/v1/models", timeout=5)
        models = r.json().get("data", [])
        print("Ollama is running. Available models:")
        for m in models:
            print(f"  - {m['id']}")
    except Exception as e:
        import traceback
        traceback.print_exc()
        print("Ollama is not reachable. Ask your instructor for the correct host address.")

check_ollama()
```

---

# Part I: REST Fundamentals for LLMs

## 1. What REST Means in Practice

You have used websites and mobile apps your whole life without knowing they communicate over REST. When your browser loads a page or an app fetches your feed, it sends an HTTP request to a URL, the server processes it and sends back structured data, and the client displays the result. Language model inference works exactly the same way — the "page" being returned is the model's response, encoded as JSON.

**A REST request has four components that you control:** the URL (which server and which action), the HTTP method (`GET` for reading, `POST` for creating or computing), the request body (a JSON object with your inputs), and the response body (a JSON object with the server's output). Every local inference server — Ollama, vLLM, llama.cpp — exposes at least two endpoints. Knowing just these two lets you talk to any of them.

| Endpoint | Method | Purpose | When you use it |
|---|---|---|---|
| `/v1/models` | `GET` | List all models currently loaded on the server | Before sending a chat request, to confirm the model name |
| `/v1/chat/completions` | `POST` | Send a conversation and receive the model's reply | Every inference call in your agent |

The `/v1/` prefix is the **version marker** — it signals that this is the first stable version of the API. If the API changes incompatibly in the future, a new `/v2/` prefix can coexist. This versioning pattern is standard REST design.

---

## 2. Ollama's Two APIs

Ollama exposes two separate HTTP APIs on the same port. The **native Ollama API** (paths starting with `/api/`) uses Ollama-specific field names and defaults. The **OpenAI-compatible API** (paths starting with `/v1/`) uses the same field names and structure as the standard REST interface, which means any code written for the standard will also work against Ollama without modification.

The difference matters in practice because the two APIs use different field names for the same data:

| | Native Ollama (`/api/chat`) | OpenAI-compatible (`/v1/chat/completions`) |
|---|---|---|
| Request field for turn history | `messages` | `messages` (same) |
| Request field for model name | `model` | `model` (same) |
| Request field for disabling streaming | `"stream": false` | `"stream": false` (same) |
| **Response field for the reply text** | `message.content` | `choices[0].message.content` |
| **Default streaming behavior** | Streams by default | Does not stream by default |

**The critical difference is in the response structure.** Code that reads `response["message"]["content"]` works against the native API but breaks silently against the OpenAI-compatible API, which wraps the reply inside a `choices` array. This is the source of many confusing "empty response" bugs.

[[MC]]
In a response from `POST /v1/chat/completions`, which JSON path contains the model's reply text?
- ( ) `response["message"]["content"]`
- ( ) `response["content"]`
- (x) `response["choices"][0]["message"]["content"]`
- ( ) `response["data"]["text"]`

> **⚠️ Common Misconception:** "The OpenAI Python SDK only works if you have an OpenAI account and API key." This is false. The SDK's `OpenAI` client accepts a `base_url` parameter that redirects every call to any server that speaks the same protocol. You still need to pass an `api_key` argument, but the server ignores it — Ollama accepts any string, including `"ollama"` or `"not-a-real-key"`. The SDK is a convenience wrapper around HTTP; it does not enforce which server you talk to.

---

# Part II: Raw HTTP vs. SDK

## 3. Three Ways to Write the Same Request

Understanding what the SDK does for you requires seeing what happens without it. We will send the same request three ways: first as a raw `curl` command that makes the HTTP protocol visible, then as a Python `requests` call that is portable with no lock-in, then as an OpenAI SDK call that trades explicit HTTP handling for cleaner code. All three produce identical outputs.

---

## Code Cell

```python
import subprocess
import json
import requests

ENDPOINT = "http://localhost:11434/v1/chat/completions"
MODEL = "llama3.2"
PAYLOAD = {
    "model": MODEL,
    "messages": [
        {"role": "system", "content": "You are a helpful assistant. Be concise."},
        {"role": "user", "content": "What is a REST API in one sentence?"}
    ],
    "stream": False,
    "temperature": 0.3
}

# --- Method 1: curl (shows the raw HTTP protocol) ---
curl_cmd = [
    "curl", "-s", "-X", "POST", ENDPOINT,
    "-H", "Content-Type: application/json",
    "-d", json.dumps(PAYLOAD)
]
print("=== Method 1: curl ===")
try:
    result = subprocess.run(curl_cmd, capture_output=True, text=True, timeout=120)
    parsed = json.loads(result.stdout)
    print(parsed["choices"][0]["message"]["content"])
except Exception as e:
    import traceback; traceback.print_exc()

# --- Method 2: Python requests (portable, no SDK) ---
print("\n=== Method 2: requests library ===")
try:
    r = requests.post(ENDPOINT, json=PAYLOAD, timeout=120)
    r.raise_for_status()
    print(r.json()["choices"][0]["message"]["content"])
except Exception as e:
    import traceback; traceback.print_exc()

# --- Method 3: OpenAI Python SDK, pointed at local Ollama ---
print("\n=== Method 3: OpenAI SDK with base_url override ===")
try:
    from openai import OpenAI
    client = OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")
    response = client.chat.completions.create(
        model=MODEL,
        messages=PAYLOAD["messages"],
        stream=False,
        temperature=0.3
    )
    print(response.choices[0].message.content)
except ImportError:
    print("openai package not installed: pip install openai")
except Exception as e:
    import traceback; traceback.print_exc()
```

---

## Model 1: The Three-Method Comparison

After running (or reviewing the projected run of) the code above, examine the three outputs side by side.

### Critical Thinking Questions

1. The `curl` command makes the HTTP request visible as a string. Identify the four components of the REST request in the `curl_cmd` list: which element is the URL, which sets the HTTP method, which sets the content type header, and which is the request body?

   > *Hint: `-X POST` sets the method. `-H` sets a header. `-d` sets the data (body). The URL is the positional argument after the flags. These are the same four components in every REST call, regardless of whether you use curl, requests, or an SDK.*

2. The `requests` version calls `r.raise_for_status()` before reading the response. What does this line do, and what would happen if you omitted it and the server returned an HTTP 500 error?

   > *Hint: HTTP status codes communicate success (2xx) and failure (4xx, 5xx). Without `raise_for_status()`, a 500 response still has a body — but that body is an error message, not a model reply. Reading `r.json()["choices"][0]` from an error body raises a `KeyError`, which is a confusing error to debug.*

3. When would you choose the raw `requests` approach over the OpenAI SDK? Give a specific scenario where the SDK would actually get in your way.

   > *Hint: Think about environments where you cannot install packages (a locked-down server, a browser-based runtime, a very small container image). Also think about custom endpoints that return non-standard response shapes — the SDK validates the response structure and will raise errors if the server returns something unexpected.*

[[MC]]
What does setting `"stream": false` in the request body change at the HTTP protocol level?
- ( ) The server generates fewer tokens in its response
- ( ) The server uses a different model internally for non-streaming requests
- (x) The server sends the complete response in a single HTTP response body instead of as a sequence of server-sent event lines
- ( ) The client receives the response faster because streaming has overhead

> **⚠️ Common Misconception:** "Streaming makes the model generate faster." The model generates tokens at the same rate regardless of whether streaming is enabled. Streaming changes how the tokens are *delivered* — in chunks as they are produced versus all at once at the end. For a user watching a chat interface, streaming feels faster because text appears immediately. For a program that processes the final answer, non-streaming is simpler because the full JSON arrives in one piece.

---

# Part III: Request Construction Deep Dive

## 4. Anatomy of a Chat Completions Payload

Every call to `/v1/chat/completions` sends the same set of fields. Some are required; some are optional with sensible defaults. Understanding each field lets you control the model's behavior precisely and debug unexpected outputs efficiently.

**The `messages` array is the heart of the request.** It is an ordered list of conversation turns, each with a `role` (who is speaking) and `content` (what they said). The three roles are: `"system"` (instructions to the model that persist across the conversation), `"user"` (what the human said), and `"assistant"` (what the model previously said, used to continue a multi-turn conversation). The model reads the entire array before generating its next reply.

$$
\text{payload} = \{\text{model}, \text{messages}: [\{r_i, c_i\}], \text{temperature} \in [0, 2], \text{max\_tokens}, \text{stream}\}
$$

| Field | Type | Required | Effect |
|---|---|---|---|
| `model` | string | Yes | Selects which loaded model handles the request |
| `messages` | array | Yes | The full conversation history in role/content pairs |
| `temperature` | float | No (default 1.0) | Controls randomness: 0.0 = deterministic, 2.0 = very random |
| `max_tokens` | int | No | Hard cap on reply length; the model stops generating at this count |
| `stream` | bool | No (default false for /v1/) | Whether to use server-sent events for incremental delivery |
| `tools` | array | No | Function definitions the model may invoke |
| `tool_choice` | string or object | No | Whether the model must call a tool, may call one, or must not |

---

## 5. Tool Calling Over the REST API

Tool calling is how agents use the REST API to act on the world. Instead of returning plain text, the model returns a `tool_calls` array containing a function name and a JSON-encoded argument string. The surrounding program executes the function, then sends the result back as a new message with `role: "tool"`. This exchange repeats until the model returns a final plain-text reply instead of a tool call.

**The model does not execute the function.** The model only decides *which* function to call and *what arguments* to pass. The program is responsible for everything that actually happens — the network request, the database query, the file write. This is the same separation we saw in the agent loop activity.

---

## Code Cell

```python
import json
import requests

ENDPOINT = "http://localhost:11434/v1/chat/completions"
MODEL = "llama3.2"

# Define a tool the model can call
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get the current weather for a city.",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "City name, e.g. 'Collegeville, PA'"
                    }
                },
                "required": ["city"]
            }
        }
    }
]

def get_weather(city):
    """Simulated weather lookup."""
    return json.dumps({"city": city, "temperature": 62, "condition": "partly cloudy"})

def run_tool_loop(user_message):
    messages = [
        {"role": "system", "content": "You are a helpful assistant. Use the get_weather tool when asked about weather."},
        {"role": "user", "content": user_message}
    ]

    for step in range(3):
        try:
            r = requests.post(ENDPOINT, json={
                "model": MODEL,
                "messages": messages,
                "tools": tools,
                "tool_choice": "auto",
                "stream": False,
                "temperature": 0.0
            }, timeout=120)
            r.raise_for_status()
            response_msg = r.json()["choices"][0]["message"]
        except Exception as e:
            import traceback; traceback.print_exc()
            return

        # If the model returned plain text, we are done
        if not response_msg.get("tool_calls"):
            print(f"Final answer: {response_msg['content']}")
            return

        # Process each tool call the model requested
        messages.append(response_msg)
        for tc in response_msg["tool_calls"]:
            fn_name = tc["function"]["name"]
            fn_args = json.loads(tc["function"]["arguments"])
            print(f"[step {step}] Model called {fn_name}({fn_args})")

            if fn_name == "get_weather":
                result = get_weather(**fn_args)
            else:
                result = json.dumps({"error": f"unknown tool: {fn_name}"})

            # Send the tool result back as a "tool" role message
            messages.append({
                "role": "tool",
                "tool_call_id": tc["id"],
                "content": result
            })

    print("Step budget exceeded without a final answer.")

run_tool_loop("What is the weather like in Collegeville, PA right now?")
```

---

## Model 2: Tool Call Trace

Examine the printed trace from the tool loop above, or walk through it with your team using the code listing.

### Critical Thinking Questions

4. Trace the `messages` list at the start of each loop iteration for the weather question. Write out the full list after step 0 completes (after the tool result has been appended). How many elements does it contain, and what is each element's `role`?

   > *Hint: Start with system + user (2 elements). After step 0: the model's assistant message (with tool_calls) is appended, then the tool result message (role: "tool") is appended. That gives 4 elements total going into step 1.*

5. The tool result is sent with `"role": "tool"` and a `"tool_call_id"`. Why does the protocol require a `tool_call_id`? What problem would occur if the model made two tool calls simultaneously and the results came back without IDs?

   > *Hint: If a model calls `get_weather("Collegeville")` and `get_weather("Philadelphia")` in the same response, two tool result messages come back. The `tool_call_id` lets the model match each result to the call that produced it. Without IDs, the model cannot tell which result belongs to which city.*

6. The system prompt says "Use the get_weather tool when asked about weather." If the user instead asks "What is 2 + 2?", predict what `response_msg.get("tool_calls")` will return and explain why.

   > *Hint: `tool_choice: "auto"` means the model decides whether a tool call is appropriate. A math question does not match the description of `get_weather`, so the model should return plain text with `tool_calls` absent or `None` from the response.*

> **⚠️ Common Misconception:** Setting `tool_choice: "auto"` does not guarantee the model will always call a tool. It means the model may call a tool if it judges one to be appropriate. The model will return plain text when it believes it can answer without using a tool. If you need to force a tool call (for testing, or to guarantee structured output), set `tool_choice: {"type": "function", "function": {"name": "your_tool_name"}}`.

---

# Part IV: Provider Portability

## 6. LiteLLM as a Universal Proxy

Once you understand the `/v1/chat/completions` protocol, you can write agent code that works against any compliant server by changing two variables: `base_url` and `model`. LiteLLM formalizes this pattern into a library and proxy server that accepts OpenAI-format requests and translates them internally to whatever format the target provider requires — whether that is Ollama locally, a cloud inference API, or a self-hosted vLLM cluster.

**The developer experience is identical across providers.** You write the request once in OpenAI format. LiteLLM handles the translation. If you switch providers, you update a configuration file; your agent code is untouched. This portability has a cost: LiteLLM adds a small latency overhead and may not expose every provider-specific parameter. For most applications, the portability benefit outweighs the cost.

---

## Code Cell

```python
# Demonstrates provider portability: same request body, two different base_urls.
# In a real environment, you would have both servers running.
# Here we send to Ollama twice with different "provider" labels to show the pattern.

import requests
import json

def chat_completion(base_url, model, messages, api_key="ollama", temperature=0.3):
    """Generic chat completion call to any OpenAI-compatible endpoint."""
    endpoint = f"{base_url.rstrip('/')}/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    payload = {
        "model": model,
        "messages": messages,
        "stream": False,
        "temperature": temperature
    }
    try:
        r = requests.post(endpoint, json=payload, headers=headers, timeout=120)
        r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"]
    except Exception as e:
        import traceback; traceback.print_exc()
        return None

MESSAGES = [
    {"role": "user", "content": "Name one advantage of provider-agnostic API design in two sentences."}
]

# Provider A: local Ollama with llama3.2
print("=== Provider A: Ollama / llama3.2 ===")
result_a = chat_completion(
    base_url="http://localhost:11434/v1",
    model="llama3.2",
    messages=MESSAGES
)
print(result_a)

# Provider B: local Ollama with mistral (swap model only)
print("\n=== Provider B: Ollama / mistral ===")
result_b = chat_completion(
    base_url="http://localhost:11434/v1",
    model="mistral",
    messages=MESSAGES
)
print(result_b)

# To point at a remote OpenAI-compatible provider, you would change base_url:
# chat_completion(base_url="https://api.some-other-provider.com/v1", model="their-model-name", ...)
```

---

## Model 3: Portability and Its Limits

The `chat_completion` function above sends the same payload to two different models. Notice that only `base_url` and `model` change between the two calls — the request construction code is identical.

### Critical Thinking Questions

7. List three things that could break when you switch from one provider to another even though both are "OpenAI-compatible." For each, give a concrete example of how the breakage would appear at runtime.

   > *Hint: Think about model names (a model called `llama3.2` on Ollama may be named differently on another provider), context window limits (a 128k-context message that fits in one model may overflow another), and tool support (some local models do not implement tool calling even if the endpoint accepts the `tools` field).*

8. The `chat_completion` function trusts that `r.json()["choices"][0]["message"]["content"]` always exists. Write a more defensive version that handles the case where a provider returns a non-standard response shape (for example, an error JSON with no `choices` key).

   > *Hint: Wrap the key access in a `try/except KeyError` or check `"choices" in r.json()` before indexing. Log the full raw response when parsing fails so you can debug the provider's actual behavior.*

9. LiteLLM adds an abstraction layer between your code and the provider. Name one scenario where this abstraction is valuable and one scenario where it would be better to call the provider's API directly without LiteLLM in the middle.

   > *Hint: Abstraction is valuable when you need to switch providers quickly or test across multiple models. Direct access is better when you need a provider-specific parameter that LiteLLM does not expose, or when LiteLLM's version lags behind a provider's latest API update.*

[[MC]]
What is the minimum change needed to point an OpenAI Python SDK call at a local Ollama server instead of the default remote endpoint?
- ( ) Reinstall the `openai` package with a special `--local` flag
- ( ) Replace every `client.chat.completions.create(...)` call with `requests.post(...)`
- ( ) Set the `OPENAI_API_KEY` environment variable to `"ollama"`
- (x) Instantiate the `OpenAI` client with `base_url="http://localhost:11434/v1"` and `api_key="ollama"`

> **⚠️ Common Misconception:** Switching providers is not always as simple as changing `base_url` and `model`. The OpenAI-compatible specification defines a common *structure*, but not every optional field is supported by every server. Features like `logprobs`, `response_format`, `parallel_tool_calls`, and streaming with tool calls are implemented inconsistently. Always test a new provider with the specific features your agent relies on before treating portability as guaranteed.

---

# Part III: Synthesis and Practice

## 7. Exercises

1. *Endpoint explorer.*

   - *What to do*: Use `curl` or the Python `requests` library to call `GET /v1/models` against your local Ollama instance. Parse the response and print a formatted table showing each model's `id` and (if present) its `created` timestamp.
   - *Starter hint*: The response is JSON with a `"data"` key containing a list of model objects. Each object has at least `"id"`. In Python: `r = requests.get("http://localhost:11434/v1/models"); print(r.json()["data"])`.
   - *You've succeeded when*: Your output shows a clean table of all available models and you can explain what each field in the response object means.

2. *Multi-turn conversation.*

   - *What to do*: Write a Python function `multi_turn_chat(turns)` that accepts a list of `(role, content)` tuples and sends them as a single `messages` array to `/v1/chat/completions`. Test it with a 3-turn conversation where the user refers back to something said in turn 1 in turn 3 (for example, asking the model to elaborate on its earlier answer).
   - *Starter hint*: Build the messages list as `[{"role": r, "content": c} for r, c in turns]`. The model can only "remember" previous turns because they are included in the `messages` array — there is no hidden memory in the server.
   - *You've succeeded when*: The model's third response correctly references content from turn 1, demonstrating that context is carried through the `messages` array.

3. *Tool calling from scratch.*

   - *What to do*: Add a second tool, `convert_units(value, from_unit, to_unit)`, to the tool loop from the Code Cell in Part III. Write the JSON schema definition for this tool and the Python function that implements it (handle at least kilometers-to-miles and Celsius-to-Fahrenheit). Test with a user message that requires both `get_weather` and `convert_units` in the same conversation.
   - *Starter hint*: Copy the `get_weather` tool schema and modify the `name`, `description`, and `parameters`. Add an `elif fn_name == "convert_units":` branch to the tool dispatch block. A message like "What is the weather in Paris in Fahrenheit?" should trigger both tools.
   - *You've succeeded when*: The trace shows the model calling `get_weather` first, then `convert_units` on the temperature, then returning a final plain-text answer that uses the converted value.

4. *Provider switch.*

   - *What to do*: Modify the `chat_completion` function to accept a `provider` argument (`"ollama_llama"` or `"ollama_mistral"`) and look up `base_url` and `model` from a configuration dictionary defined at the top of the file. Send the same user message to both providers and print the results side by side.
   - *Starter hint*: `PROVIDERS = {"ollama_llama": {"base_url": "http://localhost:11434/v1", "model": "llama3.2"}, "ollama_mistral": {"base_url": "http://localhost:11434/v1", "model": "mistral"}}`. This pattern scales to real provider switching — just add entries to the dictionary.
   - *You've succeeded when*: Adding a new provider requires only a new dictionary entry, and the request-sending code is untouched.

---

## Reflection Prompt

*Personal*: Before this activity, when you interacted with an AI assistant through a web interface, did you think of it as "magic" or as a program making HTTP requests to a server? Has seeing the raw curl and JSON changed how you think about those interactions? What surprised you most about how simple the protocol is at the lowest level?

*Technical*: In your notebook: You are building a coding agent that will run in a production environment where model providers may change (budget, availability, policy). Design a configuration system — a dictionary, a config file, or environment variables — that lets you switch the `base_url`, `model`, and `api_key` without touching any agent logic code. What are the tradeoffs of each approach (hardcoded dict vs. `.env` file vs. config YAML)?

*Societal*: The OpenAI-compatible API standard means that a developer can write code once and run it against many different model providers, including local models that never send data to a third-party server. What are the privacy implications of this portability? Who benefits from the ability to run inference entirely locally, and are there groups who cannot access that option? What responsibilities does this create for developers who build tools that default to cloud inference?

---

## → Coming Up Next

Now that you can speak the REST protocol fluently, the next activity takes the `tools` array to its logical conclusion: the Model Context Protocol (MCP), a formal specification for how agents discover, negotiate, and call tools across process boundaries. We will see how `getmcp.io` (from the GitHub Superpowers activity) implements exactly the patterns you built by hand today, and we will connect a live MCP server to the tool loop you wrote in Part III.

---

## 8. Further Reading

- OpenAI. "Chat Completions API Reference." *platform.openai.com/docs/api-reference/chat*. The canonical specification for the request and response format; all OpenAI-compatible servers implement a subset of this.
- BerriAI. *LiteLLM Documentation*. `docs.litellm.ai`. Covers provider setup, proxy configuration, and the translation layer between OpenAI format and provider-specific APIs.
- Shunyu Yao et al. "ReAct: Synergizing Reasoning and Acting in Language Models." *ICLR* (2023). The intellectual foundation for tool-calling agents, implemented at the REST level in today's tool loop.
