"""Cell builder for segment-4-cca-f-capstone.ipynb.

Teaching-first notebook for Segment 4: CCA-F Certification Capstone.
Maps to all five CCA-F domains. No live API calls. The notebook renders
the cert briefing and 10 weighted practice questions inline, sourced from
practice-questions.json (regenerated from the community study HTML).
"""

from __future__ import annotations


def cells() -> list[tuple[str, str]]:
    return [
        ("md", _title_md),
        ("md", _lo_md),
        ("md", _what_is_md),
        ("md", _mechanics_md),
        ("md", _cost_access_md),
        ("md", _scenario_md),
        ("md", _domain_weights_md),
        ("md", _prep_stack_md),
        ("md", _week_before_md),
        ("md", _practice_intro_md),
        ("code", _practice_loader_code),
        ("code", _practice_render_code),
        ("md", _final_qa_md),
        ("md", _course_recap_md),
        ("md", _close_md),
    ]


_title_md = """\
# Segment 4: CCA-F Certification Capstone

**Duration:** 50 minutes (12 min briefing + 28 min weighted practice + 10 min Q&A and close)
**Maps to:** All five CCA-F domains
**References:** [`../CERT-PROGRAM-BRIEFING.md`](../CERT-PROGRAM-BRIEFING.md), [`../PRACTICE-QUESTIONS.md`](../PRACTICE-QUESTIONS.md)

You have the skills. The exam is how you signal them. This segment is the **CCA-F debrief**: what is on the test, what Anthropic expects, and a weighted live practice run so you leave knowing your weakest domain.
"""

_lo_md = """\
## Learning objectives

- Name the **CCA-F exam mechanics** (60 questions, 120 minutes, $99, one attempt, 720 passing)
- Recall the **five domain weights** and which two account for 38% of the score
- Identify your **weakest domain** from the live practice questions, and what to study before sitting the exam
- Build your own **week-before-the-exam punchlist** from the briefing template
"""

_what_is_md = """\
## What CCA-F is

**Claude Certified Architect, Foundations** is Anthropic's first official certification. It targets architects already shipping with the **Agent SDK**, **Claude Code**, the **Claude API**, and **MCP**. Skill level is roughly the 301 mark - past "hello world", not yet "I run distillation pipelines."

This is a **beta product**. The exam launched in 2026 and Anthropic reserves the right to retire and refresh it. Watch the official cert page for changes.
"""

_mechanics_md = """\
## Exam mechanics (the load-bearing facts)

| Item | Value |
|---|---|
| **Questions** | 60 multiple-choice |
| **Time** | 120 minutes, single session, **no breaks** |
| **Scoring** | Scaled 100-1000, **passing = 720**, no penalty for guessing |
| **Delivery** | ProctorFree, English |
| **Results** | 2 business days |
| **Cost** | **$99** |
| **Attempts** | **One.** This is the policy that catches people. |
| **Access** | Currently restricted to Anthropic partners (claude.com/partners) |

**Plan around the one-attempt rule.** Do not schedule until your practice scores are consistently >900.
"""

_cost_access_md = """\
## Cost and access

- $99 per attempt
- One attempt per registration
- Partner-gated as of the 2026 launch; check the official page for any cohort opening
- Results in 2 business days, scored 100-1000
"""

_scenario_md = """\
## Scenario structure

The exam draws **4 scenarios at random** from a pool of **6**. Each scenario frames a set of questions in a realistic production context. The community study set we will use today has 4 scenarios x 15 questions; the same shape, different content.

**The four scenarios in our practice set:**

1. Multi-agent Research System
2. Customer Support Agent
3. Claude Code for Continuous Integration
4. Code Generation with Claude Code
"""

