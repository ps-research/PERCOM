#!/usr/bin/env python3
"""Print statement + source context around the anchor for chosen evidence rows.
Usage: python3 -I show_context.py <review_dir> <width> E001 E002 ..."""
import csv, glob, html, os, re, subprocess, sys

def read_source(path):
    ext = path.rsplit(".", 1)[-1].lower()
    if ext == "pdf":
        return subprocess.run(["pdftotext", "-layout", path, "-"], capture_output=True, text=True, timeout=120).stdout
    raw = open(path, "rb").read().decode("utf-8", "replace")
    if ext in ("html", "htm"):
        raw = re.sub(r"(?is)<(script|style).*?</\1>", " ", raw)
        raw = html.unescape(re.sub(r"(?s)<[^>]+>", " ", raw))
    return raw

def squash(s):
    return re.sub(r"\s+", " ", s.replace("­", ""))

d, width, want = sys.argv[1].rstrip("/"), int(sys.argv[2]), sys.argv[3:]
rows = {r["eid"]: r for r in csv.DictReader(open(os.path.join(d, "evidence.csv"), newline="", encoding="utf-8"))}
for eid in want:
    r = rows[eid]
    pid = r["pid"]
    found = False
    files = sorted(glob.glob(os.path.join(d, "sources", pid + "_*")), key=lambda f: (not f.endswith(".txt"), f))
    a = squash(r["anchor"]).lower()
    for f in files:
        t = squash(read_source(f))
        i = t.lower().find(a)
        if i < 0:
            a2 = re.sub(r"[^a-z0-9]+", "", a)
            comp = re.sub(r"[^a-z0-9]+", "", t.lower())
            if a2 and a2 in comp:
                # locate approximately via first 3 words
                key = " ".join(a.split()[:2])
                i = t.lower().find(key)
        if i >= 0:
            ctx = t[max(0, i - width): i + len(a) + width]
            print(f"### {eid} {pid} [{r['access_level']}] loc: {r['locator']}\nCLAIM: {r['statement']}\nANCHOR: {r['anchor']}\nSOURCE ({os.path.basename(f)}): …{ctx}…\n")
            found = True
            break
    if not found:
        print(f"### {eid} {pid} CONTEXT NOT LOCATED | {r['statement']} | {r['anchor']}\n")
