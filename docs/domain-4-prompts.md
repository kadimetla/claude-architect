# Domain 4: Prompt Engineering & Structured Output

> Reference scaffold - maps to **COURSE-FLOW.md Segment 3**

## What this domain covers

Domain 4 is about getting **predictable, machine-parseable output** from a probabilistic model. The skills:

- Writing **precise prompts** with explicit success criteria, edge-case handling, and "what NOT to do" instructions.
- Using **few-shot examples** to lock in formats that prose alone cannot enforce.
- Forcing **JSON schema conformance** via tool use and `tool_choice`.
- Building **validation and retry loops** that know when to retry and when to fail fast.
- Choosing between **real-time and batch** processing for cost-sensitive workloads.
- Stacking **multi-instance review** for high-stakes extractions where a single pass is not trustworthy.

## Core concepts

### Precise prompts: explicit criteria + format

Vague prompts produce inconsistent outputs. A precise prompt tells the model four things: what the output should look like, what to do when data is missing, what edge cases exist, and what NOT to do. Two failure modes dominate real-world extraction:

- **Plausible hallucinations.** When a field is nullable and the source text does not contain the value, the model invents something that "looks right." Fix: explicit instruction `Return null if the value is not directly stated in the source.`
- **Inconsistent formats.** "cotton blend" in one row, "Cotton/Polyester mix" in the next. Temperature 0 alone will not save you. Fix: 2-3 **few-shot examples** that demonstrate the canonical format.

Example prompt fragment with both fixes applied:

```text
Extract the material composition for each line item.

Rules:
- Return null if the material is not directly stated in the source text. Do not infer.
- Use the standardized format from the examples below. Do not paraphrase.
- If multiple materials are listed, join them with " / " in declared order.

Examples:
Input: "100% cotton, pre-shrunk"
Output: "Cotton"

Input: "cotton blend with poly"
Output: "Cotton / Polyester"

Input: "fabric, soft hand feel"
Output: null
```

### Few-shot prompting

Two or three carefully chosen input-output pairs beat any amount of prose explaining the format. Examples teach by demonstration, which is how the model was trained. Place them in the **system prompt** when the format is stable across requests (cache them with `cache_control` for cost savings), or in the **user turn** when examples need to vary per request.

Materials standardization, three examples:

```text
Input: "100% organic cotton" -> Output: "Cotton"
Input: "65/35 poly-cotton blend" -> Output: "Polyester / Cotton"
Input: "genuine leather upper, rubber sole" -> Output: "Leather / Rubber"
```

That is more reliable than a 200-word style guide.

### JSON schema enforcement via tool use

This is **the** structured-output pattern. The flow:

1. Define a **Pydantic** model with the fields you want.
2. Convert it to JSON Schema via `Model.model_json_schema()`. Pydantic emits a schema the Anthropic API accepts directly.
3. Register that schema as a tool's `input_schema`.
4. Set `tool_choice: {"type": "tool", "name": "<your_schema_tool>"}` to **force** the model to call exactly that tool.
5. The model's `tool_use` block's `input` field is now guaranteed to match your schema.

Optionally set `strict: true` on the tool definition for guaranteed schema validation on tool names and inputs.

```python
from anthropic import Anthropic
from pydantic import BaseModel, Field
from typing import Literal

class LineItem(BaseModel):
    description: str
    quantity: int = Field(ge=1)
    unit_price: float = Field(ge=0)

class Invoice(BaseModel):
    invoice_id: str
    line_items: list[LineItem]
    total: float
    confidence: Literal["high", "medium", "low"]

client = Anthropic()
response = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=2048,
    tools=[{
        "name": "extract_invoice",
        "description": "Extract structured invoice data from the provided text.",
        "input_schema": Invoice.model_json_schema(),
    }],
    tool_choice={"type": "tool", "name": "extract_invoice"},
    messages=[{"role": "user", "content": invoice_text}],
)

tool_block = next(b for b in response.content if b.type == "tool_use")
invoice = Invoice.model_validate(tool_block.input)  # Pydantic validates on parse
```

Reference: `../claude-cookbooks-main/tool_use/tool_use_with_pydantic.ipynb`.

### Validation, retry, and feedback loops

`Model.model_validate()` raises on schema violation. When it does, you have two distinct failure classes and they need different treatment:

- **Format / schema errors.** The model returned the wrong type, missed a required field, or violated a constraint. Append the validation error back to the conversation as a user turn: `Your previous output failed validation with: <error>. Please retry, conforming to the schema.` Retries succeed within 2-3 attempts the vast majority of the time.
- **Missing-information errors.** The model returned null or low confidence because the source genuinely does not contain the data (e.g., a citation that reads "et al." pointing to an external document). Retries do **not** help here. The information is not in the input.

Anti-pattern: an infinite retry loop on a missing-info failure. Cap retries at 2-3, then escalate to human review. Spending tokens on hopeless retries is a budget leak.

### Confidence calibration + human review queues

