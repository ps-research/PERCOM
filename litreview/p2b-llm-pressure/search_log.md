# Search log (p2b-llm-pressure)

## S001
- UTC: 2026-11-14T21:44:27Z
- Tool: local file read (python3)
- Query/URL: `/home/claude/pilots/lit/idea2_arxiv.json (10 earlier arXiv queries, abstracts)`
- Results: 44 entries across 10 queries; 5 queries returned 0
- Kept: Peacemaker or Troublemaker (arXiv, lead only; verified separately). Zero-hit queries recorded as prior negative evidence for Q2: sycophancy AND HVAC/thermostat/smart home/smart building/building control; LLM AND HVAC AND prompt injection/adversarial/manipulation/jailbreak/persuasion; LLM AND smart home AND sycophancy/over-compliance/persuasion/user pressure/assertive; cyber-physical AND sycophancy; LLM AND energy AND occupant AND phrasing/politeness/tone/assertiveness
- Dropped: remaining entries are HVAC/RL/distillation papers, out of scope (building-control agent covers them)

## S002
- UTC: 2026-11-14T21:46:08Z
- Tool: arXiv API (curl-equivalent urllib) https://export.arxiv.org/api/query
- Query/URL: `ti:"Ask don\x27t tell" AND ti:sycophancy (malformed escape)`
- Results: 0
- Kept: none
- Dropped: query malformed; redone in S008

## S003
- UTC: 2026-11-14T21:46:09Z
- Tool: arXiv API (curl-equivalent urllib) https://export.arxiv.org/api/query
- Query/URL: `ti:"Beyond the Sycophancy Score"`
- Results: 1
- Kept: Beyond the Sycophancy Score (arXiv 2610.08840) https://arxiv.org/abs/2610.08840
- Dropped: -

## S004
- UTC: 2026-11-14T21:46:09Z
- Tool: arXiv API (curl-equivalent urllib) https://export.arxiv.org/api/query
- Query/URL: `ti:SPINE AND ti:sycophancy`
- Results: 1
- Kept: SPINE (arXiv 2609.09090) https://arxiv.org/abs/2609.09090
- Dropped: -

## S005
- UTC: 2026-11-14T21:46:09Z
- Tool: arXiv API (curl-equivalent urllib) https://export.arxiv.org/api/query
- Query/URL: `ti:"Measuring Sycophancy of Language Models in Multi-turn"`
- Results: 1
- Kept: SYCON Bench (arXiv 2505.23840) https://arxiv.org/abs/2505.23840
- Dropped: -

## S006
- UTC: 2026-11-14T21:46:09Z
- Tool: arXiv API (curl-equivalent urllib) https://export.arxiv.org/api/query
- Query/URL: `ti:SycEval`
- Results: 1
- Kept: SycEval (arXiv 2502.08177) https://arxiv.org/abs/2502.08177
- Dropped: -

## S007
- UTC: 2026-11-14T21:46:09Z
- Tool: arXiv API (curl-equivalent urllib) https://export.arxiv.org/api/query
- Query/URL: `ti:"Towards Understanding Sycophancy in Language Models"`
- Results: 1
- Kept: Sharma et al. (arXiv 2310.13548) https://arxiv.org/abs/2310.13548
- Dropped: -

## S008
- UTC: 2026-11-14T21:46:09Z
- Tool: arXiv API (curl-equivalent urllib) https://export.arxiv.org/api/query
- Query/URL: `ti:"Reducing sycophancy in large language models"`
- Results: 2
- Kept: Ask don't tell (2602.23971) https://arxiv.org/abs/2602.23971; Simple synthetic data reduces sycophancy (2308.03958) https://arxiv.org/abs/2308.03958
- Dropped: -

## S009
- UTC: 2026-11-14T21:46:09Z
- Tool: arXiv API (curl-equivalent urllib) https://export.arxiv.org/api/query
- Query/URL: `ti:"contradict humans"`
- Results: 2
- Kept: Ranaldi & Pucci (2311.09410) https://arxiv.org/abs/2311.09410
- Dropped: family healthcare robot paper: HRI user study, not LLM yielding

