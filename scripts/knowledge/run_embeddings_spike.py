#!/usr/bin/env python3
"""Embeddings model-selection spike runner — issue #2403.

Compares BGE-M3 (local via Ollama) vs Voyage-3 vs text-embedding-3-large on a
curated eval set. Writes per-model measurement JSON to docs/reports/embeddings-spike/
and a decision doc to docs/document-intelligence/embeddings-model-selection.md.

This is a SCAFFOLD-PHASE implementation. Core logic (validation, cost-cap,
decision-doc rendering) is complete and tested with mocks. The three
model-specific runners (BGEM3LocalRunner, VoyageRunner, OpenAIRunner) are
stubs — they raise RuntimeError until the corresponding API key / Ollama
install is provisioned.

Measurement phase is user-gated. Once prereqs are available, fill in the
stub runners and invoke `main()`.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Iterable, Protocol

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_EVAL_SET = REPO_ROOT / "tests" / "fixtures" / "embeddings" / "eval-set.jsonl"
DEFAULT_REPORTS_DIR = REPO_ROOT / "docs" / "reports" / "embeddings-spike"
DEFAULT_DECISION_DOC = REPO_ROOT / "docs" / "document-intelligence" / "embeddings-model-selection.md"

DOC_KEY_RE = re.compile(r"^(sha256|md5):[0-9a-f]+$")


class CostCapExceeded(RuntimeError):
    """Raised when a spike runner's accumulated cost exceeds the configured cap."""


class ModelRunner(Protocol):
    """Minimal contract any embedding backend must satisfy."""

    name: str
    cost_tally: float

    def embed(self, text: str) -> list[float]: ...


def validate_doc_key(key: str) -> bool:
    """Return True if key matches the operating-model §3 identity format."""
    return bool(DOC_KEY_RE.match(key))


def validate_corpus(corpus: Iterable[dict]) -> None:
    """Reject any corpus document whose doc_key is not sha256:/md5:-namespaced."""
    for doc in corpus:
        key = doc.get("doc_key", "")
        if not validate_doc_key(key):
            raise ValueError(
                f"corpus doc_key {key!r} must match ^(sha256|md5):[0-9a-f]+$"
            )


def load_eval_set(path: Path) -> list[dict]:
    """Load and validate the eval set from JSONL. Raises on bad shape or <50 rows."""
    if not path.exists():
        raise FileNotFoundError(f"eval set missing: {path}")

    rows = [json.loads(ln) for ln in path.read_text().splitlines() if ln.strip()]

    # Per-row validation runs first so malformed rows fail fast with specific
    # errors, not masked by the aggregate size check below.
    for i, r in enumerate(rows):
        for required in ("query_text", "target_doc_key"):
            if required not in r:
                raise ValueError(f"row {i} missing required field {required!r}")
        if not validate_doc_key(r["target_doc_key"]):
            raise ValueError(
                f"row {i} target_doc_key {r['target_doc_key']!r} must match "
                f"^(sha256|md5):[0-9a-f]+$"
            )

    if len(rows) < 50:
        raise ValueError(
            f"eval set needs ≥50 queries (got {len(rows)}); "
            f"add more curated entries before running measurement"
        )

    return rows


@dataclass
class SpikeConfig:
    """Env-loaded configuration for the spike run."""

    models: tuple[str, ...] = ("bge-m3-local", "voyage-3-cloud", "text-embedding-3-large")
    max_usd: float = 5.0
    openai_api_key: str | None = None
    voyage_api_key: str | None = None
    ollama_host: str = "http://localhost:11434"
    corpus_sample_size: int = 500

    @classmethod
    def from_env(cls, models: tuple[str, ...] | None = None) -> "SpikeConfig":
        return cls(
            models=models or cls.models,
            max_usd=float(os.environ.get("SPIKE_MAX_USD", "5.0")),
            openai_api_key=os.environ.get("OPENAI_API_KEY"),
            voyage_api_key=os.environ.get("VOYAGE_API_KEY"),
            ollama_host=os.environ.get("OLLAMA_HOST", "http://localhost:11434"),
            corpus_sample_size=int(os.environ.get("SPIKE_CORPUS_SIZE", "500")),
        )


def check_cost_budget_or_abort(runner: ModelRunner, cap_usd: float) -> None:
    """Raise CostCapExceeded if the runner has already spent over the cap."""
    if runner.cost_tally > cap_usd:
        raise CostCapExceeded(
            f"runner {getattr(runner, 'name', '?')!r} spent "
            f"${runner.cost_tally:.4f}, cap is ${cap_usd:.2f}"
        )


def write_model_report(
    reports_dir: Path, model_name: str, result: dict[str, Any]
) -> Path:
    """Write per-model measurement JSON to reports_dir/<model>-<utc-ts>.json."""
    reports_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out = reports_dir / f"{model_name}-{ts}.json"
    out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    return out


