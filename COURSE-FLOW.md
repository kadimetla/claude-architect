# Claude Architect Foundations - Course Flow

The 4-hour instructor punchlist for the O'Reilly live training. Skills-first, demo-heavy, production-grounded.

## Course at a glance

| Segment | Duration | Topic | Key Deliverable |
|---------|----------|-------|-----------------|
| 1 | 50 min | Building AI Agents That Use Tools | A customer support agent with hook-enforced policy |
| 2 | 50 min | Tool Design, Integration, and Claude Code Workflows | An audited MCP + CLAUDE.md project configuration |
| 3 | 50 min | Prompt Engineering and Structured Output | An invoice extractor with schema validation and retry |
| 4 | 50 min | Context Management, Reliability, and Production Strategy | A production reliability triage scorecard |

**Total class time:** 4 hours (4 x 50-min segments + 3 x 10-min breaks).

**Pre-class verification:** [`./PRE-CLASS-CHECKLIST.md`](./PRE-CLASS-CHECKLIST.md). Run it the day before. Don't skip it.

## Course roadmap

We move outside-in. **Segment 1** builds an **agent** that decides what to do. **Segment 2** drops down into the **tools** that agent uses, and the Claude Code surface where you author them on a real team. **Segment 3** tightens what comes out, with **prompts** and **structured output schemas** that don't lie. **Segment 4** answers the production question: when context windows fill and one bad tool result poisons the chain, what holds the system together.

## Prerequisites

Run [`./PRE-CLASS-CHECKLIST.md`](./PRE-CLASS-CHECKLIST.md) end-to-end before class. The short version:

- **Python 3.13** with `pip` on PATH
- **Node.js 18+** (needed for `npx @modelcontextprotocol/inspector` and a few MCP servers)
- **Claude Code CLI** installed (`npm i -g @anthropic-ai/claude-code` or the official installer)
- **`ANTHROPIC_API_KEY`** environment variable set in the same shell you'll run demos from
- **VS Code** with the **Python** and **Jupyter** extensions
- This repo cloned to `C:/github/claude-architect`, with `private/claude-cookbooks-main` already pulled

If any of those fail, fix them before segment 1. We will not pause class to install Node.

---

## Segment 1 - Building AI Agents That Use Tools

**Duration:** 50 minutes (40 content + 5 exercise + 5 Q&A)
**Maps to:** Domain 1 (Reference: [`./domain-1-agentic.md`](./domain-1-agentic.md))

### Learning objectives

By the end of this segment, attendees will be able to:

- Explain the **agentic loop** and identify which `stop_reason` value drives each branch of the control flow
- Design a **coordinator-subagent** topology with isolated subagent contexts via the Task tool
- Place **hooks** at the right lifecycle events (PreToolUse, PostToolUse, SessionStart, Stop) for deterministic guarantees
- Distinguish **prompt-layer guidance** from **application-layer enforcement**, and pick the right layer for a given guarantee

### Topics covered

1. **The agentic loop lifecycle and the `stop_reason` decision tree** (10 minutes)
   - The loop in one breath: model emits content + `stop_reason` -> your code reads `stop_reason` -> you either return to user, execute tools and append `tool_result`, or resume a paused turn.
   - The six `stop_reason` values from the Messages API:
     - `end_turn` - model reached a natural stopping point
     - `max_tokens` - hit the token cap, output may be truncated
     - `stop_sequence` - a custom stop_sequence was generated
     - `tool_use` - model invoked one or more tools, you must execute and return `tool_result`
     - `pause_turn` - long-running turn was paused, resume in the next request
     - `refusal` - streaming classifier intervened on policy
   - **Anti-pattern callout:** Never parse natural language to detect completion. Always branch on `stop_reason`. "It said thanks, so I assume it's done" is how production agents go feral.

