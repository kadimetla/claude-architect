/**
 * Home view - mode picker plus a progress snapshot.
 */
import { api } from "../api.js";
import { el, mount, pct } from "../dom.js";

export async function renderHome(container: HTMLElement): Promise<void> {
  const [health, progress] = await Promise.all([api.health(), api.progress()]);

  const modeCard = (href: string, title: string, body: string) =>
    el("a", { class: "card mode-card", href }, el("h3", {}, title), el("p", {}, body));

  mount(
    container,
    el("section", { class: "hero" },
      el("h1", {}, "CCA Cert Buddy"),
      el("p", {},
        "A study aid for the Claude Certified Architect - Foundations exam. " +
        "The app runs fully offline on a bank of " + String(health.bankSize) +
        " questions. Its own architecture - MCP client and server, an agentic " +
        "loop, a validator subagent - demonstrates the five exam domains it tests.",
      ),
    ),
    el("section", { class: "card-grid" },
      modeCard("#/quiz", "Quiz", "One question at a time, weighted toward your weak domains, with full rationale."),
      modeCard("#/exam", "Exam Simulation", "A timed 60-question mock exam, 120 minutes, scored 100-1000."),
      modeCard("#/dashboard", "Progress Dashboard", "Per-domain accuracy and your spaced-repetition review queue."),
      modeCard("#/generate", "Live Generation", "Generate a fresh question and watch the agentic loop run."),
    ),
    el("section", { class: "card" },
      el("h3", {}, "Your progress so far"),
      progress.overall.answered === 0
        ? el("p", {}, "No questions answered yet. Start with a quiz.")
        : el("p", {},
            `${progress.overall.answered} answered, ` +
            `${pct(progress.overall.accuracy)} correct overall. ` +
            (progress.weakDomains.length > 0
              ? `Weak domains: ${progress.weakDomains.join(", ")}.`
              : "No weak domains yet."),
          ),
    ),
  );
}
