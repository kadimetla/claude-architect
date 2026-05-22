/**
 * MCP server prompts - user-invocable templates of cca-study-mcp.
 *
 * Prompts are the third MCP primitive. When this server is registered in
 * Claude Code, these surface as slash commands (/quiz, /exam, /explain-domain),
 * which is the Domain 3 prompt-primitive teaching surface. Each prompt returns
 * a message that instructs the host model how to drive the study interaction.
 */
import type { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { z } from "zod";
import { DOMAIN_IDS } from "../shared/domains.js";

/** Registers all cca-study-mcp prompts on the given server. */
export function registerPrompts(server: McpServer): void {
  // --- /quiz ----------------------------------------------------------------
  server.registerPrompt(
    "quiz",
    {
      title: "Run a CCA-F quiz",
      description: "Start an interactive two-phase quiz on a CCA-F domain.",
      argsSchema: {
        domain: z
          .enum(DOMAIN_IDS as [string, ...string[]])
          .describe("Domain to quiz on (D1-D5). Omit for a weighted mix."),
      },
    },
    ({ domain }) => ({
      messages: [
        {
          role: "user",
          content: {
            type: "text",
            text:
              `Run a CCA-F practice quiz${domain ? ` focused on domain ${domain}` : ""}.\n\n` +
              `For each question:\n` +
              `1. Read cca://domains and cca://domain-ref/{id} to ground yourself.\n` +
              `2. Present ONE question - the scenario, the stem, and four options A-D. ` +
              `Do NOT reveal the answer. Stop and wait.\n` +
              `3. After the learner answers, call the score_answer tool, then deliver the ` +
              `result, the per-option rationale, and the domain reference link.\n` +
              `4. Offer the next question.`,
          },
        },
      ],
    }),
  );

  // --- /exam ----------------------------------------------------------------
  server.registerPrompt(
    "exam",
    {
      title: "Brief the CCA-F exam simulation",
      description: "Explain how the full 60-question timed exam simulation works.",
      argsSchema: {},
    },
    () => ({
      messages: [
        {
          role: "user",
          content: {
            type: "text",
            text:
              `Brief me on the CCA-F exam simulation. Read cca://domains for the weights, ` +
              `then explain: 60 questions, 120 minutes, a scaled score from 100 to 1000, ` +
              `passing at 720, and how the questions are split across the five domains.`,
          },
        },
      ],
    }),
  );

  // --- /explain-domain ------------------------------------------------------
  server.registerPrompt(
    "explain-domain",
    {
      title: "Explain a CCA-F domain",
      description: "Teach one CCA-F domain in depth with concrete examples.",
      argsSchema: {
        domain: z
          .enum(DOMAIN_IDS as [string, ...string[]])
          .describe("The domain to explain (D1-D5)."),
      },
    },
    ({ domain }) => ({
      messages: [
        {
          role: "user",
          content: {
            type: "text",
            text:
              `Teach me CCA-F domain ${domain}. Call the lookup_domain_ref tool for ${domain}, ` +
              `then explain its core concepts from first principles with concrete examples. ` +
              `Finish with the two or three points most likely to appear on the exam.`,
          },
        },
      ],
    }),
  );
}
