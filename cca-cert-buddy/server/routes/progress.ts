/**
 * Progress dashboard.
 *
 * GET /api/progress - per-domain accuracy, weak-domain identification, and the
 * SM-2 review queue. All of this is computed at read time from the sessions
 * and domains_sm2 tables; nothing is precomputed or cached.
 */
import { Router } from "express";
import type { DomainProgress, Progress, ReviewItem } from "../../shared/types.js";
import { DOMAINS, getDomain } from "../../shared/domains.js";
import { getDb } from "../db.js";

export const progressRouter: Router = Router();

/** GET /api/progress - the full dashboard payload. */
progressRouter.get("/", (_req, res) => {
  const db = getDb();

  // Per-domain answered/correct tallies from the sessions table.
  const tallies = db
    .prepare(
      `SELECT domain,
              COUNT(*)      AS answered,
              SUM(correct)  AS correct
       FROM sessions GROUP BY domain`,
    )
    .all() as { domain: string; answered: number; correct: number }[];
  const tallyByDomain = new Map(tallies.map((t) => [t.domain, t]));

  const perDomain: DomainProgress[] = DOMAINS.map((d) => {
    const t = tallyByDomain.get(d.id);
    const answered = t?.answered ?? 0;
    const correct = t?.correct ?? 0;
    return {
      domain: d.id,
      name: d.name,
      answered,
      correct,
      accuracy: answered === 0 ? 0 : correct / answered,
    };
  });

  // A domain is weak if it has been answered at least 3 times under 70%.
  const weakDomains = perDomain
    .filter((d) => d.answered >= 3 && d.accuracy < 0.7)
    .map((d) => d.domain);

  // The SM-2 review queue: domains due today or earlier, soonest first.
  const today = new Date().toISOString().slice(0, 10);
  const dueRows = db
    .prepare(
      `SELECT domain, interval, due_date
       FROM domains_sm2
       WHERE due_date IS NOT NULL AND due_date <= ?
       ORDER BY due_date ASC`,
    )
    .all(today) as { domain: string; interval: number; due_date: string }[];

  const reviewQueue: ReviewItem[] = dueRows.map((r) => ({
    domain: r.domain as ReviewItem["domain"],
    name: getDomain(r.domain).name,
    dueDate: r.due_date,
    intervalDays: Math.round(r.interval),
  }));

  const totalAnswered = perDomain.reduce((s, d) => s + d.answered, 0);
  const totalCorrect = perDomain.reduce((s, d) => s + d.correct, 0);

  const progress: Progress = {
    perDomain,
    weakDomains,
    reviewQueue,
    overall: {
      answered: totalAnswered,
      correct: totalCorrect,
      accuracy: totalAnswered === 0 ? 0 : totalCorrect / totalAnswered,
    },
  };
  res.json(progress);
});
