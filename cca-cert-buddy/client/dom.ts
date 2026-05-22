/**
 * Tiny DOM helpers.
 *
 * `el` builds elements with attributes and children; text children are set via
 * textContent, never innerHTML, so model- or user-sourced strings cannot inject
 * markup. This keeps the views terse without a framework.
 */

type Child = Node | string | null | undefined | false;

/** Creates an element with optional attributes and children. */
export function el<K extends keyof HTMLElementTagNameMap>(
  tag: K,
  attrs: Record<string, string> = {},
  ...children: Child[]
): HTMLElementTagNameMap[K] {
  const node = document.createElement(tag);
  for (const [key, value] of Object.entries(attrs)) {
    if (key === "class") node.className = value;
    else node.setAttribute(key, value);
  }
  for (const child of children) {
    if (child === null || child === undefined || child === false) continue;
    node.append(typeof child === "string" ? document.createTextNode(child) : child);
  }
  return node;
}

/** Clears a container and appends fresh nodes. */
export function mount(container: HTMLElement, ...nodes: Node[]): void {
  container.replaceChildren(...nodes);
}

/** Formats a 0-1 accuracy as a percentage string. */
export function pct(fraction: number): string {
  return `${Math.round(fraction * 100)}%`;
}

/** Formats seconds as MM:SS. */
export function clock(totalSeconds: number): string {
  const s = Math.max(0, Math.floor(totalSeconds));
  const mm = String(Math.floor(s / 60)).padStart(2, "0");
  const ss = String(s % 60).padStart(2, "0");
  return `${mm}:${ss}`;
}
