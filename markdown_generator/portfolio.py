#!/usr/bin/env python3
"""
Portfolio markdown generator for academicpages.

Reads portfolio.xlsx and writes one .md file per row into ../_portfolio/.

Spreadsheet columns (header row required):
    title       – item title                          [required]
    date        – DD/MM/YYYY (used for sorting newest-first)
    image       – local path or URL to a photo        (mutually exclusive with youtube)
    youtube     – YouTube video ID (e.g. dQw4w9WgXcQ) (mutually exclusive with image)
    description – short caption shown on the card
    tags        – comma-separated list of tags
    body        – full page body text (markdown supported)

Usage:
    python portfolio.py                        # reads portfolio.xlsx
    python portfolio.py --xlsx my.xlsx         # custom input file
    python portfolio.py --output /path/        # custom output directory
"""

import argparse
import os
import re
import pandas as pd

# ── Helpers ────────────────────────────────────────────────────────────────────

HTML_ESCAPE = {"&": "&amp;", '"': "&quot;", "'": "&apos;"}

def html_escape(text: str) -> str:
    if not isinstance(text, str):
        return ""
    return "".join(HTML_ESCAPE.get(c, c) for c in text)


def is_set(value) -> bool:
    return pd.notna(value) and str(value).strip() not in ("", "nan")


def slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_]+", "-", text)
    return re.sub(r"-{2,}", "-", text)[:60]


# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Generate portfolio markdown files from XLSX.")
    parser.add_argument("--xlsx",   default="portfolio.xlsx",  help="Input XLSX file (default: portfolio.xlsx)")
    parser.add_argument("--output", default="../_portfolio/",  help="Output directory (default: ../_portfolio/)")
    args = parser.parse_args()

    os.makedirs(args.output, exist_ok=True)

    df = pd.read_excel(args.xlsx, header=0)
    # Sort newest-first by date if column present
    if "date" in df.columns:
        df["_date_sort"] = pd.to_datetime(df["date"], dayfirst=True, errors="coerce")
        df = df.sort_values("_date_sort", ascending=False, na_position="last").drop(columns=["_date_sort"])
        df = df.reset_index(drop=True)
    print(f"Loaded {len(df)} rows from {args.xlsx}")

    written = 0
    skipped = 0
    for idx, row in df.iterrows():

        # ── Required ───────────────────────────────────────────────────────
        title = str(row.get("title", "")).strip() if is_set(row.get("title")) else ""
        if not title:
            print(f"  SKIP row {idx+2}: missing title")
            skipped += 1
            continue

        # ── Optional fields ────────────────────────────────────────────────
        date_raw    = row.get("date", "")
        date        = ""
        if is_set(date_raw):
            try:
                from datetime import datetime
                for fmt in ("%d/%m/%Y", "%Y-%m-%d", "%m/%d/%Y"):
                    try:
                        date = datetime.strptime(str(date_raw).strip(), fmt).strftime("%Y-%m-%d")
                        break
                    except ValueError:
                        continue
                if not date:
                    date = pd.to_datetime(date_raw, dayfirst=True).strftime("%Y-%m-%d")
            except Exception:
                pass
        image       = str(row.get("image",       "")).strip() if is_set(row.get("image"))       else ""
        youtube     = str(row.get("youtube",     "")).strip() if is_set(row.get("youtube"))     else ""
        description = str(row.get("description", "")).strip() if is_set(row.get("description")) else ""
        tags_raw    = str(row.get("tags",        "")).strip() if is_set(row.get("tags"))        else ""
        body        = str(row.get("body",        "")).strip() if is_set(row.get("body"))        else ""
        paper       = str(row.get("paper",       "")).strip() if is_set(row.get("paper"))       else ""
        code        = str(row.get("code",        "")).strip() if is_set(row.get("code"))        else ""
        data        = str(row.get("data",        "")).strip() if is_set(row.get("data"))        else ""

        # Parse comma-separated tags
        tags = [t.strip() for t in tags_raw.split(",") if t.strip()] if tags_raw else []

        # ── Filename ───────────────────────────────────────────────────────
        md_filename = f"{slugify(title)}.md"

        # ── YAML front-matter ──────────────────────────────────────────────
        md  = "---\n"
        md += f'title: "{html_escape(title)}"\n'
        md += "collection: portfolio\n"
        if date:
            md += f'date: "{date}"\n'
        if image:
            md += f'image: "{image}"\n'
        if youtube:
            md += f'youtube: "{youtube}"\n'
        if description:
            md += f'description: "{html_escape(description)}"\n'
        if tags:
            md += "tags:\n"
            for tag in tags:
                md += f"  - {tag}\n"
        md += "---\n"

        # ── Body ──────────────────────────────────────────────────────────
        if not body:
            # Auto-construct body from description + resources
            parts = []
            if description:
                parts.append(description)
            if paper or code or data:
                parts.append("\nInterested in more details? Please see the following resources.")
                resources = []
                if paper:
                    resources.append(f"**Paper:** [{paper}]({paper})")
                if code:
                    resources.append(f"**Code:** [{code}]({code})")
                if data:
                    resources.append(f"**Data:** [{data}]({data})")
                parts.append("  \n".join(resources))
            body = "\n\n".join(parts)

        if body:
            md += f"\n{body}\n"

        # ── Write ─────────────────────────────────────────────────────────
        out_path = os.path.join(args.output, md_filename)
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(md)
        print(f"  Wrote: {md_filename}")
        written += 1

    print(f"Done. {written} written, {skipped} skipped → {args.output}")


if __name__ == "__main__":
    main()
