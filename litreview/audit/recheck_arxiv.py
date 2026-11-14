#!/usr/bin/env python3
"""Independent re-fetch: ask arXiv for every arXiv id in an index and compare titles.
Usage: python3 -I recheck_arxiv.py <review_dir>"""
import csv, os, re, sys, time, urllib.request, difflib
import xml.etree.ElementTree as ET
d = sys.argv[1].rstrip("/")
rows = list(csv.DictReader(open(os.path.join(d, "sources/index.csv"), newline="", encoding="utf-8")))
ids = {}
for r in rows:
    blob = " ".join([r.get("doi_or_arxiv", ""), r.get("url_fetched", "")])
    m = re.search(r"(?<!\d)(\d{4}\.\d{4,5})(?!\d)", blob)
    if m and ("arxiv" in blob.lower()):
        ids[m.group(1)] = r
print(f"{os.path.basename(d)}: {len(rows)} sources, {len(ids)} with an arXiv id")
norm = lambda s: re.sub(r"[^a-z0-9]+", " ", s.lower()).strip()
got = {}
keys = sorted(ids)
for i in range(0, len(keys), 25):
    chunk = keys[i:i+25]
    url = "http://export.arxiv.org/api/query?max_results=50&id_list=" + ",".join(chunk)
    for attempt in range(3):
        try:
            xml = urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "litreview-audit/0.1"}), timeout=60).read()
            break
        except Exception as e:
            xml = None; err = e; time.sleep(6)
    if xml is None:
        print("  fetch failed:", err); continue
    ns = {"a": "http://www.w3.org/2005/Atom"}
    for e in ET.fromstring(xml).findall("a:entry", ns):
        aid = re.search(r"(\d{4}\.\d{4,5})", e.find("a:id", ns).text).group(1)
        got[aid] = (" ".join(e.find("a:title", ns).text.split()), [a.find("a:name", ns).text for a in e.findall("a:author", ns)], e.find("a:published", ns).text[:10])
    time.sleep(4)
ok = bad = miss = 0
for k in keys:
    r = ids[k]
    if k not in got:
        miss += 1; print(f"  NOT RETURNED {r['pid']} {k} | {r['title'][:70]}"); continue
    t, authors, pub = got[k]
    ratio = difflib.SequenceMatcher(None, norm(t), norm(r["title"])).ratio()
    first = authors[0].split()[-1].lower() if authors else ""
    a_ok = first in r.get("authors", "").lower()
    if ratio >= 0.85 and a_ok:
        ok += 1
    else:
        bad += 1
        print(f"  CHECK {r['pid']} {k} ratio {ratio:.2f} author_ok {a_ok}\n     index: {r['title'][:90]} | {r.get('authors','')[:50]} | {r.get('year','')}\n     arxiv: {t[:90]} | {', '.join(authors[:3])} | {pub}")
print(f"  title+first-author confirmed {ok}, to check {bad}, not returned {miss}")
