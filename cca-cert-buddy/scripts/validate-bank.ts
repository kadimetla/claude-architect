/**
 * Whole-bank structural validator.
 *
 * Runs shared/question-validator.ts across every question in
 * data/question-bank.json and exits non-zero if any question fails. This is
 * the quality gate: it runs after the generator and in CI to guarantee the
 * shipped bank is structurally sound.
 *
 * Run with: npm run validate:bank
 */
import { readFileSync, existsSync } from "node:fs";
import type { Question } from "../shared/types.js";
import { validateQuestion } from "../shared/question-validator.js";
import { BANK_PATH } from "../shared/paths.js";

function main(): void {
  if (!existsSync(BANK_PATH)) {
    console.error(`Question bank not found at ${BANK_PATH}. Run \`npm run seed\` first.`);
    process.exit(1);
  }

  const bank = JSON.parse(readFileSync(BANK_PATH, "utf8")) as Question[];
  let failed = 0;

  bank.forEach((q, index) => {
    // Validate each question against all OTHER situations for the dup guard.
    const others = bank.filter((_, i) => i !== index).map((o) => o.situation);
    const result = validateQuestion(q, others);
    if (!result.ok) {
      failed += 1;
      console.error(`FAIL question global_n=${q.global_n} (${q.domain}, source=${q.source}):`);
      for (const issue of result.issues) console.error(`  - ${issue}`);
    }
  });

  if (failed > 0) {
    console.error(`\n${failed} of ${bank.length} questions failed validation.`);
    process.exit(1);
  }
  console.log(`PASS: all ${bank.length} questions are structurally valid.`);
}

main();