_domain_weights_md = """\
## Domain weights

| Domain | Weight | Notebook |
|---|---|---|
| **D1** Agentic Architecture | **27%** (biggest single lever) | Segment 1 |
| **D3** Claude Code | **20%** | Segment 2 |
| **D4** Prompts + Structured Output | **20%** | Segment 3 |
| **D2** Tool Design + MCP | **18%** | Segment 2 |
| **D5** Context + Reliability | **15%** | Segment 3 |

**D1 + D3 + D4 = 67% of the exam.** Weight your study time the same way.
**D2 + D3 = 38%** - that pairing is why we covered both in one segment.
"""

_prep_stack_md = """\
## The prep stack

| Resource | Purpose |
|---|---|
| **Anthropic Academy: Claude 101** | Conceptual grounding (free) |
| **Anthropic Academy: Building with the API** | Messages API + tool use (free) |
| **Anthropic Academy: Intro to MCP** | Protocol shape, transports (free) |
| **Anthropic Academy: Claude Code in Action** | Claude Code CLI + hierarchy (free) |
| **CCA-F Exam Guide PDF** | Downloaded after registration |
| **Anthropic Practice Exam** | Target **>900/1000** before scheduling |
| **Community practice questions** (this notebook) | Calibration only, not predictors |

The Anthropic Practice Exam is the authoritative practice signal. Treat community questions (including the 60 in our `PRACTICE-QUESTIONS.md`) as calibration, not as predictors.
"""

_week_before_md = """\
## Tim's week-before-the-exam punchlist

The full 13-item version lives in [`../CERT-PROGRAM-BRIEFING.md`](../CERT-PROGRAM-BRIEFING.md). The headlines:

1. **Score >900** on the Anthropic Practice Exam cold
2. **Rebuild Segment 1 from memory** in 30 minutes (you should be able to write the agent loop and a hook without looking)
3. **Re-read `domain-1-agentic.md`** - it is the 27% domain
4. **Skim `domain-3-claude-code.md`** and `domain-4-prompts.md` - the 20% domains
5. **Verify proctoring setup** the night before (camera, mic, ID)
6. **Single attempt.** Do not schedule until 1-4 are green.
"""

_practice_intro_md = """\
## Weighted live practice (28 minutes)

We will run **10 questions** weighted across the four scenarios in our community study set. The 60-question full set ships as take-home in [`../PRACTICE-QUESTIONS.md`](../PRACTICE-QUESTIONS.md).

**Source disclaimer (read aloud once):**
> These questions are community-sourced from Paul Larionov's study repo. They are **calibration practice**, not exam predictors. Treat them as a self-assessment.

**Format per question (~2.5 minutes each):**
1. Read the situation
2. Cohort votes A/B/C/D in chat (30 seconds)
3. Reveal the correct answer
4. Walk through why the distractors are plausible-but-wrong
5. Color the correct answer with a production tip from the matching `domain-N-*.md` reference
"""

_practice_loader_code = """\
import json
import random
from collections import defaultdict
from pathlib import Path

REPO_ROOT = Path.cwd().parent if Path.cwd().name == "notebooks" else Path.cwd()
qs_path = REPO_ROOT / "practice-questions.json"
all_questions = json.loads(qs_path.read_text(encoding="utf-8"))

# Group by scenario for a weighted sample.
by_scenario: dict[str, list[dict]] = defaultdict(list)
for q in all_questions:
    by_scenario[q["scenario"]].append(q)

# Weight to match exam blueprint emphasis. The community set has 15 per
# scenario; we draw weighted to push the agentic + claude-code count up.
# Seed deterministic for reproducibility across cohorts.
SEED = 2026  # bump per cohort if you want a fresh set
rng = random.Random(SEED)

WEIGHTS = {
    "Multi-agent Research System": 3,        # ~ D1 Agentic
    "Customer Support Agent": 3,             # ~ D1 + D5
    "Claude Code for Continuous Integration": 2,  # ~ D3
    "Code Generation with Claude Code": 2,   # ~ D3 + D4
}

sample: list[dict] = []
for scenario, n in WEIGHTS.items():
    pool = by_scenario[scenario]
    sample.extend(rng.sample(pool, k=min(n, len(pool))))

assert len(sample) == 10, f"expected 10 sampled questions, got {len(sample)}"
print(f"Sampled {len(sample)} questions across {len(WEIGHTS)} scenarios (seed={SEED}):")
for i, q in enumerate(sample, 1):
    print(f"  {i:2d}. [{q['scenario'][:35]:<35}] q{q['n']:02d}")
"""

