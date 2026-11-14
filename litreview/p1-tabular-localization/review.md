# Literature review — Tabular foundation models as Wi-Fi fingerprint localizers (PerCom WiP, paper 1)

Prepared 2026-11-14 (UTC). Every factual sentence about a paper carries an evidence tag `[Pxxx:Eyyy]` that resolves to `evidence.csv` (statement, locator, ≤12-word anchor) and to `sources/index.csv` (file, URL, SHA-256). Sentences marked **(our arithmetic)** or **(our inference)** are computations or readings made in this review, not claims of the cited paper.

---

## 0. Scope and method

- **Searches.** 35 logged searches (S001–S035 in `search_log.md`): local files (5), arXiv API (11 query groups), WebSearch (4), Consensus (6 calls, one rate-limited), OpenAlex (blocked, HTTP 429), Semantic Scholar (blocked, HTTP 429), Crossref (16 title look-ups), Hugging Face API (2), publisher and repository pages (5 groups).
- **Sources.** 39 source records (P001–P039): **17 FULLTEXT** (12 full-text papers, plus the SODIndoorLoc repository documents, the Zenodo and UCI dataset records and two sets of Hugging Face licence/metadata files) and **22 ABSTRACT**. Full-text paper reads used: 12 of the 14 allowed (P001, P002, P004, P005, P006, P007, P008, P009, P010, P013, P014, P023). Abstract-level entries: 22 of about 25.
- **Evidence.** 159 rows in `evidence.csv`. Every anchor was checked by script for an exact (whitespace-normalised) match in the saved source text before it was written.
- **Not reached.** OpenAlex and Semantic Scholar (rate limits), so the citing-papers search could not be run directly; GitHub API (not enabled in this session); MDPI, Elsevier and IEEE Xplore landing pages (blocked); Google Scholar was not used. See `unverified.md`.

## 1. Positioning (one paragraph)

Recent PerCom WiP work brought large pretrained models to fingerprint localization in two ways. Locaris fine-tunes a frozen Llama-3.2-1B with LoRA on telemetry written as text and claims few-shot cross-environment adaptation and robustness to missing APs [P001:E001][P001:E002][P001:E010][P001:E011]. The diffusion-transformer paper generates synthetic fingerprints to cut survey cost [P002:E013]. Few-shot fingerprinting otherwise relies on meta-learning or metric learning. These methods need meta-training on source environments and usually gradient adaptation in the target [P019:E120][P020:E122][P017:E117][P026:E135]. Wireless foundation models are pretrained on wireless channel data [P016:E116][P021:E123]. The closest in spirit, RA-LWLM, does training-free in-context localization from a per-scene reference database, but its in-context module is trained on labelled CSI from simulated scenes [P014:E109][P014:E111][P014:E112]. Tabular foundation models (TabPFN v2/2.5/3, TabICL/TabICLv2) are pretrained only on synthetic tables and predict in context [P013:E098][P006:E070][P022:E124][P039:E150]. Their own papers say they work best on small, IID data and are weaker on grouped splits and very large tables [P007:E081][P007:E083]. We found no paper that applies a tabular foundation model or prior-data fitted network to RSSI, CSI, BLE or cellular fingerprint positioning (Q1, §2-C below). That absence is the gap, but it rests on a search that is not exhaustive. The open question is whether an off-the-shelf, never-fine-tuned tabular in-context learner matches fine-tuned LLM localizers and classical baselines when only a few reference points are surveyed and APs go missing.

---

## 2. Clusters

### A. LLM and transformer-based fingerprint localizers

Synthesis. The UCSC group's line is WiFiGPT, then Locaris (arXiv), then the Locaris PerCom WiP. WiFiGPT fine-tunes LLaMA-3 models with LoRA and emits the answer as text by greedy decoding. It is trained separately per dataset and environment [P005:E033][P005:E034][P005:E036]. Locaris replaces text output with an MLP regression head and trains less than 1% of the parameters [P001:E004]. On SODIndoorLoc it adds vendor, scene and building descriptions to the RSSI tokens [P004:E023]. Its missing-AP robustness is shown on the 4–5-AP RSS-RTT dataset by dropping one or two APs [P004:E028][P004:E029]. Baselines there encode missing APs with placeholder values [P004:E030]. IndoorCART is an encoder-only transformer with missing-signal-aware attention. It reports 1.33 m MAE on SODIndoorLoc [P010:E050][P010:E051], and it reproduces six earlier RSSI transformers on the same split [P010:E152]. CR-AP (capsule routing on an AP–RP graph) reports 2.07 m mean error on SODIndoorLoc and an AP-masking robustness study [P023:E126][P023:E127].

