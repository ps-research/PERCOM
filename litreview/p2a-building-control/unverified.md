# Unverified items, access failures and conflicts (p2a-building-control)

## A. Sources we could not read in full, and what the review limits itself to

| pid / item | Access | What failed | What the review says about it |
|---|---|---|---|
| P003 Miyake et al., "From LLM Control to Environment-Adaptive Agents..." (NeurIPS 2026 workshop, OpenReview 4uChurOKJx) | ABSTRACT (neurips.cc listing) | OpenReview PDF/API returned HTTP 403 bot challenge (S007, not bypassed). The forum URL was not on the WebFetch allowlist (S008). No arXiv preprint exists (S006, S011) | Only the listing abstract: handoff, critic-based filtering, 27x, 15-day real room. Unknown: the filter rule, any injected teacher errors, occupant inputs, energy results in the real room |
| P045 Lyu, Lai, Zhang et al., "LLM-Powered Agent for Occupant-Centric Indoor Environment Control: Design, Implementation, and Evaluation" (SSRN 6136668) | LISTING | SSRN fetch failed (S031); no other copy found (S032) | Nothing beyond the title. Ranked as a medium, unknown-content novelty threat |
| P044 Sawada et al., "Office-in-the-Loop for Building HVAC Control with Multimodal Foundation Models" (BuildSys 2024, 10.1145/3671127.3698182) | LISTING (Crossref metadata) | Not fetched; the DCE 2025 journal version (P008) was used instead | No content claims |
| P043 Sinergym BuildSys 2021 paper (10.1145/3486611.3488729) | LISTING (Crossref) | Paper not fetched; the online docs (P012) were used for every Sinergym fact | Facts come from the docs only |
| P019 Qi et al. 2026, Advances in Applied Energy 23:100283 | ABSTRACT, weak | Direct curl returned 403. Only a WebFetch tool summary was saved (S030). Crossref has no abstract (S057) | E107/E108 are labelled as tool paraphrase. The earlier negative claim ("no occupant feedback channel") was removed in the audit |
| P018 Sasaki et al. BuildSys 2025 CPSIS | ABSTRACT (presentation slides, not the paper) | The dblp record was blocked by a proof-of-work challenge (S028). The paper PDF was not found | Claims are limited to slide content |
| P021-P040 (Consensus records) | ABSTRACT | Consensus free tier returns no DOI; some abstracts are truncated excerpts (P040 contains "[...]") | Claims are limited to the returned text. P040's "2-10 occupants" was removed in the audit |

## B. Leads seen but not checked (titles only; say nothing about content)
- Sun et al., "preference-conditioned reinforcement learning", residential HVAC, Energy 2026: not found (S033).
- A 2026 *Renewable and Sustainable Energy Reviews* review on LLMs and human-centric thermal comfort: not found (S045).
- Lee et al., "LLM-Driven Generative Agents for Simulating Occupant Feedback in Built Environments": not found. The candidate at energy-proceedings.org was a different paper (S026, S027, S046).
- JARVIS (Lee et al. 2026, IMWUT), noted in S039; the arXiv 2507.04748 entry (S054) shows it is an HVAC question-answering framework. Not saved and not cited.
- ThermoLLM arXiv 2606.22911 (S024), arXiv 2606.28011 and 2601.20005 (S009), and arXiv 2609.02719 eco-feedback (S022): title-level only, not checked.
- arXiv 2311.00772, a smart-home agent called "SAGE" (S020): title only. **Name clash** with P004 SAGE (Selective Agent Guidance via Entropy); the two are unrelated works.
- Group-comfort papers dropped for budget in S043 (Laftchiev, Zhang review, Yu MARL, etc.), and overcooling/demand-response papers in S036.
- Imperfect-teacher papers dropped in S055 (NAC 2018, AC-Teach 2019, Jing 2020, Kessler Faulkner 2020/2021).

## C. Facts not confirmed from a primary source
- P006 ELLM venue: the index says ICML 2023 "per Miyake ref [8]". The arXiv record saved does not confirm the venue. The review cites no venue for it.
- P002 LLM4Teach: arXiv year 2023 vs IJCAI 2024. The venue comes from the arXiv comment only (E026); the IJCAI proceedings page was not fetched.
- P004 SAGE "EMNLP 2026 Findings" comes from the arXiv journal_ref (E042) and the Consensus listing; the ACL Anthology was not fetched.
- P014 BuildOcc and P041 Korus-Du et al.: journal info from arXiv journal_ref only.
- PMV/PPD and ASHRAE 55 / ISO 7730 standard texts were not accessed. All PMV statements rest on P027/P028 abstracts.
- Sinergym:
  - The docs saved are the moving "main" branch (fetched 2026-11-14), not a pinned release.
  - Only four pages were saved (Environments, Buildings, Rewards, Weathers). They do not mention PMV/PPD outputs or comfort meters, but other pages (wrappers, output variables) were not checked. "Sinergym does not expose PMV" is therefore **not** established.
  - Miyake et al.'s two-storey AirflowNetwork office is not among the buildings on the saved Buildings page. Whether it is a custom model or ships in another Sinergym version is unverified.
- The Evil-AI Benchmark smart-building scenarios: the abstract does not say whether any concern HVAC setpoints or report energy.

## D. Conflicts between sources
- **P022 venue.** Consensus lists "Science and Technology for the Built Environment". doi.org/Crossref gives *HVAC&R Research* 6(4):289-305, 2000. The index was corrected to Crossref (see `audit_log.md`). The likely explanation is a later journal renaming, but this was not verified.
- **Office-in-the-Loop duration and saving.** P005 reports 47.9% and "approximately 7.5 weeks" over two periods [P005:E048]. P008 reports 47.92% and "about 1.5 months" in two periods [P008:E069][P008:E071]. These are consistent within rounding; the review quotes P008.
- **P002 year** (2023 arXiv vs IJCAI 2024): see C.
- **P008 extracted text** drops minus signs ("from 3 to +3"). The surrounding words ("3 being cold") confirm the scale is -3..+3.

## E. Process notes
- Bot challenges (OpenReview, dblp) and the SSRN failure were not bypassed.
- One Consensus call hit a rate limit (S037, S041) and was retried after waiting.
- Extra full-text reads used while finishing: 1 of 6 (P046 TGRL).