_practice_render_code = """\
from IPython.display import Markdown, display


def render_question(q: dict, i: int) -> None:
    md_lines = [
        f"### Practice question {i}: {q['scenario']} (q{q['n']:02d})",
        "",
        f"**Situation:** {q['situation']}",
        "",
        f"**Question:** {q['question']}",
        "",
    ]
    for opt in q["options"]:
        md_lines.append(f"- **{opt['letter']}.** {opt['text']}")
    md_lines.append("")
    md_lines.append("<details><summary><b>Reveal answer + explanation</b></summary>")
    md_lines.append("")
    md_lines.append(f"**Correct: {q['correct']}**")
    md_lines.append("")
    md_lines.append(q["explanation"])
    md_lines.append("")
    md_lines.append("</details>")
    md_lines.append("")
    md_lines.append("---")
    display(Markdown("\\n".join(md_lines)))


for i, q in enumerate(sample, 1):
    render_question(q, i)
"""

_final_qa_md = """\
## Final Q&A (10 minutes)

Anticipated questions to invite:

- **"How do I monitor an agent in production?"** Log every `stop_reason`, every tool call, every hook block. Three streams, one dashboard, before you ship.
- **"When do I split a monolithic agent into coordinator + subagents?"** When subtasks have independent success criteria, when context bloat hurts answer quality, or when you want per-agent tool scope. Do not split for theoretical purity.
- **"What is the cost story for prompt caching?"** `cache_control: {"type": "ephemeral", "ttl": "5m"}` on system prompts and large tool definitions. Hits run roughly 90% cheaper than misses. Cache writes cost more than reads, so do the math before assuming caching is free.
- **"How do I know when I am ready to sit the exam?"** When the Anthropic Practice Exam scores >900/1000 cold, and when you can rebuild Segment 1 from memory in 30 minutes.
- **"What is the renewal path?"** Anthropic reserves the right to retire and refresh exams. Per the public Exam Policy, certifications tied to beta products may expire when the production exam goes live. Watch the cert page.
"""

_course_recap_md = """\
## What you built today

- A **customer support agent** with deterministic policy enforcement via a PreToolUse hook (Segment 1)
- A configured **Claude Code environment** with CLAUDE.md hierarchy + MCP servers across three transports (Segment 2)
- An **invoice extraction pipeline** with Pydantic-driven schema enforcement and a bounded retry loop (Segment 3)
- A **production reliability mental model**: context pinning, output pruning, escalation triage, structured errors

You can rebuild any of these from this notebook tomorrow. That is the point.
"""

_close_md = """\
## Taking it further

1. **This week:** wire one of today's agents into a real production workflow. Do not let the demo code die in a notebook.
2. **Next:** read the 5 domain reference files in this repo for deeper dives - especially `domain-1-agentic.md` (27% domain) and `domain-5-context.md` (the topics Segment 3 did not have time for).
3. **Toward the exam:** work through [`../CERT-PROGRAM-BRIEFING.md`](../CERT-PROGRAM-BRIEFING.md), take the Anthropic Practice Exam (target >900/1000), then schedule. **One attempt only.**
4. **Calibration practice:** use [`../PRACTICE-QUESTIONS.md`](../PRACTICE-QUESTIONS.md) (community-sourced) to self-assess between Anthropic Practice Exam attempts.

Thanks for spending four hours. Now go ship something that does not lie.

> **Memento mori. Also, ship the PR.**
"""
