import { DISCLAIMER } from "@/lib/copy/approved";
import { OCR_NOTICE, type OcrProvider, type OcrResult } from "@/lib/ocr/types";

const MOCK_TEXT = "Calpol 500\nPantocid40";

export class MockOcrProvider implements OcrProvider {
  async readText(_image: Blob, opts: { signal: AbortSignal; lang?: "en" | "hi" }): Promise<OcrResult> {
    if (opts.signal.aborted) {
      throw new DOMException("Aborted", "AbortError");
    }
    return {
      requestId: "mock-ocr",
      text: MOCK_TEXT,
      candidates: ["Calpol 500", "Pantocid40"],
      language: opts.lang ?? "en",
      provider: "mock",
      mock: true,
      preprocessed: false,
      notice: OCR_NOTICE,
    };
  }
}

export function mockOcrDisclaimer(): string {
  return DISCLAIMER;
}
