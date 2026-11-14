# Literature review: control side of "occupant-request phrasing x LLM HVAC controller / LLM policy teacher"

Folder: `p2a-building-control/`. Every factual sentence about a paper ends with `[Pxxx:Eyyy]`, which points into `evidence.csv` and `sources/index.csv`. Sentences without a tag are my own synthesis or inference and are labelled as such where it matters.

---

## 0. Scope and method

- **Scope.** This review covers the control side only: LLM-guided RL, imperfect teachers, LLMs in HVAC control, occupant-feedback channels, LLM-simulated occupants, comfort ground truth, complaint behaviour, and simulators. The language side (sycophancy, phrasing effects on LLMs) is left to the other agent.
- **Searches.** S001-S059 in `search_log.md`, run on 2026-11-14 between 21:44Z and 22:31Z UTC.
  - S001-S050 were run by the first agent; S051-S059 were added while finishing.
  - Tools: arXiv API, WebSearch, WebFetch, Consensus, Crossref, doi.org, curl, and local file reads.
- **Sources.** 51 in total: 11 FULLTEXT, 37 ABSTRACT, 3 LISTING.
  - One extra full-text read was used out of the 6 allowed (P046).
- **Evidence.** 159 rows (98 from full texts, 61 from abstracts).
  - 63 of them were re-verified by hand against the saved sources; all 159 anchors were verified by script. See `audit_log.md`.
- **Blocked or weak access.** The full text of the Tokyo NeurIPS follow-up (P003) was blocked by an OpenReview bot challenge and was not bypassed (S007, S008). P019 rests on a WebFetch tool summary only. P043, P044 and P045 are LISTING only. See `unverified.md`.

## 1. Positioning

**What is known:**
- LLM-guided RL in HVAC works in simulation:
  - Miyake et al. regularise a SAC actor towards a Gaussian centred on an LLM's action [P001:E001]. This reaches in about 200 steps what SAC needs over 1000 for [P001:E013].
  - Their follow-up adds critic-based filtering that decides when the teacher's guidance stops helping [P003:E028]. It reports a 15-day real-room deployment [P003:E030].
- Both the RL-side work on imperfect teachers and the HVAC work treat teacher error as task-level noise:
  - SAGE explicitly targets imperfect but informative teachers, not systematically misleading ones [P004:E039].
  - SAGE warns that it may distil systematic teacher biases [P004:E040].
- LLM HVAC controllers that read occupant feedback feed it as numbers:
  - Office-in-the-Loop gives per-unit -3..+3 votes in the prompt [P008:E064][P008:E065].
  - Digital-twin RL counts simulated hot/cold votes [P009:E075].
- The critical review of 66 LLM-for-HVAC studies:
  - finds prompt-based control sensitive to prompt formulation [P005:E050];
  - asks for repeatability across prompt variants as an evaluation target [P005:E057];
  - flags prompt injection and input provenance as unaddressed [P005:E055].

**The gap.** No retrieved work varies the *phrasing* of occupant requests while holding their content fixed, and none measures the effect on an LLM controller's setpoints, energy or comfort. No retrieved work asks whether an RL student inherits or unlearns a teacher bias that comes from occupant language. (This rests on the negative searches listed under Q1.)

---

## 2. Clusters

### A. LLM-guided RL in general (LLM as teacher, prior or planner)

**Synthesis.**
- LLM4Teach trains a student RL agent with an RL loss plus a distillation term towards the LLM teacher [P002:E018]. The teacher weight is decayed piecewise and finally cut to zero [P002:E020]. Miyake et al. borrow this annealing idea [P001:E017].
- Other roles for the LLM:
  - goal proposer, rewarding the achievement of LLM-suggested goals (ELLM) [P006:E060];
  - action-mask generator for a value-based RL agent (HVAC) [P007:E061];
  - meta-policy selecting among RL controllers from JSON-formatted states (heat pump) [P020:E109].
- In all of these, the LLM's input is a description of the environment state. None includes human messages [P001:E004][P002:E019][P020:E109].

| pid | paper | what it does | data or simulator | headline result | how our project differs | cite? | access |
|---|---|---|---|---|---|---|---|
| P001 | Miyake et al. 2026 (PerCom WiP) | KL-regularised SAC towards a Gaussian LLM teacher [P001:E001] | EnergyPlus via Sinergym, Tokyo winter and Singapore summer [P001:E008][P001:E010] | Matches SAC's 1000-step level in about 200 steps [P001:E013] | We add occupant messages and vary their phrasing; the teacher becomes a biased channel | must | FULLTEXT |
| P003 | Miyake et al. 2026 (NeurIPS workshop) | LLM-to-agent handoff with critic-based filtering [P003:E027][P003:E028] | EnergyPlus (2 climates) plus a real room [P003:E029][P003:E030] | Up to 27x fewer interactions than SAC [P003:E029] | Their filter targets general teacher error; we test a structured, language-induced bias | must | ABSTRACT |
| P002 | Zhou et al. (LLM4Teach), IJCAI 2024 | RL loss plus distillation towards an uncertainty-aware LLM teacher [P002:E018][P002:E019] | MiniGrid, Habitat [P002:E022] | Student 0.77 vs LLM 0.52 in ColoredDoorKey [P002:E023] | Discrete toy tasks; no humans in the loop | must | FULLTEXT |
| P006 | Du et al. (ELLM) | LLM-suggested goals as exploration reward [P006:E060] | Crafter, Housekeep [P006:E060] | n/a (abstract) | LLM as goal proposer, not action teacher | maybe | ABSTRACT |
| P007 | Zhong et al. 2026 | Fine-tuned LLM produces action masks for masked RL [P007:E061] | Calibrated 7-zone office simulator [P007:E062] | Mean PPD 7.30%, 140.90 kWh/day [P007:E062] | No occupant language; LLM constrains rather than teaches | maybe | FULLTEXT |
| P020 | Demirel et al. 2026 (SusTech) | LLM meta-policy over an RL portfolio, JSON prompts [P020:E109] | Residential heat-pump simulation testbed [P020:E109] | Up to 5.1% higher mean reward [P020:E109] | No occupant input; decoding-hyperparameter sensitivity only [P020:E110] | maybe | ABSTRACT |

