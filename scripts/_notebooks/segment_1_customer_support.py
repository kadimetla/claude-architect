"""Cell builder for segment-1-customer-support-agent.ipynb.

Teaching-first notebook for Segment 1: Building AI Agents That Use Tools.
Maps to CCA-F Domain 1 (27% exam weight).

Structure: Learning Objectives -> Concept -> Demo (Scenario A + B) ->
Exercise -> Key Takeaways -> Bridge to Segment 2 -> Appendix.
"""

from __future__ import annotations


def cells() -> list[tuple[str, str]]:
    return [
        ("md", _title_md),
        ("md", _lo_md),
        ("md", _concept_loop_md),
        ("md", _concept_stop_reason_md),
        ("md", _concept_hooks_md),
        ("md", _concept_subagents_md),
        ("md", _demo_setup_md),
        ("code", _imports_code),
        ("md", _demo_tools_md),
        ("code", _tools_code),
        ("md", _demo_synthetic_db_md),
        ("code", _synthetic_db_code),
        ("md", _demo_hook_md),
        ("code", _hook_code),
        ("md", _demo_loop_md),
        ("code", _loop_code),
        ("md", _demo_scenario_a_md),
        ("code", _scenario_a_code),
        ("md", _demo_scenario_b_md),
        ("code", _scenario_b_code),
        ("md", _hook_stress_test_md),
        ("code", _hook_stress_test_code),
        ("md", _exercise_md),
        ("md", _key_takeaways_md),
        ("md", _bridge_md),
        ("md", _appendix_md),
        ("code", _appendix_code),
    ]


_title_md = """\
# Segment 1: Building AI Agents That Use Tools

**Duration:** 50 minutes
**Maps to:** CCA-F Domain 1 (Agentic Architecture, 27% exam weight)
**Reference:** [`../domain-1-agentic.md`](../domain-1-agentic.md)

We are going to build a **customer support agent** that decides which tools to call, in what order, and when to escalate. The dramatic beat: the model will *want* to break a refund policy. A **PreToolUse hook** will say no. The agent will re-plan and escalate correctly. The guarantee comes from your code, not from begging the prompt.
"""

_lo_md = """\
## Learning objectives

By the end of this segment you will be able to:

- Explain the **agentic loop** and identify which `stop_reason` value drives each branch of the control flow
- Place **hooks** at the right lifecycle events (PreToolUse, PostToolUse) for deterministic guarantees
- Distinguish **prompt-layer guidance** from **application-layer enforcement**, and pick the right layer for a given guarantee
- Sketch a **coordinator-subagent** topology and name when it pays off vs. when it just adds latency
"""

_concept_loop_md = """\
## The agentic loop in one breath

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

_concept_hooks_md = """\
## Hooks as deterministic guarantees

A **hook** is a function that runs at a specific lifecycle event - not on the model's say-so, on your code's. The two we care about today:

- **PreToolUse** - runs *before* a tool executes. Inspect the tool name and inputs. Return `None` to allow, or return a **structured error** to block. The blocked call appends back to the conversation so the model can re-plan.
- **PostToolUse** - runs *after* a tool returns. Audit, transform, log. Never raises; log loudly, return quietly.

The rule: **anything that must hold, hook it.** Anything that should usually hold but is allowed to drift, prompt it. Confusing those two is how policy quietly evaporates.

Reference implementation lives at `../hooks-example.py`. Read it after class.
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

We will *sketch* a coordinator-subagent setup in the appendix at the end of this notebook. It uses `claude_agent_sdk.Task` rather than the bare Messages API, so we are not going to run it live. The shape is what matters.
"""

_demo_setup_md = """\
## Demo: customer support agent

We will build the agent in four moves:

1. **Tools** - four definitions whose `description` carries the contract
2. **Synthetic DB** - small Python dicts so tool execution is deterministic and cheap
3. **The hook** - a PreToolUse gate that blocks over-cap refunds
4. **The loop** - branches on `stop_reason`, dispatches tools, surfaces escalations

Then we run two scenarios: a benign happy path and a $750 refund against a $500 cap.
"""

_imports_code = """\
import json
import os
from pathlib import Path
from typing import Any

from anthropic import Anthropic

