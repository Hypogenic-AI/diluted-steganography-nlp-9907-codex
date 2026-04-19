# Literature Review: Diluted Steganography

## Review Scope

### Research Question
How well do current large language models detect or extract diluted
steganographic signals in text, especially when the hidden message is spread
across dispersed positions rather than encoded in obvious local patterns?

### Inclusion Criteria
- Papers on linguistic steganography, text watermarking, hidden message detection, or covert communication in LLM outputs
- Papers on LLM reasoning or extraction over dispersed or multi-hop textual signals
- Papers introducing benchmarks, datasets, or evaluation methods relevant to hidden signal recovery in text
- Papers from 2019-2026, with preference for 2023-2026 for LLM-specific work

### Exclusion Criteria
- Purely image/audio steganography papers without transferable text methods
- Security papers unrelated to natural-language hidden signal detection or extraction
- Opinion pieces or blog posts without technical details

### Time Frame
2019-2026

### Sources
- Paper-finder service
- arXiv
- Semantic Scholar
- Papers with Code
- GitHub

## Search Log

| Date | Query | Source | Results | Notes |
|------|-------|--------|---------|-------|
| 2026-04-19 | `linguistic steganography large language models hidden message detection extraction` | paper-finder | service unavailable | fell back to manual search |
| 2026-04-19 | `text steganography keyword-based hidden message extraction NLP` | paper-finder | service unavailable | fell back to manual search |
| 2026-04-19 | broad searches on linguistic steganography, LLM steganography, steganalysis | arXiv / ACL Anthology / GitHub / Papers with Code | 10 papers selected | focused on papers with methods, code, or benchmarks |

## Screening Results

| Paper | Title Screen | Abstract Screen | Full-Text | Notes |
|-------|-------------|-----------------|-----------|-------|
| 2104.09833 | Include | Include | Include | edit-based baseline with masked LM |
| 2021.findings-acl.268 | Include | Include | Include | formal generative security baseline |
| 2107.12168 | Include | Include | Include | classical steganalysis baseline |
| 2312.16840 | Include | Include | Include | useful conceptual framework |
| 2403.10856 | Include | Include | Deep read | strongest practical modern linguistic baseline |
| 2404.10229 | Include | Include | Include | black-box GPT-4/UI method; keyword-set design is relevant |
| 2405.09090 | Include | Include | Include | LLM-based detection baseline |
| 2504.08977 | Include | Include | Deep read | robustness to edits and paraphrases |
| 2505.03439 | Include | Include | Include | frontier-model safety framing |
| 2507.02737 | Include | Include | Deep read | closest direct match to hypothesis |

## Paper Summaries

### Research Area Overview

The literature splits into three threads. First, classic linguistic steganography focuses on encoding payload bits into generated or edited text while preserving fluency and low detectability. Second, newer LLM-based work uses zero-shot prompting or black-box APIs to improve text quality and capacity. Third, recent safety work asks whether frontier LLMs themselves can intentionally hide or recover messages and whether monitors can catch them. The exact question in this project, detecting or extracting **diluted** signals where evidence is spread across many positions, is still largely open. Existing work mostly studies obvious local encodings, whole-text generative schemes, or broad monitor-evasion settings rather than sparse keyword-triggered extraction.

### Key Papers

#### Frustratingly Easy Edit-based Linguistic Steganography with a Masked Language Model
- **Authors**: Ueoka, Murawaki, Kurohashi
- **Year**: 2021
- **Source**: NAACL 2021
- **Key Contribution**: Revives edit-based steganography using a masked LM instead of handcrafted rules.
- **Methodology**: Masks every `f`-th token subject to skip rules, then selects replacements from MLM candidates to encode bits.
- **Datasets Used**: Real text corpus for evaluation; paper emphasizes natural text and crowd evaluation rather than synthetic-only metrics.
- **Results**: Lower payload than GPT-2 generation baselines, but much harder for automatic detectors to distinguish; human quality close to real texts.
- **Code Available**: Yes, `code/steganography-with-masked-lm/`
- **Relevance to Our Research**: Very relevant as a baseline for localized and sparse placement strategies. A diluted scheme can be seen as a more dispersed edit schedule.

