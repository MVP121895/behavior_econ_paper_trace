"""Utility functions for fetching behaviour economics articles."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List

import requests
from dateutil.relativedelta import relativedelta

API_URL = "https://api.openalex.org/works"


@dataclass
class Article:
    title: str
    authors: List[str]
    journal: str
    doi: str
    published_date: str
    abstract: str
    url: str
    concepts: List[str]


def default_from_date(years: int = 10) -> datetime:
    return datetime.utcnow() - relativedelta(years=years)


def build_query_params(issn: str, keyword: str, from_date: datetime, max_results: int, mailto: str | None = None) -> Dict[str, str]:
    filters = [
        f"host_venue.issn:{issn}",
        f"from_publication_date:{from_date.strftime('%Y-%m-%d')}",
    ]

    params: Dict[str, str] = {
        "filter": ",".join(filters),
        "search": keyword,
        "sort": "publication_date:desc",
        "per-page": str(max_results),
    }

    if mailto:
        params["mailto"] = mailto

    return params


def fetch_articles(issn: str, keyword: str, from_date: datetime, max_results: int = 50, mailto: str | None = None) -> List[Article]:
    params = build_query_params(issn=issn, keyword=keyword, from_date=from_date, max_results=max_results, mailto=mailto)
    response = requests.get(API_URL, params=params, timeout=30)
    response.raise_for_status()
    items = response.json().get("results", [])
    filtered = [item for item in items if contains_keyword(item, keyword)]
    return [normalize_article(item) for item in filtered]


def normalize_article(item: Dict) -> Article:
    title = item.get("display_name", "")

    authors: List[str] = []
    for authorship in item.get("authorships", []) or []:
        author_info = authorship.get("author") or {}
        name = author_info.get("display_name")
        if name:
            authors.append(name)

    doi = (item.get("doi") or "").removeprefix("https://doi.org/")
    journal = item.get("host_venue", {}).get("display_name", "")
    abstract = extract_abstract(item)
    published_date = parse_date(item)
    url = item.get("primary_location", {}).get("landing_page_url") or item.get("host_venue", {}).get("url") or (f"https://doi.org/{doi}" if doi else "")
    concepts = [concept.get("display_name", "") for concept in item.get("concepts", [])]

    return Article(
        title=title,
        authors=authors,
        journal=journal,
        doi=doi,
        published_date=published_date,
        abstract=abstract,
        url=url,
        concepts=concepts,
    )


def parse_date(item: Dict) -> str:
    raw_date = item.get("publication_date")
    if raw_date:
        return raw_date

    year = item.get("publication_year")
    if year:
        return f"{year}-01-01"

    return ""


def contains_keyword(item: Dict, keyword: str) -> bool:
    if not keyword:
        return True

    keyword_lower = keyword.lower()

    title = item.get("display_name", "").lower()
    if keyword_lower in title:
        return True

    abstract = extract_abstract(item).lower()
    if keyword_lower in abstract:
        return True

    concepts = [concept.get("display_name", "").lower() for concept in item.get("concepts", [])]
    if any(keyword_lower in concept for concept in concepts):
        return True

    return False


def extract_abstract(item: Dict) -> str:
    inverted = item.get("abstract_inverted_index")
    if not inverted:
        return item.get("abstract", "") or ""

    index_to_word: Dict[int, str] = {}
    for word, positions in inverted.items():
        for pos in positions:
            index_to_word[pos] = word

    return " ".join(word for _, word in sorted(index_to_word.items()))


