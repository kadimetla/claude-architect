/**
 * Lazy Anthropic client factory.
 *
 * The app is fully usable on the pre-generated question bank with NO key.
 * Only the optional live-generation features touch the Claude API, so the
 * client is created lazily and the absence of a key is a friendly capability
 * gate, never a crash.
 */
import Anthropic from "@anthropic-ai/sdk";

/** Default model for agentic work - cost-efficient, production-grade tool use. */
export const DEFAULT_MODEL = "claude-haiku-4-5";

/**
 * Model for question authoring. Generating exam-realistic items with correct
 * distractors and rationale benefits measurably from deeper reasoning, so the
 * generator pays for Sonnet here. (Per the course model policy: Haiku by
 * default, Sonnet only where reasoning depth lifts behavior, never Opus.)
 */
export const AUTHORING_MODEL = "claude-sonnet-4-6";

let client: Anthropic | null = null;

/** True if an API key is configured - drives the liveGenAvailable flag. */
export function liveGenAvailable(): boolean {
  return Boolean(process.env.ANTHROPIC_API_KEY);
}

/**
 * Returns the shared Anthropic client, or throws a clear error if no key is
 * set. Callers in optional-feature paths should check liveGenAvailable() first
 * and return a friendly 503 rather than letting this throw.
 */
export function getAnthropic(): Anthropic {
  if (!liveGenAvailable()) {
    throw new Error(
      "ANTHROPIC_API_KEY is not set. Live generation is disabled. " +
        "Copy .env.example to .env and add a key from https://console.anthropic.com/",
    );
  }
  if (!client) {
    client = new Anthropic({ apiKey: process.env.ANTHROPIC_API_KEY });
  }
  return client;
}

/** Anthropic API pricing per million tokens, used for cost estimates. */
export const PRICING: Record<string, { input: number; output: number }> = {
  "claude-haiku-4-5": { input: 1.0, output: 5.0 },
  "claude-sonnet-4-6": { input: 3.0, output: 15.0 },
};

/** Estimates the USD cost of a call from its token usage. */
export function estimateCost(model: string, inputTokens: number, outputTokens: number): number {
  const p = PRICING[model] ?? PRICING[DEFAULT_MODEL]!;
  return (inputTokens / 1_000_000) * p.input + (outputTokens / 1_000_000) * p.output;
}
