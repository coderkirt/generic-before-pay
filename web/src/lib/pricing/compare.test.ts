import { describe, expect, it } from "vitest";
import { compareLine, listedLabel, sumLines, type CompareInput, type PriceSide } from "@/lib/pricing/compare";

const brand = (overrides: Partial<PriceSide> = {}): PriceSide => ({
  composition: "Paracetamol",
  strength: "500 mg",
  form: "tablet",
  packSize: 10,
  packPrice: 32.5,
  source: "PMBJP Price List 2024 / NPPA",
  priceDate: null,
  ...overrides,
});

const generic = (overrides: Partial<PriceSide> = {}): PriceSide => ({
  composition: "Paracetamol",
  strength: "500 mg",
  form: "tablet",
  packSize: 10,
  packPrice: 5,
  source: "PMBJP Price List 2024 / NPPA",
  priceDate: null,
  ...overrides,
});

function line(overrides: Partial<CompareInput> = {}) {
  return compareLine({
    confirmed: true,
    tier: "likely",
    quantity: 1,
    brand: brand(),
    generic: generic(),
    ...overrides,
  });
}

describe("pricing", () => {
  it("compares a confirmed same-composition line and rounds paise", () => {
    const priced = line({ quantity: 2 });
    expect(priced.status).toBe("same_composition_comparable");
    expect(priced.brandPerUnit).toBe(3.25);
    expect(priced.genericPerUnit).toBe(0.5);
    expect(priced.brandLineTotal).toBe(65);
    expect(priced.genericLineTotal).toBe(10);
    expect(priced.listedDifference).toBe(55);
    expect(priced.label).toBe("listed saving");
    expect(priced.priceDate).toBeNull();
    expect(priced.source).toBe("PMBJP Price List 2024 / NPPA");
  });

  it("normalises different pack sizes by the unit", () => {
    const priced = line({ generic: generic({ packSize: 15, packPrice: 7.5 }) });
    expect(priced.genericPerUnit).toBe(0.5);
    expect(priced.genericLineTotal).toBe(5);
    expect(priced.listedDifference).toBe(27.5);
  });

  it("hides prices for uncertain, unconfirmed, and none", () => {
    for (const priced of [
      line({ tier: "uncertain" }),
      line({ tier: "none" }),
      line({ tier: "exact", confirmed: false }),
    ]) {
      expect(priced.status).toBe("unconfirmed_match");
      expect(priced.brandPackPrice).toBeNull();
      expect(priced.genericPackPrice).toBeNull();
      expect(priced.countsTowardTotal).toBe(false);
    }
  });

  it("classifies every non-comparable outcome and keeps them out of the total", () => {
    expect(line({ generic: null }).status).toBe("no_equivalent");
    expect(line({ brand: brand({ strength: "650 mg" }) }).status).toBe("different_strength");
    expect(line({ generic: generic({ composition: "Paracetamol + Caffeine" }) }).status).toBe("combination_drug");
    expect(line({ generic: generic({ form: "capsule" }) }).status).toBe("unit_mismatch");
    expect(line({ brand: brand({ packSize: null }) }).status).toBe("missing_data");
    const totals = sumLines([
      line(),
      line({ tier: "uncertain" }),
      line({ brand: brand({ strength: "650 mg" }) }),
      line({ generic: null }),
    ]);
    expect(totals.countedLines).toBe(1);
    expect(totals.brandTotal).toBe(32.5);
    expect(totals.genericTotal).toBe(5);
    expect(totals.listedDifference).toBe(27.5);
  });

  it("shows a zero or negative difference as a listed price difference, not a saving", () => {
    const zero = line({ generic: generic({ packPrice: 32.5 }) });
    expect(zero.listedDifference).toBe(0);
    expect(zero.label).toBe("listed price difference");
    const negative = line({ brand: brand({ packPrice: 5 }), generic: generic({ packPrice: 12 }) });
    expect(negative.listedDifference).toBe(-7);
    expect(negative.label).toBe("listed price difference");
    expect(listedLabel(0)).toBe("listed price difference");
    expect(sumLines([zero, negative]).label).toBe("listed price difference");
  });
});
