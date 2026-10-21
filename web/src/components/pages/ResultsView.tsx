"use client";

import Link from "next/link";
import { MedicineCard } from "@/components/MedicineCard";
import { SavingCard } from "@/components/SavingCard";
import { loadBundledCatalog } from "@/lib/data/load";
import { useI18n } from "@/lib/i18n/context";
import { sumLines } from "@/lib/pricing/compare";
import { priceLine } from "@/lib/pricing/selection";
import { useSession } from "@/lib/session/context";

export function ResultsView() {
  const { t } = useI18n();
  const { state } = useSession();
  const catalog = loadBundledCatalog();
  const records = catalog.ok ? catalog.records : [];
  const h1 = t("results.h1");
  const empty = t("results.empty");
  const partial = t("results.partial");
  const need = t("patient.need");
  const next = t("action.continue");

  if (!state.patient.confirmed) {
    return (
      <div className="stack">
        <h1 lang={h1.locale}>{h1.text}</h1>
        <p lang={need.locale}>{need.text}</p>
        <Link className="btn btn-primary" href="/patient">
          {t("step.patient").text}
        </Link>
      </div>
    );
  }

  const priced = state.lines.map((line) => {
    const record = records.find((item) => item.id === line.selectedId);
    return { line, record, priced: priceLine(line, line.confirmed ? record : undefined) };
  });
  const totals = sumLines(priced.map((item) => item.priced));
  const anyHidden = priced.some((item) => !item.priced.countsTowardTotal);

  return (
    <div className="stack">
      <h1 lang={h1.locale}>{h1.text}</h1>
      <SavingCard totals={totals} />
      {totals.countedLines === 0 ? <p lang={empty.locale}>{empty.text}</p> : null}
      {anyHidden ? <p lang={partial.locale}>{partial.text}</p> : null}
      {priced.map((item) => (
        <MedicineCard key={item.line.key} line={item.line} record={item.record} priced={item.priced} />
      ))}
      <div className="actions no-print">
        <Link className="btn btn-primary" href="/kendras" lang={next.locale}>
          {next.text}
        </Link>
      </div>
    </div>
  );
}
