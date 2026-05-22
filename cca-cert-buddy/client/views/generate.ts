/**
 * Live generation view.
 *
 * Pick a domain, generate one fresh question through the agent core, and see
 * both the question and the full agentic-loop trace. Requires an API key; the
 * view degrades to a friendly notice when none is configured.
 */
import { api } from "../api.js";
import { el, mount } from "../dom.js";
import { state } from "../state.js";
import { renderAgentTrace } from "./agent-trace.js";
import type { Domain, GenerateResult } from "../../shared/types.js";

export async function renderGenerate(container: HTMLElement): Promise<void> {
  const [health, domains] = await Promise.all([api.health(), api.domains()]);

  if (!health.liveGenAvailable) {
    mount(
      container,
      el("section", { class: "card" },
        el("h2", {}, "Live generation"),
        el("p", {},
          "Live generation needs an Anthropic API key. Copy .env.example to .env, " +
          "add a key from console.anthropic.com, and restart the server. " +
          "Quiz and exam modes work fully without one.",
        ),
      ),
    );
    return;
  }

  const select = el("select", { class: "domain-select" },
    ...domains.map((d: Domain) => el("option", { value: d.id }, `${d.id} - ${d.name}`)),
  );
  const genBtn = el("button", { class: "primary" }, "Generate a question");
  const output = el("div", { class: "generate-output" });

  genBtn.addEventListener("click", async () => {
    genBtn.setAttribute("disabled", "true");
    mount(output, el("p", { class: "loading" }, "Running the agentic loop - this calls the API and may take a few seconds..."));
    try {
      const result: GenerateResult = await api.generate(select.value as never);
      state.lastGeneration = result;
      renderResult(output, result);
    } catch (err) {
      mount(output, el("p", { class: "error" }, err instanceof Error ? err.message : String(err)));
    } finally {
      genBtn.removeAttribute("disabled");
    }
  });

  mount(
    container,
    el("section", { class: "card" },
      el("h2", {}, "Live generation"),
      el("p", { class: "muted" },
        "Generating one question runs the whole stack: an agentic loop, MCP tool " +
        "discovery, forced structured output, and a validator subagent. The trace below " +
        "shows every step.",
      ),
      el("div", { class: "generate-controls" }, select, genBtn),
    ),
    output,
  );
}

/** Renders a finished generation: the question, then its agent trace. */
function renderResult(container: HTMLElement, result: GenerateResult): void {
  const q = result.question;
  mount(
    container,
    el("section", { class: "card question-card" },
      el("div", { class: "question-meta" },
        el("span", { class: "badge" }, `Domain ${q.domain}`),
        el("span", { class: "badge" }, "freshly generated"),
        el("span", { class: "scenario" }, q.scenario),
      ),
      el("p", { class: "situation" }, q.situation),
      el("p", { class: "stem" }, q.question),
      el("ul", { class: "options static" },
        ...q.options.map((opt) =>
          el("li", { class: opt.letter === q.correct ? "correct" : "" },
            el("strong", {}, `${opt.letter}. `),
            opt.text,
          ),
        ),
      ),
      el("p", { class: "domain-ref" }, el("strong", {}, "Explanation: "), q.explanation),
    ),
    el("section", { class: "card" }, renderAgentTrace(result)),
  );
}