## S010
- UTC: 2026-11-14T21:46:09Z
- Tool: arXiv API (curl-equivalent urllib) https://export.arxiv.org/api/query
- Query/URL: `ti:"Multilingual Agentic Policy" AND ti:sycophancy`
- Results: 0
- Kept: none
- Dropped: not on arXiv under that title; see web search later

## S011
- UTC: 2026-11-14T21:46:09Z
- Tool: arXiv API (curl-equivalent urllib) https://export.arxiv.org/api/query
- Query/URL: `ti:"Not Just RLHF"`
- Results: 1
- Kept: Not Just RLHF (2605.12991) https://arxiv.org/abs/2605.12991
- Dropped: -

## S012
- UTC: 2026-11-14T21:46:09Z
- Tool: arXiv API (curl-equivalent urllib) https://export.arxiv.org/api/query
- Query/URL: `ti:"Peacemaker or Troublemaker"`
- Results: 1
- Kept: Peacemaker or Troublemaker (2509.23055) https://arxiv.org/abs/2509.23055
- Dropped: -

## S013
- UTC: 2026-11-14T21:46:09Z
- Tool: arXiv API (curl-equivalent urllib) https://export.arxiv.org/api/query
- Query/URL: `ti:MemSyco`
- Results: 1
- Kept: MemSyco-Bench (2607.01071) https://arxiv.org/abs/2607.01071
- Dropped: -

## S014
- UTC: 2026-11-14T21:46:09Z
- Tool: arXiv API (curl-equivalent urllib) https://export.arxiv.org/api/query
- Query/URL: `ti:"Silicon Mirror"`
- Results: 2
- Kept: The Silicon Mirror (2604.00478) https://arxiv.org/abs/2604.00478
- Dropped: CCAT-prime astronomy paper, unrelated

## S015
- UTC: 2026-11-14T21:46:09Z
- Tool: arXiv API (curl-equivalent urllib) https://export.arxiv.org/api/query
- Query/URL: `ti:SmartBench`
- Results: 2
- Kept: SmartBench smart homes (2603.06636) https://arxiv.org/abs/2603.06636
- Dropped: SmartBench Chinese smartphone assistant (2503.06029): not smart home control

## S016
- UTC: 2026-11-14T21:46:09Z
- Tool: arXiv API (curl-equivalent urllib) https://export.arxiv.org/api/query
- Query/URL: `ti:AgentAuditor`
- Results: 1
- Kept: AgentAuditor (2506.00641) https://arxiv.org/abs/2506.00641
- Dropped: -

## S017
- UTC: 2026-11-14T21:46:09Z
- Tool: arXiv API (curl-equivalent urllib) https://export.arxiv.org/api/query
- Query/URL: `ti:"Safety Risk Awareness for LLM Agents"`
- Results: 1
- Kept: R-Judge (2401.10019) https://arxiv.org/abs/2401.10019
- Dropped: -

## S018
- UTC: 2026-11-14T21:46:09Z
- Tool: arXiv API (curl-equivalent urllib) https://export.arxiv.org/api/query
- Query/URL: `ti:"Be Friendly, Not Friends"`
- Results: 1
- Kept: Be Friendly, Not Friends (2502.10844) https://arxiv.org/abs/2502.10844
- Dropped: -

## S019
- UTC: 2026-11-14T21:46:09Z
- Tool: arXiv API (curl-equivalent urllib) https://export.arxiv.org/api/query
- Query/URL: `ti:"Does Sycophancy Change Decisions"`
- Results: 0
- Kept: none
- Dropped: not on arXiv under that title; web search later

