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
        ("md", _demo_few_shot_md),
        ("code", _few_shot_code),
        ("md", _demo_confidence_md),
        ("code", _confidence_code),
        ("md", _demo_case_facts_md),
        ("code", _case_facts_code),
        ("md", _demo_pruning_md),
        ("code", _pruning_code),
        ("md", _exercise_md),
        ("md", _key_takeaways_md),
        ("md", _bridge_md),
        ("md", _appendix_md),
    ]


_title_md = """\
# Segment 3: Structured Output, Context, and Production Reliability

**Duration:** 50 minutes
**Maps to:** CCA-F Domain 4 (Prompts + Structured Output, 20%) + Domain 5 (Context + Reliability, 15%)
**References:** [`../docs/domain-4-prompts.md`](../docs/domain-4-prompts.md), [`../docs/domain-5-context.md`](../docs/domain-5-context.md)

Segment 1 built the agent, Segment 2 wired its hands, and Segment 3 makes the **outputs trustworthy**. We'll extract typed `Invoice` objects from messy text with the **forced-tool-call pattern**, then close on the context and escalation levers that keep long sessions honest.
"""

_lo_md = """\
## Learning objectives

- Write **precise prompts** that specify format, edge cases, and missing-data behavior up front
- Use the **forced-tool-call pattern** to enforce a Pydantic-derived JSON schema behind a max-retry ceiling
- Pin **few-shot examples** to lock corner-case behavior that prose can't describe
- Attach a **confidence score** and route low-confidence rows to human review
- Preserve **case facts** with `cache_control` and **prune verbose tool outputs**
- Separate **explicit human requests** from **sentiment signals** when deciding to escalate
"""

_concept_precise_prompts_md = """\
## Precise prompts beat clever prompts

"Be accurate" is a wish, not a prompt. Specify four things up front:

- **Format** - JSON, table, or prose. Pick one, say so.
- **Edge cases** - the output shape on empty or malformed input.
- **Missing data** - `null`, omitted, or a sentinel when the source is silent.
- **Ambiguity** - which reading wins when the input supports two.

**Two or three worked examples** pin behavior more reliably than any temperature change.
"""

_concept_forced_tool_md = """\
## The forced-tool-call pattern for structured output

The canonical pattern for "return data in *this exact shape*":

1. Define a **Pydantic model**.
2. Convert it to **JSON Schema** with `Model.model_json_schema()`.
3. Register that as a **tool's `input_schema`**.
4. Force the call with **`tool_choice={"type": "tool", "name": "<your_tool>"}`**.
5. **Validate** the tool input. On `ValidationError`, append the error back and retry.
6. Enforce a **hard retry ceiling**, or a bad source burns 20 calls.

The schema does the typing, the forced `tool_choice` does the shape, and the retry loop closes the gap.
"""

_concept_context_md = """\
## Case facts and tool-output pruning

Long sessions rot three ways, and each has a counter:

| Failure | Counter |
|---|---|
| **Case facts drift** as turns pile up | **Pin them** in the system prompt. The model attends hardest to the window's top and bottom. |
| **Tool outputs bloat** - 8KB in, three fields read | **Prune** before appending. |
| **Resolved sub-issues clutter** later turns | **Summarize** them. Keep only the active issue verbatim. |

**Compaction** is the fallback for when window pressure hits anyway, not the strategy.
"""

_concept_escalation_md = """\
## Escalation triage (the four real triggers)

Escalate to a human on exactly four triggers:

| Trigger | Example |
|---|---|
| **Policy** | Refund above the agent cap |
| **Complexity** | Multi-system failure, no single owner |
| **Risk** | Security incident, compliance flag |
| **Explicit request** | "I want a human NOW" |

**Don't escalate on sentiment.** "I'm frustrated" is venting, "I want a human" is routing. When you do escalate, hand over a **structured summary** rather than the raw transcript: who, what, what's been tried, what's blocked.
"""

_demo_setup_md = """\
## Demo: invoice extractor with retry

Three invoices, in order of nastiness:

1. **Clean** - all fields present, validates first try.
2. **Missing field** - no PO number, `Optional[str]` handles it, no retry.
3. **Ambiguous** - first pass fails, the error goes back, the retry succeeds.

The retry ceiling is **1**, because a truly bad document should fail loudly instead of burning $20 in silence.
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
# Principled exception to the course's Haiku-default policy. Nested invoice
# schemas with line-item arrays + retry-on-validation-error is the one demo
# where Sonnet 4.6's reasoning depth measurably lifts extraction accuracy.
# Everywhere else in the course: Haiku 4.5.
MODEL = "claude-sonnet-4-6"
"""

