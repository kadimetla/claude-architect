"""Cell builder for segment-1-customer-support-agent.ipynb.

Teaching-first notebook for Segment 1: Building AI Agents That Use Tools.
Maps to CCA-F Domain 1 (27% exam weight).

Pedagogical arc (reordered 2026-05-19):
  Warm-up (first Claude call) ->
  Loop concept -> Tools + DB ->
  Loop runs (Scenario A, no hook) ->
  Motivate hooks -> Hook code -> Loop with hook ->
  Scenario B + stress test ->
  Coordinator-subagent concept -> live bare-API demo -> debrief ->
  Exercise -> Bridge -> Appendix.

The hook now lands AFTER the learner has seen the loop transition
stop_reason live. It is taught as a BACKSTOP, not the centerpiece.
"""

from __future__ import annotations


def cells() -> list[tuple[str, str]]:
    return [
        ("md", _title_md),
        ("md", _lo_md),
        # Warm-up: first Claude call (Haiku 4.5, no tools)
        ("md", _warm_up_md),
        ("code", _warm_up_code),
        # The agentic loop concept (before any code runs)
        ("md", _concept_loop_md),
        ("md", _concept_stop_reason_md),
        # Demo setup
        ("md", _demo_setup_md),
        ("code", _imports_code),
        ("md", _demo_tools_md),
        ("code", _tools_code),
        ("md", _demo_tool_enum_md),
        ("code", _tool_enum_code),
        ("md", _demo_synthetic_db_md),
        ("code", _synthetic_db_code),
        # The rung between "one bare call" and "the full loop": ONE tool call,
        # no loop, so the learner SEES a raw tool_use block and the stop_reason
        # flip before meeting the dispatcher. Feynman order - the primitive is
        # visible before it gets automated.
        ("md", _one_tool_call_md),
        ("code", _one_tool_call_code),
        # Loop runs FIRST, without hooks, so the learner sees it work
        ("md", _demo_loop_md),
        ("code", _loop_code),
        ("md", _demo_scenario_a_md),
        ("code", _scenario_a_code),
        # NOW motivate hooks. The loop is real. Make it safe.
        ("md", _motivate_hooks_md),
        ("md", _concept_hooks_md),
        ("md", _demo_hook_md),
        ("code", _hook_code),
        ("md", _loop_with_hook_md),
        ("code", _loop_with_hook_code),
        ("md", _demo_scenario_b_md),
        ("code", _scenario_b_code),
        ("md", _hook_stress_test_md),
        ("code", _hook_stress_test_code),
        # Session vocabulary (resume vs fork) - paragraph only, no demo
        ("md", _session_vocab_md),
        # Coordinator-subagent, built in three runnable beats rather than one
        # 191-line wall: (1) the tool + role table, (2) ONE parameterized runner
        # that both roles share, (3) the coordinator plus the isolation proof.
        # The split is the pedagogy - each cell runs and prints on its own.
        ("md", _concept_subagents_md),
        ("md", _subagent_demo_md),
        ("code", _subagent_setup_code),
        ("md", _subagent_runner_md),
        ("code", _subagent_runner_code),
        ("md", _coordinator_md),
        ("code", _coordinator_code),
        ("md", _subagent_debrief_md),
        ("md", _exercise_md),
        ("md", _key_takeaways_md),
        ("md", _bridge_md),
        ("md", _appendix_md),
    ]


_title_md = """\
# Segment 1: Building AI Agents That Use Tools

**Duration:** 50 minutes
**Maps to:** CCA-F Domain 1 (Agentic Architecture, 27% exam weight)
**Reference:** [`../docs/domain-1-agentic.md`](../docs/domain-1-agentic.md)

We're building a **customer support agent** that decides which tools to call and when to escalate. The model will *want* to break a refund policy, and a **PreToolUse hook** says no. **The guarantee comes from your code, not from begging the prompt.**

**Arc:** first call -> the agentic loop -> Scenario A -> the hook as a **backstop** -> Scenario B.
"""

_lo_md = """\
## Learning objectives

By the end of this segment you will be able to:

- Make a **basic Claude API call** and branch on `stop_reason`
- Explain the **agentic loop** and which `stop_reason` drives each branch
- Place **hooks** at the right lifecycle events (**PreToolUse**, **PostToolUse**)
- Distinguish **prompt-layer guidance** from **application-layer enforcement**
- Recognize **session resume vs fork**, and build a **coordinator-subagent** topology when subtask isolation pays off
"""

_warm_up_md = """\
## Warm-up: your first Claude call

One bare call. Pick a model, send a user message, read **`stop_reason`**. Everything else in this course is layers on this primitive.

**Prerequisites:** an `ANTHROPIC_API_KEY` and the `anthropic` SDK. If Segment 0 passed, you're set.

**Why Haiku 4.5?** It runs the agentic loop at production quality for roughly a fifth of the Sonnet cost. **Pick the smallest model that does the job** is itself a Domain 1 skill.
"""

