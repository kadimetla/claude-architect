# CCA-F Certification Program Briefing

> Tim's talk-track reference for the Segment 4 cert capstone. Sourced from Anthropic's public CCA-F web page, the public exam policy, and the Anthropic Academy course catalog. All facts here are publicly verifiable; nothing is quoted from non-public materials.

## 1. What CCA-F actually is

**Claude Certified Architect: Foundations (CCA-F)** is Anthropic's first official certification. It validates that you can make sound architecture and tradeoff decisions when building production applications on the **Claude Agent SDK**, **Claude API**, **Claude Code**, and **Model Context Protocol (MCP)**.

Anthropic calls it a **~301-level** exam. Translation: not introductory. The target candidate has roughly **6+ months hands-on** building agentic systems, configuring Claude Code for a team, designing MCP tool interfaces, engineering prompts for structured output, and managing context across long interactions. It is meant to certify practitioners who already ship, not learners exploring.

The "Foundations" tier label matters. This is the first rung on what will become a larger certification ladder. Future tiers will likely go deeper on specialization (security, multi-agent orchestration, MCP server engineering). CCA-F is the door, not the whole house.

## 2. Exam mechanics

| Item | Detail |
|---|---|
| **Question count** | 60 multiple-choice |
| **Time limit** | 120 minutes, single session |
| **Breaks** | None |
| **Format** | One correct answer + three distractors per question |
| **Scoring** | Scaled 100 to 1,000. **Passing score: 720**. |
| **Guessing penalty** | None. Always answer every question. |
| **Results** | Within 2 business days, with section-level breakdown |
| **Proctoring** | Remote, via ProctorFree |
| **Language** | English |
| **Attempts** | **One attempt only** (this is the headline policy item, see below) |

**Scenario structure.** The exam draws **4 scenarios at random** from a pool of **6**. Each scenario frames a set of questions in a realistic production context. The published scenarios are:

1. Customer Support Resolution Agent (Agent SDK + MCP tools, escalation patterns)
2. Code Generation with Claude Code (CLAUDE.md, slash commands, plan mode)
3. Multi-agent Research System (coordinator-subagent orchestration)
4. CI/CD Integration with Claude Code (PR review, test generation)
5. Structured Data Extraction (JSON schemas, validation, retry)
6. Long-Context Document Analysis (context management, summarization)

You will not see all six on exam day; you will see four. The exam guide is the only place that lists them with full primary-domain mappings, so download it after registering.

## 3. Registration, cost, and the one-attempt rule

**Cost:** $99 per exam. Approved partners in the **Claude Partner Network** receive a fixed discount (some get it free as part of partner benefits).

**Eligibility:** Currently restricted to **Anthropic partners**. You register through a verified partner-company email. If your company is not yet a partner, you can apply via claude.com/partners.

**One attempt only.** This is the policy that catches everyone off-guard. There is no "fail and retake next week." If you do not pass, you do not get to try again on the same registration. Treat this exam like a board exam, not a driver's license retest. Implication: rehearse heavily on the practice exam before you spend the $99.

**Cancellation and reschedule rules** live in the public Exam Policy and Certification Terms documents linked from the registration page. Read both before scheduling.

## 4. The five domains, in exam-weight order

| # | Domain | Weight | What it tests |
|---|---|---|---|
| 1 | **Agentic Architecture & Orchestration** | **27%** | Agentic loops, multi-agent coordinator-subagent patterns, task decomposition, session state, hooks as workflow enforcement |
| 3 | **Claude Code Configuration & Workflows** | **20%** | CLAUDE.md hierarchies, custom slash commands, path-specific rules, plan mode vs direct execution, CI/CD integration |
| 4 | **Prompt Engineering & Structured Output** | **20%** | Explicit criteria, few-shot, JSON schema enforcement, validation and retry loops |
| 2 | **Tool Design & MCP Integration** | **18%** | Tool interface design, structured error responses, MCP server integration, tool scoping per agent |
| 5 | **Context Management & Reliability** | **15%** | Long-interaction context preservation, escalation pattern design, error propagation across agents, confidence calibration |

**The 27% domain (Agentic Architecture) is the single biggest lever.** If you can only over-prepare on one area, prepare here. The Claude Agent SDK + multi-agent orchestration patterns drive more than a quarter of your score.

