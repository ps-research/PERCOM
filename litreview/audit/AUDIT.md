# Audit of the literature reviews

Audited on 2026-11-14 (UTC) by the planning session. Scripts are in this folder; each can be re-run.

| Review | Folder | Status |
|---|---|---|
| Paper 1: tabular foundation models for Wi-Fi fingerprint localization | `p1-tabular-localization/` | audited, passes |
| Paper 2, language side: user pressure and LLM yielding | `p2b-llm-pressure/` | audited, passes |
| Paper 2, control side: LLM-guided RL and building control | `p2a-building-control/` | review being written; not yet audited |

## What was checked

| Check | How | Paper 1 | Paper 2 language side |
|---|---|---|---|
| Every quoted phrase is in the saved source | `check_anchors.py`: normalised string match of each anchor against the saved file of that source | 159 of 159 | 164 of 164 (3 are table rows, found with layout-preserving extraction) |
| Saved files are the files recorded | SHA-256 of each file against `sources/index.csv` | 39 of 39 | 48 of 48 |
| Every tag in the review points to a ledger row | tag scan of `review.md` | 143 rows used, none missing | 145 rows used, none missing |
| Cited papers exist as described | `recheck_arxiv.py`: fresh arXiv API fetch, title and first author compared | 16 of 16 | 46 of 46 |
| Cited DOIs resolve to the same title | `recheck_doi.py`: Crossref, DataCite as fallback | 22 of 22 | 5 of 5 |
| The claim follows from the passage | passage around the anchor read by the auditor (`show_context.py`) for the rows the conclusions rest on | 27 rows, all supported | 22 rows, all supported |
| Arithmetic stated as "our arithmetic" | recomputed | Locaris Table III reconstruction correct; split sums 21,205 / 2,720 correct | not applicable |

Rows read against their passage:

- Paper 1: E007, E023, E028, E041, E042, E043, E051, E052, E053, E055, E064, E065, E066, E067, E074, E083, E088, E090, E093, E095, E109, E111, E112, E126, E127, E128, E150.
- Paper 2 language side: E003, E004, E007, E008, E016, E021, E031, E034, E039, E079, E080, E089, E092, E097, E126, E130, E142, E153, E156, E159, E162, E164.

## What the audit does not cover

- The other 274 ledger rows were checked for the quote only, not read in context.
- Completeness of the searches. The gaps are listed in each `unverified.md`.
- 56 of the 87 sources were read at abstract level only (22 in Paper 1, 34 in Paper 2 language side). The reviews mark them.

## Changes made during the audit

- `unverified.md` was missing in both folders. Both were compiled from the reviews, the search logs and the ledgers; no new literature was added.
- Nothing in `review.md`, `evidence.csv`, `sources/` or `refs.bib` was changed.

## Not in the repository

The saved source files (PDFs, HTML, text) are kept outside the repository because many are publisher copies. `sources/index.csv` records the URL, fetch time and SHA-256 of each one.
