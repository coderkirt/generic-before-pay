import { listedSavings, roundPaise } from "@/lib/data/money";
import type { DrugRecord } from "@/lib/data/types";

const FORBIDDEN = new Set([
  "dosage",
  "dosage_instructions",
  "frequency",
  "duration",
  "course",
  "substitution_advice",
  "recommendation",
  "recommendation_level",
  "advice",
  "prescription_required",
]);

const KNOWN = new Set([
  "id",
  "brand_name",
  "molecule",
  "strength",
  "unit",
  "branded_price",
  "generic_price",
  "source",
  "aliases",
  "savings_amount",
  "savings_percentage",
]);

const ID_PATTERN = /^[A-Za-z0-9]+(?:-[A-Za-z0-9]+)*$/;

export type Validation = { ok: true; records: DrugRecord[] } | { ok: false; problems: string[] };

export function validateDrugList(raw: unknown): Validation {
  if (!Array.isArray(raw)) {
    return { ok: false, problems: ["Dataset root must be a list of records."] };
  }

  const problems: string[] = [];
  const records: DrugRecord[] = [];
  const seen = new Set<string>();

  raw.forEach((item, index) => {
    const label = index + 1;
    if (item === null || typeof item !== "object" || Array.isArray(item)) {
      problems.push(`Record ${label}: must be an object.`);
      return;
    }
    const row = item as Record<string, unknown>;
    for (const key of Object.keys(row)) {
      if (FORBIDDEN.has(key.toLowerCase())) {
        problems.push(`Record ${label}: contains forbidden field '${key}'.`);
      } else if (!KNOWN.has(key)) {
        problems.push(`Record ${label}: contains unknown field '${key}'.`);
      }
    }

    const id = readString(row, "id", label, 1, 80, problems);
    const brand = readString(row, "brand_name", label, 1, 120, problems);
    const molecule = readString(row, "molecule", label, 1, 200, problems);
    const strength = readString(row, "strength", label, 1, 50, problems);
    const unit = readString(row, "unit", label, 1, 80, problems);
    const source = readString(row, "source", label, 1, 200, problems);
    const branded = readPrice(row, "branded_price", label, problems);
    const generic = readPrice(row, "generic_price", label, problems);
    const aliases = readAliases(row, label, problems);

    if (
      id === null ||
      brand === null ||
      molecule === null ||
      strength === null ||
      unit === null ||
      source === null ||
      branded === null ||
      generic === null ||
      aliases === null
    ) {
      return;
    }

    if (!ID_PATTERN.test(id)) {
      problems.push(`Record ${label}: id '${id}' must be alphanumeric groups separated by hyphens.`);
      return;
    }
    if (seen.has(id)) {
      problems.push(`Record ${label}: duplicate id '${id}'.`);
      return;
    }
    seen.add(id);

    const savings = listedSavings(branded, generic);
    if ("savings_amount" in row && !sameNumber(row.savings_amount, savings.amount)) {
      problems.push(`Record ${label}: savings_amount does not match branded_price and generic_price.`);
    }
    if ("savings_percentage" in row && !sameNumber(row.savings_percentage, savings.percentage)) {
      problems.push(`Record ${label}: savings_percentage does not match branded_price and generic_price.`);
    }
    if (problems.some((problem) => problem.startsWith(`Record ${label}:`))) {
      return;
    }

    records.push({
      id,
      brand_name: brand,
      molecule,
      strength,
      unit,
      branded_price: branded,
      generic_price: generic,
      savings_amount: savings.amount,
      savings_percentage: savings.percentage,
      source,
      aliases,
    });
  });

  if (problems.length > 0) return { ok: false, problems };
  return { ok: true, records };
}

function readString(
  row: Record<string, unknown>,
  key: string,
  label: number,
  min: number,
  max: number,
  problems: string[],
): string | null {
  const value = row[key];
  if (typeof value !== "string") {
    problems.push(`Record ${label}: '${key}' must be a string.`);
    return null;
  }
  const text = value.trim().replace(/\s+/g, " ");
  if (text.length < min || text.length > max) {
    problems.push(`Record ${label}: '${key}' must be ${min}-${max} characters.`);
    return null;
  }
  return text;
}

function readPrice(row: Record<string, unknown>, key: string, label: number, problems: string[]): number | null {
  const value = row[key];
  if (typeof value !== "number" || !Number.isFinite(value)) {
    problems.push(`Record ${label}: '${key}' must be a number.`);
    return null;
  }
  if (value < 0) {
    problems.push(`Record ${label}: '${key}' cannot be negative.`);
    return null;
  }
  const rounded = roundPaise(value);
  if (Math.abs(value - rounded) > 1e-9) {
    problems.push(`Record ${label}: '${key}' must have at most 2 decimal places.`);
    return null;
  }
  return rounded;
}

function readAliases(row: Record<string, unknown>, label: number, problems: string[]): string[] | null {
  if (!("aliases" in row) || row.aliases === undefined) return [];
  if (!Array.isArray(row.aliases)) {
    problems.push(`Record ${label}: 'aliases' must be a list of strings.`);
    return null;
  }
  const aliases: string[] = [];
  for (const alias of row.aliases) {
    if (typeof alias !== "string") {
      problems.push(`Record ${label}: 'aliases' must be a list of strings.`);
      return null;
    }
    const text = alias.trim().replace(/\s+/g, " ").toLowerCase();
    if (!text) {
      problems.push(`Record ${label}: alias cannot be empty.`);
      return null;
    }
    aliases.push(text);
  }
  return aliases;
}

function sameNumber(value: unknown, expected: number): boolean {
  return typeof value === "number" && Number.isFinite(value) && Math.abs(value - expected) < 1e-9;
}
