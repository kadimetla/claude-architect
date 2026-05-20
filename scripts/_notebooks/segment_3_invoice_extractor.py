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
- Pin **few-shot examples** to lock in corner-case behavior that prose alone cannot describe
- Attach a **per-row confidence score** and route low-confidence rows to a human review queue
- Preserve **case facts** via `cache_control` on the system block, and prune **verbose tool outputs** so long conversations stay coherent
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
# Principled exception to the course's Haiku-default policy. Nested invoice
# schemas with line-item arrays + retry-on-validation-error is the one demo
# where Sonnet 4.6's reasoning depth measurably lifts extraction accuracy.
# Everywhere else in the course: Haiku 4.5.
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

_demo_few_shot_md = """\
## Few-shot: pinning corner cases (Domain 4)

Prose instructions describe behavior. **Examples lock it.** When the corner case is one the model gets wrong without examples - subtle numeric formatting, regional date formats, optional fields the model wants to invent - two or three worked examples in the user turn move the needle more than any temperature change.

The shape: include a small `system` block plus a chat of past `user` / `assistant` turns where the assistant called the tool *correctly*. The model imitates.

Cookbook anchor: `../claude-cookbooks-main/tool_use/extracting_structured_json.ipynb` (Anthropic's structured-extraction reference).

Below we extract a tricky invoice with European-format dates (`15/05/2026` is day-month-year, not month-day-year). Without examples the model often returns `2026-05-15`. With examples it returns `2026-05-15` only when the source confirms it - and `2026-05-15` is correct here only by coincidence; the real lesson is that the assistant turn we hand-craft shows the model how to disambiguate.
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

For high-stakes extractions, you do not just want the values - you want a **self-reported confidence** so you can route the bottom 5% to a review queue.

The trick: add a `confidence: float` field (0.0 to 1.0) to the Pydantic model. The forced tool call forces the model to commit to a number. Then your downstream code reads the score and routes.

This is **cheap and load-bearing**. It is not calibrated (the model is biased toward overconfidence), but it is *useful*: the lowest-confidence rows really are the ones most worth a second look.
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

A long extraction session re-reads the same policy text on every call: vendor rules, currency rules, the company's "do not invent values" prompt. That is wasted tokens.

`cache_control` on the system block tells Anthropic: cache everything up to this point. The next call within the cache lifetime reads from cache instead of re-billing. Same idea as Segment 2's tool caching, applied to the **system prompt** rather than the tool list.

Cookbook anchor: `../claude-cookbooks-main/tool_use/automatic-context-compaction.ipynb` (the complementary fallback when caching alone is not enough).

We define a 2KB "vendor policy" block, attach `cache_control`, and run two extractions back-to-back. Watch `cache_creation_input_tokens` on call 1 and `cache_read_input_tokens` on call 2.
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
- **(c)** Require **structured claim-source mappings** from subagents; coordinator preserves them through synthesis. This is the Segment 1 coordinator-subagent pattern applied here: the synthesis subagent emits structured findings, the coordinator preserves provenance across the handoff.
- **(d)** Escalate on **policy, complexity, risk, or explicit request**. Sentiment is not a signal.
"""

_key_takeaways_md = """\
## Key takeaways

- **Forced tool calls + Pydantic schemas + max-retry ceiling** are the canonical structured-output pattern.
- **Few-shot examples** in the message history lock corner-case behavior that prose alone cannot reach.
- **Self-reported `confidence` field** routes the bottom slice to a human review queue. Not calibrated, still useful.
- **`cache_control` on the system block** pins case facts cheaply; subsequent calls hit cache. Pruning + compaction are the fallbacks.
- **Escalation triggers on policy, complexity, risk, or explicit request**. Sentiment is not a signal.

**Cookbook anchors for further study:**
- `../claude-cookbooks-main/tool_use/extracting_structured_json.ipynb` (few-shot + structured extraction)
- `../claude-cookbooks-main/tool_use/tool_use_with_pydantic.ipynb` (Pydantic-as-schema reference)
- `../claude-cookbooks-main/tool_use/automatic-context-compaction.ipynb` (compaction as a fallback)
- [`../domain-5-context.md`](../domain-5-context.md) for error propagation, provenance, and confidence calibration depth.
"""

_bridge_md = """\
## Bridge to Segment 4

> "You now have the skills. The exam is how you signal them. Last segment is the certification debrief: what's on it, what Anthropic expects, and ten practice questions to calibrate where you stand."

Open `segment-4-cca-f-capstone.ipynb`.
"""
