# CLAUDE.md - cca-cert-buddy

Guidance for Claude Code when working in this sub-project. This is a self-contained web app inside the `claude-architect` course repo.

## What this is

A local-first CCA-F exam study aid whose **own architecture demonstrates the five CCA-F exam domains**. It is a real app - Express backend, standalone MCP server, vanilla-TS SPA, SQLite store - not a Copilot agent pack. When you change a layer, keep it both a working feature AND a clean teaching example of its domain.

## Domain-to-code map (do not break these mappings)

| Domain | The code that demonstrates it |
|---|---|
| D1 Agentic | `server/agent/loop.ts` (explicit `stop_reason` switch), `server/agent/subagent-validator.ts` |
| D2 Tools/MCP | `mcp-server/*` (all three primitives), `server/agent/mcp-client.ts` (runtime discovery) |
| D3 Claude Code | `mcp-server/prompts.ts` (MCP prompts), this file |
| D4 Structured output | `server/agent/generate.ts` (forced `tool_choice`, validate-and-repair) |
| D5 Context | isolated per-call context in `generate.ts`, dup guard in `shared/question-validator.ts` |

The `loop.ts` `switch (stopReason)` must keep an explicit, documented branch for every value (`end_turn`, `tool_use`, `max_tokens`, `pause_turn`, `stop_sequence`, `refusal`). That switch IS the Domain 1 lesson - do not collapse it into an `if`.

## Stack and conventions

- **TypeScript** everywhere. ESM (`"type": "module"`), `NodeNext` resolution. Import paths use the `.js` extension even for `.ts` sources.
- **Backend**: Express 5, better-sqlite3, run via `tsx` in dev.
- **Frontend**: vanilla TS + Vite. No framework, no CSS library. Keep it that way - the small dependency surface is deliberate.
- **Validation**: zod for API bodies and the MCP tool schemas.
- **Models**: `claude-haiku-4-5` by default; `claude-sonnet-4-6` only for question authoring (`AUTHORING_MODEL` in `server/anthropic.ts`). Never Opus.
- **Paths**: never hand-roll `join(here, "..", ...)`. Import anchors from `shared/paths.ts` so code resolves correctly whether run as `.ts` via tsx or as compiled `.js` from `dist/`.

## Voice rules (enforced by the validator)

No em dashes (use ` - `), no "ask" as a noun, no AWS mentions, bold key terms in docs. `shared/question-validator.ts` enforces these on every question; `npm run validate:bank` is the gate.

## Before you commit

1. `npm run build` - both client and server must compile clean.
2. `npm test` - the `node:test` suite must pass.
3. `npm run validate:bank` - the question bank must stay structurally clean.
4. If you touched the agent core or MCP server, run a live `npm run generate -- --count 1` (needs a key) and confirm the agent trace looks right.

## Things that will bite you

- The Bash tool's working directory does not persist between calls on this box - prefer PowerShell, or prefix every Bash call with `cd`.
- `data/question-bank.json` is committed and seeded from the parent repo's `practice-questions.json`. Re-running `npm run seed` replaces only `source: "seed"` entries; generated questions survive.
- `.data/progress.db` is gitignored runtime state. The test suite appends rows to it - that is expected for a local study aid.
- The MCP client spawns `mcp-server/index.ts` via `tsx`, so the `.ts` source must ship alongside the build.