_demo_pydantic_md = """\
## Step 1: the Pydantic model

**Analogy: the passport form.** Required fields get you turned away at the border, optional fields you may leave blank, and every field carries a description telling you what to write.

- **Required fields** drive the validation errors.
- **`Optional[]`** says "`None` is legal here."
- **`Field(description=...)`** flows into the JSON Schema the model actually reads.
"""

_pydantic_code = """\
class Invoice(BaseModel):
    \"\"\"A vendor invoice extracted from raw text.

    Required fields fail validation if missing. Optional fields come back
    as None when the source text does not mention them.
    \"\"\"
    # --- REQUIRED FIELDS (no default; validation fails if missing) ---
    # The description strings here are CRITICAL. They become part of the
    # JSON Schema that the model reads to know what each field MEANS.
    # "Invoice ID printed by the vendor, e.g. INV-2026-0481" is a much
    # better instruction than just "invoice_number: str".
    invoice_number: str = Field(description="Invoice ID printed by the vendor, e.g. INV-2026-0481")
    vendor: str = Field(description="Vendor / company name issuing the invoice")
    total: float = Field(description="Total amount due in USD, no currency symbol")

    # --- OPTIONAL FIELDS (default=None; absent in source -> None in output) ---
    # Optional[str] is the form's "leave blank if not applicable" line.
    # The model is explicitly TOLD (via description) that these may be
    # null. Without the default=None, Pydantic would treat them as
    # required and the model would invent values to pass validation -
    # exactly what we DON'T want.
    po_number: Optional[str] = Field(default=None, description="Purchase order number if printed on the invoice")
    notes: Optional[str] = Field(default=None, description="Free-form notes from the invoice memo line")
    due_date: Optional[str] = Field(default=None, description="ISO 8601 due date if present, e.g. 2026-06-15")


# Inspect what Pydantic considers REQUIRED. The model receives the same
# information via the JSON Schema, so this print is a sanity check that
# the schema matches our intent.
print(f"Required fields: {sorted(Invoice.model_fields[name].is_required() and name for name in Invoice.model_fields if Invoice.model_fields[name].is_required())}")
"""

_schema_print_code = """\
schema = Invoice.model_json_schema()
print(json.dumps(schema, indent=2))
"""

_demo_extract_function_md = """\
## Step 2: register as a tool, force the call, retry on ValidationError

**Analogy: the customs counter.** Pydantic reads every field and hands the form back with red ink if anything's missing or wrong-typed. The traveler gets one correction, then the case goes to a supervisor.

Three load-bearing lines:

- **`tool_choice={"type": "tool", "name": "extract_invoice"}`** - the model must call this tool.
- **`Invoice(**block.input)`** - the validation gate.
- **`max_retries=1`** - the ceiling, hard-coded.
"""

