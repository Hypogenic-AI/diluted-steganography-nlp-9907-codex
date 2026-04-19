# Dilution Breaks Extraction Before Detection

## Title
- Dilution Breaks Extraction Before Detection: Evaluating LLM Steganalysis on Sparse Keyword Signals

## Abstract
- Motivate diluted textual steganography as a monitoring problem for synthetic text.
- State gap: prior work studies dense generation, local edits, or cover-vs-stego detection, not density sweeps with separate detection and extraction tasks.
- Describe benchmark: 72 synthetic examples across WikiText-2, IMDB, AG News; acrostic, keyword-dense, keyword-diluted; matched negatives; GPT-4.1 and GPT-5.
- Preview main results with quantitative values and significance result for GPT-4.1 dense vs diluted.
- End with significance: monitors may detect suspicious structure without recovering payloads.

## Introduction
- Hook: low-density hidden signaling is the harder and more realistic regime for monitor evaluation.
- Importance: synthetic text scaling makes sparse covert channels plausible.
- Gap: no benchmark isolates dilution while separating detection from extraction.
- Approach: corpus-grounded benchmark that sweeps acrostic, dense keyword, diluted keyword.
- Quantitative preview: GPT-4.1 exact recovery 0.75 to 0.25 from dense to diluted; GPT-5 0.50 to 0.17.
- Contributions:
  - introduce benchmark and task split
  - evaluate frontier OpenAI models under fixed prompts
  - analyze corpus effects and failure modes
  - document practical implication for LLM monitors

## Related Work
- Theme 1: generative and edit-based linguistic steganography (Ueoka, Zhang, Lin, Wu, Raj-Sankar).
- Theme 2: steganalysis and LLM-as-detector work (Yi, Bai).
- Theme 3: frontier-model covert capability and robustness studies (Perry, Karpov, Zolkowski).
- Positioning sentence at end of each paragraph tying back to dilution-specific gap.

## Methodology
- Define detection and extraction tasks.
- Describe corpora and synthetic generation scheme.
- Detail benchmark counts: 4 positive and 4 negative examples per corpus-scheme cell; 72 synthetic main examples plus 24 external sanity examples.
- Describe prompts and models.
- Metrics: detection accuracy/precision/recall/F1; extraction exact recovery and character accuracy; bootstrap CIs; Fisher exact tests.
- Implementation details: Python/packages, API usage, reasoning-effort fix for GPT-5, cost accounting.

## Results
- Table 1: pooled detection and extraction results by model and scheme.
- Table 2: Fisher exact comparisons.
- Table 3: corpus-level exact recovery.
- Figure 1: detection accuracy by scheme.
- Figure 2: exact recovery by scheme.
- Figure 3: extraction heatmap across corpora.
- Narrative:
  - detection degrades slower than extraction
  - diluted keyword is consistently hardest
  - GPT-4.1 stronger than GPT-5 on extraction
  - context length does not uniformly help
  - external benchmark sanity check near chance, treated as non-confirmatory

## Discussion
- Interpret detection/extraction gap.
- Discuss error taxonomy using examples: NONE outputs, near-miss decodes, brittleness under long diluted passages.
- Limitations: small sample, synthetic benchmark, constrained candidate schemes, clean negatives, API-specific behavior.
- Broader implications: monitoring may need stronger search/oracle components than current prompted LLMs alone.

## Conclusion
- Summarize benchmark and main finding.
- Emphasize dilution reduces exact extraction materially before detection collapses.
- Future work: more models, larger sample, open-ended prompting, noise/paraphrase tests.

## Evidence Mapping
- Report table values from REPORT.md and results/processed/*.csv.
- Figures from figures/*.png copied into paper_draft/figures/.
- Cost and environment details from results/processed/environment.json and report notes.

