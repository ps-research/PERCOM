> Written on 2026-11-15, before Paper 1 was chosen, as the bar for what this track accepts. "Paper 1" to "Paper 7" below are the seven accepted PerCom 2026 WiP papers, not our papers. The section "What this means for our two papers" is historical: only our Paper 1 (tabular foundation models for Wi-Fi fingerprint localization) goes forward.

# PerCom 2026 WiP — what seven accepted papers show

Read in full on 15 Nov 2026 (text extracted programmatically, every page and every figure and table inspected). These seven were chosen because they resemble what we can execute, so they are not a random sample of the 32 accepted papers, and an accepted list says nothing about what was rejected.

## The seven at a glance

| # | Paper | Kind | Data | Hardware | People | Figs | Tables | Eqs | Refs | Baselines | Variance shown |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | HVAC RL + LLM teacher (U Tokyo) | RL method | EnergyPlus simulator + real weather | none | none | 4 | 0 | 5 | 12 | SAC, LLM-only, converged SAC | no |
| 2 | QPilot (Keio) | RL system | own road video, 79 clips | Jetson AGX Xavier + RTX desktop | none | 3 | 4 | 2 | 15 | two fixed detectors | no |
| 3 | LLM + evacuation maps (Sapienza, Oulu) | user study | two floor maps | a phone | N = 37 | 2 | 0 | 0 | 6 | none | Likert SDs |
| 4 | Diffusion transformers for fingerprints (CMU) | generative model | 2 public datasets | none | none | 3 | 1 | 2 | 22 | GAN, interpolation, real-only, oracle | timing only |
| 5 | Locaris (UCSC) | LLM fine-tune | 2 public datasets | none | none | 7 | 3 | 0 | 7 | 5 classical + 5 ML | yes |
| 6 | LingoMotion (Aalto) | concept + first result | 1 public dataset | none | none | 3 | 1 | 0 | 17 | none | no |
| 7 | Cycling safety (Bamberg) | field study | own, 10 riders, 415 km | bike sensor, watch, camera | 10 volunteers | 2 | 0 | 2 inline | 16 | qualitative check vs a danger map | no |

## What earns acceptance

1. **A classic pervasive problem, named in the first sentence.** Buildings/HVAC, edge video analytics, indoor localization (three of the seven), human motion, cycling safety.
2. **One of three kinds of contribution.**
   - Port a method that is hot elsewhere to that problem and say you are first: papers 1, 4, 5, 6.
   - Measure on real hardware: papers 2, 7.
   - Study real people: papers 3, 7.
3. **Compute-only is a proven route.** Four of seven used no devices and no participants (1, 4, 5, 6): three on public datasets, one in a standard simulator.
4. **The evidence load is light.** Two to four figures is typical (paper 5, with seven, is the outlier); five of seven have at most one table; each has one headline number. Four of seven have baselines; three have none. Only one shows run-to-run variance.
5. **Candour is tolerated.** Paper 3's headline is that the idea mostly fails (25 of 37 users mislocalized). Paper 1 lists its limits, paper 4 prints an unflattering cost table, paper 7 calls its own analyses exploratory.
6. **Review depth is shallow.** Paper 5's text contradicts its own table; paper 4 has a possible evaluation flaw; paper 6 calls R² = 0.716 "high fidelity"; paper 7 concludes more than it tested. The bar is "relevant, new-looking, plausible", not "airtight".
7. **A roadmap.** Six of seven end with concrete next steps; the WiP is framed as step one.
8. **Shape.** Abstract → Introduction (related work often folded in, contributions stated) → Method → Evaluation or Preliminary Results → Conclusion and Future Work. 6–22 references.
9. **Titles.** Three hedge ("On the Promise of", "Investigating", "A Field Study for"); QPilot and LingoMotion put a system name in the title, and Locaris names its system in the text.

## Reinforcement learning at this track