_extract_function_code = """\
# Register the Pydantic schema AS a tool. The input_schema field is
# Invoice.model_json_schema() - the exact JSON Schema view of our
# Pydantic model. The model will receive this schema and produce output
# that conforms to it (or tries to).
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

# The system prompt enforces three operational rules:
#   1. Always call the tool (no prose responses)
#   2. Leave optional fields null when the source is silent
#   3. Never invent values to make required fields work
# Rule 3 is the load-bearing one. Without it, the model will fill
# required fields with plausible-looking fabrications and pass validation
# with garbage. We'd rather see a ValidationError than a confident lie.
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
    # Initial conversation: just the user's raw invoice text.
    # On a retry, we APPEND the failure context to this list.
    messages: list[dict[str, Any]] = [
        {"role": "user", "content": f"Extract the invoice from this text:\\n\\n{raw_text}"}
    ]
    last_error: str | None = None

    # Retry loop. range(max_retries + 1) means: attempt 0 is the first
    # try, attempt 1 is the retry. With max_retries=1, total = 2 tries.
    for attempt in range(max_retries + 1):
        # --- THE FORCED CALL ---
        # tool_choice={"type": "tool", "name": "..."} is the forced left
        # turn. The model has exactly one legal move: call extract_invoice.
        # No prose answer, no "let me think about that" - the API enforces
        # the call.
        resp = client.messages.create(
            model=MODEL,
            max_tokens=600,
            system=SYSTEM_PROMPT,
            tools=[EXTRACT_TOOL],
            tool_choice={"type": "tool", "name": "extract_invoice"},
            messages=messages,
        )
        print(f"  [attempt {attempt}] stop_reason={resp.stop_reason}")

        # Extract the tool_use block. With forced tool_choice this MUST
        # exist - the assert is a contract check, not defensive code.
        # If it ever fails, the API contract broke.
        tool_block = next((b for b in resp.content if b.type == "tool_use"), None)
        assert tool_block is not None, "forced tool_choice but no tool_use block?"

        # --- THE CUSTOMS COUNTER ---
        # Invoice(**block.input) is the validation gate. Pydantic checks
        # required fields, types, and Optional handling. If it passes,
        # we have a TYPED Invoice object - no None checks, no type
        # assertions, the rest of our code can trust the shape.
        try:
            invoice = Invoice(**tool_block.input)
            print(f"  [attempt {attempt}] validated OK")
            return invoice  # happy path - return typed object
        except ValidationError as exc:
            # The form came back from customs with red ink on it.
            last_error = str(exc)
            print(f"  [attempt {attempt}] ValidationError: {last_error[:150]}")

            # If this was the last allowed attempt, give up and surface
            # the error. Better a loud failure than a silent retry loop.
            if attempt == max_retries:
                break

            # Otherwise, feed the error BACK to the model in the
            # conversation so it can see what went wrong and try again.
            # The shape: append the assistant's tool_use, then a user
            # message containing a tool_result with is_error=True.
            # The model reads "your call failed because X; fix and retry."
            messages.append({"role": "assistant", "content": resp.content})
            messages.append({
                "role": "user",
                "content": [{
                    "type": "tool_result",
                    "tool_use_id": tool_block.id,
                    "is_error": True,                      # <-- not a result
                    "content": (
                        f"Your previous extract_invoice call failed Pydantic "
                        f"validation. Fix the input and retry:\\n{last_error}"
                    ),
                }],
            })

    # Exhausted retries. Raise so the caller knows extraction failed -
    # do NOT return a partial Invoice; downstream code would silently use
    # the bad data.
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

No PO number here, so the **`Optional[str]`** field comes back `None` and validation passes on the first attempt.
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

The handwritten total parses two ways, so the model's first guess may not validate as a `float`. The **error gets appended back**, the model corrects on attempt 1, and the loop exits. If both attempts fail we raise, because the **hard ceiling** means failing loud beats failing silent.
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

_demo_few_shot_md = """\
## Few-shot: pinning corner cases (Domain 4)

Prose describes behavior. **Examples lock it.** For the corner cases prose can't reach - decimal commas, regional date formats, optional fields the model itches to invent - two or three worked examples beat any amount of instruction tuning.

**The shape:** past `user` / `assistant` turns where the assistant called the tool *correctly*. The model imitates. Below, the **hand-crafted assistant turn** teaches it to respect a German invoice's decimal comma and DD/MM/YYYY date instead of assuming US conventions.

Cookbook anchor: `../claude-cookbooks-main/tool_use/extracting_structured_json.ipynb`.
"""

_few_shot_code = """\
TRICKY_INVOICE = '''
EUROVOX SOUND GMBH
Rechnung INV-2026-0701
Kunde: Warner Co.
Datum: 15/05/2026   Faellig: 14/06/2026

Bezeichnung                        Menge    Preis     Summe
Mikrofon-Vorverstaerker (Class A)     1     480,00    480,00
Versand (DHL Express)                                  35,00
                                                    --------
                                     TOTAL EUR        515,00

Hinweis: Zahlung per Ueberweisung. 30 Tage netto.
'''

