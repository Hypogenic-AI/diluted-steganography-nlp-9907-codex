# Downloaded Datasets

This directory contains datasets for the diluted steganography project. Large data
files are kept out of git; download instructions and small sample files are
documented here.

## Dataset 1: WikiText-2 Raw

### Overview
- Source: Hugging Face `wikitext`, config `wikitext-2-raw-v1`
- Size: train 36,718, validation 3,760, test 4,358
- Format: Hugging Face DatasetDict
- Task: natural cover-text corpus for long-form hidden-signal injection and extraction
- Splits: train / validation / test
- Local path: `datasets/wikitext2/`

### Download Instructions

Using Hugging Face:

```python
from datasets import load_dataset
dataset = load_dataset("wikitext", "wikitext-2-raw-v1")
dataset.save_to_disk("datasets/wikitext2")
```

### Loading the Dataset

```python
from datasets import load_from_disk
dataset = load_from_disk("datasets/wikitext2")
```

### Sample Data

Saved sample: `datasets/samples/wikitext2_sample.json`

### Notes
- Useful for long-range, dispersed-message experiments because entries are longer than headline-style corpora.
- Some rows are empty separators; filter empty strings before experiment generation.

## Dataset 2: IMDB Reviews

### Overview
- Source: Hugging Face `imdb`
- Size: train 25,000, test 25,000, unsupervised 50,000
- Format: Hugging Face DatasetDict
- Task: long review text for carrier generation and perturbation studies
- Splits: train / test / unsupervised
- Local path: `datasets/imdb/`

### Download Instructions

```python
from datasets import load_dataset
dataset = load_dataset("imdb")
dataset.save_to_disk("datasets/imdb")
```

### Loading the Dataset

```python
from datasets import load_from_disk
dataset = load_from_disk("datasets/imdb")
```

### Sample Data

Saved sample: `datasets/samples/imdb_sample.json`

### Notes
- Matches one of the corpora used by `zero-shot-GLS`.
- Longer reviews are a good fit for diluted or keyword-triggered hiding schemes.

## Dataset 3: AG News

### Overview
- Source: Hugging Face `ag_news`
- Size: train 120,000, test 7,600
- Format: Hugging Face DatasetDict
- Task: short-form news text for compact cover-task and extraction experiments
- Splits: train / test
- Local path: `datasets/ag_news/`

### Download Instructions

```python
from datasets import load_dataset
dataset = load_dataset("ag_news")
dataset.save_to_disk("datasets/ag_news")
```

### Loading the Dataset

```python
from datasets import load_from_disk
dataset = load_from_disk("datasets/ag_news")
```

### Sample Data

Saved sample: `datasets/samples/ag_news_sample.json`

### Notes
- Useful as a short-context contrast set against WikiText-2 and IMDB.
- Supports experiments on whether dilution fails when available cover text is short.

## Dataset 4: LLM Steganalysis Benchmark

### Overview
- Source: copied from `code/Linguistic-Steganalysis-with-LLMs/data`
- Size: 59,994 text lines total
- Format: plain text files with paired `cover.txt` / `stego.txt`
- Task: labeled cover-vs-stego detection benchmark
- Subsets: `ac`, `adg`, `hc5`
- Local path: `datasets/llm_steganalysis_benchmark/`

### Download Instructions

If the repository is already cloned:

```bash
cp -r code/Linguistic-Steganalysis-with-LLMs/data datasets/llm_steganalysis_benchmark
```

### Loading the Dataset

```python
from pathlib import Path

base = Path("datasets/llm_steganalysis_benchmark")
cover_lines = (base / "ac" / "cover.txt").read_text().splitlines()
stego_lines = (base / "ac" / "stego.txt").read_text().splitlines()
```

### Sample Data

Use the first few lines from each `cover.txt` / `stego.txt` pair as a lightweight sample.

### Notes
- Best immediate labeled detection resource in the workspace.
- Useful for calibrating baseline steganalysis before evaluating diluted schemes.

## Selection Rationale

- `WikiText-2` and `IMDB` provide long text needed for dispersed-message placement.
- `AG News` adds short-form cover text to stress-test dilution under limited context.
- `llm_steganalysis_benchmark` provides ready-made labeled cover/stego data for detector baselines.
