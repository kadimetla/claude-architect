"""Cell builder for segment-2-tool-design-and-mcp.ipynb.

Teaching-first notebook for Segment 2: Tool Design, Integration,
and Claude Code Workflows. Maps to CCA-F Domains 2 + 3 (18% + 20%,
38% combined - the heaviest pairing on the exam).
"""

from __future__ import annotations


def cells() -> list[tuple[str, str]]:
    return [
        ("md", _title_md),
        ("md", _lo_md),
        ("md", _concept_description_md),
        ("md", _concept_tool_choice_md),
        ("md", _concept_structured_errors_md),
        ("md", _concept_mcp_md),
        ("md", _concept_claude_md_hierarchy_md),
        ("md", _demo_setup_md),
        ("code", _imports_code),
        ("md", _demo_description_md),
        ("code", _description_code),
        ("md", _demo_tool_choice_md),
        ("code", _tool_choice_code),
        ("md", _demo_structured_error_md),
        ("code", _structured_error_code),
        ("md", _demo_mcp_config_md),
        ("code", _mcp_config_code),
        ("md", _mcp_server_source_md),
        ("code", _mcp_server_source_code),
        ("md", _demo_claude_md_hierarchy_md),
        ("code", _claude_md_hierarchy_code),
        ("md", _demo_tool_caching_md),
        ("code", _tool_caching_code),
        ("md", _claude_p_md),
        ("code", _claude_p_code),
        ("md", _exercise_md),
        ("md", _key_takeaways_md),
        ("md", _bridge_md),
    ]


_title_md = """\
# Segment 2: Tool Design, Integration, and Claude Code Workflows

**Duration:** 50 minutes
**Maps to:** CCA-F Domain 2 (Tools/MCP, 18%) + Domain 3 (Claude Code, 20%) = **38% of the exam**
**References:** [`../domain-2-tools-mcp.md`](../domain-2-tools-mcp.md), [`../domain-3-claude-code.md`](../domain-3-claude-code.md)

In Segment 1 you wrote the agent. Now we go one level deeper: the **tools** the agent calls, the **MCP servers** that ship those tools to multiple agents, and the **Claude Code instruction hierarchy** that lets a team enforce conventions without writing them in every prompt.
"""

_lo_md = """\
## Learning objectives

- Write **tool definitions** whose `description` and `input_schema` carry the contract, not the name
- Use **`tool_choice`** modes (`auto`, `any`, `tool`, `none`) to constrain agent behavior
- Return **structured tool errors** so the model can decide to retry, reformulate, or escalate
- Configure **`.mcp.json`** for stdio, SSE, and HTTP transports with `${ENV_VAR}` expansion
- Read a real **MCP server's source code** (`examples/mcp_cli/mcp_server.py`) and identify the FastMCP `@tool`, `@resource`, `@prompt` decorators and the stdio entrypoint
- Reason about the **CLAUDE.md hierarchy** (user, project, subtree, local) and its precedence
- Cache **tool definitions** with `cache_control` to amortize a large tool list across requests
- Run Claude Code **non-interactively** with `claude -p` for CI/CD
"""

_concept_description_md = """\
## The description is the contract

The Messages API tool shape is `name`, `description`, `input_schema`, and optional `cache_control`. Names are labels. **The description is the contract.** Spell out:

- What the tool does
- When the agent should call it
- When the agent should **not** call it
- What each input means
- What the success and failure shapes look like

Thin descriptions ("gets weather") leak responsibility into the prompt and the agent's improvisation. Opinionated descriptions let you delete prompt instructions you used to need.
"""

_concept_tool_choice_md = """\
## The four `tool_choice` modes

| Mode | Shape | When to use |
|---|---|---|
| `auto` | `{"type": "auto"}` | Default. Model decides. Supports `disable_parallel_tool_use`. |
| `any` | `{"type": "any"}` | Force the model to call *some* tool this turn. Useful for classification gates. |
| `tool` | `{"type": "tool", "name": "<tool_name>"}` | Force a *specific* tool. This is the lever for **structured output** in Segment 3. |
| `none` | `{"type": "none"}` | No tools this turn. The model must answer in prose. |

Set `disable_parallel_tool_use: true` when one tool's output feeds the next.
"""

