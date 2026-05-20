"""Cell builder for segment-2-5-control-surfaces.ipynb.

Bridge / deep-dive notebook between Segments 2 and 3. Self-study
material, not live-taught in the 4-hour window. Action-packed CCA-F
exam stud across four control surfaces the other notebooks touch
lightly:

  1. Tool enumeration (four lenses, MCP `list_tools` as headliner)
  2. `tool_choice` depth + `disable_parallel_tool_use`
  3. Stop conditions (`stop_reason`, `stop_sequences`, `max_tokens`,
     `pause_turn`, `refusal`)
  4. Managed Agents in Claude Console: `memory_stores`, `vaults`,
     `agents`, `sessions` (live SDK surface, confirmed via spike)
  5. CCA-F exam stud (cheat sheet + 5 inline practice questions)

Maps to all five CCA-F domains. Haiku 4.5 throughout except where
Sonnet 4.6 is the only option (e.g. retrieving a Console agent whose
configured model is Sonnet 4.6).
"""

from __future__ import annotations


def cells() -> list[tuple[str, str]]:
    return [
        # --- Section 0: orientation ---
        ("md", _title_md),
        ("md", _lo_md),
        ("md", _setup_md),
        ("code", _imports_code),
        # --- Section 1: three tiers tools come from + the enumeration discipline ---
        ("md", _tier_section_md),
        ("md", _tier1_md),
        ("code", _tier1_code),
        ("md", _tier2_md),
        ("code", _tier2_code),
        ("md", _tier3_md),
        ("md", _enumeration_md),
        ("code", _enumeration_code),
        # --- Section 2: tool_choice depth ---
        ("md", _tc_section_md),
        ("md", _tc_auto_vs_any_md),
        ("code", _tc_auto_vs_any_code),
        ("md", _tc_forced_md),
        ("code", _tc_forced_code),
        ("md", _tc_none_md),
        ("code", _tc_none_code),
        ("md", _tc_disable_parallel_md),
        ("code", _tc_disable_parallel_code),
        # --- Section 3: stop conditions ---
        ("md", _stop_section_md),
        ("md", _stop_reason_tree_md),
        ("md", _stop_sequences_md),
        ("code", _stop_sequences_code),
        ("md", _max_tokens_md),
        ("code", _max_tokens_code),
        ("md", _pause_refusal_md),
        # --- Section 4: Managed Agents in Console (headliner) ---
        ("md", _console_section_md),
        ("md", _console_memstore_md),
        ("code", _console_memstore_code),
        ("md", _console_vault_md),
        ("code", _console_vault_code),
        ("md", _console_agent_md),
        ("code", _console_agent_code),
        ("md", _console_tieback_md),
        # --- Section 5: CCA-F exam stud ---
        ("md", _exam_cheatsheet_md),
        ("md", _exam_questions_md),
        ("md", _bridge_md),
    ]


# ---------------------------------------------------------------------------
# Section 0: orientation
# ---------------------------------------------------------------------------

_title_md = """\
# Segment 2.5: Control surfaces, tool enumeration, and the Console asset surface

**Duration:** ~75 minutes if walked end-to-end. Self-study / Q&A overflow, not live-taught in the 4-hour window.
**Maps to:** CCA-F **all five domains** (Domain 1 stop_reason, Domain 2 tool_choice, Domain 3 Console assets, Domain 4 forced extraction, Domain 5 memory).
**References:** [`../domain-1-agentic.md`](../domain-1-agentic.md), [`../domain-2-tools-mcp.md`](../domain-2-tools-mcp.md), [`../domain-3-claude-code.md`](../domain-3-claude-code.md), [`../domain-4-prompts.md`](../domain-4-prompts.md), [`../domain-5-context.md`](../domain-5-context.md).

Segments 1-3 teach the agentic loop, tool design, and structured extraction. This bridge notebook teaches the **control surfaces** underneath those demos: the levers you reach for when a production agent misbehaves. Four levers, one Console asset surface, one cheat sheet, five practice questions.

The notebook also doubles as **CCA-F exam stud**. Every section ends with the API field name, value enumeration, and the production decision rule the exam will probe.
"""

_lo_md = """\
## Learning objectives

By the end of this notebook you will be able to:

- **Distinguish the three tiers tools come from**: Anthropic-hosted server tools (`bash_20250124`, `code_execution_20250522`, etc., registered by `type`), MCP-server tools (discovered via `list_tools` and merged at runtime), and Claude Code harness tools (`Read`/`Edit`/`Bash` - **not** API-reachable). Know which tier to reach for given a production requirement.
- **Run the enumeration discipline** every production agent owes its operators: log what your code registered (static view) AND what the model actually saw per iteration (runtime view)
- Pick the right **`tool_choice`** mode (`auto`, `any`, `tool`, `none`) for a given guarantee, and know when to set **`disable_parallel_tool_use`**
- Branch correctly on every **`stop_reason`** value, force a deterministic cutoff with **`stop_sequences`**, and use **`max_tokens`** as a control lever rather than just a budget
- Address Console-managed assets from the Anthropic SDK: **`memory_stores`** (`oreilly-memory-store`), **`vaults`** (`oreilly-vault`), **`agents`** (Deep Researcher), and **`sessions`** (the runtime that ties them together)
- Answer the five CCA-F practice questions at the end of the notebook without peeking at the rationales
"""

_setup_md = """\
## Setup

This notebook hits the live API across all four control surfaces, including the **Managed Agents** beta (`memory_stores`, `vaults`, `agents`, `sessions`). Budget: roughly **$0.10** for a full top-to-bottom run.

Haiku 4.5 is the course default. We promote to Sonnet 4.6 only when the SDK or Console resource demands it (the Deep Researcher agent is configured as Sonnet in the Console).
"""

