/**
 * Meta routes: health probe, the domain blueprint, and discovered MCP
 * primitives. These power the home page, the dashboard, and the About /
 * agent-trace teaching views.
 */
import { Router } from "express";
import type { HealthInfo, McpPrimitive } from "../../shared/types.js";
import { DOMAINS } from "../../shared/domains.js";
import { bankSize } from "../bank.js";
import { liveGenAvailable } from "../anthropic.js";
import { describeMcpPrimitives } from "../agent/mcp-client.js";

export const metaRouter: Router = Router();

/** GET /api/health - capability probe for the SPA. */
metaRouter.get("/health", (_req, res) => {
  const info: HealthInfo = {
    status: "ok",
    bankSize: bankSize(),
    liveGenAvailable: liveGenAvailable(),
  };
  res.json(info);
});

/** GET /api/domains - the five CCA-F domains with exam weights. */
metaRouter.get("/domains", (_req, res) => {
  res.json(DOMAINS);
});

/**
 * GET /api/mcp-info - the MCP primitives the backend's MCP client discovered
 * from cca-study-mcp. Returns a static fallback list if the MCP server has not
 * been contacted (for example, before any live-generation call).
 */
metaRouter.get("/mcp-info", async (_req, res) => {
  const primitives: McpPrimitive[] = await describeMcpPrimitives();
  res.json(primitives);
});
