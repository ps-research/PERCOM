"""Build the paper in a scratch folder and check it against the venue rules.

The rules come from the PerCom 2027 WiP call, the IEEE conference template and the
IEEEtran HOWTO (listed with their sources in the PI's plan notes, VENUE_RULES.md).

    python3 code/p1/paper/check_paper.py --src <overleaf clone> --work <scratch dir> [--stage submission]

It copies the project to ``--work``, runs pdflatex, bibtex (when there are citations)
and pdflatex twice, then reads the PDF, the log and the LaTeX source. The log is read
with Python, never grep. Exit code 1 means at least one FAIL.

Honesty boundary: it tests the listed rules only. It cannot tell whether a sentence is
true or whether a number is the right one for its claim.
"""
from __future__ import annotations

import argparse
import os
import re
import shutil
import subprocess
from pathlib import Path

TEMPLATE_PHRASES = [
    "This document is a model and instructions",
    "Identify applicable funding agency",
    "Given Name Surname",
    "dept. name of organization",
    "Conference Paper Title",
    "IEEE conference templates contain guidance text",
    "Sub-titles are not captured",
]
PLACEHOLDERS = ["Author names to be added", "email to be added", "0000-0000-0000-0000", "Lorem ipsum"]
LAYOUT_COMMANDS = [
    r"\\vspace\b", r"\\vskip\b", r"\\baselinestretch\b", r"\\linespread\b",
    r"\\usepackage(\[[^\]]*\])?\{geometry\}", r"\\(set|addto)length\{?\\(textheight|textwidth|columnsep|topmargin|oddsidemargin|evensidemargin|headsep|footskip)\b",
    r"\\(set|addto)length\{?\\\w*skip\b", r"\\enlargethispage\b",
]
LETTER = (612.0, 792.0)
# Names that contain digits but are not numbers: models and the building CETC331.
NAMES_WITH_DIGITS = [r"\(C[12]\)", r"TabPFN v2", r"TabICLv2", r"CETC331", r"5G", r"2-D", r"RTX PRO 6000", r"\b\d+(st|nd|rd|th)\b", r"\bseed \d+\b", r"\{(tabpfn|tabicl)\} \d+\.\d+\.\d+"]  # library versions, after \texttt is stripped


class Report:
    def __init__(self):
        self.rows = []

    def add(self, level, name, detail=""):
        self.rows.append((level, name, detail))

    def show(self):
        for level, name, detail in self.rows:
            print(f"{level:4}  {name}" + (f": {detail}" if detail else ""))
        n_fail = sum(1 for r in self.rows if r[0] == "FAIL")
        n_warn = sum(1 for r in self.rows if r[0] == "WARN")
        print(f"\n{n_fail} FAIL, {n_warn} WARN, {len(self.rows) - n_fail - n_warn} PASS")
        return n_fail


def strip_comments(text: str) -> str:
    return "\n".join(re.sub(r"(?<!\\)%.*", "", line) for line in text.splitlines())


def input_files(src: Path, main: str = "main.tex") -> list[Path]:
    """main.tex and every file it reaches through \\input or \\include, in order."""
    seen, order = set(), []

    def visit(path: Path):
        if path in seen or not path.exists():
            return
        seen.add(path)
        order.append(path)
        for m in re.finditer(r"\\(?:input|include)\{([^}]+)\}", strip_comments(path.read_text())):
            name = m.group(1)
            child = src / (name if name.endswith(".tex") else name + ".tex")
            visit(child)

    visit(src / main)
    return order


def braced(text: str, start: int) -> str:
    """Content of the brace group opening at ``text[start] == '{'``."""
    depth, i = 0, start
    while i < len(text):
        if text[i] == "{" and text[i - 1] != "\\":
            depth += 1
        elif text[i] == "}" and text[i - 1] != "\\":
            depth -= 1
            if depth == 0:
                return text[start + 1:i]
        i += 1
    return text[start + 1:]