2. **Multi-agent orchestration: coordinator-subagent** (10 minutes)
   - One **coordinator** holds the user-facing thread. **Subagents** get isolated contexts via the Task tool so the parent doesn't drown in their working notes.
   - In the `claude_agent_sdk`, the `Task` invocation pattern returns only the subagent's final answer to the parent. That isolation is the feature, not a limitation.
   - **When to split:** a subtask has its own success criteria, its own tool subset, and you don't want its intermediate reasoning polluting the main context. Research, code review, and triage are textbook fits.
   - **Anti-pattern callout:** Don't split for splitting's sake. Two coordinators chatting is just one slow agent with extra latency.

3. **Hooks as deterministic guarantees** (5 minutes)
   - **Events:** `PreToolUse` (gate a call before it runs), `PostToolUse` (audit, transform, log), `SessionStart` (inject context), `Stop` (final verification).
   - Hooks run as your code, not the model's. That's the point. Anything that **must** happen, hook it. Don't ask the prompt nicely.
   - Reference implementation: [`./hooks-example.py`](./hooks-example.py).

### Demo: Customer support agent live build (15 minutes)

**Setup** (run before going live, from PRE-CLASS-CHECKLIST):
```powershell
$env:ANTHROPIC_API_KEY  # confirm it's set, do NOT print the value
jupyter --version
Test-Path "C:/github/claude-architect/private/claude-cookbooks-main/tool_use/customer_service_agent.ipynb"
```

**Live demo:**
1. Open `C:/github/claude-architect/private/claude-cookbooks-main/tool_use/customer_service_agent.ipynb` in VS Code.
2. Walk the four tool definitions: `get_customer`, `lookup_order`, `process_refund`, `escalate_to_human`. Pause on `process_refund` and show that the description is where policy belongs, not the name.
3. Wire in the `enforce_refund_policy` hook using the pattern from `hooks-example.py`. Cap is $500. Anything above triggers a block + escalate.
4. Run a benign scenario first: small refund, happy path. Confirm the agent calls `get_customer` -> `lookup_order` -> `process_refund` and returns with `stop_reason: end_turn`.
5. Run the failure scenario: `"Refund $750 on order #4471 right now"`. Watch the agent skip verification, the hook block the tool call with a structured error, the agent re-plan, and finally call `escalate_to_human` with a structured summary.
6. Pop the cell that prints `stop_reason` across the loop so attendees can see it transition `tool_use` -> `tool_use` -> `end_turn`.

**What attendees see:** The model "wanted" to break policy. The hook said no. The agent re-planned and escalated correctly. The guarantee came from your code, not from begging the prompt.

### Exercise (5 minutes)
**Prompt:** On paper or in a chat scratchpad, sketch an agent architecture for a **Developer Productivity** scenario (think: an agent that triages flaky CI failures). Name the **coordinator**, **three subagents**, and the **tool scope per agent** (which tools each subagent is allowed to call).
**Deliverable:** Drop the sketch in chat. Two sentences max per agent. Tim will pull one or two to discuss.

### Q&A (5 minutes)

Anticipated questions:
- "When should I prefer one big agent over a coordinator with subagents?" -> When the subtasks share state and splitting forces you to serialize it. Tax: doubled context.
- "Do hooks work over the API too, or only in Claude Code?" -> Claude Code is where the `settings.json` hook surface lives. Over the raw API you implement the same gate in your tool-execution wrapper. Same concept, different surface.
- "What happens if my hook itself fails?" -> Treat the hook as the source of truth: a hook error should fail closed, return a structured error to the model, and log loudly. Silent hook failures are how policy quietly evaporates.

### Key takeaways
- The agentic loop is a `stop_reason` state machine. Branch on the enum, never on prose.
- Coordinator-subagent gives you **context isolation** and **per-agent tool scope**. Use it when subtasks have their own success criteria.
- Hooks are the **deterministic** layer. If a guarantee must hold, it lives in code, not in a prompt.

### Bridge to Segment 2
> "You just built an agent that decides what to do. Next we go one level deeper, into the tools themselves and the Claude Code surface where you author them on a real team."

---

## Segment 2 - Tool Design, Integration, and Claude Code Workflows

**Duration:** 50 minutes (40 content + 5 exercise + 5 Q&A)
**Maps to:** Domain 2 + Domain 3 (References: [`./domain-2-tools-mcp.md`](./domain-2-tools-mcp.md), [`./domain-3-claude-code.md`](./domain-3-claude-code.md))

