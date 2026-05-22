/**
 * Builds the Phase 2 answer payload (result + per-option rationale).
 *
 * Shared by the /api/answers route and the MCP server's score_answer tool so
 * both surfaces explain an answer identically.
 *
 * Seed questions carry one combined `explanation`; generated questions may
 * carry richer per-option rationale in future. This helper produces a
 * per-letter map either way: the correct option gets the full explanation,
 * each distractor gets a short "why this misses" line.
 */
import type { AnswerResult, Question } from "../shared/types.js";
import { getDomain } from "../shared/domains.js";

/** Computes the AnswerResult for a chosen letter against a bank question. */
export function buildAnswerResult(question: Question, chosen: string): AnswerResult {
  const correct = chosen === question.correct;

  const perOption: Record<string, string> = {};
  for (const opt of question.options) {
    if (opt.letter === question.correct) {
      perOption[opt.letter] = `Correct. ${question.explanation}`;
    } else {
      perOption[opt.letter] =
        `Not the best choice. This option does not satisfy the scenario as fully as ` +
        `option ${question.correct}. Compare it against the explanation for the correct answer.`;
    }
  }

  return {
    correct,
    correctLetter: question.correct,
    explanation: question.explanation,
    perOption,
    domainRef: getDomain(question.domain).refPath,
  };
}
