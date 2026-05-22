/**
 * MCP server resources - the read-only context cca-study-mcp exposes.
 *
 * Resources are how an MCP client loads grounding material before it acts.
 * Two are fixed URIs (cca://domains, cca://progress); two are templated
 * (cca://bank/{domain}, cca://domain-ref/{id}) so the client can address any
 * domain. Together they cover the static-context and per-parameter-context
 * shapes of the MCP resource primitive.
 */
import {
  McpServer,
  ResourceTemplate,
} from "@modelcontextprotocol/sdk/server/mcp.js";
import { DOMAINS } from "../shared/domains.js";
import { questionsForDomain, toPhase1 } from "../server/bank.js";
import { getDb } from "../server/db.js";
import { readDomainRef } from "./domain-refs.js";
import type { DomainId } from "../shared/types.js";

/** Registers all cca-study-mcp resources on the given server. */
export function registerResources(server: McpServer): void {
  // --- cca://domains - the exam blueprint ----------------------------------
  server.registerResource(
    "domains",
    "cca://domains",
    {
      title: "CCA-F exam domains",
      description: "The five CCA-F domains with their exam weight percentages.",
      mimeType: "application/json",
    },
    async (uri) => ({
      contents: [
        {
          uri: uri.href,
          mimeType: "application/json",
          text: JSON.stringify(DOMAINS, null, 2),
        },
      ],
    }),
  );

  // --- cca://progress - live progress from the local database --------------
  server.registerResource(
    "progress",
    "cca://progress",
    {
      title: "Study progress",
      description: "Per-domain answered/correct tallies from the local progress database.",
      mimeType: "application/json",
    },
    async (uri) => {
      const rows = getDb()
        .prepare(
          `SELECT domain, COUNT(*) AS answered, SUM(correct) AS correct
           FROM sessions GROUP BY domain`,
        )
        .all();
      return {
        contents: [
          { uri: uri.href, mimeType: "application/json", text: JSON.stringify(rows, null, 2) },
        ],
      };
    },
  );

  // --- cca://bank/{domain} - questions for one domain ----------------------
  server.registerResource(
    "bank",
    new ResourceTemplate("cca://bank/{domain}", { list: undefined }),
    {
      title: "Question bank by domain",
      description: "The bank's questions for a given domain, in Phase 1 shape (no answers).",
      mimeType: "application/json",
    },
    async (uri, { domain }) => {
      const questions = questionsForDomain(domain as DomainId).map(toPhase1);
      return {
        contents: [
          {
            uri: uri.href,
            mimeType: "application/json",
            text: JSON.stringify(questions, null, 2),
          },
        ],
      };
    },
  );

  // --- cca://domain-ref/{id} - full domain reference notes -----------------
  server.registerResource(
    "domain-ref",
    new ResourceTemplate("cca://domain-ref/{id}", { list: undefined }),
    {
      title: "CCA-F domain reference",
      description: "The full one-page reference notes for a CCA-F domain.",
      mimeType: "text/markdown",
    },
    async (uri, { id }) => ({
      contents: [
        {
          uri: uri.href,
          mimeType: "text/markdown",
          text: readDomainRef(id as DomainId),
        },
      ],
    }),
  );
}
