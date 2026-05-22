/**
 * MCP server tools - the model-callable actions of cca-study-mcp.
 *
 * Three tools, each a small, well-scoped interface with a strict input schema.
 * validate_question is deliberately built to return STRUCTURED errors (a list
 * of concrete issues) rather than prose - that is the Domain 2 "structured
 * error response" pattern the agentic loop depends on for its repair step.
 */
import type { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { z } from "zod";
import { getQuestion } from "../server/bank.js";
import { buildAnswerResult } from "../server/rationale.js";
import { readDomainRef } from "./domain-refs.js";
import { validateQuestion } from "../shared/question-validator.js";
import { DOMAIN_IDS } from "../shared/domains.js";

/** Registers all cca-study-mcp tools on the given server. */
export function registerTools(server: McpServer): void {
  // --- score_answer ---------------------------------------------------------
  server.registerTool(
    "score_answer",
    {
      title: "Score a practice answer",
      description:
        "Grade a chosen letter (A-D) against a bank question and return whether it is " +
        "correct plus per-option rationale. Use this to evaluate a learner's answer.",
      inputSchema: {
        questionId: z.number().int().describe("The question's global_n in the bank."),
        chosen: z.enum(["A", "B", "C", "D"]).describe("The letter the learner selected."),
      },
    },
    async ({ questionId, chosen }) => {
      const question = getQuestion(questionId);
      if (!question) {
        return {
          isError: true,
          content: [{ type: "text", text: `No question with global_n ${questionId}.` }],
        };
      }
      const result = buildAnswerResult(question, chosen);
      return {
        content: [{ type: "text", text: JSON.stringify(result, null, 2) }],
      };
    },
  );

  // --- validate_question ----------------------------------------------------
  server.registerTool(
    "validate_question",
    {
      title: "Validate a draft question",
      description:
        "Structurally validate a draft CCA-F question against the format and voice rules. " +
        "Returns a structured list of concrete issues - an empty list means it passed. " +
        "Use this after authoring a question to check it before delivery.",
      inputSchema: {
        draft: z
          .object({
            scenario: z.string(),
            situation: z.string(),
            question: z.string(),
            options: z.array(
              z.object({
                letter: z.string(),
                text: z.string(),
                correct: z.boolean(),
              }),
            ),
            correct: z.string(),
            explanation: z.string(),
            domain: z.string(),
            secondaryDomains: z.array(z.string()).optional(),
          })
          .describe("The draft question to validate."),
      },
    },
    async ({ draft }) => {
      const result = validateQuestion(draft);
      // A failed validation is NOT an MCP error - it is a successful tool call
      // that reports structured findings. isError is reserved for the tool
      // itself failing. The caller branches on result.ok.
      return {
        content: [{ type: "text", text: JSON.stringify(result, null, 2) }],
      };
    },
  );

  // --- lookup_domain_ref ----------------------------------------------------
  server.registerTool(
    "lookup_domain_ref",
    {
      title: "Look up a CCA-F domain reference",
      description:
        "Return the full reference notes for one CCA-F exam domain (D1-D5). " +
        "Use this to ground a question or an explanation in the domain's core concepts.",
      inputSchema: {
        domain: z
          .enum(DOMAIN_IDS as [string, ...string[]])
          .describe("The domain id: D1, D2, D3, D4, or D5."),
      },
    },
    async ({ domain }) => {
      const text = readDomainRef(domain as never);
      return { content: [{ type: "text", text }] };
    },
  );
}
