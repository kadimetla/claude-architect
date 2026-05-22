import { defineConfig } from "vite";

// The SPA lives in client/. In dev, Vite serves it on 5173 and proxies /api to
// the Express backend on 3000. In production, `vite build` emits static assets
// into dist/client, which server/index.ts serves from the same origin.
export default defineConfig({
  root: "client",
  build: {
    outDir: "../dist/client",
    emptyOutDir: true,
  },
  server: {
    port: 5173,
    proxy: {
      "/api": "http://localhost:3000",
    },
  },
});
