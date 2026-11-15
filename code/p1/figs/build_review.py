"""Build the review page (HTML) that shows every figure and table of paper 1 for the PI's approval.

    python -m p1.figs.build_review --figs results/figures --out <dir> [--notes notes.json]

Figures are referenced as files next to the page (img/*.png); tables are generated here from
the result CSVs, never typed. ``notes.json`` holds, per figure, what it shows, the defects found and
fixed before showing it, and the limits of the checks (FIGURE_TASTE v1 section 6).
"""
from __future__ import annotations

import argparse
import html
import json
import shutil
from pathlib import Path

import numpy as np
import pandas as pd

from . import figstyle as S
from .figdata import Results

CSS = """
:root {
  /* Layout: one reading column of figure plates, each followed by its notes; tables scroll inside their own box. */
  --bg: #f7f8fa; --plate: #ffffff; --fg: #15181d; --muted: #586070; --rule: #d9dde4; --accent: #2a78d6;
  --good: #0b7a3b; --chip: #eef3fb;
  --display: "Newsreader", "Iowan Old Style", Georgia, serif;
  --body: "Inter", system-ui, -apple-system, "Segoe UI", sans-serif;
  --mono: "JetBrains Mono", ui-monospace, "SFMono-Regular", Menlo, monospace;
}
@media (prefers-color-scheme: dark) { :root:not([data-theme="light"]) {
  --bg: #111418; --plate: #ffffff; --fg: #e7eaef; --muted: #a3abb8; --rule: #2c323b; --accent: #6aa7ee;
  --good: #4cc27f; --chip: #1c2633; color-scheme: dark } }
:root[data-theme="dark"] {
  --bg: #111418; --plate: #ffffff; --fg: #e7eaef; --muted: #a3abb8; --rule: #2c323b; --accent: #6aa7ee;
  --good: #4cc27f; --chip: #1c2633; color-scheme: dark }
body { background: var(--bg); color: var(--fg); font-family: var(--body); line-height: 1.55; }
.wrap { max-width: 1180px; margin: 0 auto; padding-left: max(16px, env(safe-area-inset-left, 0px));
  padding-right: max(16px, env(safe-area-inset-right, 0px)); padding-block: 28px 64px; }
h1, h2, h3 { font-family: var(--display); font-weight: 600; text-wrap: balance; line-height: 1.2; }
h1 { font-size: clamp(1.9rem, 3.4vw, 2.6rem); margin: 0 0 6px; }
h2 { font-size: 1.55rem; margin: 44px 0 6px; border-top: 1px solid var(--rule); padding-top: 22px; }
h3 { font-size: 1.2rem; margin: 0 0 8px; }
p, li { max-width: 72ch; }
.lede { color: var(--muted); margin: 0 0 18px; }
.eyebrow { font-size: .74rem; letter-spacing: .08em; text-transform: uppercase; color: var(--muted); }
.status { display: flex; flex-wrap: wrap; gap: 8px; margin: 14px 0 6px; }
.chip { background: var(--chip); border-radius: 999px; padding: 3px 11px; font-size: .82rem; }
.chip b { font-variant-numeric: tabular-nums; }
.fig { display: grid; gap: 14px; margin: 22px 0 34px; }
.plate { background: var(--plate); border: 1px solid var(--rule); border-radius: 6px; padding: 10px; }
.plate img { display: block; width: 100%; height: auto; }
.notes { display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 12px 24px; }
.notes > div { min-width: 0; }
.notes h4 { margin: 0 0 4px; font-size: .78rem; letter-spacing: .07em; text-transform: uppercase; color: var(--muted); }
.notes ul { margin: 0; padding-left: 18px; }
.verdict { border-left: 3px solid var(--accent); padding: 4px 0 4px 12px; }
.tablebox { overflow-x: auto; border: 1px solid var(--rule); border-radius: 6px; margin: 10px 0 24px; }
table { border-collapse: collapse; font-size: .86rem; font-variant-numeric: tabular-nums; width: 100%; }
th, td { padding: 6px 10px; border-bottom: 1px solid var(--rule); text-align: right; white-space: nowrap; }
th:first-child, td:first-child { text-align: left; }
thead th { font-weight: 600; background: var(--chip); position: sticky; top: 0; }
td.best { font-weight: 700; color: var(--good); }
code { font-family: var(--mono); font-size: .85em; }
.small { font-size: .84rem; color: var(--muted); }
a { color: var(--accent); }
"""


