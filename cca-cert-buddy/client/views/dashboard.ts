/**
 * Progress dashboard - per-domain accuracy and the SM-2 review queue.
 */
import { api } from "../api.js";
import { el, mount, pct } from "../dom.js";

export async function renderDashboard(container: HTMLElement): Promise<void> {
  const progress = await api.progress();

  const domainBars = progress.perDomain.map((d) => {
    const weak = progress.weakDomains.includes(d.domain);
    return el("div", { class: "domain-row" },
      el("span", { class: "domain-name" },
        `${d.domain} ${d.name}`,
        weak ? el("span", { class: "weak-tag" }, "weak") : null,
      ),
      el("div", { class: "bar" },
        el("div", { class: "bar-fill", style: `width:${pct(d.accuracy)}` }),
      ),
      el("span", { class: "domain-stat" },
        d.answered === 0 ? "no data" : `${pct(d.accuracy)} (${d.correct}/${d.answered})`,
      ),
    );
  });

  const reviewItems =
    progress.reviewQueue.length === 0
      ? [el("p", { class: "muted" }, "Nothing due for review. Answer some questions to build a schedule.")]
      : progress.reviewQueue.map((r) =>
          el("li", {},
            el("strong", {}, `${r.domain} ${r.name}`),
            ` - due ${r.dueDate}, next interval ${r.intervalDays} day(s)`,
          ),
        );

  mount(
    container,
    el("section", { class: "card" },
      el("h2", {}, "Progress"),
      el("p", { class: "muted" },
        progress.overall.answered === 0
          ? "No answers recorded yet."
          : `${progress.overall.answered} questions answered, ${pct(progress.overall.accuracy)} overall.`,
      ),
      el("div", { class: "domain-bars" }, ...domainBars),
    ),
    el("section", { class: "card" },
      el("h3", {}, "Spaced-repetition review queue"),
      el("p", { class: "muted" },
        "Domains are scheduled with the SM-2 algorithm. A missed domain resurfaces tomorrow; " +
        "a mastered one is pushed further out.",
      ),
      el("ul", { class: "review-queue" }, ...reviewItems),
    ),
  );
}
