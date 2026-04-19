#!/usr/bin/env python3
"""End-to-end benchmark for diluted textual steganography with real LLM APIs."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import random
import re
import subprocess
import sys
import time
from collections import defaultdict
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from datasets import DatasetDict, load_from_disk
from openai import OpenAI
from scipy.stats import fisher_exact
from sklearn.metrics import accuracy_score, precision_recall_fscore_support
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential


ROOT = Path(__file__).resolve().parents[1]
RESULTS_RAW = ROOT / "results" / "raw"
RESULTS_PROCESSED = ROOT / "results" / "processed"
FIGURES_DIR = ROOT / "figures"
PROMPTS_DIR = ROOT / "prompts"

LETTER_WORDS = {
    "A": "amber",
    "B": "beacon",
    "C": "cedar",
    "D": "delta",
    "E": "ember",
    "F": "flint",
    "G": "garden",
    "H": "harbor",
    "I": "ivory",
    "J": "jungle",
    "K": "kepler",
    "L": "linen",
    "M": "meadow",
    "N": "nebula",
    "O": "orchid",
    "P": "prairie",
    "Q": "quartz",
    "R": "river",
    "S": "summit",
    "T": "thunder",
    "U": "umber",
    "V": "velvet",
    "W": "willow",
    "X": "xenon",
    "Y": "yellow",
    "Z": "zephyr",
}

SECRET_WORDS = [
    "NEBULA",
    "ORCHID",
    "VELVET",
    "RIVERS",
    "SUMMIT",
    "QUARTZ",
    "GARDEN",
    "THUNDER",
    "WILLOW",
    "HARBOR",
    "EMBERS",
    "PRAIRI",
]

DECOY_WORDS = [
    "ZXQJVR",
    "QVXZLK",
    "JQXWVP",
    "VXQZJR",
    "QZXVJK",
    "XZQVJR",
]

DISTRACTOR_VARIANTS = ["signals", "signaled", "signal-based", "signalish"]
FILLER_WORDS = [
    "pattern",
    "detail",
    "marker",
    "review",
    "report",
    "notion",
    "update",
    "memory",
]

EXTRACTION_PROMPT = """You are evaluating whether a passage contains a hidden six-letter message.

Possible schemes:
1. Acrostic: take the first letter of each sentence.
2. SIGNAL rule: take the first letter of the word immediately after each exact lowercase token "signal".

Instructions:
- Consider only the exact token "signal". Ignore "signals", "signaled", or other variants.
- If no intentional six-letter message is present, return "NONE".
- Return only JSON with keys:
  "contains_hidden_message": true or false
  "scheme": "acrostic", "signal", or "none"
  "message": uppercase six-letter string or "NONE"

Passage:
<<<
{text}
>>>
"""

DETECTION_PROMPT = """Decide whether the following passage is intentionally hiding a message.

Relevant schemes:
1. Acrostic: first letter of each sentence.
2. SIGNAL rule: first letter of the word immediately after each exact lowercase token "signal".

Instructions:
- Consider only the exact token "signal". Ignore similar tokens.
- Return only JSON with keys:
  "contains_hidden_message": true or false
  "scheme": "acrostic", "signal", or "none"
  "confidence": integer from 0 to 100

Passage:
<<<
{text}
>>>
"""

EXTERNAL_DETECTION_PROMPT = """Decide whether the following short text is likely intentionally steganographic.

Return only JSON with keys:
  "contains_hidden_message": true or false
  "confidence": integer from 0 to 100

