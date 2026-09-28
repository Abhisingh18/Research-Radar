"""Cheap, local, keyword-based topic classification.

This runs before any LLM call so we never pay for papers that obviously
don't match the user's interests (see config.max_llm_candidates).
"""

from __future__ import annotations

from research_radar.config import ResearchProfile
from research_radar.sources.base import Paper


def classify(paper: Paper, profile: ResearchProfile) -> list[str]:
    """Return the list of topic names (from the profile) this paper matches."""
    blob = paper.text_blob
    return [
        topic.name
        for topic in profile.topics
        if any(kw.lower() in blob for kw in topic.keywords)
    ]


def is_excluded(paper: Paper, profile: ResearchProfile) -> bool:
    blob = paper.text_blob
    return any(phrase.lower() in blob for phrase in profile.exclude_if_matches)


def topic_priority(topics: list[str], profile: ResearchProfile) -> float:
    """Highest priority weight among the topics a paper matched (0 if none)."""
    if not topics:
        return 0.0
    by_name = {t.name: t.priority for t in profile.topics}
    return max(by_name.get(t, 0.0) for t in topics)
