"""GTM and contact outputs run without private host settings (owner decision S01).

The job-market scanner and the contact de-duplication report write to this
repository again, as before C19, with every name passed through the identifier
gate's redactor (scripts/legal/public_redaction.py): the redactor is the single
guard that keeps client and vendor names out. A host without the private
overlay or the private deny list runs instead of stopping. The classified
contact files, which hold addresses, stay in the private admin repository.

Every value in this file is synthetic.
"""
from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
SCAN_DIR = "docs/strategy/gtm/job-market-scan"
SYNTH = "zorblaxcorp"


def _load(rel: str, name: str):
    spec = importlib.util.spec_from_file_location(name, REPO_ROOT / rel)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def no_private_config(tmp_path, monkeypatch):
    """No overlay and no private deny list on this host."""
    from scripts.lib import private_overlay

    monkeypatch.setenv(private_overlay.ENV_VAR, str(tmp_path / "absent.json"))
    monkeypatch.delenv("WORKSPACE_HUB_DENY_LIST", raising=False)
    monkeypatch.delenv("LEGAL_CLIENT_MAP", raising=False)
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setenv("USERPROFILE", str(tmp_path))


@pytest.fixture
def deny_list(tmp_path, monkeypatch):
    p = tmp_path / "deny.txt"
    p.write_text(f"{SYNTH}\n", encoding="utf-8")
    monkeypatch.setenv("WORKSPACE_HUB_DENY_LIST", str(p))
    monkeypatch.delenv("LEGAL_CLIENT_MAP", raising=False)
    return p


# -- job-market scanner -------------------------------------------------------
def test_scanner_writes_to_the_repository_scan_directory_by_default(no_private_config):
    scanner = _load("scripts/gtm/job-market-scanner.py", "scanner_s01_default")
    assert scanner.OUTPUT_DIR == REPO_ROOT / SCAN_DIR
    assert scanner.RAW_DIR == REPO_ROOT / SCAN_DIR / "raw-results"
    assert scanner.CUMULATIVE_PATH == REPO_ROOT / SCAN_DIR / "cumulative-index.json"


def test_scanner_redacts_every_output_file(tmp_path, deny_list):
    scanner = _load("scripts/gtm/job-market-scanner.py", "scanner_s01_redact")
    out = tmp_path / "scan"
    (out / "raw-results").mkdir(parents=True)
    (out / "dashboard.md").write_text(f"| {SYNTH.title()} Offshore | 3 |\n", encoding="utf-8")
    (out / "raw-results" / "2026-09-28.json").write_text(
        json.dumps({"jobs": [{"company": f"{SYNTH} Ltd", "n": 1}]}), encoding="utf-8")
    scanner.redact_outputs(out)
    for f in (out / "dashboard.md", out / "raw-results" / "2026-09-28.json"):
        assert SYNTH not in f.read_text(encoding="utf-8").lower(), f.name
    json.loads((out / "raw-results" / "2026-09-28.json").read_text(encoding="utf-8"))


def test_scanner_redaction_runs_without_the_private_list(tmp_path, no_private_config):
    scanner = _load("scripts/gtm/job-market-scanner.py", "scanner_s01_public_rules")
    out = tmp_path / "scan"
    out.mkdir()
    (out / "dashboard.md").write_text("| Example Co | 3 |\n", encoding="utf-8")
    scanner.redact_outputs(out)
    assert (out / "dashboard.md").exists()


def test_weekly_refresh_commits_the_scan_directory_in_this_repository():
    text = (REPO_ROOT / "scripts/gtm/weekly-scan-refresh.sh").read_text(encoding="utf-8")
    assert "private_path_guard" not in text
    assert "--print-output-dir" not in text
    assert "outputs.job_market_dir" not in text
    assert SCAN_DIR in text


def test_scan_outputs_are_not_ignored():
    for rel in (f"{SCAN_DIR}/dashboard.md", f"{SCAN_DIR}/raw-results/2026-09-28.json",
                f"{SCAN_DIR}/cumulative-index.json"):
        r = subprocess.run(["git", "check-ignore", "-q", "--no-index", rel], cwd=REPO_ROOT)
        assert r.returncode != 0, rel


# -- contact de-duplication report --------------------------------------------
def test_contact_report_is_written_redacted_without_private_config(tmp_path, no_private_config):
    norm = _load("scripts/email/contact-normalizer.py", "contact_report_s01")
    path = norm.write_dedup_report(
        {"one@example.com", "both@example.org"}, {"two@example.net", "both@example.org"},
        out_dir=tmp_path,
    )
    text = path.read_text(encoding="utf-8")
    assert path.parent == tmp_path
    assert "Overlap=1" in text
    assert "@" not in text  # counts and domains only; no address


def test_contact_report_defaults_to_the_repository(no_private_config):
    norm = _load("scripts/email/contact-normalizer.py", "contact_report_s01_default")
    assert norm.DEDUP_REPORT_DIR == REPO_ROOT / "reports" / "email"


def test_contact_report_redacts_a_listed_domain(tmp_path, deny_list):
    norm = _load("scripts/email/contact-normalizer.py", "contact_report_s01_redact")
    path = norm.write_dedup_report({f"a@{SYNTH}.com"}, {f"a@{SYNTH}.com"}, out_dir=tmp_path)
    assert SYNTH not in path.read_text(encoding="utf-8").lower()


# -- licensed-run scripts do not stop on a missing scope setting ---------------
def test_licensed_run_scripts_have_no_scope_setting_gate():
    for bat in sorted((REPO_ROOT / "licensed-run").glob("*.bat")):
        for line in bat.read_text(encoding="utf-8").splitlines():
            assert not line.lower().startswith("if not defined licensed_run_scope"), bat.name


# -- the C19 private-destination machinery is gone ----------------------------
def test_private_destination_helpers_are_removed():
    from scripts.lib import private_overlay

    assert not hasattr(private_overlay, "require_output_dir")
    assert not hasattr(private_overlay, "check_private_dir")
    assert not (REPO_ROOT / "scripts/lib/private_path_guard.sh").exists()
