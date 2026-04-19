# Cloned Repositories

This file documents repositories gathered for baselines, tooling, or evaluation.

## Repo 1: zero-shot-GLS
- URL: `https://github.com/leonardodalinky/zero-shot-GLS`
- Purpose: official implementation of Zero-shot Generative Linguistic Steganography
- Location: `code/zero-shot-GLS/`
- Key files: `README.md`, `datasets/README.md`, `scripts/`, `evaluate/`
- Notes: uses IMDB and Twitter datasets; strongest readily available modern generative baseline in this workspace.

## Repo 2: steganography-with-masked-lm
- URL: `https://github.com/ku-nlp/steganography-with-masked-lm`
- Purpose: edit-based steganography using a masked language model
- Location: `code/steganography-with-masked-lm/`
- Key files: `README.md`, `main.py`, `requirements.txt`
- Notes: very lightweight baseline; easy to adapt for token- or keyword-local hiding/extraction experiments.

## Repo 3: lm-steganography
- URL: `https://github.com/falcondai/lm-steganography`
- Purpose: classic patient-Huffman generative steganography baseline from ACL 2019
- Location: `code/lm-steganography/`
- Key files: `core.py`, `example.ipynb`, `entropy.ipynb`, `samples/`
- Notes: useful historical baseline; README explicitly notes brittleness under active edits, which is relevant to diluted-signal robustness.

## Repo 4: Linguistic-Steganalysis-with-LLMs
- URL: `https://github.com/ba0z1/Linguistic-Steganalysis-with-LLMs`
- Purpose: LLM-based detector for steganographic text
- Location: `code/Linguistic-Steganalysis-with-LLMs/`
- Key files: `README.md`, `LMforANA.py`, `configs/`, `data/`
- Notes: includes labeled `cover.txt` / `stego.txt` files for `ac`, `adg`, and `hc5`; model weights are external and GPU-oriented, so code inspection is more useful than execution in this phase.