- Two RL papers, two different routes. Paper 1 is simulator-only (EnergyPlus through Sinergym, real weather files, an API LLM). Paper 2 needed an edge device and self-collected, hand-labelled video.
- RL novelty is modest in both: stock SAC plus one KL term borrowed from an IJCAI 2024 paper; stock DQN with a three-number state and no rule-based baseline.
- The route that fits GPUs and no devices is paper 1's: a community-standard simulator, real-world input files, three or four controllers including an upper bound, a learning curve, a final-performance bar chart and one behaviour trace.
- A search result shows the Tokyo group has since taken this line to NeurIPS 2026 with a real-room deployment (not read; from the listing only), so "LLM teacher for HVAC RL" looks occupied.

## Corrections to what I said before reading

- I said RL here is typically simulator-evaluated and needs no devices. That holds for one of the two RL papers, not both.
- From titles I counted two human-factors papers. Paper 3 is also one (index term "Human-computer interaction", a 37-person study).
- My shortlist idea "locate me from what I see" is paper 3. It is taken.
- The arXiv version of Locaris is a longer paper; the WiP is a four-page cut of it.

## What this means for our two papers

- A compute-only paper on public data or a standard simulator is squarely within what gets accepted. The recipe: a named pervasive problem; a method or question new to it; one or two public datasets or a standard simulator; three to five baselines; one main figure and one table; a stated roadmap.
- An RL paper should follow paper 1's route (simulator), on a control problem or question the Tokyo line does not cover.
- Doing the cheap things the accepted papers skipped — several seeds, error bars, text that matches the tables — would put us above the observed bar.
- The human-centred corner is real but its accepted examples used real people. Paper 7 names an open gap that needs none: self-report crowdsensing is "more susceptible to noise, reporting bias" for lack of "sensor-based validation". The smell-report finding (ratings rise with the number of recent visible reports at near-zero sensor readings) measures exactly that against physical sensors.
- Paper 3 leaves a language problem open (people give descriptions the model cannot use), but following it up would need participants.

---

# Per-paper notes

## 01 — Accelerating Model-Free RL for HVAC Control with an LLM as a Policy Teacher
Miyake, Murakami, Taniguchi, Kawahara (Univ. of Tokyo; Daikin joint research). PerCom Workshops 2026, pp. 539–542. DOI 10.1109/PerComWorkshops68308.2026.11585189

**Claim.** Model-free RL is too sample-hungry for real HVAC; an LLM alone cannot adapt to a building. Use the LLM as a "policy teacher" early, then let RL take over. Reaches good control in ~1/5 of the training steps of plain SAC.

**Method.** SAC actor objective J = J_SAC + α·J_LLM, with J_LLM = −E_{s~D}[KL(π(·|s) ‖ π_LLM(·|s))]. Teacher = Gaussian N(a_llm, σ²I), σ = 0.5 fixed; a_llm from gpt-5-mini via a role + chain-of-thought prompt given the state as text, queried for every state in each minibatch. α annealed 1.0→0.01 over 2000 steps, held to 4000, then 0. Adapted from Zhou et al., IJCAI 2024 (discrete robotics) to continuous actions. Reward r = −w_e·E − (1−w_e)·P, w_e = 0.25; comfort band 20–23.5 °C winter, 23–26 °C summer.

**Setup.** Simulation only: EnergyPlus via Sinergym. One thermal zone of a two-storey office, AirflowNetwork on, 12 temperature nodes, two AC units (setpoints + fan speeds), 30-min timestep, one-day episodes. Real weather files: Tokyo winter (train Nov–Feb, test Feb 1), Singapore summer (train Jun–Sep, test Aug 1).

**Baselines (4 controllers).** SAC from scratch; LLM-only (few-shot); LLM-SAC (ours); SAC(sat.) trained to convergence (~287,000 steps ≈ 16 simulated years) as an upper bound.

**Evidence.** 4 figures, 0 tables, 5 equations, 12 references.
- Fig. 1 architecture block diagram.
- Fig. 2 learning curves, 0–5000 steps: LLM flat at −0.1868; LLM-SAC at LLM level within ~200 steps (≈4 days) vs >1000 steps (≈21 days) for SAC; sharp dip near 2000 steps ("policy oscillation" when α drops), recovers and ends above the LLM line.
- Fig. 3 bar charts after 14–28 days of training. Tokyo winter comfort deviation ≈ SAC 5.4 / LLM 2.05 / LLM-SAC 1.4 / SAC(sat) 1.05 °C; power ≈ 165 / 138 / 115 / 110 kWh. Singapore summer comfort ≈ 0.45 / 0.04 / 0.01 / 0.12; power ≈ 42 / 38 / 36 / 23 kWh (bar heights read off the plot).
- Fig. 4 one-day control trace, LLM-only vs LLM-SAC (comfort violations shaded).

