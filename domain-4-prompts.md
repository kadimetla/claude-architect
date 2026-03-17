# Domain 1: Agentic Architecture & Orchestration (27%)

Heaviest domain. Covers how Claude agents make autonomous decisions, use tools, and coordinate with other agents.

## The Agentic Loop

Core pattern: send request, check `stop_reason`, execute tool or present response.

- `stop_reason: "tool_use"` = execute the tool, feed result back
- `stop_reason: "end_turn"` = done, present response
- Anti-patterns: parsing NL for completion, arbitrary iteration caps, checking for text content

## Multi-Agent Orchestration

- Hub-and-spoke: coordinator manages all subagent communication
- Subagents have ISOLATED context (no automatic inheritance)
- Task tool spawns subagents; coordinator `allowedTools` must include `"Task"`

## Hooks

- `PostToolUse` normalizes data before the model sees it
- Tool call interception enforces compliance (block refunds > $500)
- Hooks = deterministic guarantees. Prompts = probabilistic compliance.
