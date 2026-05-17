"""Generate the Claude Architect Foundations PPTX from the reference template.

Inherits layouts/theme from context-engineering-april-2026.pptx (Tim Warner's
proven O'Reilly live-training deck shape), then populates ~44 slides covering
the 4-segment course flow.

Slide budget (matches Context Engineering deck cadence):
- 4 intro slides:   cover, bio, course flow, opening epigraph
- 4 x 10 segments:  divider + ~9 content slides per segment
- 4 outro slides:   key takeaways, cert mention, resources, thank you
- Total:            ~48 slides

Output: C:/github/claude-architect/warner-claude-architect-may-2026.pptx
"""

from __future__ import annotations

import sys
from pathlib import Path

from pptx import Presentation
from pptx.util import Inches, Pt

REF = Path(r"C:/github/context-engineering/instructor/context-engineering-april-2026.pptx")
OUT = Path(r"C:/github/claude-architect/warner-claude-architect-may-2026.pptx")

# Layout names from the reference deck (master 0, first 11 layouts)
LAYOUT_TITLE_SLIDE = "Title Slide"
LAYOUT_TITLE_ONLY = "Title Only"           # for SEGMENT NN dividers + section markers
LAYOUT_CONTENT = "Title and Content"       # python-pptx-friendly fallback; predictable placeholders
LAYOUT_BLANK = "Blank"                     # for bespoke / quote slides

# ---------------------------------------------------------------------------
# Slide content definitions
# ---------------------------------------------------------------------------

