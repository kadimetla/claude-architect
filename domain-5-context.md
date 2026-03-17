# Domain 2: Tool Design & MCP Integration (18%)

## Tool Descriptions > Tool Names

Descriptions are the primary mechanism for tool selection. Include input formats, examples, edge cases, and boundaries.

## Structured Errors

Return `errorCategory` (transient/validation/permission/business), `isRetryable`, and human-readable description. Never return generic "Operation failed."

## Scoped Tool Distribution

4-5 tools per agent max. Each agent gets only tools for its role. `tool_choice`: `"auto"`, `"any"`, or forced specific tool.

## MCP Server Config

- Project-level `.mcp.json` (shared, committed) vs user-level `~/.claude.json` (personal)
- Env var expansion `${GITHUB_TOKEN}` keeps secrets out of repos