try:
    from dotenv import load_dotenv
    load_dotenv(Path.cwd().parent / ".env")
except ImportError:
    pass

assert os.environ.get("ANTHROPIC_API_KEY"), "ANTHROPIC_API_KEY is not set"

client = Anthropic()
MODEL = "claude-sonnet-4-6"
"""

_demo_tools_md = """\
## Step 1: tool definitions

Four tools. Notice the **`description`** field on `process_refund` - it spells out the $500 cap, the inputs, and what happens above the cap. Names lie. Descriptions don't.
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
        # If we got here, the hook approved it.
        return {"status": "refunded",
                "order_id": tool_input["order_id"],
                "amount_usd": tool_input["amount_usd"]}
    if tool_name == "escalate_to_human":
        return {"status": "escalated",
                "ticket_id": "ESC-9001",
                "customer_id": tool_input["customer_id"]}
    return {"error": f"unknown tool {tool_name}"}
"""

_demo_hook_md = """\
## Step 3: the PreToolUse hook

The contract from `../hooks-example.py`: return `None` to allow the call, or return a **structured error** to block it. The structured error gets appended back as a `tool_result` with `is_error=True`, and the model gets a chance to re-plan.

**The reason this is a hook and not a prompt instruction:** a refund cap is a business invariant. "Please respect the cap" works most of the time. *Most of the time* is the worst possible failure mode for policy.
"""

_hook_code = """\
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
    if tool_name != "process_refund":
        return None
    amount = tool_input.get("amount_usd", 0)
    if amount > REFUND_CAP_USD:
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
    return None
"""

_demo_loop_md = """\
## Step 4: the agentic loop

This is the centerpiece. The loop branches on `stop_reason`. For every iteration we **print the stop_reason**, so attendees see the state transitions live.

For each `tool_use` block the model emits, we:
1. Run `enforce_refund_policy` first (the **PreToolUse** gate)
2. If blocked, append the structured error as a `tool_result` with `is_error=True`
3. If allowed, dispatch the tool against the synthetic DB and append the result
4. Send the conversation back to the model and read the next `stop_reason`

The loop has a `max_iterations` ceiling. Unbounded loops are how a $5 demo becomes a $500 incident.
"""

_loop_code = """\
SYSTEM_PROMPT = (
    "You are a customer support agent for a vinyl and audio gear retailer. "
    "You have four tools. Always look up the customer and order before "
    "issuing a refund. Your refund authority is USD 500 per order; anything "
    "above that MUST be escalated via escalate_to_human. When you escalate, "
    "pass a structured summary, not the raw transcript."
)


def run_agent(user_message: str, max_iterations: int = 8) -> list[dict[str, Any]]:
    messages: list[dict[str, Any]] = [{"role": "user", "content": user_message}]
    for i in range(max_iterations):
        resp = client.messages.create(
            model=MODEL,
            max_tokens=1024,
            system=SYSTEM_PROMPT,
            tools=TOOLS,
            messages=messages,
        )
        print(f"[iter {i}] stop_reason={resp.stop_reason}")

        # Append the assistant turn verbatim
        messages.append({"role": "assistant", "content": resp.content})

        if resp.stop_reason == "end_turn":
            final_text = next(
                (b.text for b in resp.content if b.type == "text"), ""
            )
            print(f"\\n[final]\\n{final_text}")
            return messages

        if resp.stop_reason != "tool_use":
            print(f"[warn] unhandled stop_reason: {resp.stop_reason}")
            return messages

        # Handle each tool_use block
        tool_results: list[dict[str, Any]] = []
        for block in resp.content:
            if block.type != "tool_use":
                continue
            tool_name = block.name
            tool_input = dict(block.input)
            block_result = enforce_refund_policy(tool_name, tool_input)
            if block_result is not None:
                print(f"  [hook] BLOCKED {tool_name} -> {block_result['errorCategory']}")
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "is_error": True,
                    "content": json.dumps(block_result),
                })
                continue
            payload = _dispatch_tool(tool_name, tool_input)
            print(f"  [tool] {tool_name}({tool_input}) -> {payload}")
            tool_results.append({
                "type": "tool_result",
                "tool_use_id": block.id,
                "content": json.dumps(payload),
            })

        messages.append({"role": "user", "content": tool_results})

    print(f"[warn] hit max_iterations={max_iterations} without end_turn")
    return messages
