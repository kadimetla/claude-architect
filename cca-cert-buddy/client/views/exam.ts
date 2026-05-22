/**
 * Exam simulation view - a timed 60-question mock exam.
 *
 * 120-minute countdown, a question navigator grid, and auto-submit when the
 * clock reaches zero. Answers are held client-side until submission, then
 * scored in one call. Mirrors the real CCA-F exam shape.
 */
import { api } from "../api.js";
import { el, mount, clock } from "../dom.js";
import { state } from "../state.js";
import { navigate } from "../router.js";

export async function renderExam(container: HTMLElement): Promise<void> {
  // Resume an in-progress exam, or start a fresh one.
  if (!state.activeExam) {
    const started = await api.startExam();
    state.activeExam = {
      ...started,
      answers: new Map(),
      deadline: Date.now() + started.durationSec * 1000,
    };
  }
  const exam = state.activeExam;
  let current = 0;

  const timerEl = el("span", { class: "timer" }, "");
  const navGrid = el("div", { class: "nav-grid" });
  const questionArea = el("div", { class: "question-area" });

  /** Renders the question at index `current`. */
  function showCurrent(): void {
    const q = exam.questions[current]!;
    const chosen = exam.answers.get(q.global_n) ?? null;

    const options = q.options.map((opt) => {
      const btn = el("button", { class: "option", "data-letter": opt.letter },
        el("span", { class: "option-letter" }, opt.letter),
        el("span", { class: "option-text" }, opt.text),
      );
      if (chosen === opt.letter) btn.classList.add("selected");
      btn.addEventListener("click", () => {
        exam.answers.set(q.global_n, opt.letter);
        showCurrent();
        renderNav();
      });
      return btn;
    });

    mount(
      questionArea,
      el("div", { class: "question-meta" },
        el("span", { class: "badge" }, `Question ${current + 1} of ${exam.questions.length}`),
        el("span", { class: "badge" }, `Domain ${q.domain}`),
      ),
      el("p", { class: "situation" }, q.situation),
      el("p", { class: "stem" }, q.question),
      el("div", { class: "options" }, ...options),
      el("div", { class: "exam-controls" },
        el("button", { class: "secondary", ...(current === 0 ? { disabled: "true" } : {}) }, "Previous"),
        el("button", { class: "secondary", ...(current === exam.questions.length - 1 ? { disabled: "true" } : {}) }, "Next"),
      ),
    );
    const [prev, next] = questionArea.querySelectorAll(".exam-controls button");
    prev?.addEventListener("click", () => { current--; showCurrent(); renderNav(); });
    next?.addEventListener("click", () => { current++; showCurrent(); renderNav(); });
  }

  /** Renders the navigator grid - answered cells are marked. */
  function renderNav(): void {
    mount(
      navGrid,
      ...exam.questions.map((q, i) => {
        const cell = el("button", { class: "nav-cell" }, String(i + 1));
        if (exam.answers.has(q.global_n)) cell.classList.add("answered");
        if (i === current) cell.classList.add("current");
        cell.addEventListener("click", () => { current = i; showCurrent(); renderNav(); });
        return cell;
      }),
    );
  }

  /** Scores the exam and routes to the result view. */
  async function submitExam(): Promise<void> {
    clearInterval(ticker);
    const answers = [...exam.answers.entries()].map(([questionId, chosen]) => ({
      questionId,
      chosen,
    }));
    const result = await api.scoreExam(exam.examId, answers);
    state.lastExamResult = result;
    state.activeExam = null;
    navigate("/exam-result");
  }

  // The countdown. Renders immediately, then ticks every second and
  // auto-submits at zero.
  function tick(): void {
    const remaining = Math.round((exam.deadline - Date.now()) / 1000);
    timerEl.textContent = clock(remaining);
    timerEl.classList.toggle("urgent", remaining <= 300);
    if (remaining <= 0) void submitExam();
  }
  tick();
  const ticker = window.setInterval(tick, 1000);

  const submitBtn = el("button", { class: "primary" }, "Submit exam");
  submitBtn.addEventListener("click", () => void submitExam());

  mount(
    container,
    el("section", { class: "card exam-card" },
      el("div", { class: "exam-header" },
        el("h2", {}, "Exam Simulation"),
        timerEl,
      ),
      navGrid,
      questionArea,
      submitBtn,
    ),
  );
  showCurrent();
  renderNav();
}
