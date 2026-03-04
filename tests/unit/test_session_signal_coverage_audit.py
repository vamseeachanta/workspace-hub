from __future__ import annotations

import importlib.util
from pathlib import Path


def _load_module():
    repo_root = Path(__file__).resolve().parents[2]
    script_path = repo_root / "scripts" / "work-queue" / "audit-session-signal-coverage.py"
    spec = importlib.util.spec_from_file_location("audit_session_signal_coverage", script_path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_build_report_marks_missing_required_signals():
    mod = _load_module()
    fixture = {
        "aggregate": {
            "gate_relaxed": {"init": 1, "cross_review": 1},
            "gate_strict": {"init": 1, "cross_review": 1},
        },
        "sessions": [
            {
                "strict": True,
                "relaxed": True,
                "skills": ["work"],
                "scripts": ["scripts/review/cross-review.sh", "scripts/work-queue/close-item.sh"],
                "gate_signals": {"init": True, "cross_review": True},
            }
        ],
    }
    report = mod.build_report(fixture)
    assert report["required_signals"] >= 20
    assert "agent_cross_review" in {r["signal"] for r in report["rows"]}
    assert "plan_html_review_draft" in report["missing_required_signals"]


def test_inference_detects_agent_cross_review_and_close_archive():
    mod = _load_module()
    session = {
        "strict": False,
        "relaxed": True,
        "skills": ["work"],
        "scripts": [
            "scripts/review/cross-review.sh",
            "scripts/review/submit-to-codex.sh",
            "scripts/work-queue/close-item.sh",
            "scripts/work-queue/archive-item.sh",
        ],
        "gate_signals": {},
    }
    assert mod._session_infers_signal(session, "agent_cross_review") is True
    assert mod._session_infers_signal(session, "close_item") is True
    assert mod._session_infers_signal(session, "archive_item") is True
