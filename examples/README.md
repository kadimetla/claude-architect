# examples/

Curated reference applications that complement the six teaching notebooks in `../notebooks/`. Each subdirectory is a complete, runnable example, attributed where the source is not Tim Warner's own work.

## Index

| Directory | What it is | Source | When to study |
|---|---|---|---|
| `mcp_cli/` | Reference MCP CLI: stdio FastMCP server + client + interactive chat with `@doc-id` retrieval and `/prompt-name` commands | Anthropic Skilljar course, see [`mcp_cli/NOTICE.md`](./mcp_cli/NOTICE.md) | After Segment 2 (Tool Design and MCP) |

## Conventions

- Every example with an external source ships a `NOTICE.md` at its root that names the source, attribution, and any modifications.
- Examples are runnable on their own (each has its own `pyproject.toml` and `.python-version` where applicable). They do not share the parent repo's notebook environment.
- Examples are not auto-tested by the course smoke tests; they are study material, not class deliverables.
