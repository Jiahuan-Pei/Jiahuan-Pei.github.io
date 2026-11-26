#!/usr/bin/env python3
"""
Fetch publications from Semantic Scholar and save as a static JSON file.
Output: assets/js/publications.json

Usage:
    python fetch_publications_json.py
"""

import json
import os
import urllib.parse
import urllib.request
import time

AUTHOR_ID  = "7616787"
OUTPUT     = os.path.join(os.path.dirname(__file__), "..", "assets", "js", "publications.json")
FIELDS     = "title,year,venue,journal,authors,externalIds,url,openAccessPdf"
LIMIT      = 200


def fetch(url, retries=3, delay=10):
    req = urllib.request.Request(url, headers={"User-Agent": "academicpages/1.0"})
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(req, timeout=20) as resp:
                return json.loads(resp.read())
        except Exception as e:
            if attempt < retries - 1:
                print(f"  Attempt {attempt+1} failed: {e}. Retrying in {delay}s…")
                time.sleep(delay)
                delay *= 2
            else:
                raise


def main():
    url = (f"https://api.semanticscholar.org/graph/v1/author/{AUTHOR_ID}"
           f"/papers?fields={FIELDS}&limit={LIMIT}")
    print(f"Fetching from Semantic Scholar (author {AUTHOR_ID})…")
    data = fetch(url)
    papers = data.get("data", [])
    print(f"Found {len(papers)} papers.")

    # Sort newest-first
    papers.sort(key=lambda p: p.get("year") or 0, reverse=True)

    os.makedirs(os.path.dirname(OUTPUT), exist_ok=True)
    with open(OUTPUT, "w", encoding="utf-8") as f:
        json.dump({"papers": papers}, f, ensure_ascii=False, indent=2)
    print(f"Saved {len(papers)} papers → {OUTPUT}")


if __name__ == "__main__":
    main()
