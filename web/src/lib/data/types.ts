/** Provenance of a bundled dataset. Fixture and mock must stay visible in the UI. */
export type Provenance = "production" | "fixture" | "mock";

/** One row of data/curated_drugs.json after normalisation. Field names match the repo schema. */
export type DrugRecord = {
  id: string;
  brand_name: string;
  molecule: string;
  strength: string;
  unit: string;
  branded_price: number;
  generic_price: number;
  savings_amount: number;
  savings_percentage: number;
  source: string;
  aliases: string[];
};

/**
 * What the UI is allowed to show for one row.
 * priceDate stays null until the repo schema has a date.
 * medicineInfo stays null because the curated file has no uses or class field.
 */
export type DisplayRecord = {
  id: string;
  brandName: string;
  composition: string;
  strength: string;
  unit: string;
  form: string | null;
  packSize: number | null;
  perUnitLabel: string | null;
  brandedPackPrice: number;
  genericPackPrice: number;
  brandedPerUnit: number | null;
  genericPerUnit: number | null;
  source: string;
  priceDate: null;
  aliases: string[];
  provenance: Provenance;
  medicineInfo: null;
};

export type CatalogFile = {
  provenance: Provenance;
  priceDate: null;
  disclaimer: string;
  sourceFile: string;
  contentSha256: string;
  records: DrugRecord[];
};

export type LoadOutcome =
  | {
      ok: true;
      provenance: Provenance;
      priceDate: null;
      disclaimer: string;
      contentSha256: string;
      records: DisplayRecord[];
    }
  | {
      ok: false;
      provenance: Provenance;
      priceDate: null;
      disclaimer: string;
      records: [];
      problems: string[];
    };
