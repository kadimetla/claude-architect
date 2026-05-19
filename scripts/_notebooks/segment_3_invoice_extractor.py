"""Cell builder for segment-3-invoice-extractor.ipynb.

Teaching-first notebook for Segment 3: Structured Output, Context, and
Production Reliability. Maps to CCA-F Domains 4 (Prompts, 20%) + 5
(Context, 15%) = 35% of the exam.
"""

from __future__ import annotations


def cells() -> list[tuple[str, str]]:
    return [
        ("md", _title_md),
        ("md", _lo_md),
        ("md", _concept_precise_prompts_md),
        ("md", _concept_forced_tool_md),
        ("md", _concept_context_md),
        ("md", _concept_escalation_md),
        ("md", _demo_setup_md),
        ("code", _imports_code),
        ("md", _demo_pydantic_md),
        ("code", _pydantic_code),
        ("code", _schema_print_code),
        ("md", _demo_extract_function_md),
        ("code", _extract_function_code),
        ("md", _demo_clean_md),
        ("code", _clean_code),
        ("md", _demo_missing_md),
        ("code", _missing_code),
        ("md", _demo_ambiguous_md),
        ("code", _ambiguous_code),
        ("md", _demo_pruning_md),
        ("code", _pruning_code),
        ("md", _exercise_md),
        ("md", _key_takeaways_md),
        ("md", _bridge_md),
    ]


_title_md = """\
# Segment 3: Structured Output, Context, and Production Reliability

**Duration:** 50 minutes
**Maps to:** CCA-F Domain 4 (Prompts + Structured Output, 20%) + Domain 5 (Context + Reliability, 15%)
**References:** [`../domain-4-prompts.md`](../domain-4-prompts.md), [`../domain-5-context.md`](../domain-5-context.md)

Segment 1 built the agent. Segment 2 wired its hands. Segment 3 makes the **outputs trustworthy**. We will use the **forced-tool-call pattern** to extract typed `Invoice` objects from messy raw text, with a bounded retry loop, then close on the context and escalation patterns that keep long sessions honest.
"""

_lo_md = """\
## Learning objectives

- Write **precise prompts** that specify format, edge cases, and missing-data behavior up front
- Use the **forced-tool-call pattern** to enforce a Pydantic-derived JSON schema, with a max-retry ceiling
- Preserve **case facts** and prune **verbose tool outputs** so long conversations stay coherent
- Distinguish **explicit human requests** (escalate now) from **sentiment signals** (don't escalate on frustration alone)
"""

_concept_precise_prompts_md = """\
## Precise prompts beat clever prompts

"Be accurate" is a wish, not a prompt. **Specify upfront:**

- **Format** - JSON? Markdown table? Plain prose? Pick one and say so.
- **Edge cases** - what does the output look like when the input is empty? malformed? ambiguous?
- **Missing data** - what should each field be when the source is silent? `null`? omitted? a sentinel?
- **Multiple interpretations** - if the input could mean two things, which one does the model pick?

**Two or three input-output examples** pin behavior more reliably than any temperature change. Few-shot is load-bearing.
"""

_concept_forced_tool_md = """\
## The forced-tool-call pattern for structured output

This is the canonical pattern for "the model must return data in *this exact shape*":

1. Define a **Pydantic model**.
2. Convert it to **JSON Schema** (`Model.model_json_schema()` does this for free).
3. Register the schema as a **tool's `input_schema`**.
4. Set `tool_choice={"type": "tool", "name": "<your_tool>"}` - the model **must** call it.
5. Validate the model's tool input against the Pydantic model. On `ValidationError`, append the error back and retry.
6. **Hard ceiling on retries.** Without it, a genuinely bad source burns 20 calls in a row.

The schema does the typing. The forced `tool_choice` does the shape. Your retry loop closes the gap.
"""

