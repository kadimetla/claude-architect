/**
 * Build-time question generator.
 *
 * Runs the agent core (server/agent/generate.ts) in batch to author fresh
 * exam-realistic questions and append them to data/question-bank.json. This is
 * the author-side tool - learners never run it. It costs a few cents per run
 * and is meant to top up thin domains or refresh the bank.
 *
 * Usage:
 *   npm run generate -- --domain D2 --count 5
 *   npm run generate -- --count 2          (one question for each domain)
 *
 * Requires ANTHROPIC_API_KEY in .env.
 */
import "dotenv/config";
import type { DomainId } from "../shared/types.js";
import { DOMAIN_IDS } from "../shared/domains.js";
import { liveGenAvailable } from "../server/anthropic.js";
import { loadBank } from "../server/bank.js";
import { getDb } from "../server/db.js";
import { generateQuestion } from "../server/agent/generate.js";
import { closeMcpClient } from "../server/agent/mcp-client.js";

/** Parses --domain and --count from argv. */
function parseArgs(): { domains: DomainId[]; count: number } {
  const args = process.argv.slice(2);
  let domain: string | undefined;
  let count = 1;
  for (let i = 0; i < args.length; i++) {
    if (args[i] === "--domain") domain = args[++i];
    else if (args[i] === "--count") count = Number(args[++i]);
  }
  if (domain && !DOMAIN_IDS.includes(domain as DomainId)) {
    console.error(`Invalid --domain "${domain}". Expected one of ${DOMAIN_IDS.join(", ")}.`);
    process.exit(1);
  }
  if (!Number.isInteger(count) || count < 1) {
    console.error("--count must be a positive integer.");
    process.exit(1);
  }
  return { domains: domain ? [domain as DomainId] : DOMAIN_IDS, count };
}

async function main(): Promise<void> {
  if (!liveGenAvailable()) {
    console.error("ANTHROPIC_API_KEY is not set. Copy .env.example to .env and add a key.");
    process.exit(1);
  }

  const { domains, count } = parseArgs();
  loadBank();
  getDb();

  let kept = 0;
  let rejected = 0;
  let totalCost = 0;

  for (const domain of domains) {
    for (let i = 1; i <= count; i++) {
      process.stdout.write(`Generating ${domain} question ${i}/${count} ... `);
      try {
        const result = await generateQuestion(domain, { persist: true });
        totalCost += result.usage.estimatedCostUsd;

        if (result.validatorVerdict.ok) {
          kept += 1;
          console.log(
            `kept (global_n=${result.question.global_n}, ` +
              `${result.validatorVerdict.repairRounds} repair round(s), ` +
              `${result.trace.length} loop step(s)).`,
          );
        } else {
          rejected += 1;
          console.log(`rejected after ${result.validatorVerdict.repairRounds} repair round(s):`);
          for (const issue of result.validatorVerdict.issues) console.log(`    - ${issue}`);
        }
      } catch (err) {
        rejected += 1;
        console.log(`failed: ${err instanceof Error ? err.message : String(err)}`);
      }
    }
  }

  console.log(
    `\nDone. Kept ${kept}, rejected ${rejected}. ` +
      `Estimated cost: $${totalCost.toFixed(4)}.`,
  );
  console.log("Run `npm run validate:bank` to confirm the bank is still clean.");

  await closeMcpClient();
}

main().catch(async (err) => {
  console.error("Generation run failed:", err);
  await closeMcpClient();
  process.exit(1);
});