_imports_code = """\
from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any

# Load .env from the repo root (gitignored, never committed)
try:
    from dotenv import load_dotenv
    REPO_ROOT_CANDIDATE = Path.cwd().parent if Path.cwd().name == "notebooks" else Path.cwd()
    load_dotenv(REPO_ROOT_CANDIDATE / ".env")
except ImportError:
    pass

from anthropic import Anthropic, BadRequestError

assert os.environ.get("ANTHROPIC_API_KEY"), "ANTHROPIC_API_KEY not set"

REPO_ROOT = Path.cwd().parent if Path.cwd().name == "notebooks" else Path.cwd()
client = Anthropic()

# Haiku 4.5 is the course default. The Managed Agents beta header is required
# for client.beta.{memory_stores, vaults, agents, sessions} surfaces.
MODEL = "claude-haiku-4-5"
MANAGED_AGENTS_BETA = {"anthropic-beta": "managed-agents-2026-04-01"}

print(f"client OK, default model: {MODEL}")
"""


# ---------------------------------------------------------------------------
# Section 1: tool enumeration (four lenses)
# ---------------------------------------------------------------------------

_tier_section_md = """\
## Section 1: Three tiers tools come from (and the boundary that matters)

**The question architects keep asking wrong:** *"can my custom agent use Bash?"*

The answer is yes, no, and yes - depending on which **Bash** you mean. There are **three tiers** tools come from, and they are easy to conflate because two of them are spelled the same:

| Tier | Who hosts | Who invokes | Who executes | Registered via | Example |
|---|---|---|---|---|---|
| **1. Server tools** | Anthropic | Model | Anthropic | `tools=[{"type": "bash_20250124", ...}]` | `bash_20250124`, `code_execution_20250522`, `web_search_20250305`, `text_editor_20250728`, `memory_20250818`, `computer_20250124` |
| **2. MCP-server tools** | You (or a vendor) | Model | The MCP server's process | `list_tools()` -> merge into `tools=[]` | filesystem, GitHub, Stripe, your in-house APIs |
| **3. Harness tools** | The Claude Code CLI itself | The harness | The harness's TypeScript runtime | **not API-reachable** | `Read`, `Edit`, `Grep`, `Glob`, `Write`, `TaskCreate` |

**The teaching beat that catches everyone**: when Claude Code uses `Bash`, that is tier 3 (harness-private TypeScript). When *your* custom agent registers `bash_20250124`, that is tier 1 (Anthropic-hosted server tool). **Same noun, totally different runtimes.** A misbehaving agent is almost always a mismatch between these two **runtimes** - the model called the bash *primitive* but your code is looking for a *harness* response, or vice versa.

The rest of this section teaches each tier with one *why* and one runnable demo (or, for tier 3, the explicit boundary). Then the closing cells show the **enumeration discipline** every production agent should run: log what your code registered AND what the model actually saw, every turn.
"""

_tier1_md = """\
### Tier 1: Anthropic-hosted server tools (the primitives you don't write)

**Why this tier exists:** some capabilities are universal enough that every agent wants them and dangerous enough that you should not implement them yourself. Code execution. Web search. Filesystem editing. Shell. Computer control. Memory. If every customer wrote their own sandbox and their own search, the security and quality variance would be catastrophic. Anthropic hosts the runtime so you do not have to.

**How you recognize them:** the tool definition is keyed by `type` (a versioned identifier like `bash_20250124`) instead of by `name`. The model invokes them just like custom tools, but the *execution* happens server-side. You do not run a client-side tool loop for these; the result lands in the same response.

The two demos below make this concrete. The first uses **`bash_20250124`**: the model receives the tool definition, decides to call it, and your code sees a normal `tool_use` block. You still execute it (Anthropic runs the model's *decision*, not the shell command - that part is yours to sandbox). The second uses **`code_execution_20250522`**: the model writes Python, Anthropic runs it in a sandboxed container, and the *result* comes back inside the same response as a `code_execution_tool_result` block. **No client loop required.** The `stop_reason` is already `end_turn` when your code sees the response.

That second pattern is the load-bearing exam insight: **server tools that fully execute server-side eliminate the agentic loop for the tools Anthropic hosts.** It is the cleanest example of "managed runtime beats hand-rolled runtime" you will see this course.
"""

_tier1_code = '''\
# Most server tools want the computer-use beta header (named for historical
# reasons; covers the whole server-tool family).
SERVER_TOOL_BETA = {"anthropic-beta": "computer-use-2025-01-24"}
server_cli = client.with_options(default_headers=SERVER_TOOL_BETA)

# --- Demo 1: bash_20250124 (model decides; your code still executes) ---
print("=== Demo 1: bash_20250124 (model emits a tool_use; YOU run the shell) ===")
resp = server_cli.messages.create(
    model=MODEL,
    max_tokens=200,
    tools=[{"type": "bash_20250124", "name": "bash"}],
    messages=[{"role": "user", "content": "List the files in /tmp."}],
)
print(f"stop_reason: {resp.stop_reason}")
for block in resp.content:
    btype = getattr(block, "type", "?")
    if btype == "tool_use":
        print(f"  tool_use: name={block.name}  input={dict(block.input)}")
print("Architect note: bash_20250124 is the PRIMITIVE. The model decided to")
print("call it; your code still has to execute the command in a sandbox of")
print("YOUR choosing and feed the result back as a tool_result block.")
print()

# --- Demo 2: code_execution_20250522 (Anthropic runs it; no client loop) ---
print("=== Demo 2: code_execution_20250522 (Anthropic executes; one round-trip) ===")
resp = server_cli.messages.create(
    model=MODEL,
    max_tokens=400,
    tools=[{"type": "code_execution_20250522", "name": "code_execution"}],
    messages=[{
        "role": "user",
        "content": "Compute the standard deviation of [11, 13, 17, 19, 23, 29] using Python.",
    }],
)
print(f"stop_reason: {resp.stop_reason}")
for block in resp.content:
    btype = getattr(block, "type", "?")
    if btype == "server_tool_use":
        print(f"  server_tool_use: name={block.name}")
    elif btype == "code_execution_tool_result":
        # The execution result is INSIDE the same response. No client loop.
        result = getattr(block, "content", None)
        print(f"  code_execution_tool_result: {result!r}"[:200])
    elif btype == "text":
        print(f"  text: {block.text[:120]!r}")
print("Architect note: stop_reason is end_turn on the FIRST response. The")
print("model wrote the code, Anthropic executed it server-side, and the")
print("result landed in the same response. Compare with bash above: that")
print("required your code to loop. The difference is who hosts the runtime.")
'''