_concept_context_md = """\
## Case facts and tool-output pruning

Long sessions rot in three ways:

- **Case facts drift** - the account ID, the product, the environment all blur as turns pile up
- **Tool outputs bloat** - an 8KB JSON response of which you read three fields stays in context forever
- **Resolved sub-issues clutter** - turn 12 still carries the verbose discussion from turn 3

Three counters:

1. **Pin case facts at the top.** The model attends harder to the top and bottom of the window. Put fixed context (account ID, product, environment) in the first user turn or in the system prompt.
2. **Summarize resolved turns.** Once a sub-issue is done, replace its turns with a one-line summary. Keep verbatim only the active issue.
3. **Prune tool outputs.** If a tool returned 8KB and you used three fields, strip the rest before appending to context.

**Compaction** (the SDK's automatic summarization) is a fallback, not a strategy. Use it when window pressure hits despite the three counters above. The `automatic-context-compaction.ipynb` notebook in the upstream Anthropic cookbook is a post-class self-study lab.
"""

_concept_escalation_md = """\
## Escalation triage (the four real triggers)

Escalate to a human reviewer on:

| Trigger | Example |
|---|---|
| **Policy** | Refund above the agent cap |
| **Complexity** | Multi-system failure with no single owner |
| **Risk** | Security incident, compliance flag |
| **Explicit request** | "I want a human NOW" |

Do **not** escalate on sentiment. Frustration is not complexity. A customer saying "I'm frustrated" is venting; a customer saying "I want a human" is routing. The first is not a signal, the second is.

When you escalate, pass a **structured summary**, not the raw transcript. Human reviewers do not want to read 40 turns. They want: who, what, what has been tried, what is blocked.
"""

_demo_setup_md = """\
## Demo: invoice extractor with retry

We will build the structured-output pattern end to end. Three invoices in order:

1. **Clean** - all fields present, validates first try
2. **Missing field** - no PO number, `Optional[str]` handles it, no retry needed
3. **Ambiguous** - first pass fails validation, error is appended back, retry succeeds

Hard retry ceiling: **1**. A real bad document should fail loudly, not silently burn $20 in retries.
"""

_imports_code = """\
import json
import os
from pathlib import Path
from typing import Any, Optional

from anthropic import Anthropic
from pydantic import BaseModel, Field, ValidationError

try:
    from dotenv import load_dotenv
    load_dotenv(Path.cwd().parent / ".env")
except ImportError:
    pass

client = Anthropic()
MODEL = "claude-sonnet-4-6"
"""

_demo_pydantic_md = """\
## Step 1: the Pydantic model

Required fields drive validation errors. `Optional[]` fields say "this can be `None`". `Field(description=...)` strings flow into the JSON Schema, which the model reads to understand what each field means.
"""

_pydantic_code = """\
class Invoice(BaseModel):
    \"\"\"A vendor invoice extracted from raw text.

    Required fields fail validation if missing. Optional fields come back
    as None when the source text does not mention them.
    \"\"\"
    invoice_number: str = Field(description="Invoice ID printed by the vendor, e.g. INV-2026-0481")
    vendor: str = Field(description="Vendor / company name issuing the invoice")
    total: float = Field(description="Total amount due in USD, no currency symbol")
    po_number: Optional[str] = Field(default=None, description="Purchase order number if printed on the invoice")
    notes: Optional[str] = Field(default=None, description="Free-form notes from the invoice memo line")
    due_date: Optional[str] = Field(default=None, description="ISO 8601 due date if present, e.g. 2026-06-15")


# The Pydantic model and the JSON Schema view of it agree by construction.
print(f"Required fields: {sorted(Invoice.model_fields[name].is_required() and name for name in Invoice.model_fields if Invoice.model_fields[name].is_required())}")
"""

_schema_print_code = """\
schema = Invoice.model_json_schema()
print(json.dumps(schema, indent=2))
"""

_demo_extract_function_md = """\
## Step 2: register as a tool, force the call, retry on ValidationError

Three loadbearing lines:

- `tool_choice={"type": "tool", "name": "extract_invoice"}` - the model **must** call this tool
- `Invoice(**block.input)` - the validation gate
- `max_retries=1` - the ceiling, hard-coded
"""