FEW_SHOT_HISTORY = [
    {
        "role": "user",
        "content": "Extract the invoice from this text:\\n\\nINV-2025-0099, Vendor: SoundTrek BV, Total EUR 240,50, Date: 03/04/2025 (DD/MM/YYYY)",
    },
    {
        "role": "assistant",
        "content": [{
            "type": "tool_use",
            "id": "shot-1",
            "name": "extract_invoice",
            "input": {
                "invoice_number": "INV-2025-0099",
                "vendor": "SoundTrek BV",
                "total": 240.50,
                "po_number": None,
                "notes": None,
                "due_date": None,
            },
        }],
    },
    {
        "role": "user",
        "content": [{
            "type": "tool_result",
            "tool_use_id": "shot-1",
            "content": "OK",
        }],
    },
]


def extract_with_few_shot(raw_text: str) -> Invoice:
    \"\"\"Same forced-tool-call pattern, but with a few-shot history attached.\"\"\"
    messages = list(FEW_SHOT_HISTORY) + [
        {"role": "user", "content": f"Extract the invoice from this text:\\n\\n{raw_text}"}
    ]
    resp = client.messages.create(
        model=MODEL, max_tokens=600, system=SYSTEM_PROMPT,
        tools=[EXTRACT_TOOL],
        tool_choice={"type": "tool", "name": "extract_invoice"},
        messages=messages,
    )
    print(f"  [few-shot] stop_reason={resp.stop_reason}")
    tool_block = next(b for b in resp.content if b.type == "tool_use")
    return Invoice(**tool_block.input)


print("--- Few-shot extraction on a European-format invoice ---")
invoice = extract_with_few_shot(TRICKY_INVOICE)
print(invoice.model_dump_json(indent=2))
print()
print("Note the decimal comma (515,00 EUR) and the DD/MM/YYYY date format.")
print("Few-shot examples teach the model to respect the source's conventions.")
"""

_demo_confidence_md = """\
## Confidence scores: routing low-confidence rows to a human

High-stakes extraction wants more than the values. Add a **`confidence: float`** field to the Pydantic model, and the forced tool call makes the model commit to a number your routing code can read.

The score **isn't calibrated** (models skew overconfident), but it's still useful, because the lowest-confidence rows genuinely are the ones worth a second look.
"""

_confidence_code = """\
class InvoiceWithConfidence(Invoice):
    \"\"\"Same fields as Invoice plus a self-reported confidence score.\"\"\"
    confidence: float = Field(
        ge=0.0, le=1.0,
        description=(
            "Self-reported confidence in this extraction, 0.0 to 1.0. "
            "Lower the score when fields are ambiguous, handwritten, or "
            "you had to guess a missing-but-required value."
        ),
    )


EXTRACT_WITH_CONFIDENCE = {
    "name": "extract_invoice",
    "description": EXTRACT_TOOL["description"] + (
        " Always include a confidence score. Use < 0.6 when any required "
        "field was ambiguous, < 0.8 when optional fields had to be inferred."
    ),
    "input_schema": InvoiceWithConfidence.model_json_schema(),
}

CONFIDENCE_THRESHOLD = 0.7


def extract_with_confidence(raw_text: str) -> InvoiceWithConfidence:
    resp = client.messages.create(
        model=MODEL, max_tokens=600, system=SYSTEM_PROMPT,
        tools=[EXTRACT_WITH_CONFIDENCE],
        tool_choice={"type": "tool", "name": "extract_invoice"},
        messages=[{"role": "user", "content": f"Extract the invoice from this text:\\n\\n{raw_text}"}],
    )
    tool_block = next(b for b in resp.content if b.type == "tool_use")
    return InvoiceWithConfidence(**tool_block.input)


for label, text in [("clean", CLEAN_INVOICE), ("ambiguous", AMBIGUOUS_INVOICE)]:
    print(f"--- {label} ---")
    try:
        inv = extract_with_confidence(text)
        verdict = "HUMAN REVIEW" if inv.confidence < CONFIDENCE_THRESHOLD else "auto-approve"
        print(f"  confidence={inv.confidence:.2f}  -> {verdict}")
        print(f"  total={inv.total}, vendor={inv.vendor}")
    except Exception as exc:  # noqa: BLE001 - teaching demo
        print(f"  [error] {type(exc).__name__}: {exc}")
    print()
"""

_demo_case_facts_md = """\
## Pinning case facts with `cache_control` (Domain 5)

A long extraction session re-reads the same vendor rules, currency rules, and "don't invent values" prompt on every call. Those are billed tokens you're spending twice.