_warm_up_code = """\
import os
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv(Path.cwd().parent / ".env")
except ImportError:
    pass

assert os.environ.get("ANTHROPIC_API_KEY"), (
    "ANTHROPIC_API_KEY is not set. Export it in your shell or add it to "
    "a .env file at the repo root. See notebooks/README.md."
)

from anthropic import Anthropic

client = Anthropic()

resp = client.messages.create(
    model="claude-haiku-4-5",
    max_tokens=128,
    messages=[
        {"role": "user", "content": "In one sentence, what is an agentic loop?"},
    ],
)

# Branch on stop_reason, never on the prose. This is THE pattern.
assert resp.stop_reason == "end_turn", f"unexpected stop_reason: {resp.stop_reason}"
print(f"stop_reason: {resp.stop_reason}")
print(f"model said:  {resp.content[0].text}")
"""

_concept_loop_md = """\
## The agentic loop in one breath

The control structure that turns a call into an **agent** is small. The model emits content plus a **`stop_reason`**, and your code branches on it:

- `end_turn` -> return to the user
- `tool_use` -> execute the tools, append `tool_result`, send the conversation back
- `max_tokens` -> output may be truncated; decide whether to continue
- `stop_sequence` -> a custom stop sequence fired
- `pause_turn` -> a long-running turn was paused; resume it
- `refusal` -> the streaming classifier intervened on policy

**Branch on the enum, never on the prose.**
"""

_concept_stop_reason_md = """\
## The `stop_reason` decision tree

```
                  +-----------+
                  | API call  |
                  +-----+-----+
                        |
                        v
                +---------------+
                |  stop_reason  |
                +---+---+---+---+
                    |   |   |
        +-----------+   |   +-------------+
        |               |                 |
        v               v                 v
   end_turn        tool_use         max_tokens / pause_turn / refusal
   (return to     (execute,         (decide: continue, escalate,
    user)          append result,    or surface to caller)
                   loop)
```

**The agent isn't the model. The agent is the loop around the model.**
"""

_demo_setup_md = """\
## Demo: customer support agent

Four moves:

1. **Tools** - four definitions whose `description` carries the contract
2. **Synthetic DB** - Python dicts, so tool execution is deterministic and cheap
3. **The loop** - branches on `stop_reason`, dispatches tools, surfaces escalations
4. **The hook** - added LAST, as a **backstop**, after the loop is real

Two scenarios: a benign happy path (no hook), then a $750 refund against a $500 cap.
"""

_imports_code = """\
# client and Anthropic are already imported from the warm-up cell.
# Haiku 4.5 is the default for this course - it handles tool-using orchestration
# at production quality for roughly a fifth of the Sonnet cost. We promote to
# Sonnet 4.6 only where reasoning depth is demonstrably needed (Segment 3).
import json
from typing import Any

MODEL = "claude-haiku-4-5"
"""

_demo_tools_md = """\
## Step 1: tool definitions

Four tools. Notice the **`description`** field on `process_refund` - it spells out the $500 cap, the inputs, and what happens above the cap. **Names lie. Descriptions don't.** The description is the contract between you and the model.
"""

_tools_code = """\
TOOLS: list[dict[str, Any]] = [
    {
        "name": "get_customer",
        "description": (
            "Look up a customer by their account ID. Returns the customer "
            "record with name, email, account status, and lifetime value. "
            "Call this FIRST before any other tool when the user references "
            "an account. Do not guess customer identity."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "customer_id": {"type": "string", "description": "Account ID, e.g. C-1024"},
            },
            "required": ["customer_id"],
        },
    },
    {
        "name": "lookup_order",
        "description": (
            "Look up an order by its order number. Returns line items, "
            "order total, fulfillment status, and the linked customer ID. "
            "Call after get_customer when investigating a specific purchase."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "order_id": {"type": "string", "description": "Order number, e.g. 4470"},
            },
            "required": ["order_id"],
        },
    },
    {
        "name": "process_refund",
        "description": (
            "Issue a refund for an order. The agent is authorized to refund up "
            "to USD 500 per order. Refunds above USD 500 MUST go through "
            "escalate_to_human; the agent's refund authority stops at 500. "
            "Always call lookup_order first so the amount is grounded in the "
            "real order total, not the customer's claimed amount."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "order_id": {"type": "string"},
                "amount_usd": {"type": "number", "description": "Refund amount in USD"},
                "reason": {"type": "string", "description": "Short reason code"},
            },
            "required": ["order_id", "amount_usd", "reason"],
        },
    },
    {
        "name": "escalate_to_human",
        "description": (
            "Hand the case to a human reviewer. Pass a STRUCTURED SUMMARY: "
            "who, what, what has been tried, what is blocked. Do NOT pass the "
            "raw transcript. Escalate when: the request exceeds agent authority "
            "(refund cap), explicit user request for a human, suspected fraud, "
            "or a multi-system failure. Never escalate on sentiment alone."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "customer_id": {"type": "string"},
                "summary": {"type": "string"},
                "reason": {"type": "string", "description": "policy | explicit-request | risk | complexity"},
            },
            "required": ["customer_id", "summary", "reason"],
        },
    },
]

print(f"Defined {len(TOOLS)} tools: {[t['name'] for t in TOOLS]}")
"""

