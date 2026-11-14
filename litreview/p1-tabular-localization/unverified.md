# Unverified and unresolved items — Paper 1 (tabular foundation models for Wi-Fi fingerprint localization)

Compiled on 2026-11-14 by the planning session during the audit, because the review agent stopped before it wrote this file. Everything below is taken from `review.md` (§0, §2-C, §2-E, §6), `search_log.md` and `evidence.csv`. No new literature was added.

## A. Gaps in the novelty search (Q1)

1. **Citing-papers search not run.** OpenAlex and Semantic Scholar returned HTTP 429 on every call (S004, S025, S026). We could not list the works that cite the TabPFN papers.
2. **Not searched at all:** Google Scholar, IEEE Xplore search.
3. **Consequence.** "No prior use of a tabular foundation model for fingerprint positioning" is a negative result from arXiv, WebSearch, Consensus and the TabPFN-3 application list only. Word it "to our knowledge" and repeat the searches before submission.

## B. Open questions about the two competitors on SODIndoorLoc

4. **Which AP set did they use?** Neither Locaris nor IndoorCART says whether it used the All sheets or the pre-installed-AP sheets [P004:E023][P010:E053]. The sample counts are the same for both variants, so the counts do not settle it.
5. **IndoorCART's "364 detected APs"** [P010:E053] is not explained. The sheets have 52 / 347 / 363 RSS columns (All) and 52 / 56 / 46 (AP) [P003:E020]. The column counts were re-read from the dataset files during the audit. 364 is one more than the largest sheet; how the three buildings were merged is not stated.
6. **Locaris Table III, KNR and MLPR rows.** They cannot be reproduced from any average of the dataset paper's tables. The KNC, RFC and MLPC rows can: they equal the mean of the dataset paper's two HCXY sheets. That arithmetic was re-done during the audit and is correct.
7. **Metric definitions.** Locaris calls its metric MAE and describes it as average distance error [P004:E026], yet its median (3.88 m) is above its MAE (2.84 m) [P001:E007]. IndoorCART gives no formula [P010:E057]. Both IndoorCART and the dataset paper print RMSE values below MAE [P010:E060][P009:E068]. Published SODIndoorLoc numbers are therefore not comparable across papers.
8. **CR-AP's headline 2.07 m** may be for the HCXY building only [P023:E129].

## C. Conflicts between sources

9. **TabPFN-2.5 size limit.** Its abstract says 50,000 rows and 2,000 features [P038:E148]; the TabPFN-3 report says 100,000 rows [P006:E072].
10. **Wi-Fi RSS-RTT split sizes.** Locaris Table II [P004:E154] and the Zenodo record [P024:E131] give different counts for the lecture theatre and corridor.
11. **Year of P029 (SSD).** Crossref says 2013; Consensus says 2011.

## D. Not checked

12. **Licences on GitHub.** The GitHub API was not available (S018). Not checked: the SODIndoorLoc repository licence, the TabICL / TabICLv2 code licence, the TabPFN v1 licence. TabICL weights are BSD-3-Clause on Hugging Face [P012:E097]; the tag for TabICLv2 weights was not checked.
13. **TabPFN-2.6 and TabPFN-3.5.** Only Hugging Face repositories were found; no technical report was fetched.
14. **Publisher pages blocked.** MDPI (HTTP 403), Elsevier (redirect stub) and IEEE Xplore (empty response) could not be read (S030).

## E. Sources read at abstract level only (22 of 39)

P015, P016, P017, P018, P019, P020, P021, P022, P025, P026, P027, P028, P029, P030, P031, P032, P033, P034, P035, P036, P038, P039.

Statements tagged to these rest on the abstract or the registry record. Read the full text before quoting a number from any of them. P039 (TabICLv2) matters most: it is a candidate model for our experiments.
