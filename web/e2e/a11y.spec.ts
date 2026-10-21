import AxeBuilder from "@axe-core/playwright";
import { expect, test, type Page } from "@playwright/test";

const WIDTHS = [320, 360, 375, 390, 414, 480, 768, 834, 1024, 1280, 1440, 1920];
const ROUTES = ["/", "/scan", "/review", "/patient", "/results", "/kendras", "/print"];

async function openSession(page: Page) {
  await page.goto("/");
  await page.getByRole("button", { name: "Type medicine names" }).click();
  await page.waitForURL("**/review");
}

test.describe("responsive, language, and accessibility", () => {
  test("no horizontal overflow on the required widths", async ({ page }) => {
    test.setTimeout(300_000);
    await openSession(page);
    for (const width of WIDTHS) {
      await page.setViewportSize({ width, height: 800 });
      for (const route of ROUTES) {
        await page.goto(route, { waitUntil: "domcontentloaded" });
        const fits = await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth);
        expect(fits, `${route} at ${width}`).toBe(true);
      }
    }
  });

  test("hindi renders on every route without the review token", async ({ page }) => {
    await openSession(page);
    for (const route of ROUTES) {
      await page.goto(route);
      await page.getByRole("button", { name: "हिन्दी" }).click();
      await expect(page.locator("html")).toHaveAttribute("lang", "hi");
      await expect(page.getByText("TODO_NEEDS_HUMAN_REVIEW")).toHaveCount(0);
      await page.getByRole("button", { name: "English" }).click();
    }
  });

  test("axe reports no serious or critical issues in English or Hindi", async ({ page }) => {
    test.setTimeout(180_000);
    await openSession(page);
    for (const route of ROUTES) {
      await page.goto(route);
      for (const lang of ["English", "हिन्दी"] as const) {
        await page.getByRole("button", { name: lang }).click();
        const results = await new AxeBuilder({ page }).analyze();
        const blocking = results.violations.filter((item) => item.impact === "serious" || item.impact === "critical");
        expect(blocking, `${route} ${lang}`).toEqual([]);
      }
    }
  });

  test("keyboard reaches the typed path and reduced motion removes animation", async ({ page }) => {
    await page.emulateMedia({ reducedMotion: "reduce" });
    await page.goto("/");
    await page.keyboard.press("Tab");
    await expect(page.getByRole("link", { name: "Skip to content" })).toBeFocused();
    await page.keyboard.press("Enter");
    await expect(page.locator("#main")).toBeFocused();
    const duration = await page.locator("body").evaluate((node) => getComputedStyle(node).animationDuration);
    expect(duration === "0s" || duration === "none" || duration === "").toBe(true);
  });

  test("normal flow has no console errors, broken images, or dead primary actions", async ({ page }) => {
    const problems: string[] = [];
    page.on("console", (message) => {
      if (message.type() === "error") problems.push(message.text());
    });
    page.on("pageerror", (error) => problems.push(error.message));
    await page.goto("/");
    await page.getByRole("button", { name: "Type medicine names" }).click();
    await page.getByLabel("Medicine name").fill("Calpol 500");
    await page.getByRole("button", { name: "Add medicine" }).click();
    await page.getByRole("button", { name: /This name is correct: Calpol 500/ }).click();
    await page.getByRole("button", { name: "Continue" }).click();
    const broken = await page.locator("img").evaluateAll((images) =>
      images.filter((image) => image instanceof HTMLImageElement && image.complete && image.naturalWidth === 0).length,
    );
    expect(broken).toBe(0);
    expect(problems).toEqual([]);
  });
});