| pid | paper | what it does | data / simulator | headline result | how our project differs | cite? | access |
|---|---|---|---|---|---|---|---|
| P001 | Locaris (PerCom WiP 2026) | Frozen Llama-3.2-1B + LoRA + MLP head, AP-as-token input [P001:E001][P001:E003] | SODIndoorLoc; Wi-Fi RSS-RTT | SOD avg MAE 2.84 m [P001:E007]; lecture 0.88 m with 3% target data [P001:E009] | No fine-tuning at all; tabular in-context learner; no LLM | must | FULLTEXT |
| P004 | Locaris (arXiv 2510.11926) | Same, with protocol details, AP-drop and quantisation [P004:E028] | same | 2-AP drop: 2.5–3.5 m vs >7–9 m for CNN/KNN [P004:E029] | as above; we test missing APs on many-AP data (SOD) | must (for protocol) | FULLTEXT |
| P005 | WiFiGPT (arXiv 2505.15835) | LoRA-SFT LLaMA-3 1B/3B/8B, text output [P005:E033] | own ESP32 CSI; RSS-RTT | RSS-RTT MAE ≈0.90–1.16 m per environment [P005:E157] | per-environment training [P005:E036] vs zero training | must | FULLTEXT |
| P010 | IndoorCART (Front. Signal Process. 2026) | Encoder transformer, missing-aware attention [P010:E050] | UJIIndoorLoc, TUJI1, SODIndoorLoc | MAE 4.79 / 0.18 / 1.33 m [P010:E051] | tuned, trained per dataset [P010:E055] | must | FULLTEXT |
| P023 | CR-AP (Sci. Rep. 2026) | Capsule routing on heterogeneous AP/RP graph | SODIndoorLoc (+CETC331 cross-scene) | 2.07 m mean, P90 3.94 m [P023:E126] | trained model; its AP-masking protocol is a template for ours [P023:E127] | maybe | FULLTEXT |

### B. Few-shot, meta-learning and other data-efficient fingerprinting

Synthesis. Data-efficient fingerprinting comes in three kinds.
- **Meta-learning initialisations.** MetaLoc and FeMLoc meta-train on many source environments, then fine-tune in the target [P019:E120][P020:E122]. EnvCoLoc and GenMetaLoc add 3-D point-cloud conditioning [P017:E118][P018:E119].
- **Metric and relation learning.** The Sensors 2023 prototypical network and LESS learn embeddings or distances [P025:E134][P026:E135].
- **Synthetic augmentation.** The PerCom DiT paper generates fingerprints [P002:E013]. Its generator is trained before the real-data fraction is drawn [P002:E016], which suggests (our inference) that the generator saw more than the "1%" of real data.

| pid | paper | what it does | data / simulator | headline result | how our project differs | cite? | access |
|---|---|---|---|---|---|---|---|
| P002 | DiT fingerprint synthesis (PerCom WiP 2026) | Class-conditional DiT generates RSS fingerprints [P002:E013] | UCI WiFi (4 rooms), POWDER | 78.3%→98.5% room accuracy at 1% real data [P002:E015] | we regress coordinates with no generator and no training | must | FULLTEXT |
| P019 | MetaLoc (IEEE JSAC 2023) | MAML on historical environments [P019:E120][P019:E121] | synthetic + real | outperforms baselines (abstract) | needs meta-training + target fine-tuning | must | ABSTRACT |
| P020 | FeMLoc (IEEE IoT-J 2024) | Federated meta-learning, then minimal fine-tuning [P020:E122] | real datasets | (abstract) up to 80.95% better than NN after 100 steps | same | maybe | ABSTRACT |
| P017 | EnvCoLoc (arXiv 2026) | Point-cloud-conditioned diffusion meta-learning [P017:E117] | real-world | up to 20% lower mean error, 10 support samples [P017:E117] | needs 3-D scans + meta-training [P017:E118] | maybe | ABSTRACT |
| P018 | GenMetaLoc (arXiv 2025) | Meta-learned diffusion fingerprint generation (CSI) [P018:E119] | real CSI | outperforms baselines | needs point clouds, CSI | no | ABSTRACT |
| P025 | Few-shot WiFi FP (Sensors 2023) | Prototypical network + Kalman filter [P025:E134] | own data | better with fewer labels | classification over positions; trained encoder | maybe | ABSTRACT |
| P026 | LESS (IEEE TWC 2023) | Few-shot relation networks + augmentation [P026:E135] | dynamic indoor | adapts without network updating | trained metric; we use a pretrained generic prior | maybe | ABSTRACT |

### C. In-context learning and foundation models for wireless localization (incl. Q1)

Synthesis.
- **Wireless foundation models.** Radio Foundation Models, LWLM and OmniLoc pretrain on wireless measurements, then fine-tune or decode per task [P016:E116][P021:E123][P015:E114].
- **RA-LWLM.** It is the only paper found that frames localization as in-context learning [P014:E109]. Its context comes from retrieval in a frozen wireless-FM embedding space [P014:E110]. Its in-context module is trained on labelled CSI from Sionna ray-tracing scenes [P014:E111][P014:E112], and real measurements are left for future work [P014:E113].
- **Our design.** Ours would differ on every one of these axes: real Wi-Fi RSSI, a model never trained on any wireless data, and no localization-specific training.

**Q1 — Has anyone applied TabPFN, TabICL or any tabular foundation model or PFN to RSSI, CSI, BLE or cellular fingerprint positioning?** We found no such paper. What we searched and what came back:

