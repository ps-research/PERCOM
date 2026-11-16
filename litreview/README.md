# Literature review

Each review comes with its search log, an index of the sources it relied on, and an evidence ledger that ties every statement to a source and a location in it.

| Folder | Covers | Status |
|---|---|---|
| `p1-tabular-localization/` | Paper 1: tabular foundation models as Wi-Fi fingerprint localizers | audited |
| `p2b-llm-pressure/` | Paper 2 (dropped), language side: how the phrasing of a request changes what an LLM does | audited; kept for reference |
| `p2a-building-control/` | Paper 2 (dropped), control side: LLM-guided RL and LLM building control | audited; kept for reference |
| `audit/` | Audit report and the scripts behind it | |

## Files in each review

| File | What it is |
|---|---|
| `review.md` | The review. Every factual sentence carries a tag `[Pxxx:Eyyy]`. |
| `evidence.csv` | The ledger. One row per statement: source, location in the source, and a short quoted phrase that can be searched for. |
| `sources/index.csv` | One row per source: title, DOI or arXiv id, URL fetched, fetch time, SHA-256, and whether it was read in full or at abstract level. |
| `search_log.md` | Every search that was run, with the exact query and what came back. |
| `refs.bib` | BibTeX built from registry metadata. |
| `unverified.md` | What could not be checked, and where sources disagree. |

For Paper 1, the openly licensed source files are in `p1-tabular-localization/sources/`. The seven that may not be redistributed are listed in `sources/NOT_IN_REPO.md`, and `fetch_sources.py` downloads four of them from arXiv. The source files of the Paper 2 reviews are not in the repository.
