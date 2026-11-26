#!/usr/bin/env python3
"""
Generate _publications/*.md files from Google Scholar's citations.csv export.

CSV columns: Authors, Title, Publication, Volume, Number, Pages, Year, Publisher

Usage:
    python citations_to_md.py                        # reads citations.csv
    python citations_to_md.py --input my.csv         # custom input
    python citations_to_md.py --output /path/        # custom output dir
"""

import argparse
import csv
import os
import re

HIGHLIGHT = "Jiahuan Pei"
OUTPUT_DIR = "../_publications/"

CONFERENCE_KEYWORDS = [
    "proceedings", "conference", "workshop", "symposium",
    "acl", "emnlp", "naacl", "coling", "eacl", "sigir", "cikm",
    "www", "wsdm", "ecir", "aaai", "ijcai", "neurips", "nips",
    "icml", "iclr", "cvpr", "iccv", "eccv", "acm", "ieee", "ntcir",
    "nlpcc", "findings", "aclanthology",
]
JOURNAL_KEYWORDS = [
    "journal", "transactions", "letters", "review", "magazine",
    "frontiers", "plos", "nature", "science", "wiley", "springer",
    "inderscience", "elsevier", "ieee access",
]
ARXIV_KEYWORDS = ["arxiv", "preprint", "corr"]


# ── Helpers ────────────────────────────────────────────────────────────────────

def html_escape(text: str) -> str:
    table = {"&": "&amp;", '"': "&quot;", "'": "&apos;"}
    return "".join(table.get(c, c) for c in str(text))


def is_set(v) -> bool:
    return v is not None and str(v).strip() not in ("", "nan")


def slugify(text: str) -> str:
    text = re.sub(r"[^\w\s-]", "", str(text).lower())
    text = re.sub(r"[\s_]+", "-", text)
    return re.sub(r"-{2,}", "-", text).strip("-")[:80]


def classify(venue: str) -> str:
    v = venue.lower()
    for kw in ARXIV_KEYWORDS:
        if kw in v: return "arxiv"
    for kw in JOURNAL_KEYWORDS:
        if kw in v: return "journal"
    for kw in CONFERENCE_KEYWORDS:
        if kw in v: return "proceeding"
    return "proceeding"


def parse_authors(raw: str) -> list[str]:
    """Parse 'Last, First; Last, First; ' → ['First Last', ...]"""
    authors = []
    for entry in raw.split(";"):
        entry = entry.strip().rstrip(",")
        if not entry:
            continue
        if "," in entry:
            parts = entry.split(",", 1)
            name = parts[1].strip() + " " + parts[0].strip()
        else:
            name = entry.strip()
        authors.append(name)
    return authors


def format_authors(authors: list[str]) -> str:
    parts = []
    for name in authors:
        if HIGHLIGHT.lower() in name.lower():
            parts.append(f"<b>{name}</b>")
        else:
            parts.append(name)
    return ", ".join(parts)


def existing_date(slug: str, year: str, pub_dir: str) -> str:
    """Reuse date from an existing .md file if slug matches, else YYYY-01-01."""
    pattern = re.compile(rf"^(\d{{4}}-\d{{2}}-\d{{2}})-{re.escape(slug)}\.md$")
    try:
        for fname in os.listdir(pub_dir):
            m = pattern.match(fname)
            if m:
                return m.group(1)
    except OSError:
        pass
    return f"{year}-01-01"


# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Generate publication .md files from citations.csv")
    parser.add_argument("--input",  default="citations.csv", help="Input CSV (default: citations.csv)")
    parser.add_argument("--output", default=OUTPUT_DIR,      help="Output directory")
    args = parser.parse_args()

    os.makedirs(args.output, exist_ok=True)

    with open(args.input, newline="", encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))
    print(f"Loaded {len(rows)} rows from {args.input}")

    written = skipped = 0

    for idx, row in enumerate(rows):
        title = row.get("Title", "").strip()
        if not title:
            print(f"  SKIP row {idx+2}: missing title")
            skipped += 1
            continue

        authors_raw = row.get("Authors", "").strip()
        authors     = parse_authors(authors_raw)
        authors_str = format_authors(authors)

        venue     = row.get("Publication", "").strip()
        year      = row.get("Year", "").strip() or "????"
        publisher = row.get("Publisher", "").strip()

        pubsource = classify(venue)

        url_slug  = slugify(title)
        pub_date  = existing_date(url_slug, year, args.output)
        md_filename   = f"{pub_date}-{url_slug}.md"
        html_filename = f"{pub_date}-{url_slug}"

        # Citation string
        t = html_escape(title)
        v = html_escape(venue)
        v_clean = re.sub(r"^[Ii]n [Pp]roceedings of\s+", "", v).strip()
        v_clean = re.sub(r"^[Ii]n\s+", "", v_clean).strip()

        if pubsource == "proceeding":
            citation = f'{authors_str}, &quot;{t}.&quot; In Proceedings of {v_clean} ({year}).'
        elif pubsource == "journal":
            citation = f'{authors_str}, &quot;{t}.&quot; {v_clean}, {year}.'
        elif pubsource == "arxiv":
            citation = f'{authors_str}, &quot;{t}.&quot; arXiv, {year}.'
        else:
            citation = f'{authors_str}, &quot;{t}.&quot; {v_clean}, {year}.'

        # Front matter
        md  = "---\n"
        md += f'title: "{html_escape(title)}"\n'
        md += "collection: publications\n"
        md += f"pubsource: {pubsource}\n"
        md += f"permalink: /publication/{html_filename}\n"
        md += f"date: {pub_date}\n"
        md += f"venue: '{html_escape(venue)}'\n"
        md += f"citation: '{citation}'\n"
        md += "---\n"

        out_path = os.path.join(args.output, md_filename)
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(md)
        print(f"  Wrote: {md_filename}")
        written += 1

    print(f"\nDone. {written} written, {skipped} skipped → {args.output}")


if __name__ == "__main__":
    main()
