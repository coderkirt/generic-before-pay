"use client";

import { formatInr } from "@/lib/data/format";
import { useI18n } from "@/lib/i18n/context";
import type { PriceTotals } from "@/lib/pricing/compare";

export function SavingCard({ totals }: { totals: PriceTotals }) {
  const { t } = useI18n();
  if (totals.countedLines === 0) return null;
  const heading = t(totals.label === "listed saving" ? "price.saving" : "price.difference");
  const brand = t("results.brand");
  const generic = t("results.generic");
  const notLower = t("results.notLower");

  return (
    <section aria-labelledby="saving-heading" className="saving">
      <h2 id="saving-heading" lang={heading.locale}>
        {heading.text}
      </h2>
      <p className="price-pair">
        <span>{formatInr(totals.brandTotal)}</span>
        <span aria-hidden="true"> → </span>
        <span className="sr-only"> to </span>
        <span>{formatInr(totals.genericTotal)}</span>
      </p>
      <p>
        <span lang={brand.locale}>{brand.text}</span> {formatInr(totals.brandTotal)}
      </p>
      <p>
        <span lang={generic.locale}>{generic.text}</span> {formatInr(totals.genericTotal)}
      </p>
      <p lang={heading.locale}>
        {heading.text}: {formatInr(totals.listedDifference)}
      </p>
      {totals.listedDifference <= 0 ? <p lang={notLower.locale}>{notLower.text}</p> : null}
    </section>
  );
}
