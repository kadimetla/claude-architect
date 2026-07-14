# Domain 1: Agentic Architecture & Orchestration

> Reference scaffold - maps to **COURSE-FLOW.md Segment 1**

## What this domain covers

This domain is the load-bearing wall of the **CCA-F** skill set. You learn to design **agentic loops** that drive a model through repeated tool calls until a task is genuinely done, not just narratively concluded. You build **coordinator-subagent** systems where an orchestrator delegates to specialists with **isolated contexts**. You wire up **hooks** that turn fuzzy policy into deterministic, code-enforced guarantees. You manage **session state**, knowing when to resume a thread and when to fork. And you decompose tasks at the right altitude, leaving room for the agent to reason without micromanaging every step. Skills first. The exam will catch up.

## Core concepts

### The agentic loop and `stop_reason`

The agentic loop is the heartbeat of every Claude agent. Pattern: send messages to the API, receive an assistant turn containing one or more **content blocks**, inspect the response's `stop_reason`, then decide what to do next. If `stop_reason` is `tool_use`, you execute each tool, append a `tool_result` block for each call, and send the conversation back. If it is `end_turn`, the turn is genuinely complete. The full enumeration: `end_turn`, `max_tokens`, `stop_sequence`, `tool_use`, `pause_turn` (resumable long-running turns), and `refusal` (streaming policy intervention). **Hard rule:** never parse natural language to decide whether the agent is finished. "All done!" in prose means nothing. The API is the source of truth. Check `stop_reason`, always.

### Coordinator-subagent orchestration

A **coordinator** (sometimes called orchestrator or chief-of-staff) holds the broad task context and decides which **specialist subagent** to invoke for each subproblem. Subagents are spawned via the **Task tool** in Claude Code or via Agent SDK task invocations, and each one runs in its own **isolated conversation**, with its own tool allowlist and its own message history. The coordinator hands the subagent a focused brief, the subagent executes, and a **structured result** comes back. The parent merges those results into its own reasoning trace. The anti-pattern is daisy-chaining the full conversation log from one subagent to the next. Token costs scale superlinearly, signal-to-noise collapses, and the model loses the plot. Anthropic's **chief-of-staff agent pattern** is the canonical reference.

### Hooks as deterministic guarantees

Hooks are the architectural answer to "the model is non-deterministic, but I need a guarantee." They fire on lifecycle events: **PreToolUse** (before any tool call), **PostToolUse** (after), **SessionStart**, and **Stop**. They live in `settings.json` as a matcher plus a command:

```json
{"hooks": {"PreToolUse": [{"matcher": "Bash", "hooks": [{"type": "command", "command": "~/.claude/hooks/filter.sh"}]}]}}
```

Use case: a refund above $500 must be blocked, regardless of how persuasive the customer is or how creative the model gets. A prompt instruction can be ignored, paraphrased, or jailbroken. A **PreToolUse hook** that inspects the tool input and exits non-zero cannot. Prompts are suggestions. Hooks are contracts. If a rule must hold for compliance, safety, or money, write the hook.

### Session state, resumption, forking

Sessions persist. You can **resume** a previous conversation to continue work, or **fork** it to branch into a parallel exploration. Resume when you are picking up where you left off and the world has not meaningfully changed. Fork when you want to test two refactoring approaches, two prompt variants, or two architectural directions without cross-contaminating context. The classic gotcha lives in **asynchronous resumption**: the model reads yesterday's `tool_result` blocks, treats them as current, and confidently reports stale status. Fix: filter old `tool_result` blocks out of the resumed transcript so the agent is forced to re-fetch live data. Resume with intent. If files moved, tell the agent which ones.

### Task decomposition

Decomposition is a design call, not a default. Sometimes the agent is better off receiving a single high-level goal and figuring out the substeps itself. Sometimes the orchestrator should pre-plan and dispatch discrete subtasks. The split usually lives in the orchestrator's system prompt or in a dedicated planning step before any tool calls fire. The failure mode to avoid is **over-decomposition**: rigid procedural scripts handed to subagents brittle out the moment the environment shifts or a new topic emerges. **Goal-oriented delegation beats procedural micromanagement.** Tell the subagent what success looks like and which tools it has. Trust it to navigate.

## Demo anchor

See **COURSE-FLOW.md Segment 1** for the live build, which is taught from [`segment-1-customer-support-agent.ipynb`](../notebooks/segment-1-customer-support-agent.ipynb). Code references:

