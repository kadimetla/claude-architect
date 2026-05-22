/**
 * In-memory app state.
 *
 * Deliberately tiny: a vanilla-TS SPA does not need a reactive store. Views
 * read and write this module-scoped object directly and re-render on
 * navigation. State that must survive a reload (progress, exam runs) lives
 * server-side in SQLite, not here.
 */
import type { ExamResult, ExamStart, GenerateResult } from "../shared/types.js";

interface AppState {
  /** The exam simulation currently in progress, if any. */
  activeExam: (ExamStart & { answers: Map<number, string>; deadline: number }) | null;
  /** The most recently scored exam, handed to the result view. */
  lastExamResult: ExamResult | null;
  /** The most recent live generation, handed to the agent-trace view. */
  lastGeneration: GenerateResult | null;
}

export const state: AppState = {
  activeExam: null,
  lastExamResult: null,
  lastGeneration: null,
};
