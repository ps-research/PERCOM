"""Shared style of every PERCOM figure (FIGURE_TASTE v1 and v2).

Every figure script imports this module; no script defines its own colours or type.

Canvas: figures are drawn at twice their printed size and shrink to the IEEE
two-column page (text width 7.16 in, column 3.5 in). PNGs are saved so that they
hold 900 dpi at the printed size; PDFs are vector with embedded fonts.
"""
from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

# ----------------------------------------------------------------------------- page geometry
PRINT_TEXT_W, PRINT_COL_W = 7.16, 3.5          # IEEE two-column, inches
CANVAS = 2.0                                     # drawn at twice the printed size
TWO_COL_W, ONE_COL_W = PRINT_TEXT_W * CANVAS, PRINT_COL_W * CANVAS
PNG_DPI = int(900 / CANVAS)                      # 900 dpi at the printed size
PREVIEW_DPI = 80                                 # thumbnails
REVIEW_DPI = 125                                 # copies shown on the review page

# ----------------------------------------------------------------------------- colour: one hue per model family
# Validated with the dataviz skill's validate_palette.js (light mode, adjacent pairs): all checks pass;
# aqua, yellow and magenta sit below 3:1 on white, so every series also carries a marker and a legend row.
BLUE, ORANGE, AQUA, YELLOW = "#2a78d6", "#eb6834", "#1baf7a", "#eda100"
MAGENTA, GREEN, VIOLET, RED = "#e87ba4", "#008300", "#6250d6", "#e34948"
INK, INK2, GUIDE, PAPER = "#1d1d1b", "#52514e", "#9a9893", "#ffffff"

FAMILY = {"tabpfn": BLUE, "tabicl": ORANGE, "knn": AQUA, "rf": YELLOW, "lgbm": MAGENTA, "svr": GREEN, "mlp": VIOLET,
          "gp": RED}

# Same family = same hue. The way "not detected" is written is the line style and the marker fill:
# native missing value (NaN) = solid line, filled marker; placeholder -105 = dashed line, open marker.
MODEL = {
    "tabpfn-nan": dict(color=BLUE, ls="-", marker="o", filled=True, label="TabPFN v2, NaN"),
    "tabpfn-ph": dict(color=BLUE, ls="--", marker="o", filled=False, label="TabPFN v2, $-$105"),
    "tabicl": dict(color=ORANGE, ls="-", marker="D", filled=True, label="TabICLv2, NaN"),
    "knn": dict(color=AQUA, ls="-", marker="s", filled=True, label="kNN"),
    "rf": dict(color=YELLOW, ls="-", marker="^", filled=True, label="Random forest"),
    "lgbm-nan": dict(color=MAGENTA, ls="-", marker="v", filled=True, label="LightGBM, NaN"),
    "lgbm-ph": dict(color=MAGENTA, ls="--", marker="v", filled=False, label="LightGBM, $-$105"),
    "svr": dict(color=GREEN, ls="-", marker="P", filled=True, label="SVR"),
    "mlp": dict(color=VIOLET, ls="-", marker="X", filled=True, label="MLP"),
    "gp": dict(color=RED, ls="-", marker="h", filled=True, label="Gaussian process"),
}
SHORT = {"tabpfn-nan": "TabPFN NaN", "tabpfn-ph": "TabPFN $-$105", "tabicl": "TabICL NaN", "knn": "kNN", "rf": "RF",
         "lgbm-nan": "LightGBM NaN", "lgbm-ph": "LightGBM $-$105", "svr": "SVR", "mlp": "MLP", "gp": "GP"}
TFMS = ("tabpfn-nan", "tabpfn-ph", "tabicl")
ORDER = ["tabpfn-nan", "tabpfn-ph", "tabicl", "knn", "rf", "lgbm-nan", "lgbm-ph", "svr", "mlp", "gp"]

CONFIG_LABEL = {"CETC331": "CETC331", "HCXY-All": "HCXY (all MACs)", "HCXY-AP": "HCXY (installed APs)",
                "SYL-All": "SYL (all MACs)", "SYL-AP": "SYL (installed APs)"}
CONFIG_SHORT = {"CETC331": "CETC", "HCXY-All": "HCXY", "HCXY-AP": "HCXY-AP", "SYL-All": "SYL", "SYL-AP": "SYL-AP"}
CONFIG_MARKER = {"CETC331": "o", "HCXY-All": "s", "HCXY-AP": "D", "SYL-All": "^", "SYL-AP": "v"}


