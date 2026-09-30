"""Command-line interface for Research Radar."""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

from research_radar import pipeline, storage
from research_radar.config import load_profile
from research_radar.sources.arxiv import ArxivSource


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="research-radar",
        description="Scan arXiv for new papers matching topics you care about.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    run_parser = subparsers.add_parser(
        "run",
        help="Run the full pipeline: fetch, classify, LLM novelty analysis, score, notify.",
    )
    run_parser.add_argument("--max-fetch", type=int, default=150, help="Max papers to fetch from arXiv")
    run_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print alerts instead of sending them to Telegram",
    )
    run_parser.add_argument("--config", type=Path, default=None, help="Path to research_profile.yaml")

    search_parser = subparsers.add_parser(
        "search",
        help="Lightweight keyword search against arXiv only (no LLM, no Telegram).",
    )
    search_parser.add_argument("topics", nargs="+", help='e.g. "large language models" "AI agents"')
    search_parser.add_argument("--max", type=int, default=20, dest="max_results")
    search_parser.add_argument("--all", action="store_true", help="Include already-seen papers")
    search_parser.add_argument("--state-file", type=Path, default=storage.DEFAULT_STATE_FILE)

    backfill_parser = subparsers.add_parser(
        "backfill",
        help="One-time historical pull (e.g. since 2022) to seed the dashboard's Archive view. "
        "Never sends Telegram/WhatsApp alerts.",
    )
    backfill_parser.add_argument("--since", default="2022-01-01", help="YYYY-MM-DD (default: 2022-01-01)")
    backfill_parser.add_argument("--until", default=None, help="YYYY-MM-DD (default: today)")
    backfill_parser.add_argument("--max-fetch", type=int, default=100, help="Max papers to fetch from arXiv")
    backfill_parser.add_argument("--config", type=Path, default=None, help="Path to research_profile.yaml")

    return parser


def main(argv: list[str] | None = None) -> int:
    # Windows consoles default to cp1252, which can't encode the emoji used
    # in alert messages; UTF-8 output is safe everywhere else (incl. CI).
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")

    logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "run":
        profile = load_profile(args.config) if args.config else load_profile()
        pipeline.run(profile=profile, max_fetch=args.max_fetch, dry_run=args.dry_run)
        return 0

    if args.command == "search":
        return _search(args)

    if args.command == "backfill":
        profile = load_profile(args.config) if args.config else load_profile()
        results = pipeline.backfill(
            profile=profile, since=args.since, until=args.until, max_fetch=args.max_fetch
        )
        print(f"Backfill complete: {len(results)} historical paper(s) added to data/papers.json")
        return 0

    return 1


def _search(args: argparse.Namespace) -> int:
    try:
        source = ArxivSource()
        papers = source.fetch_by_keywords(args.topics, max_results=args.max_results)
    except Exception as exc:
        print(f"research-radar: failed to fetch papers: {exc}", file=sys.stderr)
        return 1

    seen = storage.load_seen(args.state_file)
    new_papers = papers if args.all else [p for p in papers if p.id not in seen]

    if not new_papers:
        print("No new papers found.")
    else:
        for paper in new_papers:
            authors = ", ".join(paper.authors[:3]) + (" et al." if len(paper.authors) > 3 else "")
            print(f"{paper.title.strip()}\n  {authors}\n  {paper.url}\n")

    storage.save_seen(seen | {p.id for p in papers}, args.state_file)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
