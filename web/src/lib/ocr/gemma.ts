import { codeFromEnvelope, parseOcrBody, retryAfterSeconds } from "@/lib/ocr/errors";
import { OCR_TIMEOUT_MS, OcrClientError, type OcrProvider, type OcrReadOptions, type OcrResult } from "@/lib/ocr/types";

export class GemmaBackendProvider implements OcrProvider {
  constructor(
    private readonly endpoint = "/v1/ocr",
    private readonly timeoutMs = OCR_TIMEOUT_MS,
  ) {}

  async readText(image: Blob, opts: OcrReadOptions): Promise<OcrResult> {
    const controller = new AbortController();
    const onAbort = () => controller.abort();
    opts.signal.addEventListener("abort", onAbort);
    let timedOut = false;
    const timeoutTimer = setTimeout(() => {
      timedOut = true;
      controller.abort();
    }, this.timeoutMs);

    try {
      const body = new FormData();
      body.append("file", image, "prescription.jpg");
      body.append("language", opts.lang ?? "en");
      body.append("preprocess", "true");
      body.append("handwriting", opts.handwriting ? "true" : "false");
      const requestId = newRequestId();
      const response = await fetch(this.endpoint, {
        method: "POST",
        body,
        signal: controller.signal,
        headers: { "X-Request-ID": requestId, Accept: "application/json" },
      });
      const payload: unknown = await response.json().catch(() => null);
      if (!response.ok) {
        throw new OcrClientError(
          codeFromEnvelope(payload, response.status),
          retryAfterSeconds(response.headers.get("Retry-After")),
        );
      }
      const parsed = parseOcrBody(payload);
      if (!parsed || (parsed.text.trim() === "" && parsed.candidates.length === 0)) {
        throw new OcrClientError("OCR_BAD_OUTPUT");
      }
      return { ...parsed, requestId: parsed.requestId || requestId };
    } catch (error) {
      if (error instanceof OcrClientError) throw error;
      if (timedOut) throw new OcrClientError("OCR_TIMEOUT");
      if (opts.signal.aborted) throw error;
      if (typeof navigator !== "undefined" && navigator.onLine === false) throw new OcrClientError("OFFLINE");
      throw new OcrClientError("NETWORK");
    } finally {
      clearTimeout(timeoutTimer);
      opts.signal.removeEventListener("abort", onAbort);
    }
  }
}

function newRequestId(): string {
  const bytes = new Uint8Array(8);
  crypto.getRandomValues(bytes);
  return Array.from(bytes, (byte) => byte.toString(16).padStart(2, "0")).join("");
}
