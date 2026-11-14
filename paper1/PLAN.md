# Paper 1 plan

- **Status:** draft, not approved
- **Approved by PI on:** (empty until approved; no brief is written before that)
- **Track:** IEEE PerCom Work-in-Progress, 4 pages in IEEE two-column format, including figures, tables and references

## 1. Claim and contributions

**Working title.** Tabular Foundation Models as Training-Free Wi-Fi Fingerprint Localizers.
If the results support it, the title becomes "Do We Need an LLM to Localize?". We choose after the results are in.

**Claim to test.** A tabular foundation model, taken off the shelf, can serve as a Wi-Fi fingerprint localizer with no training at all. The model was pretrained on synthetic tables only and has never seen wireless data. The surveyed fingerprints of a building are passed to it as context, and it predicts the position of a new scan. We test whether this matches tuned classical methods, how it compares with the numbers published for fine-tuned LLM localizers, and how it behaves when few reference points are surveyed or access points go missing.

**Contributions.**

1. The first study, to our knowledge, of tabular foundation models as fingerprint localizers.
2. A comparison under one stated protocol: one model per building, signal strengths as the only input, Euclidean error, tuned baselines, repeated runs.
3. Two stress tests that matter in deployment: how accuracy falls as fewer reference points are surveyed, and how it falls as access points disappear after the survey.
4. A cost account: time and memory, with no training step.

**What we write for each outcome.**

| Question | If yes | If no |
|---|---|---|
| Does the tabular model match or beat the best tuned baseline on the full survey? | Headline result | "Matches within X m with zero tuning" is still the result |
| Is its advantage largest with few reference points? | Headline number: the share of survey effort saved | Report where the crossover is |
| Does native missing-value handling help when access points go missing? | A localization-specific finding | Report it; CR-AP already found kNN is strong above 40% missing |
| Is it close to the fine-tuned LLM in the few-shot setting? | Supports the question in the title | Keep the neutral title; state what pretraining on sister environments buys |

## 2. Paper structure and page budget

| Section | Content | Pages |
|---|---|---|
| I. Introduction | LLM localizers at PerCom, their training cost, our question, contributions | 0.55 |
| II. Related work | LLM and transformer localizers; few-shot and meta-learning; wireless foundation models; tabular foundation models | 0.30 |
| III. Approach | Fingerprint table as context; two regressors for the two coordinates; missing access points as missing values; Fig. 1 | 0.50 |
| IV. Evaluation setup | Datasets, models, baselines, protocol, metrics | 0.45 |
| V. Preliminary results | Full survey (Table I); few reference points and missing access points (Fig. 2); comparison with the LLM localizer (Table II); cost | 1.35 |
| VI. Limitations, conclusion and future work | Includes device differences, other buildings as context, uncertainty estimates | 0.25 |
| Acknowledgment | Disclosure of AI use, as IEEE requires | 0.05 |
| References | 22 at most | 0.50 |

## 3. Experiments

**Rules that apply to every experiment.**

- One model per building. Inputs are signal strengths only. Building, floor, scene, user and phone labels are never inputs.
- Error is the 2-D Euclidean distance in metres between the predicted and the true position. We report mean, median, 75th and 95th percentile.
- Tabular foundation models run with default settings and are never tuned.
- Each baseline is tuned with 30 Optuna trials on reference points held out from the training sheet. Whole reference points are held out, never single scans.
- All methods see exactly the same splits and the same random draws.

**Models.**

| Group | Models |
|---|---|
| Tabular foundation models | TabPFN v2; TabICLv2 |
| Tuned baselines | k-nearest neighbours; random forest; LightGBM; support vector regression; multilayer perceptron; Gaussian process regression |
| Published numbers, quoted and not re-run | Locaris; IndoorCART; CR-AP |

**Experiments.**

| ID | Question | Data | What varies | Repeats | Feeds |
|---|---|---|---|---|---|
| E0 | Is our pipeline correct? | SODIndoorLoc | Nothing. Re-create the dataset paper's untuned kNN results (2.876 m in CETC331, 2.365 m in HCXY with all MACs) | 1 | Gate; not in the paper |
| E1 | With the full survey, how do the models compare? | SODIndoorLoc, default sheets, three buildings | Model | 5 seeds | Table I |
| E2 | How does error grow as fewer reference points are surveyed? | SODIndoorLoc | Share of reference points kept: 5, 10, 25, 50, 100% | 10 random draws | Fig. 2a |
| E3 | How does error grow when access points go missing after the survey? | SODIndoorLoc | Share of access points switched off at test time: 0 to 60% in steps of 10. Missing values written as "missing" or as a placeholder number | 10 random draws | Fig. 2b |
| E4 | How close is it to a fine-tuned LLM when little target data is available? | Wi-Fi RSS & RTT, three environments | Share of target training data, at the shares Locaris reports. Our models get the target share only | 5 seeds | Table II |
| E5 | What does it cost? | All of the above | Nothing; wall-clock time and peak GPU memory are logged in every run | | One column in Table I |

