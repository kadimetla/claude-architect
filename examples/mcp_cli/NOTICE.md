# NOTICE - mcp_cli reference application

This directory (`examples/mcp_cli/`) is a **reference MCP CLI application** vendored into the `claude-architect` repo as instructional study material. It is **not authored by Tim Warner**.

## Attribution

- **Original source:** Anthropic, "Claude with the Anthropic API" course (https://anthropic.skilljar.com/claude-with-the-anthropic-api/)
- **Course URL:** https://anthropic.skilljar.com/claude-with-the-anthropic-api/
- **Provider:** Anthropic, PBC, via Skilljar
- **Snapshot date:** Captured 2026-05 for the Claude Architect Foundations O'Reilly training.

The code was distributed as downloadable starter material accompanying that course. It is included here so learners can study a complete, runnable MCP client + stdio FastMCP server + interactive CLI in one place, alongside the rest of the course artifacts.

## What's in it

- **`main.py`** - entry point. Loads `.env`, instantiates a `Claude` service and an `MCPClient`, opens an interactive `CliApp`.
- **`mcp_client.py`** - a thin wrapper around the official `mcp.ClientSession` that exposes `list_tools`, `call_tool`, `list_prompts`, `get_prompt`, `read_resource`.
- **`mcp_server.py`** - a `FastMCP` server exposing six dummy documents as resources, plus `read_doc_contents` and `edit_document` tools and a `format` prompt. Runs over stdio.
- **`core/`** - the chat loop:
  - `claude.py` - thin Anthropic SDK wrapper
  - `chat.py` and `cli_chat.py` - chat orchestration, with `@doc-id` retrieval and `/prompt-name` command parsing
  - `cli.py` - prompt-toolkit-driven CLI shell
  - `tools.py` - tool result handling

## How this differs from the course's notebooks

The five teaching notebooks in `../../notebooks/` are **Tim Warner's original work** for the O'Reilly live training. They cite `.mcp.json` as **config-as-data** but do not run a live MCP server in a Jupyter kernel (auth-surface cross-talk). This reference app is the "what does a real MCP server and client look like in production code" companion: study it after Segment 2.

## How to run it

Setup commands and dependencies are documented in `./README.md`. The short version:

```powershell
cd examples/mcp_cli
uv venv
. .venv/Scripts/Activate.ps1
uv pip install -e .
Copy-Item .env.example .env  # then edit .env and add your ANTHROPIC_API_KEY
uv run main.py
```

## Modifications from the original

This copy is **as-distributed by Anthropic's course**, with two exceptions:

1. The committed `.env` template has been renamed to `.env.example` so the inner `.gitignore` does its job on the empty-key template too. No code changes.
2. This `NOTICE.md` has been added.

If you want the canonical source, return to https://anthropic.skilljar.com/claude-with-the-anthropic-api/.

## License

The original course distributes this code as instructional material. No explicit license file ships with the download. **Treat as Anthropic-authored instructional reference**: study it, run it, adapt patterns from it. Do not redistribute as your own work. If you want to redistribute or fork, contact Anthropic directly.
