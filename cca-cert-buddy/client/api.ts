/**
 * Typed fetch wrappers around the backend REST API.
 *
 * One function per endpoint, each returning a type from shared/types.ts, so a
 * route-shape change is a compile error in the SPA. All requests go to /api,
 * which Vite proxies to Express in dev and which is same-origin in production.
 */
import type {
  AnswerResult,
  Domain,
  ExamResult,
  ExamStart,
  GenerateResult,
  HealthInfo,
  McpPrimitive,
  Phase1Question,
  Progress,
  Question,
  DomainId,
} from "../shared/types.js";

/** Throws on a non-2xx response, surfacing the server's error message. */
async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`/api${path}`, {
    headers: { "Content-Type": "application/json" },
    ...init,
  });
  if (!res.ok) {
    const body = (await res.json().catch(() => ({}))) as { error?: string };
    throw new Error(body.error ?? `Request failed: ${res.status}`);
  }
  return res.json() as Promise<T>;
}

export const api = {
  health: () => request<HealthInfo>("/health"),

  domains: () => request<Domain[]>("/domains"),

  mcpInfo: () => request<McpPrimitive[]>("/mcp-info"),

  /** One Phase 1 quiz question, optionally constrained to a domain. */
  quizQuestion: (domain?: DomainId) =>
    request<Phase1Question[]>(
      `/questions?mode=quiz&limit=1${domain ? `&domain=${domain}` : ""}`,
    ).then((arr) => arr[0]!),

  /** The full Phase 2 question (answer revealed) by id. */
  fullQuestion: (id: number) => request<Question>(`/questions/${id}`),

  /** Records an answer and returns the Phase 2 result. */
  recordAnswer: (body: {
    questionId: number;
    chosen: string;
    mode: "quiz" | "exam";
    examId?: string;
    msElapsed?: number | null;
  }) => request<AnswerResult>("/answers", { method: "POST", body: JSON.stringify(body) }),

  progress: () => request<Progress>("/progress"),

  startExam: () => request<ExamStart>("/exam/start", { method: "POST" }),

  scoreExam: (examId: string, answers: { questionId: number; chosen: string }[]) =>
    request<ExamResult>(`/exam/${examId}/score`, {
      method: "POST",
      body: JSON.stringify({ answers }),
    }),

  /** Live-generates one question for a domain (requires an API key). */
  generate: (domain: DomainId) =>
    request<GenerateResult>("/generate", {
      method: "POST",
      body: JSON.stringify({ domain }),
    }),
};
