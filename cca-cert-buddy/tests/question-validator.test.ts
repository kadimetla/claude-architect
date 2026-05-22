/**
 * Unit tests for the question structural validator.
 */
import { test } from "node:test";
import assert from "node:assert/strict";
import { validateQuestion } from "../shared/question-validator.js";

/** A structurally sound draft, used as the baseline for negative tests. */
function soundDraft() {
  return {
    scenario: "Multi-agent pipeline",
    situation: "A coordinator delegates a research task to two subagents.",
    question: "Which approach is most effective?",
    options: [
      { letter: "A", text: "Let each subagent write the final report directly.", correct: false },
      { letter: "B", text: "Have the coordinator merge the results.", correct: true },
      { letter: "C", text: "Discard one subagent's output at random.", correct: false },
      { letter: "D", text: "Skip the coordinator entirely.", correct: false },
    ],
    correct: "B",
    explanation: "The coordinator owns integration, preserving control over the merge.",
    domain: "D1",
    secondaryDomains: [],
  };
}

test("a sound draft passes with no issues", () => {
  const result = validateQuestion(soundDraft());
  assert.equal(result.ok, true, JSON.stringify(result.issues));
});

test("a draft with three options fails", () => {
  const draft = soundDraft();
  draft.options = draft.options.slice(0, 3);
  const result = validateQuestion(draft);
  assert.equal(result.ok, false);
  assert.ok(result.issues.some((i) => i.includes("exactly 4")));
});

test("a draft with two correct options fails", () => {
  const draft = soundDraft();
  draft.options[0]!.correct = true;
  const result = validateQuestion(draft);
  assert.equal(result.ok, false);
  assert.ok(result.issues.some((i) => i.includes("exactly one option")));
});

test("a mismatched correct letter fails", () => {
  const draft = soundDraft();
  draft.correct = "A"; // option A is not the flagged-correct one
  const result = validateQuestion(draft);
  assert.equal(result.ok, false);
  assert.ok(result.issues.some((i) => i.includes("does not match")));
});

test("an em dash anywhere fails the voice check", () => {
  const draft = soundDraft();
  draft.explanation = "The coordinator owns integration — it controls the merge.";
  const result = validateQuestion(draft);
  assert.equal(result.ok, false);
  assert.ok(result.issues.some((i) => i.includes("em dash")));
});

test("an AWS mention fails the voice check", () => {
  const draft = soundDraft();
  draft.situation = "The pipeline runs on AWS infrastructure.";
  const result = validateQuestion(draft);
  assert.equal(result.ok, false);
  assert.ok(result.issues.some((i) => i.includes("AWS")));
});

test("the near-duplicate guard rejects a near-identical situation", () => {
  const draft = soundDraft();
  const result = validateQuestion(draft, [draft.situation]);
  assert.equal(result.ok, false);
  assert.ok(result.issues.some((i) => i.includes("too similar")));
});

test("an unknown domain fails", () => {
  const draft = soundDraft();
  draft.domain = "D9";
  const result = validateQuestion(draft);
  assert.equal(result.ok, false);
  assert.ok(result.issues.some((i) => i.includes("domain")));
});
