"""Tests for GTM scan retention helpers (#1709)."""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = REPO_ROOT / "scripts" / "gtm" / "job-market-scanner.py"
SPEC = importlib.util.spec_from_file_location("job_market_scanner_retention", SCRIPT_PATH)
module = importlib.util.module_from_spec(SPEC)
sys.modules["job_market_scanner_retention"] = module
assert SPEC and SPEC.loader
SPEC.loader.exec_module(module)


def test_enforce_retention_moves_old_raw_results_and_prunes_history(tmp_path, monkeypatch):
    output_dir = tmp_path / "job-market-scan"
    raw_dir = output_dir / "raw-results"
    archive_dir = output_dir / "archive"
    raw_dir.mkdir(parents=True)
    archive_dir.mkdir(parents=True)

    old_file = raw_dir / "2025-01-01.json"
    recent_file = raw_dir / "2026-03-20.json"
    old_file.write_text("{}")
    recent_file.write_text("{}")

    cumulative_path = output_dir / "cumulative-index.json"
    cumulative_path.write_text(json.dumps({
        "jobs": {},
        "scan_history": [
            {"date": "2025-01-01", "total_jobs": 10},
            {"date": "2026-03-20", "total_jobs": 5},
        ],
        "company_history": {
            "Acme": [
                {"date": "2025-01-01", "count": 4},
                {"date": "2026-03-20", "count": 2},
            ]
        },
    }))

    monkeypatch.setattr(module, "OUTPUT_DIR", output_dir)
    monkeypatch.setattr(module, "RAW_DIR", raw_dir)
    monkeypatch.setattr(module, "CUMULATIVE_PATH", cumulative_path)
    monkeypatch.setattr(module, "ARCHIVE_DIR", archive_dir)

    summary = module.enforce_retention_policy("2026-04-03")

    assert summary["archived_raw_results"] == 1
    assert not old_file.exists()
    assert (archive_dir / old_file.name).exists()
    assert recent_file.exists()

    updated = json.loads(cumulative_path.read_text())
    assert len(updated["scan_history"]) == 1
    assert updated["scan_history"][0]["date"] == "2026-03-20"
    assert len(updated["company_history"]["Acme"]) == 1
    assert updated["company_history"]["Acme"][0]["date"] == "2026-03-20"
