/**
 * Unit tests for exam scoring.
 */
import { test } from "node:test";
import assert from "node:assert/strict";
import { toScaledScore, isPassing, PASSING_SCALED_SCORE } from "../server/scoring.js";

test("a perfect raw score maps to the 1000 ceiling", () => {
  assert.equal(toScaledScore(60, 60), 1000);
});

test("a zero raw score maps to the 100 floor", () => {
  assert.equal(toScaledScore(0, 60), 100);
});

test("the scaled score is monotonic in raw-correct", () => {
  let prev = -1;
  for (let raw = 0; raw <= 60; raw++) {
    const score = toScaledScore(raw, 60);
    assert.ok(score >= prev, `score dropped at raw=${raw}`);
    prev = score;
  }
});

test("the passing line of 720 anchors exactly to 72% raw-correct", () => {
  // The piecewise curve has its kink at 72%. On a 50-question exam, 36/50 is
  // exactly 72% and must score precisely 720.
  assert.equal(toScaledScore(36, 50), 720);
  assert.ok(isPassing(toScaledScore(36, 50)), "72% should pass");
  assert.ok(!isPassing(toScaledScore(35, 50)), "below 72% should not pass");
});

test("the curve is continuous across the 72% kink", () => {
  // Just-below and just-above the kink should not jump - the two segments meet.
  const below = toScaledScore(719, 1000);
  const above = toScaledScore(721, 1000);
  assert.ok(below < 720 && above > 720, `expected ${below} < 720 < ${above}`);
});

test("isPassing respects the published passing line", () => {
  assert.equal(isPassing(PASSING_SCALED_SCORE), true);
  assert.equal(isPassing(PASSING_SCALED_SCORE - 1), false);
});

test("an empty exam scores the floor rather than dividing by zero", () => {
  assert.equal(toScaledScore(0, 0), 100);
});