| # | Where | Exact query | Result |
|---|---|---|---|
| S004 | earlier dump (local) | TabPFN × {localization, positioning, fingerprint, RSSI, wireless}, arXiv + OpenAlex | arXiv 19 + 21 + 2 + 0 + 0 titles, none on RF positioning; all OpenAlex calls HTTP 429 |
| S010 | arXiv API | `all:TabPFN AND (all:localization OR all:positioning OR all:RSSI OR all:fingerprint OR all:CSI OR all:wireless)` | 38 results, 0 relevant ("fingerprint" hits are molecular fingerprints) |
| S011–S012 | arXiv API | `("tabular foundation model" OR "prior-data fitted" OR TabICL) AND (localization OR positioning OR indoor OR RSSI OR WiFi OR Wi-Fi OR BLE OR cellular)` | 63 results, 0 relevant |
| S013 | arXiv API | `("in-context learning" OR "foundation model") AND (fingerprint OR RSSI) AND (localization OR positioning)` | 18 results; RA-LWLM and Radio FM (wireless FMs, not tabular) |
| S020–S021, S027–S028 | WebSearch (1 extended) | four phrasings, TabPFN / "tabular foundation model" × Wi-Fi/BLE/CSI/cellular/RSRP | 40 results, none uses a tabular FM |
| S022 | Consensus (50 papers) | `TabPFN prior-data fitted network indoor localization positioning RSSI CSI fingerprint` | 50 localization papers; 0 contain "TabPFN", "prior-data" or "tabular foundation" |
| S025–S026 | OpenAlex, Semantic Scholar | TabPFN localization; TabPFN indoor positioning RSSI; works citing the TabPFN Nature DOI | **blocked (HTTP 429)** |
| proxy for citing papers | TabPFN-3 report, Appendix I | text search of the 200+ applications listed by Prior Labs [P006:E079] | 0 hits for locali*, positioning, RSSI, Wi-Fi, indoor, wireless, fingerprint, Bluetooth, GNSS |
| proxy | RA-LWLM full text | "TabPFN", "tabular" | 0 hits (our check) |

Conclusion: we found no evidence of prior use. The citing-paper search (OpenAlex/Semantic Scholar) was blocked, and Google Scholar and IEEE Xplore were not searched, so the claim should be worded as "to our knowledge" and the searches re-run before submission.

| pid | paper | what it does | data / simulator | headline result | how our project differs | cite? | access |
|---|---|---|---|---|---|---|---|
| P014 | RA-LWLM (arXiv 2026) | Retrieval-augmented in-context localization with frozen wireless FM [P014:E109][P014:E110] | Sionna ray-tracing, single-BS CSI [P014:E112] | near-identical accuracy on seen and unseen scenes (abstract) | real RSSI; generic tabular prior; no ICL training on wireless data | must | FULLTEXT |
| P015 | OmniLoc (arXiv 2026) | Geometry-aware FM, anchor-free UE localization [P015:E114] | in-house + one public set [P015:E115] | outperforms existing methods (abstract) | requires wireless pretraining | maybe | ABSTRACT |
| P016 | Radio Foundation Models (arXiv 2024) | SSL-pretrained transformer on 5G CSI, then fine-tune [P016:E116] | own 5G | 10× less reference data | needs pretraining + fine-tuning | maybe | ABSTRACT |
| P021 | LWLM (arXiv 2025) | SSL wireless localization FM with decoders [P021:E123] | 5G/6G channels | 26–87.5% over non-pretrained transformers (abstract) | same | no | ABSTRACT |

### D. Tabular foundation models: capabilities, limits, licences, failure modes

Synthesis. All versions predict in context after offline pretraining on synthetic data [P022:E124][P013:E098][P006:E070]. TabPFN v2 handles regression and missing values natively. It encodes a per-cell missingness indicator [P013:E099][P013:E106]. Its regression target in pretraining is a single variable [P013:E100], so 2-D coordinates need two models or a wrapper (our inference). Regression output is a full predictive distribution [P006:E080]. The licence regime changed at v2.5 (table below).

