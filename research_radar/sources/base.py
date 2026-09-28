"""Shared interface for research sources (arXiv, Hugging Face, GitHub, ...).

Adding a new source means implementing `ResearchSource.fetch_recent()` and
returning a list of `Paper`. Everything downstream (classification, novelty
analysis, scoring, notification) is source-agnostic.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Protocol


@dataclass
class Paper:
    id: str
    source: str
    title: str
    summary: str
    authors: list[str]
    published: datetime
    updated: datetime
    url: str
    categories: list[str] = field(default_factory=list)
    code_url: str | None = None

    @property
    def text_blob(self) -> str:
        """Title + abstract, used for keyword matching."""
        return f"{self.title}\n{self.summary}".lower()


class ResearchSource(Protocol):
    name: str

    def fetch_recent(self, max_results: int) -> list[Paper]:
        """Return recently published/updated papers, newest first."""
        ...


def utcnow() -> datetime:
    return datetime.now(timezone.utc)