#### Provably Secure Generative Linguistic Steganography
- **Authors**: Zhang, Yang, Yang, Huang
- **Year**: 2021
- **Source**: Findings of ACL 2021
- **Key Contribution**: Introduces ADG, a provably secure generative method based on adaptive dynamic grouping.
- **Methodology**: Recursively groups candidate tokens under a language model and maps secret bits to groups.
- **Datasets Used**: Three public corpora.
- **Results**: Strong statistical security and high embedding capacity compared with prior generative methods.
- **Code Available**: Not collected here.
- **Relevance to Our Research**: Good baseline for “obvious” generative stego against which diluted extraction can be compared.

#### Exploiting Language Model for Efficient Linguistic Steganalysis
- **Authors**: Yi, Wu, Feng, Zhang
- **Year**: 2021
- **Source**: arXiv
- **Key Contribution**: Shows that language-model pretraining improves steganalysis over standard RNN/CNN/GNN classifiers.
- **Methodology**: Pre-trains LM-RNN and AE-RNN steganalyzers, then fine-tunes for cover-vs-stego detection.
- **Datasets Used**: Twitter and movie-review corpora with Bins, FLC, and VLC generation methods.
- **Results**: Best or near-best accuracy/F1 across most settings; gains are strongest when the detector captures token-distribution artifacts.
- **Code Available**: No repository downloaded for this paper.
- **Relevance to Our Research**: Important detection baseline. Diluted signals may reduce exactly the local distributional artifacts these models exploit.

#### Hiding in Plain Sight: Towards the Science of Linguistic Steganography
- **Authors**: Raj-Sankar, Rajagopalan
- **Year**: 2023
- **Source**: arXiv
- **Key Contribution**: Provides a useful conceptual framework built around decodability, density, and detectability.
- **Methodology**: Formalizes code design and illustrates a practical tweet-oriented construction.
- **Datasets Used**: Tweet-style communication setting.
- **Results**: Mostly conceptual, but valuable for defining measurable trade-offs.
- **Code Available**: Not collected here.
- **Relevance to Our Research**: Especially useful because dilution is directly related to code density. The hypothesis can be cast as lowering density while preserving decodability.

#### Zero-shot Generative Linguistic Steganography
- **Authors**: Lin, Luo, Zhang, Luo
- **Year**: 2024
- **Source**: NAACL 2024
- **Key Contribution**: Uses in-context learning to improve both statistical and perceptual imperceptibility without task-specific training.
- **Methodology**: Edge-flipping coding plus in-context stegotext generation guided by cover-style examples.
- **Datasets Used**: IMDB and Twitter.
- **Baselines**: NLS, SAAC, ADG, RNN-Stega, VAE-Stega.
- **Results**: Best combined readability and detectability trade-off among compared methods; reports lower steganalysis accuracy than competitors and `1.926x` better language-evaluation preference.
- **Code Available**: Yes, `code/zero-shot-GLS/`
- **Relevance to Our Research**: Strongest practical baseline for current linguistic steganography. Its evaluation setup and datasets are directly reusable.

#### Generative Text Steganography with Large Language Model
- **Authors**: Wu, Wu, Xue, Wen, Peng
- **Year**: 2024
- **Source**: ACM MM 2024
- **Key Contribution**: Proposes `LLM-Stega`, a black-box GPT-4/UI method that does not require direct vocabulary or logit access.
- **Methodology**: Constructs a keyword set, encrypted mapping, and reject-sampling mechanism over GPT-4 outputs.
- **Datasets Used**: Entertainment news and science-fiction movie-review themes; compares to News-trained baselines.
- **Baselines**: Arithmetic, ADG, Discop.
- **Results**: Highest reported embedding capacity in its setting (`5.93 bpw` on one theme) with better text quality than several baselines.
- **Code Available**: No official repository collected.
- **Relevance to Our Research**: Highly relevant because keyword-set design is close to the proposed dispersed keyword-trigger idea.

