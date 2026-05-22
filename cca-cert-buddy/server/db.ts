/**
 * SQLite persistence layer.
 *
 * A single better-sqlite3 connection, opened lazily and reused. The synchronous
 * API fits the simple request handlers in this app - no connection pool, no
 * async ceremony. The database file lives in .data/ (gitignored), so each
 * learner's progress is local and private.
 *
 * Schema is initialized idempotently on first access (CREATE TABLE IF NOT
 * EXISTS), and the five domain rows are seeded so the dashboard and review
 * queue never have to handle a missing row.
 */
import Database from "better-sqlite3";
import { mkdirSync } from "node:fs";
import { dirname } from "node:path";
import { DOMAIN_IDS } from "../shared/domains.js";
import { DB_PATH } from "../shared/paths.js";

let db: Database.Database | null = null;

/** Returns the shared connection, initializing schema on first call. */
export function getDb(): Database.Database {
  if (db) return db;

  mkdirSync(dirname(DB_PATH), { recursive: true });
  db = new Database(DB_PATH);
  // WAL improves concurrent read/write and survives a hard process kill better.
  db.pragma("journal_mode = WAL");
  initSchema(db);
  seedDomains(db);
  return db;
}

function initSchema(conn: Database.Database): void {
  conn.exec(`
    CREATE TABLE IF NOT EXISTS sessions (
      id          INTEGER PRIMARY KEY AUTOINCREMENT,
      ts          TEXT    NOT NULL,
      mode        TEXT    NOT NULL,
      exam_id     TEXT,
      question_id INTEGER NOT NULL,
      domain      TEXT    NOT NULL,
      chosen      TEXT    NOT NULL,
      correct     INTEGER NOT NULL,
      ms_elapsed  INTEGER
    );

    CREATE TABLE IF NOT EXISTS domains_sm2 (
      domain        TEXT PRIMARY KEY,
      interval      REAL NOT NULL DEFAULT 1,
      ease_factor   REAL NOT NULL DEFAULT 2.5,
      repetitions   INTEGER NOT NULL DEFAULT 0,
      last_reviewed TEXT,
      due_date      TEXT
    );

    CREATE TABLE IF NOT EXISTS exam_runs (
      id           TEXT PRIMARY KEY,
      started_ts   TEXT NOT NULL,
      finished_ts  TEXT,
      question_ids TEXT NOT NULL,
      raw_correct  INTEGER,
      scaled_score INTEGER,
      passed       INTEGER
    );

    CREATE INDEX IF NOT EXISTS idx_sessions_domain ON sessions(domain);
  `);
}

/** Ensures one domains_sm2 row per CCA-F domain exists. */
function seedDomains(conn: Database.Database): void {
  const insert = conn.prepare(
    "INSERT OR IGNORE INTO domains_sm2 (domain) VALUES (?)",
  );
  const tx = conn.transaction((ids: string[]) => {
    for (const id of ids) insert.run(id);
  });
  tx(DOMAIN_IDS);
}

/** Row shape of the sessions table. */
export interface SessionRow {
  id: number;
  ts: string;
  mode: string;
  exam_id: string | null;
  question_id: number;
  domain: string;
  chosen: string;
  correct: number;
  ms_elapsed: number | null;
}

/** Row shape of the domains_sm2 table. */
export interface Sm2Row {
  domain: string;
  interval: number;
  ease_factor: number;
  repetitions: number;
  last_reviewed: string | null;
  due_date: string | null;
}

/** Row shape of the exam_runs table. */
export interface ExamRunRow {
  id: string;
  started_ts: string;
  finished_ts: string | null;
  question_ids: string;
  raw_correct: number | null;
  scaled_score: number | null;
  passed: number | null;
}