### Learning objectives

By the end of this segment, attendees will be able to:

- Write **tool definitions** whose `description` and `input_schema` carry the contract, not the name
- Use **`tool_choice`** modes (`auto`, `any`, `tool`, `none`) to constrain agent behavior
- Configure **`.mcp.json`** for stdio, SSE, and HTTP transports with `${ENV_VAR}` expansion
- Lay out a **CLAUDE.md hierarchy** (user, project, subtree, local) and reason about precedence
- Run Claude Code **non-interactively** with `claude -p` for CI/CD scenarios

### Topics covered

1. **Tool descriptions beat tool names; structured errors** (10 minutes)
   - The tool definition shape per the Messages API: `name`, `description`, `input_schema` (JSON Schema draft 2020-12), optional `cache_control` with `ephemeral` + `ttl: "5m"` or `"1h"`.
   - **The description is the contract.** Spell out what the tool does, when to call it, when **not** to call it, what the inputs mean, and what the success/failure shapes look like. Names lie; descriptions don't.
   - **Structured error pattern** in the `tool_result` content:
     ```json
     {"isError": true, "errorCategory": "transient|permanent|policy", "isRetryable": true, "message": "..."}
     ```
   - The model uses `errorCategory` and `isRetryable` to decide whether to retry, reformulate, or escalate. Returning a bare string forces the model to guess.

2. **Scoped tool distribution and `tool_choice`** (5 minutes)
   - The four `tool_choice` modes:
     - `{"type": "auto"}` - model decides, supports `disable_parallel_tool_use`
     - `{"type": "any"}` - must call some tool
     - `{"type": "tool", "name": "<tool_name>"}` - must call this specific tool (this is the lever for **forced structured output**, more in Segment 3)
     - `{"type": "none"}` - no tools allowed this turn
   - Set `disable_parallel_tool_use: true` when ordering matters or when one tool's output feeds the next.

3. **MCP server config: `.mcp.json` vs `~/.claude.json`** (5 minutes)
   - Root key is `mcpServers`. Each server is one of three transports:
     - **stdio:** `{"command": "npx", "args": [...], "env": {"VAR": "${VAR}"}}`
     - **SSE:** `{"type": "sse", "url": "https://...", "headers": {"Authorization": "Bearer ${API_TOKEN}"}}`
     - **HTTP:** `{"type": "http", "url": "...", "headers": {...}}`
   - **`${ENV_VAR}` expansion** works in `env`, `args`, and `headers`. Recent change per the Claude Code changelog. Use it. Never commit literal secrets.

### Demo A: MCP config walkthrough (10 minutes)

**Live demo:**
1. Open `C:/github/claude-architect/.mcp.json` in VS Code. This is a real project-level config shipping with this repo.
2. Walk the `mcpServers` object server-by-server. Four servers, three transports: **filesystem** (stdio, no auth), **github** (stdio with `${GITHUB_TOKEN}`), **context7** (HTTP with header auth), **internal-knowledge-base** (SSE with bearer token). For each, name the **transport**, the **command or URL**, and the **env-var expansion** points.
3. Show what happens when `${GITHUB_TOKEN}` is unset: server fails to start with a readable error. Set it, restart, server comes up.
4. Toggle a server off by commenting its block; show the model losing access to those tools at the next session boundary.
5. Optional side-trip: open `private/claude-cookbooks-main/managed_agents/cma-mcp/` to show what an MCP server's source code looks like (vs. the client config we just walked). Two sides of the same protocol.

**What attendees see:** MCP config is plain JSON with three transport shapes and one variable-expansion rule. The hard part isn't the syntax, it's deciding which tools each agent should see.

