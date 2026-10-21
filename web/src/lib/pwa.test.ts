import { readFileSync } from "node:fs";
import path from "node:path";
import { describe, expect, it } from "vitest";

describe("service worker", () => {
  it("versions the cache and does not store non-GET or OCR requests", () => {
    const source = readFileSync(path.resolve(import.meta.dirname, "../../public/sw.js"), "utf8");
    expect(source).toContain("generic-before-pay-v1");
    expect(source).toContain('request.method !== "GET"');
    expect(source).toContain('url.pathname.startsWith("/v1/")');
  });
});
