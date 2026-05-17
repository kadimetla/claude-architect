#!/usr/bin/env python3
"""
Extract CCA-F practice questions from the community study repo's HTML test app.

.SYNOPSIS
    Reads private/claude-certified-architect-main/practical_test_en.html, locates
    the embedded `const QUESTIONS = [...];` JavaScript array, and writes two files
    at the repo root:

      - practice-questions.json   Machine-readable, schema mirrors source.
      - PRACTICE-QUESTIONS.md     Human-readable, grouped by scenario.

    Both outputs carry a top-of-file disclaimer: questions are community-sourced
    (Paul Larionov, github.com/paullarionov/claude-certified-architect), not
    Anthropic-authored, and intended for calibration only.

.DESCRIPTION
    Build-time only. Run once after the upstream HTML changes. Outputs are
    committed; this script is not a CI dependency.

    The extractor uses a non-greedy regex on the single-line minified array.
    If upstream reformats the HTML (e.g. pretty-prints the JS), the regex
    breaks and this script must be updated. The committed JSON keeps working.

.EXAMPLE
    python scripts/extract-practice-questions.py
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

REPO_ROOT: Path = Path(__file__).resolve().parent.parent
SOURCE_HTML: Path = REPO_ROOT / "private" / "claude-certified-architect-main" / "practical_test_en.html"
OUT_JSON: Path = REPO_ROOT / "practice-questions.json"
OUT_MD: Path = REPO_ROOT / "PRACTICE-QUESTIONS.md"

DISCLAIMER_MD: str = (
    "**Source:** community-contributed CCA-F study repo by Paul Larionov, "
    "[github.com/paullarionov/claude-certified-architect]"
    "(https://github.com/paullarionov/claude-certified-architect). "
    "Not Anthropic-authored. Use for calibration, not certification.\n\n"
    "These 60 multiple-choice questions are extracted verbatim from the "
    "community HTML test app. Voice and formatting reflect the community "
    "source, not this repo's style guide. The official CCA-F exam is not "
    "publicly available; treat any practice question as directional only.\n"
)


def extract_questions(html_text: str) -> list[dict[str, Any]]:
    """Pull the JS QUESTIONS array out of the HTML and parse it as JSON."""
    # The array is on one line: `const QUESTIONS = [{...}, {...}];`
    # Non-greedy so we stop at the first `];` that closes the array.
    match = re.search(r"const QUESTIONS\s*=\s*(\[.*?\]);", html_text, re.DOTALL)
    if match is None:
        raise SystemExit(
            "Could not locate `const QUESTIONS = [...]` in source HTML. "
            "The upstream community repo may have reformatted the file."
        )
    payload = match.group(1)
    try:
        return json.loads(payload)
    except json.JSONDecodeError as exc:
        raise SystemExit(f"QUESTIONS array did not parse as JSON: {exc}") from exc


def render_markdown(questions: list[dict[str, Any]]) -> str:
    """Render all questions to Markdown grouped by scenario, with collapsed answers."""
    by_scenario: dict[str, list[dict[str, Any]]] = {}
    for q in questions:
        scenario = q.get("scenario", "Uncategorized")
        by_scenario.setdefault(scenario, []).append(q)

    lines: list[str] = [
        "# CCA-F Practice Questions (Community-Sourced)",
        "",
        DISCLAIMER_MD,
        f"**Total questions:** {len(questions)} across {len(by_scenario)} scenarios.",
        "",
        "---",
        "",
    ]

    for scenario, items in by_scenario.items():
        lines.append(f"## {scenario}")
        lines.append("")
        for q in items:
            global_n = q.get("global_n", "?")
            situation = q.get("situation", "").strip()
            question_text = q.get("question", "").strip()
            options = q.get("options", [])
            correct_letter = q.get("correct", "")
            explanation = q.get("explanation", "").strip()

            lines.append(f"### Question {global_n}")
            lines.append("")
            if situation:
                lines.append(f"**Situation:** {situation}")
                lines.append("")
            lines.append(f"**Question:** {question_text}")
            lines.append("")
            for opt in options:
                letter = opt.get("letter", "?")
                text = opt.get("text", "").strip()
                lines.append(f"- **{letter}.** {text}")
            lines.append("")
            lines.append("<details>")
            lines.append(f"<summary>Show answer + explanation</summary>")
            lines.append("")
            lines.append(f"**Correct answer:** {correct_letter}")
            lines.append("")
            if explanation:
                lines.append(explanation)
            lines.append("")
            lines.append("</details>")
            lines.append("")
        lines.append("---")
        lines.append("")

    return "\n".join(lines)


def main() -> int:
    if not SOURCE_HTML.exists():
        print(f"Source HTML not found: {SOURCE_HTML}", file=sys.stderr)
        return 1

    html_text = SOURCE_HTML.read_text(encoding="utf-8")
    questions = extract_questions(html_text)

    OUT_JSON.write_text(
        json.dumps(questions, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    OUT_MD.write_text(render_markdown(questions), encoding="utf-8")

    print(f"Extracted {len(questions)} questions")
    print(f"  JSON: {OUT_JSON.relative_to(REPO_ROOT)}")
    print(f"  MD:   {OUT_MD.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