4. **Claude Code instruction hierarchy** (5 minutes)
   - The four CLAUDE.md tiers, in precedence order:
     - **User:** `~/.claude/CLAUDE.md` - your personal defaults, every project
     - **Project:** `./CLAUDE.md` at the repo root - team conventions, checked in
     - **Subtree:** `<subdir>/CLAUDE.md` - loaded on demand when files in that subdir are read
     - **Local override:** `CLAUDE.local.md` - gitignored, personal repo-specific tweaks
   - Agent SDK loads both with `settingSources: ["user", "project"]`.
   - Path-specific rules go in `.claude/rules/` with `paths:` globs so a frontend rule doesn't pollute a backend file.
   - **Plan mode** (Shift+Tab cycle) for exploration. **`claude -p`** for non-interactive headless runs - this is your CI/CD answer.

### Demo B: CLAUDE.md hierarchy audit (5 minutes)

**Live demo:**
1. Open `C:/github/claude-architect/CLAUDE.md` in VS Code. Walk the structure.
2. Show a nested CLAUDE.md if one exists; explain that it only loads when files in that subtree are read.
3. In PowerShell, run:
   ```powershell
   claude -p "audit this CLAUDE.md against repo conventions. List 3 specific improvements."
   ```
4. Show the JSON output mode for scripting:
   ```powershell
   claude -p "list all Python files with missing docstrings" --output-format json
   ```

**What attendees see:** The same Claude Code you use interactively is a CLI tool you can pipe to. `claude -p` is the bridge to GitHub Actions.

### Exercise (5 minutes)
**Prompt:** Sketch a **CLAUDE.md hierarchy for a 3-team monorepo** (backend / frontend / infra). Name **three files**: one project-root `CLAUDE.md` and two subtree `CLAUDE.md` files. For each, write a one-line statement of what belongs there and what does **not**.
**Deliverable:** Three file paths plus three one-liners in chat.

### Q&A (5 minutes)

Anticipated questions:
- "Can I put secrets in `.mcp.json`?" -> No. Use `${ENV_VAR}` and source them from your shell or a secrets manager. The file is checked in; the env vars aren't.
- "What loads first, user or project CLAUDE.md?" -> Both load, with project conventions overriding user defaults where they conflict. Keep user-level rules generic; put team-specific stuff in project.
- "When do I prefer `tool_choice: any` over `auto`?" -> When you must guarantee a tool call this turn, usually for structured output enforcement or a forced classification step.

### Key takeaways
- **Tool descriptions are the contract**, names are just labels. Spell out behavior, inputs, and error shapes.
- **MCP transports** are stdio / SSE / HTTP, and `${ENV_VAR}` expansion keeps secrets out of source.
- **CLAUDE.md hierarchy** layers from user to project to subtree to local. Use subtree files to keep frontend rules off backend files.

### Bridge to Segment 3
> "Tools give the agent hands. Prompts and schemas decide what comes out. Let's make those outputs trustworthy."

---

## Segment 3 - Prompt Engineering and Structured Output

**Duration:** 50 minutes (40 content + 5 exercise + 5 Q&A)
**Maps to:** Domain 4 (Reference: [`./domain-4-prompts.md`](./domain-4-prompts.md))

### Learning objectives

By the end of this segment, attendees will be able to:

- Write **precise prompts** that specify format, edge cases, and missing-data behavior up front
- Use the **forced-tool-call pattern** to enforce a Pydantic-derived JSON schema on model output
- Build a **validation + retry loop** that surfaces the error back to the model on `ValidationError`
- Distinguish failures that **retries fix** (format, parse, schema) from failures that **retries don't fix** (knowledge gaps, ambiguous source data)

### Topics covered

1. **Precise prompts: explicit criteria and few-shot** (8 minutes)
   - Be explicit about: **format**, **edge cases**, **what to do if a field is missing**, **what to do if multiple interpretations exist**. The model will pick reasonable defaults; reasonable defaults are not your defaults.
   - **Two or three input-output examples** beat almost any temperature change. Few-shot pins behavior more reliably than instructions.
   - **Anti-pattern callout:** "Be accurate" is not a prompt. It's a wish. Replace with a checklist of acceptance criteria.

