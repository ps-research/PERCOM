# Search log — p1 tabular-foundation-model Wi-Fi localization

All times UTC (from the system clock via python datetime.utcnow, equivalent to `date -u`). Local-file reads are logged as searches so every source has a found_via entry.

### S001
- UTC: 2026-11-14T21:44:22Z
- Tool: local file read
- Query/URL: `/home/claude/percom-wip/papers/05-locaris-decoder-only-localization/text/full_blocks.md (+paper.pdf)`
- Results: 1
- Kept: Locaris PerCom WiP 2026 (DOI 10.1109/PerComWorkshops68308.2026.11585338)
- Dropped: n/a

### S002
- UTC: 2026-11-14T21:44:22Z
- Tool: local file read
- Query/URL: `/home/claude/percom-wip/papers/04-diffusion-transformers-radio-fingerprinting/text/full_blocks.md (+paper.pdf)`
- Results: 1
- Kept: DiT fingerprinting PerCom WiP 2026 (DOI 10.1109/PerComWorkshops68308.2026.11585359)
- Dropped: n/a

### S003
- UTC: 2026-11-14T21:44:22Z
- Tool: local file read
- Query/URL: `/home/claude/percom-wip/notes/percom-wip-2026-reading-notes.md`
- Results: 1 notes file
- Kept: used only as leads (not cited as evidence)
- Dropped: n/a

### S004
- UTC: 2026-11-14T21:44:22Z
- Tool: local file read
- Query/URL: `/home/claude/pilots/lit/idea1_a.json (earlier arXiv/OpenAlex dump: TabPFN x {localization,positioning,fingerprint,RSSI,wireless})`
- Results: arXiv: 19+21+2+0+0 titles; OpenAlex: all 5 queries returned HTTP 429
- Kept: none of the titles concerns RF localization; treated as evidence for Q1 negative only after re-running (see later entries)
- Dropped: all titles are TabPFN applications in other domains (medicine, finance, molecules, graphs, time series) or TabPFN methodology

### S005
- UTC: 2026-11-14T21:44:22Z
- Tool: local file read
- Query/URL: `/home/claude/pilots/loc/SOD/README.md and 'Description of the SODIndoorLoc dataset.pdf' and file listing`
- Results: 1 README + 1 PDF + 14 CSV names
- Kept: README and description PDF
- Dropped: n/a

### S006
- UTC: 2026-11-14T21:45:10Z
- Tool: arXiv API (curl)
- Query/URL: `https://export.arxiv.org/api/query?id_list=2510.11926,2605.13986,2606.30410,2606.01899,2606.11490,2410.00617,2207.01848,2605.10004`
- Results: 8
- Kept: all 8 (Locaris long 2510.11926; TabPFN-3 2605.13986; Beyond IID 2606.30410; RA-LWLM 2606.01899; OmniLoc 2606.11490; Radio Foundation Models 2410.00617; TabPFN 2207.01848; EnvCoLoc 2605.10004) — ID/title metadata check
- Dropped: none dropped

### S007
- UTC: 2026-11-14T21:45:10Z
- Tool: arXiv API (curl)
- Query/URL: `search_query=ti:WiFiGPT`
- Results: 0
- Kept: none
- Dropped: no arXiv title contains WiFiGPT

