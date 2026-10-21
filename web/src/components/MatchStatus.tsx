"use client";

import type { Tier } from "@/lib/matching/match";
import type { MessageKey } from "@/lib/i18n/en";
import { useI18n } from "@/lib/i18n/context";

const KEY: Record<Tier, MessageKey> = {
  exact: "match.exact",
  likely: "match.likely",
  uncertain: "match.uncertain",
  none: "match.none",
};

const MARK: Record<Tier, string> = {
  exact: "✓",
  likely: "●",
  uncertain: "?",
  none: "–",
};

export function MatchStatus({ tier }: { tier: Tier }) {
  const { t } = useI18n();
  const label = t(KEY[tier]);
  return (
    <p className="status-line">
      <span aria-hidden="true">{MARK[tier]}</span>{" "}
      <span lang={label.locale}>{label.text}</span>
    </p>
  );
}
