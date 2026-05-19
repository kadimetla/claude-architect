# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

Teaching and reference material for the **Claude Architect Foundations** 4-hour live training (O'Reilly Media). The course is **skills-first** for Segments 1-3, then closes with a **CCA-F certification capstone** in Segment 4 (cert briefing + weighted practice questions). Domain 5 (Context Management) is folded into Segment 3 alongside Domain 4.

**The class is taught from the five Jupyter notebooks in `./notebooks/`.** Each notebook IS its segment - markdown cells carry the concepts, code cells carry the demos. The .md files below are the supporting reference scaffolds.

The repo ships these artifacts:

- `notebooks/segment-0-pre-flight.ipynb` - top-of-class environment verification (5 min, optional)
- `notebooks/segment-1-customer-support-agent.ipynb` - Segment 1 (Domain 1)
- `notebooks/segment-2-tool-design-and-mcp.ipynb` - Segment 2 (Domains 2 + 3)
- `notebooks/segment-3-invoice-extractor.ipynb` - Segment 3 (Domains 4 + 5)
- `notebooks/segment-4-cca-f-capstone.ipynb` - Segment 4 (cert briefing + weighted practice questions)
- `notebooks/README.md`, `notebooks/pyproject.toml`, `notebooks/uv.lock`, `notebooks/requirements.txt` - notebook setup (uv-native, pip fallback), smoke commands, voice-lint
- `scripts/build-notebooks.py` + `scripts/_notebooks/*.py` - source-of-truth Python builders; the .ipynb files are generated artifacts
- `COURSE-FLOW.md` - master instructor punchlist (4 segments × 50 min, demos, exercises, bridges)
- `PRE-CLASS-CHECKLIST.md` - instructor pre-flight (PowerShell)
- `domain-1-agentic.md` through `domain-5-context.md` - post-course reference scaffolds, one per CCA-F exam domain
- `CERT-PROGRAM-BRIEFING.md` - Segment 4 talk-track reference (exam mechanics, domain weights, week-before punchlist, all public-sourced)
- `PRACTICE-QUESTIONS.md` - 60-question cohort take-home, extracted from the community study repo with provenance disclaimer
- `practice-questions.json` - machine-readable practice-question source (Segment 4 notebook samples 10 from this)
- `scripts/extract-practice-questions.py` - build-time extractor that regenerates the two practice-question files from the upstream HTML
- `.mcp.json` - Segment 2 MCP config anchor (4 servers, 3 transports, env-var expansion)
- `hooks-example.py` - real PreToolUse / PostToolUse reference cited from Segment 1
- `coordinator-subagent-sketch.py` - Domain 1 coordinator-subagent scaffold (renamed from the old `testing.md`)
- `examples/mcp_cli/` - vendored reference MCP CLI app from Anthropic's Skilljar course (Segment 2 anchor; separate uv project with its own `pyproject.toml`, `uv.lock`, and `.python-version` pinning 3.13). Attribution in `examples/mcp_cli/NOTICE.md`.
- `claude-cookbooks-main/` - vendored copy of Anthropic's official Claude Cookbooks (MIT, Copyright (c) 2023 Anthropic). Attribution in `claude-cookbooks-main/NOTICE.md`.
- `slides/warner-claude-architect-may-2026.pptx` - course deck, built by `scripts/build-deck.py`

## How this repo bootstraps (read before running anything)

The canonical learner setup is **one command** from the repo root:

```powershell
uv run --project notebooks jupyter lab notebooks/
```

`uv run` auto-creates `notebooks/.venv/` on first invocation (~20s cold, including 107 packages from `notebooks/uv.lock`) and reuses it on every subsequent run (~1.5s warm). Do **not** suggest `pip install` first - `uv run` is the canonical entry point. Pinned deps live in `notebooks/pyproject.toml`; `notebooks/requirements.txt` is a generated pip-fallback for boxes without `uv`, kept in sync via `uv export`.

Smoke tests run via `uv run` too: `uv run --project notebooks jupyter nbconvert --to notebook --execute notebooks/segment-0-pre-flight.ipynb --output _smoke-0.ipynb` (budget ~$0.05 per notebook against the live API). Builder scripts (`scripts/build-notebooks.py` and `scripts/_notebooks/*.py`) are pure Python with no third-party deps; they run with the system Python directly, no venv required.

`examples/mcp_cli/` is a **separate uv project** with its own `pyproject.toml` and `uv.lock`. Bootstrap it independently with `cd examples/mcp_cli && uv run main.py`. Intentional separation: it is reference code from Anthropic's Skilljar course (see `examples/mcp_cli/NOTICE.md`), not part of the notebook environment.

## Architecture: how the pieces fit

This repo has no application layer. The architecture IS the teaching choreography:

- **`COURSE-FLOW.md` is the orchestrator.** Every demo block points at a real file path. Every segment maps to one or more CCA-F domains. The 4 teaching segments compress 5 exam domains (Segment 2 covers Domains 2 + 3, the heaviest pairing at 38% of exam weight).
- **`domain-*.md` files are reference scaffolds**, not lesson plans. They expand the 80-word teaching topics in COURSE-FLOW into ~1000-word references with cookbook anchors, production tips, and Anthropic docs links.
- **`claude-cookbooks-main/`** is Anthropic's official cookbook, **vendored at the repo root** (committed, MIT, Copyright (c) 2023 Anthropic, attribution in `claude-cookbooks-main/NOTICE.md`). Notebooks cite it with `../claude-cookbooks-main/...` paths. Every Demo: in COURSE-FLOW points at a notebook there. Treat as authoritative.
- **`private/claude-certified-architect-main/`** (gitignored) is a **separate community study repo** (note: name is close to this course package but the repos are distinct - `claude-certified-architect` is community-contributed, `claude-architect` is Tim's). Multi-language guides + practical_test HTMLs. **Not authoritative** because the exam isn't public yet. Use for context, not citation.
- **`research/`** holds Anthropic-Confidential source material (CCA-F Exam Guide PDF + markdown conversions). See "What NOT to commit" below.

## Required reading order before editing

1. This file
2. `~/.claude/CLAUDE.md` (Tim's personal voice + stack rules - load-bearing)
3. `COURSE-FLOW.md` to understand the teaching arc before touching any `domain-*.md`
4. The matching `domain-*.md` if you're editing a segment

## Voice rules (verified via Grep)

These are not aesthetic preferences. They are linter errors in this repo:

- **No em dashes.** Use ` - ` (hyphen with spaces), commas, or periods.
- **No "ask" as a noun.** Use "request", "question", "proposal".
- **No AWS mentions.** Azure-first if cloud comes up.
- **Bold key terms with `**term**`.** Tim is red/green colorblind and navigates by scanning bold.
- **No glazing openers** ("great question", "you're absolutely right", "excellent").

After editing any MD file, run:

```bash
grep -P "—|\bAWS\b" COURSE-FLOW.md PRE-CLASS-CHECKLIST.md domain-*.md
```

Expect zero matches. The 2026-05-16 build leaked 18 em dashes into `domain-2-tools-mcp.md` despite explicit prompts; agent self-reports of "voice compliant" cannot be trusted - verify with Grep.

## Editing conventions

- **Match `course-plan-april-2026.md` style** when extending COURSE-FLOW: 50-min segments with NO clock times, inline `(X minutes)` sub-topic budgets, `**Demo:**` blocks with numbered steps, "Learning Objectives" + "Key Takeaways" + verbatim bridge sentences between segments.
- **Every demo path must resolve.** Before adding a `Demo:` reference, verify the file exists with Glob.
- **Domain file template** (apply to every `domain-N-*.md`): `# Domain N: <Name>` header, "What this domain covers" → "Core concepts" (3-5 H3s) → "Demo anchor" (links back to matching COURSE-FLOW segment) → "Production tips" (Tim's voice) → "Further reading".
- **Minute math for COURSE-FLOW segments must sum to 50** (40 content + 5 exercise + 5 Q&A). Verify before saving.

## Code conventions

- Python examples include docstrings explaining the production pattern being demonstrated
- Comments explain **why**, not what (these are teaching materials)
- Type hints on all Python function signatures
- Tool errors follow the structured pattern: `is_error: true` plus `errorCategory` and `isRetryable` fields inside the tool_result content (never raise exceptions)
- All API key references use `os.environ` / `$env:ANTHROPIC_API_KEY` - never hardcoded

## Stack defaults (per `~/.claude/CLAUDE.md`)

| Concern | Default |
|---|---|
| Shell | **PowerShell 7+** (Bash only as fallback) |
| OS | **Windows 11** (the live training runs here) |
| Runtime | **Node.js 18+** for SDK examples, **Python 3.13+** for notebooks (`examples/mcp_cli/` pinned to 3.13 via `.python-version` because the committed `jiter` wheel has no 3.14 build) |
| Cloud | **Azure** when cloud comes up |

## What NOT to commit

- **`research/` directory** - contains the CCA-F Exam Guide PDF and its markitdown conversion (Anthropic Confidential, NTK). Already excluded by `.gitignore` line 3 (verified). Never quote verbatim in any committed file; paraphrase only and cite the public Anthropic web page / Exam Policy instead.
- The Pearson proposal documents
- API keys, tokens, credentials
- Actual exam questions or answers
- Content from `private/` (already gitignored)

## Common operations

```bash
# Verify all course artifacts present
ls COURSE-FLOW.md PRE-CLASS-CHECKLIST.md domain-*.md CERT-PROGRAM-BRIEFING.md PRACTICE-QUESTIONS.md practice-questions.json scripts/extract-practice-questions.py

# Verify all five teaching notebooks present
ls notebooks/segment-0-pre-flight.ipynb \
   notebooks/segment-1-customer-support-agent.ipynb \
   notebooks/segment-2-tool-design-and-mcp.ipynb \
   notebooks/segment-3-invoice-extractor.ipynb \
   notebooks/segment-4-cca-f-capstone.ipynb

# Voice lint sweep on Tim-authored files (must return 0 matches).
# PRACTICE-QUESTIONS.md is community-sourced and excluded; its disclaimer header covers voice drift.
grep -P "—|\bAWS\b" COURSE-FLOW.md PRE-CLASS-CHECKLIST.md CLAUDE.md CERT-PROGRAM-BRIEFING.md domain-*.md

# Voice lint sweep on notebook markdown cells (must return 0 matches)
python -c "import json, re, pathlib, sys; hits=0; \
[print(f'{p.name} cell {i}: {m.group(0)!r}') or (hits := hits + 1) \
 for p in pathlib.Path('notebooks').glob('*.ipynb') \
 for i, c in enumerate(json.loads(p.read_text(encoding='utf-8'))['cells']) \
 if c['cell_type'] == 'markdown' \
 for m in re.finditer(r'—|\bAWS\b', ''.join(c['source']))]; sys.exit(1 if hits else 0)"

# Verify domain headers are correct (1-5, no mislabels)
grep -nH "^# Domain" domain-*.md

# Verify .mcp.json parses
node -e "JSON.parse(require('fs').readFileSync('.mcp.json'))" && echo ok

# Verify practice-question JSON parses and has 60 entries
python -c "import json; print(len(json.load(open('practice-questions.json', encoding='utf-8'))))"

# Rebuild notebooks from source after editing scripts/_notebooks/*.py
python scripts/build-notebooks.py

# Smoke test all five notebooks against the API (budget ~$1)
uv run --project notebooks jupyter nbconvert --to notebook --execute notebooks/segment-0-pre-flight.ipynb --output _smoke-0.ipynb
uv run --project notebooks jupyter nbconvert --to notebook --execute notebooks/segment-1-customer-support-agent.ipynb --output _smoke-1.ipynb
uv run --project notebooks jupyter nbconvert --to notebook --execute notebooks/segment-2-tool-design-and-mcp.ipynb --output _smoke-2.ipynb
uv run --project notebooks jupyter nbconvert --to notebook --execute notebooks/segment-3-invoice-extractor.ipynb --output _smoke-3.ipynb
uv run --project notebooks jupyter nbconvert --to notebook --execute notebooks/segment-4-cca-f-capstone.ipynb --output _smoke-4.ipynb

# Regenerate practice questions from upstream HTML (run only after the community repo updates)
python scripts/extract-practice-questions.py
```

There is no build or test suite, but `package.json` ships two real scripts: `npm run lint:voice` (runs the voice-lint sweep above) and `npm run preflight` (executes `scripts/preflight.ps1`). The repo's "tests" are these scripts plus the live PRE-CLASS-CHECKLIST run-through.

`scripts/build-notebooks.py` is **idempotent** (deterministic cell IDs via sha256). A second run with no source changes produces byte-identical `.ipynb` files; if `git status` reports modifications after a rebuild, real content changed.

## When in doubt

- For Anthropic docs grounding, use Context7 MCP: `/websites/platform_claude_en_api` (Claude API docs) and `/websites/code_claude` (Claude Code docs) are the two authoritative library IDs.
- For demo questions, prefer Anthropic-authored notebooks in `claude-cookbooks-main/` over the community-authored `private/claude-certified-architect-main/` repo.