_extract_function_code = """\
EXTRACT_TOOL = {
    "name": "extract_invoice",
    "description": (
        "Extract structured invoice data from raw text. Required fields "
        "(invoice_number, vendor, total) MUST be present in the text - if "
        "any is missing, return a best-effort guess and let the validator "
        "fail. Optional fields (po_number, notes, due_date) should be null "
        "when the text is silent. Do NOT invent values."
    ),
    "input_schema": Invoice.model_json_schema(),
}

SYSTEM_PROMPT = (
    "You are an invoice extraction service. For each raw invoice text the "
    "user provides, call the extract_invoice tool with the structured fields. "
    "Do not respond in prose. Do not invent fields the source text does not "
    "contain - leave optional fields null."
)


def extract_invoice(raw_text: str, max_retries: int = 1) -> Invoice:
    \"\"\"Extract a typed Invoice from raw text via forced tool call.

    Why max_retries=1: a genuinely bad source will fail validation every
    time. Letting it retry 20 times burns money silently. One retry gives
    the model a chance to react to its own error, then we fail loud.
    \"\"\"
    messages: list[dict[str, Any]] = [
        {"role": "user", "content": f"Extract the invoice from this text:\\n\\n{raw_text}"}
    ]
    last_error: str | None = None

    for attempt in range(max_retries + 1):
        resp = client.messages.create(
            model=MODEL,
            max_tokens=600,
            system=SYSTEM_PROMPT,
            tools=[EXTRACT_TOOL],
            tool_choice={"type": "tool", "name": "extract_invoice"},
            messages=messages,
        )
        print(f"  [attempt {attempt}] stop_reason={resp.stop_reason}")

        tool_block = next((b for b in resp.content if b.type == "tool_use"), None)
        assert tool_block is not None, "forced tool_choice but no tool_use block?"

        try:
            invoice = Invoice(**tool_block.input)
            print(f"  [attempt {attempt}] validated OK")
            return invoice
        except ValidationError as exc:
            last_error = str(exc)
            print(f"  [attempt {attempt}] ValidationError: {last_error[:150]}")
            if attempt == max_retries:
                break
            # Feed the error back so the model can correct itself
            messages.append({"role": "assistant", "content": resp.content})
            messages.append({
                "role": "user",
                "content": [{
                    "type": "tool_result",
                    "tool_use_id": tool_block.id,
                    "is_error": True,
                    "content": (
                        f"Your previous extract_invoice call failed Pydantic "
                        f"validation. Fix the input and retry:\\n{last_error}"
                    ),
                }],
            })

    raise RuntimeError(f"extract_invoice exhausted retries: {last_error}")
"""

_demo_clean_md = """\
## Scenario A: clean invoice (first-try validation)

All required fields present. Optional fields populated. One attempt, one success.
"""

_clean_code = """\
CLEAN_INVOICE = '''
ACME Audio Supply Co.
Invoice INV-2026-0481
Bill to: Warner Co., Nashville TN
PO: PO-9912
Date: 2026-05-15  Due: 2026-06-15

Item                                      Qty   Unit    Total
Studio monitor pair (8" near-field)        1    1200    1200.00
Cable bundle, balanced XLR                 2     45      90.00
                                                      --------
                                          Subtotal    1290.00
                                          Tax         103.20
                                          TOTAL DUE   1393.20

Notes: Net 30. Wire transfer preferred.
'''

print("--- SCENARIO A: clean invoice ---")
invoice = extract_invoice(CLEAN_INVOICE)
print(f"\\nResult: {invoice.model_dump_json(indent=2)}")
"""

_demo_missing_md = """\
## Scenario B: missing field (Optional handles it, no retry)

No PO number on this invoice. The `Optional[str]` field comes back `None`. Validation succeeds on the first attempt because `po_number` was never required.
"""

_missing_code = """\
MISSING_PO_INVOICE = '''
RIVERSIDE PRESS BOOKS
Invoice #INV-2026-0552

Bill to: Warner Co.
Date: 2026-05-18

  Title                                    Qty    Price
  "Stoic Practices for Engineers"           20    14.00    280.00
  Shipping                                                  18.50
                                                          -------
                                              TOTAL DUE    298.50

Thanks for your business.
'''

print("--- SCENARIO B: missing PO field ---")
invoice = extract_invoice(MISSING_PO_INVOICE)
print(f"\\nResult: {invoice.model_dump_json(indent=2)}")
assert invoice.po_number is None, "po_number should be None when source is silent"
print("[OK] po_number is None as expected")
"""