_concept_structured_errors_md = """\
## Structured tool errors

When a tool returns an error, return it **as a structured object**, not a string:

```json
{
  "isError": true,
  "errorCategory": "transient | permanent | policy",
  "isRetryable": true,
  "message": "..."
}
```

The model reads `errorCategory` and `isRetryable` to decide. Categories:

- **`transient`** - retry with backoff (network blip, rate limit)
- **`permanent`** - do not retry; reformulate (bad input, unknown ID)
- **`policy`** - do not retry; escalate (over-cap refund, unauthorized action)

This is the same shape Segment 1's `enforce_refund_policy` hook returned. Same pattern, different surface.
"""

_concept_mcp_md = """\
## MCP: three transports, one variable-expansion rule

**Model Context Protocol** (MCP) is how you ship tools to *multiple* agents from a single server. The client config is just JSON:

| Transport | Use case | Shape |
|---|---|---|
| **stdio** | Local servers, scripts | `{"command": "npx", "args": [...], "env": {"VAR": "${VAR}"}}` |
| **SSE** | Streaming events, server push | `{"type": "sse", "url": "https://...", "headers": {...}}` |
| **HTTP** | Request/response, simple integration | `{"type": "http", "url": "...", "headers": {...}}` |

**`${ENV_VAR}` expansion** works in `env`, `args`, and `headers`. This is how secrets stay out of the file. **Never** commit a literal token; always use `${GITHUB_TOKEN}` (or similar) and source it from the shell.

The file goes at `.mcp.json` (project) or `~/.claude.json` (user). Project values override user values at the server level.
"""

_concept_claude_md_hierarchy_md = """\
## The CLAUDE.md instruction hierarchy

Four tiers, in precedence order from broadest to most specific:

| Tier | Path | Purpose |
|---|---|---|
| **User** | `~/.claude/CLAUDE.md` | Your personal defaults, every project |
| **Project** | `<repo>/CLAUDE.md` | Team conventions, checked in, version-controlled |
| **Subtree** | `<repo>/<subdir>/CLAUDE.md` | Loaded on demand when files in that subtree are touched |
| **Local override** | `<repo>/CLAUDE.local.md` | Gitignored, personal tweaks for one machine |

The Agent SDK loads user + project when you pass `settingSources=["user", "project"]`.

**Subtree files are the unsung hero.** A frontend rule does not need to pollute a backend file. Put React conventions in `frontend/CLAUDE.md`; they only load when you read frontend files.
"""

_demo_setup_md = """\
## Demo: tool definitions, tool_choice modes, and the structured error contract

We will exercise each concept above with a small live call. Keep an eye on:

- How the same tool behaves differently with a **thin** vs **opinionated** description
- How `stop_reason` changes when you flip `tool_choice` modes
- How the model reacts to a `policy` error vs a `transient` error
- How `.mcp.json` reads as plain JSON config (no MCP client invocation here, just config-as-data)
"""

_imports_code = """\
import json
import os
from pathlib import Path

from anthropic import Anthropic

try:
    from dotenv import load_dotenv
    load_dotenv(Path.cwd().parent / ".env")
except ImportError:
    pass

REPO_ROOT = Path.cwd().parent if Path.cwd().name == "notebooks" else Path.cwd()
client = Anthropic()
MODEL = "claude-sonnet-4-6"
"""

_demo_description_md = """\
## Thin vs opinionated descriptions

Same tool name, two descriptions. Same user prompt. Watch how the second version changes the model's behavior **without changing the prompt**.
"""

_description_code = """\
THIN_WEATHER = {
    "name": "get_weather",
    "description": "gets weather",
    "input_schema": {
        "type": "object",
        "properties": {"location": {"type": "string"}},
        "required": ["location"],
    },
}

OPINIONATED_WEATHER = {
    "name": "get_weather",
    "description": (
        "Get the current weather conditions for a specific city. Returns "
        "temperature in Celsius, conditions (clear, cloudy, rain, snow), and "
        "humidity percent. Call this when the user asks about weather. Do NOT "
        "call for forecasts more than 24 hours out - this tool only returns "
        "current conditions. If the city is ambiguous (e.g. 'Springfield'), "
        "ask the user to disambiguate BEFORE calling."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "city": {"type": "string", "description": "City name; disambiguate with region if ambiguous"},
            "region": {"type": "string", "description": "Optional state/country to disambiguate"},
        },
        "required": ["city"],
    },
}

PROMPT = "What's the weather in Springfield?"

for label, tool in [("thin", THIN_WEATHER), ("opinionated", OPINIONATED_WEATHER)]:
    resp = client.messages.create(
        model=MODEL, max_tokens=400, tools=[tool],
        messages=[{"role": "user", "content": PROMPT}],
    )
    print(f"--- {label} description ---")
    print(f"stop_reason: {resp.stop_reason}")
    for block in resp.content:
        if block.type == "text":
            print(f"text: {block.text[:200]}")
        elif block.type == "tool_use":
            print(f"tool_use: {block.name}({dict(block.input)})")
    print()
"""

