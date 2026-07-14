# Pre-class checklist - Claude Architect Foundations

> Run this 30 minutes before going live. Every box must be checked, every **Expect:** must match. If a step fails, fix it before moving on. Nothing below assumes a broken step succeeded.
>
> **First time teaching this course?** Start with [`./INSTRUCTOR-SETUP.md`](./INSTRUCTOR-SETUP.md) for the multi-day setup arc. This file assumes that setup is already complete.
>
> **Something goes down mid-class?** [`./EMERGENCY-CARD.md`](./EMERGENCY-CARD.md) is the one-page recovery sheet. Keep it open on the second monitor.

**Course:** Claude Architect Foundations (CCA-F Crash Course), 4 hours, O'Reilly Live
**Owner:** Tim Warner
**Repo:** `C:\github\claude-architect`
**Stack:** Windows 11, PowerShell 7, VS Code, Python 3.13, Claude Code CLI

## 0. The fast path: automated go/no-go

Before you walk the manual sections below, run the **read-only go/no-go board**. It covers most of what follows in one shot.

- [ ] **`preflight-class.ps1` reports GO**
  ```powershell
  cd C:\github\claude-architect
  .\scripts\preflight-class.ps1
  ```
  **Expect:** **PASS / WARN / FAIL** rows, ending in **GO** with exit code 0. It checks tooling (uv, node, npx, git), secrets (both `.env` files plus `GITHUB_TOKEN`), both venvs, the `claude-architect` kernelspec's `argv[0]`, both MCP configs (they parse, and the demo-server name is in sync), that all seven notebooks parse, and ports 8888 / 6274 / 6277.

  This script is **read-only by design**. It changes nothing, starts nothing, and stops nothing, so it's safe to run as many times as you want. A **FAIL** row tells you exactly which manual section below to go fix. Treat the sections that follow as the diagnostic detail behind each row, not as redundant work.

- [ ] **Sidecars up**
  ```powershell
  .\start-sidecar-group.ps1
  ```
  **Expect:** three windows, one each for **JupyterLab** (8888), the **MCP Inspector** (6274 web UI, 6277 proxy), and the **MCP CLI REPL**. The script is **idempotent**: it skips any sidecar whose port is already held, so re-running repairs a gap instead of stacking duplicates. Flags: `-Restart`, `-SkipPreflight`, `-NoMcpCli`, `-NoJupyter`.

  **Teaching from VS Code?** Add `-NoJupyter`. The VS Code Jupyter extension spawns its **own kernel process** and never connects to a JupyterLab server on 8888, so that sidecar is dead weight in that workflow.

  Take everything down afterward with `.\stop-sidecar-group.ps1`.

- [ ] **You've read the recovery command and can type it from memory**
  ```powershell
  cd C:\github\claude-architect
  .\start-sidecar-group.ps1 -NoJupyter
  ```
  This is the fix for nearly every mid-class sidecar failure. Tested: killing the Inspector outright and running this brought it back in about 15 seconds.

  **Do NOT reach for `scripts\run-mcp-inspector.ps1` directly mid-class.** It clears ports 6274 and 6277 **before** launching, so it kills a working Inspector on the way in. Always go through `start-sidecar-group.ps1`, which skips anything already healthy.

## 1. Environment

- [ ] **PowerShell 7+** active
  ```powershell
  $PSVersionTable.PSVersion
  ```
  **Expect:** Major 7, Minor 0 or higher

- [ ] **Python 3.13.x**
  ```powershell
  python --version
  ```
  **Expect:** `Python 3.13.x`

- [ ] **Node.js 18+**
  ```powershell
  node --version
  ```
  **Expect:** `v18.x.x` or higher

- [ ] **Claude Code CLI installed**
  ```powershell
  claude --version
  ```
  **Expect:** Version string, no error

## 2. API and auth

- [ ] **`ANTHROPIC_API_KEY` set**
  ```powershell
  if ($env:ANTHROPIC_API_KEY) { "ok ($(($env:ANTHROPIC_API_KEY).Length) chars)" } else { "MISSING" }
  ```
  **Expect:** `ok (XX chars)`, at least 90 chars for a real key

- [ ] **Claude Code session active**
  ```powershell
  claude /status
  ```
  **Expect:** Authenticated, account info shown, no rate-limit warnings

- [ ] **Claude Max subscription as fallback**, confirm logged in to claude.ai in browser tab (fallback if API rate-limits during live build)

## 3. Repo state

- [ ] **`claude-architect` repo clean**
  ```powershell
  git -C C:/github/claude-architect status
  ```
  **Expect:** `nothing to commit, working tree clean`

- [ ] **On main branch**
  ```powershell
  git -C C:/github/claude-architect branch --show-current
  ```
  **Expect:** `main`

## 4. Demo file inventory

