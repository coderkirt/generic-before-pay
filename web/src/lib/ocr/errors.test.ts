import { describe, expect, it } from "vitest";
import { codeFromEnvelope, codeFromStatus, parseOcrBody, retryAfterSeconds } from "@/lib/ocr/errors";

describe("ocr contract parsing", () => {
  it("reads the zip success shape and rejects a body without text", () => {
    const parsed = parseOcrBody({
      request_id: "abc12345",
      text: "DOLO 650",
      candidates: ["DOLO 650"],
      language: "en",
      provider: "mock",
      mock: true,
      preprocessed: false,
      notice: "Check each one.",
    });
    expect(parsed?.text).toBe("DOLO 650");
    expect(parsed?.mock).toBe(true);
    expect(parseOcrBody({ text: 1, candidates: [] })).toBeNull();
    expect(parseOcrBody({ text: "", candidates: "nope" })).toBeNull();
  });

  it("maps status codes and the error envelope", () => {
    expect(codeFromStatus(413)).toBe("FILE_TOO_LARGE");
    expect(codeFromStatus(415)).toBe("UNSUPPORTED_IMAGE");
    expect(codeFromStatus(429)).toBe("RATE_LIMITED");
    expect(codeFromStatus(502)).toBe("OCR_BAD_OUTPUT");
    expect(codeFromStatus(503)).toBe("OCR_UNAVAILABLE");
    expect(codeFromStatus(504)).toBe("OCR_TIMEOUT");
    expect(codeFromEnvelope({ error: { code: "IMAGE_TOO_LARGE" } }, 400)).toBe("FILE_TOO_LARGE");
    expect(retryAfterSeconds("12")).toBe(12);
    expect(retryAfterSeconds(null)).toBeNull();
  });
});
