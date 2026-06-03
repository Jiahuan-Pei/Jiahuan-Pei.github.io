#!/usr/bin/env python3
"""
Teaching course markdown generator for academicpages.

Reads courses.xlsx and writes one .md file per row into ../_teaching/.

Spreadsheet columns (header row required):
    title     – course title                          [required]
    type      – e.g. "Bachelor Course", "Master Course"
    url_slug  – slug for filename and permalink       [required]
    venue      – university / institution name
    date       – DD/MM/YYYY
    location   – city, country
    course_url – link to the course page (optional)
    notes      – body text shown on the page (markdown supported)

Usage:
    python courses.py                        # reads courses.xlsx
    python courses.py --xlsx my.xlsx         # custom input file
    python courses.py --output /path/        # custom output directory
"""

import argparse
import os
import re
import pandas as pd
from datetime import datetime

# ── Helpers ────────────────────────────────────────────────────────────────────

HTML_ESCAPE = {"&": "&amp;", '"': "&quot;", "'": "&apos;"}

def html_escape(text: str) -> str:
    if not isinstance(text, str):
        return ""
    return "".join(HTML_ESCAPE.get(c, c) for c in text)


def is_set(value) -> bool:
    return pd.notna(value) and str(value).strip() not in ("", "nan")


def normalise_date(raw) -> str:
    if not pd.notna(raw):
        return ""
    s = str(raw).strip()
    if not s or s.lower() in ("nan", ""):
        return ""
    if re.match(r"^\d{4}-\d{2}-\d{2}$", s):
        return s
    for fmt in ("%d/%m/%Y", "%d-%m-%Y", "%d/%m/%y", "%d-%m-%y",
                "%Y-%m-%d", "%m/%d/%Y", "%m-%d-%Y"):
        try:
            return datetime.strptime(s, fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue
    try:
        return pd.to_datetime(s, dayfirst=True).strftime("%Y-%m-%d")
    except Exception:
        return s


# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Generate teaching course markdown files from XLSX.")
    parser.add_argument("--xlsx",   default="courses.xlsx",   help="Input XLSX file (default: courses.xlsx)")
    parser.add_argument("--output", default="../_teaching/",  help="Output directory (default: ../_teaching/)")
    args = parser.parse_args()

    os.makedirs(args.output, exist_ok=True)

    df = pd.read_excel(args.xlsx, header=0)
    print(f"Loaded {len(df)} rows from {args.xlsx}")

    written = 0
    skipped = 0
    for _, row in df.iterrows():

        # ── Required fields ────────────────────────────────────────────────
        title    = str(row.get("title",    "")).strip() if is_set(row.get("title"))    else ""
        url_slug = str(row.get("url_slug", "")).strip() if is_set(row.get("url_slug")) else ""

        if not title or not url_slug:
            print(f"  SKIP: missing title or url_slug → {dict(row)}")
            skipped += 1
            continue

        # ── Optional fields ────────────────────────────────────────────────
        course_type = str(row.get("type",     "")).strip() if is_set(row.get("type"))     else ""
        venue       = str(row.get("venue",    "")).strip() if is_set(row.get("venue"))    else ""
        date        = normalise_date(row.get("date", ""))
        location    = str(row.get("location",   "")).strip() if is_set(row.get("location"))   else ""
        course_url  = str(row.get("course_url", "")).strip() if is_set(row.get("course_url")) else ""
        notes       = str(row.get("notes",      "")).strip() if is_set(row.get("notes"))      else ""

        # Ensure 'course-' prefix
        slug_with_prefix = url_slug if url_slug.startswith("course-") else f"course-{url_slug}"
        md_filename = f"{slug_with_prefix}.md"
        permalink   = f"/teaching/{slug_with_prefix}"

        # ── YAML front-matter ──────────────────────────────────────────────
        md  = "---\n"
        md += f'title: "{html_escape(title)}"\n'
        md += 'role: "Teacher"\n'
        md += 'collection: teaching\n'
        if course_type:
            md += f'type: "{html_escape(course_type)}"\n'
        md += f'permalink: {permalink}\n'
        if venue:
            md += f'venue: "{html_escape(venue)}"\n'
        if date:
            md += f'date: "{date}"\n'
        if location:
            md += f'location: "{html_escape(location)}"\n'
        if course_url:
            md += f'course_url: "{course_url}"\n'
        md += "---\n"

        # ── Body ──────────────────────────────────────────────────────────
        if course_url:
            md += f"\n[Course page]({course_url})\n"
        if notes:
            md += f"\n{notes}\n"

        # ── Write ─────────────────────────────────────────────────────────
        out_path = os.path.join(args.output, md_filename)
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(md)
        print(f"  Wrote: {md_filename}")
        written += 1

    print(f"Done. {written} written, {skipped} skipped → {args.output}")


if __name__ == "__main__":
    main()