def _current_commit_sha() -> str:
    """Best-effort short git SHA of HEAD; returns 'unknown' if not available."""
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=REPO_ROOT,
            text=True,
        ).strip()
    except Exception:
        return "unknown"


def render_decision_doc(
    output_path: Path,
    results: list[dict[str, Any]],
    chosen_model: str,
    rationale: str,
    measurement_commit_sha: str,
) -> Path:
    """Compile results into a decision markdown. Includes numeric rubric + pick + SHA."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    lines: list[str] = []
    lines.append("# Embeddings model-selection decision (#2403)")
    lines.append("")
    lines.append(f"> Measurement commit SHA: `{measurement_commit_sha}`")
    lines.append(f"> Chosen model: **{chosen_model}**")
    lines.append("")
    lines.append("## Rubric (per-model numeric comparison)")
    lines.append("")
    lines.append("| Model | recall@10 | cost_usd | p95_latency_ms | corpus_docs_embedded |")
    lines.append("|---|---|---|---|---|")
    for r in results:
        lines.append(
            f"| {r['model']} | {r['recall_at_10']} | {r['cost_usd']} | "
            f"{r['p95_latency_ms']} | {r['corpus_docs_embedded']} |"
        )
    lines.append("")
    lines.append("## Rationale")
    lines.append("")
    lines.append(rationale)
    lines.append("")
    output_path.write_text("\n".join(lines) + "\n")
    return output_path


# ── Stub runners (scaffold phase; user provisions prereqs later) ──────────────


class _StubRunner:
    def __init__(self, name: str, blocker: str):
        self.name = name
        self._blocker = blocker
        self.cost_tally = 0.0

    def embed(self, text: str) -> list[float]:
        raise RuntimeError(
            f"{self.name}: measurement phase not runnable — {self._blocker}"
        )


def make_bge_m3_local_runner(cfg: SpikeConfig) -> ModelRunner:
    return _StubRunner(
        "bge-m3-local",
        "Ollama not installed. Install from https://ollama.com/, then `ollama pull bge-m3`.",
    )


def make_voyage_runner(cfg: SpikeConfig) -> ModelRunner:
    if not cfg.voyage_api_key:
        return _StubRunner("voyage-3-cloud", "VOYAGE_API_KEY not set.")
    return _StubRunner("voyage-3-cloud", "Runner impl deferred — key detected; fill in.")


def make_openai_runner(cfg: SpikeConfig) -> ModelRunner:
    if not cfg.openai_api_key:
        return _StubRunner("text-embedding-3-large", "OPENAI_API_KEY not set.")
    return _StubRunner(
        "text-embedding-3-large", "Runner impl deferred — key detected; fill in."
    )


RUNNER_FACTORIES: dict[str, Callable[[SpikeConfig], ModelRunner]] = {
    "bge-m3-local": make_bge_m3_local_runner,
    "voyage-3-cloud": make_voyage_runner,
    "text-embedding-3-large": make_openai_runner,
}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--eval-set", type=Path, default=DEFAULT_EVAL_SET)
    ap.add_argument("--reports-dir", type=Path, default=DEFAULT_REPORTS_DIR)
    ap.add_argument("--decision-doc", type=Path, default=DEFAULT_DECISION_DOC)
    ap.add_argument(
        "--scaffold-check", action="store_true",
        help="Validate eval set + config + runner factories without running measurement",
    )
    args = ap.parse_args(argv)

    cfg = SpikeConfig.from_env()
    eval_set = load_eval_set(args.eval_set)
    runners = {m: RUNNER_FACTORIES[m](cfg) for m in cfg.models if m in RUNNER_FACTORIES}

    if args.scaffold_check:
        print(f"[OK] eval set: {len(eval_set)} queries validated at {args.eval_set}")
        print(f"[OK] config: models={cfg.models} cap=${cfg.max_usd}")
        for name, r in runners.items():
            is_stub = isinstance(r, _StubRunner)
            print(f"[{'STUB' if is_stub else 'READY'}] {name}")
        return 0

    # Measurement phase (requires real runners — stubs will raise)
    all_results: list[dict[str, Any]] = []
    for name, runner in runners.items():
        if isinstance(runner, _StubRunner):
            print(f"[SKIP] {name}: {runner._blocker}", file=sys.stderr)
            continue
        check_cost_budget_or_abort(runner, cfg.max_usd)
        # Real measurement loop would live here; omitted until runners are implemented.
        raise NotImplementedError(
            f"measurement loop not yet wired for {name} — "
            f"scaffold phase only provides validation, cost-cap, and reporting."
        )

    if not all_results:
        print("[INFO] no real runners available; exiting without writing decision doc",
              file=sys.stderr)
        return 2

    best = max(all_results, key=lambda r: r["recall_at_10"])
    render_decision_doc(
        output_path=args.decision_doc,
        results=all_results,
        chosen_model=best["model"],
        rationale=f"Highest recall@10 at acceptable cost and latency.",
        measurement_commit_sha=_current_commit_sha(),
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
