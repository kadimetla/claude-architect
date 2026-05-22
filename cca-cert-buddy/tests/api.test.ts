/**
 * API smoke tests - exercise the Express app via supertest, no port bound.
 *
 * These cover the offline surface (no API key needed): health, domains,
 * question selection, answer recording, progress, and the full exam flow.
 */
import { test } from "node:test";
import assert from "node:assert/strict";
import request from "supertest";
import { createApp } from "../server/app.js";

const app = createApp();

test("GET /api/health reports an ok status and the bank size", async () => {
  const res = await request(app).get("/api/health");
  assert.equal(res.status, 200);
  assert.equal(res.body.status, "ok");
  assert.ok(res.body.bankSize >= 60, `bankSize was ${res.body.bankSize}`);
});

test("GET /api/domains returns five domains summing to 100%", async () => {
  const res = await request(app).get("/api/domains");
  assert.equal(res.status, 200);
  assert.equal(res.body.length, 5);
  const total = res.body.reduce((s: number, d: { weight: number }) => s + d.weight, 0);
  assert.equal(total, 100);
});

test("GET /api/questions returns a Phase 1 question with no answer fields", async () => {
  const res = await request(app).get("/api/questions?mode=quiz");
  assert.equal(res.status, 200);
  const q = res.body[0];
  assert.ok(q.global_n, "question should have a global_n");
  assert.equal(q.correct, undefined, "Phase 1 must not reveal the correct letter");
  assert.equal(q.explanation, undefined, "Phase 1 must not reveal the explanation");
});

test("POST /api/answers grades an answer and returns per-option rationale", async () => {
  const list = await request(app).get("/api/questions?domain=D1&mode=quiz");
  const questionId = list.body[0].global_n;

  const res = await request(app)
    .post("/api/answers")
    .send({ questionId, chosen: "A", mode: "quiz", msElapsed: 5000 });
  assert.equal(res.status, 200);
  assert.equal(typeof res.body.correct, "boolean");
  assert.ok(["A", "B", "C", "D"].includes(res.body.correctLetter));
  assert.equal(Object.keys(res.body.perOption).length, 4);
});

test("POST /api/answers rejects an unknown question id", async () => {
  const res = await request(app)
    .post("/api/answers")
    .send({ questionId: 999999, chosen: "A", mode: "quiz" });
  assert.equal(res.status, 404);
});

test("GET /api/progress returns the five-domain breakdown", async () => {
  const res = await request(app).get("/api/progress");
  assert.equal(res.status, 200);
  assert.equal(res.body.perDomain.length, 5);
  assert.ok(typeof res.body.overall.answered === "number");
});

test("the exam flow: start yields 60 questions, score yields a scaled result", async () => {
  const start = await request(app).post("/api/exam/start");
  assert.equal(start.status, 200);
  assert.equal(start.body.questions.length, 60);
  assert.equal(start.body.durationSec, 7200);

  // Answer every question with its first option.
  const answers = start.body.questions.map((q: { global_n: number; options: { letter: string }[] }) => ({
    questionId: q.global_n,
    chosen: q.options[0].letter,
  }));
  const score = await request(app)
    .post(`/api/exam/${start.body.examId}/score`)
    .send({ answers });
  assert.equal(score.status, 200);
  assert.equal(score.body.total, 60);
  assert.ok(score.body.scaledScore >= 100 && score.body.scaledScore <= 1000);
  assert.equal(typeof score.body.passed, "boolean");
});

test("scoring an exam twice is rejected", async () => {
  const start = await request(app).post("/api/exam/start");
  await request(app).post(`/api/exam/${start.body.examId}/score`).send({ answers: [] });
  const second = await request(app)
    .post(`/api/exam/${start.body.examId}/score`)
    .send({ answers: [] });
  assert.equal(second.status, 409);
});

test("POST /api/generate returns 503 when no API key is configured", async (t) => {
  if (process.env.ANTHROPIC_API_KEY) {
    t.skip("ANTHROPIC_API_KEY is set - the 503 path cannot be exercised here.");
    return;
  }
  const res = await request(app).post("/api/generate").send({ domain: "D1" });
  assert.equal(res.status, 503);
});