_tier2_md = """\
### Tier 2: MCP-server tools (the primitives you write, hosted elsewhere)

**Why this tier exists:** server tools (tier 1) cover the universals - shell, search, code execution. Everything else - your internal APIs, your vendor integrations, your domain-specific tools - is too specific for Anthropic to host. MCP closes that gap by giving you a **standard protocol** for exposing your own tools to any MCP-aware agent (Claude Code, Cursor, custom). You write a server once; every MCP client can discover it.

**How tier 2 differs from tier 1:** the tools are hosted in **your** process (or a vendor's), not Anthropic's. The model still invokes them by emitting a `tool_use` block; your MCP client routes the call to the right server; the server runs the implementation and returns a result. This is also the **tier that scales by configuration, not code**. Add a new MCP server to `.mcp.json` and your agent gains its tools without a source change.

**The discovery primitive** is `list_tools()`. The MCP client calls it against each connected server and merges the schemas into the `tools=[]` array passed to `messages.create()`. The reference implementation in this repo:

- `examples/mcp_cli/mcp_client.py:69-71` - `MCPClient.list_tools()`
- `examples/mcp_cli/core/tools.py:10-23` - `ToolManager.get_all_tools()` (merge-across-servers)

Below we print those excerpts verbatim. **They are short.** The pattern is small because the protocol does the heavy lifting.
"""

_tier2_code = '''\
mcp_client_path = REPO_ROOT / "examples" / "mcp_cli" / "mcp_client.py"
tool_manager_path = REPO_ROOT / "examples" / "mcp_cli" / "core" / "tools.py"

def print_excerpt(path: Path, start: int, end: int, label: str) -> None:
    lines = path.read_text(encoding="utf-8").splitlines()
    print(f"=== {label} ({path.relative_to(REPO_ROOT)}:{start}-{end}) ===")
    for i, line in enumerate(lines[start - 1 : end], start=start):
        print(f"{i:4d}  {line}")
    print()

print_excerpt(mcp_client_path, 60, 78, "MCPClient.list_tools()")
print_excerpt(tool_manager_path, 1, 30, "ToolManager.get_all_tools()")

print("Pattern in plain English:")
print("  1. For each MCP server in .mcp.json, open a client session.")
print("  2. Call client.list_tools() - the server returns its tool schemas.")
print("  3. Merge results into one tools=[...] list, pass to messages.create().")
print("  4. When the model emits tool_use, route by name to the right client.")
print()
print("Architect note: when you add a new tool to an MCP server, EVERY agent")
print("connected to it picks it up on the next list_tools call. No client-side")
print("source change. That is why this tier scales where hand-rolled tools do not.")
'''

_tier3_md = """\
### Tier 3: the Claude Code harness surface (the boundary you cannot cross)

**Why this tier is different:** Claude Code (`claude.ai/code`, the CLI you may be using to *build* this course) is itself an agent. When it executes `Read`, `Edit`, `Grep`, `Glob`, `Write`, `Bash`, `TaskCreate`, those calls **never appear in the `tools=[...]` parameter of a Messages API request you can see.** They are implemented inside the harness process in TypeScript, and the harness only exposes them to *its own* model session.

This is the **boundary architects keep tripping over**: you cannot register Claude Code's `Bash` from your custom agent. What you can register is `bash_20250124` (tier 1), which is a different runtime with a different sandbox model, different streaming semantics, and a different security envelope. They share a name. They share almost nothing else.

| If you want... | Reach for... | Why |
|---|---|---|
| Your custom agent to run shell commands | Tier 1: `bash_20250124` | API-reachable; you implement the sandbox |
| Your custom agent to call your in-house APIs | Tier 2: MCP server | Protocol-standard, hot-pluggable via `.mcp.json` |
| Claude Code to do an arbitrary thing in *its* loop | Tier 3: a **slash command** or **skill** | Discovered via `/help`, `~/.claude/skills/`, `~/.claude/settings.json` |

**You discover tier 3 through the harness, not the API:**

- Inside Claude Code, run `/help` to see slash commands and skills
- Read `~/.claude/settings.json` to see what is registered globally
- Walk `~/.claude/skills/` to see what is invokable
- Check project-scoped `.mcp.json` files for MCP servers Claude Code itself can reach (those are tier 2 from the harness's perspective)

**Exam beat (and the trap that catches working architects):** "What tools does Claude Code expose?" and "what tools can my custom agent use?" are two different questions with two different answers. The API surface is universal; the harness surface is local to the harness. When you build a custom agent, you live in tiers 1 and 2.
"""

_enumeration_md = """\
### The enumeration discipline (regardless of tier)

Now that the three tiers are clear, the operational habit is the same in all of them: **prove what your code registered, and prove what the model actually saw.** Mismatches between those two are where most production bugs hide.

Two views, both mandatory:

1. **Static view at startup**: iterate `tools=[...]` and log every name, schema, and any `cache_control` flag.
2. **Runtime view per iteration**: in the agentic loop, log the *scoped* tool list and the active `tool_choice` after every turn. When a model "forgot" a tool, the log will show the scoped tools list never included it.

The cell below shows both. When you wire this into production, route the lines to your structured-log shipper (the names will match what you grep for in incidents).
"""

