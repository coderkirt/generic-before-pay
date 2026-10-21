import { similarityScore } from "@/lib/matching/distance";
import { doubleMetaphone } from "@/lib/matching/metaphone";
import { normalizeName, parseStrength, sameStrength, type StrengthPart } from "@/lib/matching/strength";
import {
  SCORE_LIKELY_AT,
  SCORE_LIKELY_GAP,
  SCORE_NONE_BELOW,
  STRENGTH_CONFLICT_CAP,
} from "@/lib/matching/thresholds";
import type { DisplayRecord } from "@/lib/data/types";

export type Tier = "exact" | "likely" | "uncertain" | "none";

export type MatchReason =
  | "empty_input"
  | "exact_brand"
  | "strength_needed"
  | "likely_spelling"
  | "close_matches"
  | "strength_conflict"
  | "not_in_data";

export type MatchCandidate = {
  id: string;
  brandName: string;
  composition: string;
  strength: string;
  score: number;
};

export type StrengthStatus = "matched" | "missing" | "conflict" | "none";

export type MatchResult = {
  input: string;
  tier: Tier;
  reason: MatchReason;
  matches: MatchCandidate[];
  strengthStatus: StrengthStatus;
};

type Stem = { name: string; from: "brand" | "alias" | "molecule"; parts: StrengthPart[] };

export function matchQuery(input: string, records: DisplayRecord[]): MatchResult {
  const parsed = parseStrength(input);
  if (!parsed.name) {
    return { input, tier: "none", reason: "empty_input", matches: [], strengthStatus: "none" };
  }

  const scored = records
    .map((record) => scoreRecord(parsed, record, input))
    .filter((row) => row.score > 0)
    .sort((a, b) => b.score - a.score || a.candidate.brandName.localeCompare(b.candidate.brandName));

  const exact = scored.filter((row) => row.brandExact);
  if (exact.length === 1 && parsed.parts.length === 0 && sharesStem(parsed.name, records) > 1) {
    return {
      input,
      tier: "uncertain",
      reason: "strength_needed",
      matches: scored
        .filter((row) => recordHasStem(row.candidate.id, parsed.name, records))
        .slice(0, 3)
        .map((row) => row.candidate),
      strengthStatus: "missing",
    };
  }
  if (exact.length === 1) {
    return {
      input,
      tier: "exact",
      reason: "exact_brand",
      matches: [exact[0]!.candidate],
      strengthStatus: parsed.parts.length === 0 ? "missing" : "matched",
    };
  }
  if (exact.length > 1) {
    return {
      input,
      tier: "uncertain",
      reason: "strength_needed",
      matches: exact.slice(0, 3).map((row) => row.candidate),
      strengthStatus: "missing",
    };
  }

  if (parsed.parts.length === 0 && !parsed.name.includes(" ")) {
    const mentioned = scored.filter((row) => recordMentions(row.candidate.id, parsed.name, records));
    if (mentioned.length > 1) {
      return {
        input,
        tier: "uncertain",
        reason: "strength_needed",
        matches: mentioned.slice(0, 3).map((row) => row.candidate),
        strengthStatus: "missing",
      };
    }
  }

  const top = scored[0];
  const second = scored[1];
  if (!top || top.score < SCORE_NONE_BELOW) {
    return { input, tier: "none", reason: "not_in_data", matches: [], strengthStatus: "none" };
  }

  const gap = top.score - (second?.score ?? 0);
  const strengthStatus: StrengthStatus = top.conflict ? "conflict" : parsed.parts.length === 0 ? "missing" : "matched";
  if (top.score >= SCORE_LIKELY_AT && gap >= SCORE_LIKELY_GAP && !top.conflict) {
    return {
      input,
      tier: "likely",
      reason: "likely_spelling",
      matches: [top.candidate],
      strengthStatus,
    };
  }
  return {
    input,
    tier: "uncertain",
    reason: top.conflict ? "strength_conflict" : second && gap < SCORE_LIKELY_GAP ? "close_matches" : "close_matches",
    matches: scored.filter((row) => row.score >= SCORE_NONE_BELOW).slice(0, 3).map((row) => row.candidate),
    strengthStatus,
  };
}

export function matchLines(lines: string[], records: DisplayRecord[]): MatchResult[] {
  return lines.map((line) => matchQuery(line, records));
}

function scoreRecord(
  query: { name: string; parts: StrengthPart[] },
  record: DisplayRecord,
  raw: string,
): { score: number; brandExact: boolean; conflict: boolean; candidate: MatchCandidate } {
  if (normalizeName(raw) === normalizeName(record.brandName)) {
    return {
      score: 100,
      brandExact: true,
      conflict: false,
      candidate: {
        id: record.id,
        brandName: record.brandName,
        composition: record.composition,
        strength: record.strength,
        score: 100,
      },
    };
  }
  const recordParts = parseStrength(record.strength).parts;
  const conflict = query.parts.length > 0 && !sameStrength(query.parts, recordParts);
  let best = 0;
  let brandExact = false;

  for (const stem of stems(record)) {
    if (!stem.name) continue;
    if (stem.name === query.name && stem.from === "brand" && !conflict) {
      const stemParts = stem.parts.length > 0 ? stem.parts : recordParts;
      const partsOk = query.parts.length === 0 || sameStrength(query.parts, stemParts);
      if (partsOk) brandExact = true;
      best = 100;
      continue;
    }
    if (stem.name === query.name) {
      best = Math.max(best, 96);
      continue;
    }
    best = Math.max(best, nameScore(query.name, stem.name));
  }

  if (conflict) best = Math.min(best, STRENGTH_CONFLICT_CAP);
  if (brandExact && conflict) brandExact = false;

  return {
    score: best,
    brandExact,
    conflict,
    candidate: {
      id: record.id,
      brandName: record.brandName,
      composition: record.composition,
      strength: record.strength,
      score: best,
    },
  };
}

function recordMentions(id: string, token: string, records: DisplayRecord[]): boolean {
  const record = records.find((item) => item.id === id);
  if (!record) return false;
  return stems(record).some((stem) => stem.name === token || stem.name.split(" ").includes(token));
}

function sharesStem(name: string, records: DisplayRecord[]): number {
  return records.filter((record) => stems(record).some((stem) => stem.name === name)).length;
}

function recordHasStem(id: string, name: string, records: DisplayRecord[]): boolean {
  const record = records.find((item) => item.id === id);
  return record ? stems(record).some((stem) => stem.name === name) : false;
}

function stems(record: DisplayRecord): Stem[] {
  const brand = parseStrength(record.brandName);
  const list: Stem[] = [{ name: brand.name, from: "brand", parts: brand.parts }];
  for (const alias of record.aliases) {
    const parsed = parseStrength(alias);
    list.push({ name: parsed.name, from: "alias", parts: parsed.parts });
  }
  const molecule = record.composition.replace(/\([^)]*\)/g, " ");
  const full = normalizeName(molecule);
  const first = full.split(" ")[0] ?? "";
  if (full) list.push({ name: full, from: "molecule", parts: [] });
  if (first.length >= 5 && first !== full) list.push({ name: first, from: "molecule", parts: [] });
  return list;
}

function nameScore(query: string, candidate: string): number {
  const base = similarityScore(query, candidate);
  if (base < 50) return base;
  const queryCode = doubleMetaphone(query);
  const candidateCode = doubleMetaphone(candidate);
  if (queryCode && queryCode === candidateCode) return Math.min(100, base + 4);
  return base;
}
