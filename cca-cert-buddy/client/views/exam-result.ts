/**
 * Exam result view - the scaled-score screen.
 */
import { el, mount, pct } from "../dom.js";
import { state } from "../state.js";
import { navigate } from "../router.js";

export function renderExamResult(container: HTMLElement): void {
  const result = state.lastExamResult;
  if (!result) {
    mount(
      container,
      el("section", { class: "card" },
        el("p", {}, "No exam result to show. Run an exam simulation first."),
        el("button", { class: "primary" }, "Go to Exam Sim"),
      ),
    );
    container.querySelector("button")?.addEventListener("click", () => navigate("/exam"));
    return;
  }

  const domainRows = result.perDomain.map((d) =>
    el("div", { class: "domain-row" },
      el("span", { class: "domain-name" }, `${d.domain} ${d.name}`),
      el("div", { class: "bar" },
        el("div", { class: "bar-fill", style: `width:${pct(d.accuracy)}` }),
      ),
      el("span", { class: "domain-stat" }, `${d.correct}/${d.answered}`),
    ),
  );

  mount(
    container,
    el("section", { class: "card result-card" },
      el("h2", {}, result.passed ? "Pass" : "Not yet a pass"),
      el("div", { class: result.passed ? "score pass" : "score fail" },
        String(result.scaledScore),
      ),
      el("p", { class: "score-detail" },
        `Scaled score (100-1000). Passing line is 720. ` +
        `Raw: ${result.rawCorrect} of ${result.total} correct.`,
      ),
      el("h4", {}, "By domain"),
      el("div", { class: "domain-bars" }, ...domainRows),
      el("button", { class: "primary" }, "Take another exam"),
    ),
  );
  container.querySelector("button")?.addEventListener("click", () => navigate("/exam"));
}
