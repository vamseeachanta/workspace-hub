"""Reproducible synthetic example for the publication diagnostic.

Inputs, method and expected answer are documented in
docs/runbooks/equivalence-publication-evidence.md. This example uses no Git,
network, scheduler, authentication or solver. Run from the repository root:

    uv run --no-project --with pyyaml python tests/monitoring/equivalence_publish_example.py

The timestamp and duration are constructed inputs, not measured evidence.
"""
from __future__ import annotations

import importlib.util
import json
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location(
    "equivalence_publish_check", ROOT / "scripts/monitoring/equivalence_publish_check.py",
)
check = importlib.util.module_from_spec(spec)
spec.loader.exec_module(check)
from equivalence_schema import LEARNING_KEYS


def example():
    """Independent answer: 12:00 minus 11:00 is one hour; a 2s publish passes.

    Acceptance source: build-equality-matrix.py PUBLISH_STALE_H and
    PUBLISH_SLOW_S, the existing issue #3502 publish-health contract (2026).
    Versions/success codes: equivalence_schema.py validate_fingerprint and
    equivalence_state.py validate_publish_health version-1 contracts (2026).
    """
    fingerprint = {
        "fingerprint_version": 1, "machine_id": "example", "hostname": "example",
        "role": "contribute-minimal", "ts": "2026-10-22T11:00:00Z",
        "clone_head": None, "behind_origin": None, "ahead_origin": None,
        "harness_version": None, "harness_install": None, "registry_sha256": None,
        "learning_cron_ages_h": dict.fromkeys(LEARNING_KEYS),
        "provider_soul_hashes": dict.fromkeys(
            ("hermes", "claude", "codex", "codex_agents", "gemini")
        ),
        "on_main": True, "index_lock_stale_min": None, "last_publish_duration_s": None,
    }
    receipt = {
        "schema_version": 1, "ts": "2026-10-22T11:00:02Z", "phase": "publish",
        "duration_s": 2, "rc": 0,
    }
    report = {
        "machine": "example", "generated_at": "2026-10-22T11:01:00Z",
        "dimensions": {"publish_health": {
            "last_publish_at": receipt["ts"], "last_publish_duration_s": 2,
            "last_publish_rc": 0,
        }},
    }
    return check.assess(
        machine="example", published=json.dumps(fingerprint), local=json.dumps(fingerprint),
        health=json.dumps(receipt), report=report,
        now=datetime(2026, 10, 22, 12, tzinfo=UTC),
    )


if __name__ == "__main__":
    result = example()
    # The expected answer above is independent of the implementation.
    assert result["status"] == "PASS", result
    print(json.dumps(result, indent=2))
