#!/usr/bin/env python3
"""
Convert citations.csv (exported from Google Scholar) to assets/js/publications.json.

Usage:
    python fetch_publications_json.py
    python fetch_publications_json.py --input my.csv
"""

import argparse
import csv
import json
import os
import re

OUTPUT = os.path.join(os.path.dirname(__file__), "..", "assets", "js", "publications.json")

CONF_KW  = ["proceedings","conference","workshop","symposium","acl","emnlp","naacl",
             "coling","eacl","sigir","cikm","www","wsdm","ecir","aaai","ijcai",
             "neurips","nips","icml","iclr","cvpr","iccv","eccv","acm","ieee",
             "ntcir","nlpcc","findings","chi","uist","cscw","iui","assets"]
JOUR_KW  = ["journal","transactions","letters","review","magazine","frontiers",
             "plos","nature","science","wiley","springer","inderscience","elsevier"]
ARXIV_KW = ["arxiv","preprint","corr"]
BOOK_KW  = ["thesis","dissertation"]


def classify(venue, title=""):
    t = (venue + " " + title).lower()
    for k in ARXIV_KW:
        if k in t: return "arxiv"
    for k in BOOK_KW:
        if k in t: return "book"
    for k in JOUR_KW:
        if k in t: return "journal"
    for k in CONF_KW:
        if k in t: return "proceeding"
    return "proceeding"


def parse_authors(raw):
    """Parse 'Last, First; Last, First; ' → [{'name': 'First Last'}, ...]"""
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
        authors.append({"name": name})
    return authors


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default=os.path.join(os.path.dirname(__file__), "citations.csv"))
    args = parser.parse_args()

    with open(args.input, newline="", encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))
    print(f"Loaded {len(rows)} rows from {args.input}")

    papers = []
    for row in rows:
        title   = row.get("Title", "").strip()
        venue   = row.get("Publication", "").strip()
        year    = row.get("Year", "").strip()
        authors = parse_authors(row.get("Authors", ""))

        if not title:
            continue

        papers.append({
            "title":      title,
            "year":       int(year) if year.isdigit() else None,
            "venue":      venue,
            "authors":    authors,
            "pubsource":  classify(venue, title),
            "externalIds": {},
            "url":        "",
        })

    # Sort newest-first
    papers.sort(key=lambda p: p.get("year") or 0, reverse=True)

    os.makedirs(os.path.dirname(OUTPUT), exist_ok=True)
    with open(OUTPUT, "w", encoding="utf-8") as f:
        json.dump({"papers": papers}, f, ensure_ascii=False, indent=2)
    print(f"Saved {len(papers)} papers → {OUTPUT}")


if __name__ == "__main__":
    main()
