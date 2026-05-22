/**
 * MCP client - the backend's connection to its own cca-study-mcp server.
 *
 * This is the Domain 2 showcase from the consumer side. The backend does NOT
 * hard-code the MCP server's capabilities: it spawns cca-study-mcp as a stdio
 * subprocess, then DISCOVERS its tools, resources, and prompts at runtime via
 * listTools / listResources / listPrompts. Discovered tools are converted to
 * Anthropic tool definitions and handed straight to the agentic loop.
 *
 * The client connects lazily on first use and is reused for the process
 * lifetime. The /api/mcp-info route reports whatever was discovered.
 */
import { Client } from "@modelcontextprotocol/sdk/client/index.js";
import { StdioClientTransport } from "@modelcontextprotocol/sdk/client/stdio.js";
import type { McpPrimitive } from "../../shared/types.js";
import { MCP_SERVER_SCRIPT } from "../../shared/paths.js";

/** An MCP tool discovered from the server, ready to pass to Claude. */
export interface DiscoveredTool {
  name: string;
  description: string;
  inputSchema: Record<string, unknown>;
}

let client: Client | null = null;
let discoveredPrimitives: McpPrimitive[] | null = null;

/**
 * Connects to cca-study-mcp (spawning it as a subprocess) and returns the
 * shared MCP client. Idempotent - subsequent calls reuse the connection.
 */
export async function getMcpClient(): Promise<Client> {
  if (client) return client;

  const transport = new StdioClientTransport({
    command: process.execPath, // the current Node binary
    args: ["--import", "tsx", MCP_SERVER_SCRIPT],
    stderr: "inherit",
  });

  const c = new Client({ name: "cca-cert-buddy-backend", version: "1.0.0" });
  await c.connect(transport);
  client = c;

  // Discover the full primitive surface and cache it for /api/mcp-info.
  await discoverPrimitives(c);
  return c;
}

/**
 * Lists every primitive from the server and caches the summary. Resources come
 * in two flavors - fixed URIs (listResources) and templated URIs
 * (listResourceTemplates) - and both are enumerated so the full MCP surface,
 * including cca://bank/{domain}, is visible.
 */
async function discoverPrimitives(c: Client): Promise<void> {
  const [tools, resources, resourceTemplates, prompts] = await Promise.all([
    c.listTools(),
    c.listResources(),
    c.listResourceTemplates(),
    c.listPrompts(),
  ]);

  const primitives: McpPrimitive[] = [];
  for (const t of tools.tools) {
    primitives.push({ kind: "tool", name: t.name, description: t.description ?? "" });
  }
  for (const r of resources.resources) {
    primitives.push({ kind: "resource", name: r.uri, description: r.description ?? "" });
  }
  for (const rt of resourceTemplates.resourceTemplates) {
    primitives.push({
      kind: "resource",
      name: rt.uriTemplate,
      description: rt.description ?? "",
    });
  }
  for (const p of prompts.prompts) {
    primitives.push({ kind: "prompt", name: p.name, description: p.description ?? "" });
  }
  discoveredPrimitives = primitives;
}

/** The discovered MCP tools in the shape the agentic loop passes to Claude. */
export async function getDiscoveredTools(): Promise<DiscoveredTool[]> {
  const c = await getMcpClient();
  const { tools } = await c.listTools();
  return tools.map((t) => ({
    name: t.name,
    description: t.description ?? "",
    inputSchema: t.inputSchema as Record<string, unknown>,
  }));
}

/**
 * Calls one MCP tool and returns its text content concatenated. The loop uses
 * this to execute a tool_use block and feed the result back to Claude.
 */
export async function callMcpTool(
  name: string,
  args: Record<string, unknown>,
): Promise<{ text: string; isError: boolean }> {
  const c = await getMcpClient();
  const result = await c.callTool({ name, arguments: args });

  const text = Array.isArray(result.content)
    ? result.content
        .filter((b): b is { type: "text"; text: string } => b.type === "text")
        .map((b) => b.text)
        .join("\n")
    : "";
  return { text, isError: result.isError === true };
}

/**
 * The MCP primitive surface for /api/mcp-info. Connects on demand so the route
 * reports a live discovery result rather than a hard-coded list.
 */
export async function describeMcpPrimitives(): Promise<McpPrimitive[]> {
  if (discoveredPrimitives) return discoveredPrimitives;
  try {
    await getMcpClient();
  } catch (err) {
    console.error("[mcp] discovery failed:", err instanceof Error ? err.message : err);
    return [];
  }
  return discoveredPrimitives ?? [];
}

/** Closes the MCP connection. Used by tests and graceful shutdown. */
export async function closeMcpClient(): Promise<void> {
  if (client) {
    await client.close();
    client = null;
    discoveredPrimitives = null;
  }
}
