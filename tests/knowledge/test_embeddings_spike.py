"""Tests for scripts/knowledge/run_embeddings_spike.py (issue #2403).

Scaffold-phase tests: cover all testable AC behaviors with mocks.
The actual measurement runs (BGE-M3 local / Voyage API / OpenAI API) are
deferred until API keys are provisioned / Ollama installed.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path
from unittest.mock import Mock

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
RUNNER = REPO_ROOT / "scripts" / "knowledge" / "run_embeddings_spike.py"
EVAL_SET = REPO_ROOT / "tests" / "fixtures" / "embeddings" / "eval-set.jsonl"
DECISION_DOC = REPO_ROOT / "docs" / "document-intelligence" / "embeddings-model-selection.md"

sys.path.insert(0, str(REPO_ROOT / "scripts" / "knowledge"))
import run_embeddings_spike as spike  # noqa: E402


# ── eval-set shape (AC 1: ≥50 queries with doc_key targets) ──────────────────

def test_eval_set_exists_with_50_plus_queries():
    assert EVAL_SET.exists(), f"eval set missing: {EVAL_SET}"
    rows = [json.loads(ln) for ln in EVAL_SET.read_text().splitlines() if ln.strip()]
    assert len(rows) >= 50, f"need ≥50 queries, got {len(rows)}"


def test_eval_set_doc_keys_all_sha256_or_md5():
    rows = [json.loads(ln) for ln in EVAL_SET.read_text().splitlines() if ln.strip()]
    for r in rows:
        assert spike.validate_doc_key(r["target_doc_key"]), \
            f"invalid doc_key {r['target_doc_key']!r} for query {r['query_text'][:40]!r}"


def test_eval_set_rejects_bare_hex(tmp_path):
    bad = tmp_path / "bad.jsonl"
    bad.write_text(json.dumps({"query_text": "q", "target_doc_key": "abc123"}) + "\n")
    with pytest.raises(ValueError, match="doc_key"):
        spike.load_eval_set(bad)


# ── corpus validation (v2 fix — rejects corpus with non-conforming keys) ─────

def test_spike_runner_rejects_corpus_with_non_conforming_doc_keys():
    bad_corpus = [{"doc_key": "plain-text-path.md", "text": "hi"}]
    with pytest.raises(ValueError, match="doc_key"):
        spike.validate_corpus(bad_corpus)


# ── cost cap (AC 5) ──────────────────────────────────────────────────────────

def test_spike_aborts_over_cost_cap():
    class ExpensiveMock:
        cost_tally = 10.0
        def embed(self, text): return [0.0]
    with pytest.raises(spike.CostCapExceeded):
        spike.check_cost_budget_or_abort(ExpensiveMock(), cap_usd=5.0)


# ── env-var API key loading (threat-model AC) ────────────────────────────────

def test_api_keys_loaded_from_env_only(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("VOYAGE_API_KEY", raising=False)
    cfg = spike.SpikeConfig.from_env(models=("voyage-3-cloud",))
    assert cfg.voyage_api_key is None
    monkeypatch.setenv("VOYAGE_API_KEY", "test-key-xyz")
    cfg2 = spike.SpikeConfig.from_env(models=("voyage-3-cloud",))
    assert cfg2.voyage_api_key == "test-key-xyz"


# ── uncurated eval set rejected (AC: fail if <50) ────────────────────────────

def test_spike_rejects_uncurated_eval_set(tmp_path):
    tiny = tmp_path / "tiny.jsonl"
    tiny.write_text(json.dumps(
        {"query_text": "q", "target_doc_key": "sha256:" + "a" * 64}
    ) + "\n")
    with pytest.raises(ValueError, match="50"):
        spike.load_eval_set(tiny)


# ── per-model JSON output (AC 2) ─────────────────────────────────────────────

def test_spike_runner_produces_json_per_model(tmp_path, monkeypatch):
    class FakeRunner:
        name = "fake-model"
        cost_tally = 0.0
        def embed(self, text): return [1.0, 0.0, 0.0]
    reports_dir = tmp_path / "reports"
    spike.write_model_report(
        reports_dir=reports_dir,
        model_name="fake-model",
        result={
            "model": "fake-model",
            "corpus_docs_embedded": 500,
            "cost_usd": 0.12,
            "recall_at_10": 0.74,
            "p95_latency_ms": 183.2,
        },
    )
    outputs = list(reports_dir.glob("fake-model-*.json"))
    assert len(outputs) == 1, f"expected 1 report, got {outputs}"
    data = json.loads(outputs[0].read_text())
    assert data["model"] == "fake-model"
    for k in ("corpus_docs_embedded", "cost_usd", "recall_at_10", "p95_latency_ms"):
        assert k in data, f"missing key: {k}"


# ── decision doc contains all models + pick + rubric numbers ─────────────────

def test_decision_doc_contains_all_models_and_pick(tmp_path):
    out = tmp_path / "decision.md"
    spike.render_decision_doc(
        output_path=out,
        results=[
            {"model": "bge-m3-local", "recall_at_10": 0.71, "cost_usd": 0.0,
             "p95_latency_ms": 42.0, "corpus_docs_embedded": 500},
            {"model": "voyage-3-cloud", "recall_at_10": 0.85, "cost_usd": 0.09,
             "p95_latency_ms": 180.0, "corpus_docs_embedded": 500},
            {"model": "text-embedding-3-large", "recall_at_10": 0.82, "cost_usd": 0.13,
             "p95_latency_ms": 210.0, "corpus_docs_embedded": 500},
        ],
        chosen_model="voyage-3-cloud",
        rationale="Highest recall at acceptable cost and latency.",
        measurement_commit_sha="abcdef1234567890",
    )
    body = out.read_text()
    for m in ("bge-m3-local", "voyage-3-cloud", "text-embedding-3-large"):
        assert m in body, f"model {m!r} missing from decision doc"
    assert "voyage-3-cloud" in body  # pick
    assert "Highest recall" in body  # rationale


def test_decision_doc_references_commit_sha(tmp_path):
    out = tmp_path / "decision.md"
    spike.render_decision_doc(
        output_path=out, results=[], chosen_model="n/a",
        rationale="scaffold", measurement_commit_sha="abc1234f",
    )
    assert "abc1234f" in out.read_text()


def test_decision_doc_contains_rubric_numbers_per_model(tmp_path):
    out = tmp_path / "decision.md"
    results = [
        {"model": "bge-m3-local", "recall_at_10": 0.71, "cost_usd": 0.0,
         "p95_latency_ms": 42.0, "corpus_docs_embedded": 500},
        {"model": "voyage-3-cloud", "recall_at_10": 0.85, "cost_usd": 0.09,
         "p95_latency_ms": 180.0, "corpus_docs_embedded": 500},
    ]
    spike.render_decision_doc(
        output_path=out, results=results, chosen_model="voyage-3-cloud",
        rationale="r", measurement_commit_sha="abcdef1",
    )
    body = out.read_text()
    for r in results:
        assert str(r["recall_at_10"]) in body
        assert str(r["cost_usd"]) in body
        assert str(r["p95_latency_ms"]) in body


# ── runner CLI smoke test (importable + main() entry) ────────────────────────

def test_runner_module_importable():
    assert hasattr(spike, "main")
    assert hasattr(spike, "validate_doc_key")
    assert hasattr(spike, "load_eval_set")
    assert hasattr(spike, "SpikeConfig")
    assert hasattr(spike, "CostCapExceeded")


# ── real backend client wiring (measurement remains env/runtime gated) ───────

def _json_response(payload: dict):
    response = Mock()
    response.__enter__ = Mock(return_value=response)
    response.__exit__ = Mock(return_value=None)
    response.read.return_value = json.dumps(payload).encode("utf-8")
    return response


def test_openai_runner_posts_embedding_request(monkeypatch):
    calls = []

    def fake_urlopen(req, timeout):
        calls.append((req, timeout))
        return _json_response({"data": [{"embedding": [0.1, 0.2, 0.3]}]})

    monkeypatch.setattr(spike.urllib.request, "urlopen", fake_urlopen)
    runner = spike.make_openai_runner(
        spike.SpikeConfig(openai_api_key="test-openai-key")
    )

    assert not isinstance(runner, spike._StubRunner)
    assert runner.embed("query text") == [0.1, 0.2, 0.3]
    req, timeout = calls[0]
    assert req.full_url == "https://api.openai.com/v1/embeddings"
    assert req.headers["Authorization"] == "Bearer test-openai-key"
    assert json.loads(req.data.decode("utf-8")) == {
        "model": "text-embedding-3-large",
        "input": "query text",
    }
    assert timeout == 60


def test_voyage_runner_posts_embedding_request(monkeypatch):
    calls = []

    def fake_urlopen(req, timeout):
        calls.append((req, timeout))
        return _json_response({"data": [{"embedding": [0.4, 0.5]}]})

    monkeypatch.setattr(spike.urllib.request, "urlopen", fake_urlopen)
    runner = spike.make_voyage_runner(
        spike.SpikeConfig(voyage_api_key="test-voyage-key")
    )

    assert not isinstance(runner, spike._StubRunner)
    assert runner.embed("query text") == [0.4, 0.5]
    req, timeout = calls[0]
    assert req.full_url == "https://api.voyageai.com/v1/embeddings"
    assert req.headers["Authorization"] == "Bearer test-voyage-key"
    assert json.loads(req.data.decode("utf-8")) == {
        "model": "voyage-3",
        "input": ["query text"],
    }
    assert timeout == 60


def test_bge_runner_posts_ollama_request(monkeypatch):
    calls = []

    def fake_urlopen(req, timeout):
        calls.append((req, timeout))
        return _json_response({"embedding": [0.6, 0.7]})

    monkeypatch.setattr(spike.shutil, "which", lambda name: "/usr/bin/ollama")
    monkeypatch.setattr(spike.urllib.request, "urlopen", fake_urlopen)
    runner = spike.make_bge_m3_local_runner(
        spike.SpikeConfig(ollama_host="http://localhost:11434")
    )

    assert not isinstance(runner, spike._StubRunner)
    assert runner.embed("query text") == [0.6, 0.7]
    req, timeout = calls[0]
    assert req.full_url == "http://localhost:11434/api/embeddings"
    assert json.loads(req.data.decode("utf-8")) == {
        "model": "bge-m3",
        "prompt": "query text",
    }
    assert timeout == 120
