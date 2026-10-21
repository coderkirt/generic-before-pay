export type StrengthPart = { value: number; unit: string };

const UNIT = String.raw`mcg|mg|ml|iu|g|%`;
const WITH_UNIT = new RegExp(String.raw`(\d+(?:\.\d+)?)\s*(${UNIT})(?![a-z0-9])`, "gi");
const SLASH = /(\d+(?:\.\d+)?)\s*\/\s*(\d+(?:\.\d+)?)(?!\s*(?:mg|mcg|g|ml|iu|%))/gi;
const GLUED = /([A-Za-z])(\d+(?:\.\d+)?)(?!\d)/g;
const BARE = /(?:^|\s)(\d+(?:\.\d+)?)(?=\s|$)/g;

/** Pull strengths out of a brand, alias, or typed line. Bare numbers and glued numbers are mg, as in Pantocid40 and 500/125. */
export function parseStrength(raw: string): { name: string; parts: StrengthPart[] } {
  let text = raw.normalize("NFKD");
  const parts: StrengthPart[] = [];

  text = text.replace(SLASH, (_full, left: string, right: string) => {
    parts.push({ value: Number(left), unit: "mg" }, { value: Number(right), unit: "mg" });
    return " ";
  });
  text = text.replace(WITH_UNIT, (_full, num: string, unit: string) => {
    parts.push({ value: Number(num), unit: unit.toLowerCase() });
    return " ";
  });
  text = text.replace(GLUED, (_full, letter: string, num: string) => {
    parts.push({ value: Number(num), unit: "mg" });
    return letter;
  });
  text = text.replace(BARE, (_full, num: string) => {
    parts.push({ value: Number(num), unit: "mg" });
    return " ";
  });

  return { name: normalizeName(text), parts: sortParts(parts) };
}

export function sameStrength(left: StrengthPart[], right: StrengthPart[]): boolean {
  if (left.length !== right.length) return false;
  return left.every((part, index) => part.value === right[index]?.value && part.unit === right[index]?.unit);
}

export function sortParts(parts: StrengthPart[]): StrengthPart[] {
  return [...parts].sort((a, b) => a.value - b.value || a.unit.localeCompare(b.unit));
}

const NOISE = new Set([
  "tab",
  "tabs",
  "tablet",
  "tablets",
  "cap",
  "caps",
  "capsule",
  "capsules",
  "strip",
  "of",
]);

/** Case, whitespace, punctuation, and unicode fold. Devanagari is not transliterated; the repo does not specify a map. */
export function normalizeName(raw: string): string {
  const folded = raw.normalize("NFKD").toLowerCase().replace(/\p{M}/gu, "");
  const spaced = folded.replace(/[^a-z0-9+%]+/g, " ").replace(/\s+/g, " ").trim();
  return spaced
    .split(" ")
    .filter((token) => token && !NOISE.has(token))
    .join(" ");
}