### B. Imperfect or unreliable teachers in RL

**Synthesis.** The retrieved mechanisms for coping with a bad teacher fall into five types:

1. **Fixed annealing schedules.** Used by LLM4Teach and Miyake et al. [P002:E020][P001:E002]. TGRL argues a constant weight over-relies on a sub-optimal teacher [P046:E144].
2. **Performance-based adaptive weighting.**
   - TGRL raises or lowers the teacher weight by comparing the main policy with a reward-only auxiliary policy [P046:E143].
   - Adaptive Expert Guidance learns the expert's share of control, which decays to zero [P049:E149].
3. **Value-gated intervention.**
   - TS2C intervenes based on trajectory value estimates [P047:E147].
   - The NeurIPS follow-up uses critic-based filtering [P003:E028].
   - SAGE uses advantage-weighted BC [P004:E034].
4. **Per-state usefulness estimates.** Soft action priors [P048:E148].
5. **Filtering noisy evaluative feedback.** CANDERE-COACH tolerates up to 40% incorrect feedback [P050:E151].

**Evidence on how well these work:**
- SAGE's own ablation finds no consistent benefit of advantage weighting over plain BC [P004:E037].
- Early in training the critic is uninformative, so SAGE's weighting behaves like plain BC [P004:E036].
- In TGRL's tests, teachers of 40-100% success still yielded a 100% student in Tiger Door [P046:E145]. That teacher error is random-like, not a systematic bias.
- LLM4Teach classifies LLM errors as incorrect, inefficient or inconsistent [P002:E024]. It claims the student corrects teacher mistakes through environment feedback [P002:E021].

(Inference) None of these tests a teacher whose bias is correlated with an input feature such as the phrasing of an occupant message. This is the case where a critic trained on a reward that ignores the bias could fail to flag it.

| pid | paper | what it does | data or simulator | headline result | how our project differs | cite? | access |
|---|---|---|---|---|---|---|---|
| P004 | Bonetta et al. (SAGE), EMNLP 2026 Findings | Entropy-gated VLM queries; BC on teacher transitions; advantage weighting [P004:E032][P004:E033][P004:E034] | FrozenLake, EZPoints, CardMaze, ALFWorld, 3 MiniGrid tasks [P004:E041] | AWBC no consistent benefit; random teacher never helps [P004:E037][P004:E038] | They exclude systematically misleading teachers [P004:E039]; we construct one | must | FULLTEXT |
| P046 | Shenfeld et al. (TGRL), ICML 2023 | Adaptive teacher weight via a counterfactual reward-only policy [P046:E143] | Tiger Door, Lava Crossing, Shadow Hand [P046:E145] | 100% student from a 40% teacher (Tiger Door) [P046:E145] | Principled alternative to Miyake's fixed schedule; untested on biased teachers | must | FULLTEXT |
| P047 | Xue et al. (TS2C) 2023 | Value-based teacher intervention [P047:E147] | Continuous control (abstract) | Student surpasses imperfect teacher [P047:E147] | Not LLM; no input-correlated bias | maybe | ABSTRACT |
| P048 | Centa & Preux, AAAI 2023 | Per-state teacher usefulness adapts feedback strength [P048:E148] | Tabular and deep RL (abstract) | More stable than distillation baselines [P048:E148] | Per-state weighting could localise phrasing-triggered states (inference) | maybe | ABSTRACT |
| P049 | Affinita et al. 2026 | Learnable expert share of control [P049:E149] | 34 tasks [P049:E149] | Share decays to zero [P049:E149] | Survey of weighting options [P049:E150] | maybe | ABSTRACT |
| P050 | Li et al. (CANDERE-COACH) 2024 | Noise filter for evaluative feedback [P050:E151] | 3 domains [P050:E151] | Works at 40% wrong feedback [P050:E151] | Binary feedback, not action teacher | no | ABSTRACT |
| P002 | LLM4Teach | Soft instructions; student corrects teacher [P002:E021][P002:E025] | MiniGrid, Habitat | see A | see A | must | FULLTEXT |

### C. LLMs with RL, and LLMs as controllers, for buildings and HVAC

**Synthesis.**
- The review codes 15 control-category papers; 12 are simulation-only and 13 research-only [P005:E047]. No study in the corpus is rated ready-now [P005:E044].
- Direct LLM control:
  - Song et al. control HVAC in the BEAR simulator through a prompt of task description, demonstrations and current observation [P010:E078][P010:E079].
  - Office-in-the-Loop sets real-office setpoints from sensors plus occupant feedback [P008:E063]. It reports 47.92% energy saving with LLMs alone [P008:E071].
- Hybrid LLM-RL work: Miyake et al. [P001:E001], their follow-up [P003:E028], Zhong et al. [P007:E061], Demirel et al. [P020:E109], and OccuReward, which uses Gemini to write SAC reward functions in CityLearn v2 [P013:E094].
- The review states that prompt engineering alone cannot enforce comfort and setpoint constraints [P005:E049].
- Office-in-the-Loop limits the risk with a setpoint range in the prompt, a 10-sample majority vote and human double-checks [P008:E067].