_demo_tool_choice_md = """\
## All four `tool_choice` modes

Run the same prompt against each mode. Notice how `stop_reason` flips between `tool_use` and `end_turn` based purely on the mode.
"""

_tool_choice_code = """\
WEATHER_TOOL = OPINIONATED_WEATHER  # reuse from the previous cell
USER = "I'm planning a picnic in Boston tomorrow. Should I go?"

modes = [
    {"type": "auto"},
    {"type": "any"},
    {"type": "tool", "name": "get_weather"},
    {"type": "none"},
]

for mode in modes:
    resp = client.messages.create(
        model=MODEL, max_tokens=300, tools=[WEATHER_TOOL], tool_choice=mode,
        messages=[{"role": "user", "content": USER}],
    )
    print(f"mode={mode} -> stop_reason={resp.stop_reason}")
    for block in resp.content:
        if block.type == "tool_use":
            print(f"  tool_use: {block.name}({dict(block.input)})")
        elif block.type == "text":
            print(f"  text: {block.text[:120]!r}")
    print()
"""

_demo_structured_error_md = """\
## Structured error contract

A helper to build the structured error payload. We show two cases: a **transient** error (the model should retry) and a **policy** error (the model must not).
"""

_structured_error_code = """\
def make_tool_error(category: str, message: str, *, retryable: bool) -> dict:
    \"\"\"Build a structured tool-result error payload.

    The model reads errorCategory and isRetryable to decide whether to
    retry, reformulate, or escalate. Bare strings force it to guess.
    \"\"\"
    assert category in {"transient", "permanent", "policy"}, category
    return {
        "isError": True,
        "errorCategory": category,
        "isRetryable": retryable,
        "message": message,
    }


print("transient (retryable):")
print(json.dumps(make_tool_error("transient",
                                 "weather API timed out", retryable=True), indent=2))
print()
print("policy (not retryable):")
print(json.dumps(make_tool_error("policy",
                                 "weather API blocked for this region", retryable=False),
                 indent=2))
"""

_demo_mcp_config_md = """\
## `.mcp.json` as config-as-data

Open `../.mcp.json` and pretty-print its structure. Four servers, three transports, env-var expansion in the right places. This is the file the cohort can copy and modify for their own projects.
"""

_mcp_config_code = """\
mcp_path = REPO_ROOT / ".mcp.json"
config = json.loads(mcp_path.read_text(encoding="utf-8"))
servers = config["mcpServers"]

print(f"{len(servers)} servers configured\\n")
for name, spec in servers.items():
    if "command" in spec:
        transport = "stdio"
        endpoint = f"{spec['command']} {' '.join(spec.get('args', []))}"
    elif spec.get("type") == "sse":
        transport = "SSE"
        endpoint = spec.get("url", "")
    elif spec.get("type") == "http":
        transport = "HTTP"
        endpoint = spec.get("url", "")
    else:
        transport = "unknown"
        endpoint = ""

    # Find env-var expansion points
    raw = json.dumps(spec)
    env_refs = sorted(set(s for s in raw.split("${") if "}" in s for s in [s.split("}", 1)[0]] if s))

    print(f"  {name}")
    print(f"    transport: {transport}")
    print(f"    endpoint:  {endpoint[:80]}")
    if env_refs:
        print(f"    env vars:  {env_refs}")
    print()
"""

_mcp_server_source_md = """\
## What an MCP server actually looks like (source code, not config)

`.mcp.json` told us the **client side**: which servers to start, what transport, which env vars. The **server side** is real Python. We did not stand one up in a Jupyter kernel because the stdio handshake cross-talks with the notebook's own stdio, but we can read the source of a complete, runnable example.

`../examples/mcp_cli/mcp_server.py` is a **FastMCP** server: ~95 lines, exposes six dummy documents as resources, plus a `read_doc_contents` tool, an `edit_document` tool, and a `format` prompt. It runs over **stdio** when invoked by an MCP client. This is the exact shape your `.mcp.json` stdio servers conform to.

This code is reference material from Anthropic's "Claude with the Anthropic API" Skilljar course. Attribution lives at [`../examples/mcp_cli/NOTICE.md`](../examples/mcp_cli/NOTICE.md). After class, run it locally with `uv run main.py` from `examples/mcp_cli/` to see the same client-server protocol round-trip in your own terminal.

The next cell prints the file so you can read the key idioms inline: `@mcp.tool(...)`, `@mcp.resource(...)`, `@mcp.prompt(...)`, and the trailing `mcp.run(transport="stdio")`.
"""

