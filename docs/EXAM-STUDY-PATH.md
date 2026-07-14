# CCA-F Study Path for This Workshop

This workshop teaches **Claude Architect** skills - the production patterns for building with Claude Code, the Claude Agent SDK, the Claude API, and MCP. Underneath that visible arc, every segment also rehearses the **architecture habits, vocabulary, and scenario-analysis patterns** that Anthropic's Claude Certified Architect: Foundations (CCA-F) exam tests.

**This is not an exam-dump session.** The practice material in this repo is **calibration**, not a braindump. The authoritative source for exam mechanics, registration, and policy is Anthropic; see [`CERT-PROGRAM-BRIEFING.md`](./CERT-PROGRAM-BRIEFING.md).

## How this workshop maps to the exam

The mapping is one-to-many on purpose: most architecture skills cross domain boundaries, and the exam asks you to reason across them. Each segment has a **primary skill** (what you walk out being able to do) and **CCA-F domain coverage** (which exam objectives you exercised along the way).

| Workshop Segment | Notebook | Primary Skill | CCA-F Domains | Scenario Families |
|---|---|---|---|---|
| **0** Pre-flight | [`segment-0-pre-flight.ipynb`](../notebooks/segment-0-pre-flight.ipynb) | Environment + credentials + SDK floor check | D1, D5 | Developer productivity |
| **1** Building AI Agents | [`segment-1-customer-support-agent.ipynb`](../notebooks/segment-1-customer-support-agent.ipynb) | Agentic loop, `stop_reason` branching, **PreToolUse hooks** as deterministic guarantees, coordinator-subagent isolation | **D1** (27%), D2, D5 | Customer Support Resolution Agent, Multi-Agent Research |
| **2** Tool Design + MCP + Claude Code | [`segment-2-tool-design-and-mcp.ipynb`](../notebooks/segment-2-tool-design-and-mcp.ipynb) | Opinionated tool descriptions, four `tool_choice` modes, structured errors, MCP config, CLAUDE.md hierarchy, prompt caching | **D2** (18%) + **D3** (20%) | Developer Productivity, CI/CD Integration |
| **2.5** Control Surfaces (self-study) | [`segment-2-5-control-surfaces.ipynb`](../notebooks/segment-2-5-control-surfaces.ipynb) | Three tiers tools come from (server tools, MCP, harness), full `tool_choice` depth + `disable_parallel_tool_use`, `stop_sequences` / `max_tokens` as control levers, **live Claude Console asset surface** (memory_stores, vaults, agents, sessions) | **All five** (D1-D5) | Cross-cutting; this notebook is the exam-stud anchor |
| **3** Structured Output + Reliability | [`segment-3-invoice-extractor.ipynb`](../notebooks/segment-3-invoice-extractor.ipynb) | Forced `tool_choice` for schema compliance, Pydantic validation with retry, case-facts pinning via `cache_control`, confidence-routing triage | **D4** (20%) + **D5** (15%) | Structured Data Extraction Pipeline |
| **4** CCA-F Capstone | [`segment-4-cca-f-capstone.ipynb`](../notebooks/segment-4-cca-f-capstone.ipynb) | Cert briefing + **domain-weighted** practice questions + take-home punchlist | D1-D5 (review) | Cross-cutting |
| **Exam Mastery** (off-clock) | [`cca-f-exam-mastery.ipynb`](../notebooks/cca-f-exam-mastery.ipynb) | Every one of the **30 CCA-F task statements** (TS1.1 through TS5.6) mapped to a runnable minimal demo, plus exam mechanics and a one-page cheat sheet | **All five**, by task statement | All six |

## Start here: the exam-mastery notebook

[`cca-f-exam-mastery.ipynb`](../notebooks/cca-f-exam-mastery.ipynb) is **the single most exam-aligned artifact in this repo**, and it's the one to open first when you sit down to study. It's a standalone reference, off the 4-hour live clock, in seven parts: one per domain, plus a mechanics-and-coverage part that carries the domain weights, the cheat sheet, and a self-check.

What makes it the anchor:

