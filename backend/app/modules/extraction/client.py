import json
from typing import Protocol

import httpx

from app.core.config import Settings
from app.modules.extraction.mock import MockExtractor
from app.modules.extraction.normalize import ExtractionError, normalize_extraction_output
from app.modules.extraction.prompts import build_prompt
from app.modules.extraction.schemas import ExtractionInput, ExtractionOutput


class Extractor(Protocol):
    model_name: str

    def extract(self, input_data: ExtractionInput) -> tuple[ExtractionOutput, dict]: ...


class LiveExtractor:
    def __init__(self, settings: Settings) -> None:
        if not settings.ai_api_key:
            raise ValueError("AI_API_KEY is required for live extraction mode.")
        self.settings = settings
        self.model_name = settings.ai_model

    def extract(self, input_data: ExtractionInput) -> tuple[ExtractionOutput, dict]:
        prompt = build_prompt(input_data)
        base_url = self.settings.ai_base_url or "https://api.openai.com/v1"
        response = httpx.post(
            f"{base_url.rstrip('/')}/chat/completions",
            headers={"Authorization": f"Bearer {self.settings.ai_api_key}"},
            json={
                "model": self.settings.ai_model,
                "messages": [
                    {"role": "system", "content": "Return JSON only."},
                    {"role": "user", "content": prompt},
                ],
                "response_format": {"type": "json_object"},
            },
            timeout=30.0,
        )
        response.raise_for_status()
        payload = response.json()
        content = payload["choices"][0]["message"]["content"]
        try:
            parsed = json.loads(content)
        except json.JSONDecodeError as exc:
            raise ExtractionError("AI returned invalid JSON.", raw_output={"content": content}) from exc
        if not isinstance(parsed, dict):
            raise ExtractionError("AI JSON must be an object.", raw_output={"content": content})
        return normalize_extraction_output(parsed), parsed


def get_extractor(settings: Settings) -> Extractor:
    mode = settings.ai_extraction_mode.strip().lower()
    if mode == "live" and settings.ai_api_key:
        return LiveExtractor(settings)
    return MockExtractor()