def table_html(df: pd.DataFrame, best_cols: dict | None = None, fmt: dict | None = None) -> str:
    fmt = fmt or {}
    best_cols = best_cols or {}
    head = "".join(f"<th>{html.escape(str(c))}</th>" for c in df.columns)
    rows = []
    for _, r in df.iterrows():
        cells = []
        for c in df.columns:
            v = r[c]
            s = fmt[c](v) if c in fmt and pd.notna(v) else ("" if pd.isna(v) else str(v))
            cls = ' class="best"' if c in best_cols and pd.notna(v) and v == best_cols[c] else ""
            cells.append(f"<td{cls}>{html.escape(s)}</td>")
        rows.append("<tr>" + "".join(cells) + "</tr>")
    return f'<div class="tablebox"><table><thead><tr>{head}</tr></thead><tbody>{"".join(rows)}</tbody></table></div>'


def fig_block(name: str, img_dir: Path, figs: Path, note: dict) -> str:
    src = figs / "preview_hi" / f"{name}.png"
    if not src.exists():
        src = figs / f"{name}.png"
    if not src.exists():
        return f'<p class="small">({name}: not rendered yet)</p>'
    shutil.copyfile(src, img_dir / f"{name}.png")

    def ul(items):
        return "<ul>" + "".join(f"<li>{html.escape(i)}</li>" for i in items) + "</ul>"

    return f"""
<section class="fig" id="{name}">
  <div><span class="eyebrow">{html.escape(note.get('slot', ''))}</span><h3>{html.escape(note.get('title', name))}</h3></div>
  <div class="plate"><img src="img/{name}.png" alt="{html.escape(note.get('alt', note.get('title', name)))}" loading="lazy"></div>
  <div class="notes">
    <div><h4>What it shows</h4>{ul(note.get('shows', []))}</div>
    <div><h4>Defects found and fixed before showing</h4>{ul(note.get('fixed', []))}</div>
    <div><h4>Limits of my checks</h4>{ul(note.get('limits', []))}</div>
  </div>
  {f'<p class="verdict">{html.escape(note["verdict"])}</p>' if note.get('verdict') else ''}
  <p class="small">Files: <code>{name}.pdf</code> (vector, embedded fonts), <code>{name}.png</code> (900 dpi at print size){', standalone panels in <code>panels/</code>' if note.get('panels') else ''}. Source data: {html.escape(note.get('source', ''))}</p>
</section>"""