**What it does not have.** No seeds, error bars or significance tests (curves look like single runs); one building; no ablation of σ or the α schedule; no accounting of LLM query cost; no real deployment. Limitations paragraph admits simulation-only, instability at the hand-over, and sensitivity to bad teacher advice.

**Structure.** Abstract → I Intro (related work folded in, 3 contribution bullets) → II Method (A objective, B teacher, C reward) → III Evaluation and Discussion (A setup, B learning efficiency, C final performance, D qualitative) → IV Conclusion (limits + future work) → Acknowledgment → References.

**Why it got in (my reading).** Classic pervasive problem (smart buildings) first, LLM as a tool. Takes a known ML recipe from another field and ports it to a domain-specific constraint (continuous actions). Standard community simulator, real weather, sensible baselines including an upper bound, one clear headline number.

**Aside.** A search result showed the same group later presenting an extended version at NeurIPS 2026 (critic-based filtering, EnergyPlus in two climates, a 15-day real-room deployment) — the WiP was the first step of a larger line.

---

## 02 — QPilot: Reinforcement Learning-Based Adaptive Scheduling for Object-Sparse MOT
Lo, Huang, Tsuge, Chen, Okoshi, Nakazawa (Keio Univ.; Reitaku Univ.; NICT grant). PerCom Workshops 2026, pp. 580–583. DOI 10.1109/PerComWorkshops68308.2026.11585199

**Claim.** On edge devices, multi-object tracking (MOT) is limited by detector cost. In object-sparse video (most frames empty), an RL agent that switches detector size per frame gets better tracking than a fixed small detector for a small extra GPU cost, and adapts to the device.

**Method.** DQN (Stable-Baselines3, 3-layer MLP) chooses among four YOLOv8 sizes (n/s/m/l) for the next frame. State S_t = (FPS_t/FPS_max, N_t/N_max, M_t) ∈ R³ — frame rate, number of tracked objects, current model index. Actions {0,1,2,3}. Tracker: ByteTrack. Models exported to ONNX → TensorRT. Reward described only in words (positive when objects are tracked at target FPS; small penalty for over-using compute; when empty, reward high FPS). Hyperparameters: learning starts after 2,000 steps, lr 1e-4, ε 1.0→0.1 over 40% of training. Builds on the group's own SenSys 2025 scheduler JumpQ (which skips detection; QPilot always detects but varies the model).

**Setup.** Real hardware, own data. Two platforms: desktop RTX 5060 Ti 16 GB and NVIDIA Jetson AGX Xavier 32 GB. Own road-driving videos (Kanagawa): train on 75 clips × 1,800 frames; test on 4 clips × 1,800 frames, hand-labelled with DarkLabel in MOT17 format; metrics via TrackEval.

**Baselines.** Only fixed YOLOv8n and fixed YOLOv8s. No fixed m/l, no hand-written switching rule, no comparison with JumpQ.

**Evidence.** 3 figures, 4 tables, 2 equations, 15 references.
- Fig. 1 system overview (RL decision layer / sensing layer / tracking layer). Fig. 2 DQN architecture.
- Table I platform specs.
- Table II MOT metrics. RTX: QPilot MOTA 52.60 / IDF1 68.89 / HOTA 56.17 vs N 39.26 / 56.57 / 46.01 vs S 44.73 / 62.76 / 50.68. Xavier: 46.23 / 63.46 / 52.28 vs N 37.55 / 54.87 / 45.11 vs S 43.73 / 61.68 / 49.14. Also FN, FP, MT, ML.
- Table III ID precision / recall: RTX 0.9788 / 0.5352; Xavier 0.9725 / 0.4721 (both above baselines).
- Table IV GPU usage / FPS. RTX: QPilot 16.66% / 58.56 vs N 10.54% / 63.63 vs S 13.62% / 60.75. Xavier: 45.98% / 27.16 vs N 39.69% / 29.32 vs S 53.55% / 25.79.
- Fig. 3 switching timelines over 1,800 frames: RTX toggles between N (≈60 FPS) and L (≈40 FPS); Xavier toggles between N (≈30 FPS) and M (≈15 FPS) and stays on M for the last ~500 frames.

