import { expect, test } from "@playwright/test";

const DISCLAIMER =
  "This shows published generic names and indicative prices for medicines already named. It is not medical advice and it is not a recommendation to substitute. Confirm the medicine, the strength, and the price with your doctor or pharmacist before you buy or change anything.";

test("home shell exposes the next action, disclaimer, and skip link", async ({ page }) => {
  await page.goto("/");
  await expect(page.getByRole("heading", { level: 1 })).toHaveText("Listed prices, before you pay");
  await expect(page.getByRole("link", { name: "Scan a prescription" })).toBeVisible();
  await expect(page.getByRole("button", { name: "Type medicine names" })).toBeVisible();
  await expect(page.getByText(DISCLAIMER)).toBeVisible();
  await expect(page.getByText("TODO_NEEDS_HUMAN_REVIEW")).toHaveCount(0);
  await page.keyboard.press("Tab");
  await expect(page.getByRole("link", { name: "Skip to content" })).toBeFocused();
});

test("refresh on review shows the privacy recovery screen", async ({ page }) => {
  await page.goto("/review");
  await expect(
    page.getByRole("heading", { name: "Your session was cleared for privacy. Start again." }),
  ).toBeVisible();
});