**`cache_control` on the system block** means "cache everything up to here," so the next call within the cache lifetime reads from cache instead of re-billing. Same lever as Segment 2's tool caching, moved to the **system prompt**.

Two extractions, back-to-back, against a 2KB vendor policy. Watch **`cache_creation_input_tokens`** on call 1, **`cache_read_input_tokens`** on call 2.
"""

_case_facts_code = """\
# Realistic vendor-policy block. Production extractors carry several kilobytes
# of policy: numbering rules, locale conventions, edge-case overrides,
# disambiguation tables. We model that here so the cacheable prefix clears
# Sonnet 4.x's 1024-token floor with margin and the cache demonstrably engages.
VENDOR_POLICY = (
    "VENDOR POLICY (apply to every invoice extraction, in order)\\n\\n"
    "1. Decimal separators. European vendors (Eurozone, UK, Scandinavia, "
    "Eastern Europe) use comma as the decimal separator and period as the "
    "thousands separator: '1.515,00 EUR' is 1515.00 EUR. North American and "
    "most APAC vendors invert: '1,515.00 USD' is 1515.00 USD. When the locale "
    "is ambiguous, prefer the convention that produces a plausible total given "
    "the line items: a $51,500 toner cartridge is almost certainly 51.50.\\n"
    "2. Date formats. DD/MM/YYYY for EU vendors, MM/DD/YYYY for US vendors, "
    "YYYY-MM-DD for ISO-disciplined vendors (most enterprise SaaS). When the "
    "month component is 13+ you know it is DD/MM. When the date is unambiguous "
    "(e.g., 2026-05-20 vs 20/05/2026 vs 05/20/2026), always emit the ISO 8601 "
    "form in your output regardless of the source format.\\n"
    "3. PO numbers. Only fill po_number if the invoice prints one explicitly. "
    "Do not infer from the customer's order history, prior invoices, or "
    "email subject lines. A missing PO is a legitimate state for one-off "
    "purchases (consultants, ad-hoc shipping, expense reimbursements).\\n"
    "4. Totals. Always the final 'TOTAL DUE' line, never a subtotal, never a "
    "'GRAND TOTAL' that double-counts tax. If multiple totals appear, prefer "
    "the one explicitly labeled DUE or PAYABLE. If only a subtotal and a tax "
    "line are visible, sum them and lower confidence by 0.10.\\n"
    "5. Tax handling. Sales tax (US), VAT (EU/UK), GST (Canada/Australia), and "
    "HST (some Canadian provinces) are all separate line items in the source "
    "but roll up into the total. Do not surface tax as a distinct field; the "
    "total field is the bottom line the customer pays. The vendor's tax-ID "
    "number (VAT-ID, GSTIN, EIN) goes in metadata.tax_id if visible.\\n"
    "6. Notes field. Include only the literal memo text printed on the "
    "invoice. Do not paraphrase. Do not summarize. If the invoice has no "
    "memo, the notes field stays empty - not null, not 'N/A', not 'no memo'.\\n"
    "7. Currency. Store the numeric amount in the `total` field. Mention the "
    "currency in the `notes` field whenever it is not USD. ISO 4217 codes "
    "only (EUR, GBP, JPY, CAD, MXN, BRL, INR), never symbols, never spelled-"
    "out names. If the invoice mixes currencies (line items in EUR but total "
    "in USD), trust the bottom line and note the conversion in notes.\\n"
    "8. Vendor name normalization. Use the legal entity name as printed, in "
    "upper case if that is how the invoice prints it. Strip company-type "
    "suffixes (GMBH, S.A., LLC, INC) from the searchable name field but "
    "preserve them in the vendor.legal_name field. Strip trailing punctuation.\\n"
    "9. Line-item arrays. Preserve the order from the invoice. Each line item "
    "carries description, quantity, unit_price, and line_total. If any of the "
    "four is missing from the source, set the missing field to null and lower "
    "confidence proportionally. Never invent unit prices by dividing line "
    "totals; quantities can be fractional (consultant hours, freight weight).\\n"
    "10. Confidence scoring. Start at 1.0. Subtract 0.10 for each ambiguity "
    "you resolved against the rules above (decimal-comma resolution, date-"
    "format resolution, total disambiguation, currency conversion). Subtract "
    "0.20 if the source text is OCR output with visible artifacts. Floor at "
    "0.30; if you would go lower, return a structured error instead and let "
    "the retry loop downstream re-prompt with a more specific schema.\\n"
    "11. Edge cases. Credit memos (negative totals) are valid; preserve the "
    "sign. Refund invoices may show a negative due amount; the field name in "
    "the output stays `total` and the value goes negative. Recurring-billing "
    "invoices repeat the same fields each cycle; do not deduplicate across "
    "calls. Drafts and proformas are not yet payable; flag them in notes.\\n"
    "12. Disambiguation table for ambiguous vendor strings (handle in order):\\n"
    "    - 'AMAZON' alone: Amazon Marketplace, currency USD unless suffix \\n"
    "       implies otherwise (AMAZON UK -> GBP, AMAZON DE -> EUR).\\n"
    "    - 'GOOGLE' alone: prefer Google Cloud (workspace + GCP); if line \\n"
    "       items include 'AdWords' or 'Ads', it is Google Ads instead.\\n"
    "    - 'MICROSOFT' alone: prefer Microsoft 365 (subscription pattern); \\n"
    "       Azure invoices print 'Microsoft Azure' explicitly.\\n"
    "    - Bare three-letter acronyms (IBM, SAP, HPE): legal-name field stays \\n"
    "       acronym-form; the metadata.full_name field uses the spelled-out \\n"
    "       form from the invoice header.\\n"
    "13. Locale-specific quirks. German invoices use the Umsatzsteuer-ID \\n"
    "    (USt-IdNr.) for VAT; UK invoices use a 9-digit VAT number; French \\n"
    "    invoices print a SIRET as well as a VAT-ID. Capture whichever \\n"
    "    appears in metadata.tax_id; if multiple appear, prefer VAT-ID.\\n"
    "\\n"
    "DO NOT INVENT VALUES. Optional fields with no source evidence stay null. "
    "Required fields with no source evidence trigger a structured retry, not a "
    "hallucinated guess. Confidence below 0.50 also triggers retry. The audit "
    "log captures every invented value and the cohort gets a weekly report on "
    "extraction quality keyed off that log; do not contribute to it."
)

