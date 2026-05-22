/**
 * Ambient declarations for Vite asset imports.
 *
 * Vite resolves `import "./styles.css"` at build time; this declaration lets
 * the TypeScript compiler accept the side-effect import too.
 */
declare module "*.css";
