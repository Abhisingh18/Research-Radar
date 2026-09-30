"""arXiv source adapter, using arXiv's public Atom API (no API key required)."""

from __future__ import annotations

from datetime import datetime, timezone
from urllib.parse import urlencode
from xml.etree import ElementTree

import requests

from research_radar.sources.base import Paper

ARXIV_API_URL = "http://export.arxiv.org/api/query"
ATOM_NS = "{http://www.w3.org/2005/Atom}"
ARXIV_NS = "{http://arxiv.org/schemas/atom}"

DEFAULT_CATEGORIES = ["cs.AI", "cs.CL", "cs.CV", "cs.LG", "cs.SD", "cs.RO", "eess.AS"]


class ArxivSource:
    name = "arxiv"

    def __init__(self, categories: list[str] | None = None, timeout: float = 20.0):
        self.categories = categories or DEFAULT_CATEGORIES
        self.timeout = timeout

    def fetch_recent(self, max_results: int = 100) -> list[Paper]:
        cat_query = " OR ".join(f"cat:{c}" for c in self.categories)
        return self._query(cat_query, max_results)

    def fetch_by_keywords(self, keywords: list[str], max_results: int = 100) -> list[Paper]:
        if not keywords:
            raise ValueError("at least one keyword is required")
        query = " OR ".join(f'all:"{kw.strip()}"' for kw in keywords if kw.strip())
        return self._query(query, max_results)

    def fetch_by_keywords_since(
        self, keywords: list[str], since: str, until: str | None = None, max_results: int = 100
    ) -> list[Paper]:
        """Historical search: `since`/`until` are "YYYY-MM-DD" (until defaults to today).

        Sorted by relevance rather than date, since a single page of results
        spanning years should surface the strongest matches, not just
        whatever was submitted closest to `until`.
        """
        if not keywords:
            raise ValueError("at least one keyword is required")
        until_str = (until or datetime.now(timezone.utc).strftime("%Y-%m-%d")).replace("-", "") + "2359"
        since_str = since.replace("-", "") + "0000"
        keyword_query = " OR ".join(f'all:"{kw.strip()}"' for kw in keywords if kw.strip())
        query = f"({keyword_query}) AND submittedDate:[{since_str} TO {until_str}]"
        return self._query(query, max_results, sort_by="relevance")

    def _query(self, search_query: str, max_results: int, sort_by: str = "submittedDate") -> list[Paper]:
        params = {
            "search_query": search_query,
            "start": 0,
            "max_results": max_results,
            "sortBy": sort_by,
            "sortOrder": "descending",
        }
        url = f"{ARXIV_API_URL}?{urlencode(params)}"
        response = requests.get(url, timeout=self.timeout)
        response.raise_for_status()
        return _parse_feed(response.text)


def _parse_feed(xml_text: str) -> list[Paper]:
    root = ElementTree.fromstring(xml_text)
    papers: list[Paper] = []

    for entry in root.findall(f"{ATOM_NS}entry"):
        arxiv_id = entry.findtext(f"{ATOM_NS}id", default="").strip()
        title = " ".join(entry.findtext(f"{ATOM_NS}title", default="").split())
        summary = " ".join(entry.findtext(f"{ATOM_NS}summary", default="").split())
        published = _parse_datetime(entry.findtext(f"{ATOM_NS}published", default=""))
        updated = _parse_datetime(entry.findtext(f"{ATOM_NS}updated", default=""))

        authors = [
            author.findtext(f"{ATOM_NS}name", default="").strip()
            for author in entry.findall(f"{ATOM_NS}author")
        ]

        categories = [
            cat.attrib.get("term", "") for cat in entry.findall(f"{ATOM_NS}category")
        ]

        papers.append(
            Paper(
                id=arxiv_id,
                source="arxiv",
                title=title,
                summary=summary,
                authors=[a for a in authors if a],
                published=published,
                updated=updated,
                url=arxiv_id,
                categories=[c for c in categories if c],
            )
        )

    return papers


def _parse_datetime(value: str) -> datetime:
    if not value:
        return datetime.now(timezone.utc)
    return datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