_demo_ambiguous_md = """\
## Scenario C: ambiguous total (first-pass ValidationError, retry succeeds)

This invoice has a handwritten total that could be parsed two ways. The model's first guess may not validate as a `float`. The error gets appended back, the model corrects on attempt 1, the loop exits.

If both attempts fail, we raise. Hard ceiling means we fail loud, not silently.
"""

_ambiguous_code = """\
AMBIGUOUS_INVOICE = '''
GIBSON GUITAR SERVICE
Service Invoice INV-2026-0617
Customer: T. Warner

  Fret level + crown                        180.00
  Nut replacement (bone)                     65.00
  Setup, intonation, restring               120.00
  Shop supplies                              ~22.50 (estimate)
                                          ----------
                                Total      "three eighty seven, fifty"

Pay on pickup. No card fees.
'''

print("--- SCENARIO C: ambiguous total ---")
try:
    invoice = extract_invoice(AMBIGUOUS_INVOICE, max_retries=1)
    print(f"\\nResult: {invoice.model_dump_json(indent=2)}")
except RuntimeError as exc:
    print(f"\\n[fail-loud] {exc}")
    print("This is the correct behavior when a genuinely bad source exhausts retries.")
"""

_demo_pruning_md = """\
## Sidebar: tool-output pruning (not executed)

A tool returns 8KB of JSON. You used three fields. The other 7.5KB is paying rent in the context window. Strip it.
"""

_pruning_code = """\
def prune_tool_output(payload: dict[str, Any], keep_fields: list[str]) -> dict[str, Any]:
    \"\"\"Return a pruned copy of a tool payload containing only keep_fields.

    Why: large tool outputs bloat the context window and degrade attention.
    If the rest is genuinely needed in a later turn, refetch it; tokens
    saved are tokens you can spend on better reasoning.
    \"\"\"
    return {k: payload[k] for k in keep_fields if k in payload}


# Illustration only, not part of the live demo
bloated = {
    "order_id": "4471",
    "status": "delivered",
    "items": ["Pro studio monitor speaker (pair)"],
    "total_usd": 750,
    "audit_log": [{"ts": "...", "actor": "...", "action": "..."}] * 50,  # noise
    "fulfillment": {"...": "..."},  # noise
    "carrier_metadata": {"...": "..."},  # noise
}
keep = ["order_id", "status", "total_usd"]
print(f"original keys: {sorted(bloated)}")
print(f"pruned keys:   {sorted(prune_tool_output(bloated, keep))}")
print(f"size: {len(json.dumps(bloated))} -> {len(json.dumps(prune_tool_output(bloated, keep)))} bytes")
"""

_exercise_md = """\
## Exercise: triage scorecard (5 minutes)

For each failure below, name the **design fix** in one sentence. Pattern recognition is the skill.

| # | Failure | Your fix |
|---|---|---|
| a | Agent picked the wrong tool for the task | ? |
| b | Refund processed for $847 against a $500 policy | ? |
| c | Synthesis output has no source attributions | ? |
| d | Agent escalated because the user said "I'm frustrated" | ? |

Reference answers:

- **(a)** Tighten **tool descriptions** and/or **scope tools per agent**; consider `tool_choice` to force the right call.
- **(b)** **Application-layer intercept via a PreToolUse hook**, not a prompt instruction. Policy is code, not vibes.
- **(c)** Require **structured claim-source mappings** from subagents; coordinator preserves them through synthesis.
- **(d)** Escalate on **policy, complexity, risk, or explicit request**. Sentiment is not a signal.
"""

_key_takeaways_md = """\
## Key takeaways

- **Forced tool calls + Pydantic schemas + max-retry ceiling** are the canonical structured-output pattern.
- **Case facts pinned at the top + tool-output pruning** keep long conversations coherent without burning tokens. Compaction is a fallback.
- **Escalation triggers on policy, complexity, risk, or explicit request**. Sentiment is not a signal.
- Further self-study: [`../domain-5-context.md`](../domain-5-context.md) covers error propagation, provenance preservation, and confidence calibration.
"""

_bridge_md = """\
## Bridge to Segment 4

> "You now have the skills. The exam is how you signal them. Last segment is the certification debrief: what's on it, what Anthropic expects, and ten practice questions to calibrate where you stand."

Open `segment-4-cca-f-capstone.ipynb`.
"""
