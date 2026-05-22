/**
 * The Express app - routes and middleware, with no listen().
 *
 * Separated from index.ts so tests can import a ready-to-exercise app via
 * supertest without binding a port. index.ts adds the listen() call.
 */
import express from "express";
import { existsSync } from "node:fs";
import { join } from "node:path";

import { PROJECT_ROOT } from "../shared/paths.js";
import { loadBank } from "./bank.js";
import { getDb } from "./db.js";
import { metaRouter } from "./routes/meta.js";
import { questionsRouter } from "./routes/questions.js";
import { answersRouter } from "./routes/answers.js";
import { progressRouter } from "./routes/progress.js";
import { examRouter } from "./routes/exam.js";
import { generateRouter } from "./routes/generate.js";

/** Builds the configured Express app. Loads the bank and database eagerly. */
export function createApp(): express.Express {
  // Fail fast if the bank or database cannot be brought up - better a loud
  // crash now than a confusing 500 on the first request.
  loadBank();
  getDb();

  const app = express();
  app.use(express.json({ limit: "256kb" }));

  // REST API.
  app.use("/api", metaRouter);
  app.use("/api/questions", questionsRouter);
  app.use("/api/answers", answersRouter);
  app.use("/api/progress", progressRouter);
  app.use("/api/exam", examRouter);
  app.use("/api/generate", generateRouter);

  // Serve the built SPA in production. In dev this directory does not exist
  // (the Vite dev server handles the frontend instead), so the guard skips it.
  const clientDist = join(PROJECT_ROOT, "dist", "client");
  if (existsSync(clientDist)) {
    app.use(express.static(clientDist));
    // SPA fallback: any non-API GET returns index.html so the hash router works.
    app.get(/^(?!\/api).*/, (_req, res) => {
      res.sendFile(join(clientDist, "index.html"));
    });
  }

  // Centralized error handler - Express 5 forwards async rejections here.
  app.use(
    (err: unknown, _req: express.Request, res: express.Response, _next: express.NextFunction) => {
      const message = err instanceof Error ? err.message : "Internal server error.";
      console.error("[error]", message);
      res.status(500).json({ error: message });
    },
  );

  return app;
}
