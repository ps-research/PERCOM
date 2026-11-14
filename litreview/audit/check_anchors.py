#!/usr/bin/env python3
"""Check every evidence row: does the anchor phrase occur in a saved source file of that pid?
Usage: python3 -I check_anchors.py <review_dir>
Writes <audit_dir>/<review>_anchor_check.csv and prints a summary."""
import csv, glob, html, os, re, subprocess, sys, hashlib, unicodedata

def norm(s):
    s = unicodedata.normalize("NFKD", s)
    s = s.replace("­", "")
    s = re.sub(r"-\s*\n\s*", "", s)            # de-hyphenate line breaks
    s = s.lower()
    s = re.sub(r"[‘’“”\"'`]", "", s)
    s = re.sub(r"[‐-―−]", "-", s)
    s = re.sub(r"[^a-z0-9%.+\-]+", " ", s)
    return re.sub(r"\s+", " ", s).strip()

def loose(s):
    return re.sub(r"[^a-z0-9]+", "", norm(s))

def read_source(path):
    ext = path.rsplit(".", 1)[-1].lower()
    if ext == "pdf":
        try:
            return subprocess.run(["pdftotext", path, "-"], capture_output=True, text=True, timeout=120).stdout
        except Exception:
            return ""
    raw = open(path, "rb").read().decode("utf-8", "replace")
    if ext in ("html", "htm"):
        raw = re.sub(r"(?is)<(script|style).*?</\1>", " ", raw)
        raw = html.unescape(re.sub(r"(?s)<[^>]+>", " ", raw))
    return raw

def main(d):
    d = d.rstrip("/")
    name = os.path.basename(d)
    out_dir = os.path.dirname(os.path.abspath(__file__))
    idx = {r["pid"]: r for r in csv.DictReader(open(os.path.join(d, "sources/index.csv"), newline="", encoding="utf-8"))}
    files = {}
    for f in sorted(glob.glob(os.path.join(d, "sources", "*"))):
        b = os.path.basename(f)
        m = re.match(r"(P\d+)", b)
        if m:
            files.setdefault(m.group(1), []).append(f)
    cache = {}
    def texts(pid):
        if pid not in cache:
            t = "\n".join(read_source(f) for f in files.get(pid, []))
            cache[pid] = (norm(t), loose(t))
        return cache[pid]
    rows = list(csv.DictReader(open(os.path.join(d, "evidence.csv"), newline="", encoding="utf-8")))
    res = []
    for r in rows:
        pid = r["pid"].strip()
        anchor = r["anchor"].strip()
        if pid not in idx:
            status = "PID_NOT_IN_INDEX"
        elif pid not in files:
            status = "NO_SOURCE_FILE"
        elif not anchor:
            status = "NO_ANCHOR"
        else:
            n, l = texts(pid)
            a, al = norm(anchor), loose(anchor)
            if a and a in n:
                status = "EXACT"
            elif al and al in l:
                status = "LOOSE"
            else:
                # try split on ellipsis
                parts = [p for p in re.split(r"\.\.\.|…", anchor) if len(loose(p)) >= 8]
                if len(parts) > 1 and all(loose(p) in l for p in parts):
                    status = "PARTS"
                else:
                    status = "MISSING"
        res.append({"eid": r["eid"], "pid": pid, "status": status, "anchor_words": len(anchor.split()), "access": r.get("access_level", ""), "anchor": anchor})
    with open(os.path.join(out_dir, f"{name}_anchor_check.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(res[0].keys())); w.writeheader(); w.writerows(res)
    from collections import Counter
    c = Counter(x["status"] for x in res)
    print(f"== {name}: {len(res)} rows | " + ", ".join(f"{k} {v}" for k, v in sorted(c.items())))
    for x in res:
        if x["status"] not in ("EXACT", "LOOSE", "PARTS"):
            print(f"   {x['eid']} {x['pid']} [{x['status']}] {x['anchor'][:110]}")
    # sha256 check of saved files against index
    bad = 0; checked = 0
    for pid, r in idx.items():
        want = (r.get("sha256") or "").strip().lower()
        if not want:
            continue
        got = {hashlib.sha256(open(f, "rb").read()).hexdigest() for f in files.get(pid, [])}
        checked += 1
        if want not in got:
            bad += 1
            print(f"   sha256 mismatch {pid}: index {want[:12]}… files {[g[:12] for g in got]}")
    print(f"   sha256: {checked - bad}/{checked} index hashes match a saved file; pids in index without file: {sorted(set(idx) - set(files))}")
    long_anchor = [x['eid'] for x in res if x['anchor_words'] > 12]
    print(f"   anchors over 12 words: {len(long_anchor)}")
    used = {x['pid'] for x in res}
    print(f"   sources never cited in ledger: {sorted(set(idx) - used)}")

if __name__ == "__main__":
    main(sys.argv[1])
