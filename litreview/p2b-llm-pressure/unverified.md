# Unverified and unresolved items — Paper 2, language side (user pressure, phrasing and LLM yielding)

Compiled on 2026-11-14 by the planning session during the audit, because the review agent stopped before it wrote this file. Everything below is taken from `review.md` (§0, §2, §6), `search_log.md` and `evidence.csv`. No new literature was added.

## A. Papers that need a full-text read before we claim novelty

1. **P045, "Conduct Under Pressure" (arXiv 2609.25447).** A user insists, begs, flatters or grieves; one scene type is a plan that costs the user money; 60 models [P045:E153]. Abstract only.
2. **P046, SyPS (arXiv 2608.23837, Findings of EMNLP 2026).** Paired prompt variants with the situation held fixed, and a phrasing-sensitivity score [P046:E156][P046:E162]. Abstract only. It is the closest metric design.
3. **P039, Meincke et al., PNAS 2026.** Read only through the authors' lab summary page [P039:E142]. Check the numbers against the PNAS text before quoting.

## B. Lead not found

4. **"Does Sycophancy Change Decisions?"** (given in the brief as a CHI 2026 lead). No exact-title hit (S028). Not cited anywhere in the review.

## C. Withdrawn

5. **arXiv 2608.21377** surfaced in S032 and is marked withdrawn on arXiv. Not used.

## D. Licences and availability of stimulus sets

6. **GitHub-hosted resources.** GitHub was not reachable (S041), so no licence was checked for: SYCON-Bench [P004:E050], the PAP taxonomy [P008:E075], the Conduct Under Pressure scenes [P045:E155].
7. **P002 (Yang et al.) pressure templates.** The paper says they are in its supplementary material [P002:E014]. Whether that material is public, and under what licence, is unknown.
8. **SPINE (P003).** Code and data are promised "upon publication" [P003:E028]; not released.
9. **Social Sycophancy Scale (P036).** Supplement on OSF per the arXiv comment [P036:E161]; licence not checked.
10. **Only confirmed licence:** PLUM, CC BY 4.0 [P013:E103]. It covers politeness only.

## E. Tools not used

11. Consensus was not used for this review. Searches ran on the arXiv API, WebSearch, Crossref and doi.org. One arXiv call hit HTTP 429 (S044) and was repeated as S045.

## F. Sources read at abstract level only (34 of 48)

P015 to P048. Statements tagged to these rest on the arXiv abstract, an ACL Anthology abstract page (P016) or a lab summary page (P039). Read the full text before quoting a number from any of them.

## G. Conflicts in the literature (real disagreements, not errors)

12. **Does emotional phrasing matter?** P002 says no beyond repetition, in a randomised content-fixed design [P002:E004]. P003 says emotional appeals show the highest drop rate, in an observational design [P003:E020][P003:E021]. Both statements were confirmed in the PDFs.
13. **Does expressed certainty matter?** Yes in free-text advice, no in forced choice, within the same paper [P001:E031][P001:E039].
14. **Does claimed authority matter?** Little in P002 and P007; more in P037, P008 and P039.