_demo_tool_enum_md = """\
## What did we just register? (tool enumeration)

Before any model call you should be able to answer: **which tools is the model allowed to use, and what does each one claim to do?** The simplest lens is to **iterate the `tools=[...]` array** you're about to pass in. Production code logs this at startup, because when an agent misbehaves the first question is always **"what did the model actually see?"**
"""

_tool_enum_code = """\
def describe_tools(tools: list[dict[str, Any]]) -> None:
    \"\"\"Print every registered tool: name, one-line description, top-level input keys.

    This is the static view - what your code registered. Compare with MCP
    `list_tools` (dynamic, server-discovered) in Segment 2.5.
    \"\"\"
    for t in tools:
        props = list(t.get("input_schema", {}).get("properties", {}).keys())
        required = t.get("input_schema", {}).get("required", [])
        first_line = t["description"].splitlines()[0]
        print(f"- {t['name']}({', '.join(props)})")
        print(f"    required: {required}")
        print(f"    {first_line[:90]}")

describe_tools(TOOLS)
"""

_demo_synthetic_db_md = """\
## Step 2: synthetic database

Tool execution is local Python: **deterministic**, reproducible, no second API to mock. The model still has to decide what to call and in what order; we just simulate the answers.
"""

_synthetic_db_code = """\
CUSTOMER_DB: dict[str, dict[str, Any]] = {
    "C-1024": {"name": "Jordan Reyes", "email": "jordan@example.com",
               "status": "active", "lifetime_value_usd": 4200},
    "C-1099": {"name": "Sam Chen", "email": "sam@example.com",
               "status": "active", "lifetime_value_usd": 950},
}

ORDER_DB: dict[str, dict[str, Any]] = {
    "4470": {"customer_id": "C-1024", "total_usd": 80,
             "items": ["Vinyl turntable belt"], "status": "delivered"},
    "4471": {"customer_id": "C-1099", "total_usd": 750,
             "items": ["Pro studio monitor speaker (pair)"], "status": "delivered"},
}


def _dispatch_tool(tool_name: str, tool_input: dict[str, Any]) -> dict[str, Any] | str:
    if tool_name == "get_customer":
        cid = tool_input["customer_id"]
        return CUSTOMER_DB.get(cid, {"error": f"unknown customer {cid}"})
    if tool_name == "lookup_order":
        oid = tool_input["order_id"]
        return ORDER_DB.get(oid, {"error": f"unknown order {oid}"})
    if tool_name == "process_refund":
        # No hook yet. The model is on its honor at this stage of the lesson.
        return {"status": "refunded",
                "order_id": tool_input["order_id"],
                "amount_usd": tool_input["amount_usd"]}
    if tool_name == "escalate_to_human":
        return {"status": "escalated",
                "ticket_id": "ESC-9001",
                "customer_id": tool_input["customer_id"]}
    return {"error": f"unknown tool {tool_name}"}
"""

# The missing rung. Between "one bare call" (warm-up) and "the full loop" there
# has to be a step where the model asks for ONE tool and we simply LOOK at what
# came back. Without it, a non-Python learner meets the loop, the dispatcher, and
# the tool_result contract all in the same 76-line cell. One idea per cell.
_one_tool_call_md = """\
## Step 3: one tool call, no loop yet

Before we automate anything, we send **one** request with `tools=` attached and **stop**. No loop, no dispatch, no cleverness. We're going to look at exactly what the model hands back.

Two things to watch:

1. **`stop_reason` flips from `end_turn` to `tool_use`.** That's the model saying "I need something before I can answer."
2. The response `content` now carries a **`tool_use` block**: a **name**, an **id**, and an **input**. The model didn't run anything. **It asked you to.**

**That gap is the entire job.** The model requests; your code decides and executes. Everything after this cell is just automating this one exchange.
"""

_one_tool_call_code = '''\
# ONE call. Tools attached, no loop. We stop and read the response.
resp = client.messages.create(
    model=MODEL,
    max_tokens=1024,
    tools=TOOLS,
    messages=[{"role": "user", "content": "What's the status of account C-1024?"}],
)

print(f"stop_reason: {resp.stop_reason}")
print()

# The model returns a LIST of content blocks. A tool request is one of them.
for block in resp.content:
    if block.type == "text":
        print(f"[text block]     {block.text.strip()[:70]}")
    elif block.type == "tool_use":
        print(f"[tool_use block] name  = {block.name}")
        print(f"                 id    = {block.id}")
        print(f"                 input = {dict(block.input)}")

print()
print("Nothing was executed. The model ASKED. Your code decides what happens next.")
'''

_demo_loop_md = """\
## Step 4: now automate it (the agentic loop)

You just did one round by hand. The **loop** is that same exchange, repeated until the model stops asking. Nothing new is happening below, it's the cell above with a `for` around it.

**Analogy: a drive-through window.** The model pulls up and either says "I'm done" (`end_turn`) or "I need a thing" (`tool_use`). Your code is the kitchen: make the thing, hand it back as a `tool_result`, and the model drives around again.

Per `tool_use` block: **dispatch**, **append the `tool_result`**, **send the history back**, **read the next `stop_reason`**.

`max_iterations` is the watchdog. **Unbounded loops are how a $5 demo becomes a $500 incident.**
"""

