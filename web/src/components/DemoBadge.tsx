"use client";

import { useI18n } from "@/lib/i18n/context";
import { loadBundledCatalog } from "@/lib/data/load";

export function DemoBadge() {
  const { t } = useI18n();
  const catalog = loadBundledCatalog();
  if (catalog.ok && catalog.provenance === "production") return null;
  const label = t("demo.badge");
  return (
    <span className="badge" lang={label.locale} data-provenance={catalog.provenance}>
      {label.text}
    </span>
  );
}
