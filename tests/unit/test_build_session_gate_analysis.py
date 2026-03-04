from __future__ import annotations

import importlib.util
from pathlib import Path


def _load_module():
    repo_root = Path(__file__).resolve().parents[2]
    script_path = repo_root / "scripts" / "work-queue" / "build-session-gate-analysis.py"
    spec = importlib.util.spec_from_file_location("build_session_gate_analysis", script_path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_infer_gate_signals_for_common_workflow_markers():
    mod = _load_module()
    text = """
    scripts/agents/session.sh init --provider codex
    scripts/work-queue/set-active-wrk.sh WRK-690
    scripts/review/cross-review.sh
    scripts/work-queue/verify-gate-evidence.py WRK-690 --phase close
    scripts/work-queue/close-item.sh WRK-690
    future-work.yaml
    """
    scripts = mod._infer_scripts(text)
    gates = mod.infer_gate_signals(text, scripts)
    assert gates["init"] is True
    assert gates["set_active_wrk"] is True
    assert gates["cross_review"] is True
    assert gates["verify_gate_evidence"] is True
    assert gates["future_work"] is True
    assert gates["close_or_archive"] is True


def test_strict_relaxed_classification():
    mod = _load_module()
    strict, relaxed = mod._strict_relaxed(
        {
            "init": True,
            "set_active_wrk": True,
            "verify_gate_evidence": True,
            "cross_review": True,
            "claim_evidence": True,
            "close_or_archive": True,
        }
    )
    assert strict is True
    assert relaxed is True

