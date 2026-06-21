---
layout: assignment
permalink: /Assignments/MCPServer
title: "CS357: Foundations of Artificial Intelligence - Lab: Build and Deploy an MCP Server with OAuth 2.0"

info:
  coursenum: CS357
  points: 100
  goals:
    - To implement a working MCP server that exposes at least two tools
    - To secure the MCP server with OAuth 2.0 client credentials flow
    - To connect the MCP server to a local AI agent and demonstrate tool invocation
    - To document the full data flow from agent request through OAuth token to tool response
  rubric:
    - weight: 30
      description: MCP Server Implementation
      preemerging: No working MCP server is submitted, or the server does not expose any callable tools
      beginning: The server starts and exposes at least one tool, but tool execution fails or input validation is absent
      progressing: Two tools are implemented and callable, with input schema validation and structured logging in place, with a minor gap such as missing error handling for malformed inputs
      proficient: At least two tools are implemented (one that reads data, one that transforms or processes data), input schemas are validated before processing, every invocation is logged with timestamp and result status, and the server handles invalid inputs gracefully with informative error responses
    - weight: 25
      description: OAuth Integration
      preemerging: No OAuth integration is attempted, or the server accepts requests without any token validation
      beginning: Token validation is present but scopes are not enforced, or the implementation accepts expired tokens
      progressing: Bearer token validation is implemented and rejects requests without a valid token, with scope enforcement present for at least one scope, and token expiry rejection demonstrated
      proficient: The server validates Bearer tokens on every request, enforces at least two scopes (read and admin), correctly rejects expired tokens with an appropriate HTTP status and error body, and the OAuth configuration is documented with the client, resource server, and authorization server roles identified
    - weight: 25
      description: Agent Integration and Demo
      preemerging: The MCP server is not connected to any agent, or the agent cannot discover or invoke the tools
      beginning: The agent can discover tools but tool invocation fails or only succeeds in a manually constructed test rather than an organic agent task
      progressing: The agent successfully invokes at least one tool as part of a real task, with the invocation trace captured showing tool discovery and the tool call, with error case testing attempted
      proficient: The agent completes a task that naturally requires both MCP tools, the full invocation trace is captured showing tool discovery, token exchange, tool call, and response, and at least two error cases are tested and documented (expired token and tool failure)
    - weight: 20
      description: Documentation and Security Analysis
      preemerging: No data flow diagram or pair log is submitted
      beginning: A diagram exists but omits the OAuth token exchange step, and the port table is missing or incomplete
      progressing: The data flow diagram covers the agent, MCP server, and OAuth server with the token exchange shown, the port table is complete, and reflection prompts are answered with reference to the lab
      proficient: The data flow diagram is accurate end-to-end including token issuance, Bearer header transmission, scope validation, and tool response, the port table covers all three services with no collisions, and reflection answers articulate the specific security properties that OAuth adds over unauthenticated MCP access
  readings:
    - rtitle: "MCP Server Activity"
      rlink: "https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-mcpserver.md"
    - rtitle: "The Local Agent Stack Activity"
      rlink: "https://www.billmongan.com/LiaScript/?https://raw.githubusercontent.com/BillJr99/Ursinus-CS357/gh-pages/_pages/Activities/liascript-agentstack.md"

tags:
  - mcp
  - oauth
  - agents
  - security

---

In this lab, you and your partner will build a Model Context Protocol (MCP) server that exposes real tools to a local AI agent, then secure it with OAuth 2.0 so that only authorized clients can invoke those tools. The skills being assessed are implementation precision (does the server actually work?), security integration (does OAuth actually gate access?), and documentation clarity (can someone else understand the data flow?). This lab is completed in **pairs using driver/navigator roles with swaps at least every 30 minutes and a swap log**.

## Part 1: Design and Plan

Choose a domain for your MCP server from the following options (or propose an alternative to the instructor): local file search, calendar query, weather API wrapping a local data file, or code repository summary. For each of your two tools, write the complete tool schema: `name`, `description`, `input_schema` (as a JSON Schema object with required fields and types), and the expected return type and structure.

Sketch the OAuth 2.0 flow for your deployment: identify who is the client (the agent), who is the authorization server (use Keycloak in dev mode, a mock OAuth server, or another option approved by the instructor), and what scopes are required (`mcp:read` for tool invocation, `mcp:admin` for listing all available tools). Produce the **port table** for all three services (MCP server, OAuth authorization server, AI agent) and resolve any collisions before writing any code.

## Part 2: Implement the MCP Server

Using the MCP Python SDK (`modelcontextprotocol/python-sdk`) or the TypeScript SDK, implement your server and expose your two tools. The first tool must read or retrieve data; the second must transform or process data in some way. Before executing any tool, validate that the inputs match the declared schema and return a structured error response if they do not. Add structured logging to every tool invocation: log the timestamp, the tool name, the caller identity (from the token, in Part 3), the inputs (redact any sensitive values), and the result status (success or error). Verify both tools work by calling them directly with `curl` before adding OAuth.

## Part 3: Add OAuth 2.0

Register your MCP server as an OAuth 2.0 resource server with your chosen authorization server. Implement Bearer token validation on every incoming request: requests without a valid token must be rejected with HTTP 401. Enforce scopes: a token with only `mcp:read` may invoke tools, while listing all available tools requires `mcp:admin`. Demonstrate token expiry by issuing a short-lived token, waiting for it to expire, and showing that the server returns HTTP 401 with an appropriate error body. Document the OAuth configuration (client ID, scopes, token endpoint URL) in your submission, with secrets redacted.

## Part 4: Agent Integration

Configure your local AI agent to use your MCP server by adding it to the agent's MCP configuration (for example, Claude Code's `~/.claude.json` or the equivalent for your chosen agent). Give the agent a task that naturally requires using both of your MCP tools — do not construct the tool calls manually. Capture the **full invocation trace**: tool discovery (the agent listing available tools), the token exchange or token use, the tool call with its parameters, and the tool response. Then test two error cases: present an expired token and show the rejection, then cause the tool itself to fail (e.g., search for a nonexistent resource) and show how the agent handles the error response.

## Deliverables

Submit a ZIP containing: your MCP server source code, the OAuth authorization server configuration (secrets redacted), the agent MCP configuration file, the full invocation trace from Part 4, the error case test outputs, a data flow diagram showing the complete path from agent request through OAuth token issuance to tool response, the port table, and the pair log with role-swap timestamps.

## Reflection Prompts

- What is the advantage of MCP over giving the agent raw HTTP access to the same underlying data? What does the tool schema give you that a bare API endpoint does not?
- How did OAuth scopes limit what the agent could do — and what would happen if the agent's token were stolen?
- What would you need to add or change to make this deployment production-ready? Name at least three specific gaps.
- If collaboration beyond your pair occurred, identify it. Do you certify that this submission represents your pair's original work? Please identify any and all portions of your submission that were not originally written by you.
- Approximately how many hours did this lab take (I will not judge you for this at all...I am simply using it to gauge if the assignments are too easy or hard)?
