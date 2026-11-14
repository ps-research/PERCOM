# Search log (p2a-building-control)

## S001
- time_utc: 2026-11-14T21:44:23Z
- tool: local file read
- query: `/home/claude/percom-wip/papers/01-hvac-rl-llm-policy-teacher/text/full_blocks.md`
- results: 1
- kept: Miyake et al. PerCom WiP 2026 (P001; IEEE copy supplied locally)
- dropped: n/a

## S002
- time_utc: 2026-11-14T21:44:23Z
- tool: local file read
- query: `/home/claude/percom-wip/notes/percom-wip-2026-reading-notes.md`
- results: 1
- kept: used only as leads (not cited as evidence)
- dropped: n/a

## S003
- time_utc: 2026-11-14T21:44:23Z
- tool: local file read
- query: `/home/claude/pilots/lit/idea2_arxiv.json (10 earlier arXiv API queries; 4 of them sycophancy/injection/phrasing x HVAC/smart-home returned 0)`
- results: 44
- kept: leads: 2603.26050, 2609.05314, 2403.16809, 2605.28168, 2609.01567, LATS
- dropped: remaining ~38 are LLM distillation/reasoning papers unrelated to control or teachers in RL

## S004
- time_utc: 2026-11-14T21:44:58Z
- tool: arXiv API
- query: `id_list=2311.13373,2302.06692,2609.01567,2603.26050,2605.28168,2403.16809,2308.03028,2609.05314,2512.25055`
- results: 9
- kept: all 9 (metadata+abstract for leads)
- dropped: none

## S005
- time_utc: 2026-11-14T21:44:58Z
- tool: WebFetch
- query: `https://neurips.cc/virtual/2026/160099`
- results: 1
- kept: Tokyo follow-up listing (title, 7 authors, workshop, abstract summary, OpenReview id 4uChurOKJx)
- dropped: n/a

## S006
- time_utc: 2026-11-14T21:44:58Z
- tool: arXiv API
- query: `search_query=all:"environment-adaptive" AND all:HVAC`
- results: 0
- kept: none
- dropped: no preprint on arXiv

## S007
- time_utc: 2026-11-14T21:44:58Z
- tool: curl
- query: `https://openreview.net/pdf?id=4uChurOKJx ; https://api2.openreview.net/notes?id=4uChurOKJx`
- results: 0
- kept: none
- dropped: HTTP 403 'Challenge verification required' (bot challenge); not bypassed

## S008
- time_utc: 2026-11-14T21:44:58Z
- tool: WebFetch
- query: `https://openreview.net/forum?id=4uChurOKJx`
- results: 0
- kept: none
- dropped: URL not on session allowlist

## S009
- time_utc: 2026-11-14T21:44:58Z
- tool: WebSearch
- query: `"From LLM Control to Environment-Adaptive Agents" HVAC`
- results: 10
- kept: only the NeurIPS listing matches
- dropped: others are different papers (2312.11701, 2606.28011, 2601.20005, 2603.26050 etc.); 2606.28011 and 2601.20005 noted as possible leads

## S010
- time_utc: 2026-11-14T21:45:41Z
- tool: WebSearch
- query: `"LLM-to-agent handoff" HVAC critic-based filtering real-room deployment`
- results: 10
- kept: Office-in-the-Loop DCE PDF (cambridge.org S2632673625100105a); 2609.05314
- dropped: no preprint of the Tokyo follow-up; others duplicates or unrelated (2507.04748, osaka-u page)

## S011
- time_utc: 2026-11-14T21:45:41Z
- tool: arXiv API
- query: `search_query=au:"Miyake T" AND all:HVAC ; search_query=all:HVAC AND all:LLM AND all:handoff`
- results: 0
- kept: none
- dropped: 0 results each; Tokyo follow-up has no arXiv preprint

## S012
- time_utc: 2026-11-14T21:48:23Z
- tool: curl (Cambridge Core OA PDF)
- query: `https://resolve.cambridge.org/core/services/aop-cambridge-core/content/view/B6CE619AC4EBC5EB1E917F55835B4692/S2632673625100105a.pdf/...`
- results: 1
- kept: Sawada et al. 2025 DCE Office-in-the-Loop (P008, CC BY-NC-SA)
- dropped: n/a