| Version | Documented rows / features / classes | Regression | Missing values | Licence (as fetched 2026-11-14) | Weights gated? |
|---|---|---|---|---|---|
| TabPFN v1 (2022) | ≤1,000 train rows, ≤100 numerical features, no missing values, ≤10 classes [P022:E125] | no (classification) [P022:E124] | no [P022:E125] | not checked | not checked |
| TabPFN v2 (Nature 2025) | ≤10,000 samples, ≤500 features evaluated [P013:E103]; ≤10 classes natively [P013:E101] | yes [P013:E099] | yes, indicator per cell [P013:E106] | Prior Labs License 1.1 = Apache 2.0 + attribution [P011:E090][P011:E091] | no (HF gated=false) [P011:E095] |
| TabPFN-2.5 (2025) | "up to 50,000 data points and 2,000 features" (abstract) [P038:E148]; TabPFN-3 report says 100,000 rows and 2,000 features [P006:E072]; conflict in `unverified.md` | yes, 85% win rate vs XGBoost to 100K/2K [P038:E149] | (not stated in abstract) | non-commercial, non-production [P011:E092]; bans surveillance-related use [P011:E093]; not for consumers [P011:E094] | no [P011:E095] |
| TabPFN-2.6 | no technical document fetched | — | — | "tabpfn-2.6-license-v1.0" (same family as 2.5) [P011:E093] | no [P011:E095] |
| TabPFN-3 (2026) | to 1M rows; wins reported to 1M rows / 200 features [P006:E071]; ≤200 features per estimator by default [P006:E074]; up to 160 classes | yes, distributional [P006:E080] | native NaN indicator [P006:E073] | TABPFN-3.0: no commercial or production use of model, derivatives or outputs [P006:E078] | no [P011:E095] |
| TabPFN-3.5 | HF repo only (created 2026-09-09) [P011:E096]; no report fetched | — | — | "tabpfn-3-5-license-v1.0" [P011:E096] | no [P011:E095] |
| TabICL (2025) | ≤500K samples, 500 features, ~20 GB GPU [P008:E087] | **no** (classification only) [P008:E088] | (TALENT uses mean imputation; not native) | BSD-3-Clause on HF [P012:E097] | no [P012:E097] |
| TabICLv2 (2026) | million-scale under 50 GB GPU [P039:E151] | yes [P039:E150] | (not stated in abstract) | code released (abstract) [P039:E150]; HF tag for v2 weights not checked | not checked |

Known failure modes stated by the model authors or the BeyondArena benchmark:
- Large data, highly non-smooth regression targets and real-time inference [P013:E102][P013:E108].
- Early feature compression becomes a bottleneck when rows and features are both large [P006:E075].
- Grouped splits and data above 100k rows [P007:E083].
- IID splits applied to grouped data distort rankings [P007:E084].

| pid | paper | what it does | data | headline result | relevance | cite? | access |
|---|---|---|---|---|---|---|---|
| P013 | TabPFN v2 (Nature 2025) | Synthetic-prior ICL for classification + regression | AutoML/CTR23 ≤10k rows | beats tuned baselines ≤10k samples [P013:E098] | the model we use (licence-safe) | must | FULLTEXT |
| P022 | TabPFN v1 (arXiv 2022) | Original PFN classifier | OpenML-CC18 small | competitive with AutoML [P022:E124] | lineage | maybe | ABSTRACT |
| P038 | TabPFN-2.5 report | Scaled TabPFN | TabArena | wins to 100K/2K [P038:E149] | larger context | maybe | ABSTRACT |
| P006 | TabPFN-3 report | 1M rows, NaN handling, OOD prior [P006:E076] | TabArena etc. | SOTA claims | per-estimator 200-feature cap matters for 300+ AP tables [P006:E074] | must | FULLTEXT |
| P008 | TabICL | Column-then-row ICL classifier | TALENT | on par with TabPFNv2, faster | classification only [P008:E088] | maybe | FULLTEXT |
| P039 | TabICLv2 | Open TFM, regression + classification [P039:E150] | TabArena, TALENT | beats RealTabPFN-2.5 (abstract) | permissively licensed alternative | must | ABSTRACT |
| P007 | Beyond IID (BeyondArena) | Benchmark of TFMs off IID | 142 datasets | TFMs best ≤100k IID, weaker on grouped [P007:E081] | location-disjoint splits are "grouped" (our inference) | must | FULLTEXT |

### E. Datasets and published numbers

Synthesis. SODIndoorLoc has 9 training and 5 testing sheets. The variants differ in AP set (all detected MACs vs pre-installed APs only) and in samples per RP (30 vs averaged) [P003:E018][P009:E046]. Test points sit at locations different from the RPs [P009:E047], and undetected MACs are +100 [P003:E019]. RSS dimensions are 52/347/363 (All) and 52/56/46 (pre-installed APs) for CETC331/HCXY/SYL [P003:E020]. The RSS-RTT Zenodo set has non-overlapping train and test points, 4–5 APs, a Pixel 3 phone and a CC BY 4.0 licence [P024:E132][P024:E133]. UJIIndoorLoc (>20 users, 25 devices) and TUJI1 (5 devices, fixed split) are the standard multi-device benchmarks [P034:E143][P035:E144]. UCI Wireless Indoor Localization is a 4-room classification set with no coordinates [P037:E146].

**Q2 — Locaris vs IndoorCART on SODIndoorLoc.**