_mcp_server_source_code = """\
mcp_server_path = REPO_ROOT / "examples" / "mcp_cli" / "mcp_server.py"
if not mcp_server_path.exists():
    print(f"[skip] {mcp_server_path} not found; see examples/mcp_cli/NOTICE.md")
else:
    source = mcp_server_path.read_text(encoding="utf-8")
    # Walk the structurally interesting lines, not the whole 95-line file
    for i, line in enumerate(source.splitlines(), start=1):
        stripped = line.strip()
        if (stripped.startswith("@mcp.")
                or stripped.startswith("def ")
                or stripped.startswith("mcp = FastMCP")
                or stripped.startswith("mcp.run(")):
            print(f"  L{i:>3}: {line}")
    print()
    print(f"Total file: {len(source.splitlines())} lines at {mcp_server_path}")
    print("Tools, resources, prompts: three FastMCP primitives, one stdio entrypoint.")
"""

_demo_claude_md_hierarchy_md = """\
## CLAUDE.md hierarchy walk

We will not call the API here - we just print what each tier covers in this repo.
"""

_claude_md_hierarchy_code = """\
tiers = [
    ("User", Path.home() / ".claude" / "CLAUDE.md", "personal defaults, every project"),
    ("Project", REPO_ROOT / "CLAUDE.md", "team conventions, checked in"),
    ("Subtree", REPO_ROOT / "notebooks" / "CLAUDE.md", "loaded on demand"),
    ("Local override", REPO_ROOT / "CLAUDE.local.md", "gitignored, personal tweaks"),
]
for tier, path, purpose in tiers:
    present = "[present]" if path.exists() else "[absent ]"
    print(f"{present} {tier:<16} {path}")
    print(f"           {purpose}\\n")
"""

_claude_p_md = """\
## `claude -p`: the headless surface (Domain 3, plan mode)

The Claude Code CLI runs interactively *and* headlessly. `claude -p "<prompt>"` is the bridge to CI/CD. This is **plan mode for automation**: no terminal, no human in the loop, just a one-shot run that returns text or JSON.

Common shapes:

```powershell
# audit the project CLAUDE.md
claude -p "audit ./CLAUDE.md against repo conventions. List 3 specific improvements."

# JSON output for scripting, with an allowlist
claude -p "list all Python files with missing docstrings" --output-format json --allowedTools "Read,Grep,Glob"
```

Pipe the JSON into a GitHub Actions step and you have an LLM-backed lint that runs on every PR.

The next cell shells out via `subprocess` to prove the surface works. It falls back gracefully if `claude` is not on the path - which it often is not inside a Jupyter kernel that loaded its own environment. **Read the output, do not depend on the command running.**
"""

_claude_p_code = """\
import shutil
import subprocess

claude_cli = shutil.which("claude")
if claude_cli is None:
    print("[skip] `claude` is not on this kernel's PATH.")
    print("       Run the headless call in your PowerShell terminal instead:")
    print()
    print('       claude -p "What is the agentic loop in one sentence?" --output-format json')
    print()
    print("       Inside a notebook the CLI often conflicts with the SDK auth surface.")
    print("       The point of this cell is the SHAPE, not the side effect.")
else:
    try:
        # Short prompt, JSON output, 30-second wall clock. Adjust if your CLI is slower.
        result = subprocess.run(
            [claude_cli, "-p", "Say the words 'plan mode works' and nothing else.",
             "--output-format", "json"],
            capture_output=True, text=True, timeout=30,
        )
        print(f"[exit code] {result.returncode}")
        print(f"[stdout]\\n{result.stdout[:500]}")
        if result.stderr:
            print(f"[stderr]\\n{result.stderr[:200]}")
    except subprocess.TimeoutExpired:
        print("[timeout] `claude -p` did not return in 30s. Try it in PowerShell.")
    except Exception as exc:  # noqa: BLE001 - teaching demo, surface everything
        print(f"[error] {type(exc).__name__}: {exc}")
        print("Run the command in your terminal; it is the canonical surface.")
"""

