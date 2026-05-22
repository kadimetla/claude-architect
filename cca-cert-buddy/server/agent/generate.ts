/**
 * Question generation - the agent core, where the whole enchilada meets.
 *
 * Generating one CCA-F question exercises every CCA-F domain at once:
 *   D1  the agentic loop drives generate -> validate -> repair
 *   D2  the loop's tools are discovered live from the cca-study-mcp server
 *   D4  emit_question is forced via tool_choice, so output is schema-shaped
 *   D1  the validator SUBAGENT judges the draft in an isolated context
 *   D5  the model sees only the relevant domain reference - focused context
 *
 * Shared by POST /api/generate (one question, no persist) and the build-time
 * scripts/generate-questions.ts (batch, persist to the bank).
 */
import type Anthropic from "@anthropic-ai/sdk";
import { readFileSync, writeFileSync } from "node:fs";
import type { DomainId, GenerateResult, Question } from "../../shared/types.js";
import { getDomain } from "../../shared/domains.js";
import { BANK_PATH } from "../../shared/paths.js";
import { getAnthropic, AUTHORING_MODEL, estimateCost } from "../anthropic.js";
import { allQuestions, nextGlobalN, loadBank } from "../bank.js";
import { runAgentLoop } from "./loop.js";
import { validateWithSubagent } from "./subagent-validator.js";
import type { DraftQuestion } from "../../shared/question-validator.js";

/** Max generate-fix rounds before the coordinator gives up on a draft. */
const MAX_REPAIR_ROUNDS = 3;

/**
 * The system prompt for the authoring loop. It states explicit success
 * criteria and what NOT to do - the Domain 4 "precise prompt" pattern.
 */
function authoringSystemPrompt(domain: DomainId, domainRef: string): string {
  const meta = getDomain(domain);
  return [
    `You are an expert CCA-F (Claude Certified Architect - Foundations) exam-item author.`,
    `Write ONE original, exam-realistic multiple-choice question for domain ${domain}: ${meta.name}.`,
    ``,
    `Success criteria:`,
    `- The scenario forces a genuine architectural decision, not trivia recall.`,
    `- Exactly four options, letters A-D, with exactly one defensible correct answer.`,
    `- Distractors are plausible but clearly wrong to someone who knows the domain.`,
    `- The explanation says why the correct answer wins.`,
    `- No em dashes (use " - "), no AWS mentions, no "ask" used as a noun.`,
    ``,
    `Process:`,
    `1. Call emit_question with your draft (you are required to call it first).`,
    `2. If you receive validation issues, call emit_question again with a corrected draft.`,
    ``,
    `Ground the question in these domain reference notes:`,
    ``,
    domainRef,
  ].join("\n");
}

/** The forced-output tool. Its input_schema IS the question schema. */
const EMIT_QUESTION_TOOL = {
  name: "emit_question",
  description: "Emit one CCA-F practice question matching the required schema.",
  input_schema: {
    type: "object" as const,
    properties: {
      scenario: { type: "string", description: "Short scenario title." },
      situation: { type: "string", description: "The scenario context, 2-5 sentences." },
      question: { type: "string", description: "The question stem." },
      options: {
        type: "array",
        minItems: 4,
        maxItems: 4,
        items: {
          type: "object",
          properties: {
            letter: { type: "string", enum: ["A", "B", "C", "D"] },
            text: { type: "string" },
            correct: { type: "boolean" },
          },
          required: ["letter", "text", "correct"],
        },
      },
      correct: { type: "string", enum: ["A", "B", "C", "D"] },
      explanation: { type: "string", description: "Why the correct answer wins." },
      secondaryDomains: {
        type: "array",
        items: { type: "string", enum: ["D1", "D2", "D3", "D4", "D5"] },
      },
    },
    required: ["scenario", "situation", "question", "options", "correct", "explanation"],
  },
};

/**
 * Generates one question for a domain by running the agent core.
 *
 * @param domain  the CCA-F domain to author for
 * @param opts.persist  if true, append the question to data/question-bank.json
 */