| Aspect | Locaris | IndoorCART |
|---|---|---|
| Train / test files | "default train/test split" of the dataset paper [P004:E022]; Table I counts 955/11,370/8,880 train, 840/860/1,020 test [P001:E006]. These equal the `_30` (HCXY, SYL) and CETC331 sheet sizes [P003:E020][P009:E046] (our inference; All_30 and AP_30 have the same counts, so the AP set is not identified) | "21,205 training and 2,720 test samples" [P010:E052], equal to the sums of the same sheets (our arithmetic); original partitions kept [P010:E054] |
| Features | valid RSSI values plus vendor identifiers, scene descriptions and building labels as text [P004:E023]; All vs AP sheet not stated | 364 "detected APs" and features listed as "Floor, BuildingID, coordinates, RSSI" [P010:E053]; 364 matches neither the All union (762) nor the AP union (154) (our arithmetic); missing APs imputed column-wise, Min–Max scaled [P010:E056] |
| Model granularity | per building, results averaged over CETC331/SYL/HCXY [P001:E007]; 3 seeds [P004:E024] | one model for SODIndoorLoc as a whole [P010:E055], attributing gains to its three-building, multi-floor layout [P010:E061]; fixed split + bootstrap CI |
| Metric | "MAE" described as average distance error [P004:E026]; but its median (3.88 m) exceeds its MAE (2.84 m) [P001:E007], unusual for Euclidean errors (our inference) | MAE and R² as primary metrics, no formula in text [P010:E057]; Euclidean errors used in the worst-case analysis [P010:E058] |
| Baselines | "adopted from" the dataset paper [P001:E005] (default scikit-learn parameters [P009:E039]) | nine baselines re-tuned on a validation split [P010:E055]; e.g. KNNR 2.66 m, RFR 2.15 m [P010:E059] |

**Our reconstruction of Locaris Table III (our arithmetic).** The dataset paper ran classifiers (KNC, RFC, MLPC) only in HCXY [P009:E044][P009:E041]. Locaris's KNC, RFC and MLPC rows equal, in all five columns, the mean of the dataset paper's HCXY sheet-1 (All_30) and sheet-2 (AP_30) rows [P009:E043]. For example:
- KNC MAE (2.339 + 5.893)/2 = 4.116 and 95th (6.686 + 25.807)/2 = 16.247 [P009:E041][P009:E064][P001:E007].
- RFC MAE (6.242 + 7.227)/2 = 6.735 [P009:E042][P009:E065].
- MLPC MAE (29.411 + 6.955)/2 = 18.183 [P009:E066][P009:E067].

These baselines are therefore HCXY-only, half of them use the pre-installed-AP sheet, and none was tuned, even though Table III is captioned as an average across all three buildings [P001:E007]. The KNR and MLPR rows could not be reproduced from any subset average of Tables 11–13 (unresolved, `unverified.md`).

**Why 1.33 m vs 2.84 m?** The split does not explain the gap: both use the same default sheets. The plausible sources are:
- aggregation: a per-building average for Locaris vs one pooled model for IndoorCART;
- inputs: Locaris adds scene and building text, and IndoorCART lists floor and building IDs among its features;
- the unclear MAE definition in both papers;
- tuned (IndoorCART) vs untuned (Locaris) comparators.

This cannot be settled from the papers (our inference). Both papers, and the dataset paper, print "RMSE" values below MAE in places [P009:E068][P010:E060]. That is impossible for a root-mean-square of the same errors (our inference), so the RMSE columns cannot be compared across these papers.

**Dataset-paper baselines and metric definitions.**
- Metrics are MAE, RMSE, 50th, 75th (the IPIN competition score) and 95th percentile error, in metres [P009:E040].
- Baselines are scikit-learn with no tuning; KNN uses k = 5, distance weighting and the Euclidean metric [P009:E039].
- Best per sheet: HCXY All_30 SVC 2.259 / KNC 2.339 MAE [P009:E159][P009:E041]; HCXY AP_30 RFR 3.198 [P009:E158]; SYL best MAEs 3.844 (SVR, All_30), 3.787 (RFR, AP_30), 3.782 (KNR, All_Avg), 4.048 (KNR, AP_Avg) [P009:E044]; CETC331 KNR 2.876 [P009:E045].
- The abstract says the "best average positioning accuracy is about 2.3 m" [P009:E038].
- Dropping from 347 to 56 MACs in HCXY raised KNR MAE by 59.3% [P009:E048].

| pid | dataset / paper | what it provides | split | published numbers | use for us | cite? | access |
|---|---|---|---|---|---|---|---|
| P009/P003 | SODIndoorLoc (Satellite Navigation 2022) | 3 buildings, All vs AP sheets, user/phone IDs [P003:E021] | fixed RP/TP sheets | see Q2 | main benchmark; AP vs All gives a missing-AP axis | must | FULLTEXT |
| P024/P036 | Wi-Fi RSS & RTT (Zenodo; J-ISPIN 2024) | 3 LOS conditions, 4–5 APs [P024:E132] | non-overlapping points | J-ISPIN: up to 1.8 m gain [P036:E145] | few-shot cross-environment (Locaris protocol) | must | FULLTEXT / ABSTRACT |
| P034 | UJIIndoorLoc (IPIN 2014) | multi-building, 25 devices [P034:E143] | fixed | IndoorCART 4.79 m [P010:E051] | 520 APs exceeds TabPFN v2's evaluated 500 features [P013:E103] | maybe | ABSTRACT |
| P035 | TUJI1 (Data in Brief 2024) | 5 devices, fine grid [P035:E144] | fixed train/test | IndoorCART 0.18 m [P010:E051]; dense split caveat [P010:E062] | device heterogeneity | maybe | ABSTRACT |
| P037 | UCI Wireless Indoor Localization | 2,000 rows, 7 APs, 4 rooms [P037:E146] | none | DiT 98.5% at 1% real data [P002:E015] | classification only; unsuitable for coordinate regression | no | FULLTEXT |