**Details that the briefs will pin down.**

- E0 must come within 0.05 m of the dataset paper. If it does not, the node stops and reports.
- E1 uses the sheets with all detected MACs. The sheets with pre-installed access points only are run as well and reported in the text.
- The HCXY training sheet has 11,370 rows, above the 10,000 that TabPFN v2 was evaluated on. Its context is a random 10,000 rows, and we say so.
- In E2, the baselines are re-tuned on each reduced survey.
- In E3, the same access points are switched off for every test scan of a draw.
- In E1, the difference between the best tabular model and the best baseline gets a paired bootstrap interval over test points.

## 4. Assets

| Asset | Source | Licence | Status |
|---|---|---|---|
| SODIndoorLoc | github.com/bijingxue/SODIndoorLoc; Bi et al., Satellite Navigation 2022 | Not yet read | Node records it at download |
| Wi-Fi RSS & RTT | Zenodo, 10.5281/zenodo.11558791 | CC BY 4.0 | Confirmed |
| TabPFN v2 weights | Prior Labs, Hugging Face | Prior Labs License 1.1 (Apache 2.0 plus an attribution clause) | Confirmed |
| TabICLv2 | `tabicl` package | Code released; licence of the v2 weights not yet read | Node records it at download |
| scikit-learn, LightGBM, Optuna, GPyTorch | PyPI | BSD-3 / MIT / MIT / MIT | Node records versions |

Not used: TabPFN 2.5 and later. Their licence is non-commercial and excludes research relating to surveillance.

## 5. Figures and tables

| Item | Content | Width |
|---|---|---|
| Fig. 1 | Schematic: the surveyed fingerprints are the context, a new scan is the query, the output is a position. A small inset contrasts this with fine-tuning an LLM | One column |
| Table I | Full survey. Rows: methods. Columns: mean error per building, average, median, 95th percentile, time. Published numbers in separate rows, marked "as reported, different protocol" | One column |
| Fig. 2 | (a) error against share of reference points; (b) error against share of access points missing. Lines per method, bands showing spread over draws | Two columns |
| Table II | Few-shot results on Wi-Fi RSS & RTT next to the numbers Locaris reports | One column |

One headline number goes in the abstract. Which one is decided after the results.

## 6. Risks

| Risk | What we do |
|---|---|
| Someone has already done this. The literature search is closed and one search (papers citing TabPFN) was never run | Write "to our knowledge" |
| The tabular model is weak on location-disjoint splits; its own literature warns about grouped splits | This is one of the things we measure. An honest negative is acceptable at this venue |
| Published LLM numbers are not comparable with ours (different inputs, unclear metric) | Quote them as reported, in separate rows, with the caveat |
| "You only applied an existing model" | Lead with the localization-specific findings: missing-value handling, survey effort saved, cost |
| Locaris's authors may review the paper | Stay neutral. We say we re-ran all baselines under one protocol. We do not write about the problems in their baseline table |
| The LLM is clearly ahead in E4 | Keep the neutral title and say what pretraining on sister environments buys |
| Model size limits (10,000 rows, 500 features for TabPFN v2) | HCXY context capped at 10,000 rows; all feature counts are below 500 |
| IEEE policy on AI-generated content | Disclose in the Acknowledgment |

An informal single run in the planning sandbox had the tabular model ahead of kNN in all three buildings. It is not evidence and is not reported. The node reproduces everything from scratch.

## 7. Compute estimate

Under one GPU-day in total on a single GPU, a few gigabytes of disk. Most of the time goes to tuning the baselines on CPU.

## 8. What follows approval

Three briefs, each run by the compute node only when its status is `approved`:

1. `P1-E01`: environment, data, pipeline check (E0), full survey (E1), cost logging (E5).
2. `P1-E02`: few reference points (E2) and missing access points (E3).
3. `P1-E03`: comparison on Wi-Fi RSS & RTT (E4).

## 9. Decisions for the PI

| Decision | Recommendation |
|---|---|
| Include the head-to-head with Locaris's published few-shot numbers (E4)? | Yes. Without it the "LLM" question has no direct evidence. We report it whichever way it goes |
| Mention the problems in Locaris's baseline table? | No |
| Title | Neutral working title now; decide after results |
