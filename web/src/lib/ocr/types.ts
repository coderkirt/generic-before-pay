export const OCR_MAX_BYTES = 5 * 1024 * 1024;
export const OCR_TIMEOUT_MS = 25_000;

export type OcrResult = {
  requestId: string;
  text: string;
  candidates: string[];
  language: "en" | "hi";
  provider: string;
  mock: boolean;
  preprocessed: boolean;
  notice: string;
};

export type OcrFailureCode =
  | "FILE_TOO_LARGE"
  | "UNSUPPORTED_IMAGE"
  | "RATE_LIMITED"
  | "OCR_BAD_OUTPUT"
  | "OCR_UNAVAILABLE"
  | "OCR_TIMEOUT"
  | "NETWORK"
  | "OFFLINE"
  | "CAMERA_DENIED"
  | "EMPTY_IMAGE";

export class OcrClientError extends Error {
  readonly code: OcrFailureCode;
  readonly retryAfter: number | null;

  constructor(code: OcrFailureCode, retryAfter: number | null = null) {
    super(code);
    this.name = "OcrClientError";
    this.code = code;
    this.retryAfter = retryAfter;
  }
}

export interface OcrProvider {
  readText(image: Blob, opts: { signal: AbortSignal; lang?: "en" | "hi" }): Promise<OcrResult>;
}

/** Fixed notice. Server notice text is not rendered, so a model cannot supply facts. */
export const OCR_NOTICE =
  "Candidates are text read from the image, not verified matches. Please check each one.";