CACHED_SYSTEM = [
    {
        "type": "text",
        "text": SYSTEM_PROMPT + "\\n\\n" + VENDOR_POLICY,
        "cache_control": {"type": "ephemeral"},
    },
]


def extract_with_cached_facts(raw_text: str) -> tuple[Invoice, dict]:
    resp = client.messages.create(
        model=MODEL, max_tokens=600,
        system=CACHED_SYSTEM,
        tools=[EXTRACT_TOOL],
        tool_choice={"type": "tool", "name": "extract_invoice"},
        messages=[{"role": "user", "content": f"Extract the invoice from this text:\\n\\n{raw_text}"}],
    )
    tool_block = next(b for b in resp.content if b.type == "tool_use")
    usage = resp.usage
    counters = {
        "input_tokens": usage.input_tokens,
        "cache_creation": getattr(usage, "cache_creation_input_tokens", 0) or 0,
        "cache_read": getattr(usage, "cache_read_input_tokens", 0) or 0,
    }
    return Invoice(**tool_block.input), counters


print("Call 1 (writes the cache):")
_, c1 = extract_with_cached_facts(CLEAN_INVOICE)
print(f"  {c1}")
print()
print("Call 2 (should hit the cache):")
_, c2 = extract_with_cached_facts(MISSING_PO_INVOICE)
print(f"  {c2}")
print()
print("cache_read > 0 on call 2 means the 2KB vendor policy was served from cache.")
print("Pattern works on system blocks, tool blocks, and large user-turn prefixes.")
"""

_demo_pruning_md = """\
## Sidebar: tool-output pruning (not executed)

A tool returns 8KB of JSON and you read three fields. The other 7.5KB pays rent in the context window for the rest of the session, so **strip it before appending**.
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

Name the **design fix** for each failure in one sentence. One fix each, no essays.

| # | Failure | Your fix |
|---|---|---|
| a | Agent picked the wrong tool | ? |
| b | Refund of $847 processed against a $500 policy cap | ? |
| c | Synthesis output carries no source attributions | ? |
| d | Agent escalated because the user said "I'm frustrated" | ? |

Answers:

- **(a)** Tighter **tool descriptions**, per-agent scoping, `tool_choice` to force the call.
- **(b)** A **PreToolUse hook**. Policy is code, not a prompt instruction.
- **(c)** **Structured claim-source mappings** from subagents, preserved through synthesis.
- **(d)** Escalate on **policy, complexity, risk, or explicit request** only.
"""

_key_takeaways_md = """\
## Key takeaways

- **Forced tool call + Pydantic schema + retry ceiling** is the canonical structured-output pattern.
- **Few-shot examples** lock corner cases prose can't reach.
- **A `confidence` field** routes the bottom slice to human review. Uncalibrated, still useful.
- **`cache_control` on the system block** pins case facts cheaply. Pruning and compaction are the fallbacks.
- **Escalate on policy, complexity, risk, or explicit request.** Sentiment isn't a signal.

**Further study:**
- `../claude-cookbooks-main/tool_use/extracting_structured_json.ipynb` (few-shot extraction)
- `../claude-cookbooks-main/tool_use/tool_use_with_pydantic.ipynb` (Pydantic-as-schema)
- `../claude-cookbooks-main/tool_use/automatic-context-compaction.ipynb` (compaction fallback)
- [`../docs/domain-5-context.md`](../docs/domain-5-context.md) for provenance and confidence calibration.
"""

_bridge_md = """\
## Bridge to Segment 4

> "You now have the skills. The exam is how you signal them. Last segment is the certification debrief: what's on it, what Anthropic expects, and ten practice questions to calibrate where you stand."

Open `segment-4-cca-f-capstone.ipynb`.
"""

_appendix_md = """\
## Going further

Everything below is optional. Pick the group that matches what you want to get better at.

**Deeper on this segment**

- [`../docs/domain-4-prompts.md`](../docs/domain-4-prompts.md) - the full Domain 4 reference on precise prompts, format control, and few-shot design.
- [`../docs/domain-5-context.md`](../docs/domain-5-context.md) - the Domain 5 reference on context windows, caching, pruning, and compaction.

**Structured output, more ways**

- [`../claude-cookbooks-main/tool_use/extracting_structured_json.ipynb`](../claude-cookbooks-main/tool_use/extracting_structured_json.ipynb) - Anthropic's own take on the forced-tool-call extraction pattern.
- [`../claude-cookbooks-main/tool_use/tool_use_with_pydantic.ipynb`](../claude-cookbooks-main/tool_use/tool_use_with_pydantic.ipynb) - Pydantic as the schema authority, which is exactly what we did here.
- [`../examples/messages_api/005_controlling_output.ipynb`](../examples/messages_api/005_controlling_output.ipynb) - output-shape control at the raw Messages API level, without tools in the way.
- [`../examples/messages_api/002_system_prompt.ipynb`](../examples/messages_api/002_system_prompt.ipynb) - the system prompt treated as a control surface rather than a greeting.

**Context management**

- [`./segment-2-5-control-surfaces.ipynb`](./segment-2-5-control-surfaces.ipynb) - the self-study deep dive, including the Claude Console `memory_stores` and `vaults` assets that carry the Domain 5 persistence story.
- [`../claude-cookbooks-main/misc/prompt_caching.ipynb`](../claude-cookbooks-main/misc/prompt_caching.ipynb) - caching beyond the single system block we cached above.
- [`../claude-cookbooks-main/tool_use/automatic-context-compaction.ipynb`](../claude-cookbooks-main/tool_use/automatic-context-compaction.ipynb) - the compaction fallback. It doesn't currently run because of an upstream SDK drift bug, so read it for the pattern rather than executing it.

**The managed-agents counterpart**

- [`../examples/agents_api/04_structured_output_and_validation.ipynb`](../examples/agents_api/04_structured_output_and_validation.ipynb) - the same structured-output problem, solved inside a managed agent.
- [`../examples/agents_api/05_context_and_escalation.ipynb`](../examples/agents_api/05_context_and_escalation.ipynb) - context management and escalation triage on the managed-agents surface.

**Where to go next**

- [`../docs/EXAM-STUDY-PATH.md`](../docs/EXAM-STUDY-PATH.md) - the domain-by-domain study map.
- [`../docs/COOKBOOK-INDEX.md`](../docs/COOKBOOK-INDEX.md) - which cookbook backs which course topic.
"""