## S013
- time_utc: 2026-11-14T21:48:23Z
- tool: curl (arXiv PDF)
- query: `https://arxiv.org/pdf/2403.16809 ; 2308.03028 ; 2512.25055`
- results: 3
- kept: P009, P010, P011
- dropped: n/a

## S014
- time_utc: 2026-11-14T21:49:00Z
- tool: curl
- query: `https://ugr-sail.github.io/sinergym/compilation/main/pages/{environments,buildings,rewards,weathers}.html`
- results: 4
- kept: Sinergym docs (main branch; tags up to v3.12.0) saved as P012
- dropped: n/a

## S015
- time_utc: 2026-11-14T21:50:12Z
- tool: arXiv API
- query: `(all:LLM OR all:"language model") AND (all:HVAC OR all:thermostat OR all:"building control") AND (all:sycophancy OR all:sycophantic OR all:"over-compliance" OR all:persuasion OR all:persuasive)`
- results: 0
- kept: none
- dropped: zero results (negative search for Q1)

## S016
- time_utc: 2026-11-14T21:50:12Z
- tool: arXiv API
- query: `(all:LLM OR all:"language model") AND (all:HVAC OR all:thermostat OR all:"thermal comfort") AND (all:phrasing OR all:wording OR all:tone OR all:politeness OR all:emotional OR all:insistent OR all:urgency)`
- results: 0
- kept: none
- dropped: zero results (negative search for Q1)

## S017
- time_utc: 2026-11-14T21:50:12Z
- tool: arXiv API
- query: `(all:"smart home" OR all:"home automation" OR all:"smart building") AND (all:"prompt injection" OR all:jailbreak)`
- results: 2
- kept: PromptShield Home 2608.05495; Promptware attacks 2508.12175
- dropped: none dropped

## S018
- time_utc: 2026-11-14T21:50:12Z
- tool: arXiv API
- query: `(all:LLM OR all:"language model") AND all:thermostat`
- results: 3
- kept: none
- dropped: 2111.13654 (model beliefs), 2405.03821 (small LMs in devices, no setpoint-phrasing study per title), 2510.12091 (polymers) off-topic

## S019
- time_utc: 2026-11-14T21:50:12Z
- tool: arXiv API
- query: `(all:LLM OR all:"language model") AND all:"thermal comfort" AND (all:complaint OR all:complaints OR all:request OR all:requests)`
- results: 1
- kept: none
- dropped: 2606.23001 EnerInfer (on-device inference energy) off-topic

## S020
- time_utc: 2026-11-14T21:50:12Z
- tool: arXiv API
- query: `(all:"smart home" OR all:"home assistant") AND (all:LLM OR all:"language model") AND (all:safety OR all:attack OR all:adversarial OR all:manipulation)`
- results: 20
- kept: 2608.05495 (dup); 2311.00772 SAGE smart-home agent (title only, noted)
- dropped: remaining 18 are IoT security/ADL recognition/benchmarks without occupant-request phrasing

## S021
- time_utc: 2026-11-14T21:50:12Z
- tool: arXiv API
- query: `(all:LLM OR all:"language model") AND all:HVAC AND (all:occupant OR all:occupants) AND (all:feedback OR all:preference)`
- results: 1
- kept: 2403.16809 (dup, P009)
- dropped: none

## S022
- time_utc: 2026-11-14T21:50:12Z
- tool: arXiv API
- query: `(all:LLM OR all:"language model") AND (all:occupant OR all:occupants) AND (all:simulate OR all:simulated OR all:"generative agents" OR all:persona)`
- results: 69
- kept: BuildOcc 2609.02729; 2609.02719 eco-feedback (title only)
- dropped: first 25 inspected; rest are persona-bias/occupational-persona LLM papers ('occupational' matched 'occupant' stem) off-topic

## S023
- time_utc: 2026-11-14T21:50:12Z
- tool: arXiv API
- query: `all:sycophancy AND (all:agent OR all:agents) AND (all:control OR all:"tool use" OR all:action)`
- results: 16
- kept: none for this cluster (language-side; left to the other agent)
- dropped: none concerns building, HVAC or smart-home control

