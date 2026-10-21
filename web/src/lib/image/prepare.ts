import { OCR_MAX_BYTES } from "@/lib/ocr/types";

const TYPES = new Set(["image/jpeg", "image/png", "image/webp"]);
const MAX_EDGE = 1600;
const MAX_PIXELS = 25_000_000;

export type ImageProblem = "empty" | "type" | "too_big";

export function classifyImage(file: { size: number; type: string }): ImageProblem | null {
  if (file.size <= 0) return "empty";
  if (!TYPES.has(file.type)) return "type";
  return null;
}

export async function prepareImage(file: File): Promise<{ blob: Blob } | { problem: ImageProblem }> {
  const problem = classifyImage(file);
  if (problem) return { problem };
  if (file.size <= OCR_MAX_BYTES && file.type === "image/jpeg") {
    return { blob: file };
  }
  const blob = await compressImage(file);
  if (!blob) return { problem: "type" };
  if (blob.size > OCR_MAX_BYTES) return { problem: "too_big" };
  return { blob };
}

async function compressImage(file: File): Promise<Blob | null> {
  if (typeof createImageBitmap !== "function") {
    return file.size <= OCR_MAX_BYTES ? file : null;
  }
  const bitmap = await createImageBitmap(file).catch(() => null);
  if (!bitmap) return null;
  const longest = Math.max(bitmap.width, bitmap.height);
  const pixelScale = Math.sqrt(MAX_PIXELS / Math.max(1, bitmap.width * bitmap.height));
  const scale = Math.min(1, MAX_EDGE / longest, pixelScale);
  const canvas = document.createElement("canvas");
  canvas.width = Math.max(1, Math.round(bitmap.width * scale));
  canvas.height = Math.max(1, Math.round(bitmap.height * scale));
  const context = canvas.getContext("2d");
  if (!context) {
    bitmap.close();
    return null;
  }
  context.drawImage(bitmap, 0, 0, canvas.width, canvas.height);
  bitmap.close();
  const blob = await new Promise<Blob | null>((resolve) => canvas.toBlob((value) => resolve(value), "image/jpeg", 0.72));
  return blob;
}