- It maps **every one of the 30 CCA-F task statements**, TS1.1 through TS5.6, to a minimal demo you can actually run. The notebook audits its own coverage and reports 30/30: D1 7/7, D2 5/5, D3 6/6, D4 6/6, D5 6/6.
- It's **fully smoke-verified**, 20 of 20 cells green, zero errors.
- It **creates no billable resources**. Nothing to archive, nothing to leak, no session quietly costing you money while you read.

Walk it once end to end. Then walk the parts your practice questions say you're weak in.

**Segment 2.5 is the depth pass on the control surfaces.** It is a self-study deep dive (also off the live clock) that ties together every control surface the live segments touch lightly: full `tool_choice` modes including `disable_parallel_tool_use`, every `stop_reason` value including the rare ones (`stop_sequences`, `max_tokens` as control lever, `pause_turn`, `refusal`), MCP `list_tools` runtime discovery, and the live Claude Console asset surface (`memory_stores`, `vaults`, `agents`, `sessions`). Where exam-mastery gives you breadth across all 30 task statements, 2.5 gives you depth on the levers. Walk exam-mastery first, then this one.

## Two example tracks worth your time

Neither of these is on the live clock, and both are smoke-verified green.

**[`examples/messages_api/`](../examples/messages_api/) is the on-ramp.** Ten short notebooks on the raw Messages API: a single request, the system prompt as a control surface, temperature, streaming, and output control, with `_exercise` variants on three of them. If the agentic loop feels like magic rather than mechanism, this is why. The loop is just `messages.create()` in a while-loop with a `stop_reason` branch, and these notebooks build that primitive one idea at a time. Most relevant to **D1** (the primitive under the loop) and **D4** (`005_controlling_output` and `002_system_prompt` are output control, plainly).

**[`examples/agents_api/`](../examples/agents_api/) is the counterpart.** Six notebooks on the **Managed Agents API**, where Anthropic hosts the loop you otherwise hand-roll. Each is banded to a domain, and each ends by archiving its resources, which you should let it do.

| Notebook | Domain |
|---|---|
| [`01_agentic_loop_and_sessions.ipynb`](../examples/agents_api/01_agentic_loop_and_sessions.ipynb) | **D1** |
| [`02_coordinator_and_subagents.ipynb`](../examples/agents_api/02_coordinator_and_subagents.ipynb) | **D1** |
| [`03_tools_and_structured_errors.ipynb`](../examples/agents_api/03_tools_and_structured_errors.ipynb) | **D2**, with the D3 bridge |
| [`04_structured_output_and_validation.ipynb`](../examples/agents_api/04_structured_output_and_validation.ipynb) | **D4** |
| [`05_context_and_escalation.ipynb`](../examples/agents_api/05_context_and_escalation.ipynb) | **D5** |
| [`06_cca_f_capstone.ipynb`](../examples/agents_api/06_cca_f_capstone.ipynb) | All domains |

These notebooks make **live, billable, beta-gated** calls, so they're a different budget than exam-mastery. Read the contrast, though: seeing the same loop hosted for you is the fastest way to understand what your hand-rolled version is actually doing.

## Domain weighting reference

The CCA-F exam draws **60 multiple-choice questions** weighted across five domains. Segment 4 in this workshop samples 10 questions using the **same weighting** so the practice ratio matches the real exam ratio:

| Domain | Exam weight | Segment 4 sample | Reference |
|---|---:|---:|---|
| **D1** Agentic Architecture & Orchestration | 27% | 3 questions | [`domain-1-agentic.md`](./domain-1-agentic.md) |
| **D2** Tool Design & MCP Integration | 18% | 2 questions | [`domain-2-tools-mcp.md`](./domain-2-tools-mcp.md) |
| **D3** Claude Code Configuration & Workflows | 20% | 2 questions | [`domain-3-claude-code.md`](./domain-3-claude-code.md) |
| **D4** Prompt Engineering & Structured Output | 20% | 2 questions | [`domain-4-prompts.md`](./domain-4-prompts.md) |
| **D5** Context Management & Reliability | 15% | 1 question | [`domain-5-context.md`](./domain-5-context.md) |

