# REPORT: Diluted Steganography

## 1. Executive Summary
This study tested whether current LLMs can still detect and recover hidden messages when the signal is diluted across long passages instead of encoded in obvious local patterns. Using real OpenAI API models on a controlled benchmark built from `WikiText-2`, `IMDB`, and `AG News`, I compared acrostic encoding, dense keyword-trigger encoding, and diluted keyword-trigger encoding.

The main result is consistent across both tested models: extraction degrades sharply under dilution, while detection degrades more slowly. `gpt-4.1` achieved exact recovery rates of `0.67` on acrostics, `0.75` on dense keyword encoding, and `0.25` on diluted keyword encoding. `gpt-5` showed the same ordering at `0.58`, `0.50`, and `0.17`. This supports the core hypothesis that diluted steganographic signals remain materially harder for LLMs to recover than obvious or denser schemes.

Practically, this means current LLM-based monitors may still notice suspicious structure without reliably extracting the payload once the signal is sparse, dispersed, and mixed with ordinary text. That gap matters for both misuse analysis and robustness evaluation as synthetic text generation scales.

## 2. Research Question & Motivation

### Research question
How well do current LLMs detect and extract steganographic messages when the hidden signal is diluted from obvious acrostics to sparse keyword-conditioned rules embedded in natural cover text?

### Why this matters
Prior work on linguistic steganography has focused mostly on dense generation schemes, edit-based hiding, and cover-vs-stego classification. The literature review in this workspace identified a specific gap: no benchmark explicitly isolates signal dilution while separating detection from extraction. That gap matters because large-scale synthetic text makes sparse hidden signaling more feasible and harder to audit.

## 3. Literature Review Summary
The pre-gathered literature converged on three points:

1. Modern linguistic steganography is good at preserving fluency and reducing obvious statistical artifacts.
2. LLMs can outperform older classifiers in some steganalysis settings, but those evaluations usually target dense or structurally simple schemes.
3. Recent frontier-model safety work suggests current models have limited covert capability on subtle tasks, but does not directly test diluted keyword-conditioned extraction.

This project contributes a benchmark that explicitly sweeps density and context rather than testing only obvious schemes or generic cover-vs-stego detection.

## 4. Methodology

### Benchmark design
I generated a synthetic benchmark from three local corpora:
- `WikiText-2` for long, multi-sentence encyclopedia-like cover passages.
- `IMDB` for long review text.
- `AG News` for shorter news passages.

For each corpus, I created:
- `acrostic`: first letter of each sentence encodes a six-letter secret.
- `keyword_dense`: first letter of the word immediately after exact token `signal` encodes the secret.
- `keyword_diluted`: the same `signal` rule, but spread across a much longer passage with distractor variants like `signals` and `signal-based`.

Each condition included matched negative controls. The main evaluation used `4` positive and `4` negative examples per corpus-condition cell, for `72` synthetic examples total. I also ran a small external sanity check on `24` examples from `datasets/llm_steganalysis_benchmark`, though that probe turned out not to be informative with a generic prompt.

### Models and prompts
Real API models were used throughout:
- `gpt-4.1`
- `gpt-5`

Two prompt types were used:
- Detection prompt: decide whether a passage hides a message under either candidate scheme.
- Extraction prompt: return the six-letter message or `NONE`.

Exact prompt texts are saved in `prompts/`.

### Metrics
- Detection: accuracy, precision, recall, F1.
- Extraction: exact six-letter recovery rate and character-level accuracy.
- Uncertainty: bootstrap 95% confidence intervals.
- Pairwise comparison: Fisher exact tests on pooled exact-recovery counts.

### Environment and hardware
- Python `3.12.8`
- GPUs available: `4 x NVIDIA RTX A6000`, but unused because this was API-based research
- Core libraries: `openai`, `datasets`, `pandas`, `numpy`, `scipy`, `matplotlib`, `seaborn`, `scikit-learn`

### Cost tracking
Observed token usage:
- `gpt-4.1`: `40,446` input tokens, `3,968` output tokens
- `gpt-5`: `40,314` input tokens, `5,460` output tokens

