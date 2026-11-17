# Prompt for the designer session: Fig. 1 (overview), PERCOM paper 1

You are designing Fig. 1 of a 4-page IEEE conference paper (PerCom 2027, Work-in-Progress track, two-column IEEE format). Build it in Adobe Illustrator as a flat, professional vector figure. It sits at the top of the right column on page 1, so it is one column wide. Read this whole brief before drawing. Every word and number in the figure must come from this brief; do not add any.

## What the figure must say at a glance

A tabular foundation model localizes a phone from a building's Wi-Fi survey with no training, and keeps its accuracy when access points go missing, while trained localizers must be trained again for every building and degrade.

The paper's title: "Tabular Foundation Models as Training-Free Wi-Fi Fingerprint Localizers Robust to Missing Access Points".

## Background you need (do not put this text in the figure)

- **Wi-Fi fingerprinting.** A building is surveyed: at many known spots (reference points) a phone records how strongly it hears each Wi-Fi access point. The survey is a table: one row per scan, one column per access point, each cell a signal strength. An access point that is not heard leaves the cell empty. A new scan from a phone is located by comparing it with the survey; the output is a 2-D position (x, y).
- **Trained localizers (the usual way).** Six baselines (k-nearest neighbours, random forest, LightGBM, support vector regression, multilayer perceptron, Gaussian process) are trained and tuned on each building's survey. Recent work fine-tunes a language model instead. Either way, every new building needs its own training.
- **Our way.** A tabular foundation model (two of them: TabPFN v2 and TabICLv2) was pretrained once on synthetic tables. We give it the survey as context and the new scan as the query; it returns (x, y) in one forward pass. Its weights stay frozen: no training, no tuning. An access point the phone does not hear is passed as a missing value.
- **The stress test.** After the survey, access points go missing from later scans. The inset (provided, see below) shows mean positioning error as 0 to 60% of access points go missing: our two models stay low; the tuned baselines climb.

## Canvas, type and colour (hard rules)