## S024
- time_utc: 2026-11-14T21:51:12Z
- tool: WebSearch (extended)
- query: `LLM HVAC controller occupant request wording tone over-compliance energy setpoint`
- results: 9
- kept: Qi et al. AAE S2666792426000223; Lyu et al. SSRN 6136668; ThermoLLM 2606.22911 (title only); CityLearn v2 2405.03848
- dropped: no result studies request wording/tone; others are older MPC, a patent, a substack summary of 2609.05314, and an unrelated RL fine-tuning paper

## S025
- time_utc: 2026-11-14T21:51:12Z
- tool: WebSearch
- query: `Sasaki "LLM-Driven Agent-Based Evaluation Framework for Occupant-Centric HVAC Control" BuildSys 2025`
- results: 10
- kept: dblp conf/buildsys/SasakiTOS25; osaka-u slide PDF; osaka-u post 3087
- dropped: duplicates/Office-in-the-Loop

## S026
- time_utc: 2026-11-14T21:51:12Z
- tool: WebSearch
- query: `"LLM-Driven Generative Agents for Simulating Occupant Feedback in Built Environments"`
- results: 10
- kept: energy-proceedings.org cue2025/1769499305.pdf (candidate)
- dropped: TravelAgent 2412.18985 and generative-occupants project page are different works; 2403.16809 dup

## S027
- time_utc: 2026-11-14T21:51:21Z
- tool: curl
- query: `https://www.energy-proceedings.org/wp-content/uploads/cue2025/1769499305.pdf`
- results: 1
- kept: none
- dropped: it is Li et al. 2025 (LLM code generation for co-simulation), not Lee et al.; not relevant

## S028
- time_utc: 2026-11-14T21:51:43Z
- tool: curl
- query: `https://dblp.org/rec/conf/buildsys/SasakiTOS25.bib`
- results: 0
- kept: none
- dropped: bot-challenge page (Anubis proof-of-work); not bypassed

## S029
- time_utc: 2026-11-14T21:51:43Z
- tool: curl
- query: `https://www.ane.cmc.osaka-u.ac.jp/wp-content/uploads/2026/02/Buildsys_presentation_slide_final.pdf`
- results: 1
- kept: Sasaki et al. BuildSys 2025 CPSIS workshop slides (P018)
- dropped: n/a

## S030
- time_utc: 2026-11-14T21:52:26Z
- tool: curl / Crossref / WebFetch
- query: `https://www.sciencedirect.com/science/article/pii/S2666792426000223 ; api.crossref.org query 'Energy-efficient HVAC control residential ... occupant intention inference multimodal LLMs'`
- results: 3
- kept: Qi et al. 2026 AAE 23:100283, DOI 10.1016/j.adapen.2026.100283 (curl 403; WebFetch returned a tool summary of first 100k chars) -> P019
- dropped: Crossref hits 2-3 (Quintana 2021 cohort PCM; Meimand & Jazizadeh 2024) noted as F-cluster leads

## S031
- time_utc: 2026-11-14T21:52:26Z
- tool: WebFetch
- query: `https://papers.ssrn.com/sol3/papers.cfm?abstract_id=6136668`
- results: 0
- kept: none
- dropped: site client_error; Lyu et al. SSRN 6136668 recorded as LISTING from search snippet only

## S032
- time_utc: 2026-11-14T21:52:40Z
- tool: WebSearch
- query: `Lyu Lai Zhang Lian "LLM-Powered Agent for Occupant-Centric Indoor Environment Control"`
- results: 10
- kept: none
- dropped: no copy of the SSRN paper; results are other LLM/building papers (2410.19262 DAO-twin, PMC12431303 review, NJIT CPS) - not verified

## S033
- time_utc: 2026-11-14T21:52:40Z
- tool: WebSearch
- query: `Sun "preference-conditioned reinforcement learning" residential HVAC control changing preferences Energy 2026`
- results: 10
- kept: none matching Sun et al. Energy 2026
- dropped: results are other residential RL/MPC and personalised-control papers (2510.01475, 2512.09481, VT thesis); Sun et al. left unverified

