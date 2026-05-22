/**
 * Unit tests for the SM-2 spaced-repetition module.
 */
import { test } from "node:test";
import assert from "node:assert/strict";
import { review, qualityFromAnswer, dueDateFrom } from "../server/sm2.js";

const FRESH = { interval: 1, easeFactor: 2.5, repetitions: 0 };

test("a correct first review sets a 1-day interval", () => {
  const next = review(FRESH, 4);
  assert.equal(next.repetitions, 1);
  assert.equal(next.interval, 1);
});

test("a correct second review jumps the interval to 6 days", () => {
  const after1 = review(FRESH, 4);
  const after2 = review(after1, 4);
  assert.equal(after2.repetitions, 2);
  assert.equal(after2.interval, 6);
});

test("a correct third review grows the interval by the ease factor", () => {
  let s = review(FRESH, 4);
  s = review(s, 4);
  const after3 = review(s, 4);
  assert.equal(after3.repetitions, 3);
  // interval was 6; grows by ease factor (~2.5), so it should exceed 6.
  assert.ok(after3.interval > 6, `expected interval > 6, got ${after3.interval}`);
});

test("a wrong answer resets repetitions and drops the interval to 1", () => {
  let s = review(FRESH, 4);
  s = review(s, 4); // interval now 6
  const lapsed = review(s, 2); // wrong
  assert.equal(lapsed.repetitions, 0);
  assert.equal(lapsed.interval, 1);
});

test("the ease factor never falls below the 1.3 floor", () => {
  let s = FRESH;
  for (let i = 0; i < 20; i++) s = review(s, 0); // repeated total failure
  assert.ok(s.easeFactor >= 1.3, `ease factor ${s.easeFactor} fell below 1.3`);
});

test("review never mutates its input", () => {
  const input = { ...FRESH };
  review(input, 5);
  assert.deepEqual(input, FRESH);
});

test("qualityFromAnswer scores fast-correct above slow-correct above wrong", () => {
  assert.equal(qualityFromAnswer(true, 5_000), 5);
  assert.equal(qualityFromAnswer(true, 60_000), 4);
  assert.equal(qualityFromAnswer(true, null), 4);
  assert.equal(qualityFromAnswer(false, 5_000), 2);
});

test("dueDateFrom advances the date by the interval", () => {
  const due = dueDateFrom(new Date("2026-05-01T00:00:00Z"), 6);
  assert.equal(due, "2026-05-07");
});
