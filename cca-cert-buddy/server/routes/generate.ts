/**
 * Live question generation (optional, requires an API key).
 *
 * POST /api/generate - generate one fresh exam-realistic question for a domain
 * by running the agent core: an MCP client drives an agentic loop that calls
 * Claude with MCP-discovered tools, and a validator subagent checks the draft.
 *
 * The response includes the full agent trace - every loop iteration, each
 * stop_reason, every MCP tool call - so the agent-trace view can render the
 * Domain 1 / 2 / 4 patterns live.
 */
import { Router } from "express";
import { z } from "zod";
import { DOMAIN_IDS } from "../../shared/domains.js";
import { liveGenAvailable } from "../anthropic.js";
import { generateQuestion } from "../agent/generate.js";

export const generateRouter: Router = Router();

const generateBody = z.object({
  domain: z.enum(DOMAIN_IDS as [string, ...string[]]),
});

/** POST /api/generate - run the agent core to author one question. */
generateRouter.post("/", async (req, res, next) => {
  if (!liveGenAvailable()) {
    res.status(503).json({
      error:
        "Live generation is disabled. Set ANTHROPIC_API_KEY in .env to enable it. " +
        "The quiz and exam modes work fully without a key.",
    });
    return;
  }

  const parsed = generateBody.safeParse(req.body);
  if (!parsed.success) {
    res.status(400).json({ error: parsed.error.issues[0]?.message ?? "Invalid body." });
    return;
  }

  try {
    const result = await generateQuestion(parsed.data.domain as never, { persist: false });
    res.json(result);
  } catch (err) {
    next(err);
  }
});