**What it does not have.** RL is off-the-shelf with a 3-number state; the learned policy looks like "objects present → big model", and no rule-based baseline is run to show RL is needed. Reward not given numerically. Test set is four clips. No seeds or variance. Data not public.

**Structure.** Abstract → I Intro → II Related Work (scheduling / MOT / RL) → III Methodology (architecture; RL model selection) → IV Experimental Implementation (training; labelling + metrics; GPU measurement) → V Demonstration and Evaluation (tracking; efficiency; switching behaviour) → VI Conclusion and Future Work → Acknowledgment → References.

**Why it got in (my reading).** Named system, real edge device, real measurements (FPS, GPU %), standard task metrics, smart-city framing, and continuity with the lab's prior work. The RL itself is thin, so the bar for RL novelty at this track is low; what carried it is the systems evidence.

**Relevance to us.** This RL paper was NOT simulator-only — it needed a Jetson and self-collected, hand-labelled video.

---

## 03 — Investigating out-of-the-box Indoor Localization Using Large Language Models and Evacuation Maps
Trasciatti, Zeppieri, Datla, Panizzi (Sapienza Univ. of Rome); Chambers (Univ. of Oulu). PerCom Workshops 2026, pp. 526–529. DOI 10.1109/PerComWorkshops68308.2026.11585232. Index terms: Human-computer interaction, Indoor navigation, Large language models.

**Claim.** Infrastructure-free coarse indoor localization: give a vision LLM the building's evacuation map; the user describes what they see ("a fire extinguisher near an emergency exit"); the LLM marks the position on the map. Framed as an early feasibility study that "identifies current limitations".

**Method.** A custom GPT (GPT-o4-mini-high) with a short fixed prompt and the evacuation map uploaded; it asks about safety equipment, infers x,y and overlays a red cross with matplotlib. Model picked after an informal pre-test of Qwen2.5-VL, LLaVA 1.6, Llama 3.2-Vision, GPT-o4-mini and GPT-o4-mini-high (no numbers reported for that pre-test).

**Setup.** In-person user study, two sites, N = 37: Univ. of Oulu (N = 17) and Sapienza (N = 20). One fixed spot per site, chosen to be neither trivial nor impossible. Pre-questionnaire (demographics, 5-point Likert familiarity items), ChatGPT session on a provided phone (text or speech, English), post-questionnaire (was it right? trust, clarity, ease, frustration). May–June 2025.

**Baselines.** None. No comparison with any other localization method, model, or prompt.

**Evidence.** 2 figures (both are just the two evacuation maps), 0 tables, 0 equations, 6 references. All results are reported in running prose.
- Headline is negative: 25 of 37 users were NOT correctly localized (6/17 correct at Oulu, 6/20 at Sapienza).
- Oulu: trust 2.70 (SD 0.91); ease of describing 3.00; not-frustrating 3.80; clarity 3.05; conversation 44 s mean (median 20 s) + 85 s image generation; 2.6 messages. Of 11 mislocalized, only 4 could point to their true spot on the map.
- Sapienza: trust 2.85; ease 3.20; not-frustrating 4.45; clarity 3.30; conversation 20 s + 37 s image generation; 1.8 messages. Of 14 mislocalized, 8 could not pinpoint their position.
- Qualitative: vague first descriptions ("surrounded by green doors") gave the longest conversations and failed at both sites.

**What it does not have.** No statistics beyond means/SDs (they say the trust difference is not significant for lack of data); one location per building; no baselines; no ablation of prompt or model; no analysis of why the LLM failed (user description vs map reading).

