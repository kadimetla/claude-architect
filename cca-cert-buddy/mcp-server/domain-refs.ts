/**
 * Reads the CCA-F domain reference markdown from the parent repo.
 *
 * The domain-N-*.md files in claude-architect/ are the authoritative one-page
 * references for each exam domain. The MCP server exposes them as resources
 * and the lookup_domain_ref tool; the question generator feeds the relevant
 * one into Claude as focused, isolated context.
 */
import { readFileSync, existsSync } from "node:fs";
import { join } from "node:path";
import type { DomainId } from "../shared/types.js";
import { getDomain } from "../shared/domains.js";
import { REPO_ROOT } from "../shared/paths.js";

/**
 * Returns the full reference markdown for a domain. Falls back to the domain's
 * name and weight if the file is missing, so the MCP server never hard-fails
 * on a relocated reference doc.
 */
export function readDomainRef(domain: DomainId): string {
  const meta = getDomain(domain);
  // refPath is "../domain-N-*.md" relative to the shared/ module; resolve it
  // against the repo root instead.
  const fileName = meta.refPath.replace(/^\.\.\//, "");
  const path = join(REPO_ROOT, fileName);

  if (!existsSync(path)) {
    return (
      `# ${meta.id}: ${meta.name}\n\n` +
      `Exam weight: ${meta.weight}%.\n\n` +
      `Reference file ${fileName} was not found in the repo root. ` +
      `This is a fallback summary.`
    );
  }
  return readFileSync(path, "utf8");
}