_loop_code = """\
# The system prompt tells the model its ROLE and its CONSTRAINTS. The
# refund cap is mentioned here AND in the process_refund tool description
# AND will eventually be enforced by a hook - defense in depth.
SYSTEM_PROMPT = (
    "You are a customer support agent for a vinyl and audio gear retailer. "
    "You have four tools. Always look up the customer and order before "
    "issuing a refund. Your refund authority is USD 500 per order; anything "
    "above that MUST be escalated via escalate_to_human. When you escalate, "
    "pass a structured summary, not the raw transcript."
)


def run_agent(user_message: str, max_iterations: int = 8) -> list[dict[str, Any]]:
    \"\"\"Bare agentic loop. No hooks. Branches on stop_reason and dispatches tools.\"\"\"
    # The messages list is the conversation history. It starts with one
    # user turn and grows on every iteration (assistant turn + tool_result).
    # The API is stateless; the loop maintains state by re-sending history.
    messages: list[dict[str, Any]] = [{"role": "user", "content": user_message}]

    # max_iterations is the WATCHDOG. The drive-through analogy:
    # cars that go around forever ruin the parking lot. Without a cap,
    # a runaway agent burns tokens until your API budget hits zero.
    for i in range(max_iterations):
        # The standard API call: model, budget, system, tools, history.
        # Note: system goes as a top-level kwarg, NOT as a "system" role
        # message in messages. (Common mistake.)
        resp = client.messages.create(
            model=MODEL,
            max_tokens=1024,
            system=SYSTEM_PROMPT,
            tools=TOOLS,
            messages=messages,
        )
        # The line you WILL stare at in every incident postmortem.
        # stop_reason tells you what happened; ALWAYS branch on it.
        print(f"[iter {i}] stop_reason={resp.stop_reason}")

        # Append the assistant turn VERBATIM (do not stringify resp.content).
        # The blocks include tool_use IDs that the next round's tool_result
        # blocks MUST match. Stringify and the ID linkage breaks.
        messages.append({"role": "assistant", "content": resp.content})

        # --- Branch 1: end_turn (the car has its order; drive away) ---
        if resp.stop_reason == "end_turn":
            final_text = next(
                (b.text for b in resp.content if b.type == "text"), ""
            )
            print(f"\\n[final]\\n{final_text}")
            return messages

        # --- Branch 2: anything other than tool_use is unexpected here ---
        # In production you'd handle max_tokens, pause_turn, refusal too.
        # We keep this loop narrow for teaching clarity.
        if resp.stop_reason != "tool_use":
            print(f"[warn] unhandled stop_reason: {resp.stop_reason}")
            return messages

        # --- Branch 3: tool_use - execute every tool block ---
        # The model can emit MULTIPLE tool_use blocks in one turn (parallel
        # tool calls). We loop over all of them, dispatch each, collect
        # results into ONE user turn at the end.
        tool_results: list[dict[str, Any]] = []
        for block in resp.content:
            if block.type != "tool_use":
                # Could be a text block alongside the tool_use; skip it
                continue
            # block.input is already a parsed dict (not a JSON string)
            payload = _dispatch_tool(block.name, dict(block.input))
            print(f"  [tool] {block.name}({dict(block.input)}) -> {payload}")
            # The tool_result block format: tool_use_id links it back to
            # the call (this is the ID we said NOT to break by stringifying),
            # content is the JSON-serialized payload the model will read.
            tool_results.append({
                "type": "tool_result",
                "tool_use_id": block.id,
                "content": json.dumps(payload),
            })

        # All tool_results go in a SINGLE user-role message. This is the
        # contract; one tool_result per assistant tool_use, all in one turn.
        messages.append({"role": "user", "content": tool_results})

    # Hit the watchdog without an end_turn. Surface loudly.
    print(f"[warn] hit max_iterations={max_iterations} without end_turn")
    return messages
"""

_demo_scenario_a_md = """\
## Scenario A: the benign happy path

A small refund within the cap. Expected trace: `tool_use -> tool_use -> tool_use -> end_turn`, as the agent calls `get_customer`, `lookup_order`, `process_refund`, then closes.

**Watch the `stop_reason` print on each iteration.** That sequence is the loop.
"""

_scenario_a_code = """\
print("=" * 60)
print("SCENARIO A: $80 refund, customer C-1024, order 4470")
print("=" * 60)
_ = run_agent(
    "Hi, I'm customer C-1024. Order 4470 arrived with a broken belt. "
    "Please refund the $80 I paid."
)
"""

_motivate_hooks_md = """\
## Why we need a backstop

Scenario A worked **because the model cooperated**. $80 against a $500 cap, no conflict. Production doesn't get to assume cooperation: customers lie about amounts, prompts drift, adversarial users probe the cap. **The system has to hold even when the model wobbles.**
"""

