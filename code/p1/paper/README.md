# code/p1/paper

Tools for drafting paper 1. The manuscript itself lives in the PI's Overleaf project; at the PI's request a copy goes to `paper1/draft/` for a pull request.

| File | What it does |
|---|---|
| `make_numbers.py` | Writes `ASSETS/numbers.tex`: every number in the paper as a macro read from merged results, with its source file, selector and SHA-256 prefix beside it. No number is typed by hand. |
| `check_paper.py` | Builds the paper in a scratch folder (pdflatex, bibtex, pdflatex twice) and checks it against the PerCom 2027 WiP call, the IEEE conference template and the IEEEtran HOWTO: 4 pages, US letter, embedded fonts, no LaTeX errors or overfull boxes, no layout changes, no template text, no math in the title or abstract, no em dashes, no hand-typed numbers, and the template's wording rules. Exit code 1 means a rule failed. |

Run from the repository root:

```
python3 code/p1/paper/make_numbers.py --out <overleaf clone>/ASSETS/numbers.tex
python3 code/p1/paper/check_paper.py --src <overleaf clone> --work <scratch folder> [--texmf <extra TeX packages>] [--stage submission]
```

`check_paper.py` reads the PDF with PyMuPDF. `--texmf` points the local build at TeX Live packages the local install lacks (the template's `algorithmic.sty`, `IEEEtran.bst`); Overleaf has them.

The checker tests the listed rules only. It cannot tell whether a sentence is true or whether a number is the right one for its claim.