| pid | paper | what it does | data or simulator | headline result | how our project differs | cite? | access |
|---|---|---|---|---|---|---|---|
| P008 | Sawada et al. 2025 (DCE) | GPT-4/4V setpoint control with occupant feedback in prompt [P008:E063][P008:E069] | Real office, 30 workers, about 1.5 months [P008:E069] | 47.92% energy saving, 26.36% comfort gain vs 23 C baseline [P008:E071] | Numeric votes only; no phrasing manipulation; no RL student | must | FULLTEXT |
| P010 | Song et al. 2023 | GPT-4 prompt-based HVAC control [P010:E078] | BEAR [P010:E079] | n/a here | No occupants | maybe | FULLTEXT |
| P013 | Zaregarizi & Yavari 2026 | LLM-generated reward functions for SAC [P013:E094] | CityLearn v2, DB II profiles [P013:E094] | Elderly female profile least satisfied early [P013:E095] | LLM shapes reward offline, not per-step setpoints | maybe | ABSTRACT |
| P007 / P020 / P001 / P003 | see A | | | | | | |

### D. LLM controllers that take occupant feedback

**Synthesis.** Four input formats appear in the retrieved literature:

1. **Numeric per-zone votes in the prompt.** Office-in-the-Loop [P008:E064][P008:E065].
2. **Vote counts in the RL state rather than the prompt.** Yang et al.: "temperature increase/decrease/constant" counts [P009:E075].
3. **Explicit or under-specified natural-language commands to a smart-home or BEMS agent:**
   - "Set the AC to 20 degrees." [P011:E081];
   - under-specified goals such as "make it cozy" in Sasha [P030:E135];
   - unconstrained commands to an on-device thermostat [P017:E101];
   - multi-turn conversation routed to a Control agent in HEMA [P051:E152].
4. **Non-verbal inference.** Camera footage to occupant states for MPC (Qi et al.; tool summary only) [P019:E107].

The review's comfort/occupant category (A5) has seven primary papers, leaning towards advisory and feedback-mining roles [P005:E142]. One cited system routes natural-language comfort requests to regression or RL models but is not yet connected to live sensors [P005:E141].

| pid | paper | how feedback reaches the LLM | prompt format published? | how our project differs | cite? | access |
|---|---|---|---|---|---|---|
| P008 | Office-in-the-Loop (DCE 2025) | Per-unit -3..+3 votes plus temperatures, setpoints, power, outdoor data; past cycles as few-shot demonstrations [P008:E064][P008:E066] | Yes: block list (Sec. 4.1, Fig. 6); preliminary free-text "comfort level is 5 on a scale of 1 to 10" [P008:E068] | We replace votes with free-text requests of controlled phrasing | must | FULLTEXT |
| P009 | Yang et al. 2024 | LLM-simulated vote counts enter the RL state [P009:E075][P009:E076] | Vote categories given | LLM simulates occupants, does not control | must (E) | FULLTEXT |
| P011 | He & Jazizadeh 2025 | Chat commands to a BEMS agent; 120 queries, 86% device-control accuracy [P011:E080][P011:E081] | Example queries (Table 2) | Commands are explicit; vague ones trigger clarification [P011:E082] | maybe | FULLTEXT |
| P051 | Jung 2026 (HEMA) | Multi-turn chat, classifier routes to a Control agent [P051:E152] | Not in abstract | Evaluated with LLM-simulated users [P051:E153] | maybe | ABSTRACT |
| P030 | King et al. (Sasha) | Under-specified smart-home goals [P030:E135] | n/a (abstract) | Not HVAC energy | maybe | ABSTRACT |
| P017 | King et al. (Thoughtful Things) | Unconstrained commands to a lamp and thermostat [P017:E101] | n/a | Small on-device LMs | no | ABSTRACT |
| P019 | Qi et al. 2026 (AAE) | Camera footage, not language [P019:E107] | n/a | Non-verbal | no | ABSTRACT (tool summary) |
| P045 | Lyu et al. (SSRN) | Unknown | Unknown | Unknown; see unverified.md | ? | LISTING |

### E. LLM-simulated occupants as an evaluation tool

**Synthesis.**
- Systems that simulate occupants with LLMs:
  - Yang et al. simulate population groups in a mall, with comfort ranges generated by the LLM [P009:E074][P009:E076]. They report that temperature 0 gives consistent trends [P009:E077].
  - Sasaki et al. couple gpt-4o persona agents with EnergyPlus. The agents output a -3..+3 thermal sensation vote and a movement destination [P018:E102][P018:E103].
  - BuildOcc grounds occupant agents in the American Time Use Survey and exposes REST/MCP interfaces to EnergyPlus or Home Assistant [P014:E096].
  - HEMA uses LLM-simulated users for evaluation [P051:E153].
- Validity concerns:
  - TCEval finds LLM-agent PMV distributions diverge markedly from human data [P042:E139]. Agents perform near-randomly at discrete comfort classification [P042:E140].
  - The review calls digital-occupant assumptions uncalibrated [P005:E051].
  - BuildOcc reports internal consistency only [P014:E097].
  - Sasaki et al. list external validation with real occupants as future work [P018:E105].

