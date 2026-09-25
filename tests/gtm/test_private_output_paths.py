"""Generated GTM and contact outputs go to a private destination (C19 findings).

The job-market scanner's outputs and the contact de-duplication report name
employers, contractors, client domains and mailbox addresses. They are written
to a private repository whose location is read at run time from the private
overlay (``outputs.job_market_dir`` and ``outputs.contact_report_dir``). An
absent, relative, missing or in-repository destination fails closed: nothing is
written and the error names the key, never a value.

Every value in this file is synthetic.
"""
from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest

from scripts.lib import private_overlay

REPO_ROOT = Path(__file__).resolve().parents[2]
ENV = private_overlay.ENV_VAR
SCAN_DIR = "docs/strategy/gtm/job-market-scan"


def _overlay(tmp_path: Path, outputs: dict | None) -> Path:
    payload: dict = {"version": 1}
    if outputs is not None:
        payload["outputs"] = outputs
    path = tmp_path / "private-lists.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def _load(rel: str, name: str):
    spec = importlib.util.spec_from_file_location(name, REPO_ROOT / rel)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def private_dir(tmp_path):
    target = tmp_path / "private-repo" / "gtm"
    target.mkdir(parents=True)
    return target


# --------------------------------------------------------------------------
# overlay helper
# --------------------------------------------------------------------------
def test_outputs_section_is_part_of_the_schema(tmp_path, monkeypatch, private_dir):
    monkeypatch.setenv(ENV, str(_overlay(tmp_path, {"job_market_dir": str(private_dir)})))
    overlay = private_overlay.load()
    assert private_overlay.require_output_dir(
        overlay, "outputs.job_market_dir", public_root=REPO_ROOT
    ) == private_dir.resolve()


def test_outputs_value_must_be_a_string(tmp_path, monkeypatch):
    monkeypatch.setenv(ENV, str(_overlay(tmp_path, {"job_market_dir": ["x"]})))
    with pytest.raises(private_overlay.PrivateOverlayError):
        private_overlay.load()


def test_unknown_outputs_key_fails_closed(tmp_path, monkeypatch):
    monkeypatch.setenv(ENV, str(_overlay(tmp_path, {"elsewhere_dir": "/x"})))
    with pytest.raises(private_overlay.PrivateOverlayError):
        private_overlay.load()


def test_absent_destination_fails_closed_and_names_the_key():
    with pytest.raises(private_overlay.PrivateOverlayError) as exc:
        private_overlay.require_output_dir({}, "outputs.job_market_dir", public_root=REPO_ROOT)
    assert "outputs.job_market_dir" in str(exc.value)


def test_relative_destination_fails_closed():
    overlay = {"version": 1, "outputs": {"job_market_dir": "relative/synthetic-dir"}}
    with pytest.raises(private_overlay.PrivateOverlayError) as exc:
        private_overlay.require_output_dir(overlay, "outputs.job_market_dir", public_root=REPO_ROOT)
    assert "synthetic-dir" not in str(exc.value)


def test_missing_destination_fails_closed(tmp_path):
    overlay = {"version": 1, "outputs": {"job_market_dir": str(tmp_path / "synthetic-absent")}}
    with pytest.raises(private_overlay.PrivateOverlayError) as exc:
        private_overlay.require_output_dir(overlay, "outputs.job_market_dir", public_root=REPO_ROOT)
    assert "synthetic-absent" not in str(exc.value)


def test_destination_inside_the_public_repository_fails_closed():
    inside = REPO_ROOT / "docs"
    overlay = {"version": 1, "outputs": {"job_market_dir": str(inside)}}
    with pytest.raises(private_overlay.PrivateOverlayError):
        private_overlay.require_output_dir(overlay, "outputs.job_market_dir", public_root=REPO_ROOT)


# --------------------------------------------------------------------------
# job-market scanner
# --------------------------------------------------------------------------
def test_scanner_import_does_not_point_at_the_public_tree(tmp_path, monkeypatch):
    monkeypatch.setenv(ENV, str(tmp_path / "absent.json"))
    scanner = _load("scripts/gtm/job-market-scanner.py", "scanner_outputs_bare")
    assert scanner.OUTPUT_DIR is None
    assert scanner.RAW_DIR is None
    assert scanner.CUMULATIVE_PATH is None


def test_scanner_without_private_destination_fails_closed(tmp_path, monkeypatch):
    monkeypatch.setenv(ENV, str(tmp_path / "absent.json"))
    scanner = _load("scripts/gtm/job-market-scanner.py", "scanner_outputs_absent")
    with pytest.raises(private_overlay.PrivateOverlayError):
        scanner.resolve_output_dir(None)