# Each entry: (layout_name, title, body_lines_or_None, speaker_notes_or_None)
SLIDES: list[tuple[str, str, list[str] | None, str | None]] = [
    # ---- COURSE INTRO ----------------------------------------------------
    (
        LAYOUT_TITLE_SLIDE,
        "Claude Architect Foundations",
        ["A 4-hour O'Reilly Live Training", "Tim Warner | techtrainertim.com"],
        "Cold open: skills-first production-architecture course. Describe the CCA-F cert without teaching to exam items (exam not yet public). Set expectations: heavy on live demos, light on slides.",
    ),
    (
        LAYOUT_CONTENT,
        "Tim Warner",
        [
            "Microsoft MVP (Azure AI)",
            "Pluralsight Principal Author, 200+ courses, 1M+ learners",
            "O'Reilly Live Training instructor",
            "Microsoft Press / Pearson senior content developer",
            "28+ years on the Microsoft stack",
            "techtrainertim.com  |  github.com/timothywarner-org",
        ],
        "30 second bio. Mention you teach from first principles. No glazing, no fluff. If they want production patterns, they're in the right room.",
    ),
    (
        LAYOUT_CONTENT,
        "Course Flow (4 Segments x 50 min)",
        [
            "Segment 1 - Building AI Agents That Use Tools",
            "Segment 2 - Tool Design, Integration, and Claude Code Workflows",
            "Segment 3 - Prompt Engineering and Structured Output",
            "Segment 4 - Context Management, Reliability, and Production Strategy",
            "",
            "10-minute breaks between segments. Total 4 hours.",
        ],
        "Tell them where the slides + code live: github.com/timothywarner-org/claude-architect. Cert mention deferred to the end so we don't lead with exam mechanics.",
    ),
    (
        LAYOUT_BLANK,
        '"The model is non-deterministic. Your architecture cannot be."',
        None,
        "Frame the whole course in one sentence. Hooks are deterministic. Schemas are deterministic. Application-layer intercepts are deterministic. The model isn't, and that's fine.",
    ),

    # ---- SEGMENT 1: AGENTIC ARCHITECTURE --------------------------------
    (LAYOUT_TITLE_ONLY, "SEGMENT 01", None, "Domain 1: Agentic Architecture & Orchestration. 50 minutes. Heaviest exam weight (27 percent of the blueprint)."),
    (
        LAYOUT_CONTENT,
        "What you'll build",
        [
            "A customer support agent with backend tools",
            "Hook-enforced policy (refund cap, prerequisite checks)",
            "Structured escalation to human review",
            "By end of segment: you can sketch any agent topology",
        ],
        "This is the live build. Set expectations: we WILL hit edge cases. That's the point.",
    ),
    (
        LAYOUT_CONTENT,
        "The agentic loop",
        [
            "Send request -> model emits content + stop_reason",
            "Read stop_reason -> branch",
            "tool_use? Execute tool, append tool_result, loop",
            "end_turn? Return to user, done",
            "pause_turn? Resume in next request",
            "",
            "Never parse natural language to detect completion.",
        ],
        "The six stop_reason values: end_turn, max_tokens, stop_sequence, tool_use, pause_turn, refusal. Branch on the API field, not on what the model 'said'.",
    ),
    (
        LAYOUT_CONTENT,
        "Coordinator + subagents",
        [
            "ONE coordinator holds the user-facing thread",
            "Subagents get isolated contexts via the Task tool",
            "Subagent returns its final answer to the parent, not its working notes",
            "Split when: own success criteria, own tool subset, own context discipline",
            "Don't split for splitting's sake. Two coordinators chatting = one slow agent.",
        ],
        "Isolation is the feature. The parent doesn't drown in subagent reasoning. Reference: chief_of_staff_agent notebook.",
    ),
    (
        LAYOUT_CONTENT,
        "Hooks: deterministic guarantees",
        [
            "PreToolUse  - gate a call before it runs",
            "PostToolUse - audit, transform, log",
            "SessionStart - inject context",
            "Stop        - final verification",
            "",
            "Hooks run as YOUR code, not the model's. Anything that MUST happen, hook it.",
        ],
        "Show hooks-example.py in the demo. The $500 refund cap is the canonical example: prompt says 'don't refund over $500', hook ENFORCES it.",
    ),
    (
        LAYOUT_BLANK,
        "DEMO: Customer support agent (15 min)",
        None,
        "Open private/claude-cookbooks-main/tool_use/customer_service_agent.ipynb. Wire 4 tools. Add the refund-cap hook from hooks-example.py. Audience sees: agent skips verification -> hook blocks -> agent re-plans -> escalates. The aha moment is when the hook fires.",
    ),
    (
        LAYOUT_CONTENT,
        "Exercise (5 min)",
        [
            "Sketch architecture for a Developer Productivity scenario",
            "On paper or in chat: coordinator + 3 subagents + tool scope per agent",
            "What does each subagent specialize in?",
            "What's the success criterion for each?",
            "What tools does each get? (Cap each at ~5)",
        ],
        "Walk the room (chat) for 90 seconds, then share 2-3 designs out loud. Reinforce: tool descriptions > tool names; isolation > shared context.",
    ),
    (
        LAYOUT_CONTENT,
        "Segment 1 takeaways",
        [
            "Branch on stop_reason, not on natural-language signals",
            "Coordinator + isolated subagents beats one giant context",
            "Hooks turn 'should' into 'must'",
        ],
        "Bridge: 'You just built an agent that decides what to do. Next we go one level deeper, into the tools themselves and the Claude Code surface where you author them on a real team.'",
    ),

    # ---- SEGMENT 2: TOOLS + CLAUDE CODE (Domains 2 + 3) -----------------
    (LAYOUT_TITLE_ONLY, "SEGMENT 02", None, "Domains 2 + 3. 50 minutes. Heaviest segment (38 percent of exam weight combined). Two demos."),
    (
        LAYOUT_CONTENT,
        "Two domains, one segment",
        [
            "Domain 2 - Tool Design & MCP Integration (18% of blueprint)",
            "Domain 3 - Claude Code Configuration & Workflows (20%)",
            "Combined = 38%, the biggest chunk of the cert",
            "Why combined? Claude Code IS the primary MCP-consuming surface",
            "You can't teach one without the other in production",
        ],
        "Explain the merge. Tools live, Claude Code is where you orchestrate them. Different domains in the blueprint, same conversation in real life.",
    ),
    (
        LAYOUT_CONTENT,
        "Tool definitions: name + description + input_schema",
        [
            "name        - how the model invokes it",
            "description - STRONGLY recommended, drives selection",
            "input_schema - JSON Schema draft 2020-12 (type, properties, required)",
            "Optional: cache_control ephemeral (5m or 1h), strict: true",
            "",
            "Tool DESCRIPTIONS do the work, not tool NAMES.",
        ],
        "A tool named get_data with description 'Fetch customer record by ID' beats one named getCustomerRecordById with description 'Gets data.' Write descriptions like you're onboarding a junior engineer.",
    ),
    (
        LAYOUT_CONTENT,
        "Structured tool errors",
        [
            "Anti-pattern: raise exceptions from tool implementations",
            "Anti-pattern: return empty strings on failure",
            "Pattern: return tool_result content with is_error: true",
            "Add structured fields: errorCategory, isRetryable",
            "Model can then decide: retry, fall back, or escalate",
        ],
        "Thrown exceptions crash the agent. Structured errors let it recover. This is the entire reliability story for tools in one slide.",
    ),
    (
        LAYOUT_CONTENT,
        "tool_choice modes",
        [
            "auto - model decides (default)",
            "any  - must call SOME tool",
            "tool - must call THIS specific tool (force the schema)",
            "none - no tools allowed",
            "",
            "Force structured output: tool_choice {type: tool, name: extract_X}",
        ],
        "tool_choice tool + a Pydantic schema is the cheat code for structured output. We'll prove it in Segment 3.",
    ),
    (
        LAYOUT_CONTENT,
        "Cap agents at ~5 tools",
        [
            "More tools = worse selection accuracy",
            "Beyond 5: split into subagents with scoped tool sets",
            "Specificity in descriptions beats quantity of tools",
            "Anti-pattern: dump 30 tools into one agent because 'flexibility'",
        ],
        "Mention the analyze_dependencies vs Grep anti-pattern: model defaults to built-in Grep if custom tool description isn't specific enough.",
    ),
    (
        LAYOUT_CONTENT,
        "MCP server config (.mcp.json)",
        [
            "Three transports: stdio, SSE, HTTP",
            "stdio: command + args + env (local subprocess)",
            "SSE / HTTP: type + url + headers (remote)",
            "${ENV_VAR} expansion works in env, args, AND headers",
            "Project: ./.mcp.json    User: ~/.claude.json",
        ],
        "Show repo's own .mcp.json in the demo. Four servers, three transports, env-var expansion.",
    ),
    (
        LAYOUT_BLANK,
        "DEMO A: MCP config walkthrough (10 min)",
        None,
        "Open C:/github/claude-architect/.mcp.json in VS Code. Walk server-by-server: filesystem (stdio), github (stdio + ${GITHUB_TOKEN}), context7 (HTTP + header), internal-knowledge-base (SSE + bearer). Show what happens when GITHUB_TOKEN is unset.",
    ),
    (
        LAYOUT_CONTENT,
        "CLAUDE.md hierarchy",
        [
            "User    ~/.claude/CLAUDE.md           - your machine, every project",
            "Project ./CLAUDE.md                   - team conventions, in git",
            "Subtree ./<subdir>/CLAUDE.md         - on-demand when files in subdir are read",
            "Local   ./CLAUDE.local.md             - gitignored personal override",
            "",
            "Agent SDK: settingSources [user, project] loads both",
        ],
        "Loaded order matters. User + project additively. Subtree on demand keeps token budget tight. Local for personal preferences without polluting team.",
    ),
    (
        LAYOUT_CONTENT,
        "Plan mode vs. headless mode",
        [
            "Plan mode    - interactive, proposes plan, waits for approval. Default.",
            "Headless     - claude -p 'prompt', non-interactive, pipe-friendly",
            "             - --output-format json|stream-json for parsing",
            "             - --allowedTools 'Read,Edit,Bash' to scope",
            "",
            "Headless = THE CI/CD answer. Pre-commit hooks. PR review. Release notes.",
        ],
        "git log --oneline -20 | claude -p 'summarize these recent commits' - this is the demo callout for Segment 2 Demo B. Three seconds, one command, real value.",
    ),
    (
        LAYOUT_BLANK,
        "DEMO B: CLAUDE.md hierarchy + claude -p (5 min)",
        None,
        "Open this repo's own CLAUDE.md. Walk the structure. Run: claude -p 'audit this CLAUDE.md against the documented conventions'. Show the headless output. Pipe a git log into it.",
    ),
    (
        LAYOUT_CONTENT,
        "Exercise (5 min)",
        [
            "Design a CLAUDE.md hierarchy for a 3-team monorepo",
            "Teams: backend (Go), frontend (React/TS), infra (Terraform)",
            "Each team has different conventions",
            "Where does each rule go? User, project, subtree, or .claude/rules?",
            "What goes in .claude/rules/ with paths: globs?",
        ],
        "The correct answer: project CLAUDE.md for shared (commit style, security), subtree CLAUDE.md for team-specific conventions, .claude/rules with paths: globs for language-specific lint rules.",
    ),
    (
        LAYOUT_CONTENT,
        "Segment 2 takeaways",
        [
            "Descriptions, not names, drive tool selection",
            ".mcp.json: three transports, ${ENV} expansion, secrets in env never in file",
            "CLAUDE.md hierarchy is additive; claude -p is your CI/CD primitive",
        ],
        "Bridge: 'Tools give the agent hands. Prompts and schemas decide what comes out. Let's make those outputs trustworthy.'",
    ),

    # ---- SEGMENT 3: PROMPT ENGINEERING + STRUCTURED OUTPUT -------------
    (LAYOUT_TITLE_ONLY, "SEGMENT 03", None, "Domain 4: Prompt Engineering & Structured Output. 50 minutes. 20 percent of exam weight."),
    (
        LAYOUT_CONTENT,
        "What you'll build",
        [
            "An invoice extractor with Pydantic schema",
            "tool_choice forces the model to return validated JSON",
            "Validation-retry loop handles malformed output",
            "3 invoices: clean, missing field, ambiguous line item",
            "By end of segment: you can extract structured data from anything",
        ],
        "Set expectations: this is the LONGEST live build (20 min). Highest demo risk. If anything goes sideways, switch to the markdown walkthrough.",
    ),
    (
        LAYOUT_CONTENT,
        "Precise prompts > vague prompts",
        [
            "Be specific: format, edge cases, missing-data handling",
            "Plausible hallucinations: model invents values for nullable fields",
            "Fix: explicit 'return null if not directly stated' instruction",
            "Inconsistent formats: 'cotton blend' vs 'Cotton/Polyester mix'",
            "Fix: 2-3 few-shot examples, not lower temperature",
        ],
        "Few-shot beats temperature tuning every time. The model needs examples, not knobs.",
    ),
    (
        LAYOUT_CONTENT,
        "JSON schema via tool use",
        [
            "1. Define a Pydantic model with your fields",
            "2. Convert to JSON Schema (model.model_json_schema())",
            "3. Register as a tool's input_schema",
            "4. Set tool_choice {type: tool, name: <your_schema>}",
            "5. Model's tool_use input is now guaranteed to match the schema",
            "",
            "Optional: strict: true on the tool for guaranteed validation",
        ],
        "Walk through this in code in the demo. The Pydantic model is the source of truth for both runtime validation AND the API contract.",
    ),
    (
        LAYOUT_CONTENT,
        "Validation + retry loops",
        [
            "Effective: format errors, JSON parse failures, schema mismatches",
            "    -> append the error string as a user turn, retry",
            "    -> succeeds in 2-3 attempts",
            "Ineffective: knowledge gaps, ambiguous source data",
            "    -> retries DO NOT help",
            "    -> cap at 2-3, then escalate to human review",
        ],
        "Anti-pattern: infinite retry on missing-info failure. Burns tokens, model can't invent the data, escalation is the right move.",
    ),
    (
        LAYOUT_CONTENT,
        "Confidence-based routing",
        [
            "Have the model output field-level confidence: high | medium | low",
            "Route: high -> automated, medium -> spot-check, low -> human",
            "CRITICAL: validate accuracy by document type AND field",
            "Aggregate 95% accuracy can mask 60% accuracy on specific segments",
        ],
        "Per-segment calibration warning. If you don't break it down by doc type, high-aggregate accuracy lies to you.",
    ),
    (
        LAYOUT_BLANK,
        "DEMO: Invoice extractor live build (20 min)",
        None,
        "Open extracting_structured_json.ipynb + tool_use_with_pydantic.ipynb. Build Pydantic schema. Register as tool. Run on 3 invoices. Add validation-retry loop. This is the highest-demo-risk block of the course; have the markdown walkthrough open as fallback.",
    ),
    (
        LAYOUT_CONTENT,
        "Exercise (5 min)",
        [
            "Design an extraction schema for a domain you know",
            "Fields: required vs Optional[]",
            "Add a confidence Literal: 'high' | 'medium' | 'low'",
            "Add a notes Optional[str] for ambiguity",
            "Share your schema in chat",
        ],
        "Reinforces: nullable fields need explicit prompt instructions, confidence is the routing key, notes catches the 'I'm not sure' cases.",
    ),
    (
        LAYOUT_CONTENT,
        "Segment 3 takeaways",
        [
            "Pydantic + tool_choice tool = guaranteed valid JSON",
            "Few-shot examples beat temperature changes",
            "Retries help format errors; retries do NOT help missing info",
        ],
        "Bridge: 'We have agents, tools, prompts. Production is where context windows fill up and one bad tool result poisons the chain. Last segment is about not breaking when scale arrives.'",
    ),

    # ---- SEGMENT 4: CONTEXT + RELIABILITY ------------------------------
    (LAYOUT_TITLE_ONLY, "SEGMENT 04", None, "Domain 5: Context Management & Reliability. 50 minutes. 15 percent of exam weight + production strategy."),
    (
        LAYOUT_CONTENT,
        "Context preservation in long sessions",
        [
            "Pin case-facts at the top of every turn",
            "Summarize resolved turns into narrative",
            "Keep verbatim history ONLY for the active issue",
            "Prune verbose tool outputs - extract the fields you used, drop the rest",
            "Application-side filtering, before the next turn",
        ],
        "How lawyers manage case files. Same discipline for long agent sessions. 48-turn conversation should not have 48 turns of tool_result clutter.",
    ),
    (
        LAYOUT_CONTENT,
        "Escalation design",
        [
            "Honor explicit human requests IMMEDIATELY",
            "    'I want a human NOW' = escalate, don't clarify, don't try one more tool",
            "Pass STRUCTURED summary to the human queue, not the transcript",
            "Never escalate on sentiment alone (frustration != complexity)",
            "Confidence-based escalation: low confidence -> human review",
        ],
        "Frustrated user with a $5 refund doesn't need a human. Calm user with a multi-account billing dispute does. Sentiment is not complexity.",
    ),
    (
        LAYOUT_CONTENT,
        "Error propagation in multi-agent systems",
        [
            "Subagents return structured error context, not silently empty results",
            "Parent decides: retry, fall back to alternate subagent, or escalate",
            "Never swallow exceptions in tool implementations",
            "Tool errors as tool_result content with is_error: true",
            "Application exceptions crash the agent. Structured errors let it recover.",
        ],
        "The except: pass anti-pattern is the most common reliability bug. Catch errors. Return them. Let the model recover.",
    ),
    (
        LAYOUT_CONTENT,
        "Provenance and source attribution",
        [
            "Synthesis agents MUST preserve claim->source mappings from subagents",
            "Each subagent returns {claim, evidence, source, confidence}",
            "Synthesis agent keeps the source field on every claim it surfaces",
            "Include publication dates for dated information",
            "Anti-pattern: synthesis prose with no attribution",
        ],
        "No source = no claim. Treat attribution as a REQUIRED output field, not a nicety. This is the difference between a research agent and a hallucination machine.",
    ),
    (
        LAYOUT_BLANK,
        "DEMO: Context compaction (10 min)",
        None,
        "Open automatic-context-compaction.ipynb. Run a long convo. Watch compaction event fire. Show the summary the model generates. Explain when to use this vs. manual case-facts pinning.",
    ),
    (
        LAYOUT_CONTENT,
        "Production triage exercise (5 min)",
        [
            "For each failure, name the design fix:",
            "(a) Agent picked wrong tool for the task",
            "(b) Refund processed for $847 against $500 policy",
            "(c) Synthesis output has no source attributions",
            "(d) Agent escalated because user said 'I'm frustrated'",
        ],
        "Answers: (a) better descriptions + scope tools per agent, (b) hook intercept, (c) require claim-source mappings, (d) escalate on policy/complexity not sentiment.",
    ),

    # ---- COURSE WRAP ---------------------------------------------------
    (
        LAYOUT_CONTENT,
        "What you built today",
        [
            "Customer support agent with hook-enforced policy",
            "Configured Claude Code env with .mcp.json + CLAUDE.md hierarchy",
            "Invoice extractor with schema enforcement + validation retry",
            "Production reliability mental model: context, escalation, errors, provenance",
        ],
        "Recap the four artifacts. Tie back to the cold-open quote: model is non-deterministic, your architecture cannot be.",
    ),
    (
        LAYOUT_CONTENT,
        "About the CCA-F certification (2 min)",
        [
            "Anthropic's Claude Certified Architect: Foundations exam",
            "Not publicly available yet (as of May 2026)",
            "When it lands, the 5-domain blueprint is your study scaffold:",
            "  1. Agentic Architecture (27%)   - covered in Segment 1",
            "  2. Tool Design / MCP (18%)      - covered in Segment 2",
            "  3. Claude Code (20%)            - covered in Segment 2",
            "  4. Prompt Engineering (20%)     - covered in Segment 3",
            "  5. Context / Reliability (15%)  - covered in Segment 4",
        ],
        "Skills-first framing. We taught the skills behind the domains. The reference files in the repo (domain-N-*.md) map skills to exam objectives when the exam goes public.",
    ),
    (
        LAYOUT_CONTENT,
        "Resources and next steps",
        [
            "Repo: github.com/timothywarner-org/claude-architect",
            "Reference files: domain-1-agentic.md through domain-5-context.md",
            "Anthropic Academy: anthropic.skilljar.com (watch for exam launch)",
            "Anthropic docs: docs.claude.com",
            "Anthropic cookbooks: github.com/anthropics/anthropic-cookbook",
            "",
            "Next: wire one of today's patterns into a real workflow THIS WEEK",
        ],
        "If they don't ship something in 7 days, the muscle memory fades. Pick the smallest possible win and ship it.",
    ),
    (
        LAYOUT_TITLE_SLIDE,
        "Thank you",
        ["Tim Warner | techtrainertim.com", "github.com/timothywarner-org/claude-architect"],
        "Final Q&A. Anticipated questions: cost story for prompt caching, when to split an agent, monitoring production agents, MCP server hosting.",
    ),
]