_demo_tool_caching_md = """\
## Tool caching with `cache_control`

When the tool block is large (a dozen tools, opinionated descriptions, schemas), you pay tokens for it on **every** request. `cache_control` marks a prefix of the request as cacheable; subsequent calls within the cache lifetime hit the cache and skip re-billing those input tokens.

Anthropic supports two patterns. **Automatic caching** (recommended) is a single top-level kwarg on `messages.create()` that lets the SDK place the cache breakpoint for you. **Explicit breakpoints** put `cache_control` on individual content or tool blocks for fine-grained control (up to 4 breakpoints per request). We demo the automatic pattern because it is one line and it is what Anthropic's own cookbook recommends.

```python
# Automatic caching - one kwarg, breakpoint placed for you
resp = client.messages.create(
    model=MODEL,
    cache_control={"type": "ephemeral"},
    tools=tools,
    messages=[{"role": "user", "content": prompt}],
)
```

The response carries `cache_creation_input_tokens` when the cache is written and `cache_read_input_tokens` when it is hit. When caching engages, `input_tokens` drops dramatically because the tool block is no longer counted as fresh input.

**The minimum-size gotcha is real.** On Sonnet 4.x the cacheable prefix must clear **1024 tokens**; on **Haiku 4.5** and **Opus** it is **4096 tokens** (per the Anthropic cookbook). Below the floor, `cache_control` is silently ignored - no creation, no reads, no warning. A single small tool plus a short prompt will *look* like caching is broken when really the request never crossed the threshold. Production tool blocks routinely carry a dozen opinionated tools, which is exactly when caching pays for itself.

Cookbook anchor: `../claude-cookbooks-main/misc/prompt_caching.ipynb` (Anthropic's canonical caching walkthrough; `cache_control` as kwarg, multi-turn, and explicit breakpoints).

We run a **four-tool** block (weather + forecast + air quality + sun times) twice with `cache_control` as a top-level kwarg. First call writes the cache. Second call reads it. Watch the counters flip.
"""

_tool_caching_code = '''\
# Sonnet 4.x will not cache a prefix below 1024 input tokens. A single weather
# tool plus a short prompt sits around 700, so cache_control silently no-ops.
# Production tool blocks carry a dozen tools; we simulate that with three more
# opinionated definitions to push the prefix past the floor.

OPINIONATED_FORECAST = {
    "name": "get_forecast",
    "description": (
        "Return a multi-day weather forecast for a city. Days 1-7 are supported. "
        "Returns daily high/low in Celsius, conditions, precipitation probability, "
        "and wind speed in km/h. Call when the user asks about future weather "
        "beyond today. Do NOT call for current conditions - use get_weather. "
        "If the city is ambiguous, ask the user to disambiguate BEFORE calling. "
        "Forecasts past day 7 are not supported; tell the user instead of calling."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "city": {"type": "string", "description": "City name"},
            "region": {"type": "string", "description": "Optional state/country"},
            "days": {"type": "integer", "minimum": 1, "maximum": 7,
                     "description": "Number of forecast days, 1-7"},
        },
        "required": ["city", "days"],
    },
}

OPINIONATED_AIR_QUALITY = {
    "name": "get_air_quality",
    "description": (
        "Return the current air-quality index (AQI) and dominant pollutant for a "
        "city. AQI is reported on the US EPA scale (0-500). Call when the user "
        "asks about air quality, smog, pollen, or whether it is safe to exercise "
        "outdoors. Do NOT call for general weather - use get_weather. AQI data "
        "is updated hourly; do not promise real-time precision finer than that. "
        "If no monitoring station exists within 50km of the city, return a "
        "policy error and explain coverage gaps instead of inventing a number."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "city": {"type": "string", "description": "City name"},
            "region": {"type": "string", "description": "Optional state/country"},
        },
        "required": ["city"],
    },
}

OPINIONATED_SUN_TIMES = {
    "name": "get_sun_times",
    "description": (
        "Return sunrise, sunset, civil twilight start, and civil twilight end "
        "for a city on a specific date. All times returned in the city's local "
        "timezone as ISO 8601 strings. Call when the user asks about daylight, "
        "golden hour, dawn, dusk, or solar event timing. Do NOT call for "
        "general weather or moon phases. Dates more than 100 years in the "
        "future are not supported; return a permanent error in that case."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "city": {"type": "string"},
            "region": {"type": "string"},
            "date": {"type": "string", "description": "ISO 8601 date, YYYY-MM-DD"},
        },
        "required": ["city", "date"],
    },
}

# Four-tool block, no per-tool cache_control marker. We engage caching via the
# top-level cache_control kwarg on messages.create() - the "automatic caching"
# pattern from Anthropic's cookbook. The SDK places the breakpoint for us.
TOOLS = [
    OPINIONATED_WEATHER,
    OPINIONATED_FORECAST,
    OPINIONATED_AIR_QUALITY,
    OPINIONATED_SUN_TIMES,
]

USER = "What's the weather in Boston?"

def call(label: str) -> None:
    resp = client.messages.create(
        model=MODEL,
        max_tokens=200,
        cache_control={"type": "ephemeral"},  # automatic caching
        tools=TOOLS,
        messages=[{"role": "user", "content": USER}],
    )
    usage = resp.usage
    created = getattr(usage, "cache_creation_input_tokens", 0) or 0
    read = getattr(usage, "cache_read_input_tokens", 0) or 0
    print(f"[{label}] input={usage.input_tokens}  "
          f"cache_creation={created}  cache_read={read}  "
          f"stop_reason={resp.stop_reason}")

print("Call 1 (writes the cache):")
call("call 1")
print("\\nCall 2 (reads from cache; input_tokens drops, cache_read > 0):")
call("call 2")
print()
print("Expected shape: call 1 cache_creation > 0, call 2 cache_read > 0.")
print("Minimum cacheable prefix on Sonnet 4.x is 1024 tokens; on Haiku 4.5/Opus it is 4096.")
print("Below the floor, cache_control is silently ignored. Ephemeral TTL is ~5 minutes.")
'''

