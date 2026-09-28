"""Loads the user-editable research profile (config/research_profile.yaml)."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import yaml

DEFAULT_CONFIG_PATH = Path(__file__).resolve().parent.parent / "config" / "research_profile.yaml"


@dataclass
class Topic:
    name: str
    priority: float
    keywords: list[str]


@dataclass
class ResearchProfile:
    topics: list[Topic]
    exclude_if_matches: list[str]
    notify_threshold: float
    max_llm_candidates: int
    max_alerts_per_run: int

    def all_keywords(self) -> list[str]:
        seen: set[str] = set()
        keywords: list[str] = []
        for topic in self.topics:
            for kw in topic.keywords:
                key = kw.lower()
                if key not in seen:
                    seen.add(key)
                    keywords.append(kw)
        return keywords


def load_profile(path: Path = DEFAULT_CONFIG_PATH) -> ResearchProfile:
    raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}

    topics = [
        Topic(
            name=name,
            priority=float(spec.get("priority", 0.5)),
            keywords=list(spec.get("keywords", [])),
        )
        for name, spec in (raw.get("topics") or {}).items()
    ]

    return ResearchProfile(
        topics=topics,
        exclude_if_matches=list(raw.get("exclude_if_matches") or []),
        notify_threshold=float(raw.get("notify_threshold", 6.5)),
        max_llm_candidates=int(raw.get("max_llm_candidates", 15)),
        max_alerts_per_run=int(raw.get("max_alerts_per_run", 5)),
    )
