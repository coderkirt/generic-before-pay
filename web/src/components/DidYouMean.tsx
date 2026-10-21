"use client";

import type { DisplayRecord } from "@/lib/data/types";
import type { MatchReason } from "@/lib/matching/match";
import { useI18n } from "@/lib/i18n/context";

export function DidYouMean({
  reason,
  candidateIds,
  records,
  onPick,
}: {
  reason: MatchReason;
  candidateIds: string[];
  records: DisplayRecord[];
  onPick: (id: string) => void;
}) {
  const { t } = useI18n();
  const rows = candidateIds
    .map((id) => records.find((record) => record.id === id))
    .filter((record): record is DisplayRecord => record !== undefined);
  if (rows.length === 0) return null;
  const label = t(reason === "strength_needed" ? "match.strength" : "match.didYouMean");

  return (
    <div>
      <p lang={label.locale}>{label.text}</p>
      <ul className="choice-list">
        {rows.map((record) => (
          <li key={record.id}>
            <button type="button" className="btn btn-secondary" onClick={() => onPick(record.id)}>
              <span lang={label.locale}>{label.text}</span> {record.brandName}
            </button>
          </li>
        ))}
      </ul>
    </div>
  );
}
