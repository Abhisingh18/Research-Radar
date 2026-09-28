from research_radar.novelty import NoveltyResult
from research_radar.scoring import score


def test_score_high_novelty_high_relevance():
    novelty = NoveltyResult(novelty="HIGH", relevance_score=9.0)
    result = score(topic_priority=1.0, novelty=novelty)
    assert result == round(0.6 * 9.0 + 0.3 * 10.0 + 0.1 * 10.0, 2)


def test_score_falls_back_to_novelty_bucket_on_llm_error():
    novelty = NoveltyResult(novelty="LOW", relevance_score=0.0, error="LLM request failed")
    result = score(topic_priority=0.5, novelty=novelty)
    # llm_component falls back to the novelty bucket weight (3.0) when errored
    assert result == round(0.6 * 3.0 + 0.3 * 3.0 + 0.1 * 5.0, 2)


def test_score_unknown_novelty_is_mid_weight():
    novelty = NoveltyResult(novelty="UNKNOWN", relevance_score=5.0)
    result = score(topic_priority=0.0, novelty=novelty)
    assert result == round(0.6 * 5.0 + 0.3 * 4.0 + 0.0, 2)
