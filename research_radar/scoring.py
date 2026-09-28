"""Combines personal relevance (from the profile) with LLM novelty signal
into a single 0-10 score used to rank and threshold alerts.
"""

from __future__ import annotations

from research_radar.novelty import NoveltyResult

_NOVELTY_WEIGHT = {"HIGH": 10.0, "MEDIUM": 6.0, "LOW": 3.0, "UNKNOWN": 4.0}


def score(topic_priority: float, novelty: NoveltyResult) -> float:
    """0-10 combined score.

    60% comes from the LLM's own relevance_score (already interest-aware),
    30% from the novelty bucket, 10% from how strongly the paper matched the
    user's declared topic priorities.
    """
    novelty_component = _NOVELTY_WEIGHT.get(novelty.novelty, 4.0)
    llm_component = novelty.relevance_score if not novelty.error else novelty_component
    return round(
        0.6 * llm_component + 0.3 * novelty_component + 0.1 * (topic_priority * 10),
        2,
    )
