# Claude Architect Foundations - Notebooks

The seven teaching notebooks for the four-hour O'Reilly live training: five live-taught segments, one self-study deep dive (Segment 2.5), and one off-clock exam-mastery reference. The class is taught **from these notebooks**. Markdown cells carry the concepts. Code cells carry the demos. Run them top to bottom.

## What's here

| Notebook | Backs | Live runtime |
|---|---|---|
| `segment-0-pre-flight.ipynb` | Top-of-class verification (optional, 5 min) | 5 min |
| `segment-1-customer-support-agent.ipynb` | Segment 1: Building AI Agents That Use Tools | 50 min |
| `segment-2-tool-design-and-mcp.ipynb` | Segment 2: Tool Design, Integration, Claude Code | 50 min |
| `segment-2-5-control-surfaces.ipynb` | **Segment 2.5: Control surfaces, tool enumeration, Console assets (self-study)** | *off-clock* |
| `segment-3-invoice-extractor.ipynb` | Segment 3: Structured Output, Context, Reliability | 50 min |
| `segment-4-cca-f-capstone.ipynb` | Segment 4: CCA-F Certification Capstone | 50 min |
| `cca-f-exam-mastery.ipynb` | **Exam-mastery reference: all five domains, all 30 task statements (post-class study)** | *off-clock* |

Each segment notebook ships with **Learning Objectives**, **Concept** markdown cells, **Demo** code cells, **Exercise** prompts, **Key Takeaways**, and a **Bridge to next segment**. The four-hour class is the five live segments in order plus three ten-minute breaks. Segment 2.5 is a deep-dive self-study notebook that ties together every control surface the live segments touch lightly: all four `tool_choice` modes plus `disable_parallel_tool_use`, `stop_sequences`, `max_tokens` as a control lever, MCP `list_tools` discovery, and the live Claude Console asset surface (`memory_stores`, `vaults`, `agents`, `sessions`). Walked end to end it runs about 75 minutes against the live API.

## Cookbook anchor (optional self-study)

Several notebook cells cite Anthropic's official cookbook with `../claude-cookbooks-main/...` paths. The cookbook is **vendored at the repo root** (MIT, Copyright (c) 2023 Anthropic, see [`../claude-cookbooks-main/NOTICE.md`](../claude-cookbooks-main/NOTICE.md)). You get the whole reference library on `git clone`, no second clone required. Every code cell in `notebooks/` runs independently of the cookbook; the citations open Anthropic's authoritative notebooks for deeper study.

## Install (on-rails via uv)

```powershell
cd C:\github\claude-architect
uv run --project notebooks jupyter lab notebooks/
```

That one command does everything: creates `notebooks/.venv/` on first invocation, installs all dependencies from `notebooks/pyproject.toml`, and launches Jupyter Lab. Subsequent runs reuse the venv. Install `uv` once with `pip install uv` or `winget install astral-sh.uv`.

**Teaching sessions** should use the lifecycle helper scripts instead, which set the Jupyter AI v3 default persona to Jupyternaut (so chat messages route to someone) and handle Windows half-interrupted states cleanly on shutdown:

```powershell
.\scripts\run-jupyter.ps1            # default port 8888
.\scripts\stop-jupyter.ps1           # port-scoped, with PID fallback
```

**Fallback** (pip without uv):

```powershell
cd C:\github\claude-architect
pip install -r notebooks\requirements.txt
```

The `requirements.txt` file is kept in sync with `pyproject.toml` as a fallback path; either works.

Pinned versions:

- `anthropic>=0.40,<1.0`
- `pydantic>=2.7,<3.0`
- `python-dotenv>=1.0,<2.0`
- `ipykernel>=6.29`
- `jupyter>=1.1`
- `nbconvert>=7.16`

## Set the API key

The notebooks read `ANTHROPIC_API_KEY` from the environment. Pick one:

```powershell
$env:ANTHROPIC_API_KEY = "sk-ant-..."     # current shell only
```

Or create `C:\github\claude-architect\.env` (already in `.gitignore`):

```ini
ANTHROPIC_API_KEY=sk-ant-...
```

The notebooks call `dotenv.load_dotenv()` if the file exists. Never hardcode the key in a cell.

## Smoke test (run all seven end-to-end)

This is the dry-run before each cohort delivery. Budget roughly **$1** in API spend.

```powershell
cd C:\github\claude-architect
uv run --project notebooks jupyter nbconvert --to notebook --execute notebooks\segment-0-pre-flight.ipynb --output _smoke-0.ipynb
uv run --project notebooks jupyter nbconvert --to notebook --execute notebooks\segment-1-customer-support-agent.ipynb --output _smoke-1.ipynb
uv run --project notebooks jupyter nbconvert --to notebook --execute notebooks\segment-2-tool-design-and-mcp.ipynb --output _smoke-2.ipynb
uv run --project notebooks jupyter nbconvert --to notebook --execute notebooks\segment-2-5-control-surfaces.ipynb --output _smoke-2-5.ipynb
uv run --project notebooks jupyter nbconvert --to notebook --execute notebooks\segment-3-invoice-extractor.ipynb --output _smoke-3.ipynb
uv run --project notebooks jupyter nbconvert --to notebook --execute notebooks\segment-4-cca-f-capstone.ipynb --output _smoke-4.ipynb
uv run --project notebooks jupyter nbconvert --to notebook --execute notebooks\cca-f-exam-mastery.ipynb --output _smoke-exam-mastery.ipynb
Remove-Item notebooks\_smoke-*.ipynb
```

**Exit code 0 is not enough.** Read the printed counters on any cell that asserts an observable API behavior (`cache_creation_input_tokens`, `cache_read_input_tokens`, `stop_reason`, `tool_use` blocks). See [`../CLAUDE.md`](../CLAUDE.md#demo-verification-norm-smoke-before-commit) for the demo-verification norm and the cache-floor gotcha.

Each run must finish with no exceptions. If anything fails, fix it **before** class.

## Voice lint (zero hits required)

The Tim-voice rules from `CLAUDE.md` apply to every markdown cell. Run before committing:

```powershell
python -c "
import json, re, sys, pathlib
patterns = {
    'em-dash': r'—',
    'AWS-mention': r'\bAWS\b',
    'ask-as-noun': r'\bthe\s+ask\b|\ban\s+ask\b|\bbig\s+ask\b|\bheavy\s+ask\b',
}
hits = 0
for nb_path in pathlib.Path('notebooks').glob('*.ipynb'):
    nb = json.loads(nb_path.read_text(encoding='utf-8'))
    for i, cell in enumerate(nb['cells']):
        if cell['cell_type'] != 'markdown':
            continue
        text = ''.join(cell['source'])
        for label, pat in patterns.items():
            for m in re.finditer(pat, text):
                print(f'{nb_path.name} cell {i} [{label}]: {m.group(0)!r}')
                hits += 1
sys.exit(1 if hits else 0)
"
```

## Clear outputs before commit (mandatory)

Cell outputs can leak API key fragments or transient data. Always clear before committing:

```powershell
uv run --project notebooks jupyter nbconvert --clear-output --inplace notebooks\*.ipynb
```

## Pre-class checklist

Before each cohort delivery, in order:

1. `uv run --project notebooks python -c "import anthropic; print(anthropic.__version__)"` (catches SDK drift early; auto-syncs the venv if `pyproject.toml` changed)
2. `$env:ANTHROPIC_API_KEY` set in the shell you will record from
3. Run the smoke command above (budget ~$1)
4. Run the voice lint (must return zero hits)
5. Read `..\docs\PRE-CLASS-CHECKLIST.md` for everything outside this directory
