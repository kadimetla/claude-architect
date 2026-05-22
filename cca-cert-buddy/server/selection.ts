/**
 * Question selection.
 *
 * Quiz mode picks one question at a time, weighted toward the domains a
 * learner most needs: SM-2-overdue domains first, then weak domains (low
 * accuracy), then the CCA-F exam-weight distribution as the baseline. This
 * is the adaptive logic the cert-buddy PRD called out as the gap in static
 * question banks.
 *
 * Exam mode picks a fixed 60-question set in the exam-weight split.
 */
import type { DomainId, Question } from "../shared/types.js";
import { DOMAIN_IDS, DOMAINS, examDomainSplit } from "../shared/domains.js";
import { questionsForDomain } from "./bank.js";
import { getDb } from "./db.js";

/** Picks a random element. Caller guarantees the array is non-empty. */
function pick<T>(arr: T[]): T {
  return arr[Math.floor(Math.random() * arr.length)]!;
}

/** Weighted pick: each entry's `weight` is its relative probability mass. */
function weightedPick<T>(entries: { item: T; weight: number }[]): T {
  const total = entries.reduce((s, e) => s + e.weight, 0);
  let roll = Math.random() * total;
  for (const e of entries) {
    roll -= e.weight;
    if (roll <= 0) return e.item;
  }
  return entries[entries.length - 1]!.item;
}

/** Domains whose SM-2 due date is today or earlier. */
function overdueDomains(): DomainId[] {
  const today = new Date().toISOString().slice(0, 10);
  const rows = getDb()
    .prepare("SELECT domain FROM domains_sm2 WHERE due_date IS NOT NULL AND due_date <= ?")
    .all(today) as { domain: string }[];
  return rows.map((r) => r.domain as DomainId);
}

/** Domains answered at least 3 times with accuracy below 70%. */
function weakDomains(): DomainId[] {
  const rows = getDb()
    .prepare(
      `SELECT domain,
              COUNT(*) AS answered,
              SUM(correct) AS correct
       FROM sessions GROUP BY domain`,
    )
    .all() as { domain: string; answered: number; correct: number }[];
  return rows
    .filter((r) => r.answered >= 3 && r.correct / r.answered < 0.7)
    .map((r) => r.domain as DomainId);
}

/**
 * Picks one quiz question. If `domain` is given, the pick is constrained to it;
 * otherwise the domain is chosen by adaptive weighting:
 *   overdue domain  -> weight x3
 *   weak domain     -> weight x2
 *   baseline        -> the CCA-F exam weight
 */
export function pickQuizQuestion(domain?: DomainId): Question {
  let targetDomain: DomainId;

  if (domain) {
    targetDomain = domain;
  } else {
    const overdue = new Set(overdueDomains());
    const weak = new Set(weakDomains());
    targetDomain = weightedPick(
      DOMAINS.filter((d) => questionsForDomain(d.id).length > 0).map((d) => {
        let weight = d.weight;
        if (overdue.has(d.id)) weight *= 3;
        else if (weak.has(d.id)) weight *= 2;
        return { item: d.id, weight };
      }),
    );
  }

  const pool = questionsForDomain(targetDomain);
  if (pool.length === 0) {
    throw new Error(`No questions in the bank for domain ${targetDomain}.`);
  }
  return pick(pool);
}

/**
 * Selects exactly `total` questions for an exam simulation, split across
 * domains by the CCA-F exam weights. If a domain's pool is smaller than its
 * allotment, it draws with replacement for the shortfall so the exam still
 * has the right shape - a signal to top up that domain via the generator.
 */
export function selectExamQuestions(total: number): Question[] {
  const split = examDomainSplit(total);
  const selected: Question[] = [];

  for (const id of DOMAIN_IDS) {
    const need = split[id];
    const pool = questionsForDomain(id);
    if (pool.length === 0) continue;

    const shuffled = pool.slice().sort(() => Math.random() - 0.5);
    for (let i = 0; i < need; i++) {
      // Draw without replacement while the pool lasts, then with replacement.
      selected.push(i < shuffled.length ? shuffled[i]! : pick(pool));
    }
  }

  // Interleave so consecutive questions are not all from the same domain.
  return selected.sort(() => Math.random() - 0.5);
}
