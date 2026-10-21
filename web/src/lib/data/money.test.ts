import { describe, expect, it } from "vitest";
import { roundPercent } from "@/lib/data/money";

describe("percentage rounding", () => {
  it("matches Python half-even rounding used by the curated seed", () => {
    expect(roundPercent((146 / 160) * 100)).toBe(91.2);
    expect(roundPercent((26 / 32) * 100)).toBe(81.2);
    expect(roundPercent(91.35)).toBe(91.4);
    expect(roundPercent(91.24)).toBe(91.2);
  });
});