"""

_demo_scenario_a_md = """\
## Scenario A: the benign happy path

A small refund within the cap. Expected trace: `tool_use -> tool_use -> tool_use -> end_turn`. The agent calls `get_customer`, then `lookup_order`, then `process_refund`, then closes.
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

_demo_scenario_b_md = """\
## Scenario B: the $750 over-cap test (defense in depth)

We try to get the model to break policy. The trick: an **aggressive system prompt** that tells it to process whatever the user demands, contradicting the cap baked into `process_refund`'s description.

What you'll see is **the model holding the line anyway**, calling `escalate_to_human` with a structured summary instead of attempting the over-cap refund. That is the **prompt + tool-description layer** doing its job.

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


def run_agent_with(system_prompt: str, user_message: str, max_iterations: int = 8):
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
            return messages
        tool_results = []
        for block in resp.content:
            if block.type != "tool_use":
                continue
            block_result = enforce_refund_policy(block.name, dict(block.input))
            if block_result is not None:
                print(f"  [hook] BLOCKED {block.name} -> {block_result['errorCategory']}")
                tool_results.append({"type": "tool_result", "tool_use_id": block.id,
                                     "is_error": True, "content": json.dumps(block_result)})
                continue
            payload = _dispatch_tool(block.name, dict(block.input))
            print(f"  [tool] {block.name}({dict(block.input)}) -> {payload}")
            tool_results.append({"type": "tool_result", "tool_use_id": block.id,
                                 "content": json.dumps(payload)})
        messages.append({"role": "user", "content": tool_results})
    return messages


print("=" * 60)
print("SCENARIO B: $750 refund demand, customer C-1099, order 4471")
print("Aggressive system prompt forces the model toward the over-cap call;")
print("the PreToolUse hook is the only thing standing in its way.")
print("=" * 60)
_ = run_agent_with(
    AGGRESSIVE_SYSTEM,
    "I'm customer C-1099. Order 4471 speakers are defective. Refund the full $750 NOW.",
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

- The agentic loop is a **`stop_reason` state machine**. Branch on the enum, never on the prose.
- **Coordinator-subagent** gives you context isolation and per-agent tool scope. Use it when subtasks have their own success criteria.
- **Hooks are the deterministic layer.** If a guarantee must hold, it lives in code, not in a prompt.
- **Structured errors** (`errorCategory`, `isRetryable`) let the model decide to retry, reformulate, or escalate. Bare strings force it to guess.
"""

_bridge_md = """\
## Bridge to Segment 2

> "You just built an agent that decides what to do. Next we go one level deeper, into the tools themselves and the Claude Code surface where you author them on a real team."

Open `segment-2-tool-design-and-mcp.ipynb`.
"""

_appendix_md = """\
## Appendix: coordinator-subagent sketch (not executed)

The bare Messages API has no `Task` primitive. The Claude **Agent SDK** does. If you want to run a coordinator-subagent topology in production, this is the shape. We are not executing it in class because it would require a second SDK install and push us over the 50-minute budget. Read it after class and pair it with `../domain-1-agentic.md`.
"""

_appendix_code = """\
# Pseudocode. Do not run. Requires `pip install claude-agent-sdk`.
#
# from claude_agent_sdk import Agent, Task
#
# coordinator = Agent(
#     name="triage-coordinator",
#     system="You are the user-facing thread. Delegate research and code "
#            "review to subagents via Task. Synthesize their final answers.",
#     tools=[escalate_to_human],
# )
#
# research_subagent = Agent(
#     name="ci-log-researcher",
#     system="Read CI logs. Return only the failing test names and the "
#            "shortest repro snippet. Do not include your own working notes.",
#     tools=[fetch_ci_log, search_repo],
# )
#
# # Inside the coordinator's loop:
# subagent_result = Task(
#     subagent=research_subagent,
#     prompt="Investigate why the nightly job has been flaky for 48 hours."
# ).run()
#
# # subagent_result is the subagent's FINAL ANSWER only.
# # Its working context never enters the coordinator's window.

print("Appendix is reference only. See ../domain-1-agentic.md for depth.")
"""