- `../claude-cookbooks-main/tool_use/customer_service_agent.ipynb` - primary demo anchor (4 tools, hook-enforced policy)
- `../claude-cookbooks-main/claude_agent_sdk/01_The_chief_of_staff_agent.ipynb` - coordinator-subagent example
- `../claude-cookbooks-main/patterns/agents/orchestrator_workers.ipynb` - orchestration patterns
- `../claude-cookbooks-main/managed_agents/CMA_coordinate_specialist_team.ipynb` - specialist team coordination
- `../hooks-example.py` - Tim's `enforce_refund_policy` hook ($500 cap)
- `../coordinator-subagent-sketch.py` - coordinator-subagent scaffold (read-only reference)

### Before the loop: the Messages API primitive

If the raw `messages.create()` call still feels like magic, start at [`examples/messages_api/`](../examples/messages_api/). Ten short notebooks build the primitive the agentic loop wraps: [`001_requests.ipynb`](../examples/messages_api/001_requests.ipynb) is a single round trip, [`multi_turn_conversation.ipynb`](../examples/messages_api/multi_turn_conversation.ipynb) is the same call with an accumulating `messages` list, and that accumulation **is** the loop once you branch on `stop_reason`. Everything Domain 1 teaches sits one layer above these files.

### The other half of the loop: let Anthropic host it

Everything above is the **hand-rolled** loop, where your code owns the while-loop and the `stop_reason` branch. The **Managed Agents API** hosts that same loop server-side, and two notebooks in [`examples/agents_api/`](../examples/agents_api/) are the Domain 1 counterparts:

- [`01_agentic_loop_and_sessions.ipynb`](../examples/agents_api/01_agentic_loop_and_sessions.ipynb) - the create, send, stream, idle, teardown spine, plus server-side **session** memory across turns. Compare its idle event to the `stop_reason` branch you write by hand.
- [`02_coordinator_and_subagents.ipynb`](../examples/agents_api/02_coordinator_and_subagents.ipynb) - a coordinator with `multiagent` config delegating to specialists, which is the same isolated-context orchestration this domain teaches, minus the plumbing.

Both notebooks archive their resources in a teardown cell. A live session is a billable runtime, so run that cell.

### Task-statement coverage

[`notebooks/cca-f-exam-mastery.ipynb`](../notebooks/cca-f-exam-mastery.ipynb) **Part 1** maps all seven Domain 1 task statements (TS1.1 through TS1.7) to runnable minimal demos: the `stop_reason` state machine, prompt chaining versus dynamic decomposition, hub-and-spoke coordination, hooks as guarantees, the Task tool, and session resume versus fork. It creates no billable resources, so it's the cheapest way to rehearse this domain cold.

## Production tips (Tim's voice)

- **Check `stop_reason`, not vibes.** The model saying "I'm done!" in natural language is meaningless. The API tells you when it's done. Believe the API.
- **Hooks are your contract with reality.** If a rule MUST hold, encode it as a hook. Prompts are suggestions. Hooks are guarantees.
- **Isolated subagent contexts are a feature, not a limitation.** Don't try to give every subagent the parent's full history. They don't need it. Pass a structured brief, get a structured result.
- **Fork when you'd otherwise pollute context.** A/B exploration of two architectures in one thread confuses the model. Fork the session, run them independently, compare results.
- **Resume sessions with intent.** If files changed since the last session, tell the agent which ones changed. Don't pretend nothing happened.

## Further reading

- Anthropic: stop_reason semantics - https://docs.claude.com/en/api/messages (search for stop_reason)
- Anthropic: Claude Agent SDK - https://docs.claude.com/en/agent-sdk
- Claude Code hooks - https://docs.claude.com/en/docs/claude-code/hooks
- `../claude-cookbooks-main/claude_agent_sdk/` - full agent SDK cookbook (8 notebooks covering chief-of-staff, observability, SRE, vulnerability-detection patterns)
- `../claude-cookbooks-main/managed_agents/` - managed agent examples

Next Best Steps:
1) Validate the referenced cookbook paths under `../claude-cookbooks-main/` and the local `hooks-example.py` actually exist so learners don't hit broken links.
2) Mirror this scaffold structure into `domain-2-*.md` through `domain-5-*.md` so the post-course reference set has consistent shape across all five CCA-F domains.
3) Cross-link this file from `COURSE-FLOW.md` Segment 1 and from any top-level `README.md` study path so learners can navigate from course flow to domain reference without hunting.
