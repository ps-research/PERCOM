#!/usr/bin/env python3
"""Independent re-fetch: resolve every non-arXiv DOI in an index through Crossref (fallback DataCite) and compare titles.
Usage: python3 -I recheck_doi.py <review_dir>"""
import csv, json, os, re, sys, time, urllib.request, urllib.parse, difflib
d = sys.argv[1].rstrip("/")
rows = list(csv.DictReader(open(os.path.join(d, "sources/index.csv"), newline="", encoding="utf-8")))
norm = lambda s: re.sub(r"[^a-z0-9]+", " ", s.lower()).strip()
def get(url):
    try:
        return json.load(urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "litreview-audit/0.1 (mailto:noreply@example.org)"}), timeout=40))
    except Exception as e:
        return {"_err": str(e)[:80]}
n = ok = 0
nodoi = []
for r in rows:
    blob = r.get("doi_or_arxiv", "")
    m = re.search(r"(10\.\d{4,9}/[^\s;,|]+)", blob)
    if not m:
        if "arxiv" not in (blob + r.get("url_fetched", "")).lower():
            nodoi.append(f"{r['pid']} {r['title'][:60]} | {blob[:40]} | {r.get('url_fetched','')[:60]}")
        continue
    doi = m.group(1).rstrip(".)")
    if doi.lower().startswith("10.48550"):
        continue
    n += 1
    j = get("https://api.crossref.org/works/" + urllib.parse.quote(doi))
    title = venue = year = None
    if "message" in j:
        msg = j["message"]
        title = (msg.get("title") or [""])[0]; venue = (msg.get("container-title") or [""])[0]
        year = (msg.get("issued", {}).get("date-parts") or [[None]])[0][0]
    else:
        j2 = get("https://api.datacite.org/dois/" + urllib.parse.quote(doi))
        a = j2.get("data", {}).get("attributes", {})
        if a:
            title = (a.get("titles") or [{}])[0].get("title", ""); venue = a.get("publisher"); year = a.get("publicationYear")
    if title is None:
        print(f"  UNRESOLVED {r['pid']} {doi} ({j.get('_err')})")
    else:
        ratio = difflib.SequenceMatcher(None, norm(title), norm(r["title"])).ratio()
        flag = "ok " if ratio >= 0.8 else "CHECK"
        ok += ratio >= 0.8
        print(f"  {flag} {r['pid']} {doi} | registry: {str(venue)[:38]} {year} | index: {r.get('venue','')[:38]} {r.get('year','')}" + ("" if ratio >= 0.8 else f"\n       index title: {r['title'][:80]}\n       registry   : {title[:80]}"))
    time.sleep(0.4)
print(f"{os.path.basename(d)}: {ok}/{n} DOIs confirmed by registry title")
print("  sources with neither DOI nor arXiv id:"); [print("   ", x) for x in nodoi]
