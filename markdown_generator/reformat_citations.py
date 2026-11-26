#!/usr/bin/env python3
"""
Reformat citation field in all _publications/*.md files to:
  Authors, "Title." In Proceedings of Venue (Year).   ← proceedings
  Authors, "Title." Venue, Year.                       ← journal / book
  Authors, "Title." arXiv, Year.                       ← arxiv
"""
import os
import re
from pathlib import Path

PUB_DIR = Path(__file__).parent.parent / "_publications"

CONFERENCE_KEYWORDS = [
    "proceedings", "conference", "workshop", "symposium", "acl", "emnlp",
    "naacl", "coling", "eacl", "sigir", "cikm", "www", "wsdm", "ecir",
    "aaai", "ijcai", "neurips", "nips", "icml", "iclr", "cvpr", "iccv",
    "eccv", "acm", "ieee", "aclanthology",
]
JOURNAL_KEYWORDS = [
    "journal", "transactions", "letters", "review", "magazine",
    "frontiers", "plos", "nature", "science", "wiley", "springer",
]
ARXIV_KEYWORDS = ["arxiv", "preprint", "corr"]


def classify(pubsource: str, venue: str) -> str:
    if pubsource in ("proceeding", "journal", "arxiv", "book"):
        return pubsource
    v = venue.lower()
    for kw in ARXIV_KEYWORDS:
        if kw in v:
            return "arxiv"
    for kw in JOURNAL_KEYWORDS:
        if kw in v:
            return "journal"
    for kw in CONFERENCE_KEYWORDS:
        if kw in v:
            return "proceeding"
    return "proceeding"


def build_citation(authors_str: str, title: str, venue: str, year: str, pubsource: str) -> str:
    kind = classify(pubsource, venue)
    t = title.replace("&quot;", "'").replace("&amp;", "&").strip('"')
    v = venue.replace("&amp;", "&").strip("'\"")
    # Strip leading "In Proceedings of" / "In " from venue (we add it ourselves)
    v = re.sub(r"^[Ii]n [Pp]roceedings of\s+", "", v).strip()
    v = re.sub(r"^[Ii]n\s+", "", v).strip()
    if kind == "proceeding":
        return f'{authors_str}, &quot;{t}.&quot; In Proceedings of {v} ({year}).'
    elif kind == "journal":
        return f'{authors_str}, &quot;{t}.&quot; {v}, {year}.'
    elif kind == "arxiv":
        return f'{authors_str}, &quot;{t}.&quot; arXiv, {year}.'
    else:
        return f'{authors_str}, &quot;{t}.&quot; {v}, {year}.'


def get_field(fm: str, key: str) -> str:
    """Extract a YAML field value (single or double quoted, or unquoted)."""
    m = re.search(rf"^{key}:\s*['\"]?(.*?)['\"]?\s*$", fm, re.MULTILINE)
    return m.group(1).strip() if m else ""


def extract_authors(citation: str) -> str:
    """Pull the author string before the first &quot; from an existing citation."""
    idx = citation.find("&quot;")
    if idx == -1:
        idx = citation.find('"')
    if idx == -1:
        return ""
    return citation[:idx].rstrip(", ").strip()


files = sorted(PUB_DIR.glob("*.md"))
updated = 0

for fpath in files:
    text = fpath.read_text(encoding="utf-8")

    # Split front matter
    parts = text.split("---", 2)
    if len(parts) < 3:
        continue
    _, fm, body = parts

    title      = get_field(fm, "title")
    venue      = get_field(fm, "venue")
    pubsource  = get_field(fm, "pubsource")
    date_str   = get_field(fm, "date")
    year       = date_str[:4] if date_str else "????"

    old_citation = get_field(fm, "citation")
    if not old_citation:
        print(f"  SKIP (no citation): {fpath.name}")
        continue

    authors_str = extract_authors(old_citation)
    if not authors_str:
        authors_str = f"<b>Jiahuan Pei</b> et al."

    new_citation = build_citation(authors_str, title, venue, year, pubsource)

    if new_citation == old_citation:
        continue

    # Replace citation line in front matter
    new_fm = re.sub(
        r"^citation:.*$",
        f"citation: '{new_citation}'",
        fm,
        flags=re.MULTILINE,
    )

    fpath.write_text(f"---{new_fm}---{body}", encoding="utf-8")
    print(f"  Updated: {fpath.name}")
    updated += 1

print(f"\nDone. {updated}/{len(files)} files updated.")
