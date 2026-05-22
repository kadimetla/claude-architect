/**
 * Exam simulation.
 *
 * POST /api/exam/start      - begin a timed 60-question mock exam
 * POST /api/exam/:id/score  - grade a completed exam, return the scaled score
 *
 * The exam mirrors the real CCA-F: 60 questions, 120 minutes, a scaled score
 * from 100 to 1000, passing at 720. Exam answers are also written to the
 * sessions table so they feed the dashboard and SM-2 like quiz answers do.
 */
import { Router } from "express";
import { randomUUID } from "node:crypto";
import { z } from "zod";
import type { ExamResult, ExamStart } from "../../shared/types.js";
import { EXAM_DURATION_SEC, EXAM_QUESTION_COUNT } from "../../shared/domains.js";
import { getQuestion, toPhase1 } from "../bank.js";
import { selectExamQuestions } from "../selection.js";
import { gradeExam, toScaledScore, isPassing } from "../scoring.js";
import { getDb } from "../db.js";
import type { ExamRunRow } from "../db.js";
import { review, qualityFromAnswer, dueDateFrom } from "../sm2.js";
import type { Sm2Row } from "../db.js";

export const examRouter: Router = Router();

/** POST /api/exam/start - select 60 questions and persist the run. */
examRouter.post("/start", (_req, res) => {
  const questions = selectExamQuestions(EXAM_QUESTION_COUNT);
  const examId = randomUUID();

  getDb()
    .prepare(
      "INSERT INTO exam_runs (id, started_ts, question_ids) VALUES (?, ?, ?)",
    )
    .run(
      examId,
      new Date().toISOString(),
      JSON.stringify(questions.map((q) => q.global_n)),
    );

  const payload: ExamStart = {
    examId,
    questions: questions.map(toPhase1),
    durationSec: EXAM_DURATION_SEC,
  };
  res.json(payload);
});

const scoreBody = z.object({
  answers: z.array(
    z.object({
      questionId: z.number().int(),
      chosen: z.enum(["A", "B", "C", "D"]),
    }),
  ),
});

/** POST /api/exam/:id/score - grade the exam and persist the result. */
examRouter.post("/:id/score", (req, res) => {
  const examId = req.params.id;
  const parsed = scoreBody.safeParse(req.body);
  if (!parsed.success) {
    res.status(400).json({ error: parsed.error.issues[0]?.message ?? "Invalid body." });
    return;
  }

  const db = getDb();
  const run = db.prepare("SELECT * FROM exam_runs WHERE id = ?").get(examId) as
    | ExamRunRow
    | undefined;
  if (!run) {
    res.status(404).json({ error: `No exam run with id ${examId}.` });
    return;
  }
  if (run.finished_ts) {
    res.status(409).json({ error: "This exam has already been scored." });
    return;
  }

  // Resolve the exam's question set from the persisted id list.
  const questionIds = JSON.parse(run.question_ids) as number[];
  const questions = questionIds
    .map((id) => getQuestion(id))
    .filter((q): q is NonNullable<typeof q> => q !== undefined);

  const answerMap = new Map(parsed.data.answers.map((a) => [a.questionId, a.chosen]));
  const { rawCorrect, perDomain } = gradeExam(questions, answerMap);
  const scaledScore = toScaledScore(rawCorrect, questions.length);
  const passed = isPassing(scaledScore);

  // Persist the result and write every answered question into sessions so the
  // exam feeds the dashboard and SM-2, exactly as quiz answers do.
  const now = new Date();
  const finishTx = db.transaction(() => {
    db.prepare(
      `UPDATE exam_runs
       SET finished_ts = ?, raw_correct = ?, scaled_score = ?, passed = ?
       WHERE id = ?`,
    ).run(now.toISOString(), rawCorrect, scaledScore, passed ? 1 : 0, examId);

    const insertSession = db.prepare(
      `INSERT INTO sessions (ts, mode, exam_id, question_id, domain, chosen, correct, ms_elapsed)
       VALUES (@ts, 'exam', @examId, @questionId, @domain, @chosen, @correct, NULL)`,
    );
    const selectSm2 = db.prepare("SELECT * FROM domains_sm2 WHERE domain = ?");
    const updateSm2 = db.prepare(
      `UPDATE domains_sm2
       SET interval = ?, ease_factor = ?, repetitions = ?, last_reviewed = ?, due_date = ?
       WHERE domain = ?`,
    );

    for (const q of questions) {
      const chosen = answerMap.get(q.global_n);
      if (!chosen) continue; // unanswered questions are not recorded as answers
      const correct = chosen === q.correct;
      insertSession.run({
        ts: now.toISOString(),
        examId,
        questionId: q.global_n,
        domain: q.domain,
        chosen,
        correct: correct ? 1 : 0,
      });

      const row = selectSm2.get(q.domain) as Sm2Row;
      const next = review(
        { interval: row.interval, easeFactor: row.ease_factor, repetitions: row.repetitions },
        qualityFromAnswer(correct, null),
      );
      updateSm2.run(
        next.interval,
        next.easeFactor,
        next.repetitions,
        now.toISOString().slice(0, 10),
        dueDateFrom(now, next.interval),
        q.domain,
      );
    }
  });
  finishTx();

  const result: ExamResult = {
    examId,
    rawCorrect,
    total: questions.length,
    scaledScore,
    passed,
    perDomain,
  };
  res.json(result);
});
