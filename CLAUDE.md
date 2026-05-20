# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

Teaching and reference material for the **Claude Architect Foundations** 4-hour live training (O'Reilly Media). The course is **skills-first** for Segments 1-3, then closes with a **CCA-F certification capstone** in Segment 4 (cert briefing + weighted practice questions). Domain 5 (Context Management) is folded into Segment 3 alongside Domain 4.

**The class is taught from the five live-teaching Jupyter notebooks in `./notebooks/`.** Each notebook IS its segment - markdown cells carry the concepts, code cells carry the demos. A sixth **self-study deep-dive notebook** (Segment 2.5) ships alongside for cohort homework and Q&A overflow but is not on the 4-hour clock. The .md files below are the supporting reference scaffolds.

The repo ships these artifacts:

- `notebooks/segment-0-pre-flight.ipynb` - top-of-class environment verification (5 min, optional)
- `notebooks/segment-1-customer-support-agent.ipynb` - Segment 1 (Domain 1)
- `notebooks/segment-2-tool-design-and-mcp.ipynb` - Segment 2 (Domains 2 + 3)
- `notebooks/segment-2-5-control-surfaces.ipynb` - **Segment 2.5 self-study deep dive** (all five domains): full `tool_choice` modes + `disable_parallel_tool_use`, `stop_sequences` and `max_tokens` as control levers, MCP `list_tools` discovery, and the Claude Console asset surface (`memory_stores`, `vaults`, `agents`, `sessions`). Not live-taught.
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

For interactive teaching sessions, prefer the **lifecycle helper scripts** over a bare `uv run jupyter lab`:

```powershell
.\scripts\run-jupyter.ps1            # default port 8888, overrides Jupyter AI default persona to Jupyternaut
.\scripts\stop-jupyter.ps1           # port-scoped clean shutdown with PID fallback for Windows half-states
```

`run-jupyter.ps1` sets `PersonaManager.default_persona_id` to the Jupyter AI v3 Jupyternaut so chat messages route to someone (the upstream default points at the older package ID and silently routes to nobody). `stop-jupyter.ps1` matches the server by `root_dir` so it never stops an unrelated Jupyter on the box, and falls back to `Stop-Process` on the exact PID if the graceful path hangs (Jupyter AI can leave the server half-interrupted on Windows). For headless smoke runs (`nbconvert --execute`) you do not need either script - nbconvert spawns its own kernel.

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

## Demo-verification norm: smoke before commit

Any notebook cell that asserts an observable API behavior (e.g., prints `cache_creation_input_tokens`, `cache_read_input_tokens`, `stop_reason` transitions, `tool_use` blocks, hook side effects, structured-error retries) must be **smoke-verified end-to-end against the live API** before it lands in `main`. Budget **~$0.05 per segment notebook** and run:

```powershell
uv run --project notebooks jupyter nbconvert --to notebook --execute notebooks/segment-N-...ipynb --output _smoke-N.ipynb
```

Then read the cell's output and confirm it matches what the printed assertion claims. **A passing exit code is not enough** - `nbconvert` exits 0 as long as no cell raised, even if the demo's printed numbers contradict the surrounding markdown (this is exactly what happened with the segment-2 cache demo: the cell ran clean but produced `cache_read=0` when the prose promised a cache hit).

Smoke artifacts (`notebooks/_smoke-*.ipynb`) are gitignored - they are transient by design.

Rule of thumb: if the markdown above a cell makes a concrete claim ("the second call reads from cache", "stop_reason flips to end_turn"), the cell must be smoke-verified. Voice-lint and `python scripts/build-notebooks.py` confirm structure; only a live API run confirms behavior.

### Cache-floor gotcha (the 2026-05 lesson)

Any cell that demonstrates `cache_control` must clear the **model-specific cacheable-prefix floor** or caching silently no-ops with `cache_creation=0, cache_read=0`. The exit code stays 0; only the printed counters reveal the failure. Floors:

- **Sonnet 4.x**: 1024 tokens
- **Haiku 4.5**: 4096 tokens (4x higher - the trap when flipping demos from Sonnet to Haiku)

When changing a notebook's default model, audit every cache demo for prefix size. The 2026-05 Sonnet 4.6 -> Haiku 4.5 flip broke both segment-2 (tool block ~1280 tokens) and segment-3 (vendor policy ~250 tokens) because the cached prefix sat between the two floors. The fix in both cases was to enlarge the cacheable content with **realistic production prose** (system prompt, policy block, escalation playbook) targeting **+25% above the floor** so tokenizer drift does not push you back under.

## Stack defaults (per `~/.claude/CLAUDE.md`)

| Concern | Default |
|---|---|
| Shell | **PowerShell 7+** (Bash only as fallback) |
| OS | **Windows 11** (the live training runs here) |
| Runtime | **Node.js 18+** for SDK examples, **Python 3.13+** for notebooks (`examples/mcp_cli/` pinned to 3.13 via `.python-version` because the committed `jiter` wheel has no 3.14 build) |
| Cloud | **Azure** when cloud comes up |

## Model policy (course-wide, do not regress)

- **Haiku 4.5 (`claude-haiku-4-5`) is the default** for every notebook and every script in this repo. It handles tool use, agentic loops, structured errors, caching demos, and MCP discovery at production quality for ~1/5 the Sonnet cost.
- **Sonnet 4.6 (`claude-sonnet-4-6`) is reserved** for places where reasoning depth measurably lifts behavior. The only such place in this course is **Segment 3** (nested invoice schemas with retry-on-validation-error). The Segment 3 builder's `MODEL` line carries a comment justifying the exception.
- **Opus is never used** in code in this repo. Three legacy mentions in caching-floor prose ("Sonnet 4.x: 1024 / Haiku 4.5: 4096 tokens") have been stripped of their "/Opus" tail; do not re-add it.
- **Console-managed agents** (e.g. Deep Researcher) carry their own configured `model` field. The SDK respects whatever the Console sets, so the agent's resolved model may legitimately be Sonnet 4.6 even when this notebook's default is Haiku 4.5. That is not a policy violation; it is the agent's recipe.
- When adding a new MODEL constant, prefer the unversioned alias (`claude-haiku-4-5`) unless a specific feature requires a dated snapshot (Segment 0's pre-flight uses `claude-haiku-4-5-20251001` to pin the SDK floor check).

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

# Verify all six teaching notebooks present (five live + one self-study deep dive)
ls notebooks/segment-0-pre-flight.ipynb \
   notebooks/segment-1-customer-support-agent.ipynb \
   notebooks/segment-2-tool-design-and-mcp.ipynb \
   notebooks/segment-2-5-control-surfaces.ipynb \
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

# Smoke test all six notebooks against the API (budget ~$1)
uv run --project notebooks jupyter nbconvert --to notebook --execute notebooks/segment-0-pre-flight.ipynb --output _smoke-0.ipynb
uv run --project notebooks jupyter nbconvert --to notebook --execute notebooks/segment-1-customer-support-agent.ipynb --output _smoke-1.ipynb
uv run --project notebooks jupyter nbconvert --to notebook --execute notebooks/segment-2-tool-design-and-mcp.ipynb --output _smoke-2.ipynb
uv run --project notebooks jupyter nbconvert --to notebook --execute notebooks/segment-2-5-control-surfaces.ipynb --output _smoke-2-5.ipynb
uv run --project notebooks jupyter nbconvert --to notebook --execute notebooks/segment-3-invoice-extractor.ipynb --output _smoke-3.ipynb
uv run --project notebooks jupyter nbconvert --to notebook --execute notebooks/segment-4-cca-f-capstone.ipynb --output _smoke-4.ipynb

# Regenerate practice questions from upstream HTML (run only after the community repo updates)
python scripts/extract-practice-questions.py
```

There is no build or test suite, but `package.json` ships two real scripts: `npm run lint:voice` (runs the voice-lint sweep above) and `npm run preflight` (executes `scripts/preflight.ps1`). The repo's "tests" are these scripts plus the live PRE-CLASS-CHECKLIST run-through.

`scripts/build-notebooks.py` is **idempotent** (deterministic cell IDs via sha256). A second run with no source changes produces byte-identical `.ipynb` files; if `git status` reports modifications after a rebuild, real content changed.

## Claude Console asset surface (Managed Agents)

As of the 2026-05 sprint, **Segment 2.5** integrates the live Claude Console asset surface in Tim's **Default workspace**. All four resources are reachable via the SDK with the beta header `anthropic-beta: managed-agents-2026-04-01`:

| Console asset | SDK path | Provisioned name / ID | Domain anchor |
|---|---|---|---|
| Memory store | `client.beta.memory_stores` | `oreilly-memory-store` / `memstore_01CxRGu37BSyxYQaser8jXGa` | Domain 5 (persistence that survives restarts) |
| Vault | `client.beta.vaults` (+ `.credentials.mcp_oauth_validate`) | `oreilly-vault` / `vlt_011CbDoSH1GZCgFsbmkDsP51` | Domain 3 (secrets hygiene) |
| Agent | `client.beta.agents` | Deep researcher / `agent_01HEnqX2B62eYmyq1dLHcoWV` (Sonnet 4.6, template `deep-research`) | Domain 1 (managed loop vs hand-rolled) |
| Session | `client.beta.sessions` (the runtime) | created on demand via `sessions.create(agent=..., environment_id=..., vault_ids=[...])` | Domain 1 (agent + env + vault as one runtime) |

These are first-class SDK resources. The same key that authenticates `messages.create()` authenticates the full managed-agents surface. The Console UI is one of two ways to drive them; the SDK is the other. Console-managed agents carry their own configured `model` field that the SDK respects, so the Deep Researcher resolves to Sonnet 4.6 even when the calling notebook's default `MODEL` is Haiku 4.5 - this is the agent's recipe, not a model-policy violation.

## When in doubt

- For Anthropic docs grounding, use Context7 MCP: `/websites/platform_claude_en_api` (Claude API docs) and `/websites/code_claude` (Claude Code docs) are the two authoritative library IDs.
- For demo questions, prefer Anthropic-authored notebooks in `claude-cookbooks-main/` over the community-authored `private/claude-certified-architect-main/` repo.
