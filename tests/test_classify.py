from datetime import datetime, timezone

from research_radar import classify
from research_radar.config import ResearchProfile, Topic
from research_radar.sources.base import Paper

PROFILE = ResearchProfile(
    topics=[
        Topic(name="ASR", priority=1.0, keywords=["speech recognition"]),
        Topic(name="AI Agents", priority=0.8, keywords=["agentic", "LLM agent"]),
    ],
    exclude_if_matches=["survey"],
    notify_threshold=6.5,
    max_llm_candidates=15,
    max_alerts_per_run=5,
)


def _paper(title: str, summary: str = "") -> Paper:
    now = datetime.now(timezone.utc)
    return Paper(
        id="id1",
        source="arxiv",
        title=title,
        summary=summary,
        authors=[],
        published=now,
        updated=now,
        url="http://example.com",
    )


def test_classify_matches_topic_by_keyword():
    paper = _paper("A new speech recognition model")
    assert classify.classify(paper, PROFILE) == ["ASR"]


def test_classify_matches_multiple_topics():
    paper = _paper("An agentic speech recognition system", "uses an LLM agent internally")
    assert set(classify.classify(paper, PROFILE)) == {"ASR", "AI Agents"}


def test_classify_no_match_returns_empty():
    paper = _paper("Unrelated computer vision paper")
    assert classify.classify(paper, PROFILE) == []


def test_is_excluded():
    paper = _paper("A survey of speech recognition")
    assert classify.is_excluded(paper, PROFILE) is True


def test_topic_priority_picks_highest():
    assert classify.topic_priority(["ASR", "AI Agents"], PROFILE) == 1.0
    assert classify.topic_priority([], PROFILE) == 0.0
