import { describe, expect, it } from "vitest";
import { comparisonEligibility } from "@/lib/pricing/eligibility";

describe("comparison eligibility", () => {
  it("hides a price until the name is confirmed and the compositions can be compared", () => {
    expect(
      comparisonEligibility({
        catalogOk: true,
        tier: "likely",
        confirmed: false,
        status: "unconfirmed_match",
      }),
    ).toBe("needs_review");
    expect(
      comparisonEligibility({
        catalogOk: true,
        tier: "exact",
        confirmed: true,
        status: "same_composition_comparable",
      }),
    ).toBe("verified");
    expect(
      comparisonEligibility({
        catalogOk: true,
        tier: "exact",
        confirmed: true,
        status: "different_strength",
      }),
    ).toBe("not_comparable");
    expect(
      comparisonEligibility({
        catalogOk: true,
        tier: "none",
        confirmed: false,
        status: "unconfirmed_match",
      }),
    ).toBe("not_found");
    expect(
      comparisonEligibility({
        catalogOk: false,
        tier: "exact",
        confirmed: true,
        status: "same_composition_comparable",
      }),
    ).toBe("error");
  });
});
