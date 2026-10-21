import type { Tier } from "@/lib/matching/match";
import type { LineStatus } from "@/lib/pricing/compare";

/**
 * Comparison eligibility from the match tier and the pricing status.
 * A missing price date is not staleness: this dataset has no date to age.
 * "verified" means the listed-price comparison is allowed after the user
 * confirmed the name. It does not mean the photo or the spelling was verified.
 */
export type ComparisonEligibility = "verified" | "needs_review" | "not_comparable" | "not_found" | "error";

export function comparisonEligibility(input: {
  catalogOk: boolean;
  tier: Tier;
  confirmed: boolean;
  status: LineStatus;
}): ComparisonEligibility {
  if (!input.catalogOk) return "error";
  if (input.tier === "none") return "not_found";
  if (!input.confirmed || input.status === "unconfirmed_match") return "needs_review";
  if (input.status === "same_composition_comparable") return "verified";
  return "not_comparable";
}
