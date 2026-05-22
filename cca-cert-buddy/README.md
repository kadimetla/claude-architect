# CCA Cert Buddy

A self-contained, local-first study aid for the **Claude Certified Architect - Foundations (CCA-F)** exam. It runs entirely on your machine, built end to end on the latest stable Anthropic SDKs.

The twist: **the app's own architecture is the curriculum**. Every CCA-F exam domain it tests is demonstrated by a real, running layer of the app - an MCP client and server, an agentic loop with explicit `stop_reason` handling, a validator subagent, forced structured output. Read the code and you are reading the exam.

This is **not** a Copilot agent pack. Unlike the `cert-buddy-template` and `az104-cert-buddy` markdown packs, CCA Cert Buddy is a new harness with an actual web frontend, an Express backend, a standalone MCP server, and a SQLite progress store.

## What it does

- **Quiz mode** - one question at a time, weighted toward your weak domains, with full per-option rationale and a link to the domain reference.
- **Exam simulation** - a timed 60-question mock exam, 120 minutes, scored on the 100-1000 scale with a 720 passing line.
- **Progress dashboard** - per-domain accuracy and an SM-2 spaced-repetition review queue.
- **Live generation** (optional) - generate a fresh exam-realistic question and watch the agentic loop run, step by step, in the agent-trace view.

## Quick start

```powershell
cd cca-cert-buddy
npm install
npm run seed        # builds the question bank from the repo's 60 CCA-F questions
npm run dev         # Express on :3000, Vite dev server on :5173
```

Open **http://localhost:5173**. The app is fully usable on the pre-generated question bank with **no API key**.

For a production-style run:

```powershell
npm run build
npm start           # serves the built SPA + API on http://localhost:3000
```

## Optional: live generation

Live question generation and the build-time generator need an Anthropic API key. Copy the example env file and add one:

```powershell
Copy-Item .env.example .env
# edit .env, set ANTHROPIC_API_KEY=...
```

Get a key at <https://console.anthropic.com/>. Quiz and exam modes never need a key.

## Regenerating the question bank

The build-time generator authors fresh questions through the agent core:

```powershell
npm run generate -- --domain D2 --count 5    # 5 new D2 questions
npm run generate -- --count 2                # 2 per domain, all five
npm run validate:bank                        # confirm the bank is still clean
```

A full ~60-question refresh costs well under one US dollar.

## How this app demonstrates the CCA-F domains

The app is built so each load-bearing layer **is** an exam-domain demonstration. The `/about` page in the running app states each mapping with links to the code.

| Domain | Weight | Demonstrated by |
|---|---|---|
| **D1 Agentic Architecture & Orchestration** | 27% | `server/agent/loop.ts` - a real agentic loop with an explicit `stop_reason` switch. `server/agent/subagent-validator.ts` - a coordinator-subagent pattern with isolated context. |
| **D2 Tool Design & MCP Integration** | 18% | `mcp-server/` - a standalone MCP server exposing tools, resources, and prompts. `server/agent/mcp-client.ts` - a real MCP client that discovers primitives at runtime. |
| **D3 Claude Code Configuration & Workflows** | 20% | `mcp-server/prompts.ts` - MCP prompts that surface as Claude Code slash commands. This sub-project's own `CLAUDE.md`. |
| **D4 Prompt Engineering & Structured Output** | 20% | `server/agent/generate.ts` - forced `tool_choice` for schema-shaped output, plus a validate-and-repair loop. |
| **D5 Context Management & Reliability** | 15% | Each model call gets only the relevant domain reference (isolated context). The near-duplicate guard and confidence-calibrated SM-2 scoring. |

## The cca-study-mcp server

`mcp-server/` is a standalone stdio MCP server, `cca-study-mcp`, exposing all three MCP primitives:

- **Tools** - `score_answer`, `validate_question` (structured errors, not prose), `lookup_domain_ref`
- **Resources** - `cca://domains`, `cca://progress`, `cca://bank/{domain}`, `cca://domain-ref/{id}`
- **Prompts** - `/quiz`, `/exam`, `/explain-domain`

It runs three ways: spawned by the backend's MCP client, registered in a `.mcp.json` for Claude Code, or driven under the MCP Inspector.

```powershell
npm run mcp         # run cca-study-mcp standalone on stdio
```

## Architecture

```
cca-cert-buddy/
  shared/          types, domain blueprint, path anchors, question validator
  mcp-server/      cca-study-mcp - tools, resources, prompts (Domain 2 + 3)
  server/          Express API + MCP client + agentic core
    agent/         mcp-client, loop (stop_reason switch), subagent-validator, generate
    routes/        REST endpoints
  client/          vanilla-TS SPA - hash router, typed API, views
  scripts/         seed-bank, generate-questions, validate-bank
  data/            committed question bank
  .data/           gitignored runtime SQLite
```

No frontend framework, no ORM, no CSS framework - the dependency surface is kept small so the code reads as teaching material.

## Scripts

| Command | Purpose |
|---|---|
| `npm run seed` | Build `data/question-bank.json` from the repo's `practice-questions.json`. |
| `npm run dev` | Run the Express backend and Vite dev server together. |
| `npm run build` | Build the SPA and compile the backend to `dist/`. |
| `npm start` | Run the built app (SPA + API) on one port. |
| `npm run mcp` | Run the `cca-study-mcp` server standalone. |
| `npm run generate` | Author fresh questions via the agent core (needs a key). |
| `npm run validate:bank` | Structurally validate every question in the bank. |
| `npm test` | Run the `node:test` suite (SM-2, scoring, validator, API). |

## Notes

- **Scoring model.** The 100-1000 scaled score is a piecewise-linear map from raw-correct, with a kink at 72% so the 720 passing line anchors exactly to 72% correct. Anthropic's true scaling curve is not published, so this is a teaching approximation.
- **Question provenance.** The seed bank is built from `practice-questions.json` in the parent repo, whose stems are community-sourced. The seeder normalizes voice (em dashes to ` - `) on import; the upstream file is left untouched.
- **License.** MIT. Part of the Claude Architect Foundations course material.
