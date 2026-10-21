import { describe, expect, it } from "vitest";
import { classifyImage } from "@/lib/image/prepare";

describe("image validation", () => {
  it("accepts jpeg, png, and webp and rejects empty or other types", () => {
    expect(classifyImage({ size: 10, type: "image/jpeg" })).toBeNull();
    expect(classifyImage({ size: 10, type: "image/png" })).toBeNull();
    expect(classifyImage({ size: 10, type: "image/webp" })).toBeNull();
    expect(classifyImage({ size: 0, type: "image/jpeg" })).toBe("empty");
    expect(classifyImage({ size: 10, type: "image/gif" })).toBe("type");
    expect(classifyImage({ size: 10, type: "text/plain" })).toBe("type");
  });
});
