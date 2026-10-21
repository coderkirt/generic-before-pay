"""Handwriting pipeline ported from doctors-prescription (OpenCV + EMNIST TFLite).

Best-effort only. Candidates are still unverified text and must be confirmed by the user.
Never used to invent drug facts, doses, or substitution advice.
"""
from __future__ import annotations

import asyncio
from pathlib import Path

import numpy as np
from PIL import Image
import io

from .base import OcrResult, OcrUnavailable

# EMNIST balanced 47 classes, same order as the source Android interpreter.
EMNIST_CLASSES = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabdefghnqrt"
MODEL_PATH = Path(__file__).parent / "models" / "handwriting.tflite"
HANDWRITING_NOTICE = (
    "Handwriting may be read incorrectly. Please check each item against the prescription. "
    "Candidates are text read from the image, not verified matches."
)


def _cv2():
    try:
        import cv2
    except ImportError as exc:
        raise OcrUnavailable("OpenCV is not installed") from exc
    return cv2


def decode_bgr(image: bytes):
    cv2 = _cv2()
    arr = np.frombuffer(image, dtype=np.uint8)
    mat = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    if mat is None:
        pil = Image.open(io.BytesIO(image)).convert("RGB")
        mat = cv2.cvtColor(np.array(pil), cv2.COLOR_RGB2BGR)
    return mat


def preprocess_handwriting(bgr, max_side: int = 1200):
    """Steps 1–4 from the source pipeline, keeping aspect ratio (300px square is too small for a full Rx)."""
    cv2 = _cv2()
    h, w = bgr.shape[:2]
    scale = min(1.0, max_side / max(h, w))
    if scale < 1.0:
        bgr = cv2.resize(bgr, (int(w * scale), int(h * scale)))
    gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
    cv2.normalize(gray, gray, 0, 255, cv2.NORM_MINMAX)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
    gray = cv2.morphologyEx(gray, cv2.MORPH_OPEN, kernel)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    gray = clahe.apply(gray)
    _, binary = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    return bgr, gray, binary, scale


def group_rects(rects: list[tuple[int, int, int, int]], image_h: int) -> list[list[tuple[int, int, int, int]]]:
    """Group character boxes into words/lines by similar y, then sort by x (source Android logic)."""
    y_tol = max(12, int(50 * (image_h / 300)))
    min_area = max(20, int(60 * ((image_h / 300) ** 2)))
    unmatched = [r for r in rects if abs(r[2] - r[0]) * abs(r[3] - r[1]) >= min_area]
    groups: list[list[tuple[int, int, int, int]]] = []
    while unmatched:
        current = unmatched.pop(0)
        matches = [current]
        rest: list[tuple[int, int, int, int]] = []
        for rect in unmatched:
            if abs(rect[1] - current[1]) < y_tol:
                matches.append(rect)
            else:
                rest.append(rect)
        matches.sort(key=lambda r: r[0])
        groups.append(matches)
        unmatched = rest
    groups.sort(key=lambda g: g[0][1])
    return groups


def find_char_rects(binary) -> list[tuple[int, int, int, int]]:
    cv2 = _cv2()
    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    rects = []
    for c in contours:
        x, y, w, h = cv2.boundingRect(c)
        if w < 2 or h < 6:
            continue
        rects.append((x, y, x + w, y + h))
    return rects


def _load_interpreter():
    if not MODEL_PATH.is_file():
        return None
    try:
        from ai_edge_litert.interpreter import Interpreter
        return Interpreter(model_path=str(MODEL_PATH))
    except Exception:
        pass
    try:
        from tensorflow.lite.python.interpreter import Interpreter
        return Interpreter(model_path=str(MODEL_PATH))
    except Exception:
        return None


def classify_chars(binary, groups: list[list[tuple[int, int, int, int]]]) -> list[str]:
    """EMNIST CNN on each cropped character. Returns one string per word group."""
    cv2 = _cv2()
    interpreter = _load_interpreter()
    if interpreter is None:
        return []
    interpreter.allocate_tensors()
    inp = interpreter.get_input_details()[0]
    out = interpreter.get_output_details()[0]
    in_h, in_w = int(inp["shape"][1]), int(inp["shape"][2])
    words: list[str] = []
    for group in groups:
        chars: list[str] = []
        for x1, y1, x2, y2 in group:
            crop = binary[max(0, y1):max(0, y2), max(0, x1):max(0, x2)]
            if crop.size == 0:
                continue
            crop = cv2.resize(crop, (18, 18))
            crop = cv2.copyMakeBorder(crop, 5, 5, 5, 5, cv2.BORDER_CONSTANT, value=0)
            crop = cv2.resize(crop, (int(in_w), int(in_h)))
            tensor = (crop.astype(np.float32) / 255.0).reshape(1, int(in_h), int(in_w), 1)
            if inp["dtype"] != np.float32:
                tensor = tensor.astype(inp["dtype"])
            interpreter.set_tensor(inp["index"], tensor)
            interpreter.invoke()
            scores = interpreter.get_tensor(out["index"])[0]
            idx = int(np.argmax(scores))
            if 0 <= idx < len(EMNIST_CLASSES):
                chars.append(EMNIST_CLASSES[idx])
        word = "".join(chars).strip()
        if len(word) >= 3:
            words.append(word)
    return words


def run_pipeline(image: bytes) -> list[str]:
    bgr = decode_bgr(image)
    _color, _gray, binary, _scale = preprocess_handwriting(bgr)
    groups = group_rects(find_char_rects(binary), binary.shape[0])
    return classify_chars(binary, groups)


class HandwritingOcrProvider:
    """OpenCV + EMNIST TFLite, with optional Gemini/Gemma fallback for the same photo."""

    name = "handwriting"

    def __init__(self, fallback=None):
        self._fallback = fallback

    async def extract(self, image: bytes, mime: str, language: str, **kwargs) -> OcrResult:
        kwargs = {**kwargs, "handwriting": True}
        words: list[str] = []
        try:
            words = await asyncio.to_thread(run_pipeline, image)
        except OcrUnavailable:
            words = []
        except Exception:
            words = []
        text = "\n".join(words)
        if self._fallback is not None:
            extra = await self._fallback.extract(image, mime, language, **kwargs)
            merged = list(dict.fromkeys([*words, *extra.candidates]))
            blob = extra.text if extra.text else text
            if words and extra.text:
                blob = extra.text + "\n" + text
            return OcrResult(text=blob, candidates=merged or extra.candidates,
                             provider=f"{extra.provider}+handwriting", mock=extra.mock)
        if not words:
            raise OcrUnavailable("Handwriting model produced no text")
        return OcrResult(text=text, candidates=words, provider=self.name)

    async def check(self) -> bool:
        try:
            _cv2()
        except OcrUnavailable:
            return self._fallback is not None
        return MODEL_PATH.is_file() or self._fallback is not None
