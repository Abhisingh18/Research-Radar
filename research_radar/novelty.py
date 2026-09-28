"""LLM-based novelty analysis via OpenRouter (https://openrouter.ai).

OpenRouter exposes an OpenAI-compatible /chat/completions endpoint in front
of many providers, so this module has no vendor lock-in — swap the model
by setting OPENROUTER_MODEL to any model slug listed on openrouter.ai/models
(e.g. a Qwen, GLM or Nvidia Nemotron model).
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass

import requests

from research_radar.sources.base import Paper

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
DEFAULT_MODEL = "qwen/qwen-2.5-72b-instruct"

SYSTEM_PROMPT = """You are a research analyst helping a practitioner triage new \
arXiv papers in ASR, TTS, speech LLMs, VLMs, multimodal AI, LLMs and AI agents. \
Given a paper's title and abstract, produce a compact, honest analysis. \
Never fabricate results, benchmarks or code links that are not stated in the \
abstract — if something isn't mentioned, say "Not reported". Respond with ONLY \
a single JSON object, no markdown fences, no commentary, matching this schema:
{
  "problem": string,
  "new_contribution": string,
  "architecture_innovation": string,
  "results": string,
  "code_available": boolean,
  "novelty": "HIGH" | "MEDIUM" | "LOW",
  "why_interesting": string (2-3 sentences),
  "relevance_score": number (0-10, how interesting this is for the stated interest areas)
}"""


@dataclass
class NoveltyResult:
    problem: str = "Not reported"
    new_contribution: str = "Not reported"
    architecture_innovation: str = "Not reported"
    results: str = "Not reported"
    code_available: bool = False
    novelty: str = "UNKNOWN"
    why_interesting: str = ""
    relevance_score: float = 0.0
    error: str | None = None


def analyze(paper: Paper, model: str | None = None, timeout: float = 60.0) -> NoveltyResult:
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        return NoveltyResult(error="OPENROUTER_API_KEY not set; skipped LLM analysis")

    payload = {
        "model": model or os.environ.get("OPENROUTER_MODEL", DEFAULT_MODEL),
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": f"Title: {paper.title}\n\nAbstract: {paper.summary}",
            },
        ],
        "temperature": 0.2,
    }
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    try:
        response = requests.post(OPENROUTER_URL, headers=headers, json=payload, timeout=timeout)
        response.raise_for_status()
        content = response.json()["choices"][0]["message"]["content"]
        return _parse_result(content)
    except (requests.RequestException, KeyError, IndexError) as exc:
        return NoveltyResult(error=f"LLM request failed: {exc}")


def _parse_result(content: str) -> NoveltyResult:
    text = content.strip()
    if text.startswith("```"):
        text = text.strip("`")
        if text.lower().startswith("json"):
            text = text[4:]
        text = text.strip()

    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        return NoveltyResult(error=f"could not parse LLM response as JSON: {exc}")

    return NoveltyResult(
        problem=str(data.get("problem", "Not reported")),
        new_contribution=str(data.get("new_contribution", "Not reported")),
        architecture_innovation=str(data.get("architecture_innovation", "Not reported")),
        results=str(data.get("results", "Not reported")),
        code_available=bool(data.get("code_available", False)),
        novelty=str(data.get("novelty", "UNKNOWN")).upper(),
        why_interesting=str(data.get("why_interesting", "")),
        relevance_score=float(data.get("relevance_score", 0.0) or 0.0),
    )