## S034
- time_utc: 2026-11-14T21:52:40Z
- tool: WebSearch
- query: `KIT LLM-guided reinforcement learning heat pump control Karlsruhe`
- results: 10
- kept: KIT repository 1000193931 (candidate)
- dropped: other KIT records/staff pages not inspected

## S035
- time_utc: 2026-11-14T21:52:50Z
- tool: curl
- query: `https://publikationen.bibliothek.kit.edu/1000193931`
- results: 1
- kept: Demirel et al. 2026 IEEE SusTech, LLM-guided RL for heat pumps (P020, abstract)
- dropped: n/a

## S036
- time_utc: 2026-11-14T21:53:31Z
- tool: Consensus search
- query: `occupant thermal complaints commercial buildings hot and cold calls setpoint changes analysis (page_size 15)`
- results: 15
- kept: Gunay 2018 B&E (setpoint change requests); Federspiel 2000 STBE; Wang 2005 Indoor Air; Kocaman 2021; Parkinson 2021 Sci Rep; Kwon 2022 B&E
- dropped: 1998 duplicate of Federspiel; overcooling/DR/setpoint-raising papers (Marzban, Aghniaey, Alnuaimi, Kiil, Muller, Stopps, Sheikh Khan) relevant background but outside budget

## S037
- time_utc: 2026-11-14T21:53:32Z
- tool: Consensus search
- query: `large language model HVAC control occupant natural language request sycophancy prompt injection over-compliance`
- results: 0
- kept: none
- dropped: rate-limit error; retried later (see next Consensus entry)

## S038
- time_utc: 2026-11-14T21:53:32Z
- tool: Consensus search
- query: `ASHRAE Global Thermal Comfort Database II personal comfort models PMV accuracy (page_size 15)`
- results: 15
- kept: Cheung 2019 B&E (PMV accuracy 34%); Tartarini 2025 B&E (ISO 7730 vs ASHRAE 55 PMV)
- dropped: other PMV-modification and ML-comfort papers not needed for 4 canonical refs

## S039
- time_utc: 2026-11-14T21:55:16Z
- tool: Consensus search
- query: `large language model HVAC thermostat control occupant natural language requests manipulation prompt injection robustness (page_size 15)`
- results: 15
- kept: Evil-AI Benchmark (Varol et al. 2026 IEEE Access); Sasha (King et al. 2024 IMWUT); Zaman et al. 2026 IMNS (home IoT prompt injection); JARVIS (Lee et al. 2026 IMWUT, title/abstract noted)
- dropped: generic prompt-injection papers (SecAlign, Greshake, PromptFuzz, PI review, PromptInject, red-teaming, PromptGuard, referencing defence) are language-security background, not building control; 2603.26050, 2609.05314, 2308.03028 duplicates

## S040
- time_utc: 2026-11-14T21:56:23Z
- tool: Consensus search
- query: `Development of the ASHRAE Global Thermal Comfort Database II; personal comfort models new paradigm occupant-centric control (page_size 10)`
- results: 10
- kept: Foldvary Licina 2018 B&E (DB II); Kim et al. 2018 B&E (personal comfort models); Kim et al. 2017 B&E (PCM from heating/cooling behaviour)
- dropped: Parkinson 2019 adaptive nudging, Quintana 2022 cohort models, ML/BMI correction papers: relevant but not needed for 4-6 canonical refs; Cheung 2019 dup

## S041
- time_utc: 2026-11-14T21:56:23Z
- tool: Consensus search
- query: `shared office thermostat conflicts multiple occupants group thermal comfort preference aggregation fairness HVAC control`
- results: 0
- kept: none
- dropped: rate-limit error; retried below

## S042
- time_utc: 2026-11-14T21:56:23Z
- tool: Consensus search
- query: `BOPTEST ...; CityLearn reinforcement learning environment; review simulation environments reinforcement learning HVAC (page_size 10)`
- results: 10
- kept: Blum et al. 2021 JBPS (BOPTEST); Nweye et al. 2024 JBPS (CityLearn v2); Arroyo et al. 2022 Frontiers (MPC vs RL in BOPTEST)
- dropped: BOPTEST-gym, RL-MPC, Building2Building, BuildingGym, residential RL papers noted but not kept

