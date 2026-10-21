import { describe, expect, it } from "vitest";
import { loadBundledCatalog } from "@/lib/data/load";
import { priceLine } from "@/lib/pricing/selection";
import { buildLine } from "@/lib/session/lines";

describe("selection pricing", () => {
  it("hides a price until the line is confirmed, including Crosin", () => {
    const catalog = loadBundledCatalog();
    if (!catalog.ok) throw new Error("catalog");
    const crosin = buildLine("Crosin", catalog.records, "crosin");
    expect(crosin.tier).toBe("uncertain");
    expect(crosin.confirmed).toBe(false);
    const hidden = priceLine(crosin, undefined);
    expect(hidden.brandPackPrice).toBeNull();
    expect(hidden.countsTowardTotal).toBe(false);

    const calpol = buildLine("Calpol 500", catalog.records, "calpol");
    const record = catalog.records.find((item) => item.id === calpol.selectedId);
    const open = priceLine(calpol, record);
    expect(open.countsTowardTotal).toBe(false);
    const closed = priceLine({ ...calpol, confirmed: true }, record);
    expect(closed.status).toBe("same_composition_comparable");
    expect(closed.brandLineTotal).toBe(32.5);
    expect(closed.genericLineTotal).toBe(5);
  });
});
