# Claude Architect Foundations - O'Reilly Live Training

Reference architectures, code examples, and practice scenarios for the **Claude Architect** role. This 4-hour O'Reilly Media live training is **skills-first**: it teaches the production patterns that define a Claude Architect (agentic orchestration, tool design with MCP, Claude Code workflows, prompt engineering, context management) and describes the CCA-F certification structure without teaching to specific exam items.

> The Claude Certified Architect: Foundations (CCA-F) exam from Anthropic is not yet publicly available. The five reference files in this repo map to the published 5-domain exam blueprint, so you have the study scaffold ready for when the exam ships.

## What is a Claude Architect?

The Claude Architect is an emerging job role focused on designing and building production-grade applications with Claude Code, the Claude Agent SDK, the Claude API, and Model Context Protocol (MCP). Organizations across the Claude Partner Network are hiring for this skillset.

## Course at a glance

| Segment | Duration | Topic | Key deliverable |
|---|---|---|---|
| 1 | 50 min | Building AI Agents That Use Tools | Customer support agent with hook-enforced policy |
| 2 | 50 min | Tool Design, Integration, and Claude Code Workflows | MCP config walkthrough + Claude Code hierarchy demo |
| 3 | 50 min | Prompt Engineering and Structured Output | Invoice extractor with Pydantic + validation retry |
| 4 | 50 min | Context Management, Reliability, and Production Strategy | Compaction demo + production triage exercise |

Total: 4 hours (4 × 50-min segments + 3 × 10-min breaks). Instructors and learners should start at **[COURSE-FLOW.md](./COURSE-FLOW.md)**.

## Core competency areas

| Domain | Reference file | Focus |
|---|---|---|
| 1 - Agentic Architecture & Orchestration | [domain-1-agentic.md](./domain-1-agentic.md) | Agentic loops, multi-agent coordination, hooks, session management |
| 2 - Tool Design & MCP Integration | [domain-2-tools-mcp.md](./domain-2-tools-mcp.md) | Tool descriptions, structured errors, scoped distribution, MCP config |
| 3 - Claude Code Configuration & Workflows | [domain-3-claude-code.md](./domain-3-claude-code.md) | CLAUDE.md hierarchy, skills, slash commands, plan mode, CI/CD |
| 4 - Prompt Engineering & Structured Output | [domain-4-prompts.md](./domain-4-prompts.md) | Explicit criteria, few-shot prompting, JSON schemas via tool use, batch API |
| 5 - Context Management & Reliability | [domain-5-context.md](./domain-5-context.md) | Context preservation, escalation, error propagation, provenance |

## Repository layout

```text
claude-architect/
├── INSTRUCTOR-SETUP.md         # Multi-day setup arc (machine config, env vars, repo clone, backup plans)
├── COURSE-FLOW.md              # Master instructor punchlist (4 segments × 50 min)
├── PRE-CLASS-CHECKLIST.md      # Instructor pre-flight (PowerShell, 35 checks)
├── domain-1-agentic.md         # Reference: Agentic Architecture & Orchestration
├── domain-2-tools-mcp.md       # Reference: Tool Design & MCP Integration
├── domain-3-claude-code.md     # Reference: Claude Code Configuration & Workflows
├── domain-4-prompts.md         # Reference: Prompt Engineering & Structured Output
├── domain-5-context.md         # Reference: Context Management & Reliability
├── .mcp.json                   # Segment 2 Demo A anchor (4 servers, 3 transports)
├── hooks-example.py            # Agent SDK hooks: compliance enforcement
├── testing.md                  # Coordinator-subagent test patterns
├── scenario-cicd-integration.md # Codebase analysis skill with frontmatter
├── SKILL.md                    # Example slash-command / skill definition
├── CLAUDE.md                   # Claude Code project instructions for this repo
└── scripts/
    ├── voice-lint.ps1          # Enforce Tim's voice rules across all MD files
    └── preflight.ps1           # Instructor pre-flight automation (mirrors PRE-CLASS-CHECKLIST)
```

## Getting started

### Prerequisites

- [Node.js](https://nodejs.org/) 18+ for Anthropic SDK examples
- [Python](https://www.python.org/) 3.13+ for hooks and cookbook notebooks
- [Claude Code CLI](https://docs.claude.com/en/docs/claude-code) installed and authenticated
- An [Anthropic API key](https://console.anthropic.com/) set as `ANTHROPIC_API_KEY`

### Setup

```bash
git clone https://github.com/timothywarner-org/claude-architect.git
cd claude-architect
npm install
```

### Recommended learning path

1. **Read [COURSE-FLOW.md](./COURSE-FLOW.md)** for the full 4-segment teaching arc.
2. **Walk the five `domain-*.md` reference files** in order. Each maps to a course segment and points at runnable cookbook notebooks.
3. **Run the demo notebooks** in your own environment. The course depends on Anthropic's official cookbooks (`private/claude-cookbooks-main/`).
4. **Build something.** The reference architectures only land when you wire one of these patterns into a real workflow.

## Practice scenarios

Each scenario frames a realistic production context that a Claude Architect would encounter. These map to the six exam scenarios in the CCA-F blueprint:

| # | Scenario | Primary competencies |
|---|---|---|
| 1 | Customer Support Resolution Agent | Domains 1, 2, 5 |
| 2 | Claude Code for Software Development | Domains 3, 5 |
| 3 | Multi-Agent Research System | Domains 1, 2, 5 |
| 4 | Developer Productivity Tooling | Domains 1, 2, 3 |
| 5 | CI/CD Integration with Claude Code | Domains 3, 4 |
| 6 | Structured Data Extraction Pipeline | Domains 4, 5 |

## Key concepts quick reference

### Agentic loop

```text
Send request -> Check stop_reason -> "tool_use"? Execute tool, append tool_result, loop
                                  -> "end_turn"? Done
                                  -> "pause_turn"? Resume in next request
```

### Tool selection

- **Descriptions drive selection.** Detailed descriptions beat clever tool names.
- **Cap at 4-5 tools per agent.** More tools degrade selection accuracy.
- **Structured errors as tool_result content.** Never raise exceptions from tool implementations.

### Claude Code configuration

- **User-level** `~/.claude/CLAUDE.md` for personal defaults
- **Project-level** `./CLAUDE.md` at repo root for team conventions
- **Subtree** `<subdir>/CLAUDE.md` loads on demand
- **`claude -p`** for headless / CI/CD usage

### Structured output

- **`tool_use` with JSON schema = guaranteed schema compliance.** Define output as a tool's `input_schema`, force the model to call it with `tool_choice: {"type": "tool", "name": "..."}`.
- **Few-shot examples > temperature.** Two or three input-output pairs beat tuning sampling parameters.

### Context and reliability

- Pin case-facts at the top of long sessions
- Summarize resolved turns; keep verbatim history only for the active issue
- Escalate on explicit human request, policy gaps, or low confidence - never on sentiment alone

## About the instructor

**Tim Warner** is a technical trainer and content creator specializing in cloud and AI technologies. Microsoft MVP (Azure AI), Pluralsight Principal Author (200+ courses, 1M+ learners), Microsoft Press / Pearson senior content developer, O'Reilly Live Learning instructor.

- Web: [TechTrainerTim.com](https://techtrainertim.com)
- Email: [tim@techtrainertim.com](mailto:tim@techtrainertim.com)
- GitHub: [@timothywarner-org](https://github.com/timothywarner-org)

## Contributing

Contributions are welcome. See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

MIT - see [LICENSE](LICENSE).