def build(src: Path, work: Path, texmf: Path | None = None) -> tuple[Path, Path]:
    if work.exists():
        shutil.rmtree(work)
    shutil.copytree(src, work, ignore=shutil.ignore_patterns(".git"))
    env = dict(os.environ)
    if texmf:  # extra TeX Live packages the local install lacks (Overleaf has them)
        env["TEXINPUTS"] = f"{texmf}//:" + env.get("TEXINPUTS", "")
        env["BSTINPUTS"] = f"{texmf}//:" + env.get("BSTINPUTS", "")
    run = lambda *cmd: subprocess.run(cmd, cwd=work, capture_output=True, text=True, errors="replace", env=env)
    latex = ("pdflatex", "-interaction=nonstopmode", "-file-line-error", "main.tex")
    run(*latex)
    aux = (work / "main.aux").read_text(errors="replace") if (work / "main.aux").exists() else ""
    if "\\citation" in aux and "\\bibdata" in aux:
        bib = run("bibtex", "main")
        (work / "bibtex.out").write_text(bib.stdout + bib.stderr)
    run(*latex)
    run(*latex)
    return work / "main.pdf", work / "main.log"


def check_log(log: Path, rep: Report, stage: str = "draft"):
    if not log.exists():
        rep.add("FAIL", "LaTeX log", "missing")
        return
    text = log.read_text(errors="replace")
    lines = text.splitlines()
    errors = [l for l in lines if l.startswith("! ") or re.match(r"^\S+\.tex:\d+: ", l)]
    rep.add("FAIL" if errors else "PASS", "LaTeX errors", f"{len(errors)}" + (f", first: {errors[0][:120]}" if errors else ""))
    cites = sorted(set(re.findall(r"Citation `([^']+)' on page", text)))
    refs = sorted(set(re.findall(r"Reference `([^']+)' on page", text)))
    rep.add("FAIL" if cites else "PASS", "undefined citations", ", ".join(cites) or "none")
    # sections enter one by one, so a cross-reference to a section not yet written is a warning until submission
    rep.add(("FAIL" if stage == "submission" else "WARN") if refs else "PASS", "undefined references", ", ".join(refs) or "none")
    overfull = [l for l in lines if l.startswith("Overfull \\hbox")]
    rep.add("FAIL" if overfull else "PASS", "overfull boxes", f"{len(overfull)}" + (f", first: {overfull[0][:100]}" if overfull else ""))
    if "Label(s) may have changed" in text:
        rep.add("WARN", "labels", "LaTeX asks for another run")


def check_pdf(pdf: Path, rep: Report, max_pages: int):
    if not pdf.exists():
        rep.add("FAIL", "PDF", "not produced")
        return
    try:
        import pymupdf
    except ImportError:
        import fitz as pymupdf
    doc = pymupdf.open(pdf)
    rep.add("FAIL" if len(doc) > max_pages else "PASS", "page count", f"{len(doc)} of at most {max_pages}")
    bad = [i + 1 for i, p in enumerate(doc) if abs(p.rect.width - LETTER[0]) > 0.5 or abs(p.rect.height - LETTER[1]) > 0.5]
    rep.add("FAIL" if bad else "PASS", "US letter pages", f"pages off size: {bad}" if bad else "all 612 x 792 pt")
    not_embedded, type3 = set(), set()
    for page in doc:
        for xref, ext, ftype, basefont, *_ in page.get_fonts(full=True):
            if ext == "n/a":
                not_embedded.add(basefont)
            if ftype == "Type3":
                type3.add(basefont)
    rep.add("FAIL" if not_embedded else "PASS", "fonts embedded", ", ".join(sorted(not_embedded)) or "all")
    rep.add("WARN" if type3 else "PASS", "no Type 3 fonts", ", ".join(sorted(type3)) or "none")


