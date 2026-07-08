# slides

Slide decks for the **Claude Architect Foundations** course. The shipped deck for the July 2026 delivery is `warner-claude-architect-july-2026.pptx`, committed for archival so cohorts can grab the latest cut without a local Python toolchain.

## Build provenance

- **The committed deck is hand-authored.** `warner-claude-architect-july-2026.pptx` was cut by hand from the reference template, not emitted by the builder. Do **not** run `scripts/build-deck.py` expecting to reproduce it - the script generates a smaller scaffold cut and would overwrite the shipped file.
- **`scripts/build-deck.py` is a scaffold generator**, useful for starting a fresh deck from the reference template. It reads `C:/github/context-engineering/instructor/context-engineering-june-2026.pptx` and writes to the July filename. Run it only when you intend to regenerate from scratch:

  ```powershell
  uv run --with python-pptx python scripts/build-deck.py
  ```

- **Layout inheritance**: layouts come from Master 2 of the reference template - the rich Pluralsight-style library (`Section Header`, `Demo`, `Important Statement`, `Comparison: Point-by-Point`, `Up Next`, `Definition`, the `Code:` family). The build prefers Master 2 over Master 0 when names collide so section dividers and demo callouts carry the decorative master shapes.
- **Layout coverage** (measured against the shipped July 2026 deck): **89 slides across 17 distinct layouts**. The workhorses are `04_Content Slide (top title bar)` (29), `Title Only` (22), `Blank` (8), `Title_Content_No Bottom Bar` (6), and `Demo` (5).
- **Speaker notes**: written in Tim's voice (FRAMER opener + bracketed echoes + production-pattern callout where applicable). To rewrite the notes on the existing deck without touching layouts, use the `pluralsight-speaker-notes` skill at `~/.claude/skills/pluralsight-speaker-notes/`.

## Slide count and content

Total: **89 slides**, covering the four live segments plus the Segment 2.5 self-study bridge. The course package ships **seven notebooks** (five live + Segment 2.5 self-study + the off-clock `cca-f-exam-mastery.ipynb` reference); the deck covers the on-clock material and points at the two off-clock notebooks rather than teaching them.

## PDF exports

No PDF is committed. The May export was removed once it fell out of sync with the deck. If a cohort needs a PDF, export it fresh from the current `.pptx` so the two never drift.