2. **JSON schema enforcement via tool use** (7 minutes)
   - The pattern: define a **Pydantic model** -> convert to **JSON Schema** (Pydantic does this for free) -> register as a tool's `input_schema` -> set `tool_choice: {"type": "tool", "name": "<schema_tool>"}` -> the model must return data matching the schema.
   - `strict: true` parameter enforces schema validation at the API boundary, so you fail fast on the rare cases where the model tries to drift.
   - This is the canonical way to get **typed output** out of Claude. No regex, no JSON repair libraries, no praying.

3. **Validation and retry loops; when retries do and don't help** (5 minutes)
   - **Retries help when:** format errors, JSON parse failures, schema mismatches, missing required fields. The model often "knew" the answer and just got the shape wrong.
   - **Retries don't help when:** knowledge gaps, genuinely ambiguous source data, hallucinated citations ("et al." with no real source). Looping just burns tokens.
   - **The pattern:** on `ValidationError`, append the error string back as a user turn ("Your previous response failed validation: X. Return only valid JSON matching the schema."), retry **once**, then escalate.

### Demo: Invoice extractor live build (20 minutes)

**Live demo:**
1. Open `C:/github/claude-architect/private/claude-cookbooks-main/tool_use/extracting_structured_json.ipynb` and `tool_use_with_pydantic.ipynb` side by side.
2. Build a Pydantic `Invoice` model with required fields (`invoice_number`, `vendor`, `total`) and `Optional[]` fields (`po_number`, `notes`, `due_date`). Show the auto-generated JSON Schema.
3. Register the schema as a tool. Set `tool_choice: {"type": "tool", "name": "extract_invoice"}`. Model **must** call this tool.
4. Run on three sample invoices in order:
   - **Clean invoice:** all fields present. Schema validates first try. Show the typed `Invoice` object.
   - **Missing one field:** no PO number. The `Optional[str]` field comes back `None`. No retry needed. Schema is doing the work.
   - **Ambiguous line item:** a hand-written charge that could be parsed two ways. First pass fails validation. Catch the `ValidationError`. Append the error back as a user turn. Retry. Second pass succeeds.
5. Show the loop ceiling: hard-code `max_retries = 1`. Demonstrate that without the ceiling, a genuinely bad source document burns 20 calls in a row.

**What attendees see:** Structured output isn't magic. It's a tool definition, a forced `tool_choice`, and a small validation loop with a ceiling. Once you wire it once, you copy the pattern.

