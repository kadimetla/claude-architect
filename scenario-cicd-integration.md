---
context: fork
allowed-tools:
  - Read
  - Grep
  - Glob
  - Bash
argument-hint: "Path to the directory or file to analyze"
---

# Codebase Analysis Skill

Analyze the codebase and produce a structured summary:

1. Architecture overview: directories, entry points, key modules
2. Technology stack: languages, frameworks, build tools
3. Key patterns: state management, error handling, data flow
4. Test coverage: locations, patterns, gaps

Start with Glob for entry points, Grep to trace imports. Do not read every file.
