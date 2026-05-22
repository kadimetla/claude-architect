/**
 * Exam scoring.
 *
 * The real CCA-F exam reports a scaled score from 100 to 1000 with a passing
 * line at 720. We mirror that with a PIECEWISE-linear map calibrated so the
 * 72%-correct mark anchors exactly to 720 - the published "around 700-720"
 * guidance. Below 72%, raw-correct maps 0% -> 100 and 72% -> 720; above 72% it
 * maps 72% -> 720 and 100% -> 1000. This is a teaching approximation;
 * Anthropic's true scaling curve is not published.
 */
import type { DomainId, DomainProgress, Question } from "../shared/types.js";
import { DOMAINS, getDomain } from "../shared/domains.js";

export const PASSING_SCALED_SCORE = 720;
const MIN_SCALED = 100;
const MAX_SCALED = 1000;
/** The raw-correct fraction the passing scaled score anchors to. */
const PASS_FRACTION = 0.72;

/**
 * Maps a raw-correct count onto the 100-1000 scaled range with a piecewise
 * curve. The kink at 72% guarantees that a learner who answers 72% correctly
 * scores exactly the 720 passing line - so the prose and the math agree.
 */
export function toScaledScore(rawCorrect: number, total: number): number {
  if (total <= 0) return MIN_SCALED;
  const fraction = Math.max(0, Math.min(1, rawCorrect / total));

  if (fraction <= PASS_FRACTION) {
    // Lower segment: 0% -> 100, 72% -> 720.
    const t = fraction / PASS_FRACTION;
    return Math.round(MIN_SCALED + t * (PASSING_SCALED_SCORE - MIN_SCALED));
  }
  // Upper segment: 72% -> 720, 100% -> 1000.
  const t = (fraction - PASS_FRACTION) / (1 - PASS_FRACTION);
  return Math.round(PASSING_SCALED_SCORE + t * (MAX_SCALED - PASSING_SCALED_SCORE));
}

/** True if a scaled score meets the passing line. */
export function isPassing(scaledScore: number): boolean {
  return scaledScore >= PASSING_SCALED_SCORE;
}

/**
 * Grades a set of exam answers against the question bank and produces both the
 * raw count and a per-domain breakdown. `answers` maps question global_n to
 * the chosen letter; unanswered questions count as incorrect.
 */
export function gradeExam(
  questions: Question[],
  answers: Map<number, string>,
): { rawCorrect: number; perDomain: DomainProgress[] } {
  const perDomain = new Map<DomainId, { answered: number; correct: number }>();
  for (const d of DOMAINS) perDomain.set(d.id, { answered: 0, correct: 0 });

  let rawCorrect = 0;
  for (const q of questions) {
    const chosen = answers.get(q.global_n);
    const correct = chosen === q.correct;
    if (correct) rawCorrect += 1;

    const bucket = perDomain.get(q.domain)!;
    bucket.answered += 1;
    if (correct) bucket.correct += 1;
  }

  const breakdown: DomainProgress[] = DOMAINS.map((d) => {
    const b = perDomain.get(d.id)!;
    return {
      domain: d.id,
      name: getDomain(d.id).name,
      answered: b.answered,
      correct: b.correct,
      accuracy: b.answered === 0 ? 0 : b.correct / b.answered,
    };
  });

  return { rawCorrect, perDomain: breakdown };
}
