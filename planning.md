# Diluted Steganography Research Plan

## Motivation & Novelty Assessment

### Why This Research Matters
As synthetic text generation scales, hidden signals can be embedded at much lower density and with less obvious local structure, making traditional pattern-based monitoring less reliable. Measuring whether current LLMs can still detect or recover these diluted signals matters for both misuse prevention and robustness evaluation of model-based monitors.

### Gap in Existing Work
The literature review shows strong prior work on dense generative steganography, edit-based local encodings, and cover-vs-stego detection, but no benchmark that explicitly sweeps signal dilution while separating detection from message recovery. Existing frontier-model safety studies focus on obvious schemes, coordinated hiding, or hidden reasoning rather than sparse keyword-conditioned extraction across realistic cover text.

### Our Novel Contribution
We introduce a controlled benchmark for diluted textual steganography that varies carrier corpus, signal density, trigger frequency, and distractor rate while keeping the secret message and cover text distribution explicit. We test current frontier LLMs on two separate capabilities: deciding whether hidden structure exists and extracting the payload when the encoding rule ranges from obvious acrostics to dispersed keyword-triggered schemes.

### Experiment Justification
- Experiment 1: Measure extraction accuracy across encoding schemes to test whether performance falls sharply as the signal becomes more diluted.
- Experiment 2: Measure binary detection accuracy separately from extraction to determine whether models can sense hidden structure without being able to decode it.
- Experiment 3: Compare long-context and short-context cover corpora to test whether more carrier text helps or hurts diluted-signal recovery.
- Experiment 4: Add distractor triggers and light paraphrastic noise to check whether any observed capability is brittle or robust.

## Research Question
How well do current LLMs detect and extract steganographic messages when the hidden signal is progressively diluted from obvious acrostic patterns to sparse keyword-conditioned rules embedded in natural cover text?

## Background and Motivation
Prior work establishes that linguistic steganography can be highly fluent and difficult to detect, and recent papers show that LLMs are strong steganalyzers in some regimes. What remains unclear is whether those capabilities extend to low-density signals where the extraction rule is indirect, sparse, and mixed with distractors. This study targets that gap with a benchmark that isolates dilution as the primary independent variable.

## Hypothesis Decomposition
- H1: Extraction accuracy will be high for obvious encodings such as acrostics and dense keyword-next-token rules.
- H2: Extraction accuracy will drop significantly for diluted keyword-triggered schemes with distractor triggers and larger spacing.
- H3: Detection accuracy will degrade more slowly than extraction accuracy, meaning models may suspect hidden structure before they can decode it.
- H4: Long carrier texts will improve diluted extraction only up to a point; beyond that, longer context may increase distraction and reduce recovery reliability.
- H5: Light paraphrase-style corruption will disproportionately damage diluted schemes relative to obvious ones.

Independent variables:
- Encoding scheme: `acrostic`, `keyword_dense`, `keyword_diluted`
- Corpus: `wikitext2`, `imdb`, `ag_news`
- Difficulty: trigger spacing, distractor rate, optional noise
- Model: frontier LLM API condition

Dependent variables:
- Exact message recovery rate
- Character-level recovery rate
- Binary detection accuracy / F1
- Response latency, token usage, and estimated API cost

Alternative explanations to check:
- Failures may come from prompt ambiguity rather than inability
- Short-context degradation may reflect insufficient carrier capacity
- Detection success may reflect stylistic oddities introduced by synthesis rather than true steganalysis

## Proposed Methodology

### Approach
Build a synthetic but corpus-grounded benchmark from local datasets, inject hidden messages with controlled rules, and query real LLMs with fixed prompts for both extraction and detection. This approach is preferable to training new detectors because the research question concerns present-day LLM capability under realistic black-box usage, and it allows direct comparison between obvious and diluted encodings under matched conditions.

### Experimental Steps
1. Load locally available corpora and filter for usable cover passages with enough tokens for the target payload length.
2. Generate benchmark instances with three schemes:
   - `acrostic`: first letter of each sentence forms the payload.
   - `keyword_dense`: the token immediately following each trigger keyword forms the payload, with no distractors.
   - `keyword_diluted`: payload tokens occur only after selected trigger appearances, mixed with distractor triggers and variable gaps.
3. Create paired control examples from the same carrier texts with no payload but matched formatting and trigger distribution.
4. Query real LLMs with one extraction prompt and one detection prompt per example.
5. Score exact recovery, partial recovery, and detection metrics; compute confidence intervals and pairwise significance tests.
6. Run robustness checks with light noising on a subset of examples.

### Baselines
- Random-chance detection and extraction baselines.
- Rule-aware oracle decoders for each scheme to validate the benchmark labels.
- Obvious-pattern baseline: acrostic extraction.
- Dense keyword baseline: keyword-next-token extraction without dilution.
- Optional external detection sanity check: a small sample from `datasets/llm_steganalysis_benchmark`.

### Evaluation Metrics
- Exact recovery rate: proportion of examples where the full secret string is recovered exactly.
- Character recovery rate: normalized character accuracy between prediction and target.
- Detection accuracy, precision, recall, and F1 on hidden-vs-clean classification.
- Bootstrap 95% confidence intervals for the main rates.
- McNemar tests for paired detection comparisons and permutation or bootstrap tests for recovery differences.

### Statistical Analysis Plan
- Significance level: `alpha = 0.05`.
- Use bootstrap confidence intervals for message-recovery rates and character accuracy.
- Use two-sided permutation tests for differences in recovery between encoding conditions within the same model.
- Use McNemar tests for paired detection outcomes on matched examples.
- Report effect sizes as absolute percentage-point differences and odds ratios where appropriate.

## Expected Outcomes
Support for the hypothesis would look like near-ceiling performance on `acrostic`, moderate performance on `keyword_dense`, and a substantial drop on `keyword_diluted`, especially with distractors and noise. A weaker version of the hypothesis would be supported if detection remains above chance while extraction collapses under dilution.

## Timeline and Milestones
1. Resource review and planning: completed first.
2. Environment and dependency setup: minimal API/data/stats stack only.
3. Data pipeline and benchmark generation.
4. API harness and validation on a small sample.
5. Full experiment run and results collection.
6. Statistical analysis, figures, and documentation.

## Potential Challenges
- API schema or model availability may differ from assumptions.
  Mitigation: implement a provider wrapper and validate with a tiny smoke test before scaling.
- Benchmark synthesis may accidentally leak cues not related to steganography.
  Mitigation: build matched non-stego controls with similar trigger density and formatting.
- Prompt sensitivity may dominate results.
  Mitigation: keep prompts fixed and simple, and document them exactly.
- Cost or latency may become excessive.
  Mitigation: cap sample sizes to a statistically useful but tractable benchmark and cache every response.

## Success Criteria
- A reproducible benchmark is generated from local corpora and saved with metadata.
- At least one real frontier LLM is evaluated on both detection and extraction.
- Results show a quantified relationship between signal dilution and model performance.
- Statistical uncertainty, failure cases, and limitations are documented clearly in `REPORT.md`.
