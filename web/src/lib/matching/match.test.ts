import { readFileSync } from "node:fs";
import path from "node:path";
import { describe, expect, it } from "vitest";
import { buildCatalogFile } from "@/lib/data/build";
import { toDisplayRecord } from "@/lib/data/display";
import type { DisplayRecord } from "@/lib/data/types";
import { matchLines, matchQuery } from "@/lib/matching/match";
import { MISSPELLINGS, SUITE_NOTE } from "@/lib/matching/suite";

const sourcePath = path.resolve(import.meta.dirname, "../../../../data/curated_drugs.json");
const source: unknown = JSON.parse(readFileSync(sourcePath, "utf8"));
const built = buildCatalogFile(source);
if (!built.ok) throw new Error(built.problems.join("\n"));
const records: DisplayRecord[] = built.file.records.map((record) => toDisplayRecord(record, "fixture"));

describe("matcher", () => {
  it("keeps the suite labelled as a stand-in for the missing shared file", () => {
    expect(SUITE_NOTE).toMatch(/Not the missing shared/);
    expect(MISSPELLINGS.length).toBeGreaterThanOrEqual(50);
  });

  it("resolves Crosin, Pantocid40, and metformine without a confidently wrong price", () => {
    const crosin = matchQuery("Crosin", records);
    expect(crosin.tier === "exact").toBe(false);
    expect(crosin.matches[0]?.id).toBe("paracetamol-500mg-tab");

    const pantocid = matchQuery("Pantocid40", records);
    expect(pantocid.tier).toBe("likely");
    expect(pantocid.matches[0]?.id).toBe("pantoprazole-40mg-tab");

    const metformin = matchQuery("metformine", records);
    expect(metformin.tier).not.toBe("exact");
    expect(metformin.tier).not.toBe("likely");
    expect(metformin.matches.map((match) => match.id).sort()).toEqual([
      "metformin-1000mg-sr-tab",
      "metformin-500mg-tab",
    ]);
  });

  it("reports tier accuracy and allows zero confidently wrong matches", () => {
    let correct = 0;
    let confidentWrong = 0;
    const misses: string[] = [];

    for (const item of MISSPELLINGS) {
      const result = matchQuery(item.input, records);
      const top = result.matches[0];
      const confident = result.tier === "exact" || result.tier === "likely";
      const allowed = item.id ? [item.id] : (item.ids ?? []);
      if (confident && (!top || !allowed.includes(top.id))) {
        confidentWrong += 1;
        misses.push(`${item.input} confidently ${result.tier} -> ${top?.id ?? "none"} score ${top?.score ?? 0}`);
      }
      const tierOk = result.tier === item.tier;
      const idsOk =
        item.tier === "none"
          ? result.matches.length === 0
          : item.tier === "uncertain"
            ? result.matches.length > 0 && result.matches.every((match) => (item.ids ?? []).includes(match.id))
            : top?.id === item.id;
      if (tierOk && idsOk) correct += 1;
      else if (!confident || (top && allowed.includes(top.id))) {
        misses.push(
          `${item.input} expected ${item.tier} ${item.id ?? item.ids?.join("|") ?? ""} got ${result.tier} ${result.matches.map((match) => `${match.id}:${match.score}`).join(", ")}`,
        );
      }
    }

    const accuracy = (correct / MISSPELLINGS.length) * 100;
    expect(confidentWrong, misses.join("\n")).toBe(0);
    expect(misses, misses.join("\n")).toEqual([]);
    expect(accuracy).toBeGreaterThanOrEqual(90);
  });

  it("matches ten lines without needing a worker", () => {
    const lines = ["Calpol 500", "Dolo650", "Crosin", "Pantocid40", "metformine", "Telma 40", "Azithral", "Pan-D", "Omez", "aspirin"];
    const started = performance.now();
    const results = matchLines(lines, records);
    const elapsed = performance.now() - started;
    expect(results).toHaveLength(10);
    expect(elapsed).toBeLessThan(200);
  });
});