### S008
- UTC: 2026-11-14T21:45:10Z
- Tool: arXiv API (curl)
- Query/URL: `search_query=ti:TabICL`
- Results: 2
- Kept: TabICL: A Tabular Foundation Model for In-Context Learning on Large Data (http://arxiv.org/abs/2502.05564)
- Dropped: DP-TabICL (differential privacy variant, out of scope)

### S009
- UTC: 2026-11-14T21:45:10Z
- Tool: arXiv API (curl)
- Query/URL: `search_query=all:"decoder-only" AND all:WiFi AND all:localization`
- Results: 1
- Kept: Transforming Decoder-Only Transformers for Accurate WiFi-Telemetry Based Indoor Localization (http://arxiv.org/abs/2505.15835) — the WiFiGPT lead
- Dropped: none

### S010
- UTC: 2026-11-14T21:45:10Z
- Tool: arXiv API (curl), Q1 negative search
- Query/URL: `search_query=all:TabPFN AND (all:localization OR all:positioning OR all:RSSI OR all:fingerprint OR all:CSI OR all:wireless)`
- Results: 38
- Kept: none relevant to RF localization; titles recorded in the review (Q1)
- Dropped: all 38 are TabPFN in other domains or TabPFN methodology (e.g. geotechnics, graph node classification, Raman spectra, time series, cardinality estimation, clinical risk); 'fingerprint' matches are molecular fingerprints

### S011
- UTC: 2026-11-14T21:45:11Z
- Tool: arXiv API (curl), Q1 negative search
- Query/URL: `search_query=(all:"tabular foundation model" OR all:"prior-data fitted" OR all:TabICL) AND (all:localization OR all:positioning OR all:indoor OR all:RSSI OR all:WiFi OR all:Wi-Fi OR all:BLE OR all:cellular)`
- Results: 63 (first 50 inspected)
- Kept: none relevant to RF localization
- Dropped: matches on 'localization' are failure-center localization (HOLMES), 'localized' posterior estimation, robot policy learning, etc.; no Wi-Fi/BLE/cellular positioning paper

### S012
- UTC: 2026-11-14T21:45:28Z
- Tool: arXiv API (curl), Q1 negative search (continuation)
- Query/URL: `same query as S011, start=50`
- Results: 13 more (63 total)
- Kept: none relevant
- Dropped: matrix completion, time-series classification, concept drift, anomaly detection — no RF positioning

### S013
- UTC: 2026-11-14T21:45:28Z
- Tool: arXiv API (curl), cluster C
- Query/URL: `search_query=(all:"in-context learning" OR all:"foundation model") AND (all:"fingerprint" OR all:RSSI) AND (all:localization OR all:positioning)`
- Results: 18
- Kept: RA-LWLM (2606.01899); Radio Foundation Models (2410.00617); Multimodal Wireless Foundation Models (2511.15162, listing only)
- Dropped: 15 others are molecular/audio/website/model fingerprints or medical imaging

### S014
- UTC: 2026-11-14T21:46:56Z
- Tool: curl (publisher OA page)
- Query/URL: `https://satellite-navigation.springeropen.com/counter/pdf/10.1186/s43020-022-00086-y.pdf ; https://link.springer.com/content/pdf/10.1186/s43020-022-00086-y.pdf ; https://satellite-navigation.springeropen.com/articles/10.1186/s43020-022-00086-y`
- Results: PDF URLs: bot-check HTML page / HTTP 429; article HTML: 200 (full text)
- Kept: SODIndoorLoc dataset paper, full-text HTML (saved as P009)
- Dropped: PDF routes blocked; HTML full text used instead

### S015
- UTC: 2026-11-14T21:46:56Z
- Tool: curl (publisher OA page)
- Query/URL: `https://www.frontiersin.org/journals/signal-processing/articles/10.3389/frsip.2026.1884243/full`
- Results: 1 (200, full-text HTML)
- Kept: IndoorCART (saved as P010)
- Dropped: n/a

### S016
- UTC: 2026-11-14T21:48:18Z
- Tool: curl (publisher OA table pages)
- Query/URL: `https://satellite-navigation.springeropen.com/articles/10.1186/s43020-022-00086-y/tables/{11,12,13}`
- Results: 3 (200)
- Kept: Tables 11-13 of SODIndoorLoc paper (saved as P009_sodindoorloc_table11/12/13)
- Dropped: n/a

### S017
- UTC: 2026-11-14T21:52:30Z
- Tool: curl (Hugging Face API)
- Query/URL: `https://huggingface.co/api/models?author=Prior-Labs&limit=100 ; https://huggingface.co/api/models/Prior-Labs/<id> for 6 model ids`
- Results: 7 repos (TabPFN-v2-clf, TabPFN-v2-reg, tabpfn_2_5, tabpfn_2_6, tabpfn_3, tabpfn_3_5, demo)
- Kept: 6 model repos' metadata and LICENSE files (P011)
- Dropped: 'demo' repo not a model release

### S018
- UTC: 2026-11-14T21:52:30Z
- Tool: curl (Hugging Face API) + gh api
- Query/URL: `https://huggingface.co/api/models?author=jingang ; https://huggingface.co/api/models/jingang/{TabICL,TabICL-clf} ; gh api repos/soda-inria/tabicl`
- Results: 2 HF repos; gh api: HTTP 403 (GitHub access not enabled in this session)
- Kept: TabICL HF metadata (P012)
- Dropped: GitHub licence check blocked

### S019
- UTC: 2026-11-14T21:52:40Z
- Tool: curl (publisher OA page)
- Query/URL: `https://www.nature.com/articles/s41586-024-08328-6`
- Results: 1 (200, full-text HTML, CC BY 4.0)
- Kept: Hollmann et al., Nature 2025 TabPFN v2 (P013)
- Dropped: n/a

### S020
- UTC: 2026-11-14T21:53:16Z
- Tool: WebSearch
- Query/URL: `TabPFN indoor localization RSSI fingerprint`
- Results: 10
- Kept: none
- Dropped: all 10 are generic RSSI/BLE fingerprinting papers or patents; none mention TabPFN

### S021
- UTC: 2026-11-14T21:53:16Z
- Tool: WebSearch
- Query/URL: `"tabular foundation model" Wi-Fi positioning OR localization OR fingerprinting`
- Results: 10
- Kept: RA-LWLM (arXiv 2606.01899); LWLM (Chalmers listing); OmniLoc (2606.11490); arXiv 2602.04016 (title unknown, checked in S0xx)
- Dropped: patents, LinkedIn, mirror sites; none applies a tabular foundation model to localization

### S022
- UTC: 2026-11-14T21:53:16Z
- Tool: Consensus search (page_size 50)
- Query/URL: `TabPFN prior-data fitted network indoor localization positioning RSSI CSI fingerprint`
- Results: 50
- Kept: WiFiGPT (2505.15835), Locaris (PerCom W 2026), Smart Cities 2025 review (Zholamanov et al.), Singh et al. IEEE Access 2021 overview
- Dropped: no result mentions TabPFN, PFN or tabular foundation models (0 text matches); rest are generic CNN/CSI/RSSI localization papers

### S023
- UTC: 2026-11-14T21:53:16Z
- Tool: Consensus search
- Query/URL: `few-shot meta-learning WiFi fingerprint indoor localization new environment`
- Results: rate-limit error
- Kept: none
- Dropped: retried later (see following entry)

### S024
- UTC: 2026-11-14T21:53:16Z
- Tool: Consensus search (page_size 20)
- Query/URL: `WiFi fingerprint localization robustness missing access points device heterogeneity`
- Results: 20
- Kept: CR-AP (Sci. Rep. 2026, SODIndoorLoc + AP-missing); SSD (Hossain et al., IEEE TMC 2011); Park et al. INFOCOM 2011 device diversity; Laoudias et al. IPIN 2014; Singh et al. 2021 overview
- Dropped: others are niche methods not needed for a 4-page paper

### S025
- UTC: 2026-11-14T21:53:42Z
- Tool: OpenAlex API (curl)
- Query/URL: `https://api.openalex.org/works?search=TabPFN%20localization ; ?search=tabular%20foundation%20model%20positioning%20RSSI ; ?filter=doi:10.1038/s41586-024-08328-6 (to list citing works)`
- Results: HTTP 429 on all three (free daily budget for the shared IP exhausted)
- Kept: none
- Dropped: blocked

### S026
- UTC: 2026-11-14T21:53:42Z
- Tool: Semantic Scholar Graph API (curl)
- Query/URL: `https://api.semanticscholar.org/graph/v1/paper/search?query=TabPFN+localization ; ?query=TabPFN+indoor+positioning+RSSI`
- Results: HTTP 429 on both
- Kept: none
- Dropped: blocked (no API key; not creating an account per spec)

### S027
- UTC: 2026-11-14T21:53:54Z
- Tool: WebSearch (extended)
- Query/URL: `TabPFN "indoor positioning" OR "Wi-Fi fingerprinting" OR "BLE" OR "CSI localization" in-context learning`
- Results: 10
- Kept: GenMetaLoc (arXiv 2503.18078) as cluster-B lead
- Dropped: none mentions TabPFN; generic CSI/RSSI localization and surveys

### S028
- UTC: 2026-11-14T21:53:54Z
- Tool: WebSearch
- Query/URL: `TabPFN cellular positioning OR "UE localization" OR "radio map" OR "RSRP" regression`
- Results: 10
- Kept: none
- Dropped: 5G positioning / radio-map papers and patents without TabPFN

### S029
- UTC: 2026-11-14T21:55:25Z
- Tool: arXiv API (curl)
- Query/URL: `id_list=2602.04016,2503.18078 ; ti:MetaLoc ; ti:FeMLoc ; ti:"Learning to Locate" ; ti:"Large Wireless Localization Model" ; then id_list=2606.01899,2606.11490,2410.00617,2605.10004,2503.18078,2211.04258,2405.11079,2505.10134,2207.01848 (abstracts)`
- Results: 2602.04016 = multi-modal wireless FM (not localization-specific, dropped); MetaLoc 3 hits; FeMLoc 1; 'Learning to Locate' empty response (HTTP 429 interval); LWLM 1; abstracts 9
- Kept: abstracts saved as P015-P022 (OmniLoc, Radio FM, EnvCoLoc, GenMetaLoc, MetaLoc, FeMLoc, LWLM, TabPFN v1)
- Dropped: Bayesian-Boosted MetaLoc and MetaLocalization (RIS) out of scope

### S030
- UTC: 2026-11-14T21:57:50Z
- Tool: curl (publisher/repository pages)
- Query/URL: `https://www.mdpi.com/1424-8220/23/20/8458 ; https://www.mdpi.com/2624-6511/8/5/153 ; https://www.nature.com/articles/s41598-026-59813-z ; https://zenodo.org/api/records/11558791 ; https://doi.org/10.1016/j.dib.2024.110356 ; https://ieeexplore.ieee.org/document/9531555 ; https://archive.ics.uci.edu/dataset/422/wireless+indoor+localization`
- Results: MDPI x2: HTTP 403; Sci. Rep. CR-AP: 200 full text; Zenodo: 200; Elsevier DOI: redirect stub only; IEEE Xplore: 202 empty; UCI: 200
- Kept: CR-AP full text (P023); Zenodo record (P024); UCI page (P037)
- Dropped: MDPI/Elsevier/IEEE pages not retrievable; abstracts taken from Consensus records instead

### S031
- UTC: 2026-11-14T21:57:50Z
- Tool: Crossref API (curl, query.bibliographic, rows=3)
- Query/URL: `16 title queries (few-shot Sensors 2023; LESS; MetaLoc; FeMLoc; Singh 2021; Smart Cities 2025; RADAR; Horus; Ferris GP; UJIIndoorLoc; TUJI1; Feng RSS-RTT; CR-AP; SSD; Park 2011; UCI dataset)`
- Results: 48 records (3 per query)
- Kept: DOIs for 15 items (see refs.bib); UCI dataset DOI taken from the UCI page instead
- Dropped: non-matching records in each top-3

### S032
- UTC: 2026-11-14T21:57:50Z
- Tool: Consensus search (page_size 25)
- Query/URL: `few-shot learning WiFi fingerprinting indoor positioning meta-learning Learning to Locate`
- Results: 25
- Kept: Few-Shot Learning for WiFi Fingerprinting Indoor Positioning (Sensors 2023); MetaLoc (JSAC 2023); LESS (TWC 2023); EnvCoLoc; GenMetaLoc; FeMLoc (IoT-J 2024)
- Dropped: CSI device-free and cell-free variants (Jiao, Wei, Zheng, Foliadis) are further examples of the same meta-learning pattern; not needed

### S033
- UTC: 2026-11-14T21:57:50Z
- Tool: Consensus search (page_size 20)
- Query/URL: `RADAR in-building RF-based user location tracking; Horus WLAN location determination; Gaussian processes signal strength location estimation`
- Results: 19
- Kept: RADAR (INFOCOM); Horus (MobiSys 2005); Ferris et al. GP (RSS 2006)
- Dropped: later/derivative works and surveys

### S034
- UTC: 2026-11-14T21:57:50Z
- Tool: Consensus search (page_size 15)
- Query/URL: `UJIIndoorLoc multi-building multi-floor database WLAN fingerprint; TUJI1 multi-device dataset high measurement density; WiFi RSS-RTT dynamic model switching`
- Results: 15
- Kept: UJIIndoorLoc (IPIN 2014); TUJI1 (Data in Brief 2024); Feng et al. J-ISPIN 2024; SODIndoorLoc (confirms venue); Feng et al. IEEE Access 2024 dataset review (listing only)
- Dropped: method papers evaluated on UJIIndoorLoc

### S035
- UTC: 2026-11-14T21:59:14Z
- Tool: arXiv API (curl)
- Query/URL: `ti:"TabPFN-2.5" ; ti:TabICLv2 ; id_list=2511.08667,2602.11139`
- Results: 1 ; 2 ; 2
- Kept: TabPFN-2.5 report (2511.08667) and TabICLv2 (2602.11139) abstracts (P038, P039)
- Dropped: Localized TabICLv2 (k-NN context selection) — listing only, noted as possible tool

