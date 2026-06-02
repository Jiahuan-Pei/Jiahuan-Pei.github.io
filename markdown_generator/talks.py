#!/usr/bin/env python3
"""
Talks markdown generator for academicpages.

Reads talks.tsv and writes one .md file per row into ../_talks/.

TSV columns (header row required):
    title       – talk title                         [required]
    url_slug    – slug for filename and permalink    [required]
    date        – YYYY-MM-DD                         [required]
    type        – e.g. "Talk", "Invited Talk"        [defaults to "Talk"]
    venue       – conference / event name
    location    – city, country
    talk_url    – link to slides, video, etc.
    description – free-text description

Usage:
    python talks.py                    # reads talks.tsv, writes to ../_talks/
    python talks.py --tsv my.tsv       # custom input file
    python talks.py --output /path/    # custom output directory
"""

import argparse
import os
import pandas as pd
from datetime import datetime

# ── Helpers ────────────────────────────────────────────────────────────────────

HTML_ESCAPE = {"&": "&amp;", '"': "&quot;", "'": "&apos;"}

def html_escape(text: str) -> str:
    if not isinstance(text, str):
        return ""
    return "".join(HTML_ESCAPE.get(c, c) for c in text)


def is_set(value) -> bool:
    """Return True if the value is a non-empty, non-NaN string."""
    return pd.notna(value) and str(value).strip() != ""


def normalise_date(raw: str) -> str:
    """
    Normalise a date string to YYYY-MM-DD.
    Handles D/M/YY, DD/MM/YYYY, D/M/YYYY, YYYY-MM-DD, etc.
    Assumes day-first ordering (European style) for ambiguous inputs.
    """
    raw = str(raw).strip()
    if not raw:
        raise ValueError("Empty date")
    # Already ISO format
    if len(raw) == 10 and raw[4] == "-":
        return raw
    # Try day-first parsing for slash-separated dates
    for fmt in ("%d/%m/%Y", "%d/%m/%y", "%d-%m-%Y", "%d-%m-%y",
                "%m/%d/%Y", "%m/%d/%y"):
        try:
            dt = datetime.strptime(raw, fmt)
            return dt.strftime("%Y-%m-%d")
        except ValueError:
            continue
    # Fallback: let pandas infer with dayfirst=True
    try:
        dt = pd.to_datetime(raw, dayfirst=True)
        return dt.strftime("%Y-%m-%d")
    except Exception:
        raise ValueError(f"Cannot parse date: {raw!r}")


# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Generate talk markdown files from TSV.")
    parser.add_argument("--tsv",    default="talks.tsv",   help="Input TSV file (default: talks.tsv)")
    parser.add_argument("--output", default="../_talks/",  help="Output directory (default: ../_talks/)")
    args = parser.parse_args()

    os.makedirs(args.output, exist_ok=True)

    talks = pd.read_csv(args.tsv, sep="\t", header=0, encoding="latin-1")
    print(f"Loaded {len(talks)} talks from {args.tsv}")

    written = 0
    for _, item in talks.iterrows():

        # ── Required fields ────────────────────────────────────────────────
        if not is_set(item.get("title")) or not is_set(item.get("url_slug")) or not is_set(item.get("date")):
            print(f"  SKIP: missing title/url_slug/date in row: {dict(item)}")
            continue

        try:
            date = normalise_date(item["date"])
        except ValueError as e:
            print(f"  SKIP: {e}")
            continue

        url_slug  = str(item["url_slug"]).strip()
        md_filename  = f"{date}-{url_slug}.md"
        html_filename = f"{date}-{url_slug}"

        # ── YAML front-matter ──────────────────────────────────────────────
        md  = "---\n"
        md += f'title: "{html_escape(str(item["title"]))}"\n'
        md += "collection: talks\n"
        md += f'type: "{html_escape(str(item["type"])) if is_set(item.get("type")) else "Talk"}"\n'
        md += f"permalink: /talks/{html_filename}\n"

        if is_set(item.get("venue")):
            md += f'venue: "{html_escape(str(item["venue"]))}"\n'

        md += f"date: {date}\n"   # always written — was incorrectly gated on location before

        if is_set(item.get("location")):
            md += f'location: "{html_escape(str(item["location"]))}"\n'

        md += "---\n"

        # ── Body ──────────────────────────────────────────────────────────
        if is_set(item.get("talk_url")):
            md += f"\n[More information here]({str(item['talk_url']).strip()})\n"

        if is_set(item.get("description")):
            md += f"\n{html_escape(str(item['description']))}\n"

        # ── Write file ────────────────────────────────────────────────────
        out_path = os.path.join(args.output, os.path.basename(md_filename))
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(md)

        print(f"  Wrote: {md_filename}")
        written += 1

    print(f"Done. {written}/{len(talks)} talks written to {args.output}")


if __name__ == "__main__":
    main()