**Structure.** Abstract → I Intro → II Related Works (one paragraph) → III Methodology (A study setup, B locations and maps, C LLM selection and prompt, D data collected) → IV Study Outcomes (A Oulu, B Sapienza) → V Discussion and Conclusion → References.

**Why it got in (my reading).** A fresh, cheap idea aimed at PerCom's favourite problem (indoor localization), tested with real people in two countries, reported honestly as mostly not working, with a clear next step (structured input instead of free text). The track's "novel, thought-provoking, early results" language applies literally.

**Relevance to us.**
- This IS the "locate me from what I see" idea I proposed (shortlist idea 1). That idea is taken.
- It is a human-factors paper: my title-only count of human-factors papers was too low.
- A negative result was accepted, with six references and no tables.
- Their stated open problem — people give descriptions the model cannot use — is a language-understanding problem.

---

## 04 — On The Promise of Diffusion Transformers for Data-Efficient Radio Fingerprinting
Gao, Harras (Carnegie Mellon University). PerCom Workshops 2026, pp. 489–492. DOI 10.1109/PerComWorkshops68308.2026.11585359

**Claim.** Fingerprint localization needs costly site surveys. A small Diffusion Transformer (DiT) can generate synthetic RSS fingerprints so that a classifier trained with as little as 1% real data recovers near-full-data accuracy. Purely data-driven, no physics priors. The paper says DiTs "have not been applied to fingerprinting".

**Method.** Standardize each RSS vector, clip/rescale to [−1, 1], rasterize into a 16×16 grayscale "image" (short vectors: put in the first row and tile vertically; long vectors: raster order with padding). Class-conditional DDPM, T = 400, linear schedule. DiT: 4×4 patches → 16 tokens, d_model 256, learned positional embedding, timestep + class embeddings added, 4 self-attention layers, MSE noise-prediction loss, AdamW lr 2e-4, EMA weights. 3.70 M parameters.

**Setup.** Compute only, two small public datasets. Indoor: UCI WiFi Localization (2,000 samples, 7 access points, 4 rooms). Outdoor: POWDER campus RSS (up to 25 receivers per sample, transmitter position discretized into a 4×4 grid = 16 classes). Downstream judge: a fixed 5-layer MLP classifier. Real-data fractions r ∈ {1, 5, 10, 25, 50, 80}%; synthetic samples fill the remaining (1−r).

**Baselines.** Real-only, conditional GAN (small MLPs), "Kriging-inspired" interpolation (random convex combinations of same-class samples + noise), and an oracle trained on 100% real data.

**Evidence.** 3 figures, 1 table, 2 equations, 22 references.
- Fig. 1 pipeline cartoon (room → RSS vector → rasterized image → DiT). Fig. 2 architecture block diagram.
- Fig. 3 the one results figure: accuracy vs % real data, two panels. UCI: real-only 78.3% at 1% → DiT-augmented 98.5% (oracle 98.8%); 95.9% → 98.9% at 5%; GAN 75.7% and Kriging 75.6% at 1% (below real-only). POWDER: real-only 36.8% at 1% → DiT 75.4% (oracle 82.6%); 61.5% → 77.7% at 5%; 68.6% → 75.4% at 10%; at ≥25% DiT is sometimes 1–3 points below real-only. The plot shows 1–50% only (80% is mentioned in the text but not plotted).
- Table I cost: DiT 3.70 M params, 14.11 MB, 721.60 ± 47.57 ms/sample; GAN 0.096 M, 0.37 MB, 0.13 ms; Kriging 0.026 ms.

**What it does not have.** No seeds or error bars on accuracy. Toy-scale datasets (one has 4 classes). Baselines are deliberately simple. As written, the DiT and GAN are first trained "using training samples" and only then are the real-data fractions drawn for the classifier — which reads as if the generator saw the full training set, so the "1% real data" result may not be a true low-data result; the flat DiT curve is consistent with that. The paper does not address it. No real deployment, no new data.

**Structure.** Abstract → I Intro (related work folded in, no contribution bullets) → II Methodology (A rasterization, B diffusion + DiT: generation process, embedding, backbone, objective) → III Preliminary Evaluation (A setup: datasets, baselines, verification; B preliminary results: indoor, outdoor, cost–benefit) → IV Conclusion and Future Directions → References. No acknowledgment.

