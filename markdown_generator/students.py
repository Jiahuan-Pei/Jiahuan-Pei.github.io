#!/usr/bin/env python3
"""
Student supervision markdown generator for academicpages.

Reads students.xlsx (or a custom file) and writes one .md file per row
into ../_teaching/.

Expected spreadsheet columns (header row required, order doesn't matter):
    Name        – student full name                          [required]
    Type        – PhD | Master | Bachelor | High School      [required]
    Institution – venue / university name
    Thesis / Research Topic – page title
    Start Date  – YYYY-MM-DD
    End Date    – YYYY-MM-DD or empty / "Present"
    Location    – city, country  (optional)
    Notes       – body text shown on the page (optional)

Usage:
    python students.py                          # reads students.xlsx
    python students.py --xlsx my.xlsx           # custom input file
    python students.py --output /path/to/dir/   # custom output directory
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
    if not pd.notna(value):
        return False
    s = str(value).strip()
    return s != "" and s.lower() != "present" and s.lower() != "nan"


def normalise_date(raw) -> str:
    """Return YYYY-MM-DD or empty string."""
    if not pd.notna(raw):
        return ""
    s = str(raw).strip()
    if not s or s.lower() in ("present", "nan", ""):
        return ""
    # Already ISO
    if re.match(r"^\d{4}-\d{2}-\d{2}$", s):
        return s
    # Try common formats
    for fmt in ("%d/%m/%Y", "%d-%m-%Y", "%d/%m/%y", "%d-%m-%y",
                "%Y-%m-%d", "%m/%d/%Y", "%m-%d-%Y"):
        try:
            return datetime.strptime(s, fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue
    # Pandas fallback
    try:
        return pd.to_datetime(s, dayfirst=True).strftime("%Y-%m-%d")
    except Exception:
        return s  # return as-is if unparseable


def slugify(text: str) -> str:
    """Create a URL-safe slug from text."""
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_]+", "-", text)
    return re.sub(r"-{2,}", "-", text)



# ── Column name normalisation ──────────────────────────────────────────────────

COL_MAP = {
    "name":                    "name",
    "type":                    "type",
    "institution":             "venue",
    "thesis / research topic": "title",
    "thesis/research topic":   "title",
    "topic":                   "title",
    "title":                   "title",
    "start date":              "startdate",
    "startdate":               "startdate",
    "end date":                "enddate",
    "enddate":                 "enddate",
    "location":                "location",
    "notes":                   "notes",
    "description":             "notes",
}

def normalise_columns(df: pd.DataFrame) -> pd.DataFrame:
    df.columns = [COL_MAP.get(c.lower().strip(), c.lower().strip()) for c in df.columns]
    return df


# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Generate student supervision markdown files from XLSX.")
    parser.add_argument("--xlsx",   default="students.xlsx",  help="Input XLSX file (default: students.xlsx)")
    parser.add_argument("--output", default="../_teaching/",  help="Output directory (default: ../_teaching/)")
    args = parser.parse_args()

    os.makedirs(args.output, exist_ok=True)

    df = pd.read_excel(args.xlsx, header=0)
    df = normalise_columns(df)
    print(f"Loaded {len(df)} rows from {args.xlsx}")

    written = 0
    skipped = 0
    for _, row in df.iterrows():

        # ── Required fields ────────────────────────────────────────────────
        name = str(row.get("name", "")).strip() if pd.notna(row.get("name", "")) else ""
        typ  = str(row.get("type", "")).strip() if pd.notna(row.get("type", "")) else ""

        if not name or not typ or name.lower() in ("nan", ""):
            print(f"  SKIP: missing name or type → {dict(row)}")
            skipped += 1
            continue

        # ── Dates ──────────────────────────────────────────────────────────
        startdate = normalise_date(row.get("startdate", ""))
        enddate   = normalise_date(row.get("enddate",   ""))

        # ── Filename  <startYYYY-MM>-<type-slug>-<full-name>.md ──────────────
        date_prefix = startdate[:7] if startdate else "0000-00"   # YYYY-MM
        type_slug   = slugify(typ.split()[0])                     # "phd", "master", etc.
        name_slug   = slugify(name)                               # e.g. "jiahuan-pei"
        md_filename = f"{date_prefix}-{type_slug}-{name_slug}.md"
        permalink   = f"/teaching/{date_prefix}-{type_slug}-{name_slug}"

        # ── Optional fields ────────────────────────────────────────────────
        venue    = str(row.get("venue",    "")).strip() if pd.notna(row.get("venue",    "")) else ""
        title    = str(row.get("title",    "")).strip() if pd.notna(row.get("title",    "")) else ""
        location = str(row.get("location", "")).strip() if pd.notna(row.get("location", "")) else ""
        notes    = str(row.get("notes",    "")).strip() if pd.notna(row.get("notes",    "")) else ""

        # ── YAML front-matter ──────────────────────────────────────────────
        md  = "---\n"
        md += f'name: "{html_escape(name)}"\n'
        if title:
            md += f'title: "{html_escape(title)}"\n'
        md += 'role: "Supervisor"\n'
        md += 'collection: teaching\n'
        md += f'type: "{html_escape(typ)}"\n'
        md += f'permalink: {permalink}\n'
        if venue:
            md += f'venue: "{html_escape(venue)}"\n'
        if startdate:
            md += f'startdate: "{startdate}"\n'
        if enddate:
            md += f'enddate: "{enddate}"\n'
        if location:
            md += f'location: "{html_escape(location)}"\n'
        md += "---\n"

        # ── Body ──────────────────────────────────────────────────────────
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
