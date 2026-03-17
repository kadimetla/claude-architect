# Domain 5: Context Management & Reliability (15%)

## Context Preservation

Extract facts into persistent "case facts" block. Trim verbose tool outputs. Place summaries at beginning of inputs.

## Escalation

Escalate when: customer asks for human (honor immediately), policy is ambiguous, no progress possible.
Do NOT escalate based on: sentiment (doesn't correlate with complexity), self-reported confidence (poorly calibrated).

## Error Propagation

Structured error context enables coordinator recovery. Never suppress errors or terminate workflows on single failures.

## Provenance

Require claim-source mappings. When sources conflict, include both with attribution. Include publication dates.
