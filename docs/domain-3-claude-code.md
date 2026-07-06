# Domain 3: Claude Code Configuration & Workflows

> Reference scaffold. Maps to **COURSE-FLOW.md Segment 2** (shared with Domain 2).

## What this domain covers

Domain 3 is where Claude Code stops being a chat box and starts being an **opinionated coworker** that knows your stack, your conventions, and your guardrails. You configure that coworker through a layered **CLAUDE.md hierarchy**, package institutional knowledge as **custom skills** and **slash commands**, scope conventions with **path-specific rules**, and choose between **plan mode** for exploration and **headless mode** (`claude -p`) for automation. Everything ties together in **`settings.json`** (hooks, permissions, MCP servers) and in tight **iterative refinement** loops you can drop into pre-commit hooks and CI/CD pipelines.

## Core concepts

### CLAUDE.md hierarchy

Claude Code reads memory files at four levels and unions them. There is no single "winning" file. The agent sees the merged set.

- **User memory** at `~/.claude/CLAUDE.md` applies to every project on this machine. Tim's lives here and contains his voice rules, stack defaults (Azure, GitHub, PowerShell 7, Node), and the mandatory closing-ritual format.
- **Project memory** at `./CLAUDE.md` at the repo root is checked into git and applies to anyone using the repo. This file is the team's contract.
- **Subtree memory** at `<subdir>/CLAUDE.md` loads on demand when Claude reads files in that subdirectory. Great for monorepos where `backend/` runs Django and `frontend/` runs React with different conventions.
- **Local override** at `CLAUDE.local.md` is gitignored, for personal preferences without polluting the team file.

Per Claude Code docs: files in the directory hierarchy **above** the working directory load **in full at launch**. Subdirectory files load **on demand** when Claude reads files in them. The Agent SDK opts in to user + project via `setting_sources=["user", "project"]`. Conflicting rules: outcome is model-interpreted, so write non-conflicting rules or **explicitly state precedence** in the higher-priority file.

### Custom skills and slash commands

A **skill** is a versioned, reusable instruction set you ship with your repo. Skills live in `~/.claude/skills/<name>/SKILL.md` (user-wide) or `.claude/skills/<name>/SKILL.md` (project-scoped). The frontmatter (`name`, `description`) is how Claude decides whether to invoke the skill at all. The **description is the search query** the model runs against your skill library, so write it like a help-desk ticket title, not a marketing tagline. Skills can bundle scripts, templates, and reference docs alongside the `SKILL.md`.

**Slash commands** live in `~/.claude/commands/<name>.md` or `.claude/commands/<name>.md` and become `/name` invocations. A command file carries frontmatter (`context`, `allowed-tools`, `argument-hint`) and an instruction body. Skills are how you package institutional knowledge into a version-controlled artifact instead of re-typing it every session.

### Path-specific rules

Inside `.claude/rules/` you author markdown files with frontmatter `paths:` containing globs. Rules **only load when Claude reads matching files**, which keeps the context window lean. Concrete use case: backend Python files need PEP 8 + type hints; frontend TS files need React conventions; infra Terraform files need stricter commit-message rules. Path-glob rules beat scattering nested `CLAUDE.md` files through every subdirectory because they **colocate intent with the lint surface** instead of with the directory tree.

### Plan mode vs headless mode (`claude -p`)

Two operating modes, both first-class:

- **Plan mode** (interactive, the default for non-trivial work). Claude reads the codebase, asks questions, proposes a plan via `ExitPlanMode`, and waits for approval before touching files. Use it for exploration, refactors, and anything that crosses more than one file.
- **Headless mode** via `claude -p "<prompt>"`. Non-interactive, pipe-friendly, returns when done. Use it for CI/CD, pre-commit hooks, and automation. Supports `--output-format json|stream-json` for downstream parsing and `--allowedTools "Read,Edit,Bash"` to restrict the tool surface.

```bash
claude -p "Find and fix the bug in auth.py" --allowedTools "Read,Edit,Bash"
claude -p "Explain what this project does"
claude -p "List all API endpoints" --output-format json
git log --oneline -20 | claude -p "summarize these recent commits"
```

