#!/usr/bin/env python3
"""
Enrich venue data in existing _publications/*.md files using Semantic Scholar API.

This is a reliable companion to fetch_from_scholar.py: it reads existing markdown
files and fills in any missing `venue` field by querying the Semantic Scholar API,
which is free, requires no API key, and does not rate-limit like Google Scholar.

Usage:
    python enrich_venues.py

Requires: requests
    pip install requests
"""

import os
import re
import time
import logging
import requests

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
log = logging.getLogger(__name__)

PUBS_DIR = os.path.join(os.path.dirname(__file__), "../_publications")
S2_SEARCH  = "https://api.semanticscholar.org/graph/v1/paper/search"
S2_FIELDS  = "title,year,venue,publicationTypes,externalIds,openAccessPdf"
HEADERS    = {"User-Agent": "academic-site-enricher/1.0"}

CONFERENCE_KEYWORDS = [
    "proceedings", "workshop", "conference", "symposium", "annual meeting",
    "acl", "emnlp", "naacl", "coling", "eacl", "findings",
    "aaai", "ijcai", "neurips", "nips", "icml", "iclr",
    "sigir", "www", "cikm", "wsdm", "ecir", "ictir",
    "ecai", "chi ", "iui", "uist",
]
JOURNAL_KEYWORDS = [
    "journal", "transactions", "tacl", "ieee", "acm computing surveys",
    "review", "letters", "magazine", "artificial intelligence",
]
ARXIV_KEYWORDS = ["arxiv", "corr", "preprint"]
BOOK_KEYWORDS  = ["thesis", "dissertation", "book", "chapter", "springer", "elsevier"]


def classify_venue(title: str, venue: str, pub_types: list, paper_url: str) -> str:
    text = (venue + " " + title + " " + (paper_url or "")).lower()
    types_lower = [t.lower() for t in (pub_types or [])]

    if "arxiv" in text or "corr" in text:
        return "arxiv"
    if any(t in types_lower for t in ["book", "editedbook"]):
        return "book"
    for kw in BOOK_KEYWORDS:
        if kw in text:
            return "book"
    if any(t in types_lower for t in ["journalarticle", "review"]):
        return "journal"
    if any(t in types_lower for t in ["conferencepaper"]):
        return "proceeding"
    for kw in ARXIV_KEYWORDS:
        if kw in text:
            return "arxiv"
    for kw in BOOK_KEYWORDS:
        if kw in text:
            return "book"
    for kw in CONFERENCE_KEYWORDS:
        if kw in text:
            return "proceeding"
    for kw in JOURNAL_KEYWORDS:
        if kw in text:
            return "journal"
    return None  # no change


def read_frontmatter(path: str) -> dict:
    with open(path, encoding="utf-8") as f:
        content = f.read()
    m = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
    if not m:
        return {}
    fm = {}
    for line in m.group(1).splitlines():
        kv = line.split(":", 1)
        if len(kv) == 2:
            fm[kv[0].strip()] = kv[1].strip().strip("'\"")
    return fm


def update_field(path: str, field: str, value: str):
    with open(path, encoding="utf-8") as f:
        content = f.read()
    # Replace the field value inside frontmatter
    pattern = rf"^({re.escape(field)}:).*$"
    new_line = f"{field}: '{value}'"
    new_content = re.sub(pattern, new_line, content, flags=re.MULTILINE)
    if new_content != content:
        with open(path, "w", encoding="utf-8") as f:
            f.write(new_content)
        return True
    return False


def search_s2(title: str) -> dict | None:
    for attempt in range(3):
        try:
            r = requests.get(
                S2_SEARCH,
                params={"query": title, "fields": S2_FIELDS, "limit": 3},
                headers=HEADERS,
                timeout=15,
            )
            if r.status_code == 429:
                wait = 30 * (attempt + 1)
                log.warning(f"S2 rate-limit (attempt {attempt+1}), sleeping {wait}s …")
                time.sleep(wait)
                continue
            r.raise_for_status()
            data = r.json().get("data", [])
            for paper in data:
                if title.lower()[:40] in paper.get("title", "").lower():
                    return paper
            return data[0] if data else None
        except requests.HTTPError:
            return None
        except Exception as e:
            log.warning(f"S2 lookup failed for '{title[:50]}': {e}")
            return None
    return None


def main():
    md_files = sorted(f for f in os.listdir(PUBS_DIR) if f.endswith(".md"))
    log.info(f"Processing {len(md_files)} publication files …")

    updated = 0
    for fname in md_files:
        path = os.path.join(PUBS_DIR, fname)
        fm = read_frontmatter(path)
        title = fm.get("title", "")
        current_venue = fm.get("venue", "")
        current_source = fm.get("pubsource", "")

        if not title:
            continue

        # Only query S2 if venue is empty or unknown
        if current_venue and current_venue not in ("", "NA"):
            log.info(f"SKIP {fname} (venue already set)")
            continue

        log.info(f"Looking up: {title[:60]} …")
        paper = search_s2(title)
        time.sleep(1.2)  # polite delay (~50 req/min, safely under S2's limit)

        if not paper:
            log.warning(f"  → Not found on Semantic Scholar")
            continue

        venue    = paper.get("venue", "") or ""
        pub_types = paper.get("publicationTypes") or []
        ext_ids  = paper.get("externalIds") or {}
        pdf_url  = (paper.get("openAccessPdf") or {}).get("url", "") or ""

        paper_url = ""
        if ext_ids.get("ArXiv"):
            paper_url = f"https://arxiv.org/abs/{ext_ids['ArXiv']}"
        elif ext_ids.get("DOI"):
            paper_url = f"https://doi.org/{ext_ids['DOI']}"

        changed = False

        if venue:
            if update_field(path, "venue", venue):
                log.info(f"  → venue: {venue}")
                changed = True

        new_source = classify_venue(title, venue, pub_types, paper_url)
        if new_source and new_source != current_source:
            if update_field(path, "pubsource", new_source):
                log.info(f"  → pubsource: {current_source} → {new_source}")
                changed = True

        if not fm.get("paperurl") and paper_url:
            if update_field(path, "paperurl", paper_url):
                log.info(f"  → paperurl: {paper_url}")
                changed = True

        if changed:
            updated += 1

    log.info(f"Done. Updated {updated}/{len(md_files)} files.")


if __name__ == "__main__":
    main()
