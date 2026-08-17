---
layout: assignment
permalink: /Assignments/LocalAgent/Direction4
title: "CS357 Local Agent Lab Direction 4: Build and Deploy an MCP Server with OAuth 2.0"
---

> **Grading:** This page is one of the directions for the [Local Agent Lab](/Assignments/LocalAgent). It carries no separate point value and no rubric of its own — your combined core + direction work is graded with the Local Agent Lab rubric on the core lab page.

> **What this direction requires**
>
> - **Accounts:** none — the OAuth authorization server is a local mock server (or local Keycloak); no cloud identity provider is involved.
> - **API costs:** none required — the MCP server, tokens, and tools are all local. Part 4 drives the server from an agent client; the direction shows one hosted-agent configuration but explicitly permits any MCP-capable agent, including local Ollama-based agents with tool support.
> - **Installs / disk:** Python packages (`mcp[cli]`, `fastapi`, `uvicorn`, `python-jose[cryptography]`, `requests`) plus Docker Desktop or Docker Engine to run the mock OAuth2 server image (a few hundred MB; the Keycloak alternative is roughly 1 GB).
> - **Hardware:** any machine that runs the core lab; three services run simultaneously, so plan your ports.
> - **No-cost fallback:** built in — for Part 4, use an Ollama-backed agent with tool support instead of a hosted agent client, as the direction text allows.

---


Take the local agent you built in the core lab and give it real, authenticated tools. You will build a Model Context Protocol (MCP) server that exposes at least two working tools to a local AI agent, then secure it with OAuth 2.0 so that only authorized clients can invoke those tools — and document the full data flow from agent request through OAuth token to tool response.