def check_source(src: Path, rep: Report, stage: str, max_refs: int, allow: list[str]):
    files = input_files(src)
    if not files:
        rep.add("FAIL", "main.tex", "missing")
        return
    full = {f: strip_comments(f.read_text()) for f in files}
    joined = "\n".join(full.values())
    body = joined.split("\\begin{document}", 1)[-1]
    hard = "FAIL" if stage == "submission" else "WARN"

    rep.add("PASS" if "\\documentclass[conference]{IEEEtran}" in joined else "FAIL", "template class", "\\documentclass[conference]{IEEEtran}")

    hits = [f"{f.name}: {pat}" for f, t in full.items() for pat in LAYOUT_COMMANDS if re.search(pat, t)]
    rep.add("FAIL" if hits else "PASS", "no layout changes", "; ".join(hits) or "none")

    left = [p for p in TEMPLATE_PHRASES if p in joined]
    rep.add(hard if left else "PASS", "template text removed", "; ".join(left) or "none")
    held = {p: joined.count(p) for p in PLACEHOLDERS if p in joined}
    rep.add(hard if held else "PASS", "placeholders", ", ".join(f"'{p}' x{n}" for p, n in held.items()) or "none")
    # Template, "email address or ORCID" for each author; call: "include all authors' information".
    # Authors are counted by their ORCID links in the name blocks; one shared affiliation block may carry one email.
    names = " ".join(re.findall(r"\\IEEEauthorblockN\{(.*?)\}\s*\\IEEEauthorblockA", body, flags=re.S))
    ids = re.findall(r"\\orcidlink\{([^}]*)\}", names)
    if ids:
        real = sum(1 for i in ids if i != "0000-0000-0000-0000")
        emails = len(re.findall(r"[\w.+-]+@[\w-]+\.[\w.]+", " ".join(re.findall(r"\\IEEEauthorblockA\{(.*?)\}\s*(?:\\and|\})", body, flags=re.S))))
        short = len(ids) - real - emails
        rep.add(hard if short > 0 else "PASS", "author email or ORCID",
                f"{len(ids)} authors: {real} ORCID iDs, {emails} email(s); {short} without either" if short > 0 else f"{len(ids)} authors covered")

    m = re.search(r"\\title\{", body)
    title = braced(body, m.end() - 1) if m else ""
    # "\\" alone only balances title lines (HOWTO); the template's banned subtitle is "\\{\footnotesize ...}"
    bad_title = [s for s in ("$", "\\footnote{") if s in title]
    if re.search(r"\\\\\s*\{?\\(footnotesize|small|scriptsize)", title):
        bad_title.append("subtitle")
    rep.add("FAIL" if bad_title else "PASS", "title has no math, footnotes or subtitle", ", ".join(bad_title) or (title.strip()[:80] or "no title"))
    am = re.search(r"\\begin\{abstract\}(.*?)\\end\{abstract\}", body, flags=re.S)
    if am:
        bad_abs = [s for s in ("$", "\\footnote", "\\thanks") if s in am.group(1)]
        rep.add("FAIL" if bad_abs else "PASS", "abstract has no math or footnotes", ", ".join(bad_abs) or "clean")
    else:
        rep.add(hard, "abstract", "not written yet")
    km = re.search(r"\\begin\{IEEEkeywords\}(.*?)\\end\{IEEEkeywords\}", body, flags=re.S)
    if km:
        rep.add("FAIL" if "$" in km.group(1) else "PASS", "keywords have no math")
    else:
        rep.add(hard, "keywords", "not written yet")

    dashes = [f"{f.name}:{n}" for f, t in full.items() for n, line in enumerate(t.splitlines(), 1) if "---" in line or "\u2014" in line]
    rep.add("FAIL" if dashes else "PASS", "no em dashes", ", ".join(dashes) or "none")

    style = {
        "eqnarray": (r"\\begin\{eqnarray", "FAIL"), "'Eq.' before a reference": (r"\bEq\.\s*~?\\(eq)?ref", "FAIL"),
        "'Figure~\\ref' (template: 'Fig.~\\ref')": (r"\bFigure~?\s*\\ref", "FAIL"),
        "'Ref.' before a citation": (r"\bRefs?\.\s*~?\\cite", "FAIL"), "'Acknowledgement' spelling": (r"Acknowledgement", "FAIL"),
        "'et. al'": (r"\bet\.\s*al", "FAIL"), "decimal without a leading zero": (r"(?<![\w.])\.\d", "FAIL"),
        "'essentially' (template: not for 'approximately')": (r"\bessentially\b", "WARN"),
    }
    bodies = {f: t.split("\\begin{document}", 1)[-1] for f, t in full.items()}
    for name, (pat, level) in style.items():
        found = [f"{f.name}:{n}" for f, t in bodies.items()
                 for n, line in enumerate(t.splitlines(), 1) if re.search(pat, line)]
        rep.add(level if found else "PASS", name, ", ".join(found) or "none")

    typed = []
    for f, t in full.items():
        if "/ASSETS/" in f.as_posix():
            continue  # generated tables and macros
        text = t.split("\\begin{document}", 1)[-1] if "\\begin{document}" in t else t
        # inside math, subscripts and superscripts are notation (indices, dimensions), not numbers to
        # trace; drop them and still scan the rest, so a result typed inside math is still caught
        def _strip_scripts(m):
            return re.sub(r"[_^](\{[^{}]*\}|\\?[A-Za-z0-9])", " ", m.group(0))
        text = re.sub(r"\\begin\{(equation|align)\*?\}.*?\\end\{\1\*?\}", _strip_scripts, text, flags=re.S)
        text = re.sub(r"(?<!\\)\$[^$]*\$", _strip_scripts, text)
        for n, line in enumerate(text.splitlines(), 1):
            clean = re.sub(r"\\(cite|ref|eqref|label|input|include|includegraphics|bibliography|bibliographystyle|IEEEtriggeratref|begin|end|orcidlink|href|url)\*?(\[[^\]]*\])?\{[^}]*\}", " ", line)
            clean = re.sub(r"\\[A-Za-z]+", " ", clean)
            for a in NAMES_WITH_DIGITS + allow:
                clean = re.sub(a, " ", clean)
            for m in re.finditer(r"\d[\d.,]*", clean):
                typed.append(f"{f.name}:{n} '{m.group(0)}'")
    rep.add("FAIL" if typed else "PASS", "no hand-typed numbers", "; ".join(typed[:12]) + (" ..." if len(typed) > 12 else "") if typed else "none")

    bbl = src / "main.bbl"
    if bbl.exists():
        n = bbl.read_text(errors="replace").count("\\bibitem")
        rep.add("FAIL" if n > max_refs else "PASS", "reference count", f"{n} of at most {max_refs}")

    if "\\section*{Acknowledgment}" not in body:
        rep.add(hard, "Acknowledgment with the AI-use disclosure", "not written yet")


def main():
    ap = argparse.ArgumentParser(description="Build and check the paper against the venue rules.")
    ap.add_argument("--src", required=True, type=Path, help="Overleaf clone holding main.tex")
    ap.add_argument("--work", required=True, type=Path, help="scratch folder for the build (wiped)")
    ap.add_argument("--stage", choices=["draft", "submission"], default="draft")
    ap.add_argument("--max-pages", type=int, default=4)
    ap.add_argument("--max-refs", type=int, default=30, help="CONTEXT.md: no more than about 30; the plan's budget is 22")
    ap.add_argument("--allow", action="append", default=[], help="regex removed before the hand-typed number check, e.g. 'Wi-Fi 6'")
    ap.add_argument("--texmf", type=Path, help="folder of extra TeX packages for the local build")
    args = ap.parse_args()
    pdf, log = build(args.src.resolve(), args.work.resolve(), args.texmf.resolve() if args.texmf else None)
    rep = Report()
    check_log(log, rep, args.stage)
    check_pdf(pdf, rep, args.max_pages)
    check_source(args.work.resolve(), rep, args.stage, args.max_refs, args.allow)
    raise SystemExit(1 if rep.show() else 0)


if __name__ == "__main__":
    main()
