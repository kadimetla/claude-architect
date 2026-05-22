/**
 * Structural validator for CCA-F practice questions.
 *
 * One source of truth, imported by three places:
 *   - the MCP server's validate_question tool (structured-error demo)
 *   - the build-time generator's validate-and-repair loop
 *   - scripts/validate-bank.ts (whole-bank gate)
 *
 * Returns a list of human-readable issues - an empty list means the question
 * passed. The validator is intentionally strict: every issue it reports is a
 * concrete, fixable defect, so the generator's repair loop has something
 * actionable to act on.
 */
import type { DomainId } from "./types.js";
import { DOMAIN_IDS } from "./domains.js";

/** A draft question as produced by the generator, before it joins the bank. */
export interface DraftQuestion {
  scenario?: unknown;
  situation?: unknown;
  question?: unknown;
  options?: unknown;
  correct?: unknown;
  explanation?: unknown;
  domain?: unknown;
  secondaryDomains?: unknown;
}

/** Outcome of validating one question. */
export interface ValidationResult {
  ok: boolean;
  issues: string[];
}

const LETTERS = ["A", "B", "C", "D"] as const;

/** Voice-rule patterns banned in this repo (em dash, AWS, "ask" as a noun). */
function voiceIssues(text: string, field: string): string[] {
  const issues: string[] = [];
  if (text.includes("—")) {
    issues.push(`${field}: contains an em dash - use " - ", a comma, or a period.`);
  }
  if (/\bAWS\b/.test(text)) {
    issues.push(`${field}: mentions AWS - not permitted in this course material.`);
  }
  // "ask" used as a noun: "an ask", "the ask", "a heavy ask".
  if (/\b(an|the|a)\s+(\w+\s+)?ask\b/i.test(text)) {
    issues.push(`${field}: uses "ask" as a noun - use "request", "question", or "proposal".`);
  }
  return issues;
}

/**
 * Validates a draft question against the structural and voice rules.
 *
 * `existingSituations` enables a near-duplicate guard: if the draft's situation
 * overlaps heavily with an existing bank question, it is rejected so the
 * generator does not regurgitate the seed set.
 */
export function validateQuestion(
  draft: DraftQuestion,
  existingSituations: string[] = [],
): ValidationResult {
  const issues: string[] = [];

  // --- Required string fields ---
  for (const field of ["scenario", "situation", "question", "explanation"] as const) {
    const value = draft[field];
    if (typeof value !== "string" || value.trim().length === 0) {
      issues.push(`${field}: missing or empty.`);
    } else {
      issues.push(...voiceIssues(value, field));
    }
  }

  // --- Domain ---
  if (typeof draft.domain !== "string" || !DOMAIN_IDS.includes(draft.domain as DomainId)) {
    issues.push(`domain: must be one of ${DOMAIN_IDS.join(", ")}.`);
  }

  // --- Options ---
  const options = draft.options;
  if (!Array.isArray(options) || options.length !== 4) {
    issues.push("options: must be an array of exactly 4 entries.");
  } else {
    const seenLetters = new Set<string>();
    let correctCount = 0;
    options.forEach((opt, i) => {
      const o = opt as { letter?: unknown; text?: unknown; correct?: unknown };
      if (o.letter !== LETTERS[i]) {
        issues.push(`options[${i}]: letter must be "${LETTERS[i]}".`);
      }
      seenLetters.add(String(o.letter));
      if (typeof o.text !== "string" || o.text.trim().length === 0) {
        issues.push(`options[${i}]: text missing or empty.`);
      } else {
        issues.push(...voiceIssues(o.text, `options[${i}].text`));
      }
      if (o.correct === true) correctCount += 1;
    });
    if (seenLetters.size !== 4) {
      issues.push("options: letters must be A, B, C, D with no duplicates.");
    }
    if (correctCount !== 1) {
      issues.push(`options: exactly one option must have correct: true (found ${correctCount}).`);
    }
  }

  // --- correct letter matches the flagged option ---
  if (typeof draft.correct !== "string" || !LETTERS.includes(draft.correct as never)) {
    issues.push('correct: must be one of "A", "B", "C", "D".');
  } else if (Array.isArray(options)) {
    const flagged = options.find((o) => (o as { correct?: unknown }).correct === true) as
      | { letter?: unknown }
      | undefined;
    if (flagged && flagged.letter !== draft.correct) {
      issues.push(
        `correct: letter "${draft.correct}" does not match the option flagged correct ("${String(flagged.letter)}").`,
      );
    }
  }

  // --- secondaryDomains ---
  if (draft.secondaryDomains !== undefined) {
    if (!Array.isArray(draft.secondaryDomains)) {
      issues.push("secondaryDomains: must be an array when present.");
    } else if (
      draft.secondaryDomains.some((d) => !DOMAIN_IDS.includes(d as DomainId))
    ) {
      issues.push(`secondaryDomains: each entry must be one of ${DOMAIN_IDS.join(", ")}.`);
    }
  }

  // --- Near-duplicate guard ---
  if (typeof draft.situation === "string" && existingSituations.length > 0) {
    const draftTokens = tokenize(draft.situation);
    for (const existing of existingSituations) {
      if (jaccard(draftTokens, tokenize(existing)) > 0.9) {
        issues.push("situation: too similar to an existing bank question - write an original scenario.");
        break;
      }
    }
  }

  return { ok: issues.length === 0, issues };
}

/** Lowercased word set, for the duplicate-overlap measure. */
function tokenize(text: string): Set<string> {
  return new Set(
    text
      .toLowerCase()
      .replace(/[^a-z0-9\s]/g, " ")
      .split(/\s+/)
      .filter((w) => w.length > 2),
  );
}

/** Jaccard similarity of two token sets, 0 (disjoint) to 1 (identical). */
function jaccard(a: Set<string>, b: Set<string>): number {
  if (a.size === 0 && b.size === 0) return 1;
  let intersection = 0;
  for (const t of a) if (b.has(t)) intersection += 1;
  return intersection / (a.size + b.size - intersection);
}