| pid | paper | what it does | simulator | headline result | how our project differs | cite? | access |
|---|---|---|---|---|---|---|---|
| P009 | Yang et al. 2024 | LLM persona votes into RL [P009:E074] | Mall HVAC environment | Temperature 0 gives consistency [P009:E077] | Simulated occupants vote numerically; we vary utterance phrasing | must | FULLTEXT |
| P018 | Sasaki et al. 2025 (BuildSys CPSIS slides) | gpt-4o persona agents with EnergyPlus [P018:E102] | 5 rooms, 50 occupants, 10 h [P018:E104] | n/a in slides | Agents give TSV, not requests to an LLM controller | maybe | ABSTRACT (slides) |
| P014 | Jung 2026 (BuildOcc) | ATUS-grounded occupant agents [P014:E096] | EnergyPlus / Home Assistant | Internal consistency [P014:E097] | Possible generator of request content (inference) | maybe | ABSTRACT |
| P042 | Li 2025 (TCEval) | Tests LLM thermal-comfort judgements against databases [P042:E139] | ASHRAE / Chinese DBs | Divergent distributions [P042:E139] | Warns against trusting LLM occupants as ground truth | must | ABSTRACT |
| P051 | HEMA | LLM-as-simulated-user, 23 metrics [P051:E153] | Household data | n/a | Evaluation template | maybe | ABSTRACT |

### F. Thermal comfort ground truth and how simulators expose comfort

**Synthesis.**
- PMV is a weak per-person predictor:
  - On DB II, PMV predicts observed thermal sensation correctly only 34% of the time, with a mean absolute error of one scale unit [P027:E120].
  - Both the ISO 7730 and ASHRAE 55:2023 versions are right about one-third of the time [P028:E121].
- DB II has about 81,846 measurement sets with occupant votes [P032:E123].
- Thermal preference is asymmetric: 68% of "slightly warm" respondents wanted to be cooler [P028:E122].
- Personal comfort models predict individuals rather than averages [P033:E124]. One reached median accuracy 0.73 vs 0.51 for PMV/adaptive models [P034:E125].
- How the simulators and prior work expose comfort:
  - Sinergym's default LinearReward penalises absolute deviation from a comfort temperature range, with separate summer and winter ranges [P012:E090][P012:E091].
  - Miyake et al. likewise use deviation from a 20.0-23.5 C (winter) or 23.0-26.0 C (summer) band [P001:E006][P001:E007].
  - Zhong et al. report PPD [P007:E062].
  - Office-in-the-Loop uses -3..+3 votes "similar to PMV" aggregated by RMS [P008:E065][P008:E070].
- (Not found) The four Sinergym documentation pages saved do not mention PMV/PPD outputs; see `unverified.md`.

| pid | paper | what it does | data | headline result | relevance | cite? | access |
|---|---|---|---|---|---|---|---|
| P027 | Cheung et al. 2019 | PMV accuracy on DB II [P027:E120] | DB II | 34% correct [P027:E120] | Justifies reporting temperature-band and per-person metrics | must | ABSTRACT |
| P028 | Tartarini & Schiavon 2025 | ISO vs ASHRAE PMV [P028:E121] | 49,245 votes [P028:E121] | About 1/3 correct; preference asymmetry [P028:E122] | Asymmetry supports insistent "too cold" vs "too warm" designs (inference) | maybe | ABSTRACT |
| P032 | Földváry Ličina et al. 2018 | DB II description [P032:E123] | 81,846 sets | n/a | Ground-truth distributions for occupant personas | must | ABSTRACT |
| P033 / P034 | Kim et al. 2018 / 2017 | Personal comfort models [P033:E124][P034:E125] | 38-occupant office [P034:E125] | 0.73 vs 0.51 [P034:E125] | Per-occupant truth for multi-occupant setpoints | maybe | ABSTRACT |
| P012 | Sinergym docs | Comfort as range deviation [P012:E091] | n/a | n/a | Our metric baseline | must | FULLTEXT |

### G. Occupant complaint and override behaviour in real buildings

**Synthesis.**
- In four large offices, most setpoint-change requests asked to raise the 22 C default in the cooling season or lower it in the heating season [P021:E112].
- Requests were 24 times more frequent where occupants could override the thermostat [P021:E113].
- Operators made larger setpoint changes in response to complaints than occupants made themselves [P021:E114].
- Occupants complain to facility managers once their coping behaviours are exhausted [P022:E115].
- Unsolicited complaint rates correlate only moderately with questionnaire satisfaction (r_s = -0.31 to -0.36) [P023:E116].
- Complaints occur even when standards are met: 53 complaints, against a PMV-predicted 4% dissatisfied [P025:E118].
- "Hot" and "Cold" complaint temperatures overlap [P026:E119], though their means differ (summer 28.1 vs 25.8 C) [P026:E154].
- Offices are less comfortable for women largely because of overcooling, and discomfort is more often cold than hot [P024:E117].
- Group control:
  - Common aggregation rules (majority, mean, median) can be unfair to some participants [P038:E129].
  - Smartphone hot/cold votes across 12 offices saved up to 60% energy for 0.3 C more average discomfort [P039:E130].
  - Accounting for comfort sensitivity changed setpoints in 86% of simulated cases [P040:E131].
- A review of 541 studies of home heating names "personalization versus negotiation" among its tensions [P041:E137][P041:E138].

