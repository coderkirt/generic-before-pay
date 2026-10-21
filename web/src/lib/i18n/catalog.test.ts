import { describe, expect, it } from "vitest";
import { DISCLAIMER, NOT_IN_DATA, OFFLINE_MESSAGE, RECOVERY_MESSAGE } from "@/lib/copy/approved";
import { en } from "@/lib/i18n/en";
import { hi } from "@/lib/i18n/hi";
import { TODO_NEEDS_HUMAN_REVIEW } from "@/lib/i18n/placeholder";
import { resolveMessage, unapprovedHindiKeys } from "@/lib/i18n/resolve";

const BANNED = /\b(switch|replace|substitute|better|recommended)\b/i;

describe("copy catalog", () => {
  it("keeps the repo disclaimer verbatim", () => {
    expect(en.disclaimer).toBe(DISCLAIMER);
    expect(en["recovery.body"]).toBe(RECOVERY_MESSAGE);
    expect(en["offline.body"]).toBe(OFFLINE_MESSAGE);
    expect(en["info.missing"]).toBe(NOT_IN_DATA);
  });

  it("falls back to English when Hindi is unapproved and does not return the placeholder", () => {
    const resolved = resolveMessage("hi", "disclaimer");
    expect(resolved.text).toBe(DISCLAIMER);
    expect(resolved.locale).toBe("en");
    expect(resolved.needsReview).toBe(true);
    expect(resolved.text).not.toContain(TODO_NEEDS_HUMAN_REVIEW);
  });

  it("fails in CI-strict mode while Hindi legal copy still needs a person", () => {
    const keys = unapprovedHindiKeys();
    if (process.env.CI_STRICT === "1") {
      expect(keys, "TODO_NEEDS_HUMAN_REVIEW is still in the Hindi catalog").toEqual([]);
    } else {
      expect(keys).toEqual(["disclaimer", "recovery.body", "offline.body", "info.missing"]);
    }
  });

  it("keeps substitution language out of interface strings other than the approved disclaimer", () => {
    for (const [key, value] of Object.entries(en)) {
      if (key === "disclaimer") continue;
      expect(value, key).not.toMatch(BANNED);
      expect(value, key).not.toMatch(/ERR_|\[object|undefined/);
    }
    for (const [key, value] of Object.entries(hi)) {
      if (value === TODO_NEEDS_HUMAN_REVIEW) continue;
      expect(value, key).not.toMatch(BANNED);
      expect(value, key).not.toMatch(/ERR_|\[object|undefined/);
    }
  });
});
