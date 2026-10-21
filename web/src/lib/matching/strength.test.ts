import { describe, expect, it } from "vitest";
import { damerauLevenshtein } from "@/lib/matching/distance";
import { doubleMetaphone } from "@/lib/matching/metaphone";
import { normalizeName, parseStrength, sameStrength } from "@/lib/matching/strength";

describe("strength parser and normaliser", () => {
  it("parses glued, spaced, slash, decimal, and explicit units", () => {
    expect(parseStrength("Pantocid40")).toEqual({ name: "pantocid", parts: [{ value: 40, unit: "mg" }] });
    expect(parseStrength("40mg").parts).toEqual([{ value: 40, unit: "mg" }]);
    expect(parseStrength("40 mg").parts).toEqual([{ value: 40, unit: "mg" }]);
    expect(parseStrength("500/125").parts).toEqual([
      { value: 125, unit: "mg" },
      { value: 500, unit: "mg" },
    ]);
    expect(parseStrength("2.5 mg").parts).toEqual([{ value: 2.5, unit: "mg" }]);
    expect(parseStrength("10 mcg").parts[0]).toMatchObject({ value: 10, unit: "mcg" });
    expect(parseStrength("1 g").parts[0]).toMatchObject({ unit: "g" });
    expect(parseStrength("5 ml").parts[0]).toMatchObject({ unit: "ml" });
    expect(parseStrength("100 IU").parts[0]).toMatchObject({ unit: "iu" });
    expect(parseStrength("1%").parts[0]).toMatchObject({ unit: "%" });
    expect(parseStrength("Calpol").parts).toEqual([]);
  });

  it("folds case, punctuation, and noise suffixes, and does not invent a Devanagari map", () => {
    expect(normalizeName("  Calpol   TAB ")).toBe("calpol");
    expect(normalizeName("Pan-D")).toBe("pan d");
    expect(normalizeName("café")).toBe("cafe");
    expect(normalizeName("पैन")).toBe("");
  });

  it("measures Damerau-Levenshtein, including a transposition", () => {
    expect(damerauLevenshtein("crosin", "crocin")).toBe(1);
    expect(damerauLevenshtein("cetzine", "cetzien")).toBe(1);
    expect(damerauLevenshtein("pan", "pan")).toBe(0);
  });

  it("gives metformin and metformine the same metaphone code", () => {
    expect(doubleMetaphone("metformin")).toBe(doubleMetaphone("metformine"));
    expect(sameStrength(parseStrength("500 mg + 125 mg").parts, parseStrength("125 mg + 500 mg").parts)).toBe(true);
  });
});
