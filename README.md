# Claude Architect: Foundations Live Training

Reference architectures, code examples, and practice scenarios for the **Claude Architect** role. This 4-hour intensive covers the five core competency areas that define a production-ready Claude Architect: agentic orchestration, tool design with MCP, Claude Code workflows, prompt engineering, and context management.

## What Is a Claude Architect?

The Claude Architect is an emerging job role focused on designing and building production-grade applications with Claude Code, the Claude Agent SDK, the Claude API, and Model Context Protocol (MCP). Organizations across the Claude Partner Network — including Accenture, Deloitte, and Cognizant — are hiring for this skillset.

## Core Competency Areas

| Competency | Focus |
|------------|-------|
| Agentic Architecture & Orchestration | Agentic loops, multi-agent coordination, hooks, session management |
| Tool Design & MCP Integration | Tool descriptions, structured errors, scoped tool distribution, MCP config |
| Claude Code Configuration & Workflows | CLAUDE.md hierarchy, slash commands, skills, plan mode, CI/CD integration |
| Prompt Engineering & Structured Output | Explicit criteria, few-shot prompting, tool_use with JSON schemas, batch API |
| Context Management & Reliability | Context preservation, escalation patterns, error propagation, provenance |

## Repository Structure

```text
claude-architect/
├── domain-1-agentic.md          # Reference: Agentic Architecture & Orchestration
├── domain-2-tools-mcp.md        # Reference: Tool Design & MCP Integration
├── domain-4-prompts.md          # Reference: Claude Code Configuration & Workflows
├── domain-5-context.md          # Reference: Context Management & Reliability
├── hooks-example.py             # Agent SDK hooks: compliance enforcement, data normalization
├── testing.md                   # Coordinator-subagent pattern: multi-agent orchestration
├── scenario-cicd-integration.md # Codebase analysis skill with frontmatter config
├── SKILL.md                     # Example SKILL.md with context:fork and allowed-tools
├── CLAUDE.md                    # Claude Code project instructions
├── CLAUDE.md.example            # Template showing CLAUDE.md best practices
├── settings.json                # VS Code workspace settings
├── markdownlint.json            # Markdown linting configuration
└── package.json                 # Project metadata and Anthropic SDK dependencies
```

## Getting Started

### Prerequisites

- [Node.js](https://nodejs.org/) 18+ (for Anthropic SDK examples)
- [Python](https://www.python.org/) 3.11+ (for hook and agent examples)
- [Claude Code CLI](https://docs.anthropic.com/en/docs/claude-code) installed and authenticated
- An [Anthropic API key](https://console.anthropic.com/)

### Setup

```bash
git clone https://github.com/timothywarner-org/claude-architect.git
cd claude-architect
npm install
```

### Recommended Learning Path

1. **Read the reference guides** — Start with Agentic Architecture (the highest-demand competency), then work through Claude Code Workflows, Prompt Engineering, Tool Design & MCP, and Context Management.
2. **Review the code examples** — `hooks-example.py` and `testing.md` demonstrate key production patterns.
3. **Explore the configuration templates** — `CLAUDE.md.example`, `SKILL.md`, and `scenario-cicd-integration.md` show real Claude Code configuration patterns.
4. **Practice hands-on** — Build an agent with the Claude Agent SDK. Configure Claude Code for a project. Design MCP tools. Applied judgment beats memorization every time.

## Practice Scenarios

Each scenario frames a realistic production context that a Claude Architect would encounter:

| # | Scenario | Primary Competencies |
|---|----------|---------------------|
| 1 | Customer Support Resolution Agent | Agentic Architecture, Tool Design, Context Management |
| 2 | Code Generation with Claude Code | Claude Code Workflows, Context Management |
| 3 | Multi-Agent Research System | Agentic Architecture, Tool Design, Context Management |
| 4 | Developer Productivity with Claude | Tool Design, Claude Code Workflows, Agentic Architecture |
| 5 | Claude Code for Continuous Integration | Claude Code Workflows, Prompt Engineering |
| 6 | Structured Data Extraction | Prompt Engineering, Context Management |

## Key Concepts Quick Reference

### Agentic Loop

```
Send request -> Check stop_reason -> "tool_use"? Execute tool, loop back
                                  -> "end_turn"? Present response, done
```

### Tool Selection

- **Descriptions drive selection** — detailed descriptions > clever tool names
- **4-5 tools per agent max** — more tools = worse selection reliability
- **Structured errors** — `errorCategory`, `isRetryable`, human-readable message

### Claude Code Config

- **User-level** `~/.claude/CLAUDE.md` — personal, not shared
- **Project-level** `.claude/CLAUDE.md` or root — team-wide, committed
- **Path rules** `.claude/rules/*.md` with YAML frontmatter `paths` globs
- **CI/CD** — use `-p` flag for non-interactive mode

### Structured Output

- **`tool_use` with JSON schemas** = guaranteed schema compliance (no syntax errors)
- **`tool_choice: "any"`** = force tool call (no conversational text)
- **Few-shot examples** = most effective technique for consistent output

### Context & Reliability

- Extract facts into persistent "case facts" block
- Trim verbose tool outputs before they accumulate
- Escalate on: customer request, policy gaps, no progress. Not on: sentiment, self-reported confidence.

## Recommended Learning

Complete these Anthropic Academy courses to build your Claude Architect foundation:

- Building with the Claude API
- Introduction to Model Context Protocol
- Claude Code in Action
- Claude 101

## About the Instructor

**Tim Warner** is a technical trainer and content creator specializing in cloud and AI technologies. He delivers live training, writes production-focused learning materials, and builds hands-on labs that make complex concepts accessible.

- Web: [TechTrainerTim.com](https://techtrainertim.com)
- Email: [tim@techtrainertim.com](mailto:tim@techtrainertim.com)
- GitHub: [@timothywarner-org](https://github.com/timothywarner-org)

## Contributing

Contributions are welcome. Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.
