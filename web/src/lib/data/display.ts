import { NOT_IN_DATA } from "@/lib/copy/approved";
import { roundPaise } from "@/lib/data/money";
import { parseUnit } from "@/lib/data/pack";
import type { DisplayRecord, DrugRecord, Provenance } from "@/lib/data/types";

export function toDisplayRecord(record: DrugRecord, provenance: Provenance): DisplayRecord {
  const pack = parseUnit(record.unit);
  const perUnit = (price: number): number | null =>
    pack.packSize === null ? null : roundPaise(price / pack.packSize);

  return {
    id: record.id,
    brandName: record.brand_name,
    composition: record.molecule,
    strength: record.strength,
    unit: record.unit,
    form: pack.form,
    packSize: pack.packSize,
    perUnitLabel: pack.perUnitLabel,
    brandedPackPrice: record.branded_price,
    genericPackPrice: record.generic_price,
    brandedPerUnit: perUnit(record.branded_price),
    genericPerUnit: perUnit(record.generic_price),
    source: record.source,
    priceDate: null,
    aliases: record.aliases,
    provenance,
    medicineInfo: null,
  };
}

/** Curated file has no uses or class. Callers show this exact sentence. */
export function medicineInfoText(_record: DisplayRecord): typeof NOT_IN_DATA {
  return NOT_IN_DATA;
}