_enumeration_code = '''\
# Static view: a small custom tool block, the kind you might pass to a
# real customer-service agent. Pretty-print every name, schema, cache flag.
SAMPLE_TOOLS: list[dict[str, Any]] = [
    {
        "name": "get_weather",
        "description": "Get current temperature and conditions for a US city. Returns JSON.",
        "input_schema": {
            "type": "object",
            "properties": {
                "city": {"type": "string", "description": "City name, e.g. 'Nashville'"},
                "units": {"type": "string", "enum": ["F", "C"], "default": "F"},
            },
            "required": ["city"],
        },
    },
    {
        "name": "lookup_order",
        "description": "Look up an order by ID. Returns the order record or null.",
        "input_schema": {
            "type": "object",
            "properties": {"order_id": {"type": "string"}},
            "required": ["order_id"],
        },
    },
]

def describe_tools(tools: list[dict[str, Any]]) -> None:
    """Static enumeration: what your code registered (run at startup)."""
    print(f"{len(tools)} tools registered:")
    for t in tools:
        props = list(t["input_schema"].get("properties", {}).keys())
        required = t["input_schema"].get("required", [])
        cached = "cache_control" in t
        print(f"  - {t['name']}({', '.join(props)})  required={required}  cached={cached}")
        print(f"      {t['description'][:80]}")

def trace_iteration(iteration: int, scoped_tools: list[dict[str, Any]], tool_choice: dict[str, Any], stop_reason: str | None) -> None:
    """Runtime enumeration: what the model SAW at iteration N (log every turn)."""
    names = [t["name"] for t in scoped_tools]
    print(f"[iter {iteration:02d}] tools={names}  tool_choice={tool_choice}  stop_reason={stop_reason}")

print("--- Static view (run at startup) ---")
describe_tools(SAMPLE_TOOLS)
print()
print("--- Runtime view (log every iteration of the agentic loop) ---")
# Simulate three iterations of a coordinator that scopes down after routing
trace_iteration(0, SAMPLE_TOOLS, {"type": "auto"}, stop_reason=None)
trace_iteration(1, [SAMPLE_TOOLS[0]], {"type": "any"}, stop_reason="tool_use")
trace_iteration(2, [], {"type": "none"}, stop_reason="end_turn")
print()
print("Architect note: when a model 'forgot' a tool, the runtime log shows")
print("the scoped tools list never included it. When a model called the WRONG")
print("tool, the static log shows the description was the contract that")
print("invited the wrong call. Two logs, two failure modes, both indispensable.")
'''


# ---------------------------------------------------------------------------
# Section 2: tool_choice depth
# ---------------------------------------------------------------------------

_tc_section_md = """\
## Section 2: `tool_choice` depth

Four modes. Each one is a guarantee about what the model is *required* to do:

| Mode | Guarantee | Use when |
|------|-----------|----------|
| `{"type": "auto"}` | Model decides; may answer in prose | Default; the model picks tools or text |
| `{"type": "any"}` | Model **must** call some tool, model picks which | You know action is required, model picks the verb |
| `{"type": "tool", "name": "X"}` | Model **must** call tool X | Forced structured output; the Domain 4 cheat code |
| `{"type": "none"}` | Tools registered, but model **cannot** call them | "Explain, don't act" turns |

Add **`disable_parallel_tool_use: true`** when ordering matters - the model emits one tool call per turn instead of a parallel batch.

The next four cells exercise each mode against the live API and print the `stop_reason` flip.
"""

_tc_auto_vs_any_md = """\
### `auto` vs `any` (live A/B)

Same prompt, same tools, two `tool_choice` values. With `auto` the model may answer in prose if it thinks no tool is needed. With `any` it **must** call one - `stop_reason` will be `tool_use`, guaranteed.
"""

_tc_auto_vs_any_code = '''\
WEATHER_TOOL = SAMPLE_TOOLS[0]
# Deliberately ambiguous: the prompt asks a question the model could answer
# from training data ("what tools should I think about?") without needing the
# weather tool. With auto, the model should reason in prose. With any, it is
# forced to call something - it will call get_weather even though the prompt
# never named a city, because any leaves it no choice.
PROMPT = "I'm building a travel app. What kinds of weather data are useful to surface to users?"

def run(label: str, tool_choice: dict[str, Any]) -> None:
    resp = client.messages.create(
        model=MODEL,
        max_tokens=800,
        tools=[WEATHER_TOOL],
        tool_choice=tool_choice,
        messages=[{"role": "user", "content": PROMPT}],
    )
    block_types = [getattr(b, "type", "?") for b in resp.content]
    print(f"[{label:>5}] stop_reason={resp.stop_reason}  blocks={block_types}")

run("auto", {"type": "auto"})
run("any",  {"type": "any"})

print()
print("auto: model may answer in prose if it judges no tool is needed.")
print("      Expected stop_reason=end_turn with a text block.")
print("any:  model is forced to call a tool. stop_reason is always tool_use,")
print("      even when no city was specified - the model will pick or invent one.")
'''

_tc_forced_md = """\
### Forced `tool` mode (the structured-output cheat code)

This is **the** Domain 4 trick. Define a schema as a tool. Force the model to call that tool. The `tool_use.input` block is now schema-guaranteed - no JSON parsing, no `"```json"` fence, no validation rituals. The SDK validated the schema for you.

Segment 3 uses this pattern for invoice extraction. We strip it down to its skeleton here.
"""

