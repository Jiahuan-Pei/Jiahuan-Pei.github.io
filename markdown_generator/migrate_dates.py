#!/usr/bin/env python3
"""
One-time migration: convert date columns in all xlsx files from DD/MM/YYYY to YYYY-MM-DD.
Run once, then delete this script.
"""
import pandas as pd
from pathlib import Path

DATE_COLS = {
    "talks.xlsx":     ["date"],
    "students.xlsx":  ["startdate", "enddate"],
    "courses.xlsx":   ["startdate", "enddate"],
    "portfolio.xlsx": ["date"],
}

base = Path(__file__).parent

for fname, cols in DATE_COLS.items():
    path = base / fname
    if not path.exists():
        print(f"SKIP {fname} (not found)")
        continue
    df = pd.read_excel(path, header=0, dtype=str)
    changed = False
    for col in cols:
        if col not in df.columns:
            continue
        def convert(v):
            if pd.isna(v) or str(v).strip() in ("", "nan"):
                return v
            try:
                return pd.to_datetime(str(v).strip(), dayfirst=True).strftime("%Y-%m-%d")
            except Exception:
                return v
        new_col = df[col].apply(convert)
        if not new_col.equals(df[col]):
            df[col] = new_col
            changed = True
            print(f"  {fname}: converted '{col}'")
    if changed:
        df.to_excel(path, index=False)
        print(f"  Saved {fname}")
    else:
        print(f"  {fname}: no changes needed")

print("Done.")
