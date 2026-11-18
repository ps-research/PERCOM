"""Build the paper's REFERENCES.bib from the literature review's refs.bib.

The review's refs.bib stays untouched. Every change made for the paper is listed here,
so no reference is edited by hand:

* provenance fields of the review (note, ISSN, keywords, language, copyright, series,
  collection, abstract) are dropped, so they do not print in the reference list;
* journal and conference entries that carry a DOI drop their URL, as in the IEEE
  template's examples; other entries keep it;
* arXiv entries get ``howpublished = {arXiv:<id>}``, the template's form;
* IEEEtran sets titles in sentence case (the template: "Capitalize only the first
  word in a paper title, except for proper nouns"), so acronyms, system names and
  proper nouns in titles are protected with braces;
* months become BibTeX month macros; non-ASCII characters become LaTeX accents.

    python3 code/p1/paper/make_references.py --out <overleaf clone>/REFERENCES.bib
"""
from __future__ import annotations

import argparse
import hashlib
import re
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SOURCE = ROOT / "litreview" / "p1-tabular-localization" / "refs.bib"

DROP = {"note", "issn", "keywords", "language", "copyright", "series", "collection", "abstract"}
MONTHS = {"jan": "jan", "feb": "feb", "mar": "mar", "apr": "apr", "may": "may", "jun": "jun",
          "jul": "jul", "aug": "aug", "sep": "sep", "oct": "oct", "nov": "nov", "dec": "dec"}
PROTECT_WORDS = {"Wi-Fi", "Gaussian", "Horus"}  # proper nouns and names the case rule would lower
# Fields missing from the review's entries, each with where it was read.
OVERRIDES = {
    # Article number 25: publisher page metadata citation_firstpage="25", citation_volume="3"
    # (litreview/p1-tabular-localization/sources/P009_sodindoorloc_paper.html); CONTEXT.md cites "Satellite Navigation 3:25 (2022)".
    "bi2022sodindoorloc": {"pages": "25"},
    # Year 2000: the proceedings title itself, "Proceedings IEEE INFOCOM 2000" (refs.bib booktitle).
    "bahl2000radar": {"year": "2000"},
    # Family name "Le Morvan" (two words), as in the paper's byline "Marine Le Morvan"; the braces keep BibTeX
    # from reading "Le" as a middle name ("M. L. Morvan").
    "qu2026tabiclv2": {"author": 'Jingang Qu and David Holzm{\\"u}ller and Ga{\\"e}l Varoquaux and Marine {Le Morvan}'},
}
ACCENTS = {"́": "'", "̀": "`", "̈": '"', "̂": "^", "̃": "~", "̧": "c", "̌": "v"}
PLAIN = {"–": "--", "—": "---", "’": "'", "‘": "`"}


def parse(text: str):
    """[(type, key, [(field, raw value)])] from a .bib file; brace-matched, no external parser."""
    entries, i = [], 0
    while (m := re.compile(r"@(\w+)\s*\{\s*([^,\s]+)\s*,").search(text, i)):
        etype, key, j, fields = m.group(1).lower(), m.group(2), m.end(), []
        while True:
            fm = re.compile(r"\s*,?\s*(\w+)\s*=\s*").match(text, j)
            if not fm:
                end = text.index("}", j)
                break
            name, j = fm.group(1), fm.end()
            if text[j] == "{":
                depth, k = 0, j
                while True:
                    depth += {"{": 1, "}": -1}.get(text[k], 0)
                    if depth == 0:
                        break
                    k += 1
                value, j = text[j + 1:k], k + 1
            elif text[j] == '"':
                k = text.index('"', j + 1)
                value, j = text[j + 1:k], k + 1
            else:
                bm = re.compile(r"[^,}\s]+").match(text, j)
                value, j = bm.group(0), bm.end()
            fields.append((name, value))
        entries.append((etype, key, fields))
        i = end + 1
    return entries


def latex_accents(s: str) -> str:
    out = []
    for ch in s:
        if ord(ch) < 128:
            out.append(ch)
        elif ch in PLAIN:
            out.append(PLAIN[ch])
        else:
            base, *marks = unicodedata.normalize("NFD", ch)
            if len(marks) == 1 and marks[0] in ACCENTS:
                out.append("{\\%s%s}" % (ACCENTS[marks[0]], "\\i" if base == "i" else base))
            else:
                raise SystemExit(f"no LaTeX form for character {ch!r}; add it to make_references.py")
    return "".join(out)


def protect_title(title: str) -> str:
    def guard(part: str) -> str:
        core = part.strip(":,.;()")
        if not core or core.startswith("{"):
            return part
        upper_inside = any(c.isupper() for c in core[1:])
        mixed_digit = any(c.isdigit() for c in core) and any(c.isalpha() for c in core)
        if upper_inside or mixed_digit or (core.isupper() and len(core) > 1):
            return part.replace(core, "{" + core + "}", 1)
        return part

    words = []
    for word in title.split(" "):
        bare = word.strip(":,.;()")
        if bare in PROTECT_WORDS:
            words.append(word.replace(bare, "{" + bare + "}", 1))
        else:
            words.append("-".join(guard(p) for p in word.split("-")))
    return " ".join(words)


def transform(etype: str, fields: list[tuple[str, str]]):
    d = {n.lower(): v for n, v in fields}
    out = []
    for name, value in fields:
        low = name.lower()
        if low in DROP:
            continue
        if low == "url" and "doi" in d and etype in {"article", "inproceedings"}:
            continue
        if low in {"eprint", "archiveprefix", "primaryclass"}:
            continue
        if low == "month":
            mon = MONTHS.get(value.strip("{}").lower()[:3])
            if not mon:
                raise SystemExit(f"unknown month {value!r}")
            out.append((low, mon, True))
            continue
        if low == "title":
            value = protect_title(value)
        out.append((low, latex_accents(value), False))
    if d.get("archiveprefix", "").lower() == "arxiv" and "eprint" in d:
        out.append(("howpublished", f"arXiv:{d['eprint']}", False))
    return out


def render(entries, source_hash: str) -> str:
    lines = [f"% Generated by code/p1/paper/make_references.py from litreview/p1-tabular-localization/refs.bib",
             f"% (sha256 {source_hash}). Do not edit by hand.", ""]
    for etype, key, fields in entries:
        lines.append(f"@{etype}{{{key},")
        out = transform(etype, fields)
        for name, value in OVERRIDES.get(key, {}).items():
            out = [f for f in out if f[0] != name] + [(name, value, False)]
        for name, value, bare in out:
            lines.append(f"  {name} = {value}," if bare else f"  {name} = {{{value}}},")
        lines.append("}\n")
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--out", required=True, type=Path)
    args = ap.parse_args()
    text = SOURCE.read_text(encoding="utf-8")
    entries = parse(text)
    if len(entries) != text.count("\n@") + text.startswith("@"):
        raise SystemExit(f"parsed {len(entries)} entries, but the file has {text.count(chr(10) + '@') + text.startswith('@')}")
    out = render(entries, hashlib.sha256(text.encode()).hexdigest()[:12])
    args.out.write_text(out, encoding="ascii")
    print(f"wrote {args.out}: {len(entries)} entries")


if __name__ == "__main__":
    main()
