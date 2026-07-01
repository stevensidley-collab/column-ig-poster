"""Fetch and parse a Substack column page for title, dek, hero image, and teaser text."""
from __future__ import annotations

import re
from dataclasses import dataclass

import requests
from bs4 import BeautifulSoup

USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"


@dataclass
class ColumnData:
    url: str
    title: str
    dek: str
    hero_image_url: str | None
    teaser: str


def _meta(soup: BeautifulSoup, **attrs) -> str | None:
    tag = soup.find("meta", attrs=attrs)
    return tag.get("content", "").strip() if tag and tag.get("content") else None


def _extract_teaser(soup: BeautifulSoup, max_sentences: int = 3) -> str:
    content = soup.select_one(
        ".available-content, .body, article, .post-content, .post"
    )
    text = content.get_text(" ", strip=True) if content else soup.get_text(" ", strip=True)
    sentences = re.split(r"(?<=[.!?])\s+", text)
    sentences = [s.strip() for s in sentences if len(s.strip()) > 20]
    return " ".join(sentences[:max_sentences]).strip()


def fetch_column(url: str, timeout: int = 15) -> ColumnData:
    resp = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=timeout)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    title = (
        _meta(soup, property="og:title")
        or (soup.title.string.strip() if soup.title and soup.title.string else "")
        or "Untitled"
    )
    dek = _meta(soup, name="description") or _meta(soup, property="og:description") or ""
    hero_image_url = _meta(soup, property="og:image")
    teaser = _extract_teaser(soup)

    return ColumnData(
        url=url,
        title=title,
        dek=dek,
        hero_image_url=hero_image_url,
        teaser=teaser,
    )
