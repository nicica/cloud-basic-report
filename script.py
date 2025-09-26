#!/usr/bin/env python3
"""
Convert the Excel-style section of an iozone output file
into one CSV per report inside a subdirectory 'iozone_csv'.
"""

import re
from pathlib import Path
import csv

INPUT_FILE = "iozone_shared_results.txt"   # change path if needed
OUTPUT_DIR = Path("iozone_csv")            # subdirectory for CSVs
OUTPUT_DIR.mkdir(exist_ok=True)

text = Path(INPUT_FILE).read_text(errors="ignore").splitlines()

# Find the start of the Excel output section
start_idx = None
for i, line in enumerate(text):
    if line.strip().lower().startswith("excel output is below"):
        start_idx = i + 1
        break
if start_idx is None:
    raise SystemExit("Could not find 'Excel output is below:' in file.")

lines = text[start_idx:]
reports = []

report_title_re = re.compile(r'^\s*"([^"]+?) report"\s*$', re.IGNORECASE)

def parse_header(line):
    return [m.group(1) for m in re.finditer(r'"([^"]+)"', line)]

def parse_row(line):
    m = re.match(r'^\s*"([^"]+)"\s*(.*)$', line)
    if not m:
        return None, None
    row_label = m.group(1)
    vals = [v for v in re.split(r'\s+', m.group(2).strip()) if v]
    return row_label, vals

i = 0
while i < len(lines):
    m = report_title_re.match(lines[i])
    if m:
        name = m.group(1).strip()
        i += 1
        while i < len(lines) and not lines[i].strip():
            i += 1
        if i >= len(lines):
            break
        header = parse_header(lines[i]) or re.split(r'\s+', lines[i].strip())
        i += 1
        rows = []
        while i < len(lines):
            if not lines[i].strip() or report_title_re.match(lines[i]):
                break
            row_label, vals = parse_row(lines[i])
            if row_label:
                rows.append((row_label, vals))
            i += 1
        reports.append((name, header, rows))
    else:
        i += 1

for name, header, rows in reports:
    safe_name = re.sub(r'[^A-Za-z0-9]+', "_", name.lower()).strip("_")
    out_path = OUTPUT_DIR / f"iozone_{safe_name}_report.csv"

    # prepend 'kb' column for the row label
    max_cols = len(header)
    with open(out_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["kb"] + header)
        for row_label, vals in rows:
            vals_adj = vals[:max_cols] + [""] * max(0, max_cols - len(vals))
            writer.writerow([row_label] + vals_adj)

print(f"Exported {len(reports)} reports to '{OUTPUT_DIR}' directory.")