def test_scanner_uses_the_private_destination(tmp_path, monkeypatch, private_dir):
    monkeypatch.setenv(ENV, str(_overlay(tmp_path, {"job_market_dir": str(private_dir)})))
    scanner = _load("scripts/gtm/job-market-scanner.py", "scanner_outputs_private")
    out = scanner.resolve_output_dir(None)
    scanner.configure_output_dir(out)
    assert scanner.OUTPUT_DIR == private_dir.resolve()
    assert scanner.RAW_DIR == private_dir.resolve() / "raw-results"
    assert scanner.ARCHIVE_DIR == private_dir.resolve() / "archive"
    assert scanner.CUMULATIVE_PATH == private_dir.resolve() / "cumulative-index.json"


def test_scanner_explicit_output_dir_inside_the_public_repository_is_refused(tmp_path, monkeypatch):
    monkeypatch.setenv(ENV, str(tmp_path / "absent.json"))
    scanner = _load("scripts/gtm/job-market-scanner.py", "scanner_outputs_inside")
    with pytest.raises(private_overlay.PrivateOverlayError):
        scanner.resolve_output_dir(str(REPO_ROOT / SCAN_DIR))


def test_scanner_explicit_output_dir_outside_the_repository_is_used(tmp_path, monkeypatch, private_dir):
    monkeypatch.setenv(ENV, str(tmp_path / "absent.json"))
    scanner = _load("scripts/gtm/job-market-scanner.py", "scanner_outputs_explicit")
    assert scanner.resolve_output_dir(str(private_dir)) == private_dir.resolve()


def test_scanner_print_output_dir_fails_closed_without_overlay(tmp_path):
    env = {k: v for k, v in __import__("os").environ.items()}
    env[ENV] = str(tmp_path / "absent.json")
    proc = subprocess.run(
        [sys.executable, str(REPO_ROOT / "scripts/gtm/job-market-scanner.py"), "--print-output-dir"],
        capture_output=True, text=True, env=env, cwd=str(REPO_ROOT),
    )
    assert proc.returncode != 0
    assert proc.stdout.strip() == ""


def test_scanner_print_output_dir_prints_the_private_destination(tmp_path, private_dir):
    env = {k: v for k, v in __import__("os").environ.items()}
    env[ENV] = str(_overlay(tmp_path, {"job_market_dir": str(private_dir)}))
    proc = subprocess.run(
        [sys.executable, str(REPO_ROOT / "scripts/gtm/job-market-scanner.py"), "--print-output-dir"],
        capture_output=True, text=True, env=env, cwd=str(REPO_ROOT),
    )
    assert proc.returncode == 0, proc.stderr
    assert Path(proc.stdout.strip()) == private_dir.resolve()


def test_weekly_refresh_commits_to_the_private_destination_only():
    text = (REPO_ROOT / "scripts/gtm/weekly-scan-refresh.sh").read_text(encoding="utf-8")
    assert "--print-output-dir" in text
    assert SCAN_DIR + "/raw-results" not in text
    assert "git add \\\n    docs/" not in text
    # the wrapper refuses a destination inside this repository
    assert "inside this public repository" in text


# --------------------------------------------------------------------------
# contact de-duplication report
# --------------------------------------------------------------------------
def test_contact_report_without_private_destination_fails_closed(tmp_path, monkeypatch):
    monkeypatch.setenv(ENV, str(tmp_path / "absent.json"))
    norm = _load("scripts/email/contact-normalizer.py", "contact_report_absent")
    with pytest.raises(private_overlay.PrivateOverlayError):
        norm.write_dedup_report({"a@example.com"}, {"b@example.com"})


def test_contact_report_is_written_to_the_private_destination(tmp_path, monkeypatch, private_dir):
    monkeypatch.setenv(ENV, str(_overlay(tmp_path, {"contact_report_dir": str(private_dir)})))
    norm = _load("scripts/email/contact-normalizer.py", "contact_report_private")
    path = norm.write_dedup_report(
        {"one@example.com", "both@example.org"}, {"two@example.net", "both@example.org"}
    )
    assert path.parent == private_dir.resolve()
    text = path.read_text(encoding="utf-8")
    assert "Overlap=1" in text
    # counts and domains only; no address is written
    assert "@" not in text


# --------------------------------------------------------------------------
# the public tree carries no generated outputs
# --------------------------------------------------------------------------
def _tracked(prefix: str) -> list[str]:
    out = subprocess.run(["git", "ls-files", "--", prefix], cwd=REPO_ROOT,
                         capture_output=True, text=True, check=True).stdout
    return [p for p in out.splitlines() if p]


def test_public_scan_directory_holds_policy_documents_only():
    allowed = {f"{SCAN_DIR}/README.md", f"{SCAN_DIR}/RETENTION_POLICY.md", f"{SCAN_DIR}/TOS_REVIEW.md"}
    assert set(_tracked(SCAN_DIR)) <= allowed


def test_public_tree_holds_no_contact_report():
    assert _tracked("reports/email") == []