## S020
- UTC: 2026-11-14T21:46:09Z
- Tool: arXiv API (curl-equivalent urllib) https://export.arxiv.org/api/query
- Query/URL: `ti:"Sycophantic AI decreases prosocial"`
- Results: 1
- Kept: Cheng et al. (2510.01395) https://arxiv.org/abs/2510.01395
- Dropped: -

## S021
- UTC: 2026-11-14T21:46:48Z
- Tool: arXiv API https://export.arxiv.org/api/query
- Query/URL: `abs:politeness AND abs:"large language models" AND abs:prompt`
- Results: 15
- Kept: Mind Your Tone (2510.04950); Should We Respect LLMs? (2402.14531, SICon 2024); No Universal Courtesy / PLUM (2604.16275); Prompt Robustness Is Task-Dependent (2607.05554)
- Dropped: 11 political-bias papers: off-topic (matched 'polit*')

## S022
- UTC: 2026-11-14T21:46:48Z
- Tool: arXiv API https://export.arxiv.org/api/query
- Query/URL: `abs:persuasion AND abs:LLM AND abs:compliance AND (abs:Cialdini OR abs:principles)`
- Results: 1
- Kept: AgentPhishing (2610.31404) - abstract-level candidate for D
- Dropped: -

## S023
- UTC: 2026-11-14T21:46:48Z
- Tool: arXiv API https://export.arxiv.org/api/query
- Query/URL: `abs:"emotional stimuli" AND abs:"large language models"`
- Results: 10
- Kept: EmotionPrompt (2307.11760); NegativePrompt (2405.02814, IJCAI 2024); Role of Emotional Stimuli and Intensity (2604.07369)
- Dropped: remainder about emotion recognition/inference by LLMs, not effect of emotional phrasing on behaviour

## S024
- UTC: 2026-11-14T21:46:48Z
- Tool: arXiv API https://export.arxiv.org/api/query
- Query/URL: `abs:sycophancy AND (abs:agent OR abs:agents) AND (abs:tool OR abs:actions OR abs:embodied)`
- Results: 15
- Kept: Assertion-Conditioned Compliance (2512.00332); Your Wish Is My Commit (2610.36346); Peacemaker (dup)
- Dropped: others: embodiment perception, reward hacking theory, MCP security, memory search - not yielding-in-action

## S025
- UTC: 2026-11-14T21:46:48Z
- Tool: arXiv API https://export.arxiv.org/api/query
- Query/URL: `abs:"prompt injection" AND (abs:"smart home" OR abs:robot OR abs:"cyber-physical" OR abs:IoT)`
- Results: 15
- Kept: When Prompts Control Robots (2608.00747); A Study on Prompt Injection vs LLM mobile robots (2408.03515); Trust in LLM-controlled robotics survey (2601.02377); Device Context Protocol (2605.26159)
- Dropped: 3D/VLM physical-injection, MCP, ISR swarm, generic agentic taxonomies: tangential; no smart-home/building hit

## S026
- UTC: 2026-11-14T21:46:48Z
- Tool: arXiv API https://export.arxiv.org/api/query
- Query/URL: `abs:LLM AND (abs:mediator OR abs:mediation OR abs:arbitrat*) AND abs:conflicting AND abs:preferences`
- Results: 4
- Kept: none directly (no work on assertiveness deciding outcome)
- Dropped: ontology constraint acquisition, personalization memory, value dilemmas, couples co-design: not LLM arbitration between assertive humans

## S027
- UTC: 2026-11-14T21:47:26Z
- Tool: WebSearch
- Query/URL: `"Learning Multilingual Agentic Policy to Control Sycophancy" EACL 2026`
- Results: 10
- Kept: ACL Anthology 2026.eacl-long.169 https://aclanthology.org/2026.eacl-long.169
- Dropped: researchr/catalyzex mirrors and other Ranaldi papers (X-Agent EMNLP 2025) - not needed

