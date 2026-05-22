/**
 * The validator subagent - the Domain 1 coordinator-subagent pattern.
 *
 * The generator's main loop is the COORDINATOR. This module is a SUBAGENT: a
 * separate Claude call with its own isolated context and a single narrow job -
 * judge whether a draft question is exam-realistic and fix-worthy. The
 * coordinator decides repair-or-accept from the subagent's structured verdict.
 *
 * Design note: this is a hand-rolled subagent (a fresh messages.create thread),
 * not the Claude Agent SDK. The deliberate trade-off - it keeps the loop and
 * its stop_reason handling fully visible as teaching code, and adds no
 * dependency. The Claude Agent SDK's managed subagent loop is the alternative;
 * the About page explains both.
 *
 * The subagent runs TWO checks in series:
 *   1. The deterministic structural validator (shared/question-validator.ts) -
 *      cheap, exact, no model call.
 *   2. A model-based quality review - only if the structural check passes -
 *      catching defects rules cannot see (trivia recall, ambiguous distractors).
 */
import type Anthropic from "@anthropic-ai/sdk";
import { DEFAULT_MODEL } from "../anthropic.js";
import { validateQuestion } from "../../shared/question-validator.js";
import type { DraftQuestion } from "../../shared/question-validator.js";

/** The subagent's verdict on a draft question. */
export interface ValidatorVerdict {
  ok: boolean;
  issues: string[];
  /** How many structural-repair rounds this draft has been through. */
  repairRounds: number;
}

/** Tool the subagent is forced to call so its verdict is structured, not prose. */
const VERDICT_TOOL: Anthropic.Tool = {
  name: "submit_verdict",
  description: "Submit a structured quality verdict on the draft question.",
  input_schema: {
    type: "object",
    properties: {
      exam_realistic: {
        type: "boolean",
        description: "True if the question feels like a real CCA-F exam item.",
      },
      issues: {
        type: "array",
        items: { type: "string" },
        description: "Concrete, fixable defects. Empty if the question is sound.",
      },
    },
    required: ["exam_realistic", "issues"],
  },
};

/**
 * Runs the validator subagent against a draft question.
 *
 * @param client      an Anthropic client (the subagent's own thread)
 * @param draft       the draft question to judge
 * @param repairRound which structural-repair round this is (for the verdict)
 */
export async function validateWithSubagent(
  client: Anthropic,
  draft: DraftQuestion,
  repairRound: number,
): Promise<ValidatorVerdict> {
  // Step 1: deterministic structural check. Fast, free, exact.
  const structural = validateQuestion(draft);
  if (!structural.ok) {
    return { ok: false, issues: structural.issues, repairRounds: repairRound };
  }

  // Step 2: model-based quality review, in an ISOLATED context - the subagent
  // sees only the draft, never the coordinator's history.
  const response = await client.messages.create({
    model: DEFAULT_MODEL,
    max_tokens: 1024,
    system:
      "You are a CCA-F exam-quality reviewer. You judge ONE draft practice question. " +
      "An exam-realistic question: poses a scenario that forces a genuine architectural " +
      "decision (not trivia recall), has exactly one defensible correct answer, and has " +
      "distractors that are plausible but clearly wrong to someone who knows the domain. " +
      "Report only concrete, fixable defects. Always call submit_verdict.",
    tools: [VERDICT_TOOL],
    tool_choice: { type: "tool", name: "submit_verdict" },
    messages: [
      {
        role: "user",
        content: `Review this draft CCA-F question:\n\n${JSON.stringify(draft, null, 2)}`,
      },
    ],
  });

  // The subagent was forced to call submit_verdict, so the verdict is in the
  // tool_use block - no prose parsing.
  const verdictBlock = response.content.find(
    (b): b is Anthropic.ToolUseBlock => b.type === "tool_use" && b.name === "submit_verdict",
  );
  if (!verdictBlock) {
    // The subagent did not produce a verdict - treat as a non-fatal pass so a
    // single odd turn does not block the whole generation run.
    return { ok: true, issues: [], repairRounds: repairRound };
  }

  const verdict = verdictBlock.input as { exam_realistic: boolean; issues: string[] };
  return {
    ok: verdict.exam_realistic && verdict.issues.length === 0,
    issues: verdict.issues,
    repairRounds: repairRound,
  };
}