### F. Classic lineage

Synthesis. RADAR combined signal-strength measurements at several base stations with propagation modelling [P031:E140]. Horus used probabilistic models with location clustering and reported under 0.6 m average error on its testbeds [P032:E141]. Ferris et al. used Gaussian processes as a likelihood model with learned hyperparameters [P033:E142]. That GP approach is the conceptual ancestor of a Bayesian, prior-based predictor such as a PFN (our inference). The two overviews cover ML pipelines, datasets and device differences [P027:E136][P028:E137].

| pid | paper | what it does | data | headline | link to us | cite? | access |
|---|---|---|---|---|---|---|---|
| P031 | RADAR (INFOCOM 2000) | RSS + propagation model / nearest neighbour [P031:E140] | own building | "high degree of accuracy" | kNN lineage | must | ABSTRACT |
| P032 | Horus (MobiSys 2005) | probabilistic fingerprinting [P032:E141] | 2 testbeds | <0.6 m avg | probabilistic lineage | maybe | ABSTRACT |
| P033 | GP fingerprinting (RSS 2006) | GP likelihood model [P033:E142] | WiFi + GSM | superior to baselines | Bayesian prior lineage | must | ABSTRACT |
| P027 | ML Wi-Fi RSSI overview (IEEE Access 2021) | survey [P027:E136] | — | — | background | maybe | ABSTRACT |
| P028 | RSSI ML review (Smart Cities 2025) | survey [P028:E137] | — | — | background | no | ABSTRACT |

### G. Robustness to missing APs and device heterogeneity

Synthesis.
- **Device heterogeneity.** SSD (signal-strength differences) addresses heterogeneity between training and test devices [P029:E138]. Park et al. found that AP-detection features hurt under device diversity, while signal strength alone holds up [P030:E139]. That is relevant to how missingness is encoded (our inference). SODIndoorLoc documents RSS-range differences across its nine phones [P009:E049].
- **Missing-AP protocols.** CR-AP masks 10–60% of APs at random and finds that plain KNN overtakes it above 40% [P023:E127][P023:E128]. Tree ensembles degrade quickly in that setting [P023:E130]. Locaris drops 1–2 of 4–5 APs [P004:E028].
- **TFM design fit.** Tabular FMs encode NaN with an explicit indicator, so a missing AP need not be replaced by a +100 or −105 sentinel [P013:E106][P006:E073].

| pid | paper | what it does | data | headline | link to us | cite? | access |
|---|---|---|---|---|---|---|---|
| P029 | SSD (IEEE TMC) | device-robust fingerprint [P029:E138] | WiFi + BT | better cross-device accuracy | heterogeneity baseline idea | maybe | ABSTRACT |
| P030 | Device diversity (INFOCOM 2011) | analysis of RSS and AP-detection diversity [P030:E139] | many 802.11 devices | detection features hurt | how to encode missing APs | must | ABSTRACT |
| P023 | CR-AP (Sci. Rep. 2026) | AP-masking robustness [P023:E127] | SODIndoorLoc | KNN best above 40% missing [P023:E128] | reuse protocol | maybe | FULLTEXT |
| P004 | Locaris (arXiv) | AP-drop ablation [P004:E028] | RSS-RTT | 2.5–3.5 m with 2 APs dropped [P004:E029] | direct comparison point | must | FULLTEXT |

**Q3 — Does each few-shot / ICL method need training on the target environment, and what data does it need beforehand?**

| Method | Training in target? | Needed beforehand | Evidence |
|---|---|---|---|
| MetaLoc | yes, fast adaptation from meta-parameters | labelled data from many well-calibrated historical environments | [P019:E120] |
| FeMLoc | yes, minimal fine-tuning | diverse datasets from edge devices (federated meta-training) | [P020:E122] |
| EnvCoLoc | yes, inner-loop gradient steps on ~10 support samples | meta-training environments + 3-D point clouds | [P017:E117][P017:E118] |
| GenMetaLoc | yes, rapid adaptation of the generator | meta-training data, 3-D point clouds, CSI | [P018:E119] |
| LESS | no network update after initial training ("even without the network updating") | sparsely collected fingerprints of the site, augmented | [P026:E135] |
| Few-shot Sensors 2023 | not stated in abstract (prototypes from support samples) | labelled support samples per position | [P025:E134] |
| DiT augmentation | yes (generator + classifier) | the training split (generator trained first) | [P002:E016] |
| Locaris | yes, LoRA fine-tuning on 1–100% of target data | fine-tuning on two source environments | [P004:E027] |
| WiFiGPT | yes, trained per environment | none beyond the LLM | [P005:E036] |
| Radio FM | yes, per-environment optimisation | unlabelled 5G channel data for SSL | [P016:E116] |
| LWLM | yes, label-limited fine-tuning of decoders | SSL pretraining on channel data | [P021:E123] |
| RA-LWLM | **no** per-scene retraining | pretrained wireless FM + ICL module trained on labelled simulated scenes + a labelled per-scene database | [P014:E109][P014:E111] |
| OmniLoc | not stated in abstract | in-house wireless data for the FM | [P015:E114] |
| **Ours (TabPFN-type)** | **no** | nothing wireless; only the labelled target reference points as context | design premise |

