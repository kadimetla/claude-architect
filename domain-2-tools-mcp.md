# Domain 3: Claude Code Configuration & Workflows (20%)

## CLAUDE.md Hierarchy

1. User-level (`~/.claude/CLAUDE.md`) - personal, not shared
2. Project-level (`.claude/CLAUDE.md` or root) - team-wide, committed
3. Directory-level (subdirectory CLAUDE.md) - area-specific

## Path-Specific Rules

`.claude/rules/` with YAML frontmatter `paths` globs. Better than subdir CLAUDE.md for cross-directory conventions.

## Plan Mode vs Direct Execution

- Plan mode: architectural decisions, multi-file changes
- Direct execution: single-file fixes, clear scope
- `-p` flag for CI/CD non-interactive mode (this is THE exam answer)
