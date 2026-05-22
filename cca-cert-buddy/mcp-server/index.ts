/**
 * cca-study-mcp - the CCA Cert Buddy MCP server.
 *
 * A standalone stdio MCP server exposing the study domain through all three
 * MCP primitives: tools, resources, and prompts. It is the Domain 2 + 3
 * showcase, and it runs three ways:
 *   1. spawned by the backend's MCP client (server/agent/mcp-client.ts)
 *   2. registered in the repo .mcp.json so Claude Code can use it
 *   3. driven under the MCP Inspector for hands-on exploration
 *
 * Run directly with: npm run mcp
 */
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { loadBank } from "../server/bank.js";
import { getDb } from "../server/db.js";
import { registerTools } from "./tools.js";
import { registerResources } from "./resources.js";
import { registerPrompts } from "./prompts.js";

/** Builds the configured MCP server (without connecting a transport). */
export function createMcpServer(): McpServer {
  // The MCP server reads the same bank and database the web backend uses.
  loadBank();
  getDb();

  const server = new McpServer({
    name: "cca-study-mcp",
    version: "1.0.0",
  });

  registerTools(server);
  registerResources(server);
  registerPrompts(server);

  return server;
}

/** Entry point: connect the server to a stdio transport and run. */
export async function runMcpServer(): Promise<void> {
  const server = createMcpServer();
  const transport = new StdioServerTransport();
  await server.connect(transport);
  // Note: log to stderr only - stdout is the MCP protocol channel.
  console.error("cca-study-mcp running on stdio.");
}

// This file is the entry point for `npm run mcp` and is also the script the
// backend's MCP client spawns as a subprocess. In both cases it should run.
// It is never imported for its side effects, so an unconditional run is safe.
runMcpServer().catch((err) => {
  console.error("cca-study-mcp failed to start:", err);
  process.exit(1);
});
