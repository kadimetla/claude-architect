# NOTICE - Vendored copy of Anthropic Claude Cookbooks

This directory (`claude-cookbooks-main/`) is a **vendored copy of Anthropic's official Claude Cookbooks**, distributed under the MIT License. It is **not authored by Tim Warner** and is **not part of the original work** in the `claude-architect` repository.

## Why it lives here

The five teaching notebooks in `../notebooks/` cite specific cookbook examples (e.g., `customer_service_agent.ipynb`, `tool_use_with_pydantic.ipynb`, `automatic-context-compaction.ipynb`) as authoritative references and post-class self-study labs. Vendoring the cookbook at the repo root means those `../claude-cookbooks-main/...` citations resolve out of the box for every learner who clones this repo. No second `git clone`, no broken links during class.

## Attribution

- **Original author:** Anthropic, PBC
- **Upstream source:** https://github.com/anthropics/claude-cookbooks
- **License:** MIT (see `./LICENSE`)
- **Copyright:** Copyright (c) 2023 Anthropic
- **Snapshot date:** Captured 2026-05 for the `claude-architect` O'Reilly training.

This is a **point-in-time copy**, not a submodule. Upstream gets updates; this copy does not, unless Tim explicitly re-pulls. If a notebook reference looks stale, check the upstream repo for the current version.

## What the MIT License requires us to do

The MIT License (full text in `./LICENSE`) requires that the copyright notice and license text be preserved in any copy or substantial portion of the software. Both are preserved in this directory: the `LICENSE` file from the original repo, plus this NOTICE pointing at the upstream and crediting Anthropic.

## What this means for you (the learner)

- **You can read, run, modify, and redistribute** these notebooks under MIT.
- **Credit Anthropic** for the original work in any redistribution.
- **Treat these notebooks as authoritative** for the Claude API and Agent SDK patterns they demonstrate. They are written by Anthropic engineers.
- **Treat the `notebooks/` directory at the repo root as the course content.** Those are Tim Warner's teaching notebooks, written specifically for the Claude Architect Foundations training.

## Refreshing this snapshot

To re-pull the upstream cookbook:

```powershell
Remove-Item -Recurse -Force C:\github\claude-architect\claude-cookbooks-main
git clone https://github.com/anthropics/claude-cookbooks.git C:\github\claude-architect\claude-cookbooks-main
```

After refreshing, re-run the notebook smoke test (`notebooks/README.md`) to confirm any cited paths still resolve.