# ----------------------------------------------------------------------------- type scale (points on the canvas)
class FS:
    tick, label, legend, legend_title, tag, ref = 16.0, 17.5, 13.5, 14.0, 26.0, 13.5

    @classmethod
    def apply(cls, scale: float = 1.0) -> None:
        for k in ("tick", "label", "legend", "legend_title", "tag", "ref"):
            setattr(cls, k, getattr(cls, k) * scale)
        plt.rcParams.update({
            "font.family": "serif", "font.serif": ["TeX Gyre Pagella", "DejaVu Serif"],
            "mathtext.fontset": "custom", "mathtext.rm": "TeX Gyre Pagella", "mathtext.it": "TeX Gyre Pagella:italic",
            "mathtext.bf": "TeX Gyre Pagella:bold", "mathtext.cal": "TeX Gyre Pagella:italic",
            "mathtext.sf": "TeX Gyre Pagella", "mathtext.tt": "TeX Gyre Pagella",
            "font.size": cls.tick, "axes.labelsize": cls.label, "xtick.labelsize": cls.tick, "ytick.labelsize": cls.tick,
            "legend.fontsize": cls.legend, "legend.title_fontsize": cls.legend_title,
            "axes.edgecolor": INK2, "axes.labelcolor": INK, "xtick.color": INK2, "ytick.color": INK2,
            "axes.linewidth": 1.1, "xtick.major.width": 1.1, "ytick.major.width": 1.1,
            "xtick.major.size": 6, "ytick.major.size": 6, "axes.grid": True, "grid.color": "#e6e5e1",
            "grid.linewidth": 0.9, "axes.axisbelow": True, "axes.spines.top": False, "axes.spines.right": False,
            "pdf.fonttype": 42, "ps.fonttype": 42, "figure.dpi": 100, "savefig.dpi": PNG_DPI,
            "savefig.facecolor": PAPER, "figure.facecolor": PAPER, "axes.facecolor": PAPER,
        })


# ----------------------------------------------------------------------------- marks
def mark_kw(model: str, size: float = 9.0, lw: float = 2.6) -> dict:
    """Line and marker style of a model; open markers get an edge in the model colour (never white on white)."""
    st = MODEL[model]
    return dict(color=st["color"], ls=st["ls"], lw=lw, marker=st["marker"], ms=size,
                mfc=st["color"] if st["filled"] else PAPER, mec=st["color"], mew=2.0)


def halo(artist, width: float = 4.0, color: str = PAPER):
    import matplotlib.patheffects as pe

    artist.set_path_effects([pe.Stroke(linewidth=width, foreground=color), pe.Normal()])
    return artist


def handle(model: str, size: float = 11.0) -> Line2D:
    """Full-size legend swatch matching the in-plot line and marker."""
    return Line2D([0], [0], **mark_kw(model, size=size, lw=2.8))


def legend_box(ax, handles, labels, title=None, loc="best", ncol=1, **kw):
    opts = dict(handlelength=2.8, borderpad=0.6, labelspacing=0.45, columnspacing=1.2)
    opts.update(kw)
    lg = ax.legend(handles, labels, title=title, loc=loc, ncol=ncol, frameon=True, fancybox=False,
                   framealpha=0.94, edgecolor="#b9b7b0", **opts)
    lg.get_frame().set_linewidth(1.0)
    if title:
        lg.get_title().set_fontweight("bold")
    return lg


def tag(ax, letter: str, x: float = -0.13, y: float = 1.02) -> None:
    ax.text(x, y, letter, transform=ax.transAxes, fontsize=FS.tag, fontweight="bold", va="bottom", ha="left", color=INK)


def ref_line(ax, y=None, x=None, label=None, color=GUIDE, ls="--", lw=2.2, where="right"):
    """Bold reference guide with a short label in the margin."""
    if y is not None:
        ax.axhline(y, color=color, ls=ls, lw=lw, zorder=1)
        if label:
            ax.annotate(label, xy=(1.0 if where == "right" else 0.0, y), xycoords=("axes fraction", "data"),
                        xytext=(6 if where == "right" else -6, 0), textcoords="offset points",
                        ha="left" if where == "right" else "right", va="center", fontsize=FS.ref, color=INK2)
    if x is not None:
        ax.axvline(x, color=color, ls=ls, lw=lw, zorder=1)
        if label:
            ax.annotate(label, xy=(x, 1.0), xycoords=("data", "axes fraction"), xytext=(0, 4),
                        textcoords="offset points", ha="center", va="bottom", fontsize=FS.ref, color=INK2)


# ----------------------------------------------------------------------------- output
def save(fig, out_dir: Path, name: str, panels: dict | None = None, log=print) -> list[Path]:
    """Delete old outputs, write PDF + 900-dpi PNG + preview PNG, and assert they exist (FIGURE_TASTE II, D2).

    ``panels`` maps a suffix ("a", "b") to an axes; each is also saved standalone.
    """
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    targets = [(out_dir / f"{name}.pdf", {}), (out_dir / f"{name}.png", {"dpi": PNG_DPI}),
               (out_dir / "preview" / f"{name}.png", {"dpi": PREVIEW_DPI}),
               (out_dir / "preview_hi" / f"{name}.png", {"dpi": REVIEW_DPI})]
    for path, _ in targets:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.unlink(missing_ok=True)
    for path, kw in targets:
        fig.savefig(path, bbox_inches="tight", pad_inches=0.06, **kw)
    written = [p for p, _ in targets]
    for suffix, ax in (panels or {}).items():
        fig.canvas.draw()
        bbox = ax.get_tightbbox(fig.canvas.get_renderer()).transformed(fig.dpi_scale_trans.inverted()).padded(0.08)
        for ext, kw in (("pdf", {}), ("png", {"dpi": PNG_DPI})):
            p = out_dir / "panels" / f"{name}{suffix}.{ext}"
            p.parent.mkdir(parents=True, exist_ok=True)
            p.unlink(missing_ok=True)
            fig.savefig(p, bbox_inches=bbox, **kw)
            written.append(p)
    missing = [p for p in written if not p.exists()]
    if missing:
        raise RuntimeError(f"figure outputs missing after save: {missing}")
    log(f"  wrote {name}: {', '.join(p.name for p in written[:2])} + previews" + (f" + {len(written) - 4} panel files" if len(written) > 4 else ""))
    return written