_tc_forced_code = '''\
EXTRACT_TOOL = {
    "name": "extract_sentiment",
    "description": "Extract sentiment from text.",
    "input_schema": {
        "type": "object",
        "properties": {
            "sentiment": {"type": "string", "enum": ["positive", "neutral", "negative"]},
            "confidence": {"type": "number", "minimum": 0, "maximum": 1},
            "key_phrases": {"type": "array", "items": {"type": "string"}, "maxItems": 5},
        },
        "required": ["sentiment", "confidence"],
    },
}

resp = client.messages.create(
    model=MODEL,
    max_tokens=512,
    tools=[EXTRACT_TOOL],
    tool_choice={"type": "tool", "name": "extract_sentiment"},
    messages=[{
        "role": "user",
        "content": "The new policy is fine I guess but the rollout has been a disaster.",
    }],
)

print(f"stop_reason: {resp.stop_reason}")
for block in resp.content:
    if getattr(block, "type", None) == "tool_use":
        # block.input is a dict that ALREADY conforms to the schema above.
        print(f"extracted: {json.dumps(block.input, indent=2)}")
'''

_tc_none_md = """\
### `none` mode (tools registered, but the model cannot call them)

Useful for explanation turns inside a multi-step pipeline. The model sees the tool surface (so it can describe options), but cannot act. **Trying to "ask the model what tools it has" without `tool_choice: none` will sometimes trigger a tool call** - we want narration, not action.
"""

_tc_none_code = '''\
resp = client.messages.create(
    model=MODEL,
    max_tokens=600,
    tools=SAMPLE_TOOLS,
    tool_choice={"type": "none"},
    messages=[{
        "role": "user",
        "content": "Briefly: what tools do you have, and when would you use each? Two sentences per tool, no more.",
    }],
)

print(f"stop_reason: {resp.stop_reason}")
for block in resp.content:
    if getattr(block, "type", None) == "text":
        print(block.text[:600])

print()
print("Expected stop_reason=end_turn (NOT tool_use, NOT max_tokens). The model")
print("described the tools rather than calling them - that is what tool_choice")
print("type=none guarantees, regardless of how the prompt is phrased.")
'''

_tc_disable_parallel_md = """\
### `disable_parallel_tool_use` (when ordering matters)

By default, Claude may emit multiple tool_use blocks in one turn that you are expected to execute **in parallel**. That breaks down when one tool's output is the next tool's input - write-then-read, lookup-then-act, fetch-then-summarize.

Set `disable_parallel_tool_use: true` on `tool_choice` and the model emits one tool call per turn. You execute, return the result, the model emits the next.

**Exam beat:** the flag lives on the `tool_choice` object, not as a top-level parameter.
"""

_tc_disable_parallel_code = '''\
# Two tools, two clearly independent requests in one user turn.
# Without the flag, the model is free to emit both tool_use blocks in
# parallel. With the flag, it must emit them one per turn.
PARALLEL_TOOLS = [
    SAMPLE_TOOLS[0],  # get_weather
    SAMPLE_TOOLS[1],  # lookup_order
]
PROMPT = (
    "In a single response, do BOTH of these for me: "
    "(1) get the weather in Nashville, "
    "(2) look up order O-9001. "
    "I need both answers."
)

def call(tool_choice: dict[str, Any]) -> None:
    resp = client.messages.create(
        model=MODEL,
        max_tokens=512,
        tools=PARALLEL_TOOLS,
        tool_choice=tool_choice,
        messages=[{"role": "user", "content": PROMPT}],
    )
    tool_uses = [b for b in resp.content if getattr(b, "type", None) == "tool_use"]
    print(f"  tool_choice={tool_choice}")
    print(f"  stop_reason={resp.stop_reason}  tool_use_blocks={len(tool_uses)}")
    for tu in tool_uses:
        print(f"    -> {tu.name}({list(tu.input.keys())})")

print("Without the flag (parallel allowed - expect 2 tool_use blocks in one turn):")
call({"type": "any"})
print()
print("With disable_parallel_tool_use=True (expect 1 tool_use block per turn):")
call({"type": "any", "disable_parallel_tool_use": True})

print()
print("When ordering matters - write-then-read, lookup-then-act - set the flag.")
print("Note: real-world parallelism is the model's call. The flag is the cap,")
print("not the floor. If the model judges sequential is right, you get sequential.")
'''


# ---------------------------------------------------------------------------
# Section 3: stop conditions
# ---------------------------------------------------------------------------

_stop_section_md = """\
## Section 3: Stop conditions

Domain 1's hard rule: **never parse natural language to decide if the model is done. Always branch on `stop_reason`.**

The six values, what each one means, and what to do next:

| `stop_reason` | What happened | Next action |
|---|---|---|
| `end_turn` | Model finished cleanly | Return the response to the user |
| `max_tokens` | You ran out of output budget | Resume by feeding the partial turn back in, or surface as truncation |
| `stop_sequence` | A token from `stop_sequences` matched | Use the matched `stop_sequence` to dispatch |
| `tool_use` | Model emitted at least one `tool_use` block | Execute the tools, append `tool_result`, loop |
| `pause_turn` | Long-running task paused itself | Send the assistant message back unchanged to resume |
| `refusal` | Streaming policy intervention | Surface to the user; not an error to retry blindly |

The next three demos exercise the three values most learners have never *triggered* themselves: `stop_sequence`, `max_tokens`, and (in the closing paragraph) `pause_turn`.
"""

_stop_reason_tree_md = """\
### The branch-on-`stop_reason` decision tree

```
resp = client.messages.create(...)

match resp.stop_reason:
    case "end_turn":     return  # done
    case "tool_use":     execute_tools_and_loop(resp)
    case "max_tokens":   resume_or_surface_truncation(resp)
    case "stop_sequence": dispatch_on(resp.stop_sequence)
    case "pause_turn":   resend_and_continue(resp)
    case "refusal":      surface_to_user(resp)
```

Production agents have **exactly one** dispatcher that knows this match. Every other code path goes through it.
"""

