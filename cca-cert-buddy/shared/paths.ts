/**
 * Path anchors.
 *
 * The code runs two ways - as TypeScript via tsx (modules under server/,
 * mcp-server/) and as compiled JavaScript (modules under dist/server/). A
 * relative "../data" resolves differently in each. To keep one correct answer,
 * this module walks up from itself until it finds the package.json, which is
 * always the project root, and derives every shared path from there.
 */
import { existsSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

/** Walks up until a directory containing package.json is found. */
function findProjectRoot(): string {
  let dir = dirname(fileURLToPath(import.meta.url));
  for (let i = 0; i < 10; i++) {
    if (existsSync(join(dir, "package.json"))) return dir;
    const parent = dirname(dir);
    if (parent === dir) break;
    dir = parent;
  }
  throw new Error("Could not locate the project root (no package.json found above shared/).");
}

/** Absolute path to the cca-cert-buddy project root. */
export const PROJECT_ROOT: string = findProjectRoot();

/** The committed question bank. */
export const BANK_PATH: string = join(PROJECT_ROOT, "data", "question-bank.json");

/** The runtime SQLite database (gitignored). */
export const DB_PATH: string = join(PROJECT_ROOT, ".data", "progress.db");

/** The parent claude-architect repo root - one level above the project root. */
export const REPO_ROOT: string = dirname(PROJECT_ROOT);

/** The cca-study-mcp server entry script. */
export const MCP_SERVER_SCRIPT: string = join(PROJECT_ROOT, "mcp-server", "index.ts");
