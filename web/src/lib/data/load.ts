import { DISCLAIMER } from "@/lib/copy/approved";
import { toDisplayRecord } from "@/lib/data/display";
import type { CatalogFile, LoadOutcome, Provenance } from "@/lib/data/types";
import { validateDrugList } from "@/lib/data/validate";
import catalogFile from "@/data/catalog.json";

const PROVENANCE: readonly Provenance[] = ["production", "fixture", "mock"];

export function loadCatalog(raw: unknown, mode: "strict" | "degrade"): LoadOutcome {
  const outcome = interpret(raw);
  if (!outcome.ok && mode === "strict") {
    throw new Error(outcome.problems.join("\n"));
  }
  return outcome;
}

export function loadBundledCatalog(): LoadOutcome {
  const mode = process.env.NODE_ENV === "production" ? "degrade" : "strict";
  return loadCatalog(catalogFile, mode);
}

function interpret(raw: unknown): LoadOutcome {
  if (raw === null || typeof raw !== "object" || Array.isArray(raw)) {
    return failed(["Catalog must be an object."], "fixture");
  }
  const file = raw as Partial<CatalogFile>;
  const provenance = PROVENANCE.includes(file.provenance as Provenance)
    ? (file.provenance as Provenance)
    : null;
  if (!provenance) {
    return failed(["Catalog provenance must be production, fixture, or mock."], "fixture");
  }
  if (file.priceDate !== null) {
    return failed(["Catalog priceDate must be null until the repo schema has a date."], provenance);
  }
  if (file.disclaimer !== DISCLAIMER) {
    return failed(["Catalog disclaimer does not match the repo text."], provenance);
  }
  const validated = validateDrugList(file.records);
  if (!validated.ok) return failed(validated.problems, provenance);
  return {
    ok: true,
    provenance,
    priceDate: null,
    disclaimer: DISCLAIMER,
    contentSha256: typeof file.contentSha256 === "string" ? file.contentSha256 : "",
    records: validated.records.map((record) => toDisplayRecord(record, provenance)),
  };
}

function failed(problems: string[], provenance: Provenance): LoadOutcome {
  return {
    ok: false,
    provenance,
    priceDate: null,
    disclaimer: DISCLAIMER,
    records: [],
    problems,
  };
}
