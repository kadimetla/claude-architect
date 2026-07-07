# agents_api/ - Managed Agents teaching notebooks

Six small, teaching-quality notebooks on the **Managed Agents API**, each banded to a **CCA-F** exam domain and themed to keep the mechanics memorable. They follow the `first_request.ipynb` mold: one idea per cell, markdown explains **why**, the create -> send -> stream -> idle -> teardown spine repeats so it becomes muscle memory.

**Author: Tim Warner.** These notebooks are original work, not adapted from an external source.

## Concept map

| Notebook | CCA-F domain (weight) | What it teaches | Theme |
| --- | --- | --- | --- |
| `01_agentic_loop_and_sessions.ipynb` | **Domain 1 - Agentic (27%)** | The create -> send -> stream -> **idle**/`stop_reason` -> teardown loop; server-side **session** memory across turns | 70s slasher plus giallo **double-feature curator** |
| `02_coordinator_and_subagents.ipynb` | **Domain 1 - Agentic (27%)** | A coordinator agent with **`multiagent`** config delegating to specialists; isolated-context orchestration vs the daisy-chain anti-pattern | **Vampire Survivors** build council |
| `03_tools_and_structured_errors.ipynb` | **Domain 2 - Tools (18%)** | One **custom tool** plus a **structured tool error** with retry-once; the `user.custom_tool_result` event keyed by `custom_tool_use_id` and `is_error` | Vintage **guitar-gear price** agent |
| `04_structured_output_and_validation.ipynb` | **Domain 4 - Structured output (20%)** | JSON out of an agent turn plus **validate-and-retry-once**; the null-if-not-stated rule | **Transgressive-cinema** metadata extractor |
| `05_context_and_escalation.ipynb` | **Domain 5 - Context and escalation (15%)** | Route on problem **shape**, not sentiment; context-window discipline plus escalation | **Chirpy the cat** incident triage |
| `06_cca_f_capstone.ipynb` | **Capstone - D1 + D2 + D4 + D5** | All four code domains in one session, then 6 original domain-weighted self-check questions | **Nashville horror-fest** ops agent |

**On Domain 3 (Claude Code, 20%).** Domain 3 is CLI and configuration - CLAUDE.md, settings, hooks, MCP wiring - taught live in the **segment-2 course notebook**, not faked in this API surface. The one honest bridge: an agent's **`system`** prompt is a versioned artifact, much like **CLAUDE.md**.

## Running these

- These notebooks make **live, billable, beta-gated** calls against the **Managed Agents API**. Every call carries the beta header **`managed-agents-2026-04-01`**.
- Your key must have **Managed Agents beta access**, or the first create returns a 403.
- They read `examples/.env` via `python-dotenv`. Copy **`.env.example`** to `.env` and set `ANTHROPIC_API_KEY`.
- **Kernel:** pick **`claude-architect`** (pinned to `notebooks/.venv`). If it is missing on a fresh clone, register it once:

  ```powershell
  uv run --project notebooks python -m ipykernel install --user --name claude-architect --display-name "Claude Architect (notebooks/.venv)"
  ```

> **Always run the teardown cell.** A live **session** is a billable runtime that keeps costing until archived. Every notebook ends by archiving the session and the agent (**`archive`**, not `delete` - there is no `agents.delete` on this surface). In your own code, wrap the run in **`try/finally`** so teardown executes even when a turn raises.

## Voice and stack

- No em dashes (use ` - `), Azure-first if cloud comes up, no "ask" as a noun.
- Model default is **`claude-haiku-4-5`** per the repo model policy; Sonnet only where reasoning depth earns it.