The class is taught **from the five live-teaching notebooks in `./notebooks/`**; a sixth notebook (`segment-2-5-control-surfaces.ipynb`) ships alongside as a self-study deep dive and a seventh (`cca-f-exam-mastery.ipynb`) is an off-clock post-class reference. Neither of those two is on the 4-hour clock. Each segment notebook IS its segment.

Section 0's `preflight-class.ps1` already confirms that all seven notebooks parse. The checks below are the per-file detail behind that row, for when you need to know which one broke.

- [ ] **Class-day lifecycle scripts present**
  ```powershell
  @('scripts/preflight-class.ps1','start-sidecar-group.ps1','stop-sidecar-group.ps1','docs/EMERGENCY-CARD.md') |
    ForEach-Object { "$_ : $(Test-Path "C:/github/claude-architect/$_")" }
  ```
  **Expect:** `True` on all four.

- [ ] **Segment 0 pre-flight notebook**
  ```powershell
  Test-Path C:/github/claude-architect/notebooks/segment-0-pre-flight.ipynb
  ```
  **Expect:** `True`. Optional 5-min warm-up the cohort runs before Segment 1.

- [ ] **Segment 1 notebook: customer support agent**
  ```powershell
  Test-Path C:/github/claude-architect/notebooks/segment-1-customer-support-agent.ipynb
  ```
  **Expect:** `True`

- [ ] **Segment 1 hook reference: hooks-example.py**
  ```powershell
  Test-Path C:/github/claude-architect/hooks-example.py
  ```
  **Expect:** `True`. Real PreToolUse / PostToolUse reference (not the editor-settings stub it used to be).

- [ ] **Segment 2 notebook: tool design + MCP**
  ```powershell
  Test-Path C:/github/claude-architect/notebooks/segment-2-tool-design-and-mcp.ipynb
  ```
  **Expect:** `True`

- [ ] **Segment 2 MCP client config: repo's own .mcp.json**
  ```powershell
  Test-Path C:/github/claude-architect/.mcp.json
  ```
  **Expect:** `True`. The notebook loads this file and pretty-prints transports + env-var refs.

