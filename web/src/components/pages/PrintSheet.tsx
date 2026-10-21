"use client";

import { DisclaimerBlock } from "@/components/DisclaimerBlock";
import { DemoBadge } from "@/components/DemoBadge";
import { MedicineCard } from "@/components/MedicineCard";
import { SavingCard } from "@/components/SavingCard";
import { loadBundledCatalog } from "@/lib/data/load";
import { useI18n } from "@/lib/i18n/context";
import { BUNDLED_KENDRAS } from "@/lib/kendra/nearest";
import { sumLines } from "@/lib/pricing/compare";
import { priceLine } from "@/lib/pricing/selection";
import { useSession } from "@/lib/session/context";

export function PrintSheet() {
  const { t } = useI18n();
  const { state } = useSession();
  const catalog = loadBundledCatalog();
  const records = catalog.ok ? catalog.records : [];
  const h1 = t("print.h1");
  const person = t("print.patient");
  const none = t("print.none");
  const kendra = t("print.kendra");
  const noKendra = t("print.noKendra");
  const hindi = t("print.hindiMissing");
  const print = t("action.print");
  const need = t("patient.need");

  if (!state.patient.confirmed) {
    return (
      <div className="stack">
        <h1 lang={h1.locale}>{h1.text}</h1>
        <p lang={need.locale}>{need.text}</p>
      </div>
    );
  }

  const genderKey =
    state.patient.gender === "female"
      ? "patient.gender.female"
      : state.patient.gender === "male"
        ? "patient.gender.male"
        : state.patient.gender === "other"
          ? "patient.gender.other"
          : "patient.gender.unsaid";
  const gender = t(genderKey);
  const priced = state.lines
    .filter((line) => line.confirmed)
    .map((line) => {
      const record = records.find((item) => item.id === line.selectedId);
      return { line, record, priced: priceLine(line, record) };
    });
  const totals = sumLines(priced.map((item) => item.priced));

  return (
    <article className="stack print-sheet">
      <h1 lang={h1.locale}>{h1.text}</h1>
      <DemoBadge />
      <p>
        <span lang={person.locale}>{person.text}</span>: {state.patient.ageYears}-
        <span lang={gender.locale}>{gender.text}</span>
      </p>
      {priced.length === 0 ? <p lang={none.locale}>{none.text}</p> : null}
      <SavingCard totals={totals} />
      {priced.map((item) => (
        <MedicineCard key={item.line.key} line={item.line} record={item.record} priced={item.priced} />
      ))}
      <section>
        <h2 lang={kendra.locale}>{kendra.text}</h2>
        {BUNDLED_KENDRAS.length === 0 ? <p lang={noKendra.locale}>{noKendra.text}</p> : null}
      </section>
      <section lang="en">
        <DisclaimerBlock />
      </section>
      <p lang={hindi.locale}>{hindi.text}</p>
      <div className="actions no-print">
        <button type="button" className="btn btn-primary" lang={print.locale} onClick={() => window.print()}>
          {print.text}
        </button>
      </div>
    </article>
  );
}