**Why it got in (my reading).** PerCom's favourite problem (localization) + its best-known pain point (survey cost) + a fashionable model nobody had applied there + one clean headline number ("1% of the data") + honest cost table + title that hedges ("On the Promise of"). Two public datasets, one indoor and one outdoor, gave an appearance of generality.

**Relevance to us.** This is the purest compute-only template in the set: a new model class ported to a classic pervasive task, public data, one main figure, one table. Two authors, small model, days of work.

---

## 05 — Indoor Localization using Compact, Telemetry-Agnostic, Transfer-Learning Enabled Decoder-Only Transformer ("Locaris")
Bhatia, Elliott, Kuttivelil, Obraczka (UC Santa Cruz); Kocheta (independent). PerCom Workshops 2026, pp. 600–603. DOI 10.1109/PerComWorkshops68308.2026.11585338. Index terms: Indoor localization, Wi-Fi, LLM, LLaMA, GPT.

**Claim.** A small LLM (Llama-3.2-1B), fine-tuned with LoRA, can act as a Wi-Fi localization regressor that takes raw telemetry as text, handles missing access points and mixed telemetry types, and adapts to a new environment with ~5–10% of the calibration data baselines need.

**Method.** Telemetry written as a token sequence ("AP1 RTT:v AP2 RSS:v …"). Frozen Llama-3.2-1B backbone; LoRA adapters on the attention projections (q, k, v, o); the last token's hidden state goes to a 2-layer MLP regression head → (x, y); MSE loss. <1% of parameters trained. Sequences of 10–50 tokens.

**Setup.** Compute only, two public datasets (>44,000 measurements in total).
- SODIndoorLoc (RSSI; 3 buildings CETC331 / HCXY / SYL; ~24,000 samples; 1,900+ reference points).
- WiFi RSS & RTT (Zenodo; 20,500+ FTM + RSSI samples; 342 reference points; lecture theatre LOS, office mixed, corridor NLOS).

**Baselines.** SODIndoorLoc: KNC, KNR, MLPC, MLPR, RFC (taken from the dataset paper). RSS/RTT: CNN, kNN, LightGBM, MLP, Transformer.

**Evidence.** 7 figures, 3 tables, 0 equations, 7 references — the densest results section of the seven.
- Table III (SODIndoorLoc averages): Locaris MAE 2.840 m, RMSE 6.140, median 3.880, 75th 7.540, 95th 10.280. KNR: 3.758 / 4.178 / 2.703 / 4.768 / 10.293. KNC: 4.116 / 4.664 / 2.201 / 4.874 / 16.247.
- Figs. 2–4 few-shot curves (MAE ± std vs fraction of target data) for lecture / corridor / office: Locaris sub-metre at 3% (0.88 m), 10% (0.96 m), 4% (0.95 m); baselines at 100% data reach 1.14 / 1.19 / 1.49 m; Locaris at 100%: 0.61 / 0.81 / 0.80 m.
- Fig. 5 FTM+RSSI bars: Locaris 0.87 / 0.65 / 0.83 m (corridor / lecture / office) vs best baseline 1.12 / 0.95 / 1.26.
- Fig. 6 FTM-only: Locaris 1.49 / 1.05 / 1.42 vs kNN 1.39 / 1.28 / 1.41; CNN and MLP blow up (11–35 m).
- Fig. 7 RSSI-only: Locaris 5.15 / 4.50 / 2.70 vs kNN 25.23 / 7.86 / 8.00; CNN/MLP 59–86 m.
- Error bars (mean ± std) are shown — the only paper of the seven with visible run-to-run variance.

**Problems visible in the accepted paper.**
- Text says Locaris has "the lowest MAE (2.84 m) and RMSE (6.14 m)" and "consistently outperforms all baselines", but its own Table III shows KNR and KNC with lower RMSE (4.18, 4.66) and lower median and 75th-percentile error; Locaris wins on MAE and (by 1 cm) the 95th percentile only.
- RSSI-only: text says MAE "2.86 to 4.71 m"; Fig. 7 bars read 5.15 / 4.50 / 2.70.
- Conclusion says it "consistently stays under 1 m error"; SODIndoorLoc MAE is 2.84 m.
- Table II caption cites [7] for the dataset that is reference [6]; abstract has "Our findings findings".
- No limitations, no future work, no acknowledgment.