### Exercise (5 minutes)
**Prompt:** Design a Pydantic schema for an **extraction task of your choice** (resume parser, expense report, support ticket - dealer's choice). Use **`Optional[]`** for nullable fields. Use **`Literal["high","medium","low"]`** for a `confidence` field so the model is forced to self-report when it's guessing.
**Deliverable:** Paste the Pydantic class in chat. Five fields minimum, at least one Optional, at least one Literal.

### Q&A (5 minutes)

Anticipated questions:
- "Can I use this for arbitrarily nested schemas?" -> Yes, Pydantic handles nesting and JSON Schema handles nesting. The model handles 2-3 levels well. Past that, split into two extraction calls.
- "What about streaming structured output?" -> You can stream the tool_use deltas, but you validate at the end. Don't try to parse partial JSON.
- "When should I prefer a regex over schema extraction?" -> When the format is deterministic (phone numbers, ISO dates). Don't pay the model to do what `re` does in microseconds.

### Key takeaways
- **Precise prompts plus few-shot** beat temperature tuning every time.
- **Forced tool calls + Pydantic schemas** are the canonical structured output pattern.
- **Retry once on validation errors**, escalate on knowledge gaps. Loops without ceilings burn tokens and your goodwill.

### Bridge to Segment 4
> "We have agents, tools, prompts. Production is where context windows fill up and one bad tool result poisons the chain. Last segment is about not breaking when scale arrives."

---

## Segment 4 - Context Management, Reliability, and Production Strategy

**Duration:** 50 minutes (40 content + 5 exercise + 5 Q&A)
**Maps to:** Domain 5 (Reference: [`./domain-5-context.md`](./domain-5-context.md))

### Learning objectives

By the end of this segment, attendees will be able to:

- Preserve **case facts** and prune **verbose tool outputs** so long conversations stay coherent
- Distinguish **explicit human requests** (escalate now) from **sentiment signals** (don't escalate on frustration alone)
- Design **error propagation** so subagents return structured context and the coordinator decides retry / fail / escalate
- Preserve **provenance** in synthesis tasks so every claim ties back to a source

### Topics covered

1. **Context preservation across long interactions** (8 minutes)
   - **Case-facts block at the top.** Pin the unchanging context (account ID, product, environment) at the start of the conversation. The model attends harder to the top and bottom of the window.
   - **Summarize early resolved turns.** Once a sub-issue is resolved, replace its turns with a one-line summary. Keep verbatim only the **active issue**.
   - **Prune verbose tool outputs.** When a tool returns 8KB of JSON and you only used three fields, strip the rest before appending to context. The model doesn't need the noise; your token bill doesn't need the bloat.

2. **Escalation design** (7 minutes)
   - **Honor explicit requests for human immediately.** "I want a human NOW" -> escalate. Do **not** ask for clarification first. Do **not** try one more tool call. Customer told you what they want.
   - **Never escalate on sentiment alone.** Frustration is not complexity. The right signals are **policy** (refund > $500, account closure), **complexity** (multi-system failure), **risk** (security, compliance), and **explicit request**.
   - **Pass a structured summary on escalation**, not the raw transcript. Human agents don't want to read 40 turns. They want: who, what, what's been tried, what's blocked.

3. **Error propagation in multi-agent systems** (5 minutes)
   - **Subagents return structured error context.** Use the same `errorCategory` + `isRetryable` shape from Segment 2.
   - **The parent coordinator decides** retry / fail / escalate. Subagents don't retry across system boundaries; that's the parent's job.
   - **Never silently suppress errors.** Swallowing an exception so the demo doesn't crash is how you ship a system that lies confidently.

4. **Provenance and source attribution** (5 minutes)
   - **Synthesis agents must preserve claim-source mappings** from subagents. If a subagent fetched a doc, the claim that comes out of synthesis cites that doc.
   - **Cite publication dates** when synthesizing across time-sensitive sources. A 2019 best practice and a 2025 best practice are not the same artifact.
   - **Anti-pattern callout:** "According to recent research..." with no link is a fabrication waiting to happen.

### Demo: Automatic context compaction (10 minutes)

**Live demo:**
1. Open `C:/github/claude-architect/private/claude-cookbooks-main/tool_use/automatic-context-compaction.ipynb`.
2. Run a long conversation (15+ turns) with deliberately verbose tool outputs. Watch the context-window meter climb.
3. Trigger the compaction event. Show the before/after token counts and the summarization output.
4. Run a follow-up query that depends on something from turn 2. Verify it still works post-compaction. This is the **memory survives compaction** moment.

**What attendees see:** Compaction is not magic forgetting. It's structured summarization with the **case facts** preserved verbatim. Done right, the model loses noise and keeps signal.

### About the CCA-F certification (2 minutes)

> Anthropic's **Claude Certified Architect: Foundations (CCA-F)** exam isn't publicly available yet. When it lands, here's the 5-domain blueprint to study against. The reference files in this repo map today's skills back to those domains.

| Domain | Topic | Reference file |
|--------|-------|----------------|
| 1 | Agentic Architecture & Orchestration | [`./domain-1-agentic.md`](./domain-1-agentic.md) |
| 2 | Tool Design & MCP Integration | [`./domain-2-tools-mcp.md`](./domain-2-tools-mcp.md) |
| 3 | Claude Code Configuration & Workflows | [`./domain-3-claude-code.md`](./domain-3-claude-code.md) |
| 4 | Prompt Engineering & Structured Output | [`./domain-4-prompts.md`](./domain-4-prompts.md) |
| 5 | Context Management & Reliability | [`./domain-5-context.md`](./domain-5-context.md) |

Tim hasn't sat the exam yet. Frame it as "here's the structure to study when it lands." Watch the certification page for availability.

### Exercise: Triage scorecard (5 minutes)

**Prompt:** Below are four short failure descriptions. For each, name the **design fix** in one sentence. No long answers; pattern recognition is the skill.

| # | Failure | Your fix |
|---|---------|----------|
| a | Agent picked the wrong tool for the task | ? |
| b | Refund processed for $847 against a $500 policy | ? |
| c | Synthesis output has no source attributions | ? |
| d | Agent escalated because the user said "I'm frustrated" | ? |

**Deliverable:** Four one-line fixes in chat. Reference answers:
- (a) Tighten **tool descriptions** and/or **scope tools per agent**; consider `tool_choice` to force the right call.
- (b) **Application-layer intercept** via a **PreToolUse hook**, not a prompt instruction. Policy is code, not vibes.
- (c) **Require structured claim-source mappings** from subagents; coordinator preserves them through synthesis.
- (d) **Escalate on policy, complexity, risk, or explicit request - not on sentiment.** Frustration is not a routing signal.

### Final Q&A and wrap (8 minutes)

Anticipated questions:
- "How do I monitor an agent in production?" -> Log every `stop_reason`, every tool call, every hook block. Build a dashboard on those three streams before you ship.
- "When do I split a monolithic agent into coordinator + subagents?" -> When subtasks have independent success criteria, when context bloat hurts answer quality, or when you want per-agent tool scope. Don't split for theoretical purity.
- "What's the cost story for prompt caching?" -> `cache_control: {"type": "ephemeral", "ttl": "5m"}` on system prompts and large tool definitions. Hits run roughly 90% cheaper. Run the math before assuming caching is free; cache writes cost more than reads.

### Key takeaways
- **Long-running context** survives via case-facts pinning, summarization of resolved turns, and pruning verbose tool outputs.
- **Escalation** triggers on policy, complexity, risk, or explicit request. Sentiment is not a signal.
- **Provenance and structured errors** travel up from subagents to the coordinator. Silent suppression is a production bug.

---

## Course wrap-up

### What you built

- [x] A **customer support agent** with deterministic policy enforcement via hooks
- [x] A configured **Claude Code environment** with CLAUDE.md hierarchy and MCP servers
- [x] An **invoice extraction pipeline** with schema enforcement and validation retry
- [x] A **production reliability mental model**: context, escalation, errors, provenance

### About the CCA-F certification (2-minute mention)

Anthropic's **Claude Certified Architect: Foundations** exam isn't publicly available yet. When it lands, here's the 5-domain blueprint to study against:

| Domain | Topic | Reference file |
|--------|-------|----------------|
| 1 | Agentic Architecture & Orchestration | [`./domain-1-agentic.md`](./domain-1-agentic.md) |
| 2 | Tool Design & MCP Integration | [`./domain-2-tools-mcp.md`](./domain-2-tools-mcp.md) |
| 3 | Claude Code Configuration & Workflows | [`./domain-3-claude-code.md`](./domain-3-claude-code.md) |
| 4 | Prompt Engineering & Structured Output | [`./domain-4-prompts.md`](./domain-4-prompts.md) |
| 5 | Context Management & Reliability | [`./domain-5-context.md`](./domain-5-context.md) |

This course teaches the **skills behind those domains**. The reference files map skills back to exam objectives when you're ready.

### Taking it further

1. **This week:** wire one of today's agents into a real production workflow. Don't let the demo code die in a notebook.
2. **Next:** read the 5 domain reference files in this repo for deeper dives on each area.
3. **Ongoing:** watch Anthropic's certification page for exam availability: https://anthropic.skilljar.com/

### Final Q&A

Standing questions to invite:
- "How do I monitor an agent in production?"
- "When do I split a monolithic agent?"
- "What's the cost story for prompt caching?"

Thanks for spending four hours. Now go ship something that doesn't lie.

Next Best Steps:
1) Walk the four demos end-to-end on your laptop before class to time them against the segment budgets.
2) Pre-stage the three sample invoices and the customer-support failure scenario as named cells so you don't fumble paste-buffer Tetris on stage.
3) Stand up a one-page post-class email with the five `domain-*.md` links plus a calendar invite for office hours so the cohort converts attendance into follow-through.