#### Towards Next-Generation Steganalysis: LLMs Unleash the Power of Detecting Steganography
- **Authors**: Bai, Yang, Pang, Wang, Huang
- **Year**: 2024
- **Source**: arXiv
- **Key Contribution**: Reframes steganalysis as an LLM generation problem instead of a narrow classifier.
- **Methodology**: Uses generative LLMs as detectors and compares them to classical baselines.
- **Datasets Used**: Multiple steganography settings; code repo includes `ac`, `adg`, and `hc5` cover/stego files.
- **Results**: LLM-based detectors outperform older baselines by a wide margin in their setting.
- **Code Available**: Yes, `code/Linguistic-Steganalysis-with-LLMs/`
- **Relevance to Our Research**: Directly supports the experiment hypothesis, because detection/extraction by current LLMs is the main object of study.

#### Robust Steganography from Large Language Models
- **Authors**: Perry, Gupte, Pitta, Rotem
- **Year**: 2025
- **Source**: arXiv
- **Key Contribution**: Introduces weak/local and strong/semantic robustness definitions for LLM steganography.
- **Methodology**: Two constructions: watermarking-style local robustness and embedding/LSH-based semantic robustness; evaluated under n-gram shuffling, synonym substitution, and paraphrasing.
- **Datasets Used**: Authors release implementation and datasets; attack suite is central to the paper.
- **Results**: Embedding-based method is much more robust than watermarking under paraphrase-style attacks, but does not spread bits uniformly across the text.
- **Code Available**: Paper says yes, but repository was not directly identified here.
- **Relevance to Our Research**: Important for understanding whether diluted signals are robust to mild edits or paraphrases.

#### The Steganographic Potentials of Language Models
- **Authors**: Karpov, Adeleke, Cho, Perez-Campanero
- **Year**: 2025
- **Source**: ICLR 2025 workshop
- **Key Contribution**: Evaluates frontier-model covert communication and hidden reasoning, including RL fine-tuning to increase stealth.
- **Methodology**: Direct steganography, synonym-substitution prompting, coordination experiments, and indirect game-like collusion scenarios.
- **Datasets Used**: Wikinews during fine-tuning; synthetic payload sets.
- **Results**: Current models show rudimentary but non-trivial covert ability; coordination and explicit algorithms improve undetected accuracy.
- **Code Available**: Project page only; no repository collected.
- **Relevance to Our Research**: Closely tied to whether models can exploit dispersed structure when instructed or fine-tuned.

#### Early Signs of Steganographic Capabilities in Frontier LLMs
- **Authors**: Zolkowski, Nishimura-Gasparian, McCarthy, Zimmermann, Lindner
- **Year**: 2025
- **Source**: arXiv
- **Key Contribution**: Systematic evaluation of frontier LLMs on encoded message passing and encoded reasoning.
- **Methodology**: Tests coordination/no-coordination, common/uncommon schemes, hidden tasks including state tracking, AQuA-RAT, and GPQA-Diamond, and monitor-based detection.
- **Datasets Used**: State-tracking tasks plus benchmark reasoning datasets.
- **Results**: Without strong affordances, current models generally fail to hide messages past monitors; with unmonitored CoT and coordination, they can sometimes succeed. Hidden reasoning is nascent and strongest on simple state-tracking.
- **Code Available**: Paper reports transcripts release; no code repository gathered.
- **Relevance to Our Research**: The most direct evidence that current LLMs are still limited at subtle covert communication, which suggests diluted extraction may be a sensitive capability probe.

## Themes and Synthesis

### Common Methodologies
- **Generative token-level encoding**: ADG, NLS, SAAC, patient-Huffman, and Zero-shot GLS all encode bits by steering next-token selection.
- **Edit-based local encoding**: masked-LM steganography modifies existing text, which is conceptually closer to sparse or keyword-anchored hiding.
- **LLM black-box prompting**: LLM-Stega shows that direct logit access is not necessary; keyword sets and constrained prompting can still carry payloads.
- **LLM-as-detector**: recent steganalysis papers use LLMs as generative judges or tuned detectors rather than classical discriminators.
- **Safety-style evaluation**: recent 2025 work measures monitor evasion and hidden reasoning rather than only capacity and perplexity.

### Standard Baselines
- Generative baselines: NLS, SAAC, ADG, patient-Huffman, Arithmetic coding, Discop.
- Edit baseline: masked-LM substitution method.
- Detection baselines: RNN/CNN/GNN steganalyzers, LM-RNN / AE-RNN, and LLM-based steganalyzers.
- For this project specifically, a good baseline ladder is:
  - Obvious acrostic or every-`k`th-token extraction
  - Keyword-next-word extraction
  - Diluted keyword-next-word extraction with variable spacing and distractors
  - LLM-based extraction/detection vs non-LLM detectors