_stop_sequences_md = """\
### `stop_sequences` (deterministic cutoff)

Pass an array of strings. When the model would emit any of them, generation stops and `stop_reason="stop_sequence"`. The matched token comes back in `resp.stop_sequence`. The string itself is **not** included in the output.

Use case: **structured cutoff in streaming pipelines**. Generate a report, stop at `END_REPORT`, then start a new generation for the next section. No prompt fragility, no "and then nothing else please".
"""

_stop_sequences_code = '''\
resp = client.messages.create(
    model=MODEL,
    max_tokens=512,
    stop_sequences=["END_REPORT", "## Section"],
    messages=[{
        "role": "user",
        "content": (
            "Write a two-sentence status report on the Q2 launch. "
            "End with the literal token END_REPORT on its own line."
        ),
    }],
)

print(f"stop_reason: {resp.stop_reason}")
print(f"stop_sequence: {resp.stop_sequence!r}")
print(f"text:\\n{resp.content[0].text}")

print()
print("Note: the matched stop_sequence token is NOT included in the output.")
print("That is the whole point: the boundary is metadata, not text to strip.")
'''

_max_tokens_md = """\
### `max_tokens` as a control lever (not just a budget)

Most learners treat `max_tokens` as "max bill". It is also a **deliberate cutoff** - set it low to force a `stop_reason="max_tokens"`, then **resume by feeding the partial assistant turn back in** as the next message and asking the model to continue.

Use cases: agentic chunking, summary-then-detail pipelines, watchdog timeouts on runaway generation.
"""

_max_tokens_code = '''\
PROMPT = "List 50 distinct examples of color names. Number each one."

# Pass 1: deliberately cut off
resp1 = client.messages.create(
    model=MODEL,
    max_tokens=80,  # too small on purpose
    messages=[{"role": "user", "content": PROMPT}],
)
print(f"Pass 1 stop_reason: {resp1.stop_reason}")
partial = resp1.content[0].text
print(f"Pass 1 text (truncated):\\n{partial}\\n")

# Pass 2: resume by replaying the partial assistant turn
resp2 = client.messages.create(
    model=MODEL,
    max_tokens=600,
    messages=[
        {"role": "user", "content": PROMPT},
        {"role": "assistant", "content": partial},  # feed the partial back in
        {"role": "user", "content": "continue the list from where you stopped"},
    ],
)
print(f"Pass 2 stop_reason: {resp2.stop_reason}")
print(f"Pass 2 text (continuation):\\n{resp2.content[0].text[:400]}")

print()
print("Pattern: max_tokens forces a deliberate cutoff. The resumption is just")
print("a normal Messages call where the partial assistant turn is re-sent.")
'''

_pause_refusal_md = """\
### `pause_turn` and `refusal` (the two you won't trigger on purpose)

**`pause_turn`** fires on long-running agent tasks (typically with server tools like web search or computer use) when the model decides it needs a break. The fix is mechanical: pass the assistant message back **unchanged** in a follow-up `messages.create()` call. The model picks up where it left off. Domain 5 explicitly calls this out: *"a `pause_turn` stop reason is the model telling you it needs a break."*

**`refusal`** is a streaming-time policy intervention - the model declines to continue. It is not an error to retry blindly. Surface the situation, log it, and decide product-side whether to rephrase or escalate.

Both are rare enough that a deliberate live demo is unreliable in a teaching window. The point is to **have the branch in your dispatcher** so they never crash you in production.
"""


# ---------------------------------------------------------------------------
# Section 4: Managed Agents in Claude Console (live SDK surface)
# ---------------------------------------------------------------------------

_console_section_md = """\
## Section 4: Claude Console assets are first-class SDK resources

Claude Console is not a UI on top of Anthropic. It is a managed-agents control plane with a **full SDK surface**. The same key that authenticates `messages.create()` also authenticates `client.beta.memory_stores`, `client.beta.vaults`, `client.beta.agents`, and `client.beta.sessions`. Discovered live during course prep:

| Console asset | SDK resource | Sub-resources |
|---|---|---|
| Memory stores | `client.beta.memory_stores` | `.memories`, `.memory_versions` |
| Vaults | `client.beta.vaults` | `.credentials` (incl. `mcp_oauth_validate`) |
| Agents | `client.beta.agents` | `.versions` |
| Sessions (runtime) | `client.beta.sessions` | `.events`, `.threads`, `.resources` |
| Environments | `client.beta.environments` | `.work` |
| Skills | `client.beta.skills` | `.versions` |
| Files | `client.beta.files` | upload/download |

All of these require the beta header `anthropic-beta: managed-agents-2026-04-01`. We set it once at the top of the notebook.

**This section runs against Tim's Default workspace assets**: `oreilly-memory-store`, `oreilly-vault`, and the Deep Researcher template agent. If you are running this on your own account, the `list()` calls will return your assets instead. The pattern is identical.
"""

_console_memstore_md = """\
### `oreilly-memory-store` (Domain 5: context that survives restarts)

A **memory store** is a Console-managed, server-side persistence layer for an agent's memories. Different from the **Memory tool** (`memory_20250818`), which is client-side and you implement the filesystem yourself.

Memory store advantages:

- Survives kernel restarts, machine reboots, and credential rotations
- Scoped to your workspace, not to a local directory
- Has its own SDK surface: list, retrieve, create, version, archive
- Shared across sessions when you mount it via `sessions.resources`
"""

_console_memstore_code = '''\
cli = client.with_options(default_headers=MANAGED_AGENTS_BETA)

# 1. List all memory stores in the workspace, find ours by name
print("Memory stores in this workspace:")
stores = cli.beta.memory_stores.list()
for s in stores.data:
    marker = " <-- oreilly-memory-store" if s.name == "oreilly-memory-store" else ""
    print(f"  id={s.id}  name={s.name!r}{marker}")

# 2. Retrieve metadata for ours
ours = next((s for s in stores.data if s.name == "oreilly-memory-store"), None)
if ours is None:
    print("\\n(no oreilly-memory-store in this workspace; create one in the Console)")
else:
    detail = cli.beta.memory_stores.retrieve(ours.id)
    print(f"\\nMetadata:")
    print(f"  id:          {detail.id}")
    print(f"  name:        {detail.name}")
    print(f"  description: {detail.description}")
    print(f"  created_at:  {detail.created_at}")

    # 3. Memories inside the store are addressable too
    memories_methods = [m for m in dir(cli.beta.memory_stores.memories) if not m.startswith("_")]
    print(f"\\n  memories sub-resource methods: {memories_methods}")
'''