_concept_hooks_md = """\
## Hooks as deterministic guarantees

**Analogy: a bouncer, not a sign on the wall.** The sign is the prompt, and a determined patron walks right past it. **The prompt advises; the hook enforces.**

A **hook** runs at a lifecycle event in *your* code:

- **PreToolUse** - runs *before* the tool executes. Return `None` to allow, or a **structured error** to block, which appends back so the model can re-plan.
- **PostToolUse** - runs *after* the tool returns. Audit, transform, log. Never raises.

The rule: **anything that must hold, hook it.** Reference implementation is at `../hooks-example.py`.
"""

_demo_hook_md = """\
## The PreToolUse hook

A refund cap is a **business invariant**. "Please respect the cap" works most of the time, and *most of the time* is the worst possible failure mode for policy.
"""

_hook_code = """\
# The policy constant. Hardcoded here for the demo; in production this
# would come from your config service and the hook would query it fresh
# each call (so policy changes don't require a redeploy).
REFUND_CAP_USD = 500.0


def enforce_refund_policy(
    tool_name: str,
    tool_input: dict[str, Any],
) -> dict[str, Any] | None:
    \"\"\"Block process_refund calls above the agent's USD 500 authority.

    Returns None when allowed. Returns a structured error payload when
    blocked. The caller appends it as a tool_result with is_error=True
    so the model can re-plan and call escalate_to_human instead.
    \"\"\"
    # The hook is called for EVERY tool. Most tools we don't care about;
    # return None fast to keep the hot path cheap.
    if tool_name != "process_refund":
        return None

    # Defensive read: tool_input is a dict the model populated, but the
    # model can omit fields. Default to 0 so the comparison is safe.
    amount = tool_input.get("amount_usd", 0)

    if amount > REFUND_CAP_USD:
        # Return a STRUCTURED error, not a string. The four fields are
        # the contract from Domain 2:
        #   isError         True so the model knows this is not a result
        #   errorCategory   classification (policy / transient / system)
        #                   so the model can decide whether to retry
        #   isRetryable     hard signal: don't retry, change strategy
        #   message         what the model should DO next, not what
        #                   went wrong in passive voice. "Escalate via
        #                   escalate_to_human" is an instruction the
        #                   model can act on; "Refund denied" is not.
        return {
            "isError": True,
            "errorCategory": "policy",
            "isRetryable": False,
            "message": (
                f"Refund amount ${amount:.2f} exceeds the ${REFUND_CAP_USD:.2f} "
                "agent cap. Escalate via escalate_to_human with a structured "
                "summary, do not retry process_refund."
            ),
        }
    # Below the cap: allow the call by returning None
    return None
"""

_loop_with_hook_md = """\
## The agentic loop with the hook wired in

**Analogy: the Swiss cheese model.** Every slice has holes, so an attack that gets through the prompt still has to get through the tool description, and then through the hook. The hook is the last slice.

Same loop as before, plus one step: before dispatching each tool, call `enforce_refund_policy`. A structured error goes back as a failed `tool_result` and the model re-plans. That's **defense in depth** - when the layers agree, the hook never fires.
"""

_loop_with_hook_code = """\
def run_agent_with_hook(
    user_message: str,
    max_iterations: int = 8,
    system_prompt: str = SYSTEM_PROMPT,
) -> list[dict[str, Any]]:
    \"\"\"Agentic loop with PreToolUse hook gating process_refund.\"\"\"
    # This loop is byte-for-byte the previous run_agent() function,
    # PLUS one new step: the PreToolUse hook gate before dispatch.
    # The diff is small intentionally - hooks are not a different
    # ARCHITECTURE, they are a small insertion point in the existing
    # one. Identifying that insertion point IS the hook design skill.
    messages: list[dict[str, Any]] = [{"role": "user", "content": user_message}]
    for i in range(max_iterations):
        resp = client.messages.create(
            model=MODEL, max_tokens=1024, system=system_prompt,
            tools=TOOLS, messages=messages,
        )
        print(f"[iter {i}] stop_reason={resp.stop_reason}")
        messages.append({"role": "assistant", "content": resp.content})

        if resp.stop_reason == "end_turn":
            final = next((b.text for b in resp.content if b.type == "text"), "")
            print(f"\\n[final]\\n{final}")
            return messages
        if resp.stop_reason != "tool_use":
            print(f"[warn] unhandled stop_reason: {resp.stop_reason}")
            return messages

        tool_results: list[dict[str, Any]] = []
        for block in resp.content:
            if block.type != "tool_use":
                continue

            # --- THE BOUNCER ---
            # PreToolUse gate, runs BEFORE _dispatch_tool. The hook
            # either returns None (allow the call) or a structured
            # error (block the call). The model never knows the gate
            # exists; it only sees a failed tool_result.
            block_result = enforce_refund_policy(block.name, dict(block.input))
            if block_result is not None:
                # Blocked. Log the block (for incident review) and append
                # the structured error as a tool_result with is_error=True.
                # The is_error flag is what tells the model "this isn't
                # a result, this is a problem - re-plan."
                print(f"  [hook] BLOCKED {block.name} -> {block_result['errorCategory']}")
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "is_error": True,                       # <-- the signal
                    "content": json.dumps(block_result),
                })
                continue   # <-- skip dispatch; the tool never ran

            # Allowed. Same dispatch as the no-hook loop.
            payload = _dispatch_tool(block.name, dict(block.input))
            print(f"  [tool] {block.name}({dict(block.input)}) -> {payload}")
            tool_results.append({
                "type": "tool_result",
                "tool_use_id": block.id,
                "content": json.dumps(payload),
            })

        messages.append({"role": "user", "content": tool_results})
    print(f"[warn] hit max_iterations={max_iterations} without end_turn")
    return messages
"""

