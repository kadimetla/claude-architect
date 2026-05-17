# Domain 2: Tool Design & MCP Integration

> Reference scaffold - maps to **COURSE-FLOW.md Segment 2**

## What this domain covers

This domain is about giving Claude **hands**. A model without tools can reason, summarize, and write prose. A model with well-designed tools can read files, hit APIs, query databases, and orchestrate real work. Domain 2 covers the four pillars that make that reliable in production: **tool definitions** (name, description, input_schema), **structured error responses** that let the agent recover instead of crashing, **scoped tool distribution** with `tool_choice` to control selection, and **MCP server configuration** via `.mcp.json` to wire in external systems. It closes with the **built-in Claude Code tools** (Read, Write, Edit, Bash, Grep, Glob) and when to wrap them versus write your own.

## Core concepts

### Tool definitions: name, description, input_schema

Every tool you expose to Claude has three required fields. **`name`** is the string identifier the model uses to call the tool, like `get_stock_price`. **`description`** is the natural-language explanation of what the tool does, when to use it, and what it returns. Anthropic's docs are emphatic: **detailed descriptions are the single biggest lever for tool-use accuracy**. The model picks tools based on description text, not name. **`input_schema`** is a JSON Schema (draft 2020-12) describing the input shape, typically `type: object` with `properties` and a `required` array.

Optional fields worth knowing: **`cache_control`** with `{"type": "ephemeral", "ttl": "5m"}` or `"1h"` caches the tool definition across requests (huge cost win on long-lived agents). **`strict: true`** guarantees the model's tool input matches the schema exactly.

```json
{
  "name": "get_stock_price",
  "description": "Get the current stock price for a given ticker symbol.",
  "input_schema": {
    "type": "object",
    "properties": {
      "ticker": {"type": "string", "description": "The stock ticker symbol, e.g. AAPL for Apple Inc."}
    },
    "required": ["ticker"]
  }
}
```

### Structured error responses

The anti-pattern: a tool throws an uncaught exception, the runtime crashes, the agent loop dies. Almost as bad: the tool returns an empty string on failure, the model assumes success, and the conversation goes off a cliff.

The correct pattern is to **return errors as content inside `tool_result`**, with `isError: true` plus structured metadata the model can reason over. Add fields like `errorCategory` (`"transient"`, `"permanent"`, `"policy"`) and `isRetryable` (`true`/`false`). The model then decides: retry the call, fall back to another tool, or surface the failure to the user.

```json
{
  "type": "tool_result",
  "tool_use_id": "toolu_01A09q90qw90lq917835lq9",
  "content": "{\"error\": \"Rate limit exceeded\", \"errorCategory\": \"transient\", \"isRetryable\": true, \"retryAfterSeconds\": 30}",
  "is_error": true
}
```

Treat tool errors like HTTP status codes: machine-readable, categorized, and never silent.

### Scoped tool distribution + `tool_choice`

Do not dump 30 tools into one agent. Selection accuracy degrades sharply past **roughly 5 tools per agent**. If you need more capability, split into **subagents** with scoped tool sets and let an orchestrator route between them.

`tool_choice` is how you control whether and which tool the model invokes:

