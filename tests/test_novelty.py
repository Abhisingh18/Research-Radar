from datetime import datetime, timezone

from research_radar.novelty import _parse_result, analyze
from research_radar.sources.base import Paper


def test_analyze_without_api_key_returns_error(monkeypatch):
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
    now = datetime.now(timezone.utc)
    paper = Paper(
        id="id1", source="arxiv", title="t", summary="s", authors=[],
        published=now, updated=now, url="http://example.com",
    )
    result = analyze(paper)
    assert result.error is not None
    assert result.novelty == "UNKNOWN"


def test_parse_result_handles_clean_json():
    content = (
        '{"problem": "p", "new_contribution": "c", "architecture_innovation": "a", '
        '"results": "r", "code_available": true, "novelty": "high", '
        '"why_interesting": "w", "relevance_score": 8.5}'
    )
    result = _parse_result(content)
    assert result.novelty == "HIGH"
    assert result.code_available is True
    assert result.relevance_score == 8.5
    assert result.error is None


def test_parse_result_strips_markdown_fences():
    content = '```json\n{"novelty": "medium", "relevance_score": 5}\n```'
    result = _parse_result(content)
    assert result.novelty == "MEDIUM"
    assert result.relevance_score == 5.0


def test_parse_result_handles_malformed_json():
    result = _parse_result("not json at all")
    assert result.error is not None
