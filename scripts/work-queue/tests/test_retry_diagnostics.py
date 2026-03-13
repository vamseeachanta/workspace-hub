#!/usr/bin/env python3
"""Tests for WRK-1160: gate verification retry diagnostics and attempt tracking."""

import importlib.util
import io
import sys
import contextlib
from pathlib import Path
from unittest.mock import patch

# Ensure module is importable (hyphenated filename requires importlib)
REPO_ROOT = Path(__file__).resolve().parents[3]
SCRIPTS_DIR = REPO_ROOT / "scripts" / "work-queue"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

_spec = importlib.util.spec_from_file_location(
    "verify_gate_evidence",
    SCRIPTS_DIR / "verify-gate-evidence.py",
)
vge = importlib.util.module_from_spec(_spec)  # type: ignore[arg-type]
_spec.loader.exec_module(vge)  # type: ignore[union-attr]


def test_run_checks_with_retry_outputs_attempt_count_on_failure():
    """AC4: After max retries, output includes GATE_ATTEMPTS=N for log signal parsing."""
    buf = io.StringIO()
    with patch.object(vge, "run_checks", return_value=1):
        with contextlib.redirect_stdout(buf):
            with contextlib.redirect_stderr(buf):
                code, attempts = vge.run_checks_with_retry(
                    "WRK-TEST", phase="close", max_retries=3
                )
    output = buf.getvalue()
    assert code == 1
    assert attempts == 3
    assert "GATE_ATTEMPTS=3" in output


def test_run_checks_with_retry_no_attempt_marker_on_success():
    """On first-attempt success, no GATE_ATTEMPTS marker needed."""
    buf = io.StringIO()
    with patch.object(vge, "run_checks", return_value=0):
        with contextlib.redirect_stdout(buf):
            code, attempts = vge.run_checks_with_retry(
                "WRK-TEST", phase="close", max_retries=3
            )
    output = buf.getvalue()
    assert code == 0
    assert attempts == 1


def test_run_checks_with_retry_shows_unmet_gates_per_attempt():
    """AC1: Each failed attempt shows which specific gates are unmet."""
    call_count = 0

    def mock_run_checks(wrk_id, phase="close", workspace_root=None):
        nonlocal call_count
        call_count += 1
        print(f"Gate evidence for {wrk_id} (phase={phase}, assets: /tmp):")
        print("  - Plan gate: MISSING (reviewed=False)")
        print("  - TDD gate: OK (test files=['test.md'])")
        return 1

    buf = io.StringIO()
    with patch.object(vge, "run_checks", side_effect=mock_run_checks):
        with contextlib.redirect_stdout(buf):
            with contextlib.redirect_stderr(buf):
                code, attempts = vge.run_checks_with_retry(
                    "WRK-TEST", phase="close", max_retries=2
                )
    output = buf.getvalue()
    assert code == 1
    assert "unmet gates:" in output
    assert "Plan gate" in output


def test_run_checks_with_retry_shows_delta_between_attempts():
    """AC5: Delta output shows which gates changed status between attempts."""
    attempt = 0

    def mock_run_checks(wrk_id, phase="close", workspace_root=None):
        nonlocal attempt
        attempt += 1
        print(f"Gate evidence for {wrk_id} (phase={phase}, assets: /tmp):")
        if attempt == 1:
            print("  - Plan gate: MISSING (reviewed=False)")
            print("  - TDD gate: MISSING (none)")
        else:
            print("  - Plan gate: OK (reviewed=True)")
            print("  - TDD gate: MISSING (none)")
        return 1 if attempt < 3 else 0

    buf = io.StringIO()
    with patch.object(vge, "run_checks", side_effect=mock_run_checks):
        with contextlib.redirect_stdout(buf):
            with contextlib.redirect_stderr(buf):
                code, attempts = vge.run_checks_with_retry(
                    "WRK-TEST", phase="close", max_retries=3
                )
    output = buf.getvalue()
    assert "delta: Plan gate: MISSING -> OK" in output


def test_run_checks_with_retry_backoff_schedule():
    """AC2: Backoff is 1s, 3s, 9s (3^i for i=0,1,2)."""
    sleep_calls = []

    def mock_sleep(seconds):
        sleep_calls.append(seconds)

    with patch.object(vge, "run_checks", return_value=1):
        with patch("time.sleep", side_effect=mock_sleep):
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                with contextlib.redirect_stderr(buf):
                    vge.run_checks_with_retry(
                        "WRK-TEST", phase="close", max_retries=3
                    )
    # 3 attempts = 2 sleeps (no sleep after last attempt)
    assert sleep_calls == [1, 3]


def test_run_checks_with_retry_caps_at_max():
    """AC2: Retry is capped — never exceeds max_retries."""
    call_count = 0

    def mock_run_checks(wrk_id, phase="close", workspace_root=None):
        nonlocal call_count
        call_count += 1
        return 1

    with patch.object(vge, "run_checks", side_effect=mock_run_checks):
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            with contextlib.redirect_stderr(buf):
                code, attempts = vge.run_checks_with_retry(
                    "WRK-TEST", phase="close", max_retries=3
                )
    assert call_count == 3
    assert attempts == 3
    assert code == 1