export async function generateQuestion(
  domain: DomainId,
  opts: { persist: boolean },
): Promise<GenerateResult> {
  const client = getAnthropic();
  const domainRef = await loadDomainRefViaMcp(domain);

  // The agentic loop authors the draft. emit_question is a local output-
  // shaping tool offered alongside the MCP tools; it is forced on turn 1
  // (Domain 4 structured output), and the MCP-discovered tools are available
  // on later turns so the model can ground itself further.
  const loop = await runAgentLoop({
    client,
    model: AUTHORING_MODEL,
    system: authoringSystemPrompt(domain, domainRef),
    userMessage: `Author one CCA-F question for domain ${domain}. Call emit_question with your draft.`,
    forceToolFirst: "emit_question",
    extraTools: [EMIT_QUESTION_TOOL],
    maxIterations: 4,
    maxTokens: 2048,
  });

  // Pull the most recent emit_question draft out of the loop's captured inputs.
  const drafts = (loop.toolInputs["emit_question"] ?? []) as DraftQuestion[];
  if (drafts.length === 0) {
    throw new Error("The authoring loop produced no emit_question draft.");
  }
  let draft = withDomain(drafts[drafts.length - 1]!, domain);

  // The coordinator-subagent repair loop: the validator subagent judges the
  // draft; on failure the coordinator asks the author to fix the named issues.
  let verdict = await validateWithSubagent(client, draft, 0);
  let inputTokens = loop.usage.inputTokens;
  let outputTokens = loop.usage.outputTokens;

  for (let round = 1; !verdict.ok && round <= MAX_REPAIR_ROUNDS; round++) {
    const repair = await client.messages.create({
      model: AUTHORING_MODEL,
      max_tokens: 2048,
      system: authoringSystemPrompt(domain, domainRef),
      tools: [EMIT_QUESTION_TOOL],
      tool_choice: { type: "tool", name: "emit_question" },
      messages: [
        {
          role: "user",
          content:
            `This draft failed review. Fix every issue and call emit_question again.\n\n` +
            `Draft:\n${JSON.stringify(draft, null, 2)}\n\n` +
            `Issues:\n- ${verdict.issues.join("\n- ")}`,
        },
      ],
    });
    inputTokens += repair.usage.input_tokens;
    outputTokens += repair.usage.output_tokens;

    const fixed = repair.content.find(
      (b): b is Anthropic.ToolUseBlock => b.type === "tool_use" && b.name === "emit_question",
    );
    if (!fixed) break;
    draft = withDomain(fixed.input as DraftQuestion, domain);
    verdict = await validateWithSubagent(client, draft, round);

    loop.trace.push({
      iteration: loop.trace.length + 1,
      stopReason: repair.stop_reason ?? "unknown",
      action: `Repair round ${round}: re-authored the draft to fix ${verdict.issues.length === 0 ? "all" : "remaining"} issues.`,
      toolCalls: [{ name: "emit_question", ok: true, summary: "draft re-emitted" }],
    });
  }

  const question = toBankQuestion(draft, domain);
  if (opts.persist && verdict.ok) {
    appendToBank(question);
  }

  return {
    question,
    trace: loop.trace,
    validatorVerdict: verdict,
    usage: {
      inputTokens,
      outputTokens,
      estimatedCostUsd: estimateCost(AUTHORING_MODEL, inputTokens, outputTokens),
    },
  };
}

/** Reads a domain reference through the MCP server's lookup_domain_ref tool. */
async function loadDomainRefViaMcp(domain: DomainId): Promise<string> {
  // Imported lazily so the offline routes never pull in the MCP client.
  const { callMcpTool } = await import("./mcp-client.js");
  const { text } = await callMcpTool("lookup_domain_ref", { domain });
  return text;
}

/** Forces the domain field so a draft always carries the right domain id. */
function withDomain(draft: DraftQuestion, domain: DomainId): DraftQuestion {
  return { ...draft, domain };
}

/** Converts a validated draft into a full bank Question. */
function toBankQuestion(draft: DraftQuestion, domain: DomainId): Question {
  return {
    global_n: nextGlobalN(),
    scenario: String(draft.scenario),
    situation: String(draft.situation),
    question: String(draft.question),
    options: (draft.options as Question["options"]) ?? [],
    correct: draft.correct as Question["correct"],
    explanation: String(draft.explanation),
    domain,
    secondaryDomains: (draft.secondaryDomains as DomainId[]) ?? [],
    source: "generated",
  };
}

/** Appends one question to data/question-bank.json and reloads the in-memory bank. */
function appendToBank(question: Question): void {
  const current = JSON.parse(readFileSync(BANK_PATH, "utf8")) as Question[];
  current.push(question);
  writeFileSync(BANK_PATH, JSON.stringify(current, null, 2) + "\n", "utf8");
  loadBank();
}

/** The set of existing situations - used by the bank validator's dup guard. */
export function existingSituations(): string[] {
  return allQuestions().map((q) => q.situation);
}
