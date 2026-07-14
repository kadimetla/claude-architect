# examples/

Three reference suites that complement the seven teaching notebooks in [`../notebooks/`](../notebooks/README.md). Each subdirectory is a complete, runnable example, attributed where the source isn't Tim Warner's own work.

**These aren't orphans anymore.** As of the 2026-07-14 rework, the live teaching notebooks link into `examples/` from their **"Going further" appendices**: `messages_api/` is the prerequisite ramp that Segment 1 points back at, and the `agents_api/` notebooks are the managed counterparts that Segments 1, 2, 3, and 4 point forward to. They're part of the teaching path.

## Index

| Directory | What it is | Source | Status | When to study |
| --- | --- | --- | --- | --- |
| `messages_api/` | **On-ramp.** Ten Messages API primer notebooks: requests, system prompts, temperature, streaming, controlled output, three `_exercise` variants, `first_request`, and `multi_turn_conversation` | Adapted with thanks from [jaozc/building-with-the-claude-api](https://github.com/jaozc/building-with-the-claude-api/tree/main) | **All 7 non-exercise notebooks smoke-verified GREEN** (zero error cells) | Before or alongside Segment 1 (first API calls) |
| `agents_api/` | **"Anthropic hosts the loop."** Six domain-banded Managed Agents notebooks against the Console asset surface (memory stores, vaults, agents, sessions) | Tim Warner | **All 6 smoke-verified GREEN** (zero error cells), and **all 6 archive their resources** | After Segment 2.5 (Control Surfaces), or as the managed counterpart to any live segment |
| `mcp_cli/` | Reference MCP CLI: stdio FastMCP server plus client plus interactive chat with `@doc-id` retrieval and `/prompt-name` commands | Anthropic Skilljar course, see [`mcp_cli/NOTICE.md`](./mcp_cli/NOTICE.md) | Vendored reference; runs as its own uv project | After Segment 2 (Tool Design and MCP) |

## `messages_api/` - the raw Messages API on-ramp

Ten notebooks: `001_requests`, `002_system_prompt`, `003_temperature`, `004_streaming`, `005_controlling_output`, the `_exercise` variants of 001, 002, and 005, plus `first_request.ipynb` and `multi_turn_conversation.ipynb`. Start here if the raw Messages API is new to you. Everything the live class builds on top of - tool use, agentic loops, structured output - assumes you're comfortable with what these ten cover.

All **seven non-exercise notebooks are smoke-verified green** against the live API, zero error cells.

Three changes versus the [upstream source](https://github.com/jaozc/building-with-the-claude-api/tree/main) make them run in this repo's **uv**-managed world:

- **The install cell uses uv, not `%pip`.** uv-managed venvs ship without pip, so the first cell shells out to `uv pip install` pointed at the running kernel's interpreter. It's idempotent and no-ops when the packages are already present.
- **Model is `claude-haiku-4-5`**, the repo default (see the model policy in the root [`CLAUDE.md`](../CLAUDE.md)).
- **Prompts are Azure-first.** The streaming and controlled-output demos request Azure Event Grid and Azure CLI samples.

## `agents_api/` - the managed counterpart

Six notebooks, banded by CCA-F domain:

| Notebook | Covers |
| --- | --- |
| `01_agentic_loop_and_sessions.ipynb` | Domain 1: the loop Anthropic runs for you, and the session as its runtime |
| `02_coordinator_and_subagents.ipynb` | Domain 1: coordinator plus subagent delegation |
| `03_tools_and_structured_errors.ipynb` | Domains 2 and 3: tool definitions and the structured-error contract |
| `04_structured_output_and_validation.ipynb` | Domain 4: schema-constrained output and validation retries |
| `05_context_and_escalation.ipynb` | Domain 5: context management and the escalation path |
| `06_cca_f_capstone.ipynb` | All five domains end to end |

These use the **Managed Agents beta**, so requests carry the header `anthropic-beta: managed-agents-2026-04-01`. Read them as the counterpoint to the live segments: the class teaches you to hand-roll the agentic loop so you understand every moving part, and these six show what it looks like when Anthropic hosts that loop for you.

All **six are smoke-verified green** (zero error cells) and **all six archive the resources they create**, so a full run leaves nothing behind on your Console account.

## `mcp_cli/` - the vendored MCP reference app

The reference MCP CLI from Anthropic's Skilljar course. It's a **separate uv project** with its own `pyproject.toml` and `uv.lock`, and its Python is pinned to **3.13** via `.python-version` (the committed `jiter` wheel has no 3.14 build). Bootstrap it on its own:

```powershell
cd examples\mcp_cli
uv run main.py
```

Or take the on-rails path from the repo root, which owns the ports and clears any Windows half-state before launch:

```powershell
.\scripts\run-mcp-cli.ps1            # the interactive MCP CLI app
.\scripts\run-mcp-inspector.ps1      # MCP Inspector against mcp_server.py
```

Its FastMCP demo server, `mcp_cli/mcp_server.py`, is registered in the repo-root `.mcp.json` as **`oreilly-cca-mcp`** (it was `document-mcp` before the rename), so Claude Code picks it up as a project-scoped server. That's the same server the exam-mastery notebook's `list_tools` cell discovers.

## Kernel: pick "Claude Architect (notebooks/.venv)"

Every `messages_api/` notebook stamps `kernelspec.name = "claude-architect"`, a **user-scoped kernelspec** whose `argv[0]` is the absolute path to `notebooks/.venv/Scripts/python.exe`. Open a notebook and that kernel auto-selects. If it's missing on a fresh clone, register it once from the repo root:

```powershell
uv run --project notebooks python -m ipykernel install --user --name claude-architect --display-name "Claude Architect (notebooks/.venv)"
```

**The trap this avoids:** a bare `"python"` in `argv` resolves to whatever comes first on PATH, which on a typical Windows box is a machine-wide install you can't write to. The uv install cell then fails with an Access-denied `os error 5`. Pinning the absolute interpreter path means the notebook always lands in the writable uv venv, whatever PATH happens to say.

An API key must be present. These notebooks read `examples/.env` (gitignored) via `python-dotenv`, so put `ANTHROPIC_API_KEY=...` there, or export it in your shell.

## Conventions

- Every example with an external source ships a `NOTICE.md` at its root naming the source, the attribution, and any modifications.
- `mcp_cli/` is runnable on its own with its own `pyproject.toml` and `.python-version`, and doesn't share the notebook environment. The `messages_api/` and `agents_api/` notebooks run on the shared `claude-architect` kernel instead.
- Smoke artifacts (`_smoke-*.ipynb`) are **gitignored** here, same as in `notebooks/`. They're transient by design.
- These suites aren't part of the course's own smoke-test sweep, but both notebook suites have been verified green by hand against the live API.