## S028
- UTC: 2026-11-14T21:47:26Z
- Tool: WebSearch
- Query/URL: `"Does Sycophancy Change Decisions" CHI 2026`
- Results: 10
- Kept: no exact-title hit; Interaction Context Often Increases Sycophancy (arXiv 2509.12517, CHI 2026) and Too Polite to Disagree (2604.02668, SIGDIAL 2026) surfaced
- Dropped: econ working papers and press articles; lead title not confirmed -> unverified.md

## S029
- UTC: 2026-11-14T21:47:26Z
- Tool: WebSearch
- Query/URL: `LLM persuasion principles Cialdini compliance objectionable requests "Call me a jerk"`
- Results: 16
- Kept: Wharton GAIL report page https://gail.wharton.upenn.edu/research-and-insights/persuading-llms-objectionable-requests/ (Meincke et al., SSRN 5357179)
- Dropped: press/blog coverage, secondary

## S030
- UTC: 2026-11-14T21:47:26Z
- Tool: arXiv API https://export.arxiv.org/api/query
- Query/URL: `id_list=2509.12517,2604.02668`
- Results: 2
- Kept: Interaction Context Often Increases Sycophancy (CHI 2026); Too Polite to Disagree (SIGDIAL 2026)
- Dropped: -

## S031
- UTC: 2026-11-14T21:47:26Z
- Tool: arXiv API https://export.arxiv.org/api/query
- Query/URL: `ti:"How Johnny Can Persuade LLMs"`
- Results: 1
- Kept: PAP persuasion taxonomy (2401.06373)
- Dropped: -

## S032
- UTC: 2026-11-14T21:47:26Z
- Tool: arXiv API https://export.arxiv.org/api/query
- Query/URL: `abs:sycophancy AND (abs:preference OR abs:preferences OR abs:subjective OR abs:opinion) AND abs:pressure`
- Results: 15
- Kept: Claim Framing as a Driver (2610.18159); No Matter Who You Are: Addressivity (2610.25728, EMNLP 2026); Measuring Opinion Bias and Sycophancy via LLM-based Persuasion (2604.21564); Beyond Social Pressure: Epistemic Attack (2604.07749)
- Dropped: mechanistic/RL-mitigation/domain (healthcare, tutoring) papers lower priority; 2608.21377 is WITHDRAWN (noted in unverified.md)

## S033
- UTC: 2026-11-14T21:47:35Z
- Tool: WebSearch
- Query/URL: `LLM smart home assistant prompt injection attack thermostat device control study`
- Results: 10
- Kept: Invitation Is All You Need! Promptware vs Gemini (arXiv 2508.12175)
- Dropped: blogs/press coverage of the same work; secondary

## S034
- UTC: 2026-11-14T21:47:35Z
- Tool: WebSearch
- Query/URL: `LLM mediating conflicting requests multiple users group assistant whose preference wins assertive`
- Results: 10
- Kept: Multi-User LLM Agents (arXiv 2604.08567); arXiv 2503.12757 (to identify)
- Dropped: aggregator mirrors

## S035
- UTC: 2026-11-14T21:48:16Z
- Tool: arXiv API https://export.arxiv.org/api/query
- Query/URL: `id_list=2503.12757,2604.08567,2508.12175,2610.18159,2610.25728,2512.00332,2610.36346,2604.07749,2604.16275,2607.05554 (abstract metadata)`
- Results: 10
- Kept: all 10 retained as abstract-level or full-text candidates
- Dropped: -

## S036
- UTC: 2026-11-14T21:48:16Z
- Tool: arXiv API https://export.arxiv.org/api/query
- Query/URL: `abs:sycophancy AND (abs:"third-person" OR abs:"third person" OR abs:reframing OR abs:rephrasing OR abs:question)`
- Results: 15
- Kept: Ask don't tell (dup); Beacon (2510.16727); Social Sycophancy Scale (2603.15448); Why LLMs Give In medical (2608.01017, Findings EMNLP)
- Dropped: mechanistic, uncertainty, modality-specific (video/audio), Chinese factual - outside F