_console_vault_md = """\
### `oreilly-vault` (Domain 3: secrets out of source, even in notebooks)

A **vault** stores credentials your agent uses to talk to third-party services - GitHub tokens, OpenAPI keys, MCP server OAuth tokens. Two SDK surfaces:

- `client.beta.vaults` - manage the vault itself (create, list, archive)
- `client.beta.vaults.credentials` - manage credentials inside it (create, retrieve, **`mcp_oauth_validate`** for MCP OAuth flows)

**Production pattern:** mount vaults into a session via `sessions.create(vault_ids=[...])`. The agent's tools resolve credential references at call time. The credential values **never appear in your notebook**.
"""

_console_vault_code = '''\
cli = client.with_options(default_headers=MANAGED_AGENTS_BETA)

print("Vaults in this workspace:")
vaults = cli.beta.vaults.list()
for v in vaults.data:
    print(f"  id={v.id}  display_name={v.display_name!r}")

# Find oreilly-vault by display_name
ours = next((v for v in vaults.data if v.display_name == "oreilly-vault"), None)
if ours is None:
    print("\\n(no oreilly-vault in this workspace; create one in the Console)")
else:
    detail = cli.beta.vaults.retrieve(ours.id)
    print(f"\\nVault metadata:")
    print(f"  id:           {detail.id}")
    print(f"  display_name: {detail.display_name}")

    # List credentials in the vault (values are never returned, only refs)
    creds = cli.beta.vaults.credentials.list(vault_id=ours.id)
    print(f"\\nCredentials in this vault: {len(list(creds.data))}")
    for c in creds.data:
        print(f"  {c.model_dump() if hasattr(c, 'model_dump') else c}")

print()
print("Teaching beat: credential VALUES never come back over the wire.")
print("The vault returns refs; sessions resolve them at agent-call time.")
'''

_console_agent_md = """\
### Deep Researcher agent (Domain 1: agents you don't have to write the loop for)

Segment 1 built an agentic loop **from scratch** - your code orchestrates messages, tool calls, and stop_reason branching. The Managed Agents surface is the alternative: **define the agent in the Console, invoke it via the SDK, let Anthropic run the loop**.

The Deep Researcher template agent in Tim's Default workspace:

- Model: `claude-sonnet-4-6` (configured in the Console; the API respects it)
- Tools: `agent_toolset_20260401` with `always_allow` permission
- System prompt: opinionated research workflow (decompose, search, read in full, synthesize with citations, note gaps)

You invoke it by creating a **session** that references the agent, an environment, and (optionally) vaults. The session is the runtime; the agent is the recipe.
"""

_console_agent_code = '''\
cli = client.with_options(default_headers=MANAGED_AGENTS_BETA)

# 1. Find the Deep Researcher agent by name
print("Agents in this workspace:")
agents = cli.beta.agents.list()
for a in agents.data:
    marker = " <-- target" if a.name == "Deep researcher" else ""
    print(f"  id={a.id}  name={a.name!r}{marker}")

deep = next((a for a in agents.data if a.name == "Deep researcher"), None)
if deep is None:
    print("\\n(no Deep researcher agent in this workspace)")
else:
    # 2. Retrieve the full agent config
    detail = cli.beta.agents.retrieve(deep.id)
    print(f"\\nDeep Researcher config:")
    print(f"  id:          {detail.id}")
    print(f"  model:       {detail.model.id}  (speed: {detail.model.speed})")
    print(f"  description: {detail.description}")
    print(f"  tools:       {[t.get('type') if isinstance(t, dict) else getattr(t, 'type', '?') for t in detail.tools]}")
    print(f"  template:    {detail.metadata.get('template')}")
    print()
    print(f"  system prompt (first 200 chars):")
    print(f"    {detail.system[:200]}...")
    print()
    print("To invoke: client.beta.sessions.create(agent=deep.id, environment_id=...)")
    print("Sessions are the runtime; agents are the recipe. We don't burn tokens")
    print("on a full research run here - see the Console for a chat UI.")
'''

_console_tieback_md = """\
### CCA-F domain tie-back

| Console asset | CCA-F domain | What the exam will probe |
|---|---|---|
| `memory_stores` | **Domain 5** (Context Management) | Persistence that survives restarts; difference from the client-side Memory tool |
| `vaults` + `vaults.credentials` | **Domain 3** (Claude Code) | Secrets hygiene; values never leave Anthropic; `mcp_oauth_validate` for MCP OAuth |
| `agents` + `sessions` | **Domain 1** (Agentic Architecture) | Managed loop vs. hand-rolled loop; when to pick which |
| `environments` | **Domain 3** (Claude Code) | Container config for agent execution |
| `skills` | **Domain 3** (Claude Code) | Reusable agent capabilities |

**Production rule of thumb:** if your agent has any of (long-lived memory, third-party credentials, multi-step research, multi-tenant scope), reach for Managed Agents before you write a loop. If it has none of those, the Segment 1 hand-rolled loop is fine.
"""


# ---------------------------------------------------------------------------
# Section 5: CCA-F exam stud
# ---------------------------------------------------------------------------