def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument("--figs", required=True)
    p.add_argument("--out", required=True)
    p.add_argument("--notes", default=None)
    p.add_argument("--e1"), p.add_argument("--e2"), p.add_argument("--e3")
    p.add_argument("--status", default="{}")
    a = p.parse_args(argv)
    figs, out = Path(a.figs), Path(a.out)
    img = out / "img"
    if out.exists():
        shutil.rmtree(out)
    img.mkdir(parents=True)
    notes = json.loads(Path(a.notes).read_text()) if a.notes else {}
    status = json.loads(a.status)
    R = Results(a.e1, a.e2, a.e3)
    P = []
    add = P.append
    add('<title>PERCOM Figure Review</title>\n<meta name="claude:viewport-fit-sides" content="cover">')
    add('<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>')
    add('<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600&family=JetBrains+Mono&family=Newsreader:opsz,wght@6..72,600&display=swap">')
    add(f"<style>{CSS}</style>")
    add('<div class="wrap">')
    add('<span class="eyebrow">Paper 1 · IEEE PerCom WiP, 4 pages · figures and tables for review</span>')
    add("<h1>Tabular foundation models as Wi-Fi fingerprint localizers</h1>")
    add('<p class="lede">Every figure and table below is generated from the result files of briefs P1-E01, P1-E02 '
        'and P1-E03, drawn to the FIGURE_TASTE v1 and v2 standard at twice the printed size of an IEEE two-column page '
        '(text width 7.16 in, column 3.5 in). The first section is the set I recommend for the 4 pages; the second holds '
        'the candidates and supplement material for you to choose from.</p>')
    if status:
        add('<div class="status">' + "".join(f'<span class="chip">{html.escape(k)}: <b>{html.escape(str(v))}</b></span>'
                                             for k, v in status.items()) + "</div>")

    sections = [("Recommended for the 4 pages", [n for n, v in notes.items() if v.get("group") == "paper"]),
                ("Candidates and supplement", [n for n, v in notes.items() if v.get("group") != "paper"])]
    for title, names in sections:
        add(f"<h2>{html.escape(title)}</h2>")
        for n in names:
            add(fig_block(n, img, figs, notes[n]))

    # ---- tables generated from the CSVs
    add("<h2>Tables</h2>")
    e1 = R.e1_summary()
    if len(e1):
        g = e1.groupby(["model", "config"])["mean"].agg(["mean", "std", "count"]).reset_index()
        piv = g.pivot(index="model", columns="config", values="mean").reindex([m for m in S.ORDER if m in set(g["model"])])
        sd = g.pivot(index="model", columns="config", values="std").reindex(piv.index)
        df = pd.DataFrame({"Model": [S.MODEL[m]["label"].replace("$-$", "−") for m in piv.index]})
        best = {}
        for c in [c for c in ["CETC331", "HCXY-All", "HCXY-AP", "SYL-All", "SYL-AP"] if c in piv.columns]:
            col = S.CONFIG_LABEL[c]
            df[col] = piv[c].to_numpy()
            df[col + " ±sd"] = sd[c].to_numpy()
            best[col] = np.nanmin(piv[c].to_numpy())
        add("<h3>Table I data: mean positioning error on the full survey (m), mean and standard deviation over seeds</h3>")
        add(table_html(df, best_cols=best, fmt={c: (lambda v: f"{v:.3f}") for c in df.columns if c != "Model"}))
    cr = R.e2_crossing()
    if len(cr):
        show = cr[["config", "model", "knn_100_mean_m", "crossing_share_pct", "crossing_ref_points"]].copy()
        show.columns = ["Config", "Model", "Tuned kNN, full survey (m)", "Share needed to match it (%)", "Reference points"]
        add("<h3>Survey effort: smallest share of reference points at which each foundation model matches tuned kNN on the full survey</h3>")
        add(table_html(show, fmt={"Tuned kNN, full survey (m)": lambda v: f"{v:.3f}"}))
    A = R.a_uncertainty()
    if len(A):
        g = A.groupby("model")[["cover50_both", "cover80_E", "cover80_N", "cover80_both", "width80_m",
                                "spearman_spread80_error"]].mean().reindex([m for m in S.ORDER if m in set(A["model"])])
        g.insert(0, "Model", [S.MODEL[m]["label"].replace("$-$", "−") for m in g.index])
        add("<h3>Uncertainty: coverage of central predictive intervals, mean over configurations and seeds</h3>")
        add(table_html(g.reset_index(drop=True), fmt={c: (lambda v: f"{v:.3f}") for c in g.columns if c != "Model"}))
    C = R.c_seeds()
    if len(C):
        g = C.groupby(["config", "model"])["mean"].agg(["count", "mean", "std", "min", "max"]).reset_index()
        g["model"] = g["model"].map(lambda m: S.MODEL[m]["label"].replace("$-$", "−"))
        g.columns = ["Config", "Model", "Seeds", "Mean (m)", "Std (m)", "Min (m)", "Max (m)"]
        add("<h3>Twenty seeds of the foundation models on the full survey</h3>")
        add(table_html(g, fmt={c: (lambda v: f"{v:.3f}") for c in ["Mean (m)", "Std (m)", "Min (m)", "Max (m)"]}))
    E = R.e_phone_user()
    if len(E):
        g = E.groupby(["config", "group", "id", "model"])["mean_error_m"].mean().unstack("model")
        g = g[[m for m in S.ORDER if m in g.columns]]
        g.columns = [S.MODEL[m]["label"].replace("$-$", "−") for m in g.columns]
        g = g.reset_index().rename(columns={"config": "Config", "group": "By", "id": "Id"})
        add("<h3>Mean error by phone and by user of the test rows (m)</h3>")
        add(table_html(g, fmt={c: (lambda v: f"{v:.2f}") for c in g.columns if c not in ("Config", "By", "Id")}))
    add('<p class="small">Every number on this page is read from the result files in the repository branches '
        '<code>exp/P1-E01</code>, <code>exp/P1-E02</code> and <code>exp/P1-E03</code>; none is typed by hand.</p>')
    add("</div>")
    (out / "index.html").write_text("\n".join(P))
    print(f"  review page: {out / 'index.html'} with {len(list(img.glob('*.png')))} images")


if __name__ == "__main__":
    main()