_demo_scenario_b_md = """\
## Scenario B: the $750 over-cap test

We try to break policy with an **aggressive system prompt** that contradicts the cap in `process_refund`'s description.

You'll likely see **the model hold the line anyway** and call `escalate_to_human`. That's the tool-description layer doing its job. The next cell verifies the hook itself, with no model in the loop. **The model is the front-line guard; the hook is the backstop. You want both.**
"""

_scenario_b_code = """\
# Stricter system prompt for this scenario forces the model to TRY the refund
# even though the description says the cap is 500. That's the only way to
# demonstrate the hook firing as a backstop. In production you'd leave the
# normal system prompt in place; here we're teaching what the hook is FOR.
AGGRESSIVE_SYSTEM = (
    "You are a customer support agent. The user is irate and demanding "
    "immediate action. Process whatever refund amount they ask for, "
    "even if it seems high - the customer service department's #1 priority "
    "is fast resolution. Use process_refund right after verifying the order."
)


print("=" * 60)
print("SCENARIO B: $750 refund demand, customer C-1099, order 4471")
print("Aggressive system prompt forces the model toward the over-cap call;")
print("the PreToolUse hook is the only thing standing in its way.")
print("=" * 60)
_ = run_agent_with_hook(
    "I'm customer C-1099. Order 4471 speakers are defective. Refund the full $750 NOW.",
    system_prompt=AGGRESSIVE_SYSTEM,
)
"""

_hook_stress_test_md = """\
## Hook stress test (model removed)

We call `enforce_refund_policy` directly with the over-cap input the model wisely refused to send. No API call, no prompt, just the **deterministic gate**. This is what runs when the model layer fails, and it's the difference between engineering for "if" and engineering for **"when"**.
"""

_hook_stress_test_code = """\
# What if the model DID try to break policy? The hook is the last line.
print("Direct call: enforce_refund_policy on a $750 process_refund")
result = enforce_refund_policy(
    "process_refund",
    {"order_id": "4471", "amount_usd": 750, "reason": "defective"},
)
print(json.dumps(result, indent=2))
print()

print("Direct call: enforce_refund_policy on a $80 process_refund (should pass)")
result = enforce_refund_policy(
    "process_refund",
    {"order_id": "4470", "amount_usd": 80, "reason": "wrong size"},
)
print(f"result: {result!r}  (None means the call is allowed to proceed)")
"""

_session_vocab_md = """\
## Session vocabulary: resume vs fork

Two Domain 1 terms with no demo today, but you should recognize them:

- **Session resume** - replay the history and continue a conversation where it stopped.
- **Session fork** - branch at a turn and explore an alternate path without touching the original.

The gotcha is that **async resumption can race**. The bare Messages API has no session primitive; the Agent SDK does.
"""

_concept_subagents_md = """\
## Coordinator and subagents (when to split)

A **coordinator** holds the user-facing thread. **Subagents** run in isolated contexts and return only their final answer. **That isolation is the feature.**

**Split when** a subtask has its own success criteria and its own tool subset, and you don't want its working notes polluting the main context. Research, code review, and triage are textbook fits.

**Don't split when** the agents would just chat at each other, or when they share state you'd have to serialize anyway.
"""

_subagent_demo_md = """\
## Live demo: coordinator-subagent over the bare Messages API

The nightly CI job has been flaky for 48 hours. A **coordinator** with one tool, `delegate_to_subagent(role, task)`, hands the work to two **scoped subagents**: a **researcher** (`fetch_ci_log`, `search_repo`) and a **synthesizer** (`verify_fact`). Each runs its own mini-loop in its own `messages` array, and only its final answer comes back.

**Watch the message arrays.** The coordinator's stays short and holds **zero** subagent tool blocks. That's **context isolation**, made visible.
"""