> **Background resource:** the free [Hugging Face MCP Course](https://huggingface.co/learn/mcp-course/), built with Anthropic, covers the MCP protocol, building a server, and connecting clients. Work through its server-building units before this direction if MCP is new to you; this direction then adds the OAuth 2.0 authorization layer on top of that foundation.

In this lab, you and your partner will build a Model Context Protocol (MCP) server that exposes real tools to a local AI agent, then secure it with OAuth 2.0 so that only authorized clients can invoke those tools. The skills being assessed are implementation precision (does the server actually work?), security integration (does OAuth actually gate access?), and documentation clarity (can someone else understand the data flow?). This lab is completed in **pairs using driver/navigator roles with swaps at least every 30 minutes and a swap log**.

---

#### Overview

**Model Context Protocol (MCP)** is an open standard that gives AI agents a uniform way to discover and call external tools. Instead of hard-coding API calls into an agent, you publish a server that advertises its capabilities through a standard schema. The agent reads that schema, decides which tools to use, and calls them — all without the agent needing to know anything about the underlying implementation.

Why does OAuth matter here? Without authentication, any process on the same machine (or network) could invoke your MCP tools. OAuth 2.0 adds a layer of authorization: the agent must first prove its identity to an authorization server and receive a short-lived token; then the MCP server validates that token on every request and enforces scopes that limit what each caller is permitted to do. This lab walks you through all three layers: the MCP server itself, the OAuth wrapper, and the agent that uses both.

---

#### Before You Start

**Complete these prerequisite activities first:**

- [MCP Server Activity](https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-mcprestoauth.md) — introduces the MCP protocol and the Python SDK
- [The Local Agent Stack Activity](https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-agentstack.md) — walks through running a local AI agent and wiring in tools

##### Install Required Tools

Run the following commands in your terminal. If you are using a virtual environment (recommended), activate it first.

```bash
pip install "mcp[cli]" fastapi uvicorn "python-jose[cryptography]" requests
```

For the OAuth authorization server, pull the mock OAuth2 server Docker image:

```bash
docker pull ghcr.io/navikt/mock-oauth2-server:latest
```

Alternatively, you may use Keycloak in dev mode:

```bash
docker pull quay.io/keycloak/keycloak:latest
```

Both options are acceptable. The lab instructions below use the mock OAuth2 server because its startup time is faster. If you choose Keycloak, the token endpoint URL and realm configuration will differ — consult the Keycloak quickstart documentation and adapt the `curl` commands accordingly.

##### Verify Your Installation

Run each health-check command and compare your output to the expected output shown below.

```bash
$ python -c "import mcp; print(mcp.__version__)"
# Should print something like: 1.x.x

$ docker run --rm ghcr.io/navikt/mock-oauth2-server:latest --help
# Should print usage information for the mock OAuth2 server
```

If the first command raises `ModuleNotFoundError`, the `mcp` package did not install correctly. Confirm that you are in the right virtual environment and re-run `pip install "mcp[cli]"`.

If the second command hangs or fails with a "Cannot connect to the Docker daemon" error, Docker is not running. Start Docker Desktop (or the Docker daemon on Linux) and try again.

##### Port Planning

This lab runs three services simultaneously. Each must use a distinct port to avoid collisions. Plan your ports **now**, before writing any code:

| Service | Default Port | Assigned Port | Reason for Change |
|---|---|---|---|
| MCP Server | 8000 | _(fill in)_ | _(fill in or "no change")_ |
| OAuth Server | 8080 | _(fill in)_ | _(fill in or "no change")_ |
| AI Agent / Claude Code | varies | _(fill in)_ | _(fill in or "no change")_ |

> **Tip:** On most development machines port 8080 is frequently in use. Assigning the OAuth server to port 8090 is a common choice that avoids conflicts. If you are unsure whether a port is free, run `lsof -i :<port>` (macOS/Linux) or `netstat -ano | findstr :<port>` (Windows).

##### Estimated Time

| Part | Estimated Time |
|---|---|
| Part 1: Design and Plan | ~30 minutes |
| Part 2: Implement the MCP Server | ~60 minutes |
| Part 3: Add OAuth 2.0 | ~60 minutes |
| Part 4: Agent Integration | ~45 minutes |
| Documentation and Reflection | ~30 minutes |

---

#### Part 1: Design and Plan

##### Step 1: Choose Your Domain

Choose **one** of the following domains for your MCP server, or propose an alternative to the instructor before writing any code:

- **Local file search** — tools that search and read files on the local filesystem
- **Calendar query** — tools that read and summarize `.ics` or JSON calendar files
- **Weather API wrapper** — tools that query a local JSON data file of weather observations
- **Code repository summary** — tools that inspect a local git repository and summarize recent commits or changed files

Write a one-paragraph justification for your choice. Your justification should address: (a) what the two tools will do, (b) which tool reads data and which transforms or processes it, and (c) why this domain is interesting or useful to automate with an AI agent. Include this paragraph in your submission's README.

##### Step 2: Write the Tool Schemas

For each tool, you must write a complete JSON Schema object **before** implementing it. Writing the schema first forces you to think precisely about inputs, types, and constraints before you touch any code.

Here is a complete, filled-in example for a `search_files` tool and a `summarize_file` tool (these match the local file search domain):

```json
{
  "name": "search_files",
  "description": "Search for files in the local workspace matching a query string.",
  "input_schema": {
    "type": "object",
    "properties": {
      "query": {
        "type": "string",
        "description": "The search term to match against file names and contents."
      },
      "max_results": {
        "type": "integer",
        "description": "Maximum number of results to return (default: 10).",
        "default": 10
      }
    },
    "required": ["query"]
  }
}
```

```json
{
  "name": "summarize_file",
  "description": "Return the first N lines of a file as a plain-text summary.",
  "input_schema": {
    "type": "object",
    "properties": {
      "path": {
        "type": "string",
        "description": "Absolute or workspace-relative path to the file to summarize."
      },
      "lines": {
        "type": "integer",
        "description": "Number of lines to return (default: 20).",
        "default": 20
      }
    },
    "required": ["path"]
  }
}
```

Now fill in the blank template below for **your first tool** (adapt the example above for your chosen domain):

```json
{
  "name": "YOUR_TOOL_NAME",
  "description": "YOUR_DESCRIPTION",
  "input_schema": {
    "type": "object",
    "properties": {
      "PARAM_1": {
        "type": "TYPE",
        "description": "DESCRIPTION"
      }
    },
    "required": ["PARAM_1"]
  }
}
```

And for your **second tool** (the one that transforms or processes data):

```json
{
  "name": "YOUR_SECOND_TOOL_NAME",
  "description": "YOUR_DESCRIPTION",
  "input_schema": {
    "type": "object",
    "properties": {
      "PARAM_1": {
        "type": "TYPE",
        "description": "DESCRIPTION"
      }
    },
    "required": ["PARAM_1"]
  }
}
```

Include both completed schemas in your submission's README.

##### Step 3: Sketch the OAuth 2.0 Flow

Before writing any code, draw a simple ASCII diagram (or a hand-drawn photo) showing the three actors and the message flow. Here is the pattern to follow — adapt it for your deployment:

```
  AI Agent (MCP Client)
       |
       | 1. POST /token
       |    grant_type=client_credentials
       |    client_id=mcp-client
       |    client_secret=secret
       |    scope=mcp:read
       v
  OAuth Authorization Server (mock-oauth2-server or Keycloak)
       |
       | 2. Returns: { access_token, token_type, expires_in }
       v
  AI Agent (holds Bearer token)
       |
       | 3. POST /mcp  (tool call)
       |    Authorization: Bearer <access_token>
       v
  MCP Server (Resource Server)
       |
       | 4. Validate token (check signature, expiry, scope)
       | 5. Execute tool
       | 6. Return result
       v
  AI Agent (receives tool response)
```

Label each arrow with the protocol step number. Include this diagram in your submission.

##### Step 4: Fill In the Port Table

Return to the port table from the Before You Start section and complete every column. Resolve any collisions now. You will reference these ports throughout the lab.

---

##### Troubleshooting — Part 1

**"Port 8080 is already in use when I start the OAuth server."**
Use a different host port. The Docker `-p` flag maps `host:container`, so `-p 8090:8080` runs the container on host port 8090 while the container still listens internally on 8080. Update every `curl` command to use 8090.

**"My tool schema is missing a `required` field and validation is silently passing."**
JSON Schema `required` is a property of the object schema, not of individual properties. It must be a top-level array inside `"type": "object"`. If you omit `required`, all fields are considered optional and you must enforce presence manually in your code.

**"I am confused about which component is the client."**
In the OAuth 2.0 client credentials flow: the **AI agent** is the client (it requests the token), the **mock OAuth server** is the authorization server (it issues tokens), and the **MCP server** is the resource server (it validates tokens and serves tools). The MCP server never requests a token — it only validates them.

---

##### ✅ Part 1 Checkpoint

Answer these three questions in your pair log before moving to Part 2:

1. What are the names of your two tools, and which one reads data versus which one transforms or processes it?
2. What port will each of your three services use? Are there any collisions?
3. In the OAuth 2.0 flow you sketched, which component issues tokens and which component validates them?

---

#### Part 2: Implement the MCP Server

##### Step 1: Set Up the Project Structure

Create the following directory layout before writing any code. Having a clear structure now will save debugging time later.

```
cs357-mcp-lab/
├── mcp_server.py          # MCP server (this part)
├── oauth_middleware.py    # OAuth validation helpers (Part 3)
├── tools/
│   ├── __init__.py
│   ├── tool_one.py        # Your first tool's implementation
│   └── tool_two.py        # Your second tool's implementation
├── tests/
│   ├── test_tools.py      # Unit tests for tool logic
│   └── test_oauth.py      # Tests for token validation (Part 3)
├── data/                  # Any local data files your tools read
├── logs/                  # Structured log output
├── requirements.txt
└── README.md
```

Initialize the project:

```bash
mkdir -p cs357-mcp-lab/tools cs357-mcp-lab/tests cs357-mcp-lab/data cs357-mcp-lab/logs
cd cs357-mcp-lab
touch tools/__init__.py
pip freeze > requirements.txt
```

##### Step 2: Implement the MCP Server Skeleton

Create `mcp_server.py` using the starter code below. Read every `TODO` comment carefully — each one is a specific task you must complete. Do not remove the logging lines; they are required for the rubric.

```python
# mcp_server.py
# CS357 Lab: MCP Server with OAuth 2.0

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp import types
import json
import logging
from datetime import datetime

# Configure structured logging
# Every log line is a valid JSON object so it can be parsed by log aggregators.
logging.basicConfig(
    level=logging.INFO,
    format='{"time": "%(asctime)s", "level": "%(levelname)s", "message": "%(message)s"}'
)
logger = logging.getLogger(__name__)

app = Server("cs357-mcp-server")


@app.list_tools()
async def list_tools() -> list[types.Tool]:
    """Return the list of available tools.

    The MCP client (agent) calls this endpoint first to discover what
    tools are available. In Part 3 you will add scope enforcement here:
    only callers with mcp:admin may call list_tools.
    """
    # TODO: Return a list of types.Tool objects for your two tools.
    # Replace the example below with your actual tool definitions.
    # Use the JSON schemas you wrote in Part 1.
    #
    # return [
    #     types.Tool(
    #         name="search_files",
    #         description="Search for files in the local workspace.",
    #         inputSchema={
    #             "type": "object",
    #             "properties": {
    #                 "query": {"type": "string", "description": "Search term."},
    #                 "max_results": {"type": "integer", "default": 10},
    #             },
    #             "required": ["query"],
    #         },
    #     ),
    #     types.Tool(
    #         name="your_second_tool_name",
    #         description="YOUR DESCRIPTION",
    #         inputSchema={...},
    #     ),
    # ]
    pass


@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[types.TextContent]:
    """Handle tool invocation.

    This function is called every time the agent wants to run a tool.
    Log BEFORE executing so that failures are still captured in the log.
    """
    # Log every invocation BEFORE executing.
    # In Part 3 you will also log the caller identity extracted from the token.
    logger.info(
        f"Tool invoked: {name}, "
        f"arguments: {json.dumps(arguments)}, "
        f"timestamp: {datetime.utcnow().isoformat()}Z"
    )

    # TODO: Validate that required fields are present in `arguments`.
    # If a required field is missing, raise ValueError with a message that
    # names the missing field. The MCP SDK will return this as an error
    # response to the agent.
    #
    # Example:
    # if name == "search_files" and "query" not in arguments:
    #     raise ValueError("Missing required argument: query")

    if name == "search_files":
        # TODO: Implement the search_files tool.
        # Suggested steps:
        #   1. Extract "query" from arguments (already validated above).
        #   2. Extract "max_results" with a default of 10.
        #   3. Walk the local workspace directory and collect matching file paths.
        #   4. Log the result count.
        #   5. Return the results as a single types.TextContent with a JSON body.
        #
        # return [
        #     types.TextContent(
        #         type="text",
        #         text=json.dumps({"results": [...], "count": N}),
        #     )
        # ]
        pass

    elif name == "your_second_tool_name":
        # TODO: Implement your second tool.
        # Follow the same pattern:
        #   1. Validate inputs (already done above).
        #   2. Perform the operation.
        #   3. Log the outcome.
        #   4. Return types.TextContent.
        pass

    else:
        # Any unknown tool name must raise ValueError.
        # The MCP SDK will translate this into a structured error for the agent.
        raise ValueError(f"Unknown tool: {name}")


if __name__ == "__main__":
    import asyncio
    asyncio.run(stdio_server(app))
```

##### Step 3: Test the Tools Directly

Before adding OAuth, verify that both tools work by running the server in stdio mode and calling it with `curl`. In one terminal, start the server:

```bash
python mcp_server.py
```

In a second terminal, send a JSON-RPC `tools/call` request:

```bash
curl -s -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/call",
    "params": {
      "name": "search_files",
      "arguments": {"query": "README"}
    }
  }'
```

> **What you should see:**
> A JSON response containing a `result` object with a `content` array. The first element should have `"type": "text"` and a `text` field containing your tool's output. For example:
> ```json
> {
>   "jsonrpc": "2.0",
>   "id": 1,
>   "result": {
>     "content": [
>       {"type": "text", "text": "{\"results\": [\"./README.md\"], \"count\": 1}"}
>     ]
>   }
> }
> ```

Test your second tool with a similar `curl` command. Also test the error case: send a request that is missing a required argument and verify the response contains an error.

##### Step 4: Verify Structured Logging

Check the terminal where the server is running. Each invocation should produce a log line that is valid JSON. For example:

```
{"time": "2026-06-21 10:15:32,041", "level": "INFO", "message": "Tool invoked: search_files, arguments: {\"query\": \"README\"}, timestamp: 2026-06-21T10:15:32.041Z"}
```

If the log lines are not appearing, check that `logging.basicConfig` is called before the first `logger.info` call and that the log level is `INFO` or lower.

---

##### Troubleshooting — Part 2

**`ImportError: No module named 'mcp'`**
The package was not installed in the active environment. Confirm which Python interpreter is running (`which python`) and that your virtual environment is activated. Re-run `pip install "mcp[cli]"` in that environment.

**Tool handler returns `None` instead of `TextContent`**
Every branch of `call_tool` must explicitly `return` a list. A missing `return` statement (or a `pass` left in place) causes Python to return `None`, which the MCP SDK cannot serialize. Replace every `pass` with a `return [types.TextContent(...)]`.

**JSON schema validation is silently accepting missing fields**
The MCP SDK does not automatically enforce your `inputSchema`. You must validate manually in `call_tool`. After completing the TODO block, test this by intentionally sending a request without a required field and verifying that you receive a `ValueError` response.

---

##### ✅ Part 2 Checkpoint

Answer these three questions in your pair log before moving to Part 3:

1. Paste the `curl` command you used to test your first tool and the first line of the response you received.
2. What happens when you send a request with a missing required argument? Paste the response.
3. Open the log file (or terminal output) and paste one log line. Is it valid JSON? Verify by piping it through `python -m json.tool`.

---

#### Part 3: Add OAuth 2.0

##### Step 1: Start the Mock OAuth Server

Open a new terminal and start the mock OAuth2 server. This server will issue and validate JWT tokens for your lab.

```bash
docker run -d --name oauth-server -p 8090:8080 \
  ghcr.io/navikt/mock-oauth2-server:latest
```

> **What you should see:**
> Docker will print a container ID (a long hex string) and return you to the prompt. The container starts in the background. Verify it is running:
> ```bash
> docker ps
> # You should see a row with "oauth-server" in the NAMES column and
> # "0.0.0.0:8090->8080/tcp" in the PORTS column.
> ```
> The mock OAuth server's discovery document is available at:
> `http://localhost:8090/default/.well-known/openid-configuration`
> Open that URL in a browser or with `curl` to confirm the server is responding.

##### Step 2: Obtain a Token Using Client Credentials Flow

The client credentials flow is the OAuth 2.0 grant type used when a machine (not a human) needs to authenticate. The agent presents its client ID and secret directly to the token endpoint and receives an access token.

```bash
curl -s -X POST http://localhost:8090/default/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "grant_type=client_credentials&client_id=mcp-client&client_secret=secret&scope=mcp:read"
```

> **What you should see:**
> ```json
> {
>   "access_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...",
>   "token_type": "Bearer",
>   "expires_in": 3600,
>   "scope": "mcp:read"
> }
> ```
> Copy the value of `access_token`. You will use it in the next step.
> To inspect the token's claims, paste it into [jwt.io](https://jwt.io) — you should see the `sub`, `scope`, `iat`, and `exp` fields.

##### Step 3: Add Bearer Token Validation to the MCP Server

Create `oauth_middleware.py` with the helper functions below, then import and call them from `mcp_server.py`. The key points:

- Fetch the JWKS (public keys) from the OAuth server once at startup and cache them.
- On every request, extract the `Authorization: Bearer <token>` header.
- Decode the JWT using the cached public key, verify the signature, and check that `exp` is in the future.
- Reject any request that fails these checks with HTTP 401.

```python
# oauth_middleware.py
# CS357 Lab: OAuth 2.0 token validation helpers

import requests
from jose import jwt, JWTError
from datetime import datetime, timezone
import logging

logger = logging.getLogger(__name__)

# TODO: Replace this URL with your OAuth server's JWKS endpoint.
# For the mock OAuth2 server the endpoint is:
#   http://localhost:8090/default/jwks
JWKS_URI = "http://localhost:8090/default/jwks"

# TODO: Replace with the issuer shown in your discovery document.
# For the mock OAuth2 server this is typically:
#   http://localhost:8090/default
ISSUER = "http://localhost:8090/default"

_jwks_cache = None


def get_jwks() -> dict:
    """Fetch the JWKS from the authorization server (cached after first call)."""
    global _jwks_cache
    if _jwks_cache is None:
        # TODO: Fetch the JWKS from JWKS_URI using requests.get().
        # Store the parsed JSON in _jwks_cache.
        # Handle connection errors gracefully: log the error and raise.
        pass
    return _jwks_cache


def validate_token(token: str, required_scope: str = None) -> dict:
    """Decode and validate a Bearer token.

    Parameters
    ----------
    token : str
        The raw JWT string (without the 'Bearer ' prefix).
    required_scope : str, optional
        If provided, raise ValueError if this scope is not in the token.

    Returns
    -------
    dict
        The decoded token claims if validation succeeds.

    Raises
    ------
    ValueError
        If the token is expired, has an invalid signature, has the wrong
        issuer, or is missing the required scope.
    """
    jwks = get_jwks()

    try:
        # TODO: Use jose.jwt.decode() to decode and verify the token.
        # Pass the JWKS, the expected ISSUER, and the expected audience
        # (use options={"verify_aud": False} if no audience is configured).
        #
        # claims = jwt.decode(
        #     token,
        #     jwks,
        #     algorithms=["RS256"],
        #     issuer=ISSUER,
        #     options={"verify_aud": False},
        # )
        claims = None  # Replace with the actual decode call

    except JWTError as e:
        # JWTError covers expired tokens, bad signatures, wrong issuer, etc.
        logger.warning(f"Token validation failed: {e}")
        raise ValueError(f"Invalid token: {e}") from e

    # TODO: If required_scope is provided, check that it appears in
    # claims.get("scope", ""). The scope claim is a space-separated string.
    # Raise ValueError if the scope is absent.

    return claims
```

Now add token validation to `mcp_server.py`. At the top of both `list_tools` and `call_tool`, call `validate_token` with the appropriate scope. Because the MCP SDK uses stdio transport for local communication, the token is passed as a custom header or query parameter depending on your agent configuration — for this lab you will wrap the server with a small FastAPI HTTP layer.

Add a `server_http.py` file that wraps the MCP server with FastAPI:

```python
# server_http.py
# Thin HTTP wrapper that validates OAuth tokens before delegating to the MCP server.

from fastapi import FastAPI, Request, HTTPException
from oauth_middleware import validate_token
import uvicorn

fastapi_app = FastAPI()


@fastapi_app.post("/mcp")
async def mcp_endpoint(request: Request):
    """Validate Bearer token, then forward the request to the MCP server."""
    # TODO: Extract the Authorization header.
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or malformed Authorization header")

    token = auth_header.removeprefix("Bearer ")

    # TODO: Call validate_token with the appropriate scope for this endpoint.
    # For tool invocation, require "mcp:read".
    try:
        claims = validate_token(token, required_scope="mcp:read")
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))

    # TODO: Forward the request body to your MCP server logic and return the response.
    # You can call the MCP server's handler directly or via an internal HTTP call.
    # For now, return a placeholder:
    return {"status": "token valid", "subject": claims.get("sub")}


if __name__ == "__main__":
    uvicorn.run(fastapi_app, host="0.0.0.0", port=8000)
```

##### Step 4: Enforce Scopes

Update the server so that:

- `mcp:read` is required to invoke any tool (the `call_tool` handler)
- `mcp:admin` is required to list all available tools (the `list_tools` handler)

Test both paths:

```bash
# Get a read-only token
READ_TOKEN=$(curl -s -X POST http://localhost:8090/default/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "grant_type=client_credentials&client_id=mcp-client&client_secret=secret&scope=mcp:read" \
  | python -c "import sys,json; print(json.load(sys.stdin)['access_token'])")

# This should succeed (scope matches)
curl -s -X POST http://localhost:8000/mcp \
  -H "Authorization: Bearer $READ_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"search_files","arguments":{"query":"README"}}}'

# Get an admin token
ADMIN_TOKEN=$(curl -s -X POST http://localhost:8090/default/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "grant_type=client_credentials&client_id=mcp-client&client_secret=secret&scope=mcp:read mcp:admin" \
  | python -c "import sys,json; print(json.load(sys.stdin)['access_token'])")

# This should succeed
curl -s -X POST http://localhost:8000/mcp \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}'
```

##### Step 5: Demonstrate Token Expiry

Request a token with a very short lifetime. The mock OAuth2 server accepts a custom expiry via the `exp` parameter in some configurations, or you can simply wait for the default token to expire. A simpler approach is to manually craft an expired token for testing:

```bash
# Request a token with the shortest supported lifetime
# (consult mock-oauth2-server docs for the exact parameter)
curl -s -X POST http://localhost:8090/default/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "grant_type=client_credentials&client_id=mcp-client&client_secret=secret&scope=mcp:read"

# Save the token, wait for it to expire (or manually adjust the exp claim for testing),
# then re-send the request. You should receive HTTP 401.
```

> **What you should see after the token expires:**
> ```json
> {
>   "detail": "Invalid token: Signature has expired."
> }
> ```
> with HTTP status `401 Unauthorized`. Save this output for your submission.

---

##### Troubleshooting — Part 3

**"HTTP 401 even though I just got the token and it should not have expired."**
Check that your `ISSUER` constant in `oauth_middleware.py` exactly matches the `iss` claim in the token (inspect it at jwt.io). A trailing slash or wrong realm name will cause `jose.jwt.decode` to fail with an issuer mismatch, which presents as 401.

**"The `scope` claim is not in the token."**
The mock OAuth2 server only includes scopes that you explicitly request in the `scope` parameter of the token request. Confirm your `curl` command includes `scope=mcp:read`. If the claim is still absent, check the server's claim mapping configuration.

**"JWKS endpoint is unreachable: `ConnectionRefusedError`."**
The OAuth Docker container may not have finished starting. Run `docker logs oauth-server` to see its startup output. Wait until you see a line indicating the server is listening, then retry.

---

##### ✅ Part 3 Checkpoint

Answer these three questions in your pair log before moving to Part 4:

1. Paste the HTTP 401 response you received when you sent a request without a token.
2. What is the value of the `iss` claim in your token, and how does it match the `ISSUER` constant in your code?
3. Paste the HTTP 401 response you received when you presented an expired token. How does the error message differ from the "missing token" error?

---

#### Part 4: Agent Integration

##### Step 1: Configure the Agent to Use Your MCP Server

For **Claude Code**, add your MCP server to the project configuration file. Create or edit `.claude/settings.json` in your project directory (or `~/.claude.json` for a global configuration):

```json
{
  "mcpServers": {
    "cs357-lab": {
      "command": "python",
      "args": ["/absolute/path/to/cs357-mcp-lab/mcp_server.py"],
      "env": {
        "MCP_OAUTH_TOKEN_ENDPOINT": "http://localhost:8090/default/token",
        "MCP_CLIENT_ID": "mcp-client",
        "MCP_CLIENT_SECRET": "secret"
      }
    }
  }
}
```

Replace `/absolute/path/to/cs357-mcp-lab/` with the actual path on your machine.

For **other agents** (Ollama with tool support, LangChain agents, etc.), consult your agent's documentation for the equivalent MCP server registration step. The key information you need to provide is: the server command, any environment variables for OAuth credentials, and the transport type (stdio for local servers).

Restart the agent after editing the configuration. The agent should now list your tools when it starts.

##### Step 2: Give the Agent a Task That Requires Both Tools

Do **not** manually call the tools or construct the tool calls yourself. Give the agent a natural-language task and let it decide which tools to use and in what order. Here are three example tasks matched to the local file search domain — adapt for your chosen domain:

- **Task A:** "Find all Python files in the cs357-mcp-lab directory that contain the word 'TODO', then summarize the first one you find so I know what still needs to be done."
- **Task B:** "Search the workspace for any file named `requirements.txt` and show me its first 10 lines."
- **Task C:** "I want to understand the structure of this project. Find all `.py` files and then give me a summary of `mcp_server.py`."

Each of these tasks requires the agent to (1) call the search tool to locate a file, and then (2) call the transform/summarize tool on the result. This is the natural two-tool sequence you must demonstrate.

##### Step 3: Capture the Full Invocation Trace

You must capture and submit evidence of the full invocation sequence. Depending on your agent:

- **Claude Code:** run with `--debug` or check the MCP server log file in `logs/`.
- **Any agent:** redirect the MCP server's stderr to a file: `python mcp_server.py 2> logs/invocation.log`.

The trace must show:
1. The agent calling `tools/list` (tool discovery)
2. The token exchange request and response (or evidence that the token was used)
3. The `tools/call` request with the exact arguments passed
4. The tool response returned to the agent

Save the complete trace as `invocation_trace.txt` in your submission.

##### Step 4: Test Error Case 1 — Expired Token

Use the expired token from Part 3 Step 5 and send it to your server while the agent is running. Document the exact request, the server log entry, and the response the agent receives.

```bash
# Send a request with the expired token
curl -s -X POST http://localhost:8000/mcp \
  -H "Authorization: Bearer PASTE_EXPIRED_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"search_files","arguments":{"query":"README"}}}'
```

> **What you should see:**
> HTTP 401 with a body like `{"detail": "Invalid token: Signature has expired."}`.
> Save this output as `error_expired_token.txt`.

##### Step 5: Test Error Case 2 — Tool Failure

Trigger a failure inside the tool itself — for example, search for a string that matches no files, or request a summary of a file path that does not exist:

```bash
curl -s -X POST http://localhost:8000/mcp \
  -H "Authorization: Bearer $READ_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"summarize_file","arguments":{"path":"/nonexistent/path.txt"}}}'
```

> **What you should see:**
> A JSON-RPC error response (not HTTP 500) with a descriptive message. The agent should receive this error and either retry with a different path or report the failure to the user. Save this output as `error_tool_failure.txt`.

---

##### Troubleshooting — Part 4

**"The agent cannot discover my tools — it says the MCP server is unavailable."**
Check that the server is actually running (`ps aux | grep mcp_server`). Verify the path in the agent configuration is correct and absolute. Check the agent's log for the exact error message — common causes are a wrong Python interpreter path and a missing environment variable.

**"The agent discovers the tools but never invokes them."**
The agent may not think the tools are relevant to the task you gave it. Try a more explicit task: "Use the search_files tool to find README files." Also verify that your tool descriptions in `list_tools()` are clear and specific — vague descriptions cause the agent to skip the tool.

**"The agent invokes the tool but the response is not formatted as expected."**
The MCP SDK requires that `call_tool` return a `list[types.TextContent]`. If you return a plain string, a dict, or an empty list, the agent may not be able to parse the response. Double-check every `return` statement in `call_tool`.

---

##### ✅ Part 4 Checkpoint

Answer these three questions in your pair log before writing up your documentation:

1. What exact task did you give the agent? Did it naturally invoke both tools without you prompting it for each one?
2. What does the invocation trace show happened between tool discovery and the first tool call?
3. How did the agent respond when it received the tool failure error from Step 5 — did it retry, report the error, or do something else?

---

#### Deliverables

Submit a ZIP file containing all of the following:

| File | Description |
|---|---|
| `mcp_server.py` | Your MCP server implementation |
| `oauth_middleware.py` | Your OAuth token validation helpers |
| `server_http.py` | Your FastAPI HTTP wrapper |
| `tools/tool_one.py` and `tools/tool_two.py` | Individual tool implementations |
| `requirements.txt` | All Python dependencies |
| OAuth server configuration | The docker command used, with secrets redacted |
| Agent MCP configuration | The `.claude/settings.json` or equivalent, with secrets redacted |
| `invocation_trace.txt` | Full invocation trace from Part 4 Step 3 |
| `error_expired_token.txt` | Output from Part 4 Step 4 |
| `error_tool_failure.txt` | Output from Part 4 Step 5 |
| Data flow diagram | End-to-end diagram (PNG, PDF, or ASCII) |
| Port table | Completed table showing all three services |
| Pair log | Role-swap timestamps and Part checkpoint answers |
| `README.md` | Tool schema justification and domain choice paragraph |
| Reflection prompts | Written answers to all prompts below |

---

#### Extension Challenges

These challenges are optional. They are designed to push your understanding beyond the rubric requirements.

##### Challenge 1: Add a Third Tool with Admin-Only Access

Implement a third tool — for example, `list_all_indexes` or `export_results` — that requires the `mcp:admin` scope. Verify that a token with only `mcp:read` receives HTTP 403 (Forbidden) when it attempts to invoke this tool, while a token with `mcp:admin` succeeds. Document the exact test commands and responses.

##### Challenge 2: Implement Automatic Token Refresh

The agent's token expires after a set lifetime. Without refresh, the agent would need the user to manually obtain a new token. Implement a token refresh mechanism in `oauth_middleware.py`: before every request, check whether the cached token will expire within the next 60 seconds; if so, automatically request a new token using the client credentials flow before proceeding. Write a test that demonstrates the refresh happening transparently — the agent completes a long-running multi-step task without any manual token intervention even after the original token expires.

##### Challenge 3: Add Rate Limiting and a Verification Test

Add rate limiting to your MCP server so that no single client can invoke more than 10 tool calls per minute. Return HTTP 429 (Too Many Requests) with a `Retry-After` header when the limit is exceeded. Then write a test script (`tests/test_rate_limit.py`) that sends 12 rapid tool calls with the same client token and asserts that the first 10 succeed and calls 11 and 12 receive HTTP 429.

---

#### Reflection Prompts

Answer each prompt in complete sentences. Your answers should reference specific decisions you made in this lab, not generic statements about security or AI.

- What is the advantage of MCP over giving the agent raw HTTP access to the same underlying data? What does the tool schema give you that a bare API endpoint does not?
- How did OAuth scopes limit what the agent could do — and what would happen if the agent's token were stolen?
- What would you need to add or change to make this deployment production-ready? Name at least three specific gaps.
- If collaboration beyond your pair occurred, identify it. Do you certify that this submission represents your pair's original work? Please identify any and all portions of your submission that were not originally written by you.
- Approximately how many hours did this lab take (I will not judge you for this at all...I am simply using it to gauge if the assignments are too easy or hard)?
- MCP is a relatively new standard. What problem would arise if every AI tool vendor invented their own proprietary tool-calling protocol instead? How does standardization (like MCP) change the security landscape — does it make security easier or harder, and for whom?
- Imagine a malicious MCP server that lies about its tool descriptions — for example, it advertises a tool called `search_files` that actually exfiltrates data to a remote server. How could an AI agent be tricked into calling this harmful tool? What trust mechanisms (at the protocol, deployment, or organizational level) would need to exist to prevent this attack?
