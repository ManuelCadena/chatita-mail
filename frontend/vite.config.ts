import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// Chatita Mail frontend. Served at /mail/ in production (nginx), root in dev.
export default defineConfig({
  base: "/mail/",
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      "/api": {
        target: "http://localhost:8000",
        changeOrigin: true,
      },
    },
  },
});
