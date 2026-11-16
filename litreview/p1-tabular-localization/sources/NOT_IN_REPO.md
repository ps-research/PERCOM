# Sources not in the repository

This repository is public. A source file is included only when its licence allows anyone to redistribute it: Creative Commons, or metadata and licence texts. Seven full-text sources do not meet that bar. They are listed below with where to get them. `index.csv` still records the URL, fetch time and SHA-256 of every source, so a local copy can be checked against the one the review used.

| Source | Title | Why it is not here | How to get it |
|---|---|---|---|
| P001 | Locaris, PerCom 2026 WiP version | IEEE copyright | The PI has the PDF. Put it in `data/litreview-sources/` on the compute node |
| P002 | Diffusion transformers for radio fingerprinting, PerCom 2026 WiP | IEEE copyright | As P001 |
| P003 | SODIndoorLoc README and dataset description | The dataset repository has no licence file | Already in the dataset clone at `data/SODIndoorLoc/` |
| P004 | Locaris, long version (arXiv 2510.11926) | arXiv licence allows distribution by arXiv only | `fetch_sources.py` |
| P006 | TabPFN-3 technical report (arXiv 2605.13986) | As P004 | `fetch_sources.py` |
| P008 | TabICL (arXiv 2502.05564) | As P004 | `fetch_sources.py` |
| P014 | RA-LWLM (arXiv 2606.01899) | As P004 | `fetch_sources.py` |

The evidence ledger (`../evidence.csv`) quotes a short anchor phrase and gives the location for every statement drawn from these sources, so the review can be followed without them.

Licences of the full-text sources that are included:

| Source | Licence |
|---|---|
| P005 WiFiGPT (arXiv 2505.15835) | CC BY 4.0 |
| P007 Beyond IID (arXiv 2606.30410) | CC BY 4.0 |
| P009 SODIndoorLoc dataset paper (Satellite Navigation) | CC BY 4.0 |
| P010 IndoorCART (Frontiers in Signal Processing) | CC BY 4.0 |
| P013 TabPFN v2 (Nature) | CC BY 4.0 |
| P023 CR-AP (Scientific Reports) | CC BY-NC-ND 4.0; included unmodified, with a plain-text copy |
| P037 UCI Wireless Indoor Localization page | CC BY 4.0 |

The remaining included files are registry or model-hub metadata, licence texts, and abstracts.
