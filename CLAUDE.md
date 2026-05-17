# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

Teaching and reference material for the **Claude Architect Foundations** 4-hour live training (O'Reilly Media). The course is **skills-first**: it teaches production patterns for the Claude Architect role and describes the CCA-F certification structure without teaching to specific exam items (the exam isn't publicly available yet).

The repo ships seven artifacts learners and the instructor use:

- `COURSE-FLOW.md` - master instructor punchlist (4 segments × 50 min, demos, exercises, bridges)
- `PRE-CLASS-CHECKLIST.md` - instructor pre-flight (PowerShell, 35 checks)
- `domain-1-agentic.md` through `domain-5-context.md` - post-course reference scaffolds, one per CCA-F exam domain
- `.mcp.json` - Segment 2 Demo A anchor (4 servers, 3 transports, env-var expansion)
- `hooks-example.py`, `SKILL.md`, `scenario-cicd-integration.md`, `testing.md` - inline demo assets

## Architecture: how the pieces fit

This repo has no application layer. The architecture IS the teaching choreography:

- **`COURSE-FLOW.md` is the orchestrator.** Every demo block points at a real file path. Every segment maps to one or more CCA-F domains. The 4 teaching segments compress 5 exam domains (Segment 2 covers Domains 2 + 3, the heaviest pairing at 38% of exam weight).
- **`domain-*.md` files are reference scaffolds**, not lesson plans. They expand the 80-word teaching topics in COURSE-FLOW into ~1000-word references with cookbook anchors, production tips, and Anthropic docs links.
- **`private/claude-cookbooks-main/`** (gitignored) is Anthropic's official cookbook. Every Demo: in COURSE-FLOW points at a notebook there. Treat as authoritative.
- **`private/claude-certified-architect-main/`** (gitignored) is a third-party community study repo. Multi-language guides + practical_test HTMLs. **Not authoritative** because the exam isn't public yet. Use for context, not citation.
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
| Runtime | **Node.js 18+** for SDK examples, **Python 3.13** for notebooks |
| Cloud | **Azure** when cloud comes up |

## What NOT to commit

- **`research/` directory** - contains the CCA-F Exam Guide PDF and its markitdown conversion (Anthropic Confidential, NTK). **`.gitignore` currently excludes `private/` but NOT `research/`** - add `research/` to `.gitignore` before any `git add .` or surface the risk to Tim first.
- The Pearson proposal documents
- API keys, tokens, credentials
- Actual exam questions or answers
- Content from `private/` (already gitignored)

## Common operations

```bash
# Verify all 7 course artifacts present
ls COURSE-FLOW.md PRE-CLASS-CHECKLIST.md domain-*.md

# Voice lint sweep (must return 0 matches)
grep -P "—|\bAWS\b" COURSE-FLOW.md PRE-CLASS-CHECKLIST.md domain-*.md

# Verify domain headers are correct (1-5, no mislabels)
grep -nH "^# Domain" domain-*.md

# Verify .mcp.json parses
node -e "JSON.parse(require('fs').readFileSync('.mcp.json'))" && echo ok

# Verify demo notebooks exist
ls private/claude-cookbooks-main/tool_use/customer_service_agent.ipynb \
   private/claude-cookbooks-main/tool_use/extracting_structured_json.ipynb \
   private/claude-cookbooks-main/tool_use/tool_use_with_pydantic.ipynb \
   private/claude-cookbooks-main/tool_use/automatic-context-compaction.ipynb
```

There is no build, no test suite, no lint command (the `npm test` script is a placeholder). The repo's "tests" are the verification commands above plus the live PRE-CLASS-CHECKLIST run-through.

## When in doubt

- For Anthropic docs grounding, use Context7 MCP: `/websites/platform_claude_en_api` (Claude API docs) and `/websites/code_claude` (Claude Code docs) are the two authoritative library IDs.
- For demo questions, prefer notebooks in `private/claude-cookbooks-main/` over the third-party `private/claude-certified-architect-main/` repo.
