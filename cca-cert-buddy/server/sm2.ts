/**
 * SM-2 spaced-repetition scheduling.
 *
 * Classic SuperMemo-2, with the review unit being a CCA-F domain rather than
 * an individual flashcard. After each answer the domain's interval and ease
 * factor are updated; the dashboard's review queue surfaces domains whose
 * due date has arrived.
 *
 * Pure functions only - no database coupling - so the algorithm is trivially
 * unit-testable. The routes layer reads/writes the domains_sm2 table around it.
 */

/** Mutable scheduling state for one domain. */
export interface Sm2State {
  interval: number;
  easeFactor: number;
  repetitions: number;
}

/**
 * Quality of recall, 0-5 (SM-2 convention):
 *   5 = correct and fast    4 = correct    2 = wrong
 * The routes layer maps a graded answer onto this scale.
 */
export type Quality = 0 | 1 | 2 | 3 | 4 | 5;

const MIN_EASE = 1.3;

/**
 * Applies one review. Returns a new state - never mutates the input.
 *
 * Correct (quality >= 3): repetitions advance, the interval grows by the ease
 * factor, and the ease factor is nudged by the standard SM-2 formula.
 * Wrong (quality < 3): repetitions reset and the interval drops to 1 day, so
 * a missed domain resurfaces tomorrow.
 */
export function review(prev: Sm2State, quality: Quality): Sm2State {
  if (quality < 3) {
    return {
      repetitions: 0,
      interval: 1,
      easeFactor: Math.max(MIN_EASE, prev.easeFactor - 0.2),
    };
  }

  const repetitions = prev.repetitions + 1;

  let interval: number;
  if (repetitions === 1) {
    interval = 1;
  } else if (repetitions === 2) {
    interval = 6;
  } else {
    interval = Math.round(prev.interval * prev.easeFactor);
  }

  // SM-2 ease-factor update. Higher quality nudges ease up; lower nudges down.
  const easeFactor = Math.max(
    MIN_EASE,
    prev.easeFactor + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02)),
  );

  return { interval, easeFactor, repetitions };
}

/**
 * Maps a graded answer to an SM-2 quality score. A correct answer under the
 * fast threshold scores top marks; a correct-but-slow answer is still good;
 * a wrong answer scores below the passing line.
 */
export function qualityFromAnswer(correct: boolean, msElapsed: number | null): Quality {
  if (!correct) return 2;
  const FAST_MS = 20_000;
  if (msElapsed !== null && msElapsed <= FAST_MS) return 5;
  return 4;
}

/** ISO date (YYYY-MM-DD) `interval` days after `from`. */
export function dueDateFrom(from: Date, interval: number): string {
  const d = new Date(from);
  d.setDate(d.getDate() + Math.round(interval));
  return d.toISOString().slice(0, 10);
}
