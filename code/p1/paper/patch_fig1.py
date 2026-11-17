"""Fig. 1 for the paper: the designer's full-width overview with one label changed.

The designer's file (fig1_overview_fullwidth_v2.png, Illustrator export at text width, 602 dpi) labels
the arrow out of the foundation model "one forward pass". Each coordinate has its own model and both
libraries average several passes by default, so the label becomes "forward passes only" (PI ruling,
D-060). At 8 pt it is wider than the gap between the two boxes, so it is set on two lines in
TeX Gyre Termes (Times metrics) at 8 pt, centred where the old label was, on its baseline.

    python3 code/p1/paper/patch_fig1.py --out <overleaf clone>/ASSETS/IMAGES/fig1_overview.png
"""
from __future__ import annotations

import argparse
import hashlib
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[3]
SRC = ROOT / "paper1/figures/fig1_overview/fig1_overview_fullwidth_v2.png"
SRC_SHA = "9e3eb08627ed"
FONT = "/usr/share/texmf/fonts/opentype/public/tex-gyre/texgyretermes-regular.otf"
DPI = 4300 / (516 / 72.27)          # the image spans \textwidth (43pc)
SIZE = 8 / 72.27 * DPI              # 8 pt in pixels
OLD_BOX = (2125, 1040, 2592, 1110)  # the arrow head reaches into this box; only grey text is cleared  # ink of "one forward pass": x 2133-2583, y 1046-1105
INK = (29, 29, 27)                  # the figure's text colour
LINES = ("forward", "passes only")


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--out", required=True, type=Path)
    args = ap.parse_args()
    raw = SRC.read_bytes()
    if hashlib.sha256(raw).hexdigest()[:12] != SRC_SHA:
        raise SystemExit(f"{SRC} is not the designer file this patch was written for")
    im = Image.open(SRC).convert("RGB")
    a = np.array(im).astype(int)
    x0, y0, x1, y1 = OLD_BOX
    region = a[y0 - 12:y1 + 4, x0 - 8:x1 + 8]
    if not (region.mean(axis=2) < 120).any():
        raise SystemExit("old label not found where expected")
    bg = np.array(a[y0 - 10, (x0 + x1) // 2])
    box = a[y0:y1, x0:x1]
    # Grey text pixels (and their anti-aliased edges) are near-neutral; the blue arrow and its head are not.
    grey = (np.abs(box[..., 0] - box[..., 1]) < 25) & (np.abs(box[..., 1] - box[..., 2]) < 25) & (box.mean(axis=2) < 225)
    ink_cols = np.where(grey.any(axis=0))[0]
    cx = x0 + (ink_cols.min() + ink_cols.max()) / 2
    xo = grey[:, :100]                               # "one": no descenders, so its bottom is the baseline
    baseline = y0 + np.where(xo.any(axis=1))[0].max()
    box[grey] = bg
    a[y0:y1, x0:x1] = box
    im = Image.fromarray(a.astype(np.uint8))
    d = ImageDraw.Draw(im)
    f = ImageFont.truetype(FONT, round(SIZE))
    lead = round(10.2 / 72.27 * DPI)                 # the leading of the figure's own two-line labels
    l, t, r, b = (int(round(v)) for v in d.textbbox((cx, baseline - lead), LINES[0], font=f, anchor="ms"))
    if (np.abs(a[t - 6:b + 6, l - 6:r + 6] - bg).sum(axis=2) > 30).any():
        raise SystemExit("the first line would cover something other than background")
    for i, text in enumerate(reversed(LINES)):
        d.text((cx, baseline - i * lead), text, font=f, fill=INK, anchor="ms")
    left = np.array(im).astype(int)[y0:y1, x0:x1]
    bg = tuple(int(v) for v in bg)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    im.save(args.out, dpi=(round(DPI), round(DPI)))
    print(f"wrote {args.out}; label centred at x={cx:.0f}, baseline y={baseline}, {round(SIZE)} px = 8 pt; background {bg}")


if __name__ == "__main__":
    main()
