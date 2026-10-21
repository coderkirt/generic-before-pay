import { DISCLAIMER } from "@/lib/copy/approved";
import { contentSha256 } from "@/lib/data/canonical";
import type { CatalogFile, Provenance } from "@/lib/data/types";
import { validateDrugList } from "@/lib/data/validate";

/** Used by the sync script and Node tests. Not imported by client components (it hashes with node:crypto). */
export function buildCatalogFile(
  raw: unknown,
  provenance: Provenance = "fixture",
): { ok: true; file: CatalogFile } | { ok: false; problems: string[] } {
  const validated = validateDrugList(raw);
  if (!validated.ok) return validated;
  return {
    ok: true,
    file: {
      provenance,
      priceDate: null,
      disclaimer: DISCLAIMER,
      sourceFile: "data/curated_drugs.json",
      contentSha256: contentSha256(validated.records),
      records: validated.records,
    },
  };
}