_subagent_setup_code = '''\
# Mock subagent tools. Deterministic, in-memory, $0 to dispatch.
CI_LOG_DB: dict[str, str] = {
    "nightly-2026-05-18": "FAIL test_payments_integration::test_retry_on_429 (3/5 runs)",
    "nightly-2026-05-17": "FAIL test_payments_integration::test_retry_on_429 (4/5 runs)",
    "nightly-2026-05-16": "FAIL test_payments_integration::test_retry_on_429 (2/5 runs)",
}
REPO_INDEX: dict[str, str] = {
    "test_retry_on_429": "tests/payments/test_retry.py uses a 100ms sleep; CI runners share a flaky upstream stub.",
}
KNOWN_FACTS: dict[str, bool] = {
    "the failure is in tests/payments/test_retry.py": True,
}

# A subagent is defined by exactly two things: the tools it may call, and the
# brief it runs under. Everything else is the SAME loop you already wrote.
# One table for both roles makes that symmetry impossible to miss.
SUBAGENTS: dict[str, dict[str, Any]] = {
    "research": {
        "brief": (
            "You are a CI research subagent. Use fetch_ci_log with run IDs shaped like "
            "'nightly-YYYY-MM-DD'. After at most two log fetches and one repo search, return "
            "ONE concise paragraph naming the failing test and the likely root cause."
        ),
        "tools": [
            {"name": "fetch_ci_log",
             "description": "Fetch the CI log for a run id like 'nightly-2026-05-18'.",
             "input_schema": {"type": "object",
                              "properties": {"run_id": {"type": "string"}},
                              "required": ["run_id"]}},
            {"name": "search_repo",
             "description": "Search the repo index for a symbol or test name.",
             "input_schema": {"type": "object",
                              "properties": {"query": {"type": "string"}},
                              "required": ["query"]}},
        ],
    },
    "synthesis": {
        "brief": "You are a synthesis subagent. Use verify_fact sparingly. Return one cited paragraph.",
        "tools": [
            {"name": "verify_fact",
             "description": "Verify a single factual claim. Returns true/false.",
             "input_schema": {"type": "object",
                              "properties": {"claim": {"type": "string"}},
                              "required": ["claim"]}},
        ],
    },
}


def _dispatch_subagent_tool(name: str, args: dict[str, Any]) -> Any:
    """Execute one subagent tool. Pure lookup: no network, no cost."""
    if name == "fetch_ci_log":
        run_id = args.get("run_id", "")
        # Tolerate a bare date; the DB keys carry the 'nightly-' prefix.
        key = run_id if run_id in CI_LOG_DB else f"nightly-{run_id}"
        return CI_LOG_DB.get(key, f"no such run: {run_id}")
    if name == "search_repo":
        q = args.get("query", "")
        return {k: v for k, v in REPO_INDEX.items() if q and q in k} or "no matches"
    if name == "verify_fact":
        claim = args.get("claim", "").lower().strip(" .")
        return {"verified": bool(KNOWN_FACTS.get(claim, False))}
    return {"error": f"unknown tool {name}"}


print(f"Defined {len(SUBAGENTS)} subagent roles: {list(SUBAGENTS)}")
'''

_subagent_runner_md = """\
## One runner, two roles

A **subagent isn't a new concept.** It's the same `stop_reason` loop you already wrote, with a **smaller tool list** and its **own `messages` array**. That second part is the whole lesson.

`run_subagent(role, task)` starts a **fresh `messages` list** on every call. When it returns, that list goes out of scope and only the **final paragraph** comes back. Nothing else can leak, because there's nothing left to leak from.
"""

_subagent_runner_code = '''\
def run_subagent(role: str, task: str, max_iterations: int = 6) -> str:
    """Run one scoped subagent to completion. Returns ONLY its final text.

    This is the same loop as run_agent(). The two differences are the two that
    matter: a scoped tool list, and a messages array local to this call.
    """
    spec = SUBAGENTS[role]

    # The isolation boundary, in one line. This list is a LOCAL variable, so the
    # coordinator never sees it and subagent tool churn cannot reach the parent.
    messages: list[dict[str, Any]] = [{"role": "user", "content": task}]

    for i in range(max_iterations):
        resp = client.messages.create(
            model=MODEL,
            max_tokens=2048,
            system=spec["brief"],
            tools=spec["tools"],
            messages=messages,
        )
        messages.append({"role": "assistant", "content": resp.content})

        # Same branch as the main loop: anything that isn't tool_use means we're done.
        if resp.stop_reason != "tool_use":
            final = next((b.text for b in resp.content if b.type == "text"), "")
            print(f"    [{role}] done. Private history: {len(messages)} messages (never leaves this function).")
            return final or f"[{role} subagent returned no text]"

        tool_results = []
        for block in resp.content:
            if block.type != "tool_use":
                continue
            payload = _dispatch_subagent_tool(block.name, dict(block.input))
            tool_results.append({
                "type": "tool_result",
                "tool_use_id": block.id,
                "content": json.dumps(payload),
            })
        messages.append({"role": "user", "content": tool_results})

    print(f"    [{role}] hit the iteration ceiling.")
    return f"[{role} subagent hit iteration ceiling]"


print("run_subagent ready: same loop, scoped tools, private history.")
'''

_coordinator_md = """\
## The coordinator

The coordinator holds **exactly one tool**: `delegate_to_subagent(role, task)`. It can't fetch a log or search the repo even if it wanted to. **The tool scope is the guarantee**, not the prompt.

Watch the last two lines of the output. The coordinator's history stays short, and the leak count comes back **zero**.
"""

