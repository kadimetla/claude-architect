/**
 * Seed the question bank from the parent repo's hand-curated practice set.
 *
 * Reads ../practice-questions.json (60 CCA-F questions), tags each with
 * source: "seed", and writes data/question-bank.json.
 *
 * Idempotent: re-running replaces ONLY source === "seed" entries, so any
 * source === "generated" questions added later by the build-time generator
 * survive a re-seed. Run with: npm run seed
 */
import { readFileSync, writeFileSync, existsSync, mkdirSync } from "node:fs";
import { dirname, join } from "node:path";
import type { Question } from "../shared/types.js";
import { REPO_ROOT, BANK_PATH } from "../shared/paths.js";

const SOURCE = join(REPO_ROOT, "practice-questions.json");
const BANK = BANK_PATH;

/** The raw shape of a practice-questions.json entry (no source tag yet). */
type RawQuestion = Omit<Question, "source">;

/**
 * Normalizes a string to the repo voice rules. The upstream
 * practice-questions.json is community-sourced and carries em dashes; the
 * bank must be voice-clean, so the seeder rewrites em dashes (and the
 * en dash) to " - " on import. The upstream file is left untouched.
 */
function normalizeVoice(text: string): string {
  return text.replace(/\s*[—–]\s*/g, " - ");
}

/** Applies voice normalization to every text field of a question. */
function normalizeQuestion(q: RawQuestion): RawQuestion {
  return {
    ...q,
    scenario: normalizeVoice(q.scenario),
    situation: normalizeVoice(q.situation),
    question: normalizeVoice(q.question),
    explanation: normalizeVoice(q.explanation),
    options: q.options.map((o) => ({ ...o, text: normalizeVoice(o.text) })),
  };
}

function main(): void {
  if (!existsSync(SOURCE)) {
    console.error(`Source not found: ${SOURCE}`);
    console.error("Run this script from inside the cca-cert-buddy directory.");
    process.exit(1);
  }

  const raw = JSON.parse(readFileSync(SOURCE, "utf8")) as RawQuestion[];
  const seeded: Question[] = raw.map((q) => ({
    ...normalizeQuestion(q),
    source: "seed",
  }));

  // Preserve any generated questions from a prior run.
  let generated: Question[] = [];
  if (existsSync(BANK)) {
    const existing = JSON.parse(readFileSync(BANK, "utf8")) as Question[];
    generated = existing.filter((q) => q.source === "generated");
  }

  const bank = [...seeded, ...generated];

  mkdirSync(dirname(BANK), { recursive: true });
  writeFileSync(BANK, JSON.stringify(bank, null, 2) + "\n", "utf8");

  const byDomain: Record<string, number> = {};
  for (const q of bank) byDomain[q.domain] = (byDomain[q.domain] ?? 0) + 1;

  console.log(`Seeded ${seeded.length} questions, preserved ${generated.length} generated.`);
  console.log(`Bank total: ${bank.length} -> ${BANK}`);
  console.log(`By domain: ${JSON.stringify(byDomain)}`);
}

main();
