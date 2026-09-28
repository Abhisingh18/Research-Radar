"""Formats research alerts and daily digests as Telegram HTML messages."""

from __future__ import annotations

from html import escape

from research_radar.novelty import NoveltyResult
from research_radar.sources.base import Paper

NOVELTY_EMOJI = {"HIGH": "\U0001f525", "MEDIUM": "⚡", "LOW": "\U0001f4a4", "UNKNOWN": "❓"}


def format_alert(paper: Paper, topics: list[str], novelty: NoveltyResult, final_score: float) -> str:
    code_line = "Available" if novelty.code_available else "Not reported"
    emoji = NOVELTY_EMOJI.get(novelty.novelty, "❓")

    lines = [
        "\U0001f6a8 <b>NEW RESEARCH ALERT</b>",
        "",
        f"<b>{escape(paper.title)}</b>",
        f"Category: {escape(', '.join(topics) or 'Uncategorized')}",
        f"Published: {paper.published.date().isoformat()}",
        f"Score: {final_score}/10",
        "",
        f"\U0001f4a1 <b>What's new?</b>\n{escape(novelty.new_contribution)}",
        "",
        f"\U0001f9e0 <b>Architecture / approach</b>\n{escape(novelty.architecture_innovation)}",
        "",
        f"\U0001f4ca <b>Results</b>\n{escape(novelty.results)}",
        "",
        f"⭐ <b>Why you should care</b>\n{escape(novelty.why_interesting)}",
        "",
        f"{emoji} Novelty: <b>{novelty.novelty}</b>",
        f"\U0001f4bb Code: {code_line}",
        f'\U0001f4c4 Paper: <a href="{escape(paper.url)}">{escape(paper.url)}</a>',
    ]
    if novelty.error:
        lines += ["", f"⚠️ Note: {escape(novelty.error)}"]

    return "\n".join(lines)


def format_no_new_papers() -> str:
    return "Research Radar ran — no new papers cleared the alert threshold this time."


def format_daily_digest(alerts: list[tuple[Paper, list[str], NoveltyResult, float]]) -> str:
    if not alerts:
        return format_no_new_papers()

    lines = [f"\U0001f525 <b>Today's AI Research — top {len(alerts)}</b>", ""]
    for i, (paper, topics, novelty, final_score) in enumerate(alerts, start=1):
        lines.append(
            f"{i}. <b>{escape(paper.title)}</b>\n"
            f"   {escape(', '.join(topics) or 'Uncategorized')} · score {final_score}/10 · "
            f'<a href="{escape(paper.url)}">paper</a>'
        )
    return "\n".join(lines)
