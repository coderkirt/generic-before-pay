"use client";

import { formatInr } from "@/lib/data/format";
import type { DisplayRecord } from "@/lib/data/types";
import type { MessageKey } from "@/lib/i18n/en";
import { useI18n } from "@/lib/i18n/context";
import type { LineStatus, PricedLine } from "@/lib/pricing/compare";
import { comparisonEligibility } from "@/lib/pricing/eligibility";
import type { RxLine } from "@/lib/session/reducer";
import { MatchStatus } from "@/components/MatchStatus";

const STATUS_KEY: Record<LineStatus, MessageKey> = {
  same_composition_comparable: "price.same",
  different_strength: "price.strength",
  combination_drug: "price.composition",
  unit_mismatch: "price.unit",
  no_equivalent: "price.none",
  missing_data: "price.missing",
  unconfirmed_match: "price.hidden",
};

export function MedicineCard({
  line,
  record,
  priced,
  catalogOk = true,
}: {
  line: RxLine;
  record: DisplayRecord | undefined;
  priced: PricedLine;
  catalogOk?: boolean;
}) {
  const { t } = useI18n();
  const eligibility = comparisonEligibility({
    catalogOk,
    tier: line.tier,
    confirmed: line.confirmed,
    status: priced.status,
  });
  const showPrice = eligibility === "verified" && priced.brandLineTotal !== null && priced.genericLineTotal !== null;
  const status = t(STATUS_KEY[priced.status]);
  const hidden = t("price.hidden");
  const info = t("info.missing");
  const source = t("results.source");
  const noDate = t("results.noDate");
  const brand = t("results.brand");
  const generic = t("results.generic");
  const perUnit = t("results.perUnit");
  const title = record?.brandName ?? line.query;

  return (
    <article className="medicine-row" data-eligibility={eligibility}>
      <h3>{title}</h3>
      <MatchStatus tier={line.tier} />
      <p lang={status.locale}>{status.text}</p>
      {showPrice && priced.brandLineTotal !== null && priced.genericLineTotal !== null ? (
        <>
          <p className="price-pair">
            <span>{formatInr(priced.brandLineTotal)}</span>
            <span aria-hidden="true"> → </span>
            <span className="sr-only"> to </span>
            <span>{formatInr(priced.genericLineTotal)}</span>
          </p>
          <p>
            <span lang={brand.locale}>{brand.text}</span> {formatInr(priced.brandLineTotal)}
          </p>
          <p>
            <span lang={generic.locale}>{generic.text}</span> {formatInr(priced.genericLineTotal)}
          </p>
          {priced.brandPerUnit !== null && priced.genericPerUnit !== null ? (
            <p>
              <span lang={perUnit.locale}>{perUnit.text}</span> {formatInr(priced.brandPerUnit)}
              <span aria-hidden="true"> → </span>
              <span className="sr-only"> to </span>
              {formatInr(priced.genericPerUnit)}
            </p>
          ) : null}
          <p>
            <span lang={source.locale}>{source.text}</span>: {record?.source}
          </p>
          <p lang={noDate.locale}>{noDate.text}</p>
        </>
      ) : line.confirmed ? null : (
        <p lang={hidden.locale}>{hidden.text}</p>
      )}
      <p lang={info.locale}>{info.text}</p>
    </article>
  );
}
