import { test, expect } from "@playwright/test";

// T4.5 — End-to-end smoke suite for Chatita Mail v3.0.
// Runs against the deployed app (see playwright.config.ts baseURL).

test.beforeEach(async ({ page }) => {
  // Empty path keeps us within the baseURL directory (…/mail/), NOT the origin
  // root (which serves the separate Chatita Workspace app).
  await page.goto("");
  // Sidebar brand renders once the shell mounts.
  await expect(page.getByText("Chatita Mail")).toBeVisible();
});

test("inbox loads with folders and live stats", async ({ page }) => {
  await expect(page.getByRole("button", { name: /^Inbox/ })).toBeVisible();
  await expect(page.getByRole("button", { name: "Redactar" })).toBeVisible();
  await expect(page.getByRole("button", { name: /Enviados/ })).toBeVisible();
  // Stats populate (Total emails shows a number, not the loading dash).
  await expect(page.getByText("Total emails")).toBeVisible();
  // At least one email row appears in the list.
  await expect(page.locator("button").filter({ hasText: /Critical|Important|Medium|Low/ }).first())
    .toBeVisible({ timeout: 30_000 });
});

test("dashboard (Panel) renders real analytics", async ({ page }) => {
  await page.getByRole("button", { name: "Panel" }).click();
  await expect(page.getByText("Panel de analíticas")).toBeVisible();
  await expect(page.getByText("Tiempo ahorrado")).toBeVisible();
  await expect(page.getByText("Top remitentes")).toBeVisible();
});

test("accessibility mode toggles a data attribute on <html>", async ({ page }) => {
  await page.getByRole("button", { name: "Opciones de accesibilidad" }).click();
  await page.getByRole("switch", { name: /Fuente para dislexia/ }).click();
  await expect(page.locator("html")).toHaveAttribute("data-a11y-dyslexia", "1");
  // Toggle off restores the default.
  await page.getByRole("switch", { name: /Fuente para dislexia/ }).click();
  await expect(page.locator("html")).not.toHaveAttribute("data-a11y-dyslexia", "1");
});

test("voice reply (T4.1) returns audio/mpeg from the TTS endpoint", async ({ page }) => {
  // Open a reply on the first email, type text, and press "Escuchar".
  await page.getByTestId("email-row").first().click();
  await page.getByRole("button", { name: "Responder" }).click();
  await page.getByPlaceholder("Escribe tu mensaje…").fill(
    "Hola, confirmo recibido y te respondo hoy mismo. Saludos, Manuel."
  );
  const [resp] = await Promise.all([
    page.waitForResponse((r) => r.url().includes("/voice/tts"), { timeout: 30_000 }),
    page.getByRole("button", { name: "Escuchar" }).click(),
  ]);
  expect(resp.status()).toBe(200);
  expect(resp.headers()["content-type"]).toContain("audio/mpeg");
});

test("compose modal validates recipient before enabling send", async ({ page }) => {
  await page.getByRole("button", { name: "Redactar" }).click();
  await expect(page.getByText("Nuevo correo")).toBeVisible();
  const send = page.getByRole("button", { name: "Enviar" });
  await expect(send).toBeDisabled();
  await page.getByPlaceholder("correo@dominio.com, otro@dominio.com").fill("jose@manuelcadena.com");
  await expect(send).toBeEnabled();
  await page.getByRole("button", { name: "Cancelar" }).click();
  await expect(page.getByText("Nuevo correo")).toBeHidden();
});