Have the model emit field-level confidence scores as part of the schema, for example `confidence: Literal["high", "medium", "low"]`. Route downstream based on confidence:

- **High** -> automated downstream consumption.
- **Medium** -> sampled spot-check.
- **Low** -> human review queue.

Critical caveat: validate accuracy **by document type and by field**. Aggregate high-confidence accuracy can mask catastrophically low accuracy on specific document classes or specific fields. Spot-check before you trust the model's self-reported confidence in production.

### Batch processing (Message Batches API)

For non-real-time extractions, the **Message Batches API** delivers roughly **50% cost savings** versus real-time inference. Use cases: nightly invoice processing, weekly report extraction, document backfills, retrospective analytics. SLA tradeoff: batches process within 24 hours.

Default rule: **batch for asynchronous workflows, real-time only when the SLA truly demands it.** Most "real-time" extraction pipelines are actually nightly jobs in disguise.

### Multi-instance review architectures

For high-stakes extractions (medical, legal, financial), run the same prompt through **2-3 independent model passes**, then add a fourth "judge" pass that synthesizes the outputs and flags disagreements:

- **Agreement across passes** -> high confidence, route to automation.
- **Disagreement** -> route to human review.

Cost is roughly **3x baseline** but catches systematic biases that a single pass cannot detect. Reference: `../claude-cookbooks-main/patterns/agents/evaluator_optimizer.ipynb`.

## Demo anchor

See **COURSE-FLOW.md Segment 3** for the live build (invoice extractor), taught from [`segment-3-invoice-extractor.ipynb`](../notebooks/segment-3-invoice-extractor.ipynb). Segment 3 now also covers Domain 5 (context preservation, escalation triage), so the demo is tightened to a single notebook on screen. Code references:

- `../claude-cookbooks-main/tool_use/extracting_structured_json.ipynb` - primary structured-output pattern, opened live
- `../claude-cookbooks-main/tool_use/tool_use_with_pydantic.ipynb` - Pydantic + tool_use integration, referenced inline (not opened live)
- `../claude-cookbooks-main/patterns/agents/evaluator_optimizer.ipynb` - multi-pass review pattern, self-study
- `../claude-cookbooks-main/tool_use/parallel_tools.ipynb` - parallel extraction, self-study. Read it for the pattern; it currently **fails to run** on an upstream bug (see [`COOKBOOK-INDEX.md`](./COOKBOOK-INDEX.md)).

### The control surfaces underneath

Before forced tool use, there are plainer levers, and [`examples/messages_api/`](../examples/messages_api/) walks them one per notebook: [`002_system_prompt.ipynb`](../examples/messages_api/002_system_prompt.ipynb) treats the **system prompt as a control surface** rather than decoration, [`003_temperature.ipynb`](../examples/messages_api/003_temperature.ipynb) shows what the temperature dial does and doesn't buy you, and [`005_controlling_output.ipynb`](../examples/messages_api/005_controlling_output.ipynb) is output control in its simplest form. Each has an `_exercise` variant. Work these first if the Pydantic-plus-forced-tool pattern below feels like it arrived from nowhere.

For the managed-agent version, [`examples/agents_api/04_structured_output_and_validation.ipynb`](../examples/agents_api/04_structured_output_and_validation.ipynb) pulls JSON out of an agent turn and runs the same validate-then-retry-once discipline, including the null-if-not-stated rule.

### Task-statement coverage

[`notebooks/cca-f-exam-mastery.ipynb`](../notebooks/cca-f-exam-mastery.ipynb) **Part 4** covers all six Domain 4 task statements (TS4.1 through TS4.6): explicit criteria over vague instructions, few-shot for ambiguous cases, tool-use JSON schema enforcement, forced extraction with bounded retry, the Message Batches API, and multi-pass review.

## Production tips (Tim's voice)

- **Pydantic is the cheat code.** Define your schema once, reuse it for validation, serialization, and the tool definition. The model will conform.
- **Few-shot beats temperature.** If your outputs are inconsistent, add 2-3 examples before you touch the temperature dial.
- **"Return null" must be in the prompt.** Otherwise the model invents plausible values. Single highest-ROI instruction for nullable fields.
- **Retries help formatting; retries don't help knowledge gaps.** Cap them. Three strikes and escalate to a human.
- **Batch API for anything not real-time.** 50% off. Do not pay real-time prices for asynchronous work.
- **Confidence scores are routing keys, not vibes.** Use them to gate human review, and spot-check the calibration by document type before trusting it.

## Further reading

- Anthropic: Prompt engineering overview - https://docs.claude.com/en/docs/build-with-claude/prompt-engineering/overview
- Anthropic: Tool use for structured output - https://docs.claude.com/en/docs/agents-and-tools/tool-use
- Anthropic: Message Batches API - https://docs.claude.com/en/docs/build-with-claude/batch-processing
- `../claude-cookbooks-main/tool_use/` - full tool-use cookbook
- `../claude-cookbooks-main/patterns/agents/` - agent design patterns