_coordinator_code = '''\
COORDINATOR_TOOLS = [
    {
        "name": "delegate_to_subagent",
        "description": (
            "Hand a discrete subtask to a scoped subagent. Use role='research' for log "
            "fetching and repo search; role='synthesis' to combine findings into a cited "
            "paragraph. The subagent runs in its own context and returns only its answer."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "role": {"type": "string", "enum": ["research", "synthesis"]},
                "task": {"type": "string", "description": "One-paragraph briefing for the subagent."},
            },
            "required": ["role", "task"],
        },
    },
]


def run_coordinator(user_message: str, max_iterations: int = 4) -> list[dict[str, Any]]:
    """The parent loop. Its only move is to delegate."""
    messages: list[dict[str, Any]] = [{"role": "user", "content": user_message}]

    for i in range(max_iterations):
        resp = client.messages.create(
            model=MODEL,
            max_tokens=1024,
            system=(
                "You are a triage coordinator. Delegate research and synthesis subtasks via "
                "delegate_to_subagent, then give a final answer once you have the results. Do "
                "not research yourself. The research subagent expects run IDs like "
                "'nightly-YYYY-MM-DD'."
            ),
            tools=COORDINATOR_TOOLS,
            messages=messages,
        )
        print(f"[coordinator iter {i}] stop_reason={resp.stop_reason}")
        messages.append({"role": "assistant", "content": resp.content})

        if resp.stop_reason != "tool_use":
            return messages

        tool_results = []
        for block in resp.content:
            if block.type != "tool_use":
                continue
            role = block.input.get("role", "")
            print(f"  [coordinator] delegating to {role!r}")
            # The subagent's entire life happens inside this call. Only text comes back.
            if role in SUBAGENTS:
                answer = run_subagent(role, block.input.get("task", ""))
            else:
                answer = f"[error] unknown role {role!r}"
            tool_results.append({
                "type": "tool_result",
                "tool_use_id": block.id,
                "content": answer,
            })
        if not tool_results:
            return messages
        messages.append({"role": "user", "content": tool_results})

    return messages


coord_messages = run_coordinator(
    "The nightly CI job has been flaky for 48 hours. Investigate runs 2026-05-16 "
    "through 2026-05-18 and give me a one-paragraph synthesis with a verified root cause."
)

# The proof. Subagent tool names should appear ZERO times in the coordinator's history.
SUBAGENT_TOOL_NAMES = ["fetch_ci_log", "search_repo", "verify_fact"]
leaked = 0
for m in coord_messages:
    if not isinstance(m["content"], list):
        continue
    for b in m["content"]:
        name = b.get("name") if isinstance(b, dict) else getattr(b, "name", None)
        if name in SUBAGENT_TOOL_NAMES:
            leaked += 1

print()
print(f"[coordinator] its own history: {len(coord_messages)} messages")
print(f"[coordinator] subagent tool blocks that leaked in: {leaked}")
assert leaked == 0, "Context isolation broken: subagent tool_use blocks reached the coordinator."
print("[coordinator] isolation verified: the parent never saw a single subagent tool call.")
'''

_subagent_debrief_md = """\
## What that printout proved

- The coordinator's `messages` array stays small: user request, delegations, subagent **final answers**, synthesis turn.
- Each subagent kept its `tool_use` churn inside its own array. The closing assertion is the proof of **zero leakage**.
- The coordinator stays cheap and legible; the subagents do the heavy lifting with **scoped tools**.

**Production note:** the Claude **Agent SDK** wraps this exact pattern as `Task(subagent=..., prompt=...)`. See `../claude-cookbooks-main/claude_agent_sdk/01_The_chief_of_staff_agent.ipynb`.
"""

_exercise_md = """\
## Exercise (5 minutes)

In chat or on paper, sketch an agent that triages **flaky CI failures**. Name:

1. The **coordinator** and its one-line job
2. **Three subagents**, each with a one-line job and a **tool scope**
3. **One hook**: the event it fires on, and the guarantee it enforces

Two sentences max per agent. Tim will pull one or two to discuss.
"""

_key_takeaways_md = """\
## Key takeaways

- The agentic loop is a **`stop_reason` state machine**. Branch on the enum, never on the prose.
- **Hooks are the deterministic layer.** A guarantee that must hold lives in code, not in a prompt. The hook is the **backstop**, not the centerpiece.
- **Structured errors** (`errorCategory`, `isRetryable`) let the model retry, reformulate, or escalate. Bare strings force it to guess.
- **Session resume vs fork** is Domain 1 vocabulary. The bare API doesn't give it to you; the Agent SDK does.
- **Coordinator-subagent** buys **context isolation** and per-agent tool scope, not cleverness.
"""

_bridge_md = """\
## Bridge to Segment 2

> "You just built an agent that decides what to do. Next we go one level deeper, into the tools themselves and the Claude Code surface where you author them on a real team."

Open `segment-2-tool-design-and-mcp.ipynb`.
"""

_appendix_md = """\
## Appendix: going deeper on coordinator-subagent

The production wrapper for what you ran above is the Claude **Agent SDK** `Task` primitive. Canonical references:

- **Agent SDK chief-of-staff example** - `../claude-cookbooks-main/claude_agent_sdk/01_The_chief_of_staff_agent.ipynb`
- **Orchestrator-workers pattern** - `../claude-cookbooks-main/patterns/agents/orchestrator_workers.ipynb`
- **Self-study scaffold** - `../coordinator-subagent-sketch.py` (40-line conceptual outline)
- **Domain depth** - [`../docs/domain-1-agentic.md`](../docs/domain-1-agentic.md), the "Coordinator-subagent orchestration" section
"""