**Structure.** Abstract (long) → I Intro (3 contribution bullets) → II Locaris (A input, B backbone, C aggregation, D training, E inference cost) → III Experimental Methodology and Datasets → IV Results (A SODIndoorLoc; B RSS&RTT: cross-environment, telemetry ablation) → V Conclusion → References. A condensed cut of a longer arXiv paper (arXiv 2510.11926: 14 figures, 5 tables).

**Why it got in (my reading).** Localization again; an LLM as the tool; "first to…" claim; a named system; two public datasets; many baselines; ablations; a deployment-flavoured headline ("10× less calibration data"). Reviewers evidently did not cross-check the text against the table.

**Relevance to us.** Fully reproducible with GPUs: public data + a 1B open model + LoRA. Shows that "fine-tune a small open LLM on a classic pervasive regression task and beat classical baselines" is an accepted template.

---

## 06 — LingoMotion: An Interpretable and Unambiguous Symbolic Representation for Human Motion
Zhang, Liu, Xiao (Aalto University). PerCom Workshops 2026, pp. 498–501. DOI 10.1109/PerComWorkshops68308.2026.11585328. The published PDF matches the arXiv source (2603.13578) read earlier.

**Claim.** Human-motion representations (MotionGPT-style latent codes) are opaque and built on joint positions. Propose a "motion language" built on joint angles, organised like natural language: letters → words → phrases → sentences. This paper gives the concept design and implements only the first level (the alphabet).

**Method.** Convert SMPL joint positions (22 joints) to biomechanically standard joint angles. Per joint-angle channel: (1) segment the signal at local extrema, (2) normalise segments and K-Means cluster them into a codebook of shapes = "letters", (3) represent motion as a sequence of tuples (shape s, scale σ, bias μ, length l). Words / phrases / sentences are described in prose only.

**Setup.** Compute only, one public dataset: Motion-X (81.1K motion sequences), 70/30 train/test split. 28 joint-angle channels, 28 separate codebooks, 12–20 letters each.

**Baselines.** None. No comparison with VQ-VAE tokenisers or any other representation; no downstream task (no activity recognition, no generation).

**Evidence.** 3 figures, 1 table (two rows), 0 equations, 17 references.
- Fig. 1 the analogy (sound waves→letters→words… vs joint angles→motion letters→…), full page width.
- Fig. 2 SMPL skeleton with joint-angle definitions; right-hip angles are periodic during walking while right-knee position drifts.
- Fig. 3 the pipeline on right-hip flexion: segmentation, t-SNE of clusters + the 15-letter alphabet (S0–S14), original vs reconstructed curve, rendered poses.
- Table I: positions→angles→positions RMSE 0.009 / NMSE 0.005 / R² 0.978; angles→letters→angles RMSE 0.921 / NMSE 0.103 / R² 0.716.

**What it does not have.** Baselines, a downstream task, any evaluation of "interpretable" or "unambiguous" (the two words in the title). Calls R² = 0.716 "high fidelity". Refers to joint-angle algorithms "in Section IV.A" when they are in IV.B. Three of four language levels are unimplemented.

**Structure.** Abstract → I Intro (contributions in prose) → II Related Work → III Concept Design (A alphabet, B words/phrases/sentences) → IV Preliminary Implementation and Evaluation (A alphabet discovery, B positions→angles, C fidelity) → V Conclusions and Future Work → References.

**Why it got in (my reading).** A memorable framing idea with a strong Figure 1, tied to a core pervasive topic (human activity recognition), one large public dataset, and an explicit roadmap. This is the lowest evidence bar of the seven: a vision paper with one sanity-check table.

**Relevance to us.** Shows a concept-led paper with a single preliminary result is accepted. A language-flavoured idea applied to sensor data was welcome.

---

