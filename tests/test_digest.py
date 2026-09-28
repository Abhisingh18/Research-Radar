from datetime import datetime, timezone

from research_radar import digest
from research_radar.novelty import NoveltyResult
from research_radar.sources.base import Paper


def _paper() -> Paper:
    now = datetime.now(timezone.utc)
    return Paper(
        id="id1",
        source="arxiv",
        title="A <Great> Paper",
        summary="s",
        authors=[],
        published=now,
        updated=now,
        url="http://example.com/abs/1",
    )


def test_format_alert_escapes_html():
    novelty = NoveltyResult(novelty="HIGH", why_interesting="x & y")
    message = digest.format_alert(_paper(), ["ASR"], novelty, 9.0)
    assert "&lt;Great&gt;" in message
    assert "x &amp; y" in message


def test_format_alert_plain_has_no_html_tags():
    novelty = NoveltyResult(novelty="HIGH")
    message = digest.format_alert_plain(_paper(), ["ASR"], novelty, 9.0)
    assert "<b>" not in message
    assert "A <Great> Paper" in message


def test_format_no_new_papers_for_empty_digest():
    assert "no new papers" in digest.format_daily_digest([]).lower()
