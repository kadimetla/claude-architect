/**
 * SPA entry point - registers every view with the router and starts it.
 */
import "./styles.css";
import { route, startRouter } from "./router.js";
import { renderHome } from "./views/home.js";
import { renderQuiz } from "./views/quiz.js";
import { renderExam } from "./views/exam.js";
import { renderExamResult } from "./views/exam-result.js";
import { renderDashboard } from "./views/dashboard.js";
import { renderGenerate } from "./views/generate.js";
import { renderAbout } from "./views/about-domains.js";

route("/", renderHome);
route("/quiz", renderQuiz);
route("/exam", renderExam);
route("/exam-result", renderExamResult);
route("/dashboard", renderDashboard);
route("/generate", renderGenerate);
route("/about", renderAbout);

startRouter();
