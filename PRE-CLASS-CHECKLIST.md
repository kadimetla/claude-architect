# Pre-class checklist - Claude Architect Foundations

> Run this 30 minutes before going live. Every box must be checked, every **Expect:** must match. If a step fails, fix it before moving on. Nothing below assumes a broken step succeeded.
>
> **First time teaching this course?** Start with [`./INSTRUCTOR-SETUP.md`](./INSTRUCTOR-SETUP.md) for the multi-day setup arc. This file assumes that setup is already complete.

**Course:** Claude Architect Foundations (CCA-F Crash Course), 4 hours, O'Reilly Live
**Owner:** Tim Warner
**Repo:** `C:\github\claude-architect`
**Stack:** Windows 11, PowerShell 7, VS Code, Python 3.13, Claude Code CLI

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

The class is taught **from the five notebooks in `./notebooks/`**. Each notebook IS its segment.

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
  Test-Path C:/github/claude-architect/CERT-PROGRAM-BRIEFING.md
  ```
  **Expect:** `True`. The Segment 4 notebook references it for the full week-before punchlist.

- [ ] **Practice questions Markdown (cohort take-home)**
  ```powershell
  Test-Path C:/github/claude-architect/PRACTICE-QUESTIONS.md
  ```
  **Expect:** `True`. 60-question take-home reference.

- [ ] **Practice questions JSON parses to 60 entries**
  ```powershell
  python -c "import json; print(len(json.load(open(r'C:/github/claude-architect/practice-questions.json', encoding='utf-8'))))"
  ```
  **Expect:** `60`. The Segment 4 notebook samples 10 questions from this file.

- [ ] **Optional self-study reference: community practice-test HTML** (not required for class)
  ```powershell
  Test-Path C:/github/claude-architect/private/claude-certified-architect-main/practical_test_en.html
  ```
  **Expect:** `True` if cloned, otherwise skip. Alternate scoreboard UI; the Segment 4 notebook does not depend on it.

## 5. MCP configuration

- [ ] **`.mcp.json` parses (if present at repo root)**
  ```powershell
  if (Test-Path C:/github/claude-architect/.mcp.json) {
    try { Get-Content C:/github/claude-architect/.mcp.json | ConvertFrom-Json | Out-Null; "valid" }
    catch { "INVALID: $_" }
  } else { "no project .mcp.json (using user-level)" }
  ```
  **Expect:** `valid` or `no project .mcp.json (using user-level)`

- [ ] **Context7 MCP server reachable** (for live grounding of doc references)
  ```powershell
  claude mcp list
  ```
  **Expect:** `context7` (or similar) listed and connected

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

- [ ] **If API rate-limits during a live build:** switch to Claude.ai web (Claude Max session) and run the equivalent prompt manually
- [ ] **If a demo notebook errors:** fall back to the markdown walkthrough in the matching `domain-N-*.md` file
- [ ] **If Claude Code CLI itself fails:** the five `notebooks/*.ipynb` use the `anthropic` Python SDK directly and need no CLI; run cells in VS Code

## 10. Final 5 minutes before going live

- [ ] **Phone silenced**
- [ ] **Coffee / water within reach**
- [ ] **Notifications muted**, close Slack, Teams, Discord
- [ ] **COURSE-FLOW.md open in a second window**, your teaching reference
- [ ] **Deep breath. You've done this 200+ times. Ship it.**