**Q4 — What do the tabular-FM papers themselves say?**

- **Small-sample regression.**
  - TabPFN v2 supports regression and outputs a distribution [P013:E099][P006:E080].
  - It matches default CatBoost with half the training samples [P013:E104].
  - Highly non-smooth regression is a case where boosted trees are likely to win [P013:E102].
  - BeyondArena: TFMs perform best on tiny (100–1k rows) and small, IID data [P007:E082][P007:E085].
- **Many features.**
  - v2 was evaluated only to 500 features [P013:E103]; v2.5 claims 2,000 [P038:E148].
  - TabPFN-3 caps each estimator at 200 features by default and relies on ensembling to cover more [P006:E074].
  - TabPFN-3's many-features slice is classification-only [P006:E077].
  - TabPFN-3 warns of a compression bottleneck when rows and features are both large [P006:E075].
  - In BeyondArena, high dimensionality stops mattering once size is controlled [P007:E083].
- **Distribution shift.**
  - TabPFN-3 adds an out-of-distribution prior for shift and extrapolation [P006:E076].
  - TabPFN v2 criticises trees' out-of-distribution behaviour [P013:E107].
  - BeyondArena finds grouped (non-IID) splits are one of only two significant weaknesses of TFMs [P007:E083].
  - Wrong (IID) splits on grouped data distort conclusions [P007:E084].

---

## 3. Threats to novelty (ranked)

1. **RA-LWLM — high.** It already presents "training-free" in-context localization from a labelled per-scene database [P014:E109]. *Distinguish:*
   - real Wi-Fi RSSI rather than simulated single-BS CSI [P014:E112];
   - a model never trained on wireless data and with no localization-specific ICL training [P014:E111];
   - a public-dataset few-shot and missing-AP study.
2. **Unindexed or uncaught prior use of TabPFN for localization — medium-high.** Our negative result has gaps (Q1): the citing-paper search was blocked and Google Scholar and IEEE Xplore were not covered. *Distinguish / mitigate:* re-run the OpenAlex citing-works and Google Scholar searches before submission; word the claim "to our knowledge".
3. **Locaris and WiFiGPT own "foundation model + few-shot + missing APs" — medium.** They claim few-shot adaptation and missing-AP robustness [P001:E010][P001:E011][P004:E029]. *Distinguish:*
   - no fine-tuning and no GPU-hours spent on adaptation;
   - missing-AP tests on high-dimensional SODIndoorLoc (AP vs All sheets [P003:E018]) rather than 4–5-AP data;
   - our reconstruction shows Locaris's SOD baselines are untuned and HCXY-only (§2-E).
4. **Meta-learning few-shot methods — medium.** MetaLoc, FeMLoc and EnvCoLoc also target few labelled target samples [P019:E120][P017:E117]. *Distinguish:* they need meta-training environments and gradient adaptation (Q3).
5. **Wireless foundation models (OmniLoc, LWLM, Radio FM) — low.** They use different inputs and require wireless pretraining [P015:E114][P021:E123][P016:E116].
6. **"Port TabPFN to a new domain" is a common pattern — low to medium.** The TabPFN-3 report lists 200+ such applications [P006:E079]. *Distinguish:* localization-specific findings (NaN vs sentinel for missing APs, the per-estimator feature cap vs 300+ APs, 2-D regression, location-disjoint splits).

## 4. Numbers we may need to quote (with definitions)

- **SODIndoorLoc structure:**
  - training 955 / 11,370 / 8,880 samples and testing 840 / 860 / 1,020 (CETC331 / HCXY / SYL) [P001:E006];
  - HCXY and SYL training keep 30 samples per RP, CETC331 one averaged sample, 10 samples per TP [P009:E046];
  - RSS dimensions All 52/347/363 vs AP 52/56/46 [P003:E020]; undetected = +100 [P003:E019].
