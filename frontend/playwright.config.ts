import { defineConfig, devices } from "@playwright/test";

// E2E suite (T4.5). Targets the deployed app by default so tests exercise the
// real backend; override with E2E_BASE_URL to point at a local `npm run preview`.
const baseURL = process.env.E2E_BASE_URL || "https://chatita.ai/mail/";

export default defineConfig({
  testDir: "./e2e",
  timeout: 90_000,
  expect: { timeout: 15_000 },
  fullyParallel: false,
  retries: process.env.CI ? 2 : 1,
  reporter: [["list"]],
  use: {
    baseURL,
    trace: "on-first-retry",
    actionTimeout: 20_000,
    navigationTimeout: 30_000,
  },
  projects: [
    { name: "chromium", use: { ...devices["Desktop Chrome"] } },
  ],
});
