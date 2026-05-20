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
        # Coordinator-subagent: concept, then a runnable bare-API demo
        ("md", _concept_subagents_md),
        ("md", _subagent_demo_md),
        ("code", _subagent_demo_code),
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
**Reference:** [`../domain-1-agentic.md`](../domain-1-agentic.md)

We are going to build a **customer support agent** that decides which tools to call, in what order, and when to escalate. The dramatic beat: the model will *want* to break a refund policy. A **PreToolUse hook** will say no. The agent will re-plan and escalate correctly. The guarantee comes from your code, not from begging the prompt.

The arc of this notebook: **first Claude call** -> **the agentic loop in theory** -> **a working loop on Scenario A** -> **the hook as a backstop** -> **Scenario B with the hook firing**. We earn each concept before we use it.
"""

_lo_md = """\
## Learning objectives

By the end of this segment you will be able to:

- Make a **basic Claude API call** and branch on `stop_reason` (the platform's universal control lever)
- Explain the **agentic loop** and identify which `stop_reason` value drives each branch of the control flow
- Place **hooks** at the right lifecycle events (PreToolUse, PostToolUse) for deterministic guarantees
- Distinguish **prompt-layer guidance** from **application-layer enforcement**, and pick the right layer for a given guarantee
- Recognize **session resume vs fork** as Domain 1 vocabulary, and build a **coordinator-subagent** topology over the bare Messages API when subtask isolation pays off
"""

_warm_up_md = """\
## Warm-up: your first Claude call

Before we wire up tools, before we talk about loops, we make **one bare call**. Three lines. Pick a model. Send a user message. Read `stop_reason`.

This is the whole platform. Everything else in this course is layers on top of this primitive.

**Prerequisites for this cell**

- An **API key** from the Anthropic Console (https://console.anthropic.com), exported as `ANTHROPIC_API_KEY`
- The `anthropic` SDK installed (`uv sync --project notebooks` from repo root, or fallback `pip install -r notebooks/requirements.txt`)

If Segment 0 (pre-flight) passed for you, both are already true. If you skipped Segment 0 and this cell fails, that is the fix.

**Why Haiku 4.5 for the warm-up?** Cheapest, fastest model that gets a single-sentence answer right. We will switch to Sonnet 4.6 the moment we add tools, because Sonnet is the better orchestrator. Model selection is itself a Domain 1 skill: pick the smallest model that does the job.
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
    model="claude-haiku-4-5-20251001",
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

You just made one call. Now we add the control structure that turns a call into an **agent**.

The loop is small. The model emits **content** plus a **`stop_reason`**. Your code reads `stop_reason` and branches:

- `end_turn` -> return to the user
- `tool_use` -> execute the requested tools, append `tool_result`, send the conversation back to the model
- `max_tokens` -> output may be truncated; decide whether to continue
- `stop_sequence` -> a custom stop sequence fired
- `pause_turn` -> a long-running turn was paused; resume it
- `refusal` -> the streaming classifier intervened on policy

That is the whole control flow. **Branch on the enum, never on the prose.** "It said thanks, so I assume it's done" is how production agents go feral.
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

The agent is not the model. **The agent is the loop around the model.** Owning that loop is what separates a chatbot from a system.
"""

_demo_setup_md = """\
## Demo: customer support agent

We will build the agent in four moves:

1. **Tools** - four definitions whose `description` carries the contract
2. **Synthetic DB** - small Python dicts so tool execution is deterministic and cheap
3. **The loop** - branches on `stop_reason`, dispatches tools, surfaces escalations
4. **The hook** - added LATER as a backstop, after the loop is real

We run two scenarios: a benign happy path first (no hook), then a $750 refund against a $500 cap (hook fires).
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
## What did we just register? (tool enumeration, lens 1 of 4)

Before any model call, you should be able to **answer this**: at this point in the program, which tools is the model allowed to use, what does each one claim to do, and what shape does each one accept? In Segment 2.5 we show four lenses on this question; here is the simplest one - **iterate the `tools=[...]` array your code is about to pass to `messages.create()`**.

The pattern below is what production code logs at startup. When an agent does something surprising in week three, the first question is always **"what did the model actually see?"** This cell gives you that answer in five lines.
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

Tool execution is local Python. Deterministic, reproducible, no second API to mock. The model still has to *decide* what to call, in what order; we just simulate the answers.
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

_demo_loop_md = """\
## Step 3: the agentic loop (no hook yet)

**Analogy:** an agentic loop is a **drive-through window**. The car (model) pulls up to the speaker (your code calls `messages.create()`). The car says either "I'm done, here's my order" (`stop_reason=end_turn`) or "I need a thing" (`stop_reason=tool_use`). When the car asks for a thing, the kitchen (your code) makes it, hands it through the window (appends a `tool_result`), and the car drives back around for the next round. The drive-through has a max-cycles limit because cars that go around forever ruin the parking lot.

This is the centerpiece. The loop branches on `stop_reason`. For every iteration we **print the stop_reason**, so you see the state transitions live.

For each `tool_use` block the model emits, we:
1. Dispatch the tool against the synthetic DB
2. Append the result as a `tool_result`
3. Send the conversation back to the model
4. Read the next `stop_reason`

The loop has a `max_iterations` ceiling. **Unbounded loops are how a $5 demo becomes a $500 incident.**

**No hook in this version.** We want to see the loop work first.
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

A small refund within the cap. Expected trace: `tool_use -> tool_use -> tool_use -> end_turn`. The agent calls `get_customer`, then `lookup_order`, then `process_refund`, then closes.

**Watch the `stop_reason` print on each iteration.** That sequence is the loop. The agent is the loop. The model is just the decision-maker the loop calls.
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

Scenario A worked **because the model cooperated**. The cap was $500, the refund was $80, no conflict. The model behaved.

Production agents do not get to assume cooperation. Customers will lie about amounts. Prompts will drift. Adversarial users will try to break the cap. **The system has to hold even when the model wobbles.**

So we add a **PreToolUse hook**. It runs in our code, not in the model's head. The model can ask to refund $750; the hook says no. The hook is the **backstop**, the deterministic layer the prompt cannot override.

The next three cells: concept, hook code, then a re-run of the loop with the hook wired in. Then Scenario B - the $750 attack.
"""

_concept_hooks_md = """\
## Hooks as deterministic guarantees

**Analogy:** a hook is a **bouncer at the door**, not a sign on the wall. A sign that says "no shoes, no shirt, no service" is the prompt - most patrons read it and comply, but anyone determined enough can walk past. A bouncer who physically checks every patron is the hook. The bouncer doesn't argue, doesn't negotiate, doesn't trust the patron's word about their footwear. The bouncer enforces. **The prompt advises; the hook enforces.**

A **hook** is a function that runs at a specific lifecycle event - not on the model's say-so, on your code's. The two we care about today:

- **PreToolUse** - runs *before* a tool executes. Inspect the tool name and inputs. Return `None` to allow, or return a **structured error** to block. The blocked call appends back to the conversation so the model can re-plan.
- **PostToolUse** - runs *after* a tool returns. Audit, transform, log. Never raises; log loudly, return quietly.

The rule: **anything that must hold, hook it.** Anything that should usually hold but is allowed to drift, prompt it. Confusing those two is how policy quietly evaporates.

Reference implementation lives at `../hooks-example.py`. Read it after class.
"""

_demo_hook_md = """\
## The PreToolUse hook

The contract from `../hooks-example.py`: return `None` to allow the call, or return a **structured error** to block it. The structured error gets appended back as a `tool_result` with `is_error=True`, and the model gets a chance to re-plan.

**The reason this is a hook and not a prompt instruction:** a refund cap is a business invariant. "Please respect the cap" works most of the time. *Most of the time* is the worst possible failure mode for policy.
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

**Analogy:** **Swiss cheese model of accidents**. Each slice of cheese has holes (the prompt has gaps, the tool description can be misread, the model can be talked into things). A single slice doesn't stop accidents. But stack three slices and the holes rarely line up - an attack has to get through every layer. The hook is the *last* slice. When the prompt and the tool description both fail, the hook is what's left.

Same loop as before. One added step: before dispatching each tool, call `enforce_refund_policy`. If it returns a structured error, append it back as a failed `tool_result` and let the model re-plan.

This is the **defense in depth** pattern: the prompt says "respect the cap", the tool description says "stop at $500", and now the hook says "I will physically prevent you from exceeding $500". When the layers agree, the hook never fires. The hook is there for when they disagree.
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

We try to get the model to break policy. The trick: an **aggressive system prompt** that tells it to process whatever the user demands, contradicting the cap baked into `process_refund`'s description.

What you'll likely see is **the model holding the line anyway**, calling `escalate_to_human` with a structured summary instead of attempting the over-cap refund. That is the **prompt + tool-description layer** doing its job.

**This is good production behavior.** When the layers agree, the hook never has to fire. We're going to verify the hook works in the *next* cell - calling `enforce_refund_policy` directly, no model in the loop. The model is the front-line guard; the hook is the backstop. **You want both.**
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

To prove the hook is the **backstop**, we now call `enforce_refund_policy` directly with the over-cap input the model wisely refused to send. No API call. No prompt. Just the deterministic gate.

This is what runs when (not if) the model layer fails. **Engineering for "when".**
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

Two CCA-F Domain 1 terms that do not have a demo today but you should recognize:

- **Session resume** - continue an existing conversation from where it stopped. The full message history is replayed; the model picks up state. Use when the user comes back to the same thread.
- **Session fork** - branch a conversation at a specific turn and explore an alternate path without affecting the original. Use for A/B exploration, "what if I had answered differently", or rolling back a bad turn.

The gotcha: **async resumption can race.** If a user resumes a session while a background task is still running on the original branch, you can end up with two assistant turns claiming to be turn N+1. Production systems serialize per-session writes or fork explicitly.

We do not demo this in class. The bare Messages API has no session primitive - you implement resume by replaying `messages`, and fork by deep-copying the list. The Claude Agent SDK has first-class session objects; see the cookbook reference in the appendix.
"""

_concept_subagents_md = """\
## Coordinator and subagents (when to split)

One **coordinator** holds the user-facing thread. **Subagents** run in their own isolated contexts and return only their final answer to the coordinator. That isolation is the feature, not a limitation.

**Split when:**
- A subtask has its own success criteria and its own tool subset
- You do not want the subtask's working notes polluting the main context
- Research, code review, triage are textbook fits

**Do not split when:**
- Two agents would just chat at each other (one slow agent with extra latency)
- The subtasks share state that you would have to serialize anyway

Next cell, we **run** a tiny coordinator-subagent system over the bare Messages API. No second SDK install. The point of the demo is not the toy task; it is to **watch the message arrays** and see that the coordinator's context never touches the subagents' working notes.
"""

_subagent_demo_md = """\
## Live demo: coordinator-subagent over the bare Messages API

**Scenario:** the nightly CI job has been flaky for 48 hours. A **coordinator** delegates the investigation to two **scoped subagents**: a **researcher** (`fetch_ci_log`, `search_repo`) and a **synthesizer** (`verify_fact`). Each subagent runs its own mini-loop in its own `messages` array. Only its **final answer** comes back.

The coordinator gets one tool: `delegate_to_subagent(role, task)`. When the model emits a `tool_use` for `delegate_to_subagent`, our dispatcher runs a fresh `client.messages.create` loop for that subagent and returns the final text as the `tool_result`.

**What to watch in the printout:**

- The coordinator's message-history length stays small. It contains the user turn, the two delegations, two short subagent answers, and the final synthesis turn.
- Each subagent has its own message history, with its own `tool_use` and `tool_result` blocks for `fetch_ci_log` etc.
- The coordinator's array contains **no** `fetch_ci_log` or `search_repo` blocks. That is context isolation, made visible.
"""

_subagent_demo_code = """\
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


def _run_research_subagent(task: str) -> str:
    \"\"\"Scoped subagent: fetch_ci_log + search_repo only. Returns final text.\"\"\"
    tools = [
        {
            "name": "fetch_ci_log",
            "description": "Fetch the CI log for a given run id like 'nightly-2026-05-18'.",
            "input_schema": {"type": "object",
                             "properties": {"run_id": {"type": "string"}},
                             "required": ["run_id"]},
        },
        {
            "name": "search_repo",
            "description": "Search the repo index for a symbol or test name.",
            "input_schema": {"type": "object",
                             "properties": {"query": {"type": "string"}},
                             "required": ["query"]},
        },
    ]
    messages = [{"role": "user", "content": task}]
    for i in range(6):
        resp = client.messages.create(
            model=MODEL, max_tokens=2048,
            system=(
                "You are a CI research subagent. Use fetch_ci_log with run IDs in the form "
                "'nightly-YYYY-MM-DD' (e.g. 'nightly-2026-05-18'). After at most two log fetches "
                "and one repo search, return ONE concise paragraph identifying the failing test "
                "and the likely root cause. Do not include your working notes."
            ),
            tools=tools, messages=messages,
        )
        messages.append({"role": "assistant", "content": resp.content})
        if resp.stop_reason == "end_turn":
            final = next((b.text for b in resp.content if b.type == "text"), "")
            print(f"    [research subagent] message-history length: {len(messages)} (isolated)")
            return final or "[research subagent ended without text]"
        results = []
        for b in resp.content:
            if b.type != "tool_use":
                continue
            # Tolerate the model emitting bare date strings; the DB keys carry a 'nightly-' prefix.
            if b.name == "fetch_ci_log":
                run_id = b.input.get("run_id", "")
                key = run_id if run_id in CI_LOG_DB else f"nightly-{run_id}"
                payload = CI_LOG_DB.get(key, f"no such run: {run_id}")
            elif b.name == "search_repo":
                q = b.input.get("query", "")
                hits = {k: v for k, v in REPO_INDEX.items() if q and q in k}
                payload = hits or "no matches"
            else:
                payload = {"error": f"unknown tool {b.name}"}
            results.append({"type": "tool_result", "tool_use_id": b.id, "content": json.dumps(payload)})
        if not results:
            print(f"    [research subagent] stop_reason={resp.stop_reason}, ending. message-history length: {len(messages)} (isolated)")
            return "[research subagent: no dispatchable blocks]"
        messages.append({"role": "user", "content": results})
    print(f"    [research subagent] hit iteration ceiling. message-history length: {len(messages)} (isolated)")
    return "[research subagent hit iteration ceiling]"


def _run_synthesis_subagent(task: str) -> str:
    \"\"\"Scoped subagent: verify_fact only.\"\"\"
    tools = [
        {
            "name": "verify_fact",
            "description": "Verify a single factual claim. Returns true/false.",
            "input_schema": {"type": "object",
                             "properties": {"claim": {"type": "string"}},
                             "required": ["claim"]},
        },
    ]
    messages = [{"role": "user", "content": task}]
    for i in range(3):
        resp = client.messages.create(
            model=MODEL, max_tokens=2048,
            system="You are a synthesis subagent. Use verify_fact sparingly. Return one cited paragraph.",
            tools=tools, messages=messages,
        )
        messages.append({"role": "assistant", "content": resp.content})
        if resp.stop_reason == "end_turn":
            final = next((b.text for b in resp.content if b.type == "text"), "")
            print(f"    [synthesis subagent] message-history length: {len(messages)} (isolated)")
            return final or "[synthesis subagent ended without text]"
        results = []
        for b in resp.content:
            if b.type != "tool_use":
                continue
            claim = b.input.get("claim", "").lower().strip(" .")
            payload = {"verified": bool(KNOWN_FACTS.get(claim, False))}
            results.append({"type": "tool_result", "tool_use_id": b.id, "content": json.dumps(payload)})
        if not results:
            return "[synthesis subagent: tool_use stop with no dispatchable blocks]"
        messages.append({"role": "user", "content": results})
    print(f"    [synthesis subagent] message-history length: {len(messages)} (isolated, ceiling hit)")
    return "[synthesis subagent hit iteration ceiling]"


# The coordinator's only tool is delegate_to_subagent. Its tool surface stays small
# precisely because the heavy lifting lives in the scoped subagents.
COORDINATOR_TOOLS = [
    {
        "name": "delegate_to_subagent",
        "description": (
            "Hand a discrete subtask to a scoped subagent. Pick role='research' for "
            "log fetching and repo search; role='synthesis' for combining findings "
            "into a cited paragraph. The subagent runs in its own isolated context "
            "and returns only its final answer."
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
    messages: list[dict[str, Any]] = [{"role": "user", "content": user_message}]
    for i in range(max_iterations):
        resp = client.messages.create(
            model=MODEL, max_tokens=1024,
            system=(
                "You are a triage coordinator. Delegate research and synthesis subtasks via the "
                "delegate_to_subagent tool, then give a final answer when you have the subagent results. "
                "Do not attempt research yourself. The research subagent expects CI run IDs in the form "
                "'nightly-YYYY-MM-DD'."
            ),
            tools=COORDINATOR_TOOLS, messages=messages,
        )
        print(f"[coordinator iter {i}] stop_reason={resp.stop_reason}")
        messages.append({"role": "assistant", "content": resp.content})
        if resp.stop_reason == "end_turn":
            return messages
        if resp.stop_reason != "tool_use":
            return messages
        tool_results = []
        for block in resp.content:
            if block.type != "tool_use":
                continue
            role = block.input.get("role", "")
            task = block.input.get("task", "")
            print(f"  [coordinator] delegating to {role!r} subagent")
            if role == "research":
                final = _run_research_subagent(task)
            elif role == "synthesis":
                final = _run_synthesis_subagent(task)
            else:
                final = f"[error] unknown role {role!r}"
            tool_results.append({
                "type": "tool_result", "tool_use_id": block.id,
                "content": final or "[subagent returned no text]",
            })
        if not tool_results:
            # Defensive: stop_reason==tool_use with no dispatchable blocks (rare API edge case).
            return messages
        messages.append({"role": "user", "content": tool_results})
    return messages


coord_messages = run_coordinator(
    "The nightly CI job has been flaky for 48 hours. Investigate runs 2026-05-16 "
    "through 2026-05-18 and give me a one-paragraph synthesis with a verified root cause."
)

# Make the isolation visible. Coordinator's array should NOT contain any
# fetch_ci_log / search_repo / verify_fact tool_use blocks - those stayed in the subagents.
def _count_tool_uses(msgs: list[dict[str, Any]], names: list[str]) -> dict[str, int]:
    counts = {n: 0 for n in names}
    for m in msgs:
        content = m["content"]
        if not isinstance(content, list):
            continue
        for b in content:
            name = getattr(b, "name", None) if not isinstance(b, dict) else b.get("name")
            if name in counts:
                counts[name] += 1
    return counts

print()
print(f"[coordinator] message-history length: {len(coord_messages)}")
leaked = _count_tool_uses(coord_messages, ["fetch_ci_log", "search_repo", "verify_fact"])
print(f"[coordinator] subagent tool_use blocks leaked into coordinator context: {leaked}")
assert all(v == 0 for v in leaked.values()), (
    "Context isolation broken: subagent tool_use blocks leaked into the coordinator's array."
)
print("[coordinator] context isolation verified: zero subagent tool_use blocks in coordinator history.")
"""

_subagent_debrief_md = """\
## What that printout proved

- The coordinator's `messages` array is small. It holds the user request, the coordinator's `delegate_to_subagent` calls, the subagent **final answers**, and the synthesis turn.
- Each subagent kept its own `tool_use` churn (`fetch_ci_log`, `search_repo`, `verify_fact`) inside its own `messages` array. The assertion at the end is the proof: **zero leakage** into the coordinator.
- That isolation is the feature. The coordinator stays cheap and legible; the subagents do the heavy lifting in scoped contexts with scoped tools.

**Production note:** the Claude **Agent SDK** wraps this exact pattern as `Task(subagent=..., prompt=...)`. The shape you just ran by hand is what `Task` does for you - context isolation, scoped tools, final-answer return. See `../claude-cookbooks-main/claude_agent_sdk/01_The_chief_of_staff_agent.ipynb` for the SDK version.

**This is also the pattern Segment 3's triage scorecard answer (c) refers to** ("structured claim-source mappings from subagents") - the synthesizer is the subagent, the coordinator preserves provenance.
"""

_exercise_md = """\
## Exercise (5 minutes)

On paper or in chat, sketch an agent architecture for a **Developer Productivity** scenario - an agent that triages flaky CI failures. Name:

1. The **coordinator** and its one-line job
2. **Three subagents**, each with a one-line job and a **tool scope** (which tools each subagent may call)
3. **One hook** you would add, what event it fires on, and what guarantee it enforces

Two sentences max per agent. Tim will pull one or two to discuss.
"""

_key_takeaways_md = """\
## Key takeaways

- The platform primitive is `client.messages.create` + branching on **`stop_reason`**. Everything else is layers.
- The agentic loop is a **`stop_reason` state machine**. Branch on the enum, never on the prose.
- **Hooks are the deterministic layer.** If a guarantee must hold, it lives in code, not in a prompt. The hook is the backstop, not the centerpiece.
- **Structured errors** (`errorCategory`, `isRetryable`) let the model decide to retry, reformulate, or escalate. Bare strings force it to guess.
- **Session resume vs fork** is Domain 1 vocabulary; the bare API does not give it to you, the Agent SDK does.
- **Coordinator-subagent** gives you context isolation and per-agent tool scope. Use it when subtasks have their own success criteria.
"""

_bridge_md = """\
## Bridge to Segment 2

> "You just built an agent that decides what to do. Next we go one level deeper, into the tools themselves and the Claude Code surface where you author them on a real team."

Open `segment-2-tool-design-and-mcp.ipynb`.
"""

_appendix_md = """\
## Appendix: going deeper on coordinator-subagent

You already ran a bare-API version above. The production wrapper is the Claude **Agent SDK** `Task` primitive, which packages context isolation, scoped tools, and final-answer return into one call. Canonical references:

- **Agent SDK chief-of-staff example** - `../claude-cookbooks-main/claude_agent_sdk/01_The_chief_of_staff_agent.ipynb`
- **Orchestrator-workers pattern** - `../claude-cookbooks-main/patterns/agents/orchestrator_workers.ipynb`
- **Self-study scaffold** - `../coordinator-subagent-sketch.py` (40-line conceptual outline)
- **Domain depth** - [`../domain-1-agentic.md`](../domain-1-agentic.md), the "Coordinator-subagent orchestration" section
"""
