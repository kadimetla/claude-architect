/**
 * Answer recording.
 *
 * POST /api/answers - records one submitted answer, updates the domain's SM-2
 * schedule, and returns the Phase 2 payload (result + per-option rationale).
 *
 * This is where the spaced-repetition loop closes: every answer feeds both the
 * progress dashboard and the next quiz's adaptive selection.
 */
import { Router } from "express";
import { z } from "zod";
import type { AnswerResult } from "../../shared/types.js";
import { getQuestion } from "../bank.js";
import { buildAnswerResult } from "../rationale.js";
import { getDb } from "../db.js";
import type { Sm2Row } from "../db.js";
import { review, qualityFromAnswer, dueDateFrom } from "../sm2.js";

export const answersRouter: Router = Router();

const answerBody = z.object({
  questionId: z.number().int(),
  chosen: z.enum(["A", "B", "C", "D"]),
  mode: z.enum(["quiz", "exam"]).default("quiz"),
  examId: z.string().optional(),
  msElapsed: z.number().int().nonnegative().nullable().default(null),
});

/** POST /api/answers - persist an answer, advance SM-2, return Phase 2. */
answersRouter.post("/", (req, res) => {
  const parsed = answerBody.safeParse(req.body);
  if (!parsed.success) {
    res.status(400).json({ error: parsed.error.issues[0]?.message ?? "Invalid body." });
    return;
  }
  const { questionId, chosen, mode, examId, msElapsed } = parsed.data;

  const question = getQuestion(questionId);
  if (!question) {
    res.status(404).json({ error: `No question with global_n ${questionId}.` });
    return;
  }

  const result: AnswerResult = buildAnswerResult(question, chosen);
  const db = getDb();

  // Persist the answer and advance the domain's SM-2 state in one transaction,
  // so the dashboard and the review queue never see a partial write.
  const recordTx = db.transaction(() => {
    db.prepare(
      `INSERT INTO sessions (ts, mode, exam_id, question_id, domain, chosen, correct, ms_elapsed)
       VALUES (?, ?, ?, ?, ?, ?, ?, ?)`,
    ).run(
      new Date().toISOString(),
      mode,
      examId ?? null,
      questionId,
      question.domain,
      chosen,
      result.correct ? 1 : 0,
      msElapsed,
    );

    const row = db
      .prepare("SELECT * FROM domains_sm2 WHERE domain = ?")
      .get(question.domain) as Sm2Row;

    const quality = qualityFromAnswer(result.correct, msElapsed);
    const next = review(
      { interval: row.interval, easeFactor: row.ease_factor, repetitions: row.repetitions },
      quality,
    );
    const now = new Date();
    db.prepare(
      `UPDATE domains_sm2
       SET interval = ?, ease_factor = ?, repetitions = ?, last_reviewed = ?, due_date = ?
       WHERE domain = ?`,
    ).run(
      next.interval,
      next.easeFactor,
      next.repetitions,
      now.toISOString().slice(0, 10),
      dueDateFrom(now, next.interval),
      question.domain,
    );
  });
  recordTx();

  res.json(result);
});
