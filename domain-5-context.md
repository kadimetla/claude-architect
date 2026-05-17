# Domain 5: Context Management & Reliability

> Reference scaffold, maps to **COURSE-FLOW.md Segment 4**

## What this domain covers

**Context management** and **reliability** are the disciplines that keep agents useful past turn 10. This domain covers six load-bearing topics:

- **Context preservation** across long, multi-issue interactions
- **Escalation design** that distinguishes "I need a human" from "I'm annoyed"
- **Error propagation** in multi-agent systems where subagents fail silently
- **Context management in large codebases** where naive file reads burn the window
- **Human review workflows** with confidence calibration per document type
- **Provenance and source attribution** when synthesis agents combine multiple subagent outputs

If Domains 1 through 4 teach you how to build an agent that works once, Domain 5 teaches you how to build one that works on turn 48 in production.

## Core concepts

### Context preservation across long interactions

Picture a **48-turn customer support session**. The customer started with a refund, drifted into a subscription question, and ended on a payment-method update. The context window is full of resolved noise. The model is now spending tokens re-reading old turns instead of solving the active issue.

The pattern that scales:

- **Case-facts block at the top.** Customer ID, account status, current SLA tier, language preference. Pinned at every turn. This is your stable cache prefix, mark it with `{"cache_control": {"type": "ephemeral", "ttl": "1h"}}` so you stop paying full token cost.
- **Summarize resolved turns into narrative.** "Earlier in this session, the refund for order #847 was processed. The subscription question was resolved by routing to billing." One sentence replaces twelve turns.
- **Keep full verbatim history ONLY for the active, unresolved issue.** Resolved means resolved. Stop carrying it.
- **Prune verbose tool outputs.** A raw API response with 40 fields where you used 5 is 35 fields of context tax. Filter the `tool_result` content application-side before adding it to the conversation.

Tool context pruning is **application-side**, the model cannot do it for you. Reference `automatic-context-compaction.ipynb` for a worked example.

### Escalation design

Three escalation patterns, in priority order:

1. **Immediate escalation on explicit request.** "I want a human NOW." Honor it. Do not ask for clarification first. Do not try one more thing. Do not run a diagnostic tool. The customer has spoken. Route the call.
2. **Complex policy escalation.** Before handing off, ensure account-context tools are called and pass a **structured summary** to the human queue: customer ID, root cause, dollar amount, recommended action. Not the raw transcript. A human reading 48 turns to find the issue is a worse outcome than the bot trying one more time.
3. **Confidence-based escalation.** Model outputs a confidence score, low-confidence outputs route to review. This requires per-segment calibration (see Human review workflows below).

**Anti-pattern: escalating on sentiment alone.** Frustration is not complexity. A frustrated customer with a simple refund request does not need a human, they need the refund processed in two seconds. A calm customer with a billing dispute that spans three accounts and two billing cycles absolutely does need a human. Route on **problem shape**, not on **emotional temperature**.

### Error propagation in multi-agent systems

Subagents fail. The only real question is whether the parent agent knows about it. Patterns that hold up in production:

- **Subagents return structured error context.** `{"status": "failed", "errorCategory": "transient", "retryAdvice": "exponential backoff, max 3"}`. Never silently return an empty result. Empty results look like "no data found" to the parent, which is a completely different decision branch.
- **Parent decides the recovery path.** Retry the same subagent, fall back to an alternate subagent, or escalate to a human. The parent owns the policy, not the child.
- **Never swallow exceptions.** A Python `except Exception: pass` inside a tool implementation hides real failures from the model. The model then confidently asserts something false because its tool "succeeded."
- **Tool errors belong in `tool_result` content,** not as raised exceptions. The Anthropic-recommended shape is `{"type": "tool_result", "tool_use_id": "...", "content": "Database unreachable", "is_error": true}`. Add an `errorCategory` field so the model can decide whether to retry.

The distinction that matters: **application exceptions crash the agent. Structured tool errors let it recover.** Pick the second one every time.

### Context management in large codebases

Two failure modes dominate when agents work in repos:

- **Sequential file reads.** The agent uses the Read tool to load file after file, thousands of lines of unrelated code, until the window is 80% noise. By the time it finds the function it wanted, it has no room left to reason about the change.
- **Repetitive lookups.** Calling `lookup_order` twelve times for twelve related orders fills the window with twelve verbose responses, eleven of which contain the same metadata.

Fixes that work:

