#!/usr/bin/env python3
"""Independent existence check for sources that have neither a DOI nor an arXiv id in the index:
search Crossref by title and report the best match (title similarity, venue, year, DOI).
Usage: python3 -I recheck_titles.py <review_dir>"""
import csv, json, os, re, sys, time, urllib.request, urllib.parse, difflib
d = sys.argv[1].rstrip("/")
rows = list(csv.DictReader(open(os.path.join(d, "sources/index.csv"), newline="", encoding="utf-8")))
norm = lambda s: re.sub(r"[^a-z0-9]+", " ", s.lower()).strip()
out = []
for r in rows:
    blob = r.get("doi_or_arxiv", "") + " " + r.get("url_fetched", "")
    if re.search(r"10\.\d{4,9}/", r.get("doi_or_arxiv", "")) or "arxiv" in blob.lower():
        continue
    q = urllib.parse.quote(r["title"][:200])
    url = f"https://api.crossref.org/works?rows=3&query.bibliographic={q}&select=DOI,title,container-title,issued,author"
    try:
        items = json.load(urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "litreview-audit/0.1 (mailto:noreply@example.org)"}), timeout=40))["message"]["items"]
    except Exception as e:
        print(f"  ERR {r['pid']} {str(e)[:60]}"); continue
    best = None
    for it in items:
        t = (it.get("title") or [""])[0]
        ratio = difflib.SequenceMatcher(None, norm(t), norm(r["title"])).ratio()
        if best is None or ratio > best[0]:
            best = (ratio, t, it)
    if best is None:
        print(f"  NONE  {r['pid']} {r['title'][:70]}"); continue
    ratio, t, it = best
    year = (it.get("issued", {}).get("date-parts") or [[None]])[0][0]
    venue = (it.get("container-title") or [""])[0]
    fam = (it.get("author") or [{}])[0].get("family", "")
    a_ok = fam.lower() in r.get("authors", "").lower() if fam else None
    flag = "ok   " if ratio >= 0.85 else "CHECK"
    print(f"  {flag} {r['pid']} sim {ratio:.2f} author_ok {a_ok} | {it.get('DOI')} | {venue[:40]} {year} | index: {r.get('venue','')[:30]} {r.get('year','')}" + ("" if ratio >= 0.85 else f"\n        index: {r['title'][:85]}\n        found: {t[:85]}"))
    out.append({"pid": r["pid"], "similarity": round(ratio, 3), "doi_found": it.get("DOI"), "venue_found": venue, "year_found": year, "first_author_matches": a_ok, "title_index": r["title"], "title_found": t})
    time.sleep(0.5)
with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), os.path.basename(d) + "_title_check.csv"), "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=list(out[0].keys())); w.writeheader(); w.writerows(out)