- [ ] **Segment 2 CLAUDE.md (repo's own)**
  ```powershell
  Test-Path C:/github/claude-architect/CLAUDE.md
  ```
  **Expect:** `True`

- [ ] **Segment 3 notebook: invoice extractor**
  ```powershell
  Test-Path C:/github/claude-architect/notebooks/segment-3-invoice-extractor.ipynb
  ```
  **Expect:** `True`

- [ ] **Segment 4 notebook: CCA-F capstone**
  ```powershell
  Test-Path C:/github/claude-architect/notebooks/segment-4-cca-f-capstone.ipynb
  ```
  **Expect:** `True`. Renders the cert briefing and 10 weighted practice questions inline.

- [ ] **CCA-F cert briefing reference exists**
  ```powershell
  Test-Path C:/github/claude-architect/docs/CERT-PROGRAM-BRIEFING.md
  ```
  **Expect:** `True`. The Segment 4 notebook references it for the full week-before punchlist.

- [ ] **Practice questions Markdown (cohort take-home)**
  ```powershell
  Test-Path C:/github/claude-architect/docs/PRACTICE-QUESTIONS.md
  ```
  **Expect:** `True`. 60-question take-home reference.

- [ ] **Practice questions JSON parses to 60 entries**
  ```powershell
  python -c "import json; print(len(json.load(open(r'C:/github/claude-architect/practice-questions.json', encoding='utf-8'))))"
  ```
  **Expect:** `60`. The Segment 4 notebook samples 10 questions from this file.

- [ ] **Post-class study asset: CCA-F exam-mastery notebook**
  ```powershell
  Test-Path C:/github/claude-architect/notebooks/cca-f-exam-mastery.ipynb
  ```
  **Expect:** `True`. Off the 4-hour clock, so you won't teach from it, but you **will** point the cohort at it in the close. Twenty cells, zero errors, and it self-audits **30 of 30 CCA-F task statements** (D1 7/7, D2 5/5, D3 6/6, D4 6/6, D5 6/6). It creates no billable resources, so there's nothing to tear down.

- [ ] **Post-class example suites present**
  ```powershell
  @('examples/messages_api','examples/agents_api') |
    ForEach-Object { "$_ : $((Get-ChildItem "C:/github/claude-architect/$_" -Filter *.ipynb).Count) notebooks" }
  ```
  **Expect:** `examples/messages_api : 10 notebooks` and `examples/agents_api : 6 notebooks`. Both suites are smoke-verified green and are linked from the teaching notebooks' "Going further" appendices. The `messages_api` set is the API on-ramp; the `agents_api` set is the "Anthropic hosts the loop" counterpart, and all six of those archive their own resources when they finish.

- [ ] **Optional self-study reference: community practice-test HTML** (not required for class)
  ```powershell
  Test-Path C:/github/claude-architect/private/claude-certified-architect-main/practical_test_en.html
  ```
  **Expect:** `True` if cloned, otherwise skip. Alternate scoreboard UI; the Segment 4 notebook does not depend on it.

## 5. MCP configuration

- [ ] **`.mcp.json` parses and carries six servers**
  ```powershell
  (Get-Content C:/github/claude-architect/.mcp.json -Raw | ConvertFrom-Json).mcpServers.PSObject.Properties.Name
  ```
  **Expect:** six names: `filesystem`, `github`, `context7`, `internal-knowledge-base`, `oreilly-cca-mcp`, `cca-study-mcp`. Three transports across them (stdio, HTTP, SSE). Note the course's own demo server is **`oreilly-cca-mcp`**; it used to be called `document-mcp`, so ignore that older name if you see it anywhere.

- [ ] **Context7 MCP server reachable** (for live grounding of doc references)
  ```powershell
  claude mcp list
  ```
  **Expect:** `context7` (or similar) listed and connected

### Known non-bugs. Don't chase these on stage.

- **`internal-knowledge-base` will never connect.** It points at `mcp.example.com` and is a **teaching prop** that demonstrates SSE transport plus `${ENV_VAR}` expansion. Nothing in the course depends on it. Name it out loud when an attendee spots the red row.
- **MCP Inspector showing `404` plus `Unexpected token < ... not valid JSON`** means the endpoint returned an **HTML error page** where JSON was expected, which is what "nothing is listening at that URL" looks like. It gets labeled "oauth" only because discovery is the first step the Inspector attempts. Since **stdio servers can't return an HTTP 404**, a healthy stdio server sitting next to a failing HTTP or SSE one is the expected signature, not a problem to debug.

## 6. Notebook environment

- [ ] **Notebook env bootstrapped** via `uv run` (auto-creates `notebooks/.venv/` on first invocation, reuses it after):
  ```powershell
  cd C:/github/claude-architect
  uv run --project notebooks python -c "import anthropic; print(anthropic.__version__)"
  ```
  **Expect:** Version >= 0.40, no ImportError. The first run installs all six pinned deps from `notebooks/pyproject.toml`; subsequent runs start in seconds.

  **Fallback if `uv` is unavailable:** `pip install -r notebooks/requirements.txt` (kept in sync with `pyproject.toml`).

- [ ] **Jupyter / VS Code Python kernel**, open one notebook in VS Code, confirm kernel picker shows the `notebooks/.venv/` Python (3.13.x or newer)

- [ ] **pydantic importable** (using the same uv-managed venv):
  ```powershell
  uv run --project notebooks python -c "import pydantic; print(pydantic.VERSION)"
  ```
  **Expect:** Version >= 2.7, no ImportError

- [ ] **Segment 0 pre-flight notebook runs green**, open `notebooks/segment-0-pre-flight.ipynb` and Run All. Every cell prints `[OK]`. If any cell fails, fix it before going live.

## 7. Demo data fixtures

- [ ] **3 sample invoices already inline** in `notebooks/segment-3-invoice-extractor.ipynb` (clean / missing field / ambiguous). No external sample-data files needed; the strings live in the notebook itself.

## 8. Broadcast setup

- [ ] **O'Reilly platform tab open**, instructor console loaded
- [ ] **Screen-share rehearsed at 1080p**
- [ ] **VS Code terminal font** at least 16pt (audience needs to read it)
- [ ] **VS Code zoom level**, Ctrl+= until terminal text is legible from across the room
- [ ] **PowerShell color scheme**, high contrast, no blue-on-black

## 9. Backup plans

Full detail is in [`./EMERGENCY-CARD.md`](./EMERGENCY-CARD.md). The short version:

- [ ] **If a sidecar goes down (Inspector, Jupyter, MCP CLI):** re-run `.\start-sidecar-group.ps1 -NoJupyter` from the repo root. It's idempotent, so it repairs only the missing piece and leaves the healthy ones alone. About 15 seconds.
- [ ] **If API rate-limits during a live build:** switch to Claude.ai web (Claude Max session) and run the equivalent prompt manually
- [ ] **If a demo notebook errors:** fall back to the markdown walkthrough in the matching `domain-N-*.md` file
- [ ] **If Claude Code CLI itself fails:** the five `notebooks/*.ipynb` use the `anthropic` Python SDK directly and need no CLI; run cells in VS Code

## 10. Final 5 minutes before going live

- [ ] **Phone silenced**
- [ ] **Coffee / water within reach**
- [ ] **Notifications muted**, close Slack, Teams, Discord
- [ ] **COURSE-FLOW.md open in a second window**, your teaching reference
- [ ] **[`./EMERGENCY-CARD.md`](./EMERGENCY-CARD.md) open too**, so you never have to think while the cohort watches
- [ ] **Deep breath. You've done this 200+ times. Ship it.**
