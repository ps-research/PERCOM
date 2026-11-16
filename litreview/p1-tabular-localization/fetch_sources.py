#!/usr/bin/env python3
"""Fetch the Paper 1 sources that are not in the repository, so that a local copy of every
full-text source the review relied on is available.

Usage, from the repository root:
    python3 litreview/p1-tabular-localization/fetch_sources.py

Downloads into data/litreview-sources/ (data/ is ignored by git), checks each file against the
SHA-256 recorded in sources/index.csv, and writes a text version next to each PDF when
pdftotext is installed. A checksum mismatch usually means arXiv now serves a newer version;
the file is kept and the mismatch is reported.

Three sources cannot be fetched this way; see sources/NOT_IN_REPO.md.
"""
import csv
import hashlib
import os
import shutil
import subprocess
import sys
import time
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
OUT = os.path.join(ROOT, "data", "litreview-sources")
FETCH = {  # pid: file name; the URL comes from sources/index.csv
    "P004": "P004_locaris_long_2510.11926.pdf",
    "P006": "P006_tabpfn3_2605.13986.pdf",
    "P008": "P008_tabicl_2502.05564.pdf",
    "P014": "P014_ra_lwlm_2606.01899.pdf",
}


def main():
    index = {r["pid"]: r for r in csv.DictReader(open(os.path.join(HERE, "sources", "index.csv"), newline="", encoding="utf-8"))}
    os.makedirs(OUT, exist_ok=True)
    have_pdftotext = shutil.which("pdftotext") is not None
    status = 0
    for pid, name in FETCH.items():
        row = index[pid]
        url = row["url_fetched"]
        path = os.path.join(OUT, name)
        if not os.path.exists(path):
            req = urllib.request.Request(url, headers={"User-Agent": "percom-litreview-fetch/1.0"})
            with urllib.request.urlopen(req, timeout=120) as r, open(path, "wb") as fh:
                fh.write(r.read())
            time.sleep(3)  # arXiv asks for at least 3 s between requests
        got = hashlib.sha256(open(path, "rb").read()).hexdigest()
        want = row["sha256"].strip().lower()
        verdict = "matches the review's copy" if got == want else "DIFFERS from the review's copy (probably a newer arXiv version)"
        if got != want:
            status = 1
        print(f"{pid} {name}: {verdict}")
        if have_pdftotext:
            subprocess.run(["pdftotext", "-layout", path, path[:-4] + ".txt"], check=False)
    print(f"\nFiles are in {OUT}")
    if not have_pdftotext:
        print("pdftotext not found; no text versions written.")
    return status


if __name__ == "__main__":
    sys.exit(main())