Using official OpenAI pricing accessed on 2026-04-19:
- `gpt-5`: `$1.25 / 1M` input tokens and `$10.00 / 1M` output tokens
- `gpt-4.1`: `$2.00 / 1M` input tokens and `$8.00 / 1M` output tokens

Estimated run cost:
- `gpt-4.1`: about `$0.1126`
- `gpt-5`: about `$0.1050`
- Total: about `$0.2176`

One implementation detail mattered: `gpt-5` initially consumed the output budget with reasoning tokens when run at `reasoning.effort="low"`. During validation I switched to `reasoning.effort="minimal"` and updated the cache key so the final results reflect complete JSON answers rather than truncated responses.

## 5. Results

### Main pooled results

| Model | Scheme | Detection Accuracy | Exact Recovery | Character Accuracy |
|---|---:|---:|---:|---:|
| `gpt-4.1` | acrostic | 0.875 | 0.667 | 0.861 |
| `gpt-4.1` | keyword_dense | 0.917 | 0.750 | 0.958 |
| `gpt-4.1` | keyword_diluted | 0.792 | 0.250 | 0.597 |
| `gpt-5` | acrostic | 0.958 | 0.583 | 0.875 |
| `gpt-5` | keyword_dense | 0.792 | 0.500 | 0.889 |
| `gpt-5` | keyword_diluted | 0.750 | 0.167 | 0.486 |

The main pattern is stable across both models: diluted extraction is much worse than obvious or dense extraction.

### Statistical comparisons

| Model | Comparison | Rate A | Rate B | Delta | Fisher p-value |
|---|---|---:|---:|---:|---:|
| `gpt-4.1` | acrostic vs diluted | 0.667 | 0.250 | 0.417 | 0.0995 |
| `gpt-4.1` | dense vs diluted | 0.750 | 0.250 | 0.500 | 0.0391 |
| `gpt-5` | acrostic vs diluted | 0.583 | 0.167 | 0.417 | 0.0894 |
| `gpt-5` | dense vs diluted | 0.500 | 0.167 | 0.333 | 0.1930 |

The strongest confirmatory result is for `gpt-4.1`, where dense keyword extraction significantly outperformed diluted extraction at this sample size.

### Corpus effects

Selected exact-recovery rates by corpus:

| Model | Corpus | Acrostic | Dense | Diluted |
|---|---|---:|---:|---:|
| `gpt-4.1` | `ag_news` | 0.50 | 0.50 | 0.25 |
| `gpt-4.1` | `imdb` | 0.50 | 0.75 | 0.00 |
| `gpt-4.1` | `wikitext2` | 1.00 | 1.00 | 0.50 |
| `gpt-5` | `ag_news` | 0.75 | 0.25 | 0.25 |
| `gpt-5` | `imdb` | 0.25 | 0.75 | 0.25 |
| `gpt-5` | `wikitext2` | 0.75 | 0.50 | 0.00 |

Longer context did not uniformly help. `gpt-4.1` benefited from `WikiText-2` on the obvious and dense settings, but both models still struggled on diluted cases. `gpt-5` in particular dropped to `0.00` exact recovery on diluted `WikiText-2`.

### Figures
- [detection_accuracy_by_scheme.png](/workspaces/diluted-steganography-nlp-9907-codex/figures/detection_accuracy_by_scheme.png)
- [extraction_exact_by_scheme.png](/workspaces/diluted-steganography-nlp-9907-codex/figures/extraction_exact_by_scheme.png)
- [extraction_heatmap.png](/workspaces/diluted-steganography-nlp-9907-codex/figures/extraction_heatmap.png)

### Output locations
- Raw benchmark and model outputs: `results/raw/`
- Aggregate summaries: `results/processed/`
- Environment snapshot: [environment.json](/workspaces/diluted-steganography-nlp-9907-codex/results/processed/environment.json)

## 6. Analysis & Discussion

