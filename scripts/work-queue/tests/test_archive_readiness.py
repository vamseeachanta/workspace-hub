"""
Tests T1-T3: archive-readiness gate check (WRK-668).

T1: all gates satisfied → (True, ...)
T2: document-index absent with exemption note → (None, ...) soft-fail
T3: merge_status sentinel detected → (False, ...) hard-fail with spin-off recommended

Existing verifier regression: run test_gate_verifier_hardening.py and test_d_item_gates.py
alongside these tests to confirm --phase archive changes do not break the close/claim phases.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
SCRIPTS_DIR = REPO_ROOT / "scripts" / "work-queue"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from gate_checks_archive import check_archive_readiness  # type: ignore[import]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _write_archive_tooling(assets: Path, **overrides) -> None:
    """Write a minimal valid archive-tooling.yaml into assets/evidence/."""
    evidence = assets / "evidence"
    evidence.mkdir(parents=True, exist_ok=True)
    data = {
        "merge_status": "merged-to-main",
        "sync_status": "in-sync",
        "html_verification_ref": str(assets / "WRK-000-lifecycle.html"),
        "legal_scan_ref": str(assets / "evidence" / "legal-scan.md"),
        "document_index_ref": "hooks/post-archive-index.sh",
        "archive_readiness": "pass",
    }
    data.update(overrides)
    (evidence / "archive-tooling.yaml").write_text(
        "\n".join(f"{k}: {v}" for k, v in data.items()) + "\n"
    )


# ---------------------------------------------------------------------------
# T1: all gates satisfied → PASS
# ---------------------------------------------------------------------------

class TestT1ArchivePass:
    def test_archive_pass_returns_true(self, tmp_path):
        """T1: archive-tooling.yaml with all gates satisfied → (True, ...)."""
        assets = tmp_path / "assets" / "WRK-000"
        assets.mkdir(parents=True)
        # Create referenced files so path checks pass
        (assets / "WRK-000-lifecycle.html").write_text("<html/>")
        (assets / "evidence").mkdir()
        (assets / "evidence" / "legal-scan.md").write_text("PASS")
        _write_archive_tooling(assets)

        ok, msg = check_archive_readiness(assets)

        assert ok is True
        assert "pass" in msg.lower()


# ---------------------------------------------------------------------------
# T2: soft-fail — document_index_ref absent but exemption note present → WARN
# ---------------------------------------------------------------------------

class TestT2SoftFailWorkaround:
    def test_archive_soft_fail_document_index_absent_with_exemption(self, tmp_path):
        """T2: document_index_ref absent, exemption_note present → (None, ...) soft-fail."""
        assets = tmp_path / "assets" / "WRK-000"
        assets.mkdir(parents=True)
        (assets / "WRK-000-lifecycle.html").write_text("<html/>")
        (assets / "evidence").mkdir()
        (assets / "evidence" / "legal-scan.md").write_text("PASS")
        _write_archive_tooling(
            assets,
            document_index_ref="",
            archive_readiness="soft-fail",
        )
        # Write exemption into archive-tooling.yaml
        tooling_path = assets / "evidence" / "archive-tooling.yaml"
        tooling_path.write_text(
            tooling_path.read_text() + "document_index_exemption: no document-index hook needed (hub-only item)\n"
        )

        ok, msg = check_archive_readiness(assets)

        assert ok is None, f"Expected None (soft-fail), got {ok!r}: {msg}"
        assert "soft" in msg.lower() or "exempt" in msg.lower() or "warn" in msg.lower()


# ---------------------------------------------------------------------------
# T3: hard-fail — merge_status is stub sentinel → FAIL, spin-off recommended
# ---------------------------------------------------------------------------

class TestT3HardFailSpinoff:
    def test_archive_hard_fail_merge_status_sentinel(self, tmp_path):
        """T3: merge_status='checked (manual)' sentinel detected → (False, ...) hard-fail."""
        assets = tmp_path / "assets" / "WRK-000"
        assets.mkdir(parents=True)
        (assets / "WRK-000-lifecycle.html").write_text("<html/>")
        (assets / "evidence").mkdir()
        (assets / "evidence" / "legal-scan.md").write_text("PASS")
        _write_archive_tooling(
            assets,
            merge_status="checked (manual)",
            archive_readiness="hard-fail",
        )

        ok, msg = check_archive_readiness(assets)

        assert ok is False, f"Expected False (hard-fail), got {ok!r}: {msg}"
        assert "merge" in msg.lower() or "sentinel" in msg.lower() or "stub" in msg.lower()
