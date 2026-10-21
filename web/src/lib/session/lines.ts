import type { DisplayRecord } from "@/lib/data/types";
import { matchQuery } from "@/lib/matching/match";
import type { RxLine } from "@/lib/session/reducer";

let sequence = 0;

export function newLineKey(): string {
  sequence += 1;
  return `line-${sequence}`;
}

export function buildLine(query: string, records: DisplayRecord[], key = newLineKey()): RxLine {
  const result = matchQuery(query, records);
  const only = result.matches.length === 1 ? result.matches[0] : undefined;
  const selectedId = (result.tier === "exact" || result.tier === "likely") && only ? only.id : null;
  return {
    key,
    query: query.trim(),
    tier: result.tier,
    reason: result.reason,
    candidateIds: result.matches.map((match) => match.id),
    selectedId,
    confirmed: false,
    quantity: 1,
  };
}

export function linesFromOcr(text: string, candidates: string[], records: DisplayRecord[]): RxLine[] {
  const names = candidates.length > 0 ? candidates : text.split(/\r?\n/).map((line) => line.trim()).filter(Boolean);
  return names.map((name) => buildLine(name, records));
}