- **SODIndoorLoc metrics** (dataset paper): MAE, RMSE, P50, P75, P95 in metres; untuned scikit-learn baselines [P009:E040][P009:E039]. HCXY All_30 KNC MAE 2.339 m, P75 3.059 m, P95 6.686 m [P009:E068][P009:E041]; CETC331 KNR MAE 2.876 m [P009:E045]; SYL best MAE 3.782–3.844 m depending on sheet [P009:E044].
- **Locaris (SOD)**: "MAE" 2.840 m, RMSE 6.140, P50 3.880, P75 7.540, P95 10.280, averaged across the three buildings, 3 seeds [P001:E007][P004:E024]. KNR in the same table: 3.758 / 4.178 / 2.703 / 4.768 / 10.293 [P001:E007].
- **IndoorCART (SOD)**: MAE 1.33 m, 95% bootstrap CI as reported, on 2,720 test samples; strongest reproduced transformer HyTra 1.89 m [P010:E051][P010:E052][P010:E152]; tuned RFR 2.15 m, KNNR 2.66 m [P010:E059].
- **CR-AP (SOD)**: mean 2.07 m, P90 3.94 m [P023:E126]; whether this is HCXY-only is ambiguous [P023:E129].
- **RSS-RTT (Locaris few-shot)**: train on two source environments, then fine-tune with 1–100% of target training data; lecture 0.88 m at 3% vs best baseline 1.88 m [P004:E027][P001:E009]; 5 seeds; baselines tuned with 30 Optuna trials [P004:E155][P004:E156]. Split sizes conflict between Locaris Table II and the Zenodo record [P004:E154][P024:E131].
- **TabPFN v2 regime**: ≤10,000 samples and ≤500 features evaluated [P013:E103]; 0.2 s per prediction at 10k×10 [P013:E108].

## 5. Suggested reference shortlist (16)

1. Locaris, PerCom WiP 2026 [P001] — direct competitor and venue precedent.
2. Locaris arXiv long version [P004] — protocol details (split, metadata inputs, AP drop).
3. WiFiGPT [P005] — LLM fine-tuning per environment; contrast with zero training.
4. IndoorCART [P010] — best reported SODIndoorLoc number and transformer baselines.
5. DiT fingerprint synthesis, PerCom WiP 2026 [P002] — data-efficient fingerprinting at the venue.
6. MetaLoc, IEEE JSAC 2023 [P019] — canonical meta-learning few-shot localization.
7. LESS, IEEE TWC 2023 [P026] — few-shot relation learning without network updates.
8. RA-LWLM [P014] — closest in-context localization work; key differentiation.
9. TabPFN v2, Nature 2025 [P013] — the model and its documented limits.
10. TabPFN-3 report [P006] — current version, NaN handling, feature cap, licence.
11. TabICLv2 [P039] — permissively licensed regression-capable alternative.
12. Beyond IID / BeyondArena [P007] — documented failure modes (grouped splits).
13. SODIndoorLoc dataset paper [P009] — benchmark, sheets and metric definitions.
14. Wi-Fi RSS & RTT dataset (Zenodo) / J-ISPIN 2024 [P024]/[P036] — few-shot cross-environment benchmark.
15. RADAR [P031] or Ferris et al. GP [P033] — classic kNN / Bayesian lineage (choose one if space is short).
16. Park et al., INFOCOM 2011 [P030] — device diversity and missing-AP encoding.

## 6. Open questions and unverified items

See `unverified.md`. The main ones:
- the citing-paper search for Q1 was blocked;
- the AP set (All vs AP sheets) used by Locaris and IndoorCART is unknown;
- the Locaris KNR/MLPR baseline rows cannot be reproduced;
- the MAE definitions in Locaris and IndoorCART are ambiguous;
- TabPFN-2.5 limits conflict between sources;
- no technical documents exist for TabPFN-2.6/3.5;
- Locaris and Zenodo disagree on the RSS-RTT split counts.

## 7. Notes for the PI

- **Licences.** TabPFN v2 is Apache-2.0-derived with an attribution clause [P011:E090]. From 2.5 onward the licences are non-commercial and explicitly exclude "surveillance, including any research or development relating to surveillance" [P011:E093]. A localization paper may want its headline results on v2 or TabICLv2 (BSD-3 on HF for TabICL [P012:E097]), with a licence check of the TabICLv2 weights.
- **Reporting SOD.** State the sheet (All_30 vs AP_30) and whether models are per building or pooled. Use Euclidean error and a true RMSE. Keep SceneID, BuildingID and FloorID out of the inputs, or report them separately: both competitors appear to use such metadata [P004:E023][P010:E053].
- **AP vs All as a missing-AP axis.** The AP vs All sheets give a natural "missing-AP" stress test on real data (347→56 MACs raised KNR MAE by 59% in the dataset paper [P009:E048]). Pair it with CR-AP-style random masking [P023:E127], and compare NaN encoding with the +100/−105 sentinel.
- **Feature counts vs model limits.** HCXY/SYL All sheets have 347/363 features [P003:E020]. That is within v2's evaluated 500 [P013:E103] but above TabPFN-3's per-estimator default of 200 [P006:E074]. UJIIndoorLoc has 520 APs.
- **2-D targets.** TabPFN regression is single-target [P013:E100], so x and y need two fits (or a joint wrapper). Say this explicitly.
- **Splits.** Use location-disjoint splits for few-shot sampling. BeyondArena shows IID splits on grouped data inflate results [P007:E084]. IndoorCART itself cautions about dense splits [P010:E062].
- **Locaris Table III.** If we cite Locaris's SOD table, its classifier baselines equal the mean of the dataset paper's two HCXY sheets (§2-E). Re-run the baselines ourselves rather than copying them.
- **Drop UCI.** The UCI dataset is room classification only [P037:E146]; it is unsuitable for the coordinate-regression claims.