- **Start broad, then pinpoint.** Read `CLAUDE.md` and `README.md` first. Then ask the human for priority files. Do not boil the ocean.
- **Use the scratchpad pattern.** Have the agent maintain a `.scratchpad.md` with key findings, architectural maps, decisions made. Reference the scratchpad instead of re-reading source files. It compresses 4,000 lines of code into 200 lines of conclusions.
- **Application-side filtering.** Extract only the fields you need from each tool response. Drop the rest before the next turn. The model never needs to see the `createdAt`, `updatedAt`, `_etag`, and `_internalAuditTrail` fields to answer a refund question.
- **Compaction events.** When context approaches the limit, the agent receives a summary and continues with reduced history. A `pause_turn` stop reason is the model telling you it needs a break, you can resume by passing the response back in a subsequent request.

### Human review workflows and confidence calibration

Confidence routing in three tiers:

- **High (>90%):** automated downstream processing, no human in the loop
- **Medium (70 to 90%):** spot-check a sample, audit weekly
- **Low (<70%):** human review queue, mandatory

The critical move: **analyze accuracy by document type and field before trusting aggregate confidence.** A model that scores 95% accurate overall might be 60% accurate on multi-page contracts, or 50% on handwritten invoices, or 99% on standardized W-2s. Aggregate confidence hides the failure modes that matter.

Calibrate **per-segment**, not per-corpus. Build a confusion matrix by document type. Reference `managed_agents/CMA_gate_human_in_the_loop.ipynb` for the gating pattern.

### Provenance and source attribution

When synthesis agents combine outputs from multiple subagents, the financial agent, the news agent, the legal agent, they MUST preserve **claim to source** mappings. The pattern:

- Each subagent returns `{"claim": "...", "evidence": "...", "source": "...", "confidence": "..."}`
- The synthesis agent is instructed to keep the source field for every claim it surfaces in the final output
- For dated information: include publication dates so the synthesis can flag stale data ("This filing is from Q2 2023, current as of...")

**Anti-pattern:** a synthesis agent that outputs polished prose without attribution. Sources get lost in translation, claims become unverifiable, and the human reviewer has no way to audit the chain. Treat **attribution as a required output field**, not an optional nicety. No source, no claim. Period.

## Demo anchor

The two load-bearing Domain 5 concepts (case-facts pinning + tool-output pruning, and escalation triage) are taught live in **COURSE-FLOW.md Segment 3** alongside Domain 4. The compaction demo is **post-class self-study**, not a live segment. The Segment 4 capstone is the CCA-F cert briefing + practice questions; see [`./CERT-PROGRAM-BRIEFING.md`](./CERT-PROGRAM-BRIEFING.md). Code references:

- `private/claude-cookbooks-main/tool_use/automatic-context-compaction.ipynb`, self-study lab (run after class)
- `private/claude-cookbooks-main/tool_use/memory_cookbook.ipynb`, memory and recall patterns
- `private/claude-cookbooks-main/managed_agents/CMA_gate_human_in_the_loop.ipynb`, human review gating
- `private/claude-cookbooks-main/managed_agents/CMA_remember_user_preferences.ipynb`, preference persistence
- `private/claude-cookbooks-main/claude_agent_sdk/02_The_observability_agent.ipynb`, observability for production agents
- `private/claude-cookbooks-main/claude_agent_sdk/03_The_site_reliability_agent.ipynb`, SRE patterns

## Production tips (Tim's voice)

- **Case facts at the top, full history only for the active issue.** This is how lawyers manage case files. Apply the same discipline to long agent sessions.
- **Honor explicit escalation requests immediately.** "I want a human" is not a request for diagnostics. It is a command.
- **Sentiment is not complexity.** A frustrated user with a $5 refund does not need a human. A calm user with a multi-account billing dispute does.
- **Subagents that swallow errors are saboteurs.** Structured error context is non-negotiable.
- **Scratchpad files beat re-reading source.** In long exploration sessions, the agent should maintain its own dense reference doc.
- **Provenance is a required output field, not a nicety.** No source, no claim. Period.

## Further reading

- Anthropic: Context management, https://docs.claude.com/en/docs/build-with-claude/context-windows
- Anthropic: Prompt caching, https://docs.claude.com/en/docs/build-with-claude/prompt-caching
- Anthropic: Memory tool, https://docs.claude.com/en/docs/agents-and-tools/tool-use/memory-tool
- `private/claude-cookbooks-main/claude_agent_sdk/`, 8 production agent notebooks with reliability patterns
- `private/claude-cookbooks-main/managed_agents/`, managed agent reliability examples
