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

- [ ] **Private cookbooks present**
  ```powershell
  Test-Path C:/github/claude-architect/private/claude-cookbooks-main/tool_use/customer_service_agent.ipynb
  ```
  **Expect:** `True`

## 4. Demo file inventory

- [ ] **Segment 1 demo: customer_service_agent.ipynb**
  ```powershell
  Test-Path C:/github/claude-architect/private/claude-cookbooks-main/tool_use/customer_service_agent.ipynb
  ```
  **Expect:** `True`

- [ ] **Segment 1 hook: hooks-example.py**
  ```powershell
  Test-Path C:/github/claude-architect/hooks-example.py
  ```
  **Expect:** `True`

- [ ] **Segment 2 MCP client config: repo's own .mcp.json**
  ```powershell
  Test-Path C:/github/claude-architect/.mcp.json
  ```
  **Expect:** `True`
  > Demo anchor for Segment 2 Demo A. Four servers covering all three transports (stdio, HTTP, SSE) with `${ENV}` expansion. Optional side-trip: `private/claude-cookbooks-main/managed_agents/cma-mcp/` shows what an MCP **server** looks like (vs. the **client config** we walk in the main demo).

- [ ] **Segment 2 CLAUDE.md (repo's own)**
  ```powershell
  Test-Path C:/github/claude-architect/CLAUDE.md
  ```
  **Expect:** `True`

- [ ] **Segment 3 extract notebook**
  ```powershell
  Test-Path C:/github/claude-architect/private/claude-cookbooks-main/tool_use/extracting_structured_json.ipynb
  ```
  **Expect:** `True`

- [ ] **Pydantic notebook (reference only, not live)**
  ```powershell
  Test-Path C:/github/claude-architect/private/claude-cookbooks-main/tool_use/tool_use_with_pydantic.ipynb
  ```
  **Expect:** `True`. Pydantic patterns are referenced inline in the Segment 3 demo; the notebook itself is not opened live.

- [ ] **Compaction notebook (self-study reference, not live)**
  ```powershell
  Test-Path C:/github/claude-architect/private/claude-cookbooks-main/tool_use/automatic-context-compaction.ipynb
  ```
  **Expect:** `True`. Demoted from live demo in the restructure; linked from Segment 3 Key Takeaways for cohort self-study after class.

- [ ] **CCA-F cert briefing exists**
  ```powershell
  Test-Path C:/github/claude-architect/CERT-PROGRAM-BRIEFING.md
  ```
  **Expect:** `True`. Tim talks over this live during the Segment 4 cert capstone (12 min block).

- [ ] **Practice questions Markdown exists**
  ```powershell
  Test-Path C:/github/claude-architect/PRACTICE-QUESTIONS.md
  ```
  **Expect:** `True`. The 60-question cohort take-home file.

- [ ] **Practice questions JSON parses to 60 entries**
  ```powershell
  python -c "import json; print(len(json.load(open(r'C:/github/claude-architect/practice-questions.json', encoding='utf-8'))))"
  ```
  **Expect:** `60`

- [ ] **Live practice-question UI loads** (the community HTML used live in Segment 4)
  ```powershell
  Test-Path C:/github/claude-architect/private/claude-certified-architect-main/practical_test_en.html
  ```
  **Expect:** `True`. Open in a browser tab before Segment 4 starts.

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

- [ ] **Jupyter / VS Code Python kernel**, open one notebook in VS Code, confirm kernel picker shows Python 3.13.x

- [ ] **Notebook deps importable** (smoke test the first cell of customer_service_agent.ipynb)
  ```powershell
  python -c "import anthropic; print(anthropic.__version__)"
  ```
  **Expect:** Version string, no ImportError

## 7. Demo data fixtures

- [ ] **3 sample invoices ready for Segment 3 demo** (clean / missing field / ambiguous)
  - Option A: Pre-saved at `C:/github/claude-architect/private/claude-cookbooks-main/tool_use/sample_data/`
  - Option B: Inline JSON in the notebook itself (fallback)

  Verify ONE of these is true before going live.

## 8. Broadcast setup

- [ ] **O'Reilly platform tab open**, instructor console loaded
- [ ] **Screen-share rehearsed at 1080p**
- [ ] **VS Code terminal font** at least 16pt (audience needs to read it)
- [ ] **VS Code zoom level**, Ctrl+= until terminal text is legible from across the room
- [ ] **PowerShell color scheme**, high contrast, no blue-on-black

## 9. Backup plans

- [ ] **If API rate-limits during a live build:** switch to Claude.ai web (Claude Max session) and run the equivalent prompt manually
- [ ] **If a demo notebook errors:** fall back to the markdown walkthrough in the matching `domain-N-*.md` file
- [ ] **If Claude Code CLI itself fails:** open the cookbook notebook in VS Code and run cells directly via `anthropic` Python SDK

## 10. Final 5 minutes before going live

- [ ] **Phone silenced**
- [ ] **Coffee / water within reach**
- [ ] **Notifications muted**, close Slack, Teams, Discord
- [ ] **COURSE-FLOW.md open in a second window**, your teaching reference
- [ ] **Deep breath. You've done this 200+ times. Ship it.**
