# slides

Slide decks for the **Claude Architect Foundations** course. Built from `scripts/build-deck.py` against the reference O'Reilly template at `C:/github/context-engineering/instructor/context-engineering-april-2026.pptx`. The `.pptx` is committed for archival so cohorts can grab the latest cut without a local Python toolchain; rebuild from source with:

```powershell
uv run --with python-pptx python scripts/build-deck.py
```

## Build provenance

- **Source of truth**: `scripts/build-deck.py` (the slide tuples list). Deck is regenerated from this script on every rebuild.
- **Layout inheritance**: layouts come from Master 2 of the reference template - the rich Pluralsight-style library (49 layouts including `Section Header`, `Demo`, `Course Title`, `Important Statement`, `Comparison: Point-by-Point`, `Module Overview/Summary`, `Up Next`, `References-4 Items`). The build prefers Master 2 over Master 0 when names collide so section dividers and demo callouts carry the decorative master shapes.
- **Layout coverage** (as of 2026-05-21 rebuild): 49 slides across 10 distinct layouts. Zero fallback textboxes (every body sits in a proper placeholder).
- **Speaker notes**: written in Tim's voice (FRAMER opener + bracketed echoes + production-pattern callout where applicable). To rewrite the notes on the existing deck without touching layouts, use the `pluralsight-speaker-notes` skill at `~/.claude/skills/pluralsight-speaker-notes/`.

## Slide count and content

- 4 intro slides (cover, bio, course flow, opening epigraph)
- 4 segment arcs of ~10 slides each (divider + content + demo + exercise + takeaways)
- 1 Segment 2.5 bridge slide pointing at the self-study deep-dive notebook
- 5 wrap slides (recap, CCA-F brief, study path, resources, thank-you)

Total: **49 slides** matching the current 6-notebook course (Segments 0-4 live, Segment 2.5 self-study).