### What the results show
The hypothesis is supported. Both models handled obvious and denser schemes materially better than diluted ones, and detection remained stronger than exact payload extraction. That means the main failure mode under dilution is not total blindness to anomalous structure; it is incomplete recovery of the actual secret.

### Model comparison
`gpt-4.1` was more reliable than `gpt-5` on this benchmark. The largest gap appears on dense and diluted extraction, where `gpt-4.1` kept higher exact and character-level recovery. `gpt-5` still often detected hidden structure, but degraded more in exact recovery. This may reflect prompt sensitivity or the interaction between reasoning-model behavior and constrained JSON extraction.

### Error taxonomy
The dominant failure modes were:
- False negatives on diluted passages, often returning `NONE`.
- Near-miss decodes with one-letter substitutions or transpositions, such as `PRAIRA`, `QUARRY`, `EMBERB`, and `NELBUL`.
- Greater brittleness on longer diluted passages, especially when distractor variants were present.

Representative failures are saved in [extraction_failures.csv](/workspaces/diluted-steganography-nlp-9907-codex/results/processed/extraction_failures.csv).

### External benchmark sanity check
Both models scored about chance on the small external steganalysis slice. I do not treat that as evidence that they cannot detect steganography in general; it is more likely that the generic prompt was poorly aligned to those short benchmark examples, whereas the main benchmark supplied the specific candidate schemes. This external result is therefore a limitation, not part of the main claim.

## 7. Limitations
- Sample size is modest: `12` positive examples per scheme per model in the main extraction analysis.
- The benchmark is synthetic even though it is grounded in real corpora; results may differ for organically generated covert text.
- Only two candidate schemes were exposed to the model, so this is a constrained extraction study rather than an open-ended steganalysis benchmark.
- The negative controls are matched clean examples, not an exhaustive distribution of natural text.
- API behavior mattered enough to require validation fixes for `gpt-5`; model-comparison conclusions should therefore be interpreted as prompt-and-API specific.

## 8. Conclusions & Next Steps
Current LLMs can often detect or decode obvious and moderately dense textual steganography, but their performance drops sharply when the same signal is diluted across longer passages with sparse trigger locations. In this experiment, both `gpt-4.1` and `gpt-5` showed that diluted extraction is substantially less reliable than acrostic or dense keyword extraction, supporting the central research hypothesis.

The most useful next experiments are:
- Increase sample size to tighten confidence intervals.
- Test more providers and model families under matched prompts.
- Vary trigger ambiguity and message length separately from passage length.
- Add paraphrase and edit attacks that preserve semantics while perturbing adjacency.
- Compare candidate-scheme-aware prompting to fully open-ended steganalysis.

## 9. Validation Notes
- The final pipeline was rerun after the API fixes and then rerun again from cache.
- The cached validation rerun completed in about `14s`, confirming reproducible artifact generation without fresh API calls.
- Random seeds are fixed in the script, and all outputs are written to stable project-relative paths.

## 10. References
- Ueoka et al. 2021. *Frustratingly Easy Edit-based Linguistic Steganography with a Masked Language Model*.
- Zhang et al. 2021. *Provably Secure Generative Linguistic Steganography*.
- Yi et al. 2021. *Exploiting Language Model for Efficient Linguistic Steganalysis*.
- Raj-Sankar and Rajagopalan. 2023. *Hiding in Plain Sight: Towards the Science of Linguistic Steganography*.
- Lin et al. 2024. *Zero-shot Generative Linguistic Steganography*.
- Wu et al. 2024. *Generative Text Steganography with Large Language Model*.
- Bai et al. 2024. *Towards Next-Generation Steganalysis: LLMs Unleash the Power of Detecting Steganography*.
- Perry et al. 2025. *Robust Steganography from Large Language Models*.
- Karpov et al. 2025. *The Steganographic Potentials of Language Models*.
- Zolkowski et al. 2025. *Early Signs of Steganographic Capabilities in Frontier LLMs*.
- OpenAI pricing page: `https://openai.com/api/pricing/`
- OpenAI model pages: `https://developers.openai.com/api/docs/models/gpt-5`, `https://developers.openai.com/api/docs/models/gpt-4.1`