| pid | paper | finding | data | relevance to our design | cite? | access |
|---|---|---|---|---|---|---|
| P021 | Gunay et al. 2018 | 24x more requests with overrides; operators over-correct [P021:E113][P021:E114] | 4 office buildings [P021:E111] | Direction and size of real complaint-driven setpoint moves | must | ABSTRACT |
| P022 | Federspiel 2000 | Complaints after coping is exhausted; level-crossing model linked to PPD [P022:E115] | Commercial facility | Complaint frequency as a function of temperature | must | ABSTRACT |
| P023 | Wang et al. 2005 | Complaints track satisfaction only moderately [P023:E116] | Maintenance DB plus surveys | Complaints are a biased sample of discomfort | maybe | ABSTRACT |
| P024 | Parkinson et al. 2021 | Overcooling, gender inequity [P024:E117] | Two US datasets | Who is cold, and therefore who complains (inference) | maybe | ABSTRACT |
| P025 | Kocaman et al. 2021 | Complaints despite compliant temperatures [P025:E118] | Paris office | PMV vs complaints mismatch | maybe | ABSTRACT |
| P026 | Kwon et al. 2022 | Overlapping hot/cold complaint ranges [P026:E119][P026:E154] | Offices | Complaint content is noisy | maybe | ABSTRACT |
| P038 / P039 / P040 | Shin 2017 / Purdon 2013 / Jung 2019 | Group aggregation and fairness [P038:E129][P039:E130][P040:E131] | Offices / simulation | Multi-occupant shared setpoint baselines | maybe | ABSTRACT |
| P041 | Korus-Du et al. 2026 | Heating HHI review [P041:E137] | 541 studies | Negotiation among cohabitants | no | ABSTRACT |

### H. Simulators

**Sinergym.**
- Environment IDs follow `Eplus-<building>-<weather>-<control_type>-<stochastic>-v1` [P012:E083].
- Weather variability adds Ornstein-Uhlenbeck noise to the EPW data each episode [P012:E084].
- The action space must be a continuous Box; discrete versions are made with a wrapper [P012:E085].
- An empty action space hands control to the building's default schedulers [P012:E157].
- Documented buildings:
  - 5Zone: single storey, 463.6 m2, one heating plus one cooling setpoint schedule [P012:E086];
  - OfficeMedium: 3 floors, 4979.6 m2, five zones per floor, one heating/cooling setpoint pair [P012:E088];
  - 2-zone data centre, with setpoints applied to both zones [P012:E158];
  - a small data centre, a warehouse, a shop with van battery, and a 12-floor large office with grid storage [P012:E089].
- Default reward is LinearReward [P012:E090]. Others: ExpReward, HourlyLinearReward, NormalizedLinearReward, EnergyCostLinearReward, MultiZoneReward [P012:E092].
- 14 default weather files, including Tokyo [P012:E093].
- Occupancy:
  - can be changed at runtime through "context" actuators [P012:E155];
  - "people occupant" can be set as a building extra configuration [P012:E156].

**BOPTEST** provides containerised Modelica emulators with baseline control and common KPIs [P035:E126]. In BOPTEST, model-free RL performed poorly with realistic dynamics, and MPC beat RL for an equivalent formulation [P037:E128].

**CityLearn v2** is a multi-agent DER environment with dynamic occupant feedback [P036:E127]. The review notes that RL control, unlike LLM control, already has standardised benchmark environments [P005:E058].

| pid | tool | key facts | relevance | cite? | access |
|---|---|---|---|---|---|
| P012 / P043 | Sinergym docs / BuildSys 2021 paper | See above | Platform of P001 and of our study | must | FULLTEXT (docs) / LISTING (paper) |
| P035 | BOPTEST | KPIs, baseline control [P035:E126] | Alternative benchmark | maybe | ABSTRACT |
| P037 | Arroyo et al. 2022 | MPC beats RL in BOPTEST [P037:E128] | Caveat for RL claims | maybe | ABSTRACT |
| P036 | CityLearn v2 | Occupant feedback, multi-agent [P036:E127] | Used by OccuReward [P013:E094] | maybe | ABSTRACT |

### I. The critical review arXiv 2609.05314 (Neubauer et al.)

**Method.**
- The review codes 66 peer-reviewed studies (2023 to March 2026) [P005:E043].
- The corpus comes from a single Scopus query that excludes preprints [P005:E045].
- One reviewer did the coding [P005:E046].
- Result: none is ready-now, 3 are near-term and 63 research-only [P005:E044].

**Responsibility boundary.**
- Four levels are defined; comfort setpoints are the example for "LLM-autonomous-low-risk" [P005:E052].
- No reviewed paper crosses the boundary autonomously for safety-critical actuation [P005:E053].
- Constraint-enforcing wrappers, fallback controllers and sensor watchdogs appear in no current prototype [P005:E054].
- Prompt injection through operator text is listed as an unaddressed risk [P005:E055].

**Failure modes.** Six are listed:
- FM1 reasoning brittleness; FM2 semantic hallucination; FM3 executable-but-wrong; FM4 unfaithful explanations; FM5 latency; FM6 proprietary dependence [P005:E056].
- FM4 notes explanations can be "coherent, persuasive, and incorrect" [P005:E159].
- Standard metrics do not expose FM1-FM4; the review recommends repeatability across prompt variants and model versions [P005:E057].

**Relevance to us.**
- Our setting sits at the level the review calls LLM-autonomous-low-risk [P005:E052].
- Our phrasing manipulation is a direct instance of the "repeatability across prompt variants" target [P005:E057].
- The review's preprint exclusion [P005:E045] means it does not cover P001's companions on arXiv such as P007 or P009 (inference from its stated method).

---

## Answers to the explicit questions

### Q1. Phrasing, tone or insistence effects; over-compliance, sycophancy, manipulation or injection in LLM building or smart-home control

**Phrasing effects on an LLM building controller: none found.** The supporting searches:

| Search | What it covered | Result |
|---|---|---|
| S015 (arXiv) | LLM x HVAC/thermostat/building control x sycophancy/over-compliance/persuasion | 0 results |
| S016 (arXiv) | LLM x HVAC/thermostat/thermal comfort x phrasing/wording/tone/politeness/emotional/insistent/urgency | 0 results |
| S018, S019, S021 (arXiv) | LLM x thermostat; complaints/requests; occupant feedback | No phrasing study |
| S024 (extended WebSearch) | | No result studies wording or tone |
| S052 (arXiv) | Sycophancy/over-compliance/insistence x HVAC/smart home/building | 29 hits, none about control |
| S053 (WebSearch) | | None |
| S039 (Consensus) | | None |
| S059 (local grep of the five most relevant full texts: P005, P007, P008, P009, P011) | Phrasing, tone, sycophancy | No study of request phrasing; the only hit is P005's FM4 about persuasive explanations [P005:E159] |

Also: S003 reports that four earlier arXiv queries (sycophancy, injection or phrasing x HVAC/smart home) returned 0. These were run before this review and are recorded only as a lead in S003.

**Closest work:**
- The review notes prompt-based control is sensitive to prompt formulation [P005:E050] and calls for repeatability across prompt variants [P005:E057]. It does not measure occupant-phrasing effects.
- Office-in-the-Loop used free-text comfort feedback only in a preliminary test [P008:E068]. Its main study used numeric votes [P008:E065].

**Over-compliance, manipulation and injection in smart environments: yes, but security-framed.**
- Evil-AI Benchmark tests eight LLMs on 250 adversarial scenarios, including persuasion and prompt injection, with smart building as one of five domains [P029:E132].
  - Persuasion under sustained multi-turn pressure is among the most persistent weaknesses [P029:E133].
  - It also measures over-refusal [P029:E134].
- PromptShield Home finds every MLLM configuration over-refuses genuine smart-home commands [P015:E098][P015:E099].
- Promptware attacks reached home-automation control through indirect injection [P016:E100].
- Zaman et al. show post-LLM action gating blocks threats even when the LLM emits unsafe commands [P031:E136].
- The HVAC review lists prompt injection as unaddressed [P005:E055].
- Searches behind this: S017, S020, S039, S051. S051 returned 0 for LLM x HVAC/building x injection/adversarial/manipulation.

**Assessment.** No work measures benign phrasing (tentative, insistent, emotional) with content held fixed, or its effect on setpoints, energy or comfort. None studies propagation into an RL student. Evil-AI's persuasion results are abstract-only and cover adversarial attacks, not legitimate occupant requests; whether they report HVAC energy is not known.

### Q2. Tokyo follow-up, SAGE, and what Miyake et al. leave open

**Tokyo follow-up (NeurIPS 2026 workshop; abstract only, P003):**
- An LLM temporarily guides an environment-adaptive RL agent [P003:E027].
- "Critic-based filtering determines when teacher guidance remains beneficial and when the learned policy should take over" [P003:E028].
- Evaluation:
  - EnergyPlus in two climates, where the agent surpasses the LLM teacher with up to 27x fewer interactions than standard SAC [P003:E029];
  - a real room, where after 15 days of online learning it improves comfort control over rule-based and direct LLM control [P003:E030].
- Presented at the Agentic AI Benchmark and Application for Enterprise Tasks workshop [P003:E031].
- Not knowable from the abstract: the exact filter rule, whether teacher errors were deliberately injected, energy results for the real room, and whether occupant input exists. The full text was blocked (S007, S008).

**SAGE (P004):**
- Queries the teacher only when the learner's normalised entropy exceeds a threshold, and executes the returned action [P004:E032].
- Teacher-guided transitions are excluded from the PPO loss and used for BC; the critic is trained on all transitions [P004:E033].
- Teacher actions are weighted by exp(A/tau) from an environment-reward critic, clipped at 20 [P004:E034].
- Evaluated on seven tasks with 3 seeds, without the VLM at test time [P004:E041].
- Results:
  - Advantage weighting gives no consistent benefit over plain BC, while removing BC collapses performance [P004:E037].
  - A random teacher never improves over PPO and can degrade the policy [P004:E038].
- The authors scope SAGE to imperfect but informative teachers, not systematically misleading ones [P004:E039]. They warn it may distil systematic biases when flawed guidance yields apparently successful trajectories [P004:E040].

**What Miyake et al. leave open:**
- The teacher's sigma is a fixed 0.5 [P001:E003], and alpha follows a fixed schedule ending at 0 after 4000 steps [P001:E002].
- The LLM is queried for every minibatch state [P001:E005].
- The prompt contains only the environmental state [P001:E004].
- A performance drop near 2000 steps is attributed to policy oscillation [P001:E014].
- The authors name sensitivity to inappropriate teacher guidance as an open challenge [P001:E016]. Evaluation is simulation-only [P001:E016].
- (Inference) Because alpha reaches 0 [P001:E002], any teacher bias can only persist through what the actor learned before cut-off and through replay data. Whether it does persist is untested.

### Q3. How do existing systems feed occupant feedback to the LLM?

See the table in cluster D. In brief:

| Format | Systems |
|---|---|
| Structured numeric votes per HVAC unit, in a prompt block, with sensor state and past cycles as demonstrations | Office-in-the-Loop [P008:E064][P008:E065][P008:E066] |
| Vote counts as RL state features | Yang et al. [P009:E075] |
| Explicit chat commands | He & Jazizadeh [P011:E081]; HEMA [P051:E152] |
| Under-specified goals | Sasha [P030:E135] |
| Non-verbal camera inference | Qi et al. [P019:E107] |