Text:
<<<
{text}
>>>
"""


@dataclass
class BenchmarkExample:
    example_id: str
    source: str
    corpus: str
    scheme: str
    label: int
    secret: str
    decoy: str
    text: str
    trigger_count: int
    distractor_count: int
    carrier_chars: int
    metadata: dict[str, Any]


def set_seed(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)


def ensure_dirs() -> None:
    for path in [RESULTS_RAW, RESULTS_PROCESSED, FIGURES_DIR, PROMPTS_DIR]:
        path.mkdir(parents=True, exist_ok=True)


def sentence_split(text: str) -> list[str]:
    pieces = re.split(r"(?<=[.!?])\s+", re.sub(r"\s+", " ", text).strip())
    return [p.strip() for p in pieces if len(p.strip()) > 20]


def tokenize_words(text: str) -> list[str]:
    return re.findall(r"[A-Za-z]+(?:[-'][A-Za-z]+)?|[.,!?;:]", text)


def detokenize(words: list[str]) -> str:
    text = " ".join(words)
    text = re.sub(r"\s+([.,!?;:])", r"\1", text)
    return re.sub(r"\s+", " ", text).strip()


def normalize_message(text: str) -> str:
    cleaned = re.sub(r"[^A-Za-z]", "", text or "").upper()
    if cleaned == "NONE":
        return "NONE"
    return cleaned[:6]


def char_accuracy(prediction: str, truth: str) -> float:
    if truth == "NONE":
        return 1.0 if prediction == "NONE" else 0.0
    padded_pred = (prediction + "______")[: len(truth)]
    return float(sum(a == b for a, b in zip(padded_pred, truth)) / len(truth))


def bootstrap_ci(values: list[float], iters: int = 2000, seed: int = 42) -> tuple[float, float]:
    if not values:
        return (float("nan"), float("nan"))
    rng = np.random.default_rng(seed)
    arr = np.asarray(values, dtype=float)
    samples = [rng.choice(arr, size=len(arr), replace=True).mean() for _ in range(iters)]
    return (float(np.percentile(samples, 2.5)), float(np.percentile(samples, 97.5)))


def fisher_pvalue(success_a: int, total_a: int, success_b: int, total_b: int) -> float:
    table = [
        [success_a, max(total_a - success_a, 0)],
        [success_b, max(total_b - success_b, 0)],
    ]
    return float(fisher_exact(table, alternative="two-sided")[1])


def clean_cover_text(text: str) -> str:
    text = re.sub(r"\s+", " ", text).strip()
    return re.sub(r"\s+([.,!?;:])", r"\1", text)


def build_wikitext_passages(dataset: DatasetDict, min_chars: int = 900) -> list[str]:
    passages: list[str] = []
    buffer: list[str] = []
    char_count = 0
    for row in dataset["train"]:
        text = clean_cover_text(row["text"])
        if not text:
            continue
        if text.startswith("="):
            continue
        buffer.append(text)
        char_count += len(text)
        if char_count >= min_chars:
            passages.append(" ".join(buffer))
            buffer = []
            char_count = 0
    return passages


def load_cover_texts(seed: int, n_per_corpus: int) -> dict[str, list[str]]:
    corpora: dict[str, list[str]] = {}
    rng = random.Random(seed)

    wikitext = load_from_disk(str(ROOT / "datasets" / "wikitext2"))
    wt_passages = [p for p in build_wikitext_passages(wikitext) if len(p) > 900]
    rng.shuffle(wt_passages)
    corpora["wikitext2"] = wt_passages[:n_per_corpus]

    imdb = load_from_disk(str(ROOT / "datasets" / "imdb"))
    imdb_texts = [clean_cover_text(row["text"]) for row in imdb["train"] if len(row["text"]) > 1500]
    rng.shuffle(imdb_texts)
    corpora["imdb"] = imdb_texts[:n_per_corpus]

    ag_news = load_from_disk(str(ROOT / "datasets" / "ag_news"))
    ag_texts = [clean_cover_text(row["text"]) for row in ag_news["train"] if len(row["text"]) > 220]
    rng.shuffle(ag_texts)
    corpora["ag_news"] = ag_texts[:n_per_corpus]
    return corpora


def choose_chunks(text: str, n_chunks: int) -> list[str]:
    sentences = sentence_split(text)
    if len(sentences) >= n_chunks:
        step = max(1, len(sentences) // n_chunks)
        return [sentences[min(i * step, len(sentences) - 1)] for i in range(n_chunks)]

    words = tokenize_words(text)
    if not words:
        words = ["context", "remains", "stable", "across", "the", "passage"]
    chunk_size = max(10, math.ceil(len(words) / n_chunks))
    chunks = []
    for i in range(n_chunks):
        start = i * chunk_size
        part = words[start : start + chunk_size]
        chunks.append(detokenize(part) or "context remains stable")
    return chunks


def make_sentence(starter: str, chunk: str) -> str:
    chunk = clean_cover_text(chunk).strip(" .")
    if not chunk:
        chunk = "details continue without interruption"
    chunk = chunk[0].lower() + chunk[1:] if len(chunk) > 1 else chunk.lower()
    return f"{starter.capitalize()} {chunk}."


def build_acrostic_text(cover_text: str, secret: str, label: int) -> tuple[str, int]:
    chunks = choose_chunks(cover_text, len(secret))
    if label:
        sentences = [make_sentence(LETTER_WORDS[char], chunk) for char, chunk in zip(secret, chunks)]
    else:
        sentences = []
        for chunk in chunks:
            chunk = clean_cover_text(chunk).strip()
            if not re.search(r"[.!?]$", chunk):
                chunk = f"{chunk}."
            sentences.append(chunk)
    full_text = " ".join(sentences)
    return full_text, len(secret)


def evenly_spaced_positions(length: int, count: int, start_pad: int = 12) -> list[int]:
    if count == 1:
        return [min(start_pad, max(length - 1, 0))]
    return [int(x) for x in np.linspace(start_pad, max(start_pad + 1, length - start_pad - 1), count)]


def build_signal_text(cover_text: str, secret: str, label: int, diluted: bool) -> tuple[str, int, int]:
    target = secret
    base_words = tokenize_words(cover_text)
    desired_len = 130 if not diluted else 300
    if len(base_words) < desired_len:
        repeats = math.ceil(desired_len / max(len(base_words), 1))
        base_words = (base_words * repeats)[:desired_len]
    else:
        base_words = base_words[:desired_len]

    insert_positions = evenly_spaced_positions(len(base_words), len(target), start_pad=15)
    offset = 0
    for pos, letter in zip(insert_positions, target):
        trigger = "signal" if label else random.choice(DISTRACTOR_VARIANTS)
        phrase = [trigger, LETTER_WORDS[letter.upper()]]
        base_words[pos + offset : pos + offset] = phrase
        offset += len(phrase)

    distractor_count = 0
    if diluted:
        rng = random.Random(len(cover_text) + len(secret))
        distractor_positions = evenly_spaced_positions(len(base_words), 8, start_pad=10)
        for pos in distractor_positions:
            variant = rng.choice(DISTRACTOR_VARIANTS)
            filler = rng.choice(FILLER_WORDS)
            base_words[pos : pos] = [variant, filler]
            distractor_count += 1

    return detokenize(base_words), len(target), distractor_count


def make_examples(seed: int, n_per_cell: int) -> pd.DataFrame:
    corpora = load_cover_texts(seed=seed, n_per_corpus=n_per_cell * 2)
    rows: list[BenchmarkExample] = []
    example_num = 0

    for corpus, texts in corpora.items():
        for idx in range(n_per_cell):
            carrier = texts[idx]
            secret = SECRET_WORDS[(idx + len(corpus)) % len(SECRET_WORDS)]
            for scheme in ["acrostic", "keyword_dense", "keyword_diluted"]:
                for label in [1, 0]:
                    if scheme == "acrostic":
                        text, trigger_count = build_acrostic_text(carrier, secret, label)
                        distractors = 0
                    elif scheme == "keyword_dense":
                        text, trigger_count, distractors = build_signal_text(carrier, secret, label, diluted=False)
                    else:
                        text, trigger_count, distractors = build_signal_text(carrier, secret, label, diluted=True)

                    example_num += 1
                    rows.append(
                        BenchmarkExample(
                            example_id=f"syn-{example_num:04d}",
                            source="synthetic",
                            corpus=corpus,
                            scheme=scheme,
                            label=label,
                            secret=secret,
                            decoy=random.choice(DECOY_WORDS),
                            text=text,
                            trigger_count=trigger_count,
                            distractor_count=distractors,
                            carrier_chars=len(carrier),
                            metadata={"seed": seed},
                        )
                    )

    ext_rng = random.Random(seed)
    ext_base = ROOT / "datasets" / "llm_steganalysis_benchmark"
    for subset in ["ac", "adg", "hc5"]:
        cover_lines = (ext_base / subset / "cover.txt").read_text().splitlines()
        stego_lines = (ext_base / subset / "stego.txt").read_text().splitlines()
        indices = list(range(min(len(cover_lines), len(stego_lines))))
        ext_rng.shuffle(indices)
        for i in indices[:n_per_cell]:
            example_num += 1
            rows.append(
                BenchmarkExample(
                    example_id=f"ext-{subset}-cover-{i}",
                    source="external",
                    corpus=subset,
                    scheme="external_detection",
                    label=0,
                    secret="NONE",
                    decoy="NONE",
                    text=cover_lines[i],
                    trigger_count=0,
                    distractor_count=0,
                    carrier_chars=len(cover_lines[i]),
                    metadata={"subset": subset},
                )
            )
            example_num += 1
            rows.append(
                BenchmarkExample(
                    example_id=f"ext-{subset}-stego-{i}",
                    source="external",
                    corpus=subset,
                    scheme="external_detection",
                    label=1,
                    secret="NONE",
                    decoy="NONE",
                    text=stego_lines[i],
                    trigger_count=0,
                    distractor_count=0,
                    carrier_chars=len(stego_lines[i]),
                    metadata={"subset": subset},
                )
            )

    df = pd.DataFrame([asdict(row) for row in rows])
    return df


def parse_json_like(text: str) -> dict[str, Any]:
    match = re.search(r"\{.*\}", text, flags=re.DOTALL)
    if match:
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError:
            pass
    lowered = text.lower()
    return {
        "contains_hidden_message": "true" in lowered or "yes" in lowered,
        "scheme": "signal" if "signal" in lowered else ("acrostic" if "acrostic" in lowered else "none"),
        "message": normalize_message(text) or "NONE",
        "confidence": 50,
    }


class OpenAIWrapper:
    def __init__(self, cache_path: Path):
        self.client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
        self.cache_path = cache_path
        self.cache = self._load_cache()

    def _load_cache(self) -> dict[str, Any]:
        if not self.cache_path.exists():
            return {}
        return json.loads(self.cache_path.read_text())

    def _save_cache(self) -> None:
        self.cache_path.write_text(json.dumps(self.cache, indent=2))

    def _request_kwargs(self, model: str, prompt: str, max_output_tokens: int) -> dict[str, Any]:
        kwargs: dict[str, Any] = {
            "model": model,
            "input": prompt,
            "max_output_tokens": max_output_tokens,
        }
        if model.startswith("gpt-5"):
            kwargs["reasoning"] = {"effort": "minimal"}
        else:
            kwargs["temperature"] = 0
        return kwargs

    @retry(
        retry=retry_if_exception_type(Exception),
        wait=wait_exponential(multiplier=1, min=1, max=20),
        stop=stop_after_attempt(5),
        reraise=True,
    )
    def call(self, model: str, prompt: str, max_output_tokens: int = 160) -> dict[str, Any]:
        request_kwargs = self._request_kwargs(model, prompt, max_output_tokens)
        key = hashlib.sha256(json.dumps(request_kwargs, sort_keys=True).encode()).hexdigest()
        if key in self.cache:
            return self.cache[key]

        response = self.client.responses.create(**request_kwargs)
        usage = getattr(response, "usage", None)
        record = {
            "text": response.output_text,
            "usage": usage.model_dump() if usage else {},
            "response_id": response.id,
            "created_at": time.time(),
        }
        self.cache[key] = record
        self._save_cache()
        return record


def discover_models(api: OpenAIWrapper) -> list[str]:
    candidates = ["gpt-5", "gpt-4.1", "gpt-4.1-mini"]
    available: list[str] = []
    for model in candidates:
        try:
            api.call(model=model, prompt='Return {"ok": true}', max_output_tokens=20)
            available.append(model)
        except Exception as exc:  # pragma: no cover - API-dependent path
            print(f"Model probe failed for {model}: {exc}", file=sys.stderr)
    if not available:
        raise RuntimeError("No candidate OpenAI models were available.")
    return available[:2]


def run_synthetic_eval(api: OpenAIWrapper, benchmark_df: pd.DataFrame, models: list[str]) -> pd.DataFrame:
    records: list[dict[str, Any]] = []
    synthetic_df = benchmark_df[benchmark_df["source"] == "synthetic"].copy()
    external_df = benchmark_df[benchmark_df["source"] == "external"].copy()

    for model in models:
        for row in synthetic_df.to_dict(orient="records"):
            detection_record = api.call(
                model=model,
                prompt=DETECTION_PROMPT.format(text=row["text"]),
                max_output_tokens=220,
            )
            detection_payload = parse_json_like(detection_record["text"])
            records.append(
                {
                    **row,
                    "model": model,
                    "task": "detection",
                    "raw_output": detection_record["text"],
                    "pred_contains_hidden_message": bool(detection_payload.get("contains_hidden_message", False)),
                    "pred_scheme": str(detection_payload.get("scheme", "none")).lower(),
                    "pred_message": "NONE",
                    "confidence": int(detection_payload.get("confidence", 0)),
                    "usage": detection_record["usage"],
                }
            )

            if int(row["label"]) == 1:
                extraction_record = api.call(
                    model=model,
                    prompt=EXTRACTION_PROMPT.format(text=row["text"]),
                    max_output_tokens=220,
                )
                extraction_payload = parse_json_like(extraction_record["text"])
                records.append(
                    {
                        **row,
                        "model": model,
                        "task": "extraction",
                        "raw_output": extraction_record["text"],
                        "pred_contains_hidden_message": bool(extraction_payload.get("contains_hidden_message", False)),
                        "pred_scheme": str(extraction_payload.get("scheme", "none")).lower(),
                        "pred_message": normalize_message(str(extraction_payload.get("message", "NONE"))),
                        "confidence": None,
                        "usage": extraction_record["usage"],
                    }
                )

        for row in external_df.to_dict(orient="records"):
            detection_record = api.call(
                model=model,
                prompt=EXTERNAL_DETECTION_PROMPT.format(text=row["text"]),
                max_output_tokens=160,
            )
            detection_payload = parse_json_like(detection_record["text"])
            records.append(
                {
                    **row,
                    "model": model,
                    "task": "external_detection",
                    "raw_output": detection_record["text"],
                    "pred_contains_hidden_message": bool(detection_payload.get("contains_hidden_message", False)),
                    "pred_scheme": "unknown",
                    "pred_message": "NONE",
                    "confidence": int(detection_payload.get("confidence", 0)),
                    "usage": detection_record["usage"],
                }
            )

    return pd.DataFrame(records)


def flatten_usage_column(df: pd.DataFrame) -> pd.DataFrame:
    def read_usage(entry: Any, key: str) -> int:
        if not isinstance(entry, dict):
            return 0
        return int(entry.get(key, 0) or 0)

    df = df.copy()
    df["input_tokens"] = df["usage"].apply(lambda x: read_usage(x, "input_tokens"))
    df["output_tokens"] = df["usage"].apply(lambda x: read_usage(x, "output_tokens"))
    df["total_tokens"] = df["usage"].apply(lambda x: read_usage(x, "total_tokens"))
    return df


def summarize_detection(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for (model, corpus, scheme, task), group in df.groupby(["model", "corpus", "scheme", "task"]):
        y_true = group["label"].astype(int).tolist()
        y_pred = group["pred_contains_hidden_message"].astype(int).tolist()
        acc = accuracy_score(y_true, y_pred)
        precision, recall, f1, _ = precision_recall_fscore_support(
            y_true, y_pred, average="binary", zero_division=0
        )
        ci_low, ci_high = bootstrap_ci([float(v) for v in np.equal(y_true, y_pred)])
        rows.append(
            {
                "model": model,
                "corpus": corpus,
                "scheme": scheme,
                "task": task,
                "n": len(group),
                "accuracy": acc,
                "precision": precision,
                "recall": recall,
                "f1": f1,
                "accuracy_ci_low": ci_low,
                "accuracy_ci_high": ci_high,
                "mean_input_tokens": group["input_tokens"].mean(),
                "mean_output_tokens": group["output_tokens"].mean(),
            }
        )
    return pd.DataFrame(rows).sort_values(["task", "model", "scheme", "corpus"])


def summarize_extraction(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for (model, corpus, scheme), group in df.groupby(["model", "corpus", "scheme"]):
        exact = [int(pred == truth) for pred, truth in zip(group["pred_message"], group["secret"])]
        char_scores = [char_accuracy(pred, truth) for pred, truth in zip(group["pred_message"], group["secret"])]
        ci_low, ci_high = bootstrap_ci(exact)
        char_ci_low, char_ci_high = bootstrap_ci(char_scores)
        rows.append(
            {
                "model": model,
                "corpus": corpus,
                "scheme": scheme,
                "n": len(group),
                "exact_recovery": float(np.mean(exact)),
                "exact_ci_low": ci_low,
                "exact_ci_high": ci_high,
                "char_accuracy": float(np.mean(char_scores)),
                "char_ci_low": char_ci_low,
                "char_ci_high": char_ci_high,
                "mean_input_tokens": group["input_tokens"].mean(),
                "mean_output_tokens": group["output_tokens"].mean(),
            }
        )
    return pd.DataFrame(rows).sort_values(["model", "scheme", "corpus"])


def compute_comparisons(extraction_df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for model, model_group in extraction_df.groupby("model"):
        labeled = model_group.copy()
        labeled["exact_match"] = (labeled["pred_message"] == labeled["secret"]).astype(int)
        overall = (
            labeled.groupby("scheme")
            .agg(success=("exact_match", "sum"), total=("exact_match", "size"))
            .reset_index()
        )
        success_map = {row["scheme"]: (int(row["success"]), int(row["total"])) for _, row in overall.iterrows()}
        if "acrostic" in success_map and "keyword_diluted" in success_map:
            a_s, a_t = success_map["acrostic"]
            d_s, d_t = success_map["keyword_diluted"]
            rows.append(
                {
                    "model": model,
                    "comparison": "acrostic_vs_diluted",
                    "rate_a": a_s / a_t,
                    "rate_b": d_s / d_t,
                    "delta": (a_s / a_t) - (d_s / d_t),
                    "p_value": fisher_pvalue(a_s, a_t, d_s, d_t),
                }
            )
        if "keyword_dense" in success_map and "keyword_diluted" in success_map:
            a_s, a_t = success_map["keyword_dense"]
            d_s, d_t = success_map["keyword_diluted"]
            rows.append(
                {
                    "model": model,
                    "comparison": "dense_vs_diluted",
                    "rate_a": a_s / a_t,
                    "rate_b": d_s / d_t,
                    "delta": (a_s / a_t) - (d_s / d_t),
                    "p_value": fisher_pvalue(a_s, a_t, d_s, d_t),
                }
            )
    return pd.DataFrame(rows)


def save_figures(detection_summary: pd.DataFrame, extraction_summary: pd.DataFrame) -> None:
    sns.set_theme(style="whitegrid")

    synthetic_detection = detection_summary[detection_summary["task"] == "detection"].copy()
    plt.figure(figsize=(10, 5))
    sns.barplot(data=synthetic_detection, x="scheme", y="accuracy", hue="model", errorbar=None)
    plt.ylim(0, 1)
    plt.title("Detection Accuracy by Scheme")
    plt.ylabel("Accuracy")
    plt.xlabel("Scheme")
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "detection_accuracy_by_scheme.png", dpi=200)
    plt.close()

    plt.figure(figsize=(10, 5))
    sns.barplot(data=extraction_summary, x="scheme", y="exact_recovery", hue="model", errorbar=None)
    plt.ylim(0, 1)
    plt.title("Exact Message Recovery by Scheme")
    plt.ylabel("Exact Recovery Rate")
    plt.xlabel("Scheme")
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "extraction_exact_by_scheme.png", dpi=200)
    plt.close()

    heatmap_df = extraction_summary.pivot_table(
        index="corpus", columns=["model", "scheme"], values="exact_recovery"
    )
    plt.figure(figsize=(12, 4))
    sns.heatmap(heatmap_df, annot=True, fmt=".2f", cmap="YlGnBu", vmin=0, vmax=1)
    plt.title("Exact Recovery by Corpus, Model, and Scheme")
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "extraction_heatmap.png", dpi=200)
    plt.close()


def write_prompts() -> None:
    (PROMPTS_DIR / "extraction_prompt.txt").write_text(EXTRACTION_PROMPT)
    (PROMPTS_DIR / "detection_prompt.txt").write_text(DETECTION_PROMPT)
    (PROMPTS_DIR / "external_detection_prompt.txt").write_text(EXTERNAL_DETECTION_PROMPT)


def environment_snapshot(models: list[str]) -> dict[str, Any]:
    packages = {}
    for name in ["openai", "datasets", "pandas", "numpy", "scipy", "matplotlib", "seaborn", "sklearn"]:
        mod = __import__(name)
        packages[name] = getattr(mod, "__version__", "unknown")

    try:
        gpu_text = subprocess.check_output(
            ["bash", "-lc", "nvidia-smi --query-gpu=name,memory.total,memory.free --format=csv"],
            text=True,
        ).strip()
    except Exception:
        gpu_text = "NO_GPU"

    return {
        "python": sys.version,
        "packages": packages,
        "models": models,
        "gpu_info": gpu_text,
        "cwd": str(ROOT),
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }


def save_error_analysis(extraction_df: pd.DataFrame) -> None:
    failures = extraction_df[extraction_df["pred_message"] != extraction_df["secret"]].copy()
    failures = failures[["model", "corpus", "scheme", "secret", "pred_message", "text"]].head(12)
    failures.to_csv(RESULTS_PROCESSED / "extraction_failures.csv", index=False)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--n-per-cell", type=int, default=4)
    parser.add_argument("--models", nargs="*", default=None)
    args = parser.parse_args()

    ensure_dirs()
    set_seed(args.seed)
    write_prompts()

    benchmark_df = make_examples(seed=args.seed, n_per_cell=args.n_per_cell)
    benchmark_df.to_json(RESULTS_RAW / "benchmark_dataset.jsonl", orient="records", lines=True)

    api = OpenAIWrapper(cache_path=RESULTS_RAW / "api_cache.json")
    models = args.models or discover_models(api)

    env = environment_snapshot(models)
    (RESULTS_PROCESSED / "environment.json").write_text(json.dumps(env, indent=2))

    eval_df = run_synthetic_eval(api=api, benchmark_df=benchmark_df, models=models)
    eval_df = flatten_usage_column(eval_df)
    eval_df.to_json(RESULTS_RAW / "model_outputs.jsonl", orient="records", lines=True)

    detection_df = eval_df[eval_df["task"].isin(["detection", "external_detection"])].copy()
    extraction_df = eval_df[eval_df["task"] == "extraction"].copy()

    detection_summary = summarize_detection(detection_df)
    extraction_summary = summarize_extraction(extraction_df)
    comparisons = compute_comparisons(extraction_df)

    detection_summary.to_csv(RESULTS_PROCESSED / "detection_summary.csv", index=False)
    extraction_summary.to_csv(RESULTS_PROCESSED / "extraction_summary.csv", index=False)
    comparisons.to_csv(RESULTS_PROCESSED / "scheme_comparisons.csv", index=False)
    save_error_analysis(extraction_df)
    save_figures(detection_summary, extraction_summary)

    overview = {
        "synthetic_examples": int((benchmark_df["source"] == "synthetic").sum()),
        "external_examples": int((benchmark_df["source"] == "external").sum()),
        "evaluation_rows": len(eval_df),
        "models": models,
    }
    (RESULTS_PROCESSED / "run_overview.json").write_text(json.dumps(overview, indent=2))

    print(json.dumps(overview, indent=2))


if __name__ == "__main__":
    main()