**Domains 2 + 3 combined are 38%** (Tool Design + Claude Code). This is why this course doubles up Segment 2 on those two domains.

## 5. Recommended prep stack

Anthropic's own published "recommended learning" path for CCA-F:

1. **Claude 101** (Anthropic Academy)
2. **Building with the Claude API** (Anthropic Academy)
3. **Introduction to Model Context Protocol** (Anthropic Academy)
4. **Claude Code in Action** (Anthropic Academy)

All four are free on Anthropic Academy (anthropic.skilljar.com). Allow ~1 day per course if you are starting cold; less if you are already shipping on the stack.

**Beyond Anthropic's path,** the prep stack that actually moves the needle:

| Resource | What it gives you | Caveat |
|---|---|---|
| **This course** (Claude Architect Foundations live training) | Skills walkthrough mapped 1:1 to the five domains | Skills-first, not exam-question coaching |
| **Anthropic Cookbooks** (`anthropics/claude-cookbooks` on GitHub) | The notebooks the four demos are built on. Source of truth. | Treat as authoritative for patterns |
| **Reference files in this repo** (`domain-1-agentic.md` through `domain-5-context.md`) | One-page deep dives per domain | Self-study, post-class |
| **Community study repo** (Paul Larionov, `paullarionov/claude-certified-architect`) | 60-question practice test + multi-language study guide | Community-curated, not Anthropic-authored. Calibration only. |
| **The Exam Guide PDF** (downloaded after registering) | Authoritative scope, scenarios, task statements | The only authoritative blueprint. Read it three times. |
| **The Anthropic Practice Exam** (linked on the cert page) | Anthropic-authored sample questions | Aim for **>900/1000** on the practice exam before scheduling the real one |

If you skip exactly one item from this list, skip the community repo. If you skip the Practice Exam, you are gambling $99.

## 6. Tim's "week before the exam" punchlist

Do these in order. Each one assumes you have already finished the four Anthropic Academy courses and worked through this course's four demos.

**T-minus 7 days:**
1. Read the Exam Guide PDF cover to cover. Highlight every **task statement** under each domain. These are the verbs you will be tested on.
2. Take the **Anthropic Practice Exam** cold. Record your score and which domains you missed.
3. For any domain below 75%, re-read the matching `domain-N-*.md` reference file in this repo plus the corresponding cookbook notebook.

**T-minus 3 days:**
4. Rebuild the customer-support agent (Demo 1) without looking at the notebook. If you cannot do it in 30 minutes, you are not ready on Domain 1.
5. Walk a teammate through your `.mcp.json` and your CLAUDE.md hierarchy out loud. If you stumble, you do not own Domain 2 or 3 yet.
6. Run the invoice extractor (Demo 3) against a deliberately broken invoice. Verify your retry loop fires. Domain 4 confidence check.

**T-minus 1 day:**
7. Take the Practice Exam a second time. Target **>900/1000**.
8. Skim the Exam Policy. Confirm your ID matches your registration name exactly.
9. Confirm your ProctorFree environment: webcam works, room is clean, no second monitor, government ID ready.
10. Sleep. Caffeine the morning of, not the night before.

**Exam day:**
11. Answer every question. **No guessing penalty.**
12. Flag any question you are not sure about, finish the exam, come back to flagged ones with remaining time.
13. Trust your training. The exam tests judgment, not trivia.

## 7. After you pass

You get a **CCA-F digital badge** you can post on LinkedIn. The cert is recognized inside the Claude Partner Network. The certification may expire when Anthropic releases a refreshed exam tied to a new product cycle (per the public Exam Policy section on certification expiration). Renewals require retaking the current exam.

If you do not pass, the appeal window is **14 calendar days** from notification (per public Exam Policy section 4). Email `academy-support@anthropic.com` with "appeal" in the subject line.

## 8. Public references

All facts in this briefing are sourced from publicly available Anthropic materials:

- **Public certification page:** the Claude Certified Architect page on Anthropic's site
- **Public exam policy:** Anthropic Certification Exam Policy (last updated April 1, 2026)
- **Public certification terms:** Anthropic Certification Terms and Conditions
- **Anthropic Academy course catalog:** `anthropic.skilljar.com`
- **Contact:** `academy-support@anthropic.com`

Nothing in this briefing is quoted from non-public exam content.
