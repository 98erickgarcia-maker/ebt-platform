import { defineConfig } from "vite";
export default defineConfig({
  server: { proxy: { "/api": "http://127.0.0.1:5198" } },
  build: { outDir: "dist" },
});
