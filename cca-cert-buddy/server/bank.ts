/**
 * In-memory question bank.
 *
 * The bank is small (dozens to a few hundred questions) and read-only at
 * runtime, so it loads fully into memory once at startup and is indexed by
 * domain for O(1) weighted selection. The build-time generator writes
 * data/question-bank.json; this module only reads it.
 */
import { readFileSync, existsSync } from "node:fs";
import type { DomainId, Phase1Question, Question } from "../shared/types.js";
import { BANK_PATH } from "../shared/paths.js";

let all: Question[] = [];
let byId = new Map<number, Question>();
let byDomain = new Map<DomainId, Question[]>();

/** Loads and indexes the bank. Idempotent - safe to call again to reload. */
export function loadBank(): void {
  if (!existsSync(BANK_PATH)) {
    throw new Error(
      `Question bank not found at ${BANK_PATH}. Run \`npm run seed\` first.`,
    );
  }
  all = JSON.parse(readFileSync(BANK_PATH, "utf8")) as Question[];
  byId = new Map(all.map((q) => [q.global_n, q]));
  byDomain = new Map();
  for (const q of all) {
    const list = byDomain.get(q.domain) ?? [];
    list.push(q);
    byDomain.set(q.domain, list);
  }
}

/** Total questions in the bank. */
export function bankSize(): number {
  return all.length;
}

/** Every question (Phase 2 shape). */
export function allQuestions(): Question[] {
  return all;
}

/** Questions for one domain. Empty array if the domain has none. */
export function questionsForDomain(domain: DomainId): Question[] {
  return byDomain.get(domain) ?? [];
}

/** Full question by global_n, or undefined if not found. */
export function getQuestion(id: number): Question | undefined {
  return byId.get(id);
}

/**
 * Strips answer-revealing fields for a Phase 1 payload. The SPA must not
 * receive `correct` or `explanation` before the learner answers.
 */
export function toPhase1(q: Question): Phase1Question {
  return {
    global_n: q.global_n,
    scenario: q.scenario,
    situation: q.situation,
    question: q.question,
    options: q.options.map((o) => ({ letter: o.letter, text: o.text })),
    domain: q.domain,
    secondaryDomains: q.secondaryDomains,
    source: q.source,
  };
}

/** The next free global_n - used by the generator when appending questions. */
export function nextGlobalN(): number {
  return all.length === 0 ? 1 : Math.max(...all.map((q) => q.global_n)) + 1;
}
