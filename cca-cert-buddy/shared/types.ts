/**
 * Shared type vocabulary for CCA Cert Buddy.
 *
 * Both the Express backend and the vanilla-TS SPA import from this file, so the
 * API contract is checked at compile time on both sides. Keep it dependency-free
 * (no zod, no node imports) - it must compile under both tsconfig.json and
 * tsconfig.client.json.
 */

/** The five CCA-F exam domains. The review unit for spaced repetition. */
export type DomainId = "D1" | "D2" | "D3" | "D4" | "D5";

/** Where a bank question came from. */
export type QuestionSource = "seed" | "generated";

/** Quiz vs full exam simulation. */
export type StudyMode = "quiz" | "exam";

/** A multiple-choice option. `correct` is present only in Phase 2 payloads. */
export interface Option {
  letter: "A" | "B" | "C" | "D";
  text: string;
  correct?: boolean;
}

/**
 * A full bank question (Phase 2 shape). Mirrors the schema of the repo's
 * practice-questions.json, plus a `source` tag added by the seeder/generator.
 */
export interface Question {
  global_n: number;
  scenario: string;
  situation: string;
  question: string;
  options: Option[];
  correct: "A" | "B" | "C" | "D";
  explanation: string;
  domain: DomainId;
  secondaryDomains: DomainId[];
  source: QuestionSource;
}

/**
 * Phase 1 shape: what the client receives before answering. Answer-revealing
 * fields are stripped server-side so the SPA cannot peek.
 */
export type Phase1Question = Omit<Question, "correct" | "explanation"> & {
  options: Omit<Option, "correct">[];
};

/** One exam-domain row with its CCA-F weight percentage. */
export interface Domain {
  id: DomainId;
  name: string;
  weight: number;
  /** Relative path to the domain reference markdown in the parent repo. */
  refPath: string;
}

/** The Phase 2 payload returned after an answer is recorded. */
export interface AnswerResult {
  correct: boolean;
  correctLetter: "A" | "B" | "C" | "D";
  explanation: string;
  /** Per-option rationale keyed by letter. */
  perOption: Record<string, string>;
  domainRef: string;
}

/** Per-domain progress stats computed from the sessions table. */
export interface DomainProgress {
  domain: DomainId;
  name: string;
  answered: number;
  correct: number;
  accuracy: number;
}

/** One spaced-repetition review-queue entry. */
export interface ReviewItem {
  domain: DomainId;
  name: string;
  dueDate: string;
  intervalDays: number;
}

/** The full progress dashboard payload. */
export interface Progress {
  perDomain: DomainProgress[];
  weakDomains: DomainId[];
  reviewQueue: ReviewItem[];
  overall: { answered: number; correct: number; accuracy: number };
}

/** An in-flight exam simulation handed to the client. */
export interface ExamStart {
  examId: string;
  questions: Phase1Question[];
  durationSec: number;
}

/** The scored result of a completed exam simulation. */
export interface ExamResult {
  examId: string;
  rawCorrect: number;
  total: number;
  scaledScore: number;
  passed: boolean;
  perDomain: DomainProgress[];
}

/**
 * A single step in the agentic loop, captured for the agent-trace view.
 * This is the Domain 1 teaching surface made visible.
 */
export interface AgentTraceStep {
  iteration: number;
  /** The Claude stop_reason that drove this step's branch. */
  stopReason: string;
  /** Human-readable summary of what the loop did in response. */
  action: string;
  /** MCP tool calls executed in this step, if any. */
  toolCalls: { name: string; ok: boolean; summary: string }[];
}

/** The result of a live or build-time question generation, with its trace. */
export interface GenerateResult {
  question: Question;
  trace: AgentTraceStep[];
  /** The validator subagent's final verdict. */
  validatorVerdict: { ok: boolean; issues: string[]; repairRounds: number };
  usage: { inputTokens: number; outputTokens: number; estimatedCostUsd: number };
}

/** Health / capability probe response. */
export interface HealthInfo {
  status: "ok";
  bankSize: number;
  liveGenAvailable: boolean;
}

/** A discovered MCP primitive, surfaced by GET /api/mcp-info. */
export interface McpPrimitive {
  kind: "tool" | "resource" | "prompt";
  name: string;
  description: string;
}
