# Audit of the literature reviews

Audited on 2026-11-14 (UTC) by the planning session. Scripts are in this folder; each can be re-run.

| Review | Folder | Status |
|---|---|---|
| Paper 1: tabular foundation models for Wi-Fi fingerprint localization | `p1-tabular-localization/` | audited, passes |
| Paper 2, language side: user pressure and LLM yielding | `p2b-llm-pressure/` | audited, passes |
| Paper 2, control side: LLM-guided RL and building control | `p2a-building-control/` | audited, passes |

## What was checked

| Check | How | Paper 1 | Paper 2 language side | Paper 2 control side |
|---|---|---|---|---|
| Every quoted phrase is in the saved source | `check_anchors.py`: normalised string match of each anchor against the saved file of that source | 159 of 159 | 164 of 164 (3 are table rows, found with layout-preserving extraction) | 159 of 159 |
| Saved files are the files recorded | SHA-256 of each file against `sources/index.csv` | 39 of 39 | 48 of 48 | 51 of 51 |
| Every tag in the review points to a ledger row | tag scan of `review.md` | 143 rows used, none missing | 145 rows used, none missing | 149 rows used, none missing |
| Cited papers exist as described | `recheck_arxiv.py`: fresh arXiv API fetch, title and first author compared | 16 of 16 | 46 of 46 | 17 of 17 (P007: arXiv title abbreviates "LLMs" and "RL"; same paper) |
| Cited DOIs resolve to the same title | `recheck_doi.py`: Crossref, DataCite as fallback | 22 of 22 | 5 of 5 | 8 of 8 |
| Sources with neither a DOI nor an arXiv id in the index | `recheck_titles.py`: Crossref title search; arXiv title search for the rest | none (3 non-paper sources: dataset repository, model-hub metadata) | none | 25 of 25 papers found. Not checkable this way: P003 (conference listing page), P012 (software documentation) |
| The claim follows from the passage | passage around the anchor read by the auditor (`show_context.py`) for the rows the conclusions rest on | 27 rows, all supported | 22 rows, all supported | 25 rows, all supported |
| Arithmetic stated as "our arithmetic" | recomputed | Locaris Table III reconstruction correct; split sums 21,205 / 2,720 correct | not applicable | not applicable |

Rows read against their passage:

- Paper 1: E007, E023, E028, E041, E042, E043, E051, E052, E053, E055, E064, E065, E066, E067, E074, E083, E088, E090, E093, E095, E109, E111, E112, E126, E127, E128, E150.
- Paper 2 language side: E003, E004, E007, E008, E016, E021, E031, E034, E039, E079, E080, E089, E092, E097, E126, E130, E142, E153, E156, E159, E162, E164.
- Paper 2 control side: E002, E013, E016, E028, E029, E030, E037, E039, E040, E050, E055, E057, E065, E068, E071, E086, E092, E113, E114, E120, E132, E133, E139, E143, E145.

The control-side review also carries its own `audit_log.md`: the agent that finished it checked 63 rows by hand, removed two unsupported statements (E107, E131) and reworded two (E004, E118).

## What the audit does not cover

- Of the 482 ledger rows, 74 were read in context by the auditor. The rest were checked for the quote only.
- Completeness of the searches. The gaps are listed in each `unverified.md`.
- 96 of the 138 sources were read at abstract or listing level only (22 in Paper 1, 34 in Paper 2 language side, 40 in Paper 2 control side). The reviews mark them.
- In the control-side review, 20 sources (P021 to P040) rest on abstracts as returned by the Consensus search engine, some of them truncated. Their existence, venue and year were confirmed through Crossref; their abstracts were not compared with the publisher's.

## Changes made during the audit

- `unverified.md` was missing for Paper 1 and for Paper 2 language side. Both were compiled from the reviews, the search logs and the ledgers; no new literature was added.
- Nothing in any `review.md`, `evidence.csv`, `sources/` or `refs.bib` was changed by the auditor.

## Not in the repository

On 2026-11-16 the openly licensed source files of the Paper 1 review were added to the repository (32 sources; each still matches its recorded SHA-256). The seven that may not be redistributed are listed in `p1-tabular-localization/sources/NOT_IN_REPO.md`. The source files of the Paper 2 reviews are not in the repository. `sources/index.csv` records the URL, fetch time and SHA-256 of every source.
