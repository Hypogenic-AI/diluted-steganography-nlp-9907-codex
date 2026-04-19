# Diluted Steganography

This project evaluates whether real frontier LLMs can detect and recover hidden messages when the signal is progressively diluted inside natural cover text. The benchmark is built from local `WikiText-2`, `IMDB`, and `AG News` passages and compares obvious acrostics, dense keyword-trigger schemes, and diluted keyword-trigger schemes.

Key findings:
- Both tested models degraded sharply on diluted extraction relative to obvious or dense schemes.
- `gpt-4.1` was strongest overall on exact extraction: `0.67` acrostic, `0.75` dense keyword, `0.25` diluted keyword.
- `gpt-5` showed the same direction of degradation: `0.58`, `0.50`, and `0.17` exact recovery.
- Detection degraded less than extraction, especially for `gpt-5`, which often flagged diluted examples without decoding them reliably.
- Long context did not reliably solve dilution; `WikiText-2` diluted cases were still brittle, especially for `gpt-5`.

Full details are in [REPORT.md](/workspaces/diluted-steganography-nlp-9907-codex/REPORT.md).

## Reproduce

```bash
source .venv/bin/activate
python src/run_diluted_steg_experiment.py
```

This uses the workspace-local virtual environment, queries the OpenAI API with real models, writes raw outputs to `results/raw/`, summaries to `results/processed/`, and figures to `figures/`.

## File Structure

- `planning.md`: research plan and hypothesis decomposition.
- `src/run_diluted_steg_experiment.py`: benchmark generation, API evaluation, analysis, and plotting pipeline.
- `prompts/`: exact prompts used for detection and extraction.
- `results/raw/`: benchmark instances, cached API responses, and raw model outputs.
- `results/processed/`: aggregate metrics, environment snapshot, comparisons, and failure cases.
- `figures/`: exported plots used in the report.
- `REPORT.md`: full research report with results and limitations.