## S043
- time_utc: 2026-11-14T21:57:12Z
- tool: Consensus search
- query: `shared office thermostat conflicts multiple occupants group thermal comfort preference aggregation HVAC control (page_size 10)`
- results: 10
- kept: Shin et al. 2017 BuildSys (fairness in participatory aggregation); Purdon et al. 2013 LCN-W (hot/cold smartphone votes); Jung & Jazizadeh 2019 B&E (majority-vote vs sensitivity strategies)
- dropped: Laftchiev x2, Zhang review, Ihianle, Topak, Yu MARL, Xu VAV: related group-comfort control, not kept within budget

## S044
- time_utc: 2026-11-14T21:57:29Z
- tool: WebSearch
- query: `"Heating in human-HVAC interaction for smart homes" interdisciplinary overview Building and Environment`
- results: 10
- kept: arXiv 2609.23508 (Korus, Du et al. 2026; strathprints copy)
- dropped: 2609.07936 related design paper, other unrelated

## S045
- time_utc: 2026-11-14T21:57:29Z
- tool: WebSearch
- query: `large language models human-centric thermal comfort review Renewable and Sustainable Energy Reviews 2026`
- results: 10
- kept: none
- dropped: no RSER 2026 LLM thermal-comfort review found; hits are 2609.05314 (dup), PMC narrative review, personalised-comfort AI review (Strathclyde/Cardiff), TCEval - left unverified

## S046
- time_utc: 2026-11-14T21:57:29Z
- tool: WebSearch
- query: `Lee 2026 LLM-driven generative agents simulating occupant feedback built environment thermal comfort votes validation`
- results: 10
- kept: candidate 2512.23217 (checked next)
- dropped: others duplicates or unrelated (land-use MDPI, co-simulation code generation)

## S047
- time_utc: 2026-11-14T21:57:57Z
- tool: arXiv API
- query: `id_list=2609.23508 ; id_list=2512.23217`
- results: 2
- kept: P041 Korus-Du et al. 2026 (B&E 115220); P042 TCEval (Li 2025) - not Lee et al. but directly relevant to cluster E
- dropped: n/a

## S048
- time_utc: 2026-11-14T22:04:55Z
- tool: Crossref API
- query: `works/10.1145/3486611.3488729 ; works/10.1017/dce.2025.10010 ; query.bibliographic=Office-in-the-loop ... BuildSys 2024 ; query.bibliographic=Sasha smart home ... IMWUT`
- results: 4
- kept: Sinergym BuildSys 2021 metadata (P043); DCE metadata; BuildSys 2024 Office-in-the-Loop DOI 10.1145/3671127.3698182 (P044); Sasha DOI 10.1145/3643505
- dropped: unrelated second hits (DOE humidity report, IEEE standard)

## S049
- time_utc: 2026-11-14T22:04:55Z
- tool: Crossref API
- query: `title lookups (query.bibliographic, with query.author / year filter on retry) for P021,P022,P024,P027,P028,P029,P032,P033,P035,P036,P037,P038,P039; one 429 rate-limit, retried after 15 s`
- results: 13
- kept: DOIs for all 13 (P032 resolved on third attempt with year filter: 10.1016/j.buildenv.2018.06.022)
- dropped: wrong first matches for P032 (2026 ASHRAE conf paper; 'Global Public Goods') discarded

## S050
- time_utc: 2026-11-14T22:04:55Z
- tool: doi.org content negotiation + arXiv API
- query: `Accept: application/x-bibtex for 20 DOIs; export.arxiv.org id_list for 15 arXiv IDs`
- results: 35
- kept: refs.bib entries
- dropped: none


## S051
- time_utc: 2026-11-14T22:29:20Z
- tool: arXiv API
- query: `(all:LLM OR all:"language model") AND (all:HVAC OR all:thermostat OR all:"building control" OR all:"building energy") AND (all:"prompt injection" OR all:adversarial OR all:jailbreak OR all:manipulation)`
- results: 0
- kept: none
- dropped: zero results (negative search for Q1; added by finishing agent)

