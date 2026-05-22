/**
 * Agent-trace renderer.
 *
 * Renders a GenerateResult's agentic loop as a visible step list: each
 * iteration, the stop_reason that drove it, the action taken, and any MCP tool
 * calls. This is the Domain 1 / 2 / 4 teaching surface made literal - the loop
 * is shown, not hidden. Imported by the generate view.
 */
import { el } from "../dom.js";
import type { GenerateResult } from "../../shared/types.js";

/** Builds the trace section for a generation result. */
export function renderAgentTrace(result: GenerateResult): HTMLElement {
  const steps = result.trace.map((step) =>
    el("li", { class: "trace-step" },
      el("div", { class: "trace-head" },
        el("span", { class: "trace-iter" }, `Step ${step.iteration}`),
        el("span", { class: `stop-reason sr-${step.stopReason}` }, step.stopReason),
      ),
      el("p", { class: "trace-action" }, step.action),
      step.toolCalls.length > 0
        ? el("ul", { class: "trace-tools" },
            ...step.toolCalls.map((tc) =>
              el("li", { class: tc.ok ? "tool-ok" : "tool-err" },
                el("code", {}, tc.name),
                ` ${tc.ok ? "ok" : "error"} - ${tc.summary}`,
              ),
            ),
          )
        : null,
    ),
  );

  const verdict = result.validatorVerdict;

  return el("div", { class: "agent-trace" },
    el("h4", {}, "Agentic loop trace"),
    el("p", { class: "muted" },
      "Each step is one turn of the agentic loop. The stop_reason badge is the " +
      "branch the loop took - the Domain 1 pattern the CCA-F exam tests.",
    ),
    el("ol", { class: "trace-list" }, ...steps),
    el("div", { class: verdict.ok ? "verdict pass" : "verdict fail" },
      el("strong", {}, "Validator subagent: "),
      verdict.ok
        ? `accepted after ${verdict.repairRounds} repair round(s).`
        : `rejected after ${verdict.repairRounds} repair round(s).`,
    ),
    verdict.issues.length > 0
      ? el("ul", { class: "rationale" }, ...verdict.issues.map((i) => el("li", {}, i)))
      : null,
    el("p", { class: "muted usage" },
      `Tokens: ${result.usage.inputTokens} in, ${result.usage.outputTokens} out. ` +
      `Estimated cost: $${result.usage.estimatedCostUsd.toFixed(4)}.`,
    ),
  );
}