## S037
- UTC: 2026-11-14T21:48:16Z
- Tool: arXiv API https://export.arxiv.org/api/query
- Query/URL: `abs:LLM AND abs:"multi-party" AND (abs:assertive OR abs:assertiveness OR abs:dominant OR abs:loudest)`
- Results: 3
- Kept: none
- Dropped: all off-topic (privacy, MPC code, hallucination) -> negative evidence for Q3

## S038
- UTC: 2026-11-14T21:48:16Z
- Tool: arXiv API https://export.arxiv.org/api/query
- Query/URL: `abs:LLM AND (abs:"thermal comfort" OR abs:thermostat) AND (abs:"natural language" OR abs:occupant) AND (abs:request OR abs:requests OR abs:feedback)`
- Results: 2
- Kept: none for language-side review (OccuReward is building-control, left to p2a agent; recorded for Q3 context only)
- Dropped: polymer simulation off-topic

## S039
- UTC: 2026-11-14T21:48:16Z
- Tool: arXiv API https://export.arxiv.org/api/query
- Query/URL: `abs:sycophancy AND (abs:financial OR abs:monetary OR abs:cost OR abs:negotiation) AND abs:agent`
- Results: 9
- Kept: The Price of Agreement (2604.24668, ICLR 2026 FinAI workshop)
- Dropped: FinCom demo, OOM-RL, theory papers - no measured yielding cost

## S040
- UTC: 2026-11-14T21:48:16Z
- Tool: arXiv API https://export.arxiv.org/api/query
- Query/URL: `abs:"smart home" AND (abs:LLM OR abs:"language model") AND (abs:safety OR abs:attack OR abs:jailbreak)`
- Results: 15
- Kept: PromptShield Home (2608.05495, UbiComp 2026 poster); SafeOrchestrate (2611.09364)
- Dropped: ADL recognition, video anomaly, IoT intrusion detection, config repair - not manipulation of LLM controller

## S041
- UTC: 2026-11-14T21:53:56Z
- Tool: curl GitHub REST API + gh api; WebFetch github.com
- Query/URL: `repos/JiseungHong/SYCON-Bench ; repos/CHATS-lab/persuasive_jailbreaker (licence check)`
- Results: 0 (HTTP 403: GitHub access not enabled for session; WebFetch: URL not on allowlist)
- Kept: none
- Dropped: licences of GitHub-hosted stimulus sets could not be verified -> unverified.md

## S042
- UTC: 2026-11-14T21:56:13Z
- Tool: arXiv API https://export.arxiv.org/api/query
- Query/URL: `(abs:sycophancy OR abs:sycophantic OR abs:"over-compliance") AND (abs:energy OR abs:thermostat OR abs:HVAC OR abs:building OR abs:"cyber-physical" OR abs:robot)`
- Results: 20
- Kept: Conduct Under Pressure: 60 LMs (2609.25447); SyPS prompt sensitivity (2608.23837, Findings EMNLP 2026) - abstract-level only
- Dropped: no result concerns HVAC/thermostat/building/robot actions (matches are on 'building' in other senses, quadruped compliance control, steering) -> negative evidence for Q2

## S043
- UTC: 2026-11-14T21:56:13Z
- Tool: arXiv API https://export.arxiv.org/api/query
- Query/URL: `(abs:LLM OR abs:"language model") AND (abs:"group chat" OR abs:"multi-user" OR abs:"multiple users") AND (abs:conflict OR abs:conflicting) AND (abs:tone OR abs:persuasion OR abs:assertive OR abs:politeness OR abs:sycophancy)`
- Results: 0
- Kept: none
- Dropped: zero hits -> negative evidence for Q3

## S044
- UTC: 2026-11-14T21:56:13Z
- Tool: arXiv API https://export.arxiv.org/api/query
- Query/URL: `(abs:LLM OR abs:"language model") AND abs:urgency AND (abs:prompt OR abs:request) AND (abs:compliance OR abs:behavior OR abs:behaviour)`
- Results: ERROR HTTP 429
- Kept: none
- Dropped: rate-limited; retried as S045

