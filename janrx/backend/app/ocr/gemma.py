"""Gemma vision OCR via any OpenAI-compatible chat-completions endpoint (Ollama, vLLM, llama.cpp...).

The model is a TEXT READER only. The prompt forbids everything else and the output is
re-validated in service.sanitize_candidates, but never rely on the prompt alone.
"""
import base64
import json
import re

import httpx

from ..config import Settings
from .base import OcrBadOutput, OcrResult, OcrTimeout, OcrUnavailable

PROMPT = """You are an OCR engine. Read the printed text visible in this image of a medicine box, strip, or printed prescription.
Rules:
- Output ONLY valid JSON: {{"text": "<all visible text, line by line>", "candidates": ["<medicine names exactly as printed>"]}}
- No markdown, no code fences, no explanation, no <think> block.
- Copy text exactly as printed. Do not correct spelling. Do not add anything that is not visible.
- "candidates" may contain only brand or molecule names that appear in the text.
- Do NOT output dosage instructions, uses, warnings, prices, alternatives, or advice of any kind.
- If nothing is legible, output {{"text": "", "candidates": []}}.
Language hint for the printed text: {language}"""

HANDWRITING_PROMPT = """You are an OCR engine. Read handwritten and printed medicine names visible in this prescription photo.
Rules:
- Output ONLY valid JSON: {{"text": "<all visible text, line by line>", "candidates": ["<medicine names exactly as written>"]}}
- No markdown, no code fences, no explanation.
- Copy text as written. Do not correct spelling. Do not add anything that is not visible.
- "candidates" may contain only brand or molecule names that appear in the text.
- Do NOT output dosage instructions, uses, warnings, prices, alternatives, or advice of any kind.
- If nothing is legible, output {{"text": "", "candidates": []}}.
Language hint: {language}"""

_FENCE = re.compile(r"^```(?:json)?\s*|\s*```$", re.I)
_THINK = re.compile(r"<think>[\s\S]*?</think>", re.I)


def _message_text(content: object) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts: list[str] = []
        for part in content:
            if isinstance(part, str):
                parts.append(part)
            elif isinstance(part, dict) and isinstance(part.get("text"), str):
                parts.append(part["text"])
        return "".join(parts)
    raise OcrBadOutput("Unexpected response shape")


def parse_model_json(content: str) -> tuple[str, list[str]]:
    """Accept raw JSON, fenced JSON, thinking-tags, or JSON buried in extra text."""
    cleaned = _FENCE.sub("", _THINK.sub("", content).strip())
    idx = cleaned.find("{")
    if idx < 0:
        raise OcrBadOutput("Model did not return the expected JSON")
    try:
        data, _ = json.JSONDecoder().raw_decode(cleaned[idx:])
    except (ValueError, json.JSONDecodeError) as exc:
        raise OcrBadOutput("Model did not return the expected JSON") from exc
    try:
        text, cands = data["text"], data["candidates"]
        if not isinstance(text, str) or not isinstance(cands, list):
            raise ValueError("wrong types")
        return text, [c for c in cands if isinstance(c, str)]
    except (ValueError, KeyError, TypeError) as exc:
        raise OcrBadOutput("Model did not return the expected JSON") from exc


class GemmaOcrProvider:
    name = "gemma"

    def __init__(self, settings: Settings, transport: httpx.AsyncBaseTransport | None = None):
        self._s = settings
        self._transport = transport

    def _headers(self) -> dict[str, str]:
        h = {"Content-Type": "application/json"}
        if self._s.gemma_api_key:
            h["Authorization"] = f"Bearer {self._s.gemma_api_key}"
        return h

    async def extract(self, image: bytes, mime: str, language: str, **kwargs) -> OcrResult:
        data_url = f"data:{mime};base64,{base64.b64encode(image).decode()}"
        prompt = HANDWRITING_PROMPT if kwargs.get("handwriting") else PROMPT
        payload = {
            "model": self._s.gemma_model,
            "temperature": 0,
            "max_tokens": 800,
            "think": False,  # Gemma 4: never let a reasoning trace leak into the OCR JSON
            "messages": [{"role": "user", "content": [
                # Gemma 4 prefers image before text for multimodal requests.
                {"type": "image_url", "image_url": {"url": data_url}},
                {"type": "text", "text": prompt.format(language=language)},
            ]}],
        }
        try:
            async with httpx.AsyncClient(transport=self._transport,
                                         timeout=self._s.ocr_timeout_seconds) as client:
                resp = await client.post(f"{self._s.gemma_base_url.rstrip('/')}/chat/completions",
                                         json=payload, headers=self._headers())
        except httpx.TimeoutException as exc:
            raise OcrTimeout("Model timed out") from exc
        except httpx.HTTPError as exc:
            raise OcrUnavailable("Model endpoint unreachable") from exc
        if resp.status_code >= 400:
            raise OcrUnavailable(f"Model endpoint returned {resp.status_code}")
        try:
            content = _message_text(resp.json()["choices"][0]["message"]["content"])
        except (ValueError, KeyError, IndexError, TypeError, OcrBadOutput) as exc:
            raise OcrBadOutput("Unexpected response shape") from exc
        text, cands = parse_model_json(content)
        return OcrResult(text=text, candidates=cands, provider=self.name)

    async def check(self) -> bool:
        try:
            async with httpx.AsyncClient(transport=self._transport, timeout=2.0) as client:
                r = await client.get(f"{self._s.gemma_base_url.rstrip('/')}/models", headers=self._headers())
            return r.status_code < 500
        except httpx.HTTPError:
            return False
