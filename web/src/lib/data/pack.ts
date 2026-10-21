export type ParsedPack = {
  packSize: number | null;
  form: string | null;
  perUnitLabel: string | null;
};

const STRIP = /^strip of (\d+) (tablets|capsules)$/i;
const BOTTLE = /^(\d+) ml bottle$/i;

/** Read pack size only when the unit string is unambiguous. Otherwise leave it missing. */
export function parseUnit(unit: string): ParsedPack {
  const text = unit.trim().replace(/\s+/g, " ");
  const strip = STRIP.exec(text);
  if (strip?.[1] && strip[2]) {
    const packSize = Number(strip[1]);
    if (Number.isInteger(packSize) && packSize > 0) {
      const form = strip[2].toLowerCase() === "tablets" ? "tablet" : "capsule";
      return { packSize, form, perUnitLabel: form };
    }
  }
  const bottle = BOTTLE.exec(text);
  if (bottle?.[1]) {
    const packSize = Number(bottle[1]);
    if (Number.isInteger(packSize) && packSize > 0) {
      return { packSize, form: "bottle", perUnitLabel: "ml" };
    }
  }
  return { packSize: null, form: null, perUnitLabel: null };
}
