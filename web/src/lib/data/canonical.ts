import { createHash } from "node:crypto";
import type { DrugRecord } from "@/lib/data/types";

/**
 * SHA-256 of the same canonical JSON scripts/validate_and_normalize.py hashes:
 * json.dumps(records, sort_keys=True, separators=(',', ':')).
 * Integral floats are written as 5.0 so they match Python's json encoder.
 */
export function contentSha256(records: DrugRecord[]): string {
  const canonical = `[${records.map((record) => encodeObject(record)).join(",")}]`;
  return createHash("sha256").update(canonical, "utf8").digest("hex");
}

function encode(value: unknown): string {
  if (typeof value === "string") return JSON.stringify(value);
  if (typeof value === "number") return encodeNumber(value);
  if (typeof value === "boolean") return value ? "true" : "false";
  if (value === null) return "null";
  if (Array.isArray(value)) return `[${value.map((item) => encode(item)).join(",")}]`;
  if (typeof value === "object") return encodeObject(value as Record<string, unknown>);
  throw new Error("Cannot canonicalise this value");
}

function encodeObject(value: Record<string, unknown>): string {
  const keys = Object.keys(value).sort();
  return `{${keys.map((key) => `${JSON.stringify(key)}:${encode(value[key])}`).join(",")}}`;
}

function encodeNumber(value: number): string {
  const two = value.toFixed(2);
  if (two.endsWith("00")) return `${two.slice(0, -1)}`;
  if (two.endsWith("0")) return two.slice(0, -1);
  return two;
}
