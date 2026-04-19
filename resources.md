# Resources Catalog

## Summary

This document catalogs papers, datasets, and code repositories gathered for the
Diluted Steganography project.

### Papers
Total papers downloaded: 10

| Title | Authors | Year | File | Key Info |
|-------|---------|------|------|----------|
| Frustratingly Easy Edit-based Linguistic Steganography with a Masked Language Model | Ueoka et al. | 2021 | `papers/2104.09833_ueoka_masked_lm_steganography.pdf` | edit-based baseline |
| Provably Secure Generative Linguistic Steganography | Zhang et al. | 2021 | `papers/2021_findings_acl_provably_secure_generative_linguistic_steganography.pdf` | formal generative baseline |
| Exploiting Language Model for Efficient Linguistic Steganalysis | Yi et al. | 2021 | `papers/2107.12168_exploiting_language_model_for_efficient_linguistic_steganalysis.pdf` | classical detector baseline |
| Hiding in Plain Sight: Towards the Science of Linguistic Steganography | Raj-Sankar and Rajagopalan | 2023 | `papers/2312.16840_hiding_in_plain_sight_linguistic_steganography.pdf` | density/detectability framing |
| Zero-shot Generative Linguistic Steganography | Lin et al. | 2024 | `papers/2403.10856_zero_shot_generative_linguistic_steganography.pdf` | strong modern generation baseline |
| Generative Text Steganography with Large Language Model | Wu et al. | 2024 | `papers/2404.10229_generative_text_steganography_with_llm.pdf` | black-box GPT-4 method |
| Towards Next-Generation Steganalysis: LLMs Unleash the Power of Detecting Steganography | Bai et al. | 2024 | `papers/2405.09090_llms_unleash_power_detecting_steganography.pdf` | LLM steganalysis baseline |
| Robust Steganography from Large Language Models | Perry et al. | 2025 | `papers/2504.08977_robust_steganography_from_llms.pdf` | robustness to edits/paraphrase |
| The Steganographic Potentials of Language Models | Karpov et al. | 2025 | `papers/2505.03439_steganographic_potentials_of_language_models.pdf` | safety framing for covert communication |
| Early Signs of Steganographic Capabilities in Frontier LLMs | Zolkowski et al. | 2025 | `papers/2507.02737_early_signs_steganographic_capabilities_frontier_llms.pdf` | direct evidence on current LLM capabilities |

See `papers/README.md` for detailed descriptions.

### Datasets
Total datasets downloaded: 4

| Name | Source | Size | Task | Location | Notes |
|------|--------|------|------|----------|-------|
| WikiText-2 Raw | Hugging Face | 44,836 rows total | long-form cover text | `datasets/wikitext2/` | good for dispersed trigger experiments |
| IMDB | Hugging Face | 100,000 rows total | long reviews / cover text | `datasets/imdb/` | used by prior stego work |
| AG News | Hugging Face | 127,600 rows total | short-form cover text | `datasets/ag_news/` | stress-test short contexts |
| LLM Steganalysis Benchmark | cloned repo data | 59,994 lines | labeled cover-vs-stego detection | `datasets/llm_steganalysis_benchmark/` | `ac`, `adg`, `hc5` subsets |

See `datasets/README.md` for download instructions and loading notes.

### Code Repositories
Total repositories cloned: 4

| Name | URL | Purpose | Location | Notes |
|------|-----|---------|----------|-------|
| zero-shot-GLS | `github.com/leonardodalinky/zero-shot-GLS` | official zero-shot linguistic stego implementation | `code/zero-shot-GLS/` | uses IMDB/Twitter; evaluation scripts included |
| steganography-with-masked-lm | `github.com/ku-nlp/steganography-with-masked-lm` | edit-based MLM stego | `code/steganography-with-masked-lm/` | easy lightweight baseline |
| lm-steganography | `github.com/falcondai/lm-steganography` | patient-Huffman ACL 2019 baseline | `code/lm-steganography/` | classic generative approach |
| Linguistic-Steganalysis-with-LLMs | `github.com/ba0z1/Linguistic-Steganalysis-with-LLMs` | LLM-based detector | `code/Linguistic-Steganalysis-with-LLMs/` | includes labeled data, heavier model deps |

See `code/README.md` for details.

## Resource Gathering Notes

### Search Strategy

- Began with `paper-finder`, but the local service was unavailable.
- Fell back to manual arXiv, ACL Anthology, project pages, Papers with Code, and GitHub searches.
- Prioritized papers that were one of:
  - direct linguistic steganography baselines,
  - LLM-specific steganography methods,
  - steganalysis / detection methods,
  - frontier-model capability evaluations.

### Selection Criteria

- Direct relevance to hidden-message generation, detection, or extraction in text.
- Preference for papers with code, reproducible benchmarks, or clear datasets.
- Included both foundational and recent 2024-2025 work to cover method history and current frontier-model behavior.

### Challenges Encountered

- `paper-finder` did not respond locally, so discovery had to be manual.
- Some recent papers had project pages but no easily discoverable public code repositories.
- One intended Hugging Face dataset (`daily_dialog`) was not loadable with the installed `datasets` version because its legacy dataset script is no longer supported.

### Gaps and Workarounds

- No standard benchmark exists for **diluted** linguistic steganography.  
  Workaround: collect long-form cover-text corpora and a labeled steganalysis benchmark so the next phase can synthesize controlled diluted-signal data.
- Some frontier-model papers release transcripts or project pages rather than runnable code.  
  Workaround: retain the papers and gather adjacent open-source baselines that can be executed locally.

## Recommendations for Experiment Design

1. **Primary dataset(s)**: Use `WikiText-2` and `IMDB` as the main carrier corpora, with `AG News` as a short-context control.
2. **Baseline methods**: Compare obvious acrostic / every-`k`th-token schemes, masked-LM edit stego, zero-shot generative stego, and LLM-based steganalysis.
3. **Evaluation metrics**: Measure both detection and extraction separately; include exact-message recovery, token-level accuracy, detection F1/AUC, and robustness after paraphrase.
4. **Code to adapt/reuse**: Start from `code/steganography-with-masked-lm/` for sparse edit rules, `code/zero-shot-GLS/` for modern generative baselines, and `code/Linguistic-Steganalysis-with-LLMs/` for detector structure and benchmark format.

## Research Execution Notes

- Executed benchmark pipeline: `src/run_diluted_steg_experiment.py`
- Final prompts saved in `prompts/`
- Raw outputs saved in `results/raw/`
- Aggregate metrics saved in `results/processed/`
- Final write-up saved in `REPORT.md`

### Final executed setup
- Models: `gpt-4.1`, `gpt-5`
- Main corpora: `WikiText-2`, `IMDB`, `AG News`
- Schemes tested: `acrostic`, `keyword_dense`, `keyword_diluted`
- Main finding: both models degrade materially on diluted extraction relative to obvious or dense schemes
