#!/usr/bin/env python3
"""
RETIRED 2026-05-22. Do not run this script. It writes nothing.

PRACTICE-QUESTIONS.md and practice-questions.json are now HAND-MAINTAINED.

This script used to regenerate both files from the upstream community study
repo's HTML (private/claude-certified-architect-main/practical_test_en.html),
parsing its embedded `const QUESTIONS = [...]` array and merging hand-assigned
CCA-F domain tags forward across runs.

It was retired because PRACTICE-QUESTIONS.md's 60 answer explanations were
expanded in-repo with per-distractor "why the other options miss" rationale
and reference links into Anthropic's official documentation (grounded via the
Context7 MCP server). None of that content exists in the upstream community
HTML, so re-running the extractor would silently overwrite roughly 60
questions' worth of authored work.

The original 193-line extraction implementation is preserved in git history.
To genuinely revive extraction you would first need to port the enhancements
upstream, or add a merge step that carries the authored explanations forward
the same way `merge_domain_tags` once carried domain tags forward.
"""
import sys


def main() -> int:
    """Print the retirement notice and exit non-zero without touching any file."""
    print(
        "extract-practice-questions.py is RETIRED and wrote nothing.\n"
        "PRACTICE-QUESTIONS.md and practice-questions.json are hand-maintained.\n"
        "Re-running extraction would overwrite authored explanations - see the\n"
        "module docstring. Edit the two files directly instead.",
        file=sys.stderr,
    )
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
