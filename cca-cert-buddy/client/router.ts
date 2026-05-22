/**
 * A minimal hash router.
 *
 * Maps #/route to a view module's render function. No framework, no history
 * API - hash routing keeps the SPA fallback trivial (Express serves index.html
 * for every non-API path and the hash does the rest). Each view exports
 * `render(container, params)`.
 */

/** A view renders itself into the given container. */
export type View = (container: HTMLElement, params: URLSearchParams) => void | Promise<void>;

const routes = new Map<string, View>();

/** Registers a view for a route path (for example "/quiz"). */
export function route(path: string, view: View): void {
  routes.set(path, view);
}

/** Parses the current location hash into a path and its query params. */
function parseHash(): { path: string; params: URLSearchParams } {
  const raw = location.hash.replace(/^#/, "") || "/";
  const [path, query = ""] = raw.split("?");
  return { path: path || "/", params: new URLSearchParams(query) };
}

/** Renders the view matching the current hash. */
async function renderCurrent(): Promise<void> {
  const app = document.getElementById("app");
  if (!app) return;

  const { path, params } = parseHash();
  const view = routes.get(path) ?? routes.get("/");
  if (!view) {
    app.innerHTML = `<p class="error">No view registered for ${path}.</p>`;
    return;
  }

  // Highlight the active nav link by current path.
  document.querySelectorAll(".app-nav a").forEach((a) => {
    const href = (a as HTMLAnchorElement).getAttribute("href") ?? "";
    a.classList.toggle("active", href === `#${path}`);
  });

  app.innerHTML = `<p class="loading">Loading...</p>`;
  try {
    await view(app, params);
  } catch (err) {
    const p = document.createElement("p");
    p.className = "error";
    p.textContent = err instanceof Error ? err.message : String(err);
    app.replaceChildren(p);
  }
}

/** Starts the router: render now and on every hash change. */
export function startRouter(): void {
  window.addEventListener("hashchange", renderCurrent);
  renderCurrent();
}

/** Programmatic navigation. */
export function navigate(path: string): void {
  location.hash = path;
}
