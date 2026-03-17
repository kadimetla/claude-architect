# Claude Certified Architect: Foundations (CCA-F) Crash Course

Study materials, code examples, and practice scenarios for Anthropic's **Claude Certified Architect -- Foundations** certification exam. This 4-hour crash course covers all five exam domains and prepares you to pass the CCA-F on your first attempt.

## What Is the CCA-F?

The CCA-F is Anthropic's first professional certification, a 120-minute proctored exam with 60 multiple-choice questions across five domains. It validates your ability to design and build production-grade applications with Claude Code, the Claude Agent SDK, the Claude API, and Model Context Protocol (MCP). Passing score is 720/1000.

| Domain | Weight | Focus |
|--------|--------|-------|
| 1. Agentic Architecture & Orchestration | 27% | Agentic loops, multi-agent coordination, hooks, session management |
| 2. Tool Design & MCP Integration | 18% | Tool descriptions, structured errors, scoped tool distribution, MCP config |
| 3. Claude Code Configuration & Workflows | 20% | CLAUDE.md hierarchy, slash commands, skills, plan mode, CI/CD integration |
| 4. Prompt Engineering & Structured Output | 20% | Explicit criteria, few-shot prompting, tool_use with JSON schemas, batch API |
| 5. Context Management & Reliability | 15% | Context preservation, escalation patterns, error propagation, provenance |

## Repository Structure

```text
cca-f/
├── domain-1-agentic.md          # Study guide: Agentic Architecture & Orchestration
├── domain-2-tools-mcp.md        # Study guide: Tool Design & MCP Integration
├── domain-4-prompts.md          # Study guide: Claude Code Configuration & Workflows
├── domain-5-context.md          # Study guide: Context Management & Reliability
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
git clone https://github.com/timothywarner-org/cca-f.git
cd cca-f
npm install
```

### Recommended Study Path

1. **Read the domain study guides** -- Start with Domain 1 (highest weight at 27%), then work through Domains 3 and 4 (20% each), Domain 2 (18%), and Domain 5 (15%).
2. **Review the code examples** -- `hooks-example.py` and `testing.md` demonstrate key patterns directly tested on the exam.
3. **Explore the configuration templates** -- `CLAUDE.md.example`, `SKILL.md`, and `scenario-cicd-integration.md` show real Claude Code configuration patterns.
4. **Practice hands-on** -- Build an agent with the Claude Agent SDK. Configure Claude Code for a project. Design MCP tools. The exam tests applied judgment, not memorization.

## Exam Scenarios

The exam draws 4 scenarios at random from this set of 6. Each frames a realistic production context:

| # | Scenario | Primary Domains |
|---|----------|-----------------|
| 1 | Customer Support Resolution Agent | 1, 2, 5 |
| 2 | Code Generation with Claude Code | 3, 5 |
| 3 | Multi-Agent Research System | 1, 2, 5 |
| 4 | Developer Productivity with Claude | 2, 3, 1 |
| 5 | Claude Code for Continuous Integration | 3, 4 |
| 6 | Structured Data Extraction | 4, 5 |

## Key Concepts Quick Reference

### Agentic Loop (Domain 1)

```
Send request -> Check stop_reason -> "tool_use"? Execute tool, loop back
                                  -> "end_turn"? Present response, done
```

### Tool Selection (Domain 2)

- **Descriptions drive selection** -- detailed descriptions > clever tool names
- **4-5 tools per agent max** -- more tools = worse selection reliability
- **Structured errors** -- `errorCategory`, `isRetryable`, human-readable message

### Claude Code Config (Domain 3)

- **User-level** `~/.claude/CLAUDE.md` -- personal, not shared
- **Project-level** `.claude/CLAUDE.md` or root -- team-wide, committed
- **Path rules** `.claude/rules/*.md` with YAML frontmatter `paths` globs
- **CI/CD** -- use `-p` flag for non-interactive mode

### Structured Output (Domain 4)

- **`tool_use` with JSON schemas** = guaranteed schema compliance (no syntax errors)
- **`tool_choice: "any"`** = force tool call (no conversational text)
- **Few-shot examples** = most effective technique for consistent output

### Context & Reliability (Domain 5)

- Extract facts into persistent "case facts" block
- Trim verbose tool outputs before they accumulate
- Escalate on: customer request, policy gaps, no progress. Not on: sentiment, self-reported confidence.

## Recommended Learning

Complete these Anthropic Academy courses before attempting the exam:

- Building with the Claude API
- Introduction to Model Context Protocol
- Claude Code in Action
- Claude 101

## About the Instructor

**Tim Warner** is a technical trainer and content creator specializing in cloud and AI technologies. He delivers live training, writes certification prep materials, and builds hands-on labs that make complex concepts accessible.

- Web: [TechTrainerTim.com](https://techtrainertim.com)
- Email: [tim@techtrainertim.com](mailto:tim@techtrainertim.com)
- GitHub: [@timothywarner-org](https://github.com/timothywarner-org)

## Contributing

Contributions are welcome. Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.
