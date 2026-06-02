#!/usr/bin/env python3
"""
Fetch publications from Google Scholar and generate Jekyll markdown files.

Usage:
    python fetch_from_scholar.py

Requires: scholarly >= 1.7, fp (free-proxy)
    pip install scholarly free-proxy
"""

import os
import re
import time
import logging
import random
from scholarly import scholarly, ProxyGenerator

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
log = logging.getLogger(__name__)


def setup_proxy():
    """Try free proxies if direct access fails."""
    pg = ProxyGenerator()
    try:
        from fp.fp import FreeProxy
        log.info("Setting up free proxy to bypass rate limits …")
        success = pg.FreeProxies()
        if success:
            scholarly.use_proxy(pg)
            log.info("Proxy configured.")
            return True
    except Exception as e:
        log.warning(f"FreeProxy setup failed: {e}")
    return False

# ── Configuration ──────────────────────────────────────────────────────────────
SCHOLAR_USER_ID = "cnhyEW0AAAAJ"   # from googlescholar URL ?user=...
AUTHOR_DISPLAY  = "Jiahuan Pei"     # for bold highlighting in citations
OUTPUT_DIR      = os.path.join(os.path.dirname(__file__), "../_publications")

# Keywords used to classify venues into categories
CONFERENCE_KEYWORDS = [
    "proceedings", "workshop", "conference", "symposium", "annual meeting",
    "acl", "emnlp", "naacl", "coling", "eacl", "findings",
    "aaai", "ijcai", "neurips", "nips", "icml", "iclr",
    "sigir", "www", "cikm", "wsdm", "ecir", "ictir",
    "ecai", "aclanthology",
]
JOURNAL_KEYWORDS = [
    "journal", "transactions", "tacl", "ieee", "acm",
    "review", "letters", "magazine",
]
ARXIV_KEYWORDS = ["arxiv", "corr", "preprint"]
BOOK_KEYWORDS  = ["thesis", "dissertation", "book", "chapter", "springer", "elsevier"]

# ── Helpers ────────────────────────────────────────────────────────────────────

def classify_venue(title: str, venue: str, pub_url: str) -> str:
    """Return one of: proceeding | journal | arxiv | book"""
    text = (venue + " " + title + " " + pub_url).lower()

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
    # Default: conference (most NLP papers are conference papers)
    return "proceeding"


def html_escape(text: str) -> str:
    table = {"&": "&amp;", '"': "&quot;", "'": "&apos;"}
    return "".join(table.get(c, c) for c in text)


def slugify(text: str) -> str:
    text = text.replace("{", "").replace("}", "").replace("\\", "").replace(" ", "-")
    text = re.sub(r"[^a-zA-Z0-9_-]", "", text)
    return re.sub(r"-{2,}", "-", text)


def format_authors(authors_list: list, highlight: str) -> str:
    """Format author list, bolding the highlighted name."""
    parts = []
    for a in authors_list:
        name = a.strip()
        # Normalise: "Pei, Jiahuan" → "Jiahuan Pei"
        if "," in name:
            last, first = name.split(",", 1)
            name = first.strip() + " " + last.strip()
        if highlight.lower() in name.lower():
            parts.append(f"<b>{name}</b>")
        else:
            parts.append(name)
    return ", ".join(parts)


def build_md(pub: dict) -> tuple[str, str]:
    """Return (filename, markdown_content)."""
    bib   = pub.get("bib", {})
    title = bib.get("title", "Untitled").strip()
    year  = str(bib.get("pub_year", "1900")).strip()
    # scholarly uses 'journal'/'conference' on filled pubs, 'venue' on listing-only pubs
    venue = (bib.get("journal") or bib.get("conference") or bib.get("venue") or "").strip()
    if venue == "NA":
        venue = ""
    abstract = bib.get("abstract", "").strip()

    authors_raw = bib.get("author", "").split(" and ")
    citation_authors = format_authors(authors_raw, AUTHOR_DISPLAY)

    pub_url   = pub.get("pub_url", "") or ""
    eprint_id = pub.get("eprint_url", "") or ""

    # Pick best paper URL
    paper_url = pub_url or eprint_id or ""

    pubsource = classify_venue(title, venue, paper_url)

    pub_date = f"{year}-01-01"
    url_slug  = slugify(title)
    md_filename = f"{pub_date}-{url_slug}.md"
    html_filename = f"{pub_date}-{url_slug}"

    # Citation string
    citation = f'{citation_authors}, "{html_escape(title)}." {html_escape(venue)}, {year}.'

    # YAML front-matter
    md  = f'---\ntitle: "{html_escape(title)}"\n'
    md += f'collection: publications\n'
    md += f'pubsource: {pubsource}\n'
    md += f'permalink: /publication/{html_filename}\n'
    md += f'date: {pub_date}\n'
    md += f"venue: '{html_escape(venue)}'\n"
    if paper_url:
        md += f"paperurl: '{paper_url}'\n"
    md += f"citation: '{html_escape(citation)}'\n"
    md += "---\n"

    return md_filename, md


# ── Main ───────────────────────────────────────────────────────────────────────

def fetch_with_retry(fn, *args, retries=3, base_delay=10, **kwargs):
    """Call fn(*args) with exponential backoff on failure."""
    for attempt in range(retries):
        try:
            return fn(*args, **kwargs)
        except Exception as e:
            if attempt == retries - 1:
                raise
            delay = base_delay * (2 ** attempt) + random.uniform(0, 3)
            log.warning(f"Attempt {attempt+1} failed ({e}). Retrying in {delay:.0f}s …")
            time.sleep(delay)


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Try direct access first; fall back to free proxy on failure
    try:
        log.info("Searching for author on Google Scholar (direct) …")
        search_query = fetch_with_retry(scholarly.search_author_id, SCHOLAR_USER_ID, retries=2, base_delay=5)
        author = fetch_with_retry(scholarly.fill, search_query, sections=["publications"], retries=2, base_delay=5)
    except Exception:
        log.warning("Direct access failed. Trying via free proxy …")
        if not setup_proxy():
            log.error("Could not set up proxy. Install free-proxy: pip install free-proxy")
            raise
        search_query = fetch_with_retry(scholarly.search_author_id, SCHOLAR_USER_ID)
        author = fetch_with_retry(scholarly.fill, search_query, sections=["publications"])

    publications = author.get("publications", [])
    log.info(f"Found {len(publications)} publications")

    written = 0
    skipped = 0
    for i, pub in enumerate(publications):
        try:
            filled = fetch_with_retry(scholarly.fill, pub)
            # Polite delay with jitter to avoid rate limiting
            time.sleep(random.uniform(2, 4))

            md_filename, md_content = build_md(filled)
            out_path = os.path.join(OUTPUT_DIR, md_filename)

            with open(out_path, "w", encoding="utf-8") as f:
                f.write(md_content)

            title_short = filled.get("bib", {}).get("title", "")[:60]
            log.info(f"[{i+1}/{len(publications)}] {md_filename} — {title_short}")
            written += 1

        except Exception as e:
            log.warning(f"Skipped entry {i+1}: {e}")
            skipped += 1
            time.sleep(5)

    log.info(f"Done. Written: {written}, Skipped: {skipped}")


if __name__ == "__main__":
    main()
