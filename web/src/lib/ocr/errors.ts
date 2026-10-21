import { OCR_NOTICE, type OcrFailureCode, type OcrResult } from "@/lib/ocr/types";

export function parseOcrBody(body: unknown): OcrResult | null {
  if (body === null || typeof body !== "object") return null;
  const value = body as Record<string, unknown>;
  if (typeof value.text !== "string" || !Array.isArray(value.candidates)) return null;
  if (!value.candidates.every((item) => typeof item === "string")) return null;
  const language = value.language === "hi" ? "hi" : "en";
  return {
    requestId: typeof value.request_id === "string" ? value.request_id : "",
    text: value.text,
    candidates: value.candidates as string[],
    language,
    provider: typeof value.provider === "string" ? value.provider : "unknown",
    mock: value.mock === true,
    preprocessed: value.preprocessed === true,
    notice: typeof value.notice === "string" && value.notice.length > 0 ? value.notice : OCR_NOTICE,
  };
}

export function codeFromStatus(status: number): OcrFailureCode {
  if (status === 413) return "FILE_TOO_LARGE";
  if (status === 415) return "UNSUPPORTED_IMAGE";
  if (status === 429) return "RATE_LIMITED";
  if (status === 502) return "OCR_BAD_OUTPUT";
  if (status === 503) return "OCR_UNAVAILABLE";
  if (status === 504) return "OCR_TIMEOUT";
  return "OCR_UNAVAILABLE";
}

export function codeFromEnvelope(body: unknown, status: number): OcrFailureCode {
  if (body !== null && typeof body === "object") {
    const error = (body as { error?: { code?: unknown } }).error;
    const code = error?.code;
    if (code === "FILE_TOO_LARGE" || code === "IMAGE_TOO_LARGE") return "FILE_TOO_LARGE";
    if (code === "UNSUPPORTED_IMAGE") return "UNSUPPORTED_IMAGE";
    if (code === "RATE_LIMITED") return "RATE_LIMITED";
    if (code === "OCR_BAD_OUTPUT") return "OCR_BAD_OUTPUT";
    if (code === "OCR_UNAVAILABLE" || code === "DATA_NOT_LOADED") return "OCR_UNAVAILABLE";
    if (code === "OCR_TIMEOUT") return "OCR_TIMEOUT";
  }
  return codeFromStatus(status);
}

export function retryAfterSeconds(header: string | null): number | null {
  if (!header) return null;
  const seconds = Number(header);
  if (Number.isFinite(seconds) && seconds >= 0) return seconds;
  const date = Date.parse(header);
  if (Number.isNaN(date)) return null;
  return Math.max(0, Math.ceil((date - Date.now()) / 1000));
}

export function messageKeyForCode(code: OcrFailureCode): "scan.tooBig" | "scan.invalid" | "scan.rate" | "scan.bad" | "scan.unavailable" | "scan.timeout" | "scan.network" | "scan.offline" | "scan.denied" | "scan.empty" {
  switch (code) {
    case "FILE_TOO_LARGE":
      return "scan.tooBig";
    case "UNSUPPORTED_IMAGE":
      return "scan.invalid";
    case "RATE_LIMITED":
      return "scan.rate";
    case "OCR_BAD_OUTPUT":
      return "scan.bad";
    case "OCR_TIMEOUT":
      return "scan.timeout";
    case "NETWORK":
      return "scan.network";
    case "OFFLINE":
      return "scan.offline";
    case "CAMERA_DENIED":
      return "scan.denied";
    case "EMPTY_IMAGE":
      return "scan.empty";
    case "OCR_UNAVAILABLE":
      return "scan.unavailable";
  }
}
