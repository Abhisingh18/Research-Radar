"""Orchestrates a single Research Radar run:

arXiv fetch -> classify -> dedup -> LLM novelty analysis -> score ->
threshold -> Telegram/WhatsApp alert -> persist state + dashboard data.
"""

from __future__ import annotations

import json
import logging
from dataclasses import asdict
from pathlib import Path

from research_radar import classify, digest, scoring, storage, telegram, whatsapp
from research_radar.config import ResearchProfile, load_profile
from research_radar.novelty import NoveltyResult, analyze
from research_radar.sources.arxiv import ArxivSource
from research_radar.sources.base import Paper

logger = logging.getLogger("research_radar")

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
DEFAULT_STATE_FILE = DATA_DIR / "seen.json"
DEFAULT_PAPERS_FILE = DATA_DIR / "papers.json"


def run(
    profile: ResearchProfile | None = None,
    state_file: Path = DEFAULT_STATE_FILE,
    papers_file: Path = DEFAULT_PAPERS_FILE,
    max_fetch: int = 150,
    dry_run: bool = False,
) -> list[dict]:
    profile = profile or load_profile()
    seen = storage.load_seen(state_file)

    source = ArxivSource()
    fetched = source.fetch_by_keywords(profile.all_keywords(), max_results=max_fetch)
    logger.info("arxiv: fetched %d papers", len(fetched))

    candidates = _select_candidates(fetched, seen, profile)
    logger.info(
        "filtered to %d new candidates (max %d go to the LLM)",
        len(candidates),
        profile.max_llm_candidates,
    )

    analyzed = _analyze_candidates(candidates, profile)
    alerts = _rank_and_threshold(analyzed, profile)
    logger.info("%d paper(s) cleared the notify threshold (%.1f)", len(alerts), profile.notify_threshold)

    _notify(alerts, dry_run)
    _persist(fetched, alerts, seen, state_file, papers_file)

    return [_alert_to_dict(*a) for a in alerts]


def _select_candidates(
    papers: list[Paper], seen: set[str], profile: ResearchProfile
) -> list[tuple[Paper, list[str]]]:
    candidates: list[tuple[Paper, list[str]]] = []
    for paper in papers:
        if paper.id in seen:
            continue
        if classify.is_excluded(paper, profile):
            continue
        topics = classify.classify(paper, profile)
        if not topics:
            continue
        candidates.append((paper, topics))

    candidates.sort(key=lambda pt: classify.topic_priority(pt[1], profile), reverse=True)
    return candidates[: profile.max_llm_candidates]


def _analyze_candidates(
    candidates: list[tuple[Paper, list[str]]], profile: ResearchProfile
) -> list[tuple[Paper, list[str], NoveltyResult, float]]:
    results = []
    for paper, topics in candidates:
        novelty = analyze(paper)
        if novelty.error:
            logger.warning("novelty analysis skipped for %s: %s", paper.id, novelty.error)
        final_score = scoring.score(classify.topic_priority(topics, profile), novelty)
        results.append((paper, topics, novelty, final_score))
    return results


def _rank_and_threshold(
    analyzed: list[tuple[Paper, list[str], NoveltyResult, float]], profile: ResearchProfile
) -> list[tuple[Paper, list[str], NoveltyResult, float]]:
    above_threshold = [a for a in analyzed if a[3] >= profile.notify_threshold]
    above_threshold.sort(key=lambda a: a[3], reverse=True)
    return above_threshold[: profile.max_alerts_per_run]


def _notify(alerts: list[tuple[Paper, list[str], NoveltyResult, float]], dry_run: bool) -> None:
    if not alerts:
        return

    for paper, topics, novelty, final_score in alerts:
        html_message = digest.format_alert(paper, topics, novelty, final_score)
        plain_message = digest.format_alert_plain(paper, topics, novelty, final_score)

        any_channel_configured = telegram.is_configured() or whatsapp.is_configured()
        if dry_run or not any_channel_configured:
            print(plain_message)
            print("-" * 60)
            continue

        if telegram.is_configured():
            sent = telegram.send(html_message)
            logger.info("telegram alert for %s: %s", paper.id, "sent" if sent else "failed")
        if whatsapp.is_configured():
            sent = whatsapp.send(plain_message)
            logger.info("whatsapp alert for %s: %s", paper.id, "sent" if sent else "failed")


def _persist(
    fetched: list[Paper],
    alerts: list[tuple[Paper, list[str], NoveltyResult, float]],
    seen: set[str],
    state_file: Path,
    papers_file: Path,
) -> None:
    storage.save_seen(seen | {p.id for p in fetched}, state_file)

    papers_file.parent.mkdir(parents=True, exist_ok=True)
    existing: list[dict] = []
    if papers_file.exists():
        try:
            existing = json.loads(papers_file.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            existing = []

    new_entries = [_alert_to_dict(*a) for a in alerts]
    combined = new_entries + [e for e in existing if e["id"] not in {n["id"] for n in new_entries}]
    papers_file.write_text(json.dumps(combined[:200], indent=2, default=str), encoding="utf-8")


def _alert_to_dict(paper: Paper, topics: list[str], novelty: NoveltyResult, final_score: float) -> dict:
    return {
        "id": paper.id,
        "title": paper.title,
        "url": paper.url,
        "published": paper.published.isoformat(),
        "topics": topics,
        "score": final_score,
        "novelty": asdict(novelty),
    }
