# Claude Architect Foundations - Notebooks

The five teaching notebooks that back the four-hour O'Reilly live training. The class is taught **from these notebooks**. Markdown cells carry the concepts. Code cells carry the demos. Run them top to bottom.

## What's here

| Notebook | Backs | Live runtime |
|---|---|---|
| `segment-0-pre-flight.ipynb` | Top-of-class verification (optional, 5 min) | 5 min |
| `segment-1-customer-support-agent.ipynb` | Segment 1: Building AI Agents That Use Tools | 50 min |
| `segment-2-tool-design-and-mcp.ipynb` | Segment 2: Tool Design, Integration, Claude Code | 50 min |
| `segment-3-invoice-extractor.ipynb` | Segment 3: Structured Output, Context, Reliability | 50 min |
| `segment-4-cca-f-capstone.ipynb` | Segment 4: CCA-F Certification Capstone | 50 min |

Each segment notebook ships with **Learning Objectives**, **Concept** markdown cells, **Demo** code cells, **Exercise** prompts, **Key Takeaways**, and a **Bridge to next segment**. The four-hour class is the five notebooks in order plus three ten-minute breaks.

## Install

```powershell
cd C:\github\claude-architect
pip install -r notebooks\requirements.txt
```

Pinned versions:

- `anthropic>=0.40,<1.0`
- `pydantic>=2.7,<3.0`
- `python-dotenv>=1.0,<2.0`
- `ipykernel>=6.29`

## Set the API key

The notebooks read `ANTHROPIC_API_KEY` from the environment. Pick one:

```powershell
$env:ANTHROPIC_API_KEY = "sk-ant-..."     # current shell only
```

Or create `C:\github\claude-architect\.env` (already in `.gitignore`):

```
ANTHROPIC_API_KEY=sk-ant-...
```

The notebooks call `dotenv.load_dotenv()` if the file exists. Never hardcode the key in a cell.

## Smoke test (run all five end-to-end)

This is the dry-run before each cohort delivery. Budget roughly **$1** in API spend.

```powershell
cd C:\github\claude-architect
jupyter nbconvert --to notebook --execute notebooks\segment-0-pre-flight.ipynb --output _smoke-0.ipynb
jupyter nbconvert --to notebook --execute notebooks\segment-1-customer-support-agent.ipynb --output _smoke-1.ipynb
jupyter nbconvert --to notebook --execute notebooks\segment-2-tool-design-and-mcp.ipynb --output _smoke-2.ipynb
jupyter nbconvert --to notebook --execute notebooks\segment-3-invoice-extractor.ipynb --output _smoke-3.ipynb
jupyter nbconvert --to notebook --execute notebooks\segment-4-cca-f-capstone.ipynb --output _smoke-4.ipynb
Remove-Item notebooks\_smoke-*.ipynb
```

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
jupyter nbconvert --clear-output --inplace notebooks\*.ipynb
```

## Pre-class checklist

Before each cohort delivery, in order:

1. `pip install -r notebooks\requirements.txt` (catch SDK drift early)
2. `$env:ANTHROPIC_API_KEY` set in the shell you will record from
3. Run the smoke command above (budget ~$1)
4. Run the voice lint (must return zero hits)
5. Read `..\PRE-CLASS-CHECKLIST.md` for everything that lives outside this directory
