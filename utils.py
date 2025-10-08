"""Utility functions for fetching behaviour economics articles."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List

import requests
from dateutil import parser as date_parser
from dateutil.relativedelta import relativedelta

API_URL = "https://api.crossref.org/works"


@dataclass
class Article:
    title: str
    authors: List[str]
    journal: str
    doi: str
    published_date: str
    abstract: str
    url: str


def default_from_date(years: int = 10) -> datetime:
    return datetime.utcnow() - relativedelta(years=years)


def build_query_params(issn: str, keyword: str, from_date: datetime, max_results: int, mailto: str | None = None) -> Dict[str, str]:
    filters = [
        f"from-pub-date:{from_date.strftime('%Y-%m-%d')}",
        f"issn:{issn}",
    ]

    params: Dict[str, str] = {
        "query": keyword,
        "filter": ",".join(filters),
        "rows": str(max_results),
        "sort": "published",
        "order": "desc",
    }

    if mailto:
        params["mailto"] = mailto

    return params


def fetch_articles(issn: str, keyword: str, from_date: datetime, max_results: int = 50, mailto: str | None = None) -> List[Article]:
    params = build_query_params(issn=issn, keyword=keyword, from_date=from_date, max_results=max_results, mailto=mailto)
    response = requests.get(API_URL, params=params, timeout=30)
    response.raise_for_status()
    items = response.json().get("message", {}).get("items", [])
    return [normalize_article(item) for item in items]


def normalize_article(item: Dict) -> Article:
    title = item.get("title", [""])[0]
    authors = [
        " ".join(filter(None, [person.get("given"), person.get("family")]))
        for person in item.get("author", [])
    ]
    doi = item.get("DOI", "")
    journal = item.get("container-title", [""])[0]
    abstract = item.get("abstract", "")
    url = f"https://doi.org/{doi}" if doi else ""
    published_date = parse_date(item)

    return Article(
        title=title,
        authors=authors,
        journal=journal,
        doi=doi,
        published_date=published_date,
        abstract=abstract,
        url=url,
    )


def parse_date(item: Dict) -> str:
    date_parts = item.get("issued", {}).get("date-parts")
    if not date_parts:
        return ""

    parts = date_parts[0]
    year = parts[0]
    month = parts[1] if len(parts) > 1 else 1
    day = parts[2] if len(parts) > 2 else 1
    return datetime(year, month, day).strftime("%Y-%m-%d")


