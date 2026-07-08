# Scenario: CI/CD Integration with Claude Code

> Reference scaffold, maps to **COURSE-FLOW.md Segment 2** (Domain 3, with Domain 4 on the prompt design)

Exam scenario 5 on the CCA-F blueprint. This is the worked CI example that [`domain-3-claude-code.md`](./domain-3-claude-code.md) points at.

## What this scenario covers

**Headless mode** is Claude Code with no TTY: `claude -p "<prompt>"` reads a prompt, runs to completion, and prints a result. That single property is what makes it a CI citizen. A GitHub Actions runner has no interactive terminal, so an agent that requires one cannot participate in your pipeline.

The canonical wire-up is automated pull-request review: trigger on PR open, check out the diff, run Claude headless against it, post the verdict as a PR comment.

## The pattern

Four moving parts, in order.

### 1. Trigger and checkout

Fetch enough history to diff against the base branch. A shallow clone (`fetch-depth: 1`, the Actions default) cannot compute `origin/main...HEAD`.

```yaml
on:
  pull_request:
    types: [opened, synchronize]

jobs:
  review:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      pull-requests: write   # required for `gh pr comment`
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0     # full history; the diff needs a merge base
```

### 2. Run Claude headless

`--output-format json` is the load-bearing flag. Without it you get prose meant for a human terminal, and you are back to regex-scraping stdout. With it you get a parseable envelope you can branch on.

```yaml
      - name: Review the diff
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
        run: |
          git diff origin/${{ github.base_ref }}...HEAD > /tmp/pr.diff
          claude -p "$(cat .github/prompts/review.md)

          Diff under review:
          $(cat /tmp/pr.diff)" \
            --output-format json > /tmp/review.json
```

### 3. Post the result

```yaml
      - name: Comment on the PR
        env:
          GH_TOKEN: ${{ github.token }}
        run: |
          jq -r '.result' /tmp/review.json > /tmp/comment.md
          gh pr comment ${{ github.event.pull_request.number }} \
            --body-file /tmp/comment.md
```

### 4. Gate the merge, or do not

A review comment is advisory. If you want the job to **block** a merge, have the prompt emit a machine-readable verdict and exit non-zero on it. Decide this deliberately: an agent that fails the build on a false positive trains your team to bypass the check.

```bash
jq -e '.result | fromjson | .blocking == false' /tmp/review.json > /dev/null \
  || { echo "Blocking findings. See the PR comment."; exit 1; }
```

## Why prompt caching pays for itself here

The review prompt is a **stable prefix**: the same rubric, the same house style, the same severity ladder, on every run. Only the diff changes. Mark the rubric with `cache_control` and the pipeline reads it from cache on every PR after the first.

Two constraints from Domain 2 carry over unchanged. The cached prefix must clear the model's minimum-size floor (**1024 input tokens on Sonnet 4.x**, **4096 on Haiku 4.5**), and below that floor `cache_control` is silently ignored. A one-paragraph rubric will not cache. A real one, with worked examples of each severity level, will.

## Secrets hygiene

The exam tests this and so does production.

- **Pass the key via GitHub Secrets**, read as `${{ secrets.ANTHROPIC_API_KEY }}`, surfaced to the step as an env var. Never a literal.
- **Never commit a key in `.mcp.json`.** That file is config-as-data and it ships in the repo. Use `${ANTHROPIC_API_KEY}`-style env-var expansion, which is exactly why [`../.mcp.json`](../.mcp.json) is written that way.
- **Scope the workflow token.** `permissions:` defaults to write-all on many repos. Grant `contents: read` and `pull-requests: write` and nothing else.
- **Beware `pull_request_target`.** It runs with a privileged token against untrusted head code. If you reach for it to review forks, do not check out the fork's code in the same job.

## Production tips

**Bound the diff.** A 40k-line refactor will blow past your context window and your budget. Cap it, and say so in the comment rather than silently reviewing the first N lines.

```bash
git diff --stat origin/main...HEAD | tail -1
git diff origin/main...HEAD | head -c 200000 > /tmp/pr.diff
```

**Pin the model.** CI is the one place a floating alias bites you: a model refresh silently changes your review behavior on a Tuesday. Pass `--model claude-haiku-4-5` explicitly. Haiku handles diff review at production quality; promote to Sonnet only if you measure a lift.

**Make it idempotent.** `synchronize` fires on every push to the PR. Either update the existing comment (`gh pr comment --edit-last`) or you will bury the conversation under fifteen review bots.

**Fail open on API errors.** A 529 from the API should not red-X a PR that is otherwise green. Distinguish "the agent found problems" from "the agent could not run."

## Demo anchor

Taught live in **COURSE-FLOW.md Segment 2**, the `claude -p` headless block. Code references:

- [`../.mcp.json`](../.mcp.json). Env-var expansion instead of committed secrets.
- [`../hooks-example.py`](../hooks-example.py). The same compliance-gate mental model, enforced in-process rather than in CI.
- [`./domain-3-claude-code.md`](./domain-3-claude-code.md). Headless mode, `settings.json`, and the CLAUDE.md hierarchy.
- [`./domain-4-prompts.md`](./domain-4-prompts.md). Designing the review rubric itself.

## Further reading

- [Claude Code headless mode](https://code.claude.com/docs/en/headless)
- [Claude Code settings](https://code.claude.com/docs/en/settings)
- [Prompt caching](https://platform.claude.com/docs/en/build-with-claude/prompt-caching)
- [GitHub Actions: security hardening](https://docs.github.com/en/actions/security-for-github-actions/security-guides/security-hardening-for-github-actions)
