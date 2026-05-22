/**
 * Unit tests for the domain blueprint and the exam-split math.
 */
import { test } from "node:test";
import assert from "node:assert/strict";
import { DOMAINS, examDomainSplit, EXAM_QUESTION_COUNT } from "../shared/domains.js";

test("there are exactly five CCA-F domains", () => {
  assert.equal(DOMAINS.length, 5);
});

test("the domain weights sum to 100", () => {
  const total = DOMAINS.reduce((s, d) => s + d.weight, 0);
  assert.equal(total, 100);
});

test("the exam split sums to exactly the question count", () => {
  const split = examDomainSplit(EXAM_QUESTION_COUNT);
  const total = Object.values(split).reduce((s, n) => s + n, 0);
  assert.equal(total, EXAM_QUESTION_COUNT);
});

test("each domain gets at least one exam question", () => {
  const split = examDomainSplit(EXAM_QUESTION_COUNT);
  for (const d of DOMAINS) {
    assert.ok(split[d.id] >= 1, `${d.id} got ${split[d.id]} questions`);
  }
});

test("the heaviest domain (D1, 27%) gets the most questions", () => {
  const split = examDomainSplit(EXAM_QUESTION_COUNT);
  const max = Math.max(...Object.values(split));
  assert.equal(split.D1, max);
});

test("the split still sums correctly for an off-size exam", () => {
  const split = examDomainSplit(37);
  const total = Object.values(split).reduce((s, n) => s + n, 0);
  assert.equal(total, 37);
});