_exam_cheatsheet_md = """\
## Section 5: CCA-F exam stud

### One-page cheat sheet

**`tool_choice` modes** (Domain 2):

| Mode | Forces what? | When to pick |
|---|---|---|
| `{"type": "auto"}` | nothing | default |
| `{"type": "any"}` | a tool call (model picks which) | action required, model picks verb |
| `{"type": "tool", "name": "X"}` | call to tool X | forced structured output |
| `{"type": "none"}` | no tool calls | "explain, don't act" |
| add `disable_parallel_tool_use: true` | one tool per turn | ordering matters |

**`stop_reason` values** (Domain 1, **never parse prose to decide**):

- `end_turn` - done; return to user
- `tool_use` - execute tools, append `tool_result`, loop
- `max_tokens` - resume by replaying the partial assistant turn
- `stop_sequence` - dispatch on `resp.stop_sequence`
- `pause_turn` - resend assistant message unchanged to continue
- `refusal` - streaming policy intervention; surface, don't blind-retry

**Tool enumeration lenses**:

1. Static - print `tools=[...]`
2. Runtime loop - log scoped tools + `tool_choice` per iteration
3. MCP - `client.list_tools()` against each server, merge
4. Harness (Claude Code) - separate surface, not API-introspectable

**Console assets via SDK** (require `anthropic-beta: managed-agents-2026-04-01`):

- `client.beta.memory_stores` - persistence (Domain 5)
- `client.beta.vaults` (+ `.credentials`) - secrets (Domain 3)
- `client.beta.agents` + `client.beta.sessions` - managed loop (Domain 1)
"""

_exam_questions_md = """\
### Five practice questions

Answer first. Rationale is below each question. These are distinct from the 60 in the capstone deck.

---

**Q1** (Domain 2). You need an agent that *must* call a specific extraction tool and return data that conforms to its schema. Which `tool_choice` value do you set?

- A. `{"type": "auto"}`
- B. `{"type": "any"}`
- C. `{"type": "tool", "name": "extract"}`
- D. `{"type": "none"}`

<details><summary>Answer</summary>

**C**. `auto` lets the model answer in prose; `any` forces *some* tool but not the specific one; `none` forbids tool calls. Only `{"type": "tool", "name": "X"}` guarantees the call lands on the schema-bearing tool.
</details>

---

**Q2** (Domain 1). Your agent's response has `stop_reason = "max_tokens"`. The user expected a complete answer. What is the correct production behavior?

- A. Raise an error - the model failed
- B. Strip the partial output and retry with a fresh prompt
- C. Replay the partial assistant turn as a new `messages.create()` and ask the model to continue
- D. Parse the partial output for completion markers and decide based on text

<details><summary>Answer</summary>

**C**. `max_tokens` is a budget cap, not a failure. You append the partial assistant turn to the conversation and request a continuation. (A) is wrong because the model did exactly what you asked. (B) discards work. (D) violates the "never parse prose to decide control flow" rule.
</details>

---

**Q3** (Domain 2). You want the model to call two tools, but the second one **must** see the first's output. What do you set?

- A. `tool_choice = {"type": "any"}` only
- B. `tool_choice = {"type": "auto", "disable_parallel_tool_use": true}`
- C. `stop_sequences = ["TOOL_DONE"]`
- D. Send two separate requests, one per tool

<details><summary>Answer</summary>

**B**. By default Claude may emit both tool calls in one turn as a parallel batch. `disable_parallel_tool_use` forces one-per-turn so you can return the first tool's `tool_result` before the second call is decided. (C) doesn't sequence tools. (D) works but is unnecessary plumbing the SDK can do for you.
</details>

---

**Q4** (Domain 5). You want agent memory that survives kernel restarts, container rebuilds, and credential rotations. Which surface do you use?

- A. The client-side Memory tool (`memory_20250818`) with a local filesystem handler
- B. `client.beta.memory_stores` in the Console
- C. A `system` prompt containing the memory text
- D. `stop_sequences` to mark memory boundaries

<details><summary>Answer</summary>

**B**. The Memory tool (A) is **client-side** - persistence is your responsibility, and local files do not survive container rebuilds. `memory_stores` (B) is server-managed in Anthropic's Console and survives restarts. (C) is not persistence, it is per-request context. (D) is a generation control, not memory.
</details>

---

**Q5** (Domain 2 + 3). An agent connects to three MCP servers via `.mcp.json`. New tools are added to one server. How does the agent learn about them without a code change?

- A. The Anthropic API auto-discovers all MCP tools
- B. The client calls `list_tools` against each MCP server at startup and merges results into the `tools=[...]` array
- C. The agent reads the server's source code via `claude -p`
- D. The model is trained on the server's tool schemas

<details><summary>Answer</summary>

**B**. MCP tools are **server-exposed, runtime-discovered**. The MCP client calls `list_tools` against each connected server; whatever the server returns is what the agent can call. (A) is wrong - the Messages API does not introspect MCP servers for you. (C) confuses Claude Code's headless mode with MCP discovery. (D) confuses training data with runtime tool registration.
</details>
"""

_bridge_md = """\
## Bridge: where to next

You have now seen every control surface the four teaching segments use, plus the Managed Agents surface most of the Console runs on. The pieces:

- **Segment 1** built the loop you can now introspect with lens 2
- **Segment 2** uses `tool_choice` for scoping and structured errors
- **Segment 3** uses forced `tool_choice` + Pydantic validation for invoice extraction
- **This notebook** is the reference card under all three, plus the Console asset surface

For the capstone (Segment 4) and the CCA-F itself, the load-bearing facts are the **two enumerations** in the cheat sheet: every `stop_reason` value and every `tool_choice` mode. If you can recite both from memory along with the production decision rule for each, you are ready.

**Bridge to Segment 3:** the forced `tool_choice = {"type": "tool", "name": "extract_invoice"}` pattern you just learned is the engine of the invoice extractor. Open `segment-3-invoice-extractor.ipynb` and watch it run against nested schemas with validation retries.
"""
