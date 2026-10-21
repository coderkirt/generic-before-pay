import type { DisplayRecord } from "@/lib/data/types";
import { compareLine, type PricedLine, type PriceSide } from "@/lib/pricing/compare";
import type { RxLine } from "@/lib/session/reducer";

export function priceLine(line: RxLine, record: DisplayRecord | undefined): PricedLine {
  const confirmed = line.confirmed && line.selectedId !== null && record !== undefined;
  return compareLine({
    confirmed,
    tier: confirmed ? "exact" : line.tier === "none" ? "none" : "uncertain",
    quantity: line.quantity,
    brand: record ? side(record, record.brandedPackPrice) : null,
    generic: record ? side(record, record.genericPackPrice) : null,
  });
}

function side(record: DisplayRecord, packPrice: number): PriceSide {
  return {
    composition: record.composition,
    strength: record.strength,
    form: record.form,
    packSize: record.packSize,
    packPrice,
    source: record.source,
    priceDate: null,
  };
}
