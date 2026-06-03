from __future__ import annotations

import os
import re
from dataclasses import dataclass
from typing import Any, Iterable, List, Mapping, Optional


class LLMError(ValueError):
    """Raised when text generation cannot be completed."""


@dataclass(frozen=True)
class LLMSettings:
    mode: str = "mock"
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    model: Optional[str] = None

    @classmethod
    def from_environment(cls) -> "LLMSettings":
        return cls(
            mode=os.getenv("LLM_MODE", "mock").strip().lower(),
            api_key=os.getenv("LLM_API_KEY"),
            base_url=os.getenv("LLM_BASE_URL"),
            model=os.getenv("LLM_MODEL"),
        )


class MockLLMClient:
    """Deterministic local text generator used for the offline demo."""

    def generate_text(
        self,
        *,
        task: str,
        materials: Any,
        bullet_count: Optional[int] = None,
        max_length: Optional[int] = None,
    ) -> str:
        text = _normalize_materials(materials)
        if not text:
            raise LLMError("Cannot generate text because the provided materials are empty.")

        sentences = _split_sentences(text)
        summary = sentences[0] if sentences else text
        if max_length is not None and len(summary) > max_length:
            summary = summary[:max_length].rstrip()

        count = bullet_count if bullet_count is not None else min(3, len(sentences))
        points = sentences[:count]
        if not points:
            points = [summary]

        heading = {
            "summary": "Summary",
            "report": "Report",
            "business_insights": "Business insights",
        }.get(task, "Generated text")
        bullet_lines = "\n".join(f"- {point}" for point in points)
        return f"{heading}:\n{summary}\n\nKey points:\n{bullet_lines}"


def get_llm_client(settings: Optional[LLMSettings] = None) -> MockLLMClient:
    active_settings = settings or LLMSettings.from_environment()
    if active_settings.mode != "mock":
        raise LLMError(
            "Only LLM_MODE=mock is supported in the current offline stage. "
            "OpenAI-compatible API support will be added in stage 4A."
        )
    return MockLLMClient()


def _normalize_materials(materials: Any) -> str:
    parts = list(_extract_text_parts(materials))
    return " ".join(" ".join(part.split()) for part in parts if part.strip()).strip()


def _extract_text_parts(value: Any) -> Iterable[str]:
    if isinstance(value, str):
        yield value
        return
    if isinstance(value, Mapping):
        content = value.get("content")
        if isinstance(content, str):
            yield content
            return
        for item in value.values():
            yield from _extract_text_parts(item)
        return
    if isinstance(value, Iterable):
        for item in value:
            yield from _extract_text_parts(item)


def _split_sentences(text: str) -> List[str]:
    return [
        sentence.strip()
        for sentence in re.split(r"(?<=[.!?])\s+|(?<=[。！？])", text)
        if sentence.strip()
    ]