### Evaluation Metrics
- **Capacity / bits per word (BPW)**: common in generation papers; useful for comparing dense vs diluted schemes.
- **Perplexity (PPL)**: rough fluency proxy.
- **Jensen-Shannon divergence (JSD)** and related distributional scores: common statistical imperceptibility metric.
- **Steganalysis accuracy / F1 / AUC**: for cover-vs-stego detection.
- **Extraction accuracy**: proportion of hidden payload recovered exactly or at token/bit level.
- **Monitor-pass rate / undetected success**: central for frontier LLM studies.

### Datasets in the Literature
- IMDB and Twitter are common for linguistic steganography generation.
- News-style corpora appear in black-box LLM steganography work.
- Reasoning benchmarks like AQuA-RAT and GPQA-Diamond appear in frontier hidden-reasoning work.
- There is no standard benchmark specifically for **diluted** textual steganography where the signal is deliberately dispersed and sparse.

## Research Gaps

- Existing papers mostly evaluate dense or structurally simple encodings; they do not isolate the effect of **signal dilution**.
- LLM steganalysis papers study cover-vs-stego classification, but not whether an LLM can recover a payload when the extraction rule is indirect and spread across long context.
- Frontier safety papers test simple known schemes, coordination, and hidden reasoning, but not dispersed keyword-conditioned extraction over realistic text corpora.
- There is no shared benchmark varying signal density, trigger frequency, distractor frequency, and cover-text length in a controlled way.
- Robustness under paraphrase or light editing has been studied for generated schemes, but not for rule-based diluted encodings of the form “word after each trigger.”

## Gaps and Opportunities

- **Gap 1**: No benchmark explicitly sweeps message density.  
  Opportunity: generate synthetic cover/stego pairs on `WikiText-2`, `IMDB`, and `AG News` with exact density control.
- **Gap 2**: Detection and extraction are usually conflated.  
  Opportunity: evaluate both “is there a hidden signal?” and “recover the message” as separate tasks.
- **Gap 3**: Little evidence on current LLMs as extractors of sparse dispersed signals.  
  Opportunity: compare prompted frontier/open models, small local models, and non-LLM detectors.
- **Gap 4**: Sparse triggers interact with cover length.  
  Opportunity: explicitly vary short-form vs long-form cover text.

## Key Citations

- Dai and Cai, 2019. *Towards Near-imperceptible Steganographic Text.*
- Ueoka et al., 2021. *Frustratingly Easy Edit-based Linguistic Steganography with a Masked Language Model.*
- Zhang et al., 2021. *Provably Secure Generative Linguistic Steganography.*
- Lin et al., 2024. *Zero-shot Generative Linguistic Steganography.*
- Wu et al., 2024. *Generative Text Steganography with Large Language Model.*
- Bai et al., 2024. *Towards Next-Generation Steganalysis: LLMs Unleash the Power of Detecting Steganography.*
- Perry et al., 2025. *Robust Steganography from Large Language Models.*
- Zolkowski et al., 2025. *Early Signs of Steganographic Capabilities in Frontier LLMs.*

## Recommendations for Our Experiment

Based on the literature review:
- **Recommended datasets**: `WikiText-2` and `IMDB` as primary long-form carriers; `AG News` as a short-form contrast set; `llm_steganalysis_benchmark` for baseline detector sanity checks.
- **Recommended baselines**: acrostic / every-`k`th-token extraction, masked-LM edit baseline, zero-shot generative baseline, LLM-based steganalysis baseline.
- **Recommended metrics**: hidden-message exact match, token-level extraction accuracy, detection accuracy/F1/AUC, perplexity, and success-under-paraphrase.
- **Methodological considerations**:
  - Sweep density explicitly: triggers every 2, 4, 8, 16, 32 candidate positions.
  - Separate known-scheme from unknown-scheme evaluation.
  - Compare direct extraction prompts against step-by-step reasoning prompts.
  - Include distractor triggers and paraphrased cover text to test robustness.
  - Record both human-obvious and statistically subtle schemes so the “dilution” effect is interpretable.

## Key Citations