## S045
- UTC: 2026-11-14T21:56:44Z
- Tool: arXiv API https://export.arxiv.org/api/query
- Query/URL: `(abs:LLM OR abs:"language model") AND abs:urgency AND (abs:prompt OR abs:request) AND (abs:compliance OR abs:behavior OR abs:behaviour)`
- Results: 14
- Kept: Do Influence Tactics Matter? prompt framing in code generation (2608.11513, Empirical Software Engineering 2026); Under Pressure: emotional framing in small LMs (2605.20202)
- Dropped: jailbreak tree search, child-risk benchmark, robotics flocking, evacuation, negotiation personas etc.: not phrasing-effect studies

## S046
- UTC: 2026-11-14T21:57:01Z
- Tool: arXiv API https://export.arxiv.org/api/query
- Query/URL: `id_list=2609.25447,2608.23837,2608.11513,2605.20202,2510.01395,2502.10844,2605.12991,2509.23055,2607.01071,2604.00478 (abstract metadata)`
- Results: 10
- Kept: all 10 retained at abstract level
- Dropped: -

## S047
- UTC: 2026-11-14T21:57:29Z
- Tool: Crossref REST https://api.crossref.org/works (query.bibliographic)
- Query/URL: `titles: Sycophantic AI decreases prosocial...; Be Friendly, Not Friends...; Interaction Context Often Increases Sycophancy in LLMs; Learning Multilingual Agentic Policy to Control Sycophancy`
- Results: 3 rows each
- Kept: Science 10.1126/science.aec8352 (2026); CHI 2026 10.1145/3772318.3791079; CHI 2026 10.1145/3772318.3791915; EACL 2026 10.18653/v1/2026.eacl-long.169; also noticed Findings EMNLP 2025 'Challenging the Evaluator: LLM Sycophancy Under User Rebuttal' (not pursued, budget)
- Dropped: unrelated title matches

## S048
- UTC: 2026-11-14T22:01:56Z
- Tool: arXiv API https://export.arxiv.org/api/query
- Query/URL: `id_list of 46 arXiv IDs used in index.csv/refs.bib (metadata only)`
- Results: 46
- Kept: metadata for all arXiv-hosted sources (authors, year, comment, journal_ref)
- Dropped: -

## S049
- UTC: 2026-11-14T22:01:57Z
- Tool: doi.org content negotiation (Accept: application/x-bibtex)
- Query/URL: `https://doi.org/10.1126/science.aec8352 ; 10.1145/3772318.3791079 ; 10.1145/3772318.3791915 ; 10.18653/v1/2026.eacl-long.169 ; 10.1073/pnas.2535868123`
- Results: 5
- Kept: BibTeX for Cheng (Science), Sun & Wang (CHI 26), Jain (CHI 26), Ranaldi & Pucci (EACL 26), Meincke (PNAS)
- Dropped: -

## S050
- UTC: 2026-11-14T22:01:57Z
- Tool: curl (page save)
- Query/URL: `https://aclanthology.org/2026.eacl-long.169/ ; https://gail.wharton.upenn.edu/research-and-insights/persuading-llms-objectionable-requests/`
- Results: 2
- Kept: ACL Anthology abstract page (P016); Wharton GAIL research summary of Meincke et al. PNAS 2026 (P039)
- Dropped: -

## S051
- UTC: 2026-11-14T22:02:44Z
- Tool: curl https://arxiv.org/pdf/<id> (full-text downloads, 3 s apart)
- Query/URL: `2602.23971 2610.08840 2609.09090 2505.23840 2502.08177 2310.13548 2610.18159 2401.06373 2604.08567 2604.24668 2610.36346 2512.00332 2604.16275 2603.06636`
- Results: 14
- Kept: P001-P014 full texts (times per file in sources/index.csv)
- Dropped: -

