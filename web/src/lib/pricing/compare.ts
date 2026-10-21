import { roundPaise } from "@/lib/data/money";
import { normalizeName, parseStrength, sameStrength } from "@/lib/matching/strength";
import type { Tier } from "@/lib/matching/match";

export type LineStatus =
  | "same_composition_comparable"
  | "different_strength"
  | "combination_drug"
  | "unit_mismatch"
  | "no_equivalent"
  | "missing_data"
  | "unconfirmed_match";

export type PriceSide = {
  composition: string;
  strength: string;
  form: string | null;
  packSize: number | null;
  packPrice: number | null;
  source: string | null;
  priceDate: null;
};

export type CompareInput = {
  confirmed: boolean;
  tier: Tier;
  quantity: number;
  brand: PriceSide | null;
  generic: PriceSide | null;
};

export type PricedLine = {
  status: LineStatus;
  quantity: number;
  countsTowardTotal: boolean;
  brandPackPrice: number | null;
  genericPackPrice: number | null;
  brandPerUnit: number | null;
  genericPerUnit: number | null;
  brandLineTotal: number | null;
  genericLineTotal: number | null;
  listedDifference: number | null;
  label: "listed saving" | "listed price difference" | null;
  source: string | null;
  priceDate: null;
};

export type PriceTotals = {
  brandTotal: number;
  genericTotal: number;
  listedDifference: number;
  label: "listed saving" | "listed price difference";
  countedLines: number;
};

const EMPTY: PricedLine = {
  status: "unconfirmed_match",
  quantity: 0,
  countsTowardTotal: false,
  brandPackPrice: null,
  genericPackPrice: null,
  brandPerUnit: null,
  genericPerUnit: null,
  brandLineTotal: null,
  genericLineTotal: null,
  listedDifference: null,
  label: null,
  source: null,
  priceDate: null,
};

export function compareLine(input: CompareInput): PricedLine {
  const quantity = input.quantity;
  if (!input.confirmed || input.tier === "uncertain" || input.tier === "none" || !input.brand) {
    return { ...EMPTY, status: "unconfirmed_match", quantity };
  }
  if (!input.generic || input.generic.packPrice === null) {
    return {
      ...EMPTY,
      status: "no_equivalent",
      quantity,
      brandPackPrice: input.brand.packPrice,
      source: input.brand.source,
      priceDate: null,
    };
  }
  if (
    input.brand.packPrice === null ||
    input.brand.packSize === null ||
    input.generic.packSize === null ||
    input.brand.form === null ||
    input.generic.form === null ||
    quantity < 1
  ) {
    return sourcedPacks(input, "missing_data");
  }

  const brandComposition = compositionSet(input.brand.composition);
  const genericComposition = compositionSet(input.generic.composition);
  if (!sameSet(brandComposition, genericComposition)) {
    return { ...EMPTY, status: "combination_drug", quantity };
  }

  const brandStrength = parseStrength(input.brand.strength).parts;
  const genericStrength = parseStrength(input.generic.strength).parts;
  if (brandStrength.length === 0 || genericStrength.length === 0) {
    return sourcedPacks(input, "missing_data");
  }
  if (!sameStrength(brandStrength, genericStrength)) {
    return { ...EMPTY, status: "different_strength", quantity };
  }
  if (input.brand.form !== input.generic.form) {
    return { ...EMPTY, status: "unit_mismatch", quantity };
  }

  const brandPerUnit = roundPaise(input.brand.packPrice / input.brand.packSize);
  const genericPerUnit = roundPaise(input.generic.packPrice / input.generic.packSize);
  const units = quantity * input.brand.packSize;
  const brandLineTotal = roundPaise(input.brand.packPrice * quantity);
  const genericLineTotal = roundPaise(genericPerUnit * units);
  const listedDifference = roundPaise(brandLineTotal - genericLineTotal);

  return {
    status: "same_composition_comparable",
    quantity,
    countsTowardTotal: true,
    brandPackPrice: input.brand.packPrice,
    genericPackPrice: input.generic.packPrice,
    brandPerUnit,
    genericPerUnit,
    brandLineTotal,
    genericLineTotal,
    listedDifference,
    label: listedLabel(listedDifference),
    source: input.brand.source,
    priceDate: null,
  };
}

export function sumLines(lines: PricedLine[]): PriceTotals {
  let brandTotal = 0;
  let genericTotal = 0;
  let countedLines = 0;
  for (const line of lines) {
    if (!line.countsTowardTotal || line.brandLineTotal === null || line.genericLineTotal === null) continue;
    brandTotal = roundPaise(brandTotal + line.brandLineTotal);
    genericTotal = roundPaise(genericTotal + line.genericLineTotal);
    countedLines += 1;
  }
  const listedDifference = roundPaise(brandTotal - genericTotal);
  return {
    brandTotal,
    genericTotal,
    listedDifference,
    label: listedLabel(listedDifference),
    countedLines,
  };
}

export function listedLabel(amount: number): "listed saving" | "listed price difference" {
  return amount > 0 ? "listed saving" : "listed price difference";
}

function compositionSet(value: string): string[] {
  return value
    .split("+")
    .map((part) => normalizeName(part.replace(/\([^)]*\)/g, " ")))
    .filter((part) => part.length > 0)
    .sort();
}

function sameSet(left: string[], right: string[]): boolean {
  return left.length === right.length && left.every((token, index) => token === right[index]);
}

function sourcedPacks(input: CompareInput, status: LineStatus): PricedLine {
  return {
    ...EMPTY,
    status,
    quantity: input.quantity,
    brandPackPrice: input.brand?.packPrice ?? null,
    genericPackPrice: input.generic?.packPrice ?? null,
    source: input.brand?.source ?? null,
    priceDate: null,
  };
}