- Aggregation across occupants is by RMS in Office-in-the-Loop [P008:E070].
- Controller-side safeguards: a setpoint range in the prompt and 10-sample self-consistency [P008:E067].
- Free-text feedback such as "my comfort level is 5 on a scale of 1 to 10" appears only in a preliminary test [P008:E068].
- No retrieved system passes raw, emotionally phrased occupant messages to the controller and measures the effect.

### Q4. Sinergym environments, multi-occupant suitability, baselines and metrics

**Environments.**
- IDs follow the `Eplus-<building>-<weather>-<control_type>-<stochastic>-v1` pattern [P012:E083].
- Buildings: 5Zone, OfficeMedium, two 2-zone data-centre variants, a 1-zone data centre, Warehouse, ShopWithVanBattery and OfficeGridStorageSmoothing [P012:E086][P012:E088][P012:E089].
- There are 14 default weathers [P012:E093]; optional OU weather noise [P012:E084].
- Miyake et al. used a single zone of a two-storey office with AirflowNetwork and 12 nodes [P001:E008]. This building is not among those on the documented Buildings page [P012:E089] (my comparison; see `unverified.md`).

**Suitability for several occupants sharing one setpoint.** This is my inference from the documented facts:
- 5Zone has five zones controlled by one heating and one cooling setpoint schedule [P012:E086], and exposes a zone occupant count [P012:E087].
- OfficeMedium has 15 zones under one setpoint pair [P012:E088].
- Both therefore impose one shared setpoint on spatially distinct groups.
- Occupancy can be scripted at runtime through context actuators [P012:E155] or configured as "people occupant" [P012:E156].
- MultiZoneReward supports per-zone comfort ranges and lets one setpoint variable serve several zones [P012:E092][P012:E158].
- Miyake's single-zone, 12-node model [P001:E008] would instead let several occupants share a zone with spatial temperature differences.

**Baselines seen in the literature:**

| Study | Baselines |
|---|---|
| Miyake et al. [P001:E009] | SAC from scratch, LLM-only, LLM-SAC, converged SAC |
| Follow-up [P003:E030] | Rule-based and direct LLM control |
| Office-in-the-Loop [P008:E071] | Fixed 23 C setpoint |
| Zhong et al. [P007:E062] | DQN and vanilla LLM |
| BOPTEST [P035:E126] | Embedded baseline control and MPC [P037:E128] |
| Sinergym [P012:E157] | Default schedulers via an empty action space |

**Metrics seen in the literature:**

| Study | Metrics |
|---|---|
| Miyake et al. [P001:E011] | Learning curve (mean reward per episode), cumulative comfort deviation, total power |
| Sinergym default [P012:E091] | Linear reward of power and range deviation |
| Zhong et al. [P007:E062] | PPD and daily kWh |
| Office-in-the-Loop [P008:E070][P008:E071] | Energy-saving % and RMS comfort |
| BOPTEST [P035:E126] | Common KPIs |
| Miyake et al. [P001:E015] | Sample efficiency (steps to reach a level) |

### Q5. Who complains, and how do complaints drive setpoints?

- **Who complains.** Occupants complain once coping options are exhausted [P022:E115].
  - Complaint rates are only a moderate proxy for dissatisfaction [P023:E116].
  - Women are disproportionately uncomfortable from overcooling, and discomfort is more often cold than hot [P024:E117].
  - Complaints occur even when standards and PMV say conditions are acceptable [P025:E118].
  - "Hot" and "Cold" complaint temperature ranges overlap [P026:E119].
- **How complaints drive setpoints.**
  - Most requests push the 22 C default up in summer or down in winter [P021:E112].
  - Operators respond to complaints with larger setpoint changes than occupants make via overrides [P021:E114].
  - Giving occupants override access multiplies request volume by 24 [P021:E113].
  - Complaint frequency can be modelled as level crossings and tied to PPD and service-call cost [P022:E115].
- **Multi-occupant aggregation.** Majority or mean aggregation can be unfair to some occupants [P038:E129]. Sensitivity-aware strategies change setpoints in most simulated cases [P040:E131].

---

## 3. Threats to novelty (ranked)

1. **High: Tokyo follow-up (P003).**
   - Same group and same task. It already addresses unreliable teacher guidance with critic-based filtering [P003:E028] and has real-room results [P003:E030].
   - Full text unseen, so it may include occupant inputs or bias analyses we cannot rule out.
   - *Distinguish by:* a controlled, input-correlated teacher bias (phrasing with content held fixed), and measuring inheritance vs unlearning in the student under their kind of filter.
2. **Medium: Evil-AI Benchmark (P029).**
   - Persuasion under multi-turn pressure in a smart-building domain is a top weakness [P029:E132][P029:E133].
   - *Distinguish by:* benign, legitimate occupant requests rather than attacks; continuous setpoint, energy and comfort outcomes; RL distillation.
3. **Medium: Office-in-the-Loop (P008).**
   - Real deployment of an LLM HVAC controller with occupant feedback in the prompt [P008:E063], with a published prompt structure [P008:E064].
   - *Distinguish by:* free-text, phrasing-manipulated requests rather than -3..+3 votes [P008:E065]; teacher-student propagation.
4. **Medium (unknown content): Lyu et al. SSRN 6136668 (P045).** An "LLM-powered agent for occupant-centric indoor environment control" exists only as a LISTING. It could study occupant language. It must be read before submission.
5. **Low-medium: the critical review (P005).** It explicitly calls for repeatability across prompt variants [P005:E057] and names prompt-formulation sensitivity [P005:E050], so reviewers may consider the phenomenon "known". *Distinguish by:* quantifying the effect and its downstream propagation.
6. **Low: imperfect-teacher RL (P004, P046, P002).**
   - SAGE already warns about systematic bias distillation [P004:E040].
   - *Distinguish by:* being the first to test it with a natural, semantically structured bias, in continuous control.