### CI/CD integration

Headless mode + GitHub Actions = automated code review, PR descriptions, release notes, and doc updates. The pattern: trigger on PR open, checkout, run `claude -p "<review prompt>" --output-format json`, post the result as a PR comment via the `gh` CLI. The Anthropic API has **prompt caching** built in, so reusing a stable system prompt across pipeline runs is cheap. See `./scenario-cicd-integration.md` for the worked CI example. Always pass secrets via **GitHub Secrets**, never via a committed `.mcp.json`.

### `settings.json`, hooks, and MCP

Project-level `.claude/settings.json` configures hooks, permissions, and MCP servers. Hooks are **deterministic** event handlers that fire around tool use (`PreToolUse`, `PostToolUse`, `SessionStart`, `Stop`). The example below auto-formats every Write or Edit:

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": [
          {
            "type": "command",
            "command": "${CLAUDE_PLUGIN_ROOT}/scripts/format-code.sh"
          }
        ]
      }
    ]
  }
}
```

MCP servers (project-level `.mcp.json`):

```json
{
  "mcpServers": {
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": { "GITHUB_TOKEN": "${GITHUB_TOKEN}" }
    }
  }
}
```

For the **Agent SDK** equivalent, hooks are Python callables (see `../hooks-example.py` for the Domain 1 normalization + policy-gate pattern). Same mental model: **hooks are deterministic, prompts are probabilistic**. Use hooks when business rules require a guarantee.

### Iterative refinement

The progressive-development loop: small change, `claude -p "review"`, apply feedback, repeat. This beats one giant plan-mode session for most refactors because each iteration is cheap, reviewable, and revertible. Use **TodoWrite + plan mode** for the big arc, and **headless** for the micro-iterations inside it.

## Demo anchor

See **COURSE-FLOW.md Segment 2** for the live walkthrough. Code references in this repo:

- `../CLAUDE.md`. This repo's own project-level CLAUDE.md as a worked example.
- `./scenario-cicd-integration.md`. `claude -p` in a CI pipeline.
- `../hooks-example.py`. Agent SDK hook pattern (same mental model as `settings.json` hooks).
- `../settings.json`. Editor settings example for the repo.
- `../claude-cookbooks-main/skills/`. Anthropic skill examples (private; do not commit).

## Production tips (Tim's voice)

- **Tim's hierarchy rule.** User CLAUDE.md = your voice and stack defaults. Project CLAUDE.md = team conventions. Subtree CLAUDE.md = "different rules apply in this corner of the monorepo." Never duplicate. Never contradict without writing the precedence rule explicitly in the higher-priority file.
- **Skill descriptions are search terms.** The model picks skills by **description**, not by name. Write descriptions that match what a user would actually request, not what a product manager would name the feature.
- **`claude -p` is your CI/CD superpower.** Anything you'd want a senior engineer to do in a pipeline (review, summarize, audit, generate release notes), `claude -p` can do for the cost of a few thousand tokens. Cache the system prompt and the pipeline is nearly free.
- **Plan mode is not slower. Plan mode is more honest.** It surfaces what Claude is about to do before it does it. Use it for anything that touches more than one file. The 30 seconds you spend reviewing the plan saves the 30 minutes of un-doing the wrong edit.
- **`.claude/rules/` beats subtree CLAUDE.md for cross-cutting conventions.** Path-glob rules load only when relevant, so the context window stays lean and the lint rules live next to the lint surface instead of being scattered through nested CLAUDE.md files.
- **Hooks for compliance, prompts for judgment.** If a business rule must hold 100% of the time (refund cap, PII redaction, prerequisite verification), wire a hook. Prompts are probabilistic. Hooks are not.

## Further reading

- Claude Code overview. https://docs.claude.com/en/docs/claude-code/overview
- CLAUDE.md memory. https://docs.claude.com/en/docs/claude-code/memory
- Headless mode. https://docs.claude.com/en/docs/claude-code/headless
- Skills. https://docs.claude.com/en/docs/claude-code/skills
- Hooks. https://docs.claude.com/en/docs/claude-code/hooks
- `../claude-cookbooks-main/skills/`. Anthropic's own skill examples.