def find_layout(prs: Presentation, name: str):
    """Return the first slide layout matching `name` from any master."""
    for master in prs.slide_masters:
        for layout in master.slide_layouts:
            if layout.name == name:
                return layout
    raise KeyError(f"Layout not found: {name!r}")


def set_title(slide, text: str) -> None:
    """Set the slide title placeholder, or add a styled text box if the layout has none.

    Blank layout has no title placeholder. Without this fallback, the title
    string is silently dropped. We instead render a large centered title box
    so demo / quote slides still surface their headline.
    """
    if slide.shapes.title is not None:
        slide.shapes.title.text = text
        return
    # Blank layout fallback: render the title as a large text box near the top.
    left, top, width, height = Inches(0.5), Inches(2.5), Inches(12.3), Inches(2.5)
    box = slide.shapes.add_textbox(left, top, width, height)
    tf = box.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = text
    for run in p.runs:
        run.font.size = Pt(40)
        run.font.bold = True


def set_body(slide, lines: list[str]) -> None:
    """Set the body content placeholder with one paragraph per line."""
    for ph in slide.placeholders:
        # Title placeholder has idx 0; skip it. Date/footer/slidenum live higher.
        if ph.placeholder_format.idx == 0:
            continue
        if ph.placeholder_format.idx in (1, 2):  # primary content slot
            tf = ph.text_frame
            tf.clear()
            for i, line in enumerate(lines):
                p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
                p.text = line
            return
    # If we got here, no usable body placeholder. Add a text box as fallback.
    left, top, width, height = Inches(0.5), Inches(1.5), Inches(12.3), Inches(5.5)
    box = slide.shapes.add_textbox(left, top, width, height)
    tf = box.text_frame
    tf.word_wrap = True
    for i, line in enumerate(lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.text = line
        for run in p.runs:
            run.font.size = Pt(18)


def set_notes(slide, text: str) -> None:
    """Write speaker notes for the slide."""
    notes_tf = slide.notes_slide.notes_text_frame
    notes_tf.text = text


def remove_all_slides(prs: Presentation) -> None:
    """Strip every slide from the deck AND drop their XML parts from the package.

    python-pptx's ``slides._sldIdLst.remove(...)`` only removes the index entry,
    leaving orphaned ``slide{N}.xml`` parts. Saving then produces duplicate-name
    warnings and a corrupt-looking deck. To truly purge, we drop both the
    relationship from the presentation part and the slide part itself.
    """
    sldIdLst = prs.slides._sldIdLst
    pres_part = prs.part
    # Snapshot since we mutate as we iterate.
    for sldId in list(sldIdLst):
        rId = sldId.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id')
        slide_part = pres_part.related_part(rId)
        pres_part.drop_rel(rId)
        sldIdLst.remove(sldId)
        # Drop the slide part from the package so the XML file is gone too.
        partname = slide_part.partname
        if partname in prs.part.package.iter_parts():
            pass
        # iter_parts is read-only iteration; use the package's internal dict.
        package = prs.part.package
        if partname in [p.partname for p in package.iter_parts()]:
            # python-pptx exposes _parts via the package's internal collection.
            try:
                del package._parts[partname]
            except (AttributeError, KeyError):
                pass


def main() -> int:
    if not REF.exists():
        print(f"ERROR: reference deck missing at {REF}", file=sys.stderr)
        return 1

    # Open the reference deck so we inherit its masters / theme / layouts,
    # then purge ALL existing slides (parts AND index entries) before building fresh.
    prs = Presentation(REF)
    remove_all_slides(prs)

    for layout_name, title, body, notes in SLIDES:
        try:
            layout = find_layout(prs, layout_name)
        except KeyError:
            # Fallback to Title and Content if the named layout is missing.
            layout = find_layout(prs, LAYOUT_CONTENT)

        slide = prs.slides.add_slide(layout)
        set_title(slide, title)
        if body:
            set_body(slide, body)
        if notes:
            set_notes(slide, notes)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    prs.save(OUT)

    size_mb = OUT.stat().st_size / (1024 * 1024)
    print(f"Wrote {OUT}")
    print(f"  Slides: {len(SLIDES)}")
    print(f"  Size:   {size_mb:.2f} MB")
    return 0


if __name__ == "__main__":
    sys.exit(main())