- **`{"type": "auto", "disable_parallel_tool_use": false}`** - model decides; set `disable_parallel_tool_use: true` to force serial execution (useful when later calls depend on earlier results)
- **`{"type": "any", "disable_parallel_tool_use": false}`** - model must call some tool, but picks which one
- **`{"type": "tool", "name": "<name>"}`** - model must call this specific tool; use this to guarantee the first step of a pipeline, or to force structured extraction (define your output as a tool's input_schema and the model returns validated JSON for free)
- **`{"type": "none"}`** - no tools allowed; model must answer in prose

The `tool` mode is the structured-output cheat code. Define your output schema as a tool input_schema, force the model to call it, ship the parsed JSON downstream.

### MCP server configuration (.mcp.json)

The **Model Context Protocol** lets Claude Code talk to external servers (GitHub, databases, SaaS APIs, custom internal tools) over a standardized interface. Configuration lives in **`.mcp.json` at project root** (committed, team-wide) or **`~/.claude.json`** at user-level (personal, not shared). Project config wins for shared team servers; user config wins for personal credentials and experimental servers.

Three transports are supported:

- **stdio** - local subprocess, most common, used for `npx`-launched servers
- **SSE** - Server-Sent Events over HTTP, for remote servers with streaming
- **HTTP** - plain HTTP for simpler remote servers

`${ENV_VAR}` expansion works in `env`, `args`, and `headers` (recent fix per the changelog), so secrets stay out of git.

```json
// stdio (local subprocess)
{
  "mcpServers": {
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {"GITHUB_TOKEN": "${GITHUB_TOKEN}"}
    }
  }
}

// SSE (remote streaming)
{
  "mcpServers": {
    "remote-api": {
      "type": "sse",
      "url": "https://api.example.com/mcp/sse",
      "headers": {"Authorization": "Bearer ${API_TOKEN}"}
    }
  }
}
```

### Built-in Claude Code tools

Claude Code ships with **Read** (file contents), **Write** (create/overwrite), **Edit** (precise string replacement), **Bash** (shell), **Grep** (ripgrep-backed search), and **Glob** (file pattern matching). These are battle-tested and the model knows them deeply.

Write a custom tool only when a built-in cannot do the job. The classic anti-pattern: a custom `analyze_dependencies` tool the agent ignores because `Grep` for `import` statements is faster and the model trusts it more. The fix is to write a custom tool description that **explicitly contrasts with the built-in** ("Unlike Grep, this resolves transitive imports through the lockfile and returns a dependency graph").

## Demo anchor

See **COURSE-FLOW.md Segment 2** for the live walkthrough. Code references:

- `private/claude-cookbooks-main/tool_use/tool_use_with_pydantic.ipynb` - Pydantic → JSON Schema → tool input_schema pattern
- `private/claude-cookbooks-main/tool_use/tool_choice.ipynb` - tool_choice mode examples
- `private/claude-cookbooks-main/tool_use/parallel_tools.ipynb` - parallel tool execution
- `private/claude-cookbooks-main/managed_agents/cma-mcp/` - MCP server configuration walk-through
- `private/claude-cookbooks-main/tool_use/customer_service_agent.ipynb` - multi-tool agent

## Production tips (Tim's voice)

- **Descriptions, not names, do the work.** The model picks tools based on the description text. A tool named `get_data` with description "Fetch customer record by ID, returns name, email, plan tier, and signup date" beats one named `getCustomerRecordById` with description "Gets data." Write descriptions like you are onboarding a new junior engineer.
- **Cap agents at roughly 5 tools.** Beyond that, selection accuracy degrades. If you need more, split into subagents with scoped tool sets and route via an orchestrator.
- **`tool_choice: {"type": "tool", "name": "..."}` is your structured-output cheat code.** Define the output as a tool's input_schema, force the model to call it, parse validated JSON downstream. No regex on prose. No "please return only JSON" prompt hacks.
- **Return errors as tool_result content, never as exceptions.** A thrown exception crashes the agent loop. A structured error with `errorCategory` and `isRetryable` lets the agent recover.
- **`.mcp.json` lives in git. Secrets do not.** Use `${ENV_VAR}` expansion for every credential and document the required env vars in your README.

## Further reading

- Anthropic: Tool use overview - https://docs.claude.com/en/docs/agents-and-tools/tool-use
- Anthropic: tool_choice parameter - https://docs.claude.com/en/api/messages
- Claude Code: MCP integration - https://docs.claude.com/en/docs/claude-code/mcp
- Model Context Protocol spec - https://modelcontextprotocol.io
- `private/claude-cookbooks-main/tool_use/` - full tool-use cookbook (~15 notebooks)
