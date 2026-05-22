/**
 * CCA Cert Buddy - Express backend entry point.
 *
 * Serves the REST API under /api and, in production, the built SPA from
 * dist/client. In dev, the Vite dev server (port 5173) proxies /api here.
 *
 * The backend is also an MCP client: the live-generation routes connect to the
 * cca-study-mcp server. Those routes degrade gracefully when no API key is set.
 */
import "dotenv/config";
import { createApp } from "./app.js";

const PORT = Number(process.env.PORT ?? 3000);

createApp().listen(PORT, () => {
  console.log(`CCA Cert Buddy backend listening on http://localhost:${PORT}`);
});
