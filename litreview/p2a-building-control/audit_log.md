# Audit log (p2a-building-control)

Audit run by the finishing agent, 2026-11-14 between 22:27Z and 22:32Z UTC.

## Method
1. **Automated anchor check, all 142 original rows.** A script normalised whitespace, Unicode quotes and line-break hyphenation in every saved `sources/P*.txt`. It then tested whether each row's anchor occurs in the text of that row's pid. Result: all 142 anchors were found, and none is longer than 12 words. The same check was re-run after the edits and new rows below: all 159 found.
2. **Manual check of support.** For the rows below, I printed about 250 to 500 characters of the source around the anchor, and sometimes grepped the whole source. I then judged whether the source actually supports the statement. This covers 63 rows across 31 of the 45 original sources.

## Rows checked manually

| eid | pid | result | change |
|---|---|---|---|
| E003 | P001 | PASS: sigma_teacher = 0.5, fixed | none |
| E004 | P001 | PARTIAL: the anchor supports the prompt role and state text. "No occupant input" is an absence claim. A grep of the full text finds "occupant" only in comfort contexts, never as a prompt input | statement reworded to say the paper describes no occupant input |
| E006 | P001 | PASS: Eq. (4), w_e = 0.25, six lower nodes | none |
| E008 | P001 | PASS: AirflowNetwork, 12 nodes, setpoints and fan speeds, 30-min timestep (lines 229-230) | none |
| E010 | P001 | PASS | none |
| E016 | P001 | PASS: Conclusion, "sensitivity to inappropriate teacher guidance" | none |
| E021 | P002 | PASS: an author claim, labelled as a claim | none |
| E023 | P002 | PASS: 0.52 vs 0.77 | none |
| E028 | P003 | PASS: listing abstract | none |
| E029 | P003 | PASS: "up to 27x fewer environment interactions than standard SAC" | none |
| E030 | P003 | PASS | none |
| E033 | P004 | PASS: Eq. (3)-(4) | none |
| E037 | P004 | PASS: Sec. 5.3 | none |
| E039 | P004 | PASS | none |
| E040 | P004 | PASS: Potential Risks paragraph | none |
| E041 | P004 | PASS: Table 1 caption (3 seeds). "Without VLM guidance on held-out environment seeds" confirmed at line 125 | none |
| E044 | P005 | PASS: Highlights | none |
| E048 | P005 | PASS: 47.9%, about 7.5 weeks, human-in-the-loop | none |
| E049 | P005 | PASS: Sec. 4.4.4 | none |
| E050 | P005 | PASS: the context is control-oriented combinations | none |
| E051 | P005 | PASS: Sec. 4.5.2 | none |
| E052 | P005 | PASS: level 3 example is "comfort setpoints; occupancy flags" | none |
| E053 | P005 | PASS | none |
| E054 | P005 | PASS | none |
| E055 | P005 | PASS: Table 4 row; also Sec. 6.2 text | none |
| E056 | P005 | PASS: FM1-FM6 headings confirmed (lines 2711-2768) | none |
| E057 | P005 | PASS | none |
| E060 | P006 | PASS: arXiv abstract | none |
| E062 | P007 | PASS: 7.30% PPD, 140.90 kWh | none |
| E064 | P008 | PASS: items (1)-(5) | none |
| E065 | P008 | PASS: the source reads "from 3 to +3" (the minus sign was lost in extraction); "3 being cold" confirms -3 | none |
| E067 | P008 | PASS | none |
| E071 | P008 | PASS: 47.92% / 34.97% / 26.36% / 25.93% | none |
| E073 | P008 | PASS | none |
| E075 | P009 | PASS | none |
| E080 | P011 | PASS: 86% device control | none |
| E082 | P011 | PASS | none |
| E086 | P012 | PASS: actuators HTG-SETP-SCH and CLG-SETP-SCH | none |
| E090 | P012 | PASS: "Separate temperature comfort ranges are defined for summer and winter" plus the LinearReward default | none |
| E093 | P012 | PASS: counted 14 weather files in the saved Weathers table | none |
| E094 | P013 | PASS | none |
| E096 | P014 | PASS: "REST API, and Model Context Protocol server" | none |
| E099 | P015 | PASS | none |
| E102 | P018 | PASS: slide text | none |
| E107 | P019 | FAIL (provenance): the anchor and the negative claim ("no occupant feedback channel was seen") come from the WebFetch tool's own paraphrase ("I did not see..."), not from publisher text. Crossref has no abstract for this DOI (S057) | negative claim removed; statement limited to camera-based occupant-state inference feeding MPC; anchor changed to a phrase in the saved summary; locator marked as tool paraphrase |
| E108 | P019 | PASS on string, weak provenance (tool paraphrase) | locator marked "tool paraphrase; not publisher text"; listed in unverified.md |
| E109 | P020 | PASS: meta-policy over RL portfolio, JSON prompts, 5.1% | none |
| E111 | P021 | PASS | none |
| E113 | P021 | PASS | none |
| E115 | P022 | PASS: coping behaviours exhausted, level-crossing, relation to PPD discussed | none |
| E116 | P023 | PASS | none |
| E117 | P024 | PASS | none |
| E118 | P025 | PASS, incomplete: the source also states that the actual dissatisfaction ratio was 100% | statement extended with the 100% figure |
| E119 | P026 | PASS: "not separated" | none (mean values added as new row E154) |
| E120 | P027 | PASS | none |
| E126 | P035 | PASS | none |
| E127 | P036 | PASS | none |
| E128 | P037 | PASS | none |
| E130 | P039 | PASS: smartphone hot/cold votes, 12 offices, 60%, 0.3 C | none |
| E131 | P040 | FAIL (partial): "for 2-10 occupants" does not appear in the saved abstract excerpt (it is truncated with "[...]") | "2-10 occupants" deleted; statement marked as from an abstract excerpt |
| E132 | P029 | PASS: eight LLMs, 250 adversarial tests, smart building is one of five domains | none |
| E139 | P042 | PASS | none |
| E141 | P005 | PASS | none |

Summary: 59 PASS without change, 2 PASS with the statement reworded or extended (E004, E118), 1 PASS with the locator marked as weak provenance (E108), 2 FAIL corrected (E107, E131). No rows were deleted.

## Other ledger changes
- `sources/index.csv`, P022 venue: Consensus listed "Science and Technology for the Built Environment", but the doi.org/Crossref metadata in `refs.bib` gives *HVAC&R Research* 6(4):289-305 (2000). The index now gives the Crossref value and notes the Consensus label. Also recorded in `unverified.md`.
- New rows E143-E159 were added for new sources P046-P051 and for additional facts from already-saved sources (P005, P012, P026). Their anchors were checked by the same script; all found.
