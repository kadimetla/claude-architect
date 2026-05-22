/**
 * Quiz view - the two-phase study loop.
 *
 * Phase 1: show the scenario, stem, and four options. The learner picks one.
 * Phase 2: after submission, show the result, per-option rationale, and a link
 * to the domain reference. Then offer the next question.
 *
 * The Phase 1 / Phase 2 split mirrors the cert-buddy interaction the course
 * teaches: never reveal the answer before the learner commits.
 */
import { api } from "../api.js";
import { el, mount } from "../dom.js";
import type { Phase1Question } from "../../shared/types.js";

export async function renderQuiz(container: HTMLElement): Promise<void> {
  await showQuestion(container);
}

async function showQuestion(container: HTMLElement): Promise<void> {
  const q: Phase1Question = await api.quizQuestion();
  const startedAt = Date.now();
  let chosen: string | null = null;

  const optionButtons = q.options.map((opt) =>
    el("button", { class: "option", "data-letter": opt.letter },
      el("span", { class: "option-letter" }, opt.letter),
      el("span", { class: "option-text" }, opt.text),
    ),
  );

  const submitBtn = el("button", { class: "primary", disabled: "true" }, "Submit answer");
  const phase2 = el("div", { class: "phase2" });

  for (const btn of optionButtons) {
    btn.addEventListener("click", () => {
      if (chosen && phase2.childElementCount > 0) return; // locked after submit
      chosen = btn.getAttribute("data-letter");
      optionButtons.forEach((b) => b.classList.toggle("selected", b === btn));
      submitBtn.removeAttribute("disabled");
    });
  }

  submitBtn.addEventListener("click", async () => {
    if (!chosen) return;
    submitBtn.setAttribute("disabled", "true");
    const result = await api.recordAnswer({
      questionId: q.global_n,
      chosen,
      mode: "quiz",
      msElapsed: Date.now() - startedAt,
    });

    // Mark options correct/incorrect.
    for (const btn of optionButtons) {
      const letter = btn.getAttribute("data-letter")!;
      if (letter === result.correctLetter) btn.classList.add("correct");
      else if (letter === chosen) btn.classList.add("incorrect");
      btn.setAttribute("disabled", "true");
    }

    mount(
      phase2,
      el("div", { class: result.correct ? "verdict pass" : "verdict fail" },
        result.correct ? "Correct" : `Incorrect - the answer is ${result.correctLetter}`,
      ),
      el("h4", {}, "Why each option"),
      el("ul", { class: "rationale" },
        ...q.options.map((opt) =>
          el("li", {},
            el("strong", {}, `${opt.letter}. `),
            result.perOption[opt.letter] ?? "",
          ),
        ),
      ),
      el("p", { class: "domain-ref" },
        `Domain ${q.domain} reference: `,
        el("code", {}, result.domainRef),
      ),
      el("button", { class: "primary next-btn" }, "Next question"),
    );
    phase2
      .querySelector(".next-btn")!
      .addEventListener("click", () => void showQuestion(container));
  });

  mount(
    container,
    el("section", { class: "card question-card" },
      el("div", { class: "question-meta" },
        el("span", { class: "badge" }, `Domain ${q.domain}`),
        el("span", { class: "scenario" }, q.scenario),
      ),
      el("p", { class: "situation" }, q.situation),
      el("p", { class: "stem" }, q.question),
      el("div", { class: "options" }, ...optionButtons),
      submitBtn,
      phase2,
    ),
  );
}
