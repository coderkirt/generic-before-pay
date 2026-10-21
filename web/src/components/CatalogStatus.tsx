"use client";

import { useI18n } from "@/lib/i18n/context";
import type { LoadOutcome } from "@/lib/data/types";

export function CatalogStatus({ outcome }: { outcome: LoadOutcome }) {
  const { t } = useI18n();
  if (outcome.ok) return null;
  const copy = t("data.unavailable");
  return (
    <p role="alert" lang={copy.locale}>
      {copy.text}
    </p>
  );
}