## 07 — Oh, Be Safe: A Field Study for Crowdsensed Cycling Safety Maps
Das, Ackermann, Ebner, Huba, Khalil, Nicklas (University of Bamberg; German federal + NextGenerationEU funding). PerCom Workshops 2026, pp. 502–505. DOI 10.1109/PerComWorkshops68308.2026.11585384. Index terms: cycling safety, riding stress, sensor technology, map annotation, field study.

**Claim.** Before a large crowdsensing campaign on cycling safety, check whether a cheap open-source sensor (OpenBikeSensor, ultrasonic overtaking distance) is usable, how riders' stress develops across overtakes, whether the unsafe hotspots it finds agree with official danger data, and which features relate to post-ride anxiety.

**Method.** Field study + a chain of standard analyses: Valhalla/OSM map-matching of noisy GPS and DTW against smartwatch GPS; YOLOv8 on rider video for traffic counts (MAE 1.25 vs manual labels); heart-rate spike ΔHR in a 6-s window around each confirmed overtake; trips grouped by change in a 6-item STAI anxiety questionnaire (relaxed / no change / stressful) × cycling experience; Huber regression + quadratic fit of ΔHR over successive overtakes to label each trip "habituation" or "fatigue"; DBSCAN (10 m) on overtake locations for hotspots; PCA on 21 features.

**Setup.** Own data, own hardware, real people. Bamberg, July–November 2025; 10 volunteers (18–30, 7 M / 3 F); 5 routes; 415 km; two riders per run (one instrumented, one filming); Polar smartwatch; 67 questionnaire responses; weather from DWD open data.

**Baselines.** No algorithmic baselines. External check = a qualitative comparison of hotspots with the public danger map gefahrenstellen.de.

**Evidence.** 2 figures, 0 tables, 2 inline formulas, 16 references. Most results are in prose.
- GPS: 109k points, 82.3% retained after filters (2.15% water, 15.3% gpx, 0.23% speed).
- Questionnaire: STAI decreased / increased / unchanged in 19.4% / 58.2% / 22.3% of trips; 16% moderately experienced, 84% experienced.
- Fig. 1 bar chart of trips labelled fatigue vs habituation across the six groups (read off the plot: NoChange-ModExp 1/0, NoChange-Exp 5/3, Relax-ModExp 1/1, Relax-Exp 2/6, Stress-ModExp 3/0, Stress-Exp 14/5).
- Hotspots: route 2 — unsafe events across 20 trips (danger map: deep yellow / orange); route 3 — 33 unsafe events (red); route 4 — 23 (red; Fig. 2 shows their hotspot map next to the danger map); route 5 — 6 (yellow). One "safe" hotspot with ΔHR > 4 that the danger map does not flag.
- PCA: 13 components for 95% variance; PC1–PC3 = 57%, described in words (traffic + turning; max HR + temperature + speed; overtaking distance + speed + mean HR). No PCA figure.

**What it does not have.** Statistical tests; any validation of the distance measurements themselves (the conclusion still says the sensor "reliably" measures overtaking distance); a link between the PCA and the anxiety scores it is said to explain; the paper itself calls the habituation analysis "exploratory … rather than robust estimation" and the hotspot validation "qualitative".

**Structure.** Abstract → I Intro (related work folded in; four questions listed) → II Dataset Overview (A sensor data, B smartwatch, C formative study) → III Feature Processing (A map construction, B traffic volume, C physiological, D grouping riders) → IV Preliminary Results (A GPS, B stress development, C unsafe zones, D PCA) → V Conclusion → References. Uses run-in headings and a wrapped figure to fit four pages.

**Why it got in (my reading).** A real field deployment with multimodal sensing on a societally legible problem, by a funded group, presented as groundwork for a larger campaign. Effort and realism carried it, not analytic depth.

**Relevance to us.**
- The intro states the gap our smell-report finding addresses: self-report crowdsensing platforms give scores "derived from aggregated user submissions rather than sensor-based validation" and are "more susceptible to noise, reporting bias, and intentional or unintentional data vandalism". We would be measuring that reporting bias against physical sensors.
- This kind of paper is out of reach for us (needs riders, devices, months).

---
