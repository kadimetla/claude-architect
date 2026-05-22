/**
 * Question routes.
 *
 * GET /api/questions      - adaptive weighted selection, Phase 1 shape
 * GET /api/questions/:id  - one full question, Phase 2 shape (answer revealed)
 *
 * The :id route exists so the SPA can fetch the full answer payload after a
 * learner submits. The list route never reveals the answer.
 */
import { Router } from "express";
import { z } from "zod";
import { DOMAIN_IDS } from "../../shared/domains.js";
import { getQuestion, toPhase1 } from "../bank.js";
import { pickQuizQuestion } from "../selection.js";

export const questionsRouter: Router = Router();

const listQuery = z.object({
  domain: z.enum(DOMAIN_IDS as [string, ...string[]]).optional(),
  limit: z.coerce.number().int().min(1).max(20).default(1),
});

/** GET /api/questions?domain=D1&limit=1 - Phase 1 questions for quiz mode. */
questionsRouter.get("/", (req, res) => {
  const parsed = listQuery.safeParse(req.query);
  if (!parsed.success) {
    res.status(400).json({ error: parsed.error.issues[0]?.message ?? "Invalid query." });
    return;
  }
  const { domain, limit } = parsed.data;

  const out = [];
  for (let i = 0; i < limit; i++) {
    out.push(toPhase1(pickQuizQuestion(domain as never)));
  }
  res.json(out);
});

/** GET /api/questions/:id - full question including answer and explanation. */
questionsRouter.get("/:id", (req, res) => {
  const id = Number(req.params.id);
  if (!Number.isInteger(id)) {
    res.status(400).json({ error: "Question id must be an integer." });
    return;
  }
  const q = getQuestion(id);
  if (!q) {
    res.status(404).json({ error: `No question with global_n ${id}.` });
    return;
  }
  res.json(q);
});