## S052
- time_utc: 2026-11-14T22:29:24Z
- tool: arXiv API
- query: `(all:LLM OR all:"language model") AND (all:HVAC OR all:thermostat OR all:"smart home" OR all:"building") AND (all:sycophancy OR all:"over-compliance" OR all:overcompliance OR all:"user pressure" OR all:insistence)`
- results: 29
- kept: none
- dropped: all 29 are general LLM sycophancy/trust papers; 'building' matched phrases like 'Building Trust'; none concerns HVAC, thermostat or smart-home control (language side belongs to the other agent)

## S053
- time_utc: 2026-11-14T22:29:30Z
- tool: WebSearch
- query: `LLM HVAC agent occupant chat requests sycophancy OR over-compliance OR "prompt injection" thermostat setpoint`
- results: 10
- kept: arXiv 2602.15219 (HEMA, checked in S054)
- dropped: 2609.05314 and 2608.05495 duplicates; Office-in-the-Loop mirror duplicate; 2507.04748 JARVIS is HVAC question answering, not control; 2602.16140 is a human-subject BEMS advice study, not control; none studies request wording or over-compliance

## S054
- time_utc: 2026-11-14T22:29:36Z
- tool: arXiv API
- query: `id_list=2602.15219,2602.16140,2507.04748`
- results: 3
- kept: P051 HEMA (Jung 2026, SoftwareX) - conversational multi-agent control + LLM-simulated-user evaluation
- dropped: 2602.16140 (energy-saving advice role-play, no control); 2507.04748 (QA only)

## S055
- time_utc: 2026-11-14T22:29:59Z
- tool: Consensus search
- query: `reinforcement learning from imperfect or suboptimal teacher advice: detecting, down-weighting or unlearning bad guidance (page_size 15)`
- results: 15
- kept: TGRL (Shenfeld 2023) -> P046; TS2C (Xue 2023) -> P047; Soft Action Priors (Centa 2023) -> P048; Adaptive Expert Guidance (Affinita 2026) -> P049; CANDERE-COACH (Li 2024) -> P050
- dropped: SAGE duplicate (P004); NAC 2018, Jing 2020, AC-Teach 2019, Kessler Faulkner 2020/2021, Explainable Action Advising, Zhan 2016, offline OPD 2026, SocraticPO: related but either demonstrations-from-data, human-feedback robotics or LLM-reasoning distillation; five kept cover the mechanisms (dynamic weight, value-gated intervention, per-state usefulness, learnable share, noise filtering)

## S056
- time_utc: 2026-11-14T22:30:07Z
- tool: arXiv API + curl (arXiv PDF)
- query: `search_query=ti:"TGRL" AND ti:"Teacher Guided Reinforcement Learning"` then `https://arxiv.org/pdf/2307.03186`
- results: 1
- kept: P046 full text (full-text read 1 of 6 allowed)
- dropped: n/a

## S057
- time_utc: 2026-11-14T22:29:51Z
- tool: Crossref API
- query: `works/10.1016/j.adapen.2026.100283`
- results: 1
- kept: none (metadata only; no abstract deposited)
- dropped: P019 remains supported only by a WebFetch tool summary

## S058
- time_utc: 2026-11-14T22:31:21Z
- tool: doi.org content negotiation + Crossref API
- query: `Accept: application/x-bibtex for 10.1016/j.softx.2026.102633 ; works?query.bibliographic=Soft Action Priors: Towards Robust Policy Transfer ; Accept: application/x-bibtex for 10.1609/aaai.v37i6.25850`
- results: 3
- kept: BibTeX for P051 and P048 (DOI 10.1609/aaai.v37i6.25850)
- dropped: Crossref second hit (unrelated Neural ODE paper)

## S059
- time_utc: 2026-11-14T22:31:40Z
- tool: local grep over saved full texts
- query: `sycophan|manipulat|persua|tone|wording|phrasing` in P005, P007, P008, P009, P011
- results: 2 hits
- kept: P005 FM4 'coherent, persuasive' (about LLM explanations, not occupant requests) -> E159
- dropped: P008 hit is a reference title (robotic manipulation); no full text studies the phrasing of occupant requests