D1 carries the most weight; D5 carries the least but is the **easiest to under-teach** because it feels like security common sense until scenario questions get specific. If a domain feels easy, the practice questions for it are the ones to re-walk.

## Scenario families

The CCA-F exam draws **four scenarios at random from a pool of six**. The workshop's notebooks anchor learners in five of the six; the take-home practice bank ([`PRACTICE-QUESTIONS.md`](./PRACTICE-QUESTIONS.md)) covers four explicitly with room to expand.

| # | Scenario | Anchored in | Primary domains |
|---|---|---|---|
| 1 | Customer Support Resolution Agent | Segment 1 | D1, D2, D5 |
| 2 | Code Generation with Claude Code | Segment 2 demos | D3, D5 |
| 3 | Multi-Agent Research System | Segment 1 coordinator-subagent | D1, D2, D5 |
| 4 | Developer Productivity Tooling | Segment 2 + 2.5 | D1, D2, D3 |
| 5 | CI/CD Integration with Claude Code | Segment 2 `claude -p` headless | D3, D4 |
| 6 | Structured Data Extraction Pipeline | Segment 3 | D4, D5 |

## Calibration, not braindump

The practice questions in [`PRACTICE-QUESTIONS.md`](./PRACTICE-QUESTIONS.md) and the inline 10-question sample in Segment 4 are **original workshop calibration material**. They are **not** exam dumps, not predictions, and not transcriptions of any confidential source. Their purpose:

- **Calibrate your sense** of the question shape (situation, options, justification).
- **Surface your weak domains** so you know what to re-walk in the cookbook.
- **Train scenario-analysis intuition** so the real exam's scenarios feel familiar in pattern, not in content.

For an authoritative readiness check, use **Anthropic's official Practice Exam** (linked from your CCA-F Skilljar page) before scheduling the proctored attempt. See [`CERT-PROGRAM-BRIEFING.md`](./CERT-PROGRAM-BRIEFING.md) for exam mechanics (60 questions, 120 minutes, 720 passing, one attempt only) and the week-before punchlist.

## After class: a study path that actually works

The four-hour session ends. The exam is whenever you schedule it. A study path that holds up:

1. **Walk [`cca-f-exam-mastery.ipynb`](../notebooks/cca-f-exam-mastery.ipynb) cold, end to end.** It's the only artifact that touches all 30 task statements, and it costs you nothing but time. Anything in it that surprises you on this pass names the domain you're weakest in.
2. **Re-walk Segment 2.5 for depth on the control surfaces.** Exam-mastery gives you the map. 2.5 gives you the levers: full `tool_choice`, the rare `stop_reason` values, `list_tools` discovery, the Console assets.
3. **Re-take the practice questions by domain.** [`PRACTICE-QUESTIONS.md`](./PRACTICE-QUESTIONS.md) carries 60 questions tagged by primary CCA-F domain. Filter to one domain at a time, get them all right, then mix.
4. **Explain every wrong answer out loud.** Not "this one was D" but "this one was D because the question stem named a hook lifecycle event, and PostToolUse runs after the result, which means..." If you can't do that, the domain reference scaffold ([`domain-1-agentic.md`](./domain-1-agentic.md) through [`domain-5-context.md`](./domain-5-context.md)) is the next read, and each one now points back at its part of the exam-mastery notebook.
5. **Run one cookbook notebook per gap.** [`claude-cookbooks-main/`](../claude-cookbooks-main/) ships in this repo (no second clone). The notebooks Anthropic ships there are authoritative; treat them as the reference set when this workshop's pedagogy and Anthropic's official material disagree (they shouldn't, but if they do, **Anthropic wins**). Check [`COOKBOOK-INDEX.md`](./COOKBOOK-INDEX.md) first, because two of them currently fail to run on upstream bugs and you don't want to lose an evening to that.
6. **Take Anthropic's Practice Exam before booking the real one.** You get one attempt at the proctored exam. The Practice Exam is your last calibration before that one-shot.

The exam is one attempt at $99 (partner discount available). Treat it like that.
