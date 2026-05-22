/**
 * The CCA-F exam domain blueprint - the single source of truth for domain
 * identity, names, weight percentages, and reference-doc paths.
 *
 * Weights are sourced from CERT-PROGRAM-BRIEFING.md in the parent repo and
 * sum to 100. The exam-sim question split is derived from these weights.
 */
import type { Domain, DomainId } from "./types.js";

export const DOMAINS: Domain[] = [
  {
    id: "D1",
    name: "Agentic Architecture & Orchestration",
    weight: 27,
    refPath: "../domain-1-agentic.md",
  },
  {
    id: "D2",
    name: "Tool Design & MCP Integration",
    weight: 18,
    refPath: "../domain-2-tools-mcp.md",
  },
  {
    id: "D3",
    name: "Claude Code Configuration & Workflows",
    weight: 20,
    refPath: "../domain-3-claude-code.md",
  },
  {
    id: "D4",
    name: "Prompt Engineering & Structured Output",
    weight: 20,
    refPath: "../domain-4-prompts.md",
  },
  {
    id: "D5",
    name: "Context Management & Reliability",
    weight: 15,
    refPath: "../domain-5-context.md",
  },
];

export const DOMAIN_IDS: DomainId[] = DOMAINS.map((d) => d.id);

/** Lookup a domain by id. Throws on an unknown id - fail loud, not silent. */
export function getDomain(id: string): Domain {
  const found = DOMAINS.find((d) => d.id === id);
  if (!found) {
    throw new Error(`Unknown domain id: ${id}. Expected one of ${DOMAIN_IDS.join(", ")}.`);
  }
  return found;
}

/** Total questions on the real exam. The exam-sim mirrors this. */
export const EXAM_QUESTION_COUNT = 60;

/** Exam duration in seconds (120 minutes). */
export const EXAM_DURATION_SEC = 120 * 60;

/**
 * The per-domain question split for a 60-question exam, weighted by the
 * blueprint. Largest-remainder rounding guarantees the parts sum to exactly 60.
 */
export function examDomainSplit(total = EXAM_QUESTION_COUNT): Record<DomainId, number> {
  const raw = DOMAINS.map((d) => ({ id: d.id, exact: (d.weight / 100) * total }));
  const floored = raw.map((r) => ({ id: r.id, count: Math.floor(r.exact), frac: r.exact - Math.floor(r.exact) }));
  let remainder = total - floored.reduce((s, r) => s + r.count, 0);
  // Hand out the leftover seats to the largest fractional parts first.
  floored
    .slice()
    .sort((a, b) => b.frac - a.frac)
    .forEach((r) => {
      if (remainder > 0) {
        r.count += 1;
        remainder -= 1;
      }
    });
  const out = {} as Record<DomainId, number>;
  for (const r of floored) out[r.id] = r.count;
  return out;
}