- **Artboard width: exactly 3.5 in (252 pt).** Height 2.4 to 2.7 in. Trim to the content with at most 2 pt of margin.
- **Font: Times New Roman for every label** (the IEEE template's rule), **8 pt or larger at this size.** Nothing smaller than 8 pt anywhere. Region titles 8 pt bold; all other labels 8 pt regular.
- **Colours: only these, exact hex.**
  - TabPFN v2 `#2a78d6` (blue), TabICLv2 `#eb6834` (orange): these two colours mean "ours" everywhere in the figure.
  - Ink `#1d1d1b` (text, icons), dark grey `#52514e` (outlines), grey `#9a9893` (trained-localizer lane, arrows of that lane).
  - Lane fills, very light: trained lane `#f2f1ee`, our lane `#eaf2fb`. White background.
- Flat vector only: no gradients, shadows, glows, 3-D, or textures. Strokes 0.5 pt or heavier.
- No em dashes anywhere. No sentences in the figure: every label is a few words. No figure title and no caption inside the figure (the caption is set in LaTeX).
- Icons, if used, are simple flat line icons in ink: a Wi-Fi access point, a phone, a building, a gear, a lock. No brains, robots, hands, people, or other metaphors.

## Layout (recommended; keep the logic if you improve the composition)

```
+-------------------------------------------------------------+
| [Wi-Fi survey]   | Trained localizers (grey lane)            |
|  grid of cells   |  --> [gear] Train and tune --> (x, y)     |
|  some blank      |        loop arrow over 3 building icons   |
|  sizes list      |        "repeated for every building"      |
|                  |-------------------------------------------|
|                  | Training-free localization (ours) (blue)  |
|                  |  --context--> [Tabular foundation model]  |
|                  |  [New scan] --query--^   (lock) --> (x,y) |
+-------------------------------------------------------------+
| Access points missing after the survey                       |
|  [inset_plot.pdf]            [inset_legend.pdf]              |
+-------------------------------------------------------------+
```

1. **Left: the survey, shared by both lanes.** A small table glyph (about 6 rows by 8 columns of cells), with roughly one cell in six left blank. Thin arrows leave it to the right into both lanes. Under it, the three real survey sizes (see the strings).
2. **Top lane, trained localizers, all in greys.** The survey arrow enters a box with a gear: "Train and tune", with "6 tuned baselines" and "or fine-tune a language model" under it. A loop arrow around three small building icons carries "repeated for every building". The lane ends at "(x, y)".
3. **Bottom lane, our way, in blue and orange.** The survey arrow, labelled "context", enters the box "Tabular foundation model". Below it, a "New scan" glyph (a single row of cells, two of them blank, with a small phone icon) sends an arrow labelled "query" up into the same box. Inside the box: "TabPFN v2 · TabICLv2" (write "TabPFN v2" in blue and "TabICLv2" in orange), "pretrained on synthetic tables", and a lock icon with "frozen: no training, no tuning". An arrow labelled "one forward pass" leads to "(x, y)".
4. **Bottom row: the stress test.** Region title "Access points missing after the survey". Place `inset_plot.pdf` and `inset_legend.pdf` side by side.
5. **Tags.** A small rounded pill "C1" on the corner of the "Tabular foundation model" box and a pill "C2" by the stress-test title, ink text on white with a 0.5 pt ink outline. Put both pills on their own layer named `tags` so they can be switched off.

**The contrast is the point of the figure.** The top lane should look visibly heavier and more repetitive (gear, loop, three buildings); the bottom lane one clean, straight path in our colours. The inset then closes the story: our blue and orange lines stay low while the grey band climbs. Charge the figure through this contrast, never through decoration or metaphor.

## The provided inset (do not redraw)

Files, next to this prompt:
- `inset_plot.pdf` (also `.svg`): the chart, already at print size (1.62 x 1.20 in) in Times-metric type at 8 pt.
- `inset_legend.pdf` (also `.svg`): its legend (1.80 x 0.78 in).
- `inset_values.csv`: the values plotted, for your reference only.

Place both at **100 % scale**. Do not redraw, recolour, restyle, crop the axes, or scale them unevenly; every number in them is computed from the experiment files. If space forces a change, stop and report instead of editing them.

## Every text string in the figure (use exactly these)

| Where | Text |
|---|---|
| Survey title | Wi-Fi survey |
| Above the grid columns | access points |
| Beside the grid rows | reference points |
| Under the grid | blank cell: not heard |
| Sizes header | scans × access points |
| Sizes, line 1 | CETC331: 955 × 52 |
| Sizes, line 2 | HCXY: 11,370 × 347 |
| Sizes, line 3 | SYL: 8,880 × 363 |
| Top lane title | Trained localizers |
| Top box | Train and tune |
| Top box, line 2 | 6 tuned baselines |
| Top box, line 3 | or fine-tune a language model |
| Loop arrow | repeated for every building |
| Top lane output | (x, y) |
| Bottom lane title | Training-free localization (ours) |
| Arrow from survey | context |
| Query glyph | New scan |
| Under the query glyph | blank: missing value |
| Arrow from new scan | query |
| Model box title | Tabular foundation model |
| Model box, line 2 | TabPFN v2 · TabICLv2 |
| Model box, line 3 | pretrained on synthetic tables |
| By the lock icon | frozen: no training, no tuning |
| Arrow to output | one forward pass |
| Bottom lane output | (x, y) |
| Stress-test title | Access points missing after the survey |
| Tags | C1, C2 |

The three sizes are the real surveys of the three buildings (scans by access points). Do not add any other number.

## Deliver

1. `fig1_overview.ai` (source, layers named, `tags` layer separate).
2. `fig1_overview.pdf`: vector, artboard 3.5 in wide, all fonts embedded (if embedding fails, convert text to outlines and say so).
3. `fig1_overview.png`: 600 dpi preview.
4. `texts.txt`: every text string as it appears in the figure, one per line.

## Check before you hand it back

- Zoom to 400 %: nothing overlaps, no label touches a line or the inset, arrows meet their boxes.
- No text below 8 pt; every label in Times New Roman; strings match the table above exactly.
- The inset is at 100 % and unedited; colours are only the listed hex values.
- No em dashes, no sentences, no title or caption inside the figure.