_exercise_md = """\
## Exercise (5 minutes)

Sketch a **CLAUDE.md hierarchy for a 3-team monorepo** (backend / frontend / infra). Name **three files**:

1. One **project-root** `CLAUDE.md`
2. Two **subtree** `CLAUDE.md` files

For each, write a **one-line statement** of what belongs there and what does **not**.

Deliverable: three file paths plus three one-liners in chat.
"""

_key_takeaways_md = """\
## Key takeaways

- **Tool descriptions are the contract**, names are just labels. Spell out behavior, inputs, error shapes, and when *not* to call.
- **Tool scoping is subagent design.** When an agent's tool list grows past ~5, split into a coordinator with scoped subagents (Segment 1's live demo). Each subagent sees only the tools its role needs; the coordinator's surface stays small.
- The four **`tool_choice`** modes are `auto`, `any`, `tool`, `none`. `tool` is the lever for forced structured output (Segment 3).
- **Structured errors** with `errorCategory` and `isRetryable` let the model decide. Bare strings force it to guess.
- **MCP transports** are stdio / SSE / HTTP, and `${ENV_VAR}` expansion keeps secrets out of source.
- **CLAUDE.md hierarchy** layers from user to project to subtree to local. Use subtree files to keep frontend rules off backend files.
- **Prompt caching** is one kwarg: `cache_control={"type": "ephemeral"}` on `messages.create()` (automatic caching, recommended). Floor is **1024 tokens** on Sonnet 4.x and **4096** on Haiku 4.5/Opus; below the floor the marker is silently ignored. First call writes, second call reads (~5-min TTL). Cache writes cost 1.25x base input; reads cost 0.1x.
- `claude -p` is your CI/CD answer. The CLI runs headless with `--output-format json` for scripting.

**Cookbook anchors for further study:**
- `../claude-cookbooks-main/tool_use/tool_choice.ipynb` (the four modes, runnable)
- `../claude-cookbooks-main/tool_use/parallel_tools.ipynb` (parallel + caching, runnable)
- `../claude-cookbooks-main/tool_use/customer_service_agent.ipynb` (Anthropic's reference for the Segment 1 agent shape)

**Reference application for further study:**
- `../examples/mcp_cli/` - complete MCP CLI app (stdio FastMCP server + client + interactive chat). Reference material from Anthropic's "Claude with the Anthropic API" Skilljar course; attribution in `../examples/mcp_cli/NOTICE.md`. Run it locally to see the same protocol round-trip we walked as config-as-data.
"""

_bridge_md = """\
## Bridge to Segment 3

> "Tools give the agent hands. Prompts and schemas decide what comes out. Let's make those outputs trustworthy."

Open `segment-3-invoice-extractor.ipynb`.
"""
