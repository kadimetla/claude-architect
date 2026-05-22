/**
 * About view - how this app demonstrates the five CCA-F domains.
 *
 * The teaching payoff: every CCA-F domain maps to a real, running layer of
 * this app. This view states each mapping explicitly and lists the live MCP
 * primitives discovered from cca-study-mcp.
 */
import { api } from "../api.js";
import { el, mount } from "../dom.js";
import type { McpPrimitive } from "../../shared/types.js";

interface DomainMapping {
  id: string;
  name: string;
  how: string;
  files: string;
}

const MAPPINGS: DomainMapping[] = [
  {
    id: "D1",
    name: "Agentic Architecture & Orchestration",
    how:
      "server/agent/loop.ts is a real agentic loop with an explicit switch over every " +
      "stop_reason. server/agent/subagent-validator.ts is a coordinator-subagent pattern: " +
      "the validator runs in an isolated context and the loop decides repair-or-accept from " +
      "its structured verdict.",
    files: "server/agent/loop.ts, server/agent/subagent-validator.ts",
  },
  {
    id: "D2",
    name: "Tool Design & MCP Integration",
    how:
      "mcp-server/ is a standalone MCP server exposing tools, resources, and prompts. Its " +
      "validate_question tool returns structured errors, not prose. The backend is a real MCP " +
      "client that discovers the server's primitives at runtime rather than hard-coding them.",
    files: "mcp-server/*, server/agent/mcp-client.ts",
  },
  {
    id: "D3",
    name: "Claude Code Configuration & Workflows",
    how:
      "cca-study-mcp ships MCP prompts (/quiz, /exam, /explain-domain) that surface as slash " +
      "commands when the server is registered in Claude Code. The sub-project carries its own " +
      "CLAUDE.md, and the seed-vs-generate split mirrors direct execution vs deliberate, " +
      "reviewed work.",
    files: "mcp-server/prompts.ts, CLAUDE.md",
  },
  {
    id: "D4",
    name: "Prompt Engineering & Structured Output",
    how:
      "The generator forces emit_question via tool_choice, so output is schema-shaped, never " +
      "free text. The validate-and-repair loop is the Domain 4 retry pattern. The authoring " +
      "system prompt states explicit success criteria and what not to do.",
    files: "server/agent/generate.ts",
  },
  {
    id: "D5",
    name: "Context Management & Reliability",
    how:
      "Each model call receives only the relevant domain reference - focused, isolated context " +
      "rather than the whole transcript. A near-duplicate guard and confidence-calibrated SM-2 " +
      "scoring (fast-correct vs slow-correct) demonstrate reliability.",
    files: "shared/question-validator.ts, server/sm2.ts",
  },
];

export async function renderAbout(container: HTMLElement): Promise<void> {
  let primitives: McpPrimitive[] = [];
  try {
    primitives = await api.mcpInfo();
  } catch {
    // The MCP server may be unreachable; the domain mappings still render.
  }

  const domainCards = MAPPINGS.map((m) =>
    el("div", { class: "card domain-card" },
      el("h3", {}, `${m.id} - ${m.name}`),
      el("p", {}, m.how),
      el("p", { class: "domain-ref" }, el("strong", {}, "Code: "), el("code", {}, m.files)),
    ),
  );

  const primitiveList = primitives.map((p) =>
    el("li", {},
      el("span", { class: `badge badge-${p.kind}` }, p.kind),
      " ",
      el("code", {}, p.name),
      p.description ? ` - ${p.description}` : "",
    ),
  );

  mount(
    container,
    el("section", { class: "card" },
      el("h2", {}, "How this app demonstrates the CCA-F domains"),
      el("p", {},
        "CCA Cert Buddy is not a CRUD app with SDK demos bolted on. Every load-bearing layer " +
        "is itself an exam-domain demonstration. The five mappings below are real code paths " +
        "you can read.",
      ),
    ),
    el("section", { class: "card-grid" }, ...domainCards),
    el("section", { class: "card" },
      el("h3", {}, "Live MCP primitives"),
      el("p", { class: "muted" },
        primitives.length > 0
          ? `Discovered from the cca-study-mcp server at runtime - ${primitives.length} primitives.`
          : "The cca-study-mcp server was not reachable. Run the backend to discover its primitives.",
      ),
      primitiveList.length > 0 ? el("ul", { class: "primitive-list" }, ...primitiveList) : null,
    ),
  );
}
