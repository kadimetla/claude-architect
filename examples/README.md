# examples/

Curated reference applications that complement the six teaching notebooks in `../notebooks/`. Each subdirectory is a complete, runnable example, attributed where the source is not Tim Warner's own work.

## Index

| Directory / file | What it is                                                                                                               | Source                                                                    | When to study                         |
| ---------------- | ------------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------- | ------------------------------------- |
| `mcp_cli/`       | Reference MCP CLI: stdio FastMCP server + client + interactive chat with `@doc-id` retrieval and `/prompt-name` commands | Anthropic Skilljar course, see [`mcp_cli/NOTICE.md`](./mcp_cli/NOTICE.md) | After Segment 2 (Tool Design and MCP) |
| `messages_api/`  | Messages API primer notebooks (`001_*` - `005_*`): requests, system prompts, temperature, streaming, controlled output, plus three exercises, `first_request`, and `multi_turn_conversation` | Adapted with thanks from [jaozc/building-with-the-claude-api](https://github.com/jaozc/building-with-the-claude-api/tree/main) | Alongside Segment 1 (first API calls) |
| `agents_api/`    | Managed-agents notebooks (Console asset surface: memory stores, vaults, agents, sessions). **Under active construction in a separate session - do not edit.** | Tim Warner | After Segment 2.5 (Control Surfaces) |

## Running the primer notebooks (`messages_api/`)

The `messages_api/` notebooks were adapted from [jaozc/building-with-the-claude-api](https://github.com/jaozc/building-with-the-claude-api/tree/main). Three changes make them run in this repo's **uv**-managed world:

- **Install cell uses uv, not `%pip`.** uv-managed venvs ship without pip, so the first cell shells out to `uv pip install` pointed at the running kernel's interpreter. Idempotent - it no-ops when packages are already present.
- **Model is `claude-haiku-4-5`** - the repo default (see the model policy in the root `CLAUDE.md`).
- **Prompts are Azure-first** - the streaming and controlled-output demos ask for Azure Event Grid and Azure CLI samples.

### Kernel: pick "Claude Architect (notebooks/.venv)"

Every `messages_api/` notebook requests a course kernel named **`claude-architect`** whose interpreter path is pinned to `notebooks/.venv`. When you open a notebook, that kernel is auto-selected and starred. If it is missing on a fresh clone, register it once:

```powershell
uv run --project notebooks python -m ipykernel install --user --name claude-architect --display-name "Claude Architect (notebooks/.venv)"
```

An API key must be present. These notebooks read `examples/.env` (gitignored) via `python-dotenv`; put `ANTHROPIC_API_KEY=...` there, or export it in your shell.

## Conventions

- Every example with an external source ships a `NOTICE.md` at its root that names the source, attribution, and any modifications.
- Examples are runnable on their own (each has its own `pyproject.toml` and `.python-version` where applicable). They do not share the parent repo's notebook environment.
- Examples are not auto-tested by the course smoke tests; they are study material, not class deliverables.