7. **Low: smart-home injection and over-refusal (P015, P031).** Security of genuine vs injected commands [P015:E098]. This is a different question from compliance with genuine but emotionally phrased requests.

## 4. Numbers we may need to quote

| Number | Exact definition / split | Tag |
|---|---|---|
| ~200 vs >1000 steps | LLM-SAC reaches in about 200 timesteps (about 4 days) the level SAC needs over 1000 for; learning curve = mean reward per one-day episode | [P001:E013][P001:E011] |
| 287,000 steps (~16 years) | Steps for the saturated SAC baseline | [P001:E015] |
| -0.1868 | LLM-only (gpt-5-mini, few-shot) mean reward | [P001:E012][P001:E009] |
| w_e = 0.25 | r = -w_e E - (1-w_e) P; P = sum of deviations from the band over six lower nodes | [P001:E006] |
| Comfort bands | 20.0-23.5 C winter; 23.0-26.0 C summer | [P001:E007] |
| Training/evaluation splits | Tokyo: train Nov-Feb, evaluate Feb 1; Singapore: train Jun-Sep, evaluate Aug 1 | [P001:E010] |
| Alpha schedule | 1.0 to 0.01 linearly over 2000 steps, held to 4000, then 0 | [P001:E002] |
| 27x | Fewer environment interactions than standard SAC, EnergyPlus, two climates ("up to") | [P003:E029] |
| 15 days | Online learning period in the real-room deployment | [P003:E030] |
| 47.92% / 34.97% | Energy-efficiency improvement, LLMs alone / LLMs+MFMs, vs a 23 C baseline (real office) | [P008:E071] |
| 26.36% / 25.93% | Comfort improvement (RMS of feedback) for the same two conditions | [P008:E071][P008:E070] |
| 66 / 0 / 3 / 63 | Review corpus; ready-now / near-term / research-only | [P005:E043][P005:E044] |
| 34% | PMV correct prediction of observed thermal sensation, DB II | [P027:E120] |
| 81,846 | DB II measurement sets | [P032:E123] |
| 24x | Setpoint-change requests with overrides vs complaint-only buildings | [P021:E113] |
| 0.8%-54.0% | Evilness rate across eight LLMs, 250 adversarial tests | [P029:E134] |
| 7.30% PPD / 140.90 kWh/day | Zhong et al., calibrated 7-zone office | [P007:E062] |

## 5. Suggested reference shortlist (four-page paper, 17 entries)

1. **P001** Miyake et al.: the base method we extend.
2. **P003** Miyake et al. NeurIPS workshop: closest prior work; critic-based filtering of teacher guidance.
3. **P002** LLM4Teach: origin of the LLM-policy-teacher loss and annealing.
4. **P004** SAGE: imperfect-teacher distillation; explicitly leaves systematic bias open.
5. **P046** TGRL: principled adaptive teacher weighting (alternative to a fixed schedule).
6. **P005** Neubauer et al. review: prompt sensitivity, the responsibility boundary, the injection gap.
7. **P008** Office-in-the-Loop: real LLM HVAC control with occupant feedback in the prompt.
8. **P007** Zhong et al.: LLM+RL hierarchical HVAC control.
9. **P009** Yang et al.: LLM-simulated occupant votes with RL.
10. **P042** TCEval: limits of LLM-simulated comfort judgements.
11. **P029** Evil-AI Benchmark: persuasion and injection against smart-environment agents.
12. **P043 + P012** Sinergym paper and docs: platform, rewards and buildings.
13. **P021** Gunay et al.: complaint-driven setpoint changes.
14. **P022** Federspiel: complaint mechanism and PPD link.
15. **P027** Cheung et al.: PMV accuracy limits on DB II.
16. **P040** Jung et al.: multi-occupant shared-setpoint strategies.
17. **P024** Parkinson et al.: who is uncomfortable (overcooling, gender).

## 6. Open questions and unverified items

Details are in `unverified.md`. The ones that matter most:
- The P003 full text, including how the critic filter works and whether occupants appear.
- P045 content.
- P019 rests on a tool summary only.
- Whether Sinergym exposes PMV/PPD outputs; the saved docs pages are silent.
- Whether Miyake's AirflowNetwork office ships with Sinergym.
- P044 (BuildSys 2024 Office-in-the-Loop) was not read.
- Evil-AI's smart-building scenarios and metrics beyond the abstract.

## 7. Notes for the PI

- The P003 full text (OpenReview 4uChurOKJx) should be obtained, for example from the authors, before framing. It is the top novelty risk and could not be accessed here.
- SAGE's authors themselves scope out "systematically misleading" teachers [P004:E039] and flag bias distillation as a risk [P004:E040]. Their statement is a direct hook for the student-inheritance question.
- The review's "repeatability across prompt variants" recommendation [P005:E057] is a citable motivation for holding content fixed while varying phrasing.
- Real-building evidence says complaint-driven changes are directional (warmer in summer, cooler in winter) and that operators over-correct [P021:E112][P021:E114]. This gives a literature-grounded reference point for what "over-compliance" would look like.
- The complaint literature shows complaints are a poor proxy for dissatisfaction [P023:E116][P025:E118], and LLM-simulated occupants diverge from human comfort data [P042:E139]. Ground truth for comfort should therefore come from DB II-type distributions or PCMs rather than from the simulated requesters.
- Lyu et al. (SSRN 6136668) should be read through institutional access; it is the one LISTING-only item whose title overlaps our topic.
