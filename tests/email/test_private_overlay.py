"""Private run-time overlay for owner-specific lists (C19, follows C15).

The public tree carries no client or contractor names, no client domains and no
real mailbox addresses. The owner's machines restore the earlier behaviour from a
private JSON file loaded at run time (``$WORKSPACE_HUB_PRIVATE_LISTS``, default
``~/.config/workspace-hub/private-lists.json``).

Every value in this file is synthetic.
"""
from __future__ import annotations

import importlib
import importlib.util
import json
import sys
from pathlib import Path

import pytest

from scripts.lib import private_overlay

REPO_ROOT = Path(__file__).resolve().parents[2]
ENV = private_overlay.ENV_VAR

SYNTH = {
    "version": 1,
    "email": {
        "vip_domains": {
            "ace": ["synthetic-client.test"],
            "skestates": ["synthetic-tenant.test"],
        },
        "client_domains": ["synthetic-client.test"],
        "domain_company": {"synthetic-client.test": "Synthetic Client Co"},
        "routing_rules": {
            "synthetic-client.test": "archive/docs/email/client-synthetic",
            "public.example.org": "archive/docs/email/overridden",
        },
        "mailboxes": {
            "ace": "ace-owner@example.com",
            "personal": "personal-owner@example.com",
            "skestates": "family-owner@example.com",
        },
    },
    "job_market": {
        "priority_companies": ["synthetic contractor"],
        "career_urls": {"Synthetic Contractor": "https://careers.synthetic.test/"},
    },
}


def _write(tmp_path: Path, payload) -> Path:
    path = tmp_path / "private-lists.json"
    path.write_text(
        payload if isinstance(payload, str) else json.dumps(payload),
        encoding="utf-8",
    )
    return path


def _load_script(rel: str, name: str):
    spec = importlib.util.spec_from_file_location(name, REPO_ROOT / rel)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def overlay_env(tmp_path, monkeypatch):
    path = _write(tmp_path, SYNTH)
    monkeypatch.setenv(ENV, str(path))
    return path


@pytest.fixture
def no_overlay_env(tmp_path, monkeypatch):
    monkeypatch.setenv(ENV, str(tmp_path / "absent.json"))


@pytest.fixture
def oauth_env(monkeypatch):
    monkeypatch.setenv("GMAIL_OAUTH_CLIENT_ID", "synthetic-id")
    monkeypatch.setenv("GMAIL_OAUTH_CLIENT_SECRET", "synthetic-secret")


# --------------------------------------------------------------------------
# loader contract
# --------------------------------------------------------------------------
def test_default_path_is_under_user_config(monkeypatch):
    monkeypatch.delenv(ENV, raising=False)
    path = private_overlay.resolve_path()
    assert path.parts[-3:] == (".config", "workspace-hub", "private-lists.json")


def test_env_var_overrides_path(tmp_path, monkeypatch):
    monkeypatch.setenv(ENV, str(tmp_path / "x.json"))
    assert private_overlay.resolve_path() == tmp_path / "x.json"


def test_absent_file_is_the_documented_empty_overlay(no_overlay_env):
    overlay = private_overlay.load()
    assert overlay == {}
    assert private_overlay.get_list(overlay, "job_market.priority_companies") == []
    assert private_overlay.get_mapping(overlay, "email.routing_rules") == {}


def test_valid_file_loads(overlay_env):
    overlay = private_overlay.load()
    assert private_overlay.get_list(overlay, "email.client_domains") == [
        "synthetic-client.test"
    ]
    assert private_overlay.get_mapping(overlay, "email.mailboxes")["skestates"] == (
        "family-owner@example.com"
    )


@pytest.mark.parametrize(
    "payload",
    [
        "{not json",
        "[]",
        {"version": 2},
        {"version": 1, "unknown_section": {}},
        {"version": 1, "email": {"unknown_key": []}},
        {"version": 1, "email": {"client_domains": "not-a-list"}},
        {"version": 1, "email": {"client_domains": [1, 2]}},
        {"version": 1, "email": {"routing_rules": ["not", "a", "mapping"]}},
        {"version": 1, "email": {"vip_domains": {"ace": "not-a-list"}}},
        {"version": 1, "job_market": {"career_urls": {"A": 3}}},
    ],
)
def test_malformed_file_fails_closed(tmp_path, monkeypatch, payload):
    monkeypatch.setenv(ENV, str(_write(tmp_path, payload)))
    with pytest.raises(private_overlay.PrivateOverlayError) as exc:
        private_overlay.load()
    # The error names the path, never the file contents.
    assert "synthetic" not in str(exc.value)


# --------------------------------------------------------------------------
# consumers: behaviour restored with the overlay, public defaults without it
# --------------------------------------------------------------------------
def test_account_scope_default_mailbox_comes_from_overlay(overlay_env):
    accounts = importlib.reload(importlib.import_module("scripts.email.state.accounts"))
    scope = accounts.AccountScope.default()
    assert scope.normalize("family-owner@example.com").alias == "skestates"
    assert scope.cleanup_enabled("family-owner@example.com") is False


def test_account_scope_default_without_overlay_carries_no_address(no_overlay_env):
    accounts = importlib.reload(importlib.import_module("scripts.email.state.accounts"))
    scope = accounts.AccountScope.default()
    assert scope.accounts["skestates"].email is None
    assert scope.normalize("skestates").alias == "skestates"
    assert scope.normalize("family-owner@example.com").status == "config_missing"


def test_digest_vip_domains_and_mailboxes_from_overlay(overlay_env, oauth_env):
    digest = _load_script("scripts/email/gmail-digest.py", "gmail_digest_c19")
    assert "synthetic-client.test" in digest.ACE_VIP_DOMAINS
    assert "synthetic-tenant.test" in digest.SKESTATES_VIP_DOMAINS
    assert digest.ACCOUNTS["skestates"]["email"] == "family-owner@example.com"


def test_digest_without_overlay_keeps_public_defaults(no_overlay_env, oauth_env):
    digest = _load_script("scripts/email/gmail-digest.py", "gmail_digest_c19_bare")
    assert "synthetic-client.test" not in digest.ACE_VIP_DOMAINS
    assert "shell.com" in digest.ACE_VIP_DOMAINS
    assert digest.ACCOUNTS["ace"]["email"].endswith("@example.com")


def test_archive_extract_routing_overlay_wins(overlay_env):
    extract = _load_script("scripts/email/gmail-archive-extract.py", "gmail_extract_c19")
    rules = extract.load_routing()
    assert rules["synthetic-client.test"] == "archive/docs/email/client-synthetic"
    assert rules["public.example.org"] == "archive/docs/email/overridden"
    # public rules still load
    assert rules["sandsig.com"] == "assethold/data/cre-listings"
    assert extract.ACCOUNTS["ace"]["email"] == "ace-owner@example.com"


def test_archive_extract_public_routing_has_no_placeholder_rules(no_overlay_env):
    extract = _load_script("scripts/email/gmail-archive-extract.py", "gmail_extract_c19_bare")
    rules = extract.load_routing()
    assert not any("installation-contractor" in k or "installation-contractor" in v
                   for k, v in rules.items())


def test_contact_normalizer_client_domains_from_overlay(overlay_env):
    norm = _load_script("scripts/email/contact-normalizer.py", "contact_normalizer_c19")
    assert norm.infer_category_ace("synthetic-client.test") == "client"
    assert norm.infer_company("synthetic-client.test") == "Synthetic Client Co"


def test_contact_normalizer_without_overlay(no_overlay_env):
    norm = _load_script("scripts/email/contact-normalizer.py", "contact_normalizer_c19_bare")
    assert norm.infer_category_ace("synthetic-client.test") == "unknown"
    assert norm.infer_category_ace("shell.com") == "client"


def test_job_market_priority_and_career_urls_from_overlay(overlay_env):
    scanner = _load_script("scripts/gtm/job-market-scanner.py", "job_market_scanner_c19")
    assert scanner.is_priority_company("Synthetic Contractor Ltd")
    assert scanner.COMPANY_CAREER_URLS["Synthetic Contractor"] == (
        "https://careers.synthetic.test/"
    )


def test_job_market_without_overlay(no_overlay_env):
    scanner = _load_script("scripts/gtm/job-market-scanner.py", "job_market_scanner_c19_bare")
    assert not scanner.is_priority_company("Synthetic Contractor Ltd")
    assert scanner.is_priority_company("Subsea7 Inc")


# --------------------------------------------------------------------------
# Codex r1 (C19): absent overlay -> read-only fallback only; destructive and
# routing-to-repo actions fail closed; degraded priority warns once.
# --------------------------------------------------------------------------
import argparse  # noqa: E402
import os  # noqa: E402
import subprocess  # noqa: E402


def _stderr_lines(text: str) -> list[str]:
    return [ln for ln in text.splitlines() if ln.strip()]


def test_is_present_follows_the_resolved_path(tmp_path, monkeypatch):
    monkeypatch.setenv(ENV, str(tmp_path / "absent.json"))
    assert private_overlay.is_present() is False
    monkeypatch.setenv(ENV, str(_write(tmp_path, SYNTH)))
    assert private_overlay.is_present() is True


def test_require_present_fails_closed_naming_no_values(tmp_path, no_overlay_env):
    with pytest.raises(private_overlay.PrivateOverlayAbsent) as exc:
        private_overlay.require_present("archive mail to a repository")
    msg = str(exc.value)
    assert "absent" in msg and "refusing to archive mail to a repository" in msg
    assert str(tmp_path) not in msg
    assert isinstance(exc.value, private_overlay.PrivateOverlayError)


def test_require_present_passes_with_overlay(overlay_env):
    private_overlay.require_present("archive mail to a repository")


def test_warn_if_absent_prints_one_line(no_overlay_env, capsys, tmp_path):
    assert private_overlay.warn_if_absent("VIP priority") is True
    err = _stderr_lines(capsys.readouterr().err)
    assert len(err) == 1
    assert "private overlay absent" in err[0] and "VIP priority" in err[0]
    assert str(tmp_path) not in err[0]


def test_warn_if_absent_silent_with_overlay(overlay_env, capsys):
    assert private_overlay.warn_if_absent("VIP priority") is False
    assert capsys.readouterr().err == ""


# gmail-archive-extract: --delete, archiving to a repo -> fail closed ----------
@pytest.mark.parametrize("delete,dry_run", [(True, False), (False, False), (True, True)])
def test_archive_extract_gate_fails_closed_without_overlay(no_overlay_env, capsys,
                                                           tmp_path, delete, dry_run):
    extract = _load_script("scripts/email/gmail-archive-extract.py", "gmail_extract_gate_a")
    with pytest.raises(SystemExit) as exc:
        extract.overlay_gate(argparse.Namespace(delete=delete, dry_run=dry_run))
    assert exc.value.code == 2
    err = capsys.readouterr().err
    assert "private overlay absent" in err and "refusing" in err
    assert str(tmp_path) not in err


def test_archive_extract_dry_run_degrades_with_warning(no_overlay_env, capsys):
    extract = _load_script("scripts/email/gmail-archive-extract.py", "gmail_extract_gate_b")
    capsys.readouterr()
    extract.overlay_gate(argparse.Namespace(delete=False, dry_run=True))
    err = _stderr_lines(capsys.readouterr().err)
    assert len(err) == 1 and "private overlay absent" in err[0]


@pytest.mark.parametrize("delete,dry_run", [(True, False), (False, False), (False, True)])
def test_archive_extract_gate_passes_with_overlay(overlay_env, capsys, delete, dry_run):
    extract = _load_script("scripts/email/gmail-archive-extract.py", "gmail_extract_gate_c")
    capsys.readouterr()
    extract.overlay_gate(argparse.Namespace(delete=delete, dry_run=dry_run))
    assert capsys.readouterr().err == ""


def _run_script(rel: str, *args: str, env_extra: dict) -> subprocess.CompletedProcess:
    env = dict(os.environ)
    env.update(env_extra)
    env["PYTHONPATH"] = str(REPO_ROOT)
    return subprocess.run([sys.executable, str(REPO_ROOT / rel), *args],
                          capture_output=True, text=True, env=env, cwd=str(REPO_ROOT))


def test_archive_extract_delete_cli_exits_before_any_request(tmp_path):
    r = _run_script("scripts/email/gmail-archive-extract.py",
                    "--account", "ace", "--query", "in:inbox", "--delete",
                    env_extra={ENV: str(tmp_path / "absent.json"),
                               "HOME": str(tmp_path), "USERPROFILE": str(tmp_path)})
    assert r.returncode == 2, r.stderr
    assert "refusing" in r.stderr
    assert str(tmp_path) not in r.stdout + r.stderr


# contact-normalizer writes classified contact files into a repository ---------
def test_contact_normalizer_write_fails_closed_without_overlay(tmp_path):
    r = _run_script("scripts/email/contact-normalizer.py",
                    env_extra={ENV: str(tmp_path / "absent.json")})
    assert r.returncode == 2, r.stderr
    assert "private overlay absent" in r.stderr and "refusing" in r.stderr
    assert str(tmp_path) not in r.stdout + r.stderr


def test_contact_normalizer_write_gate_passes_with_overlay(overlay_env):
    norm = _load_script("scripts/email/contact-normalizer.py", "contact_normalizer_gate")
    norm.require_overlay_for_write()


# VIP and job-market priority degrade with a one-line warning ------------------
def test_digest_warns_once_without_overlay(no_overlay_env, oauth_env, capsys):
    _load_script("scripts/email/gmail-digest.py", "gmail_digest_warn_a")
    err = [ln for ln in _stderr_lines(capsys.readouterr().err) if "private overlay" in ln]
    assert len(err) == 1 and "absent" in err[0]


def test_digest_silent_with_overlay(overlay_env, oauth_env, capsys):
    _load_script("scripts/email/gmail-digest.py", "gmail_digest_warn_b")
    assert "private overlay" not in capsys.readouterr().err


def test_job_market_warns_once_without_overlay(no_overlay_env, capsys):
    _load_script("scripts/gtm/job-market-scanner.py", "job_market_warn_a")
    err = [ln for ln in _stderr_lines(capsys.readouterr().err) if "private overlay" in ln]
    assert len(err) == 1 and "absent" in err[0]


def test_job_market_silent_with_overlay(overlay_env, capsys):
    _load_script("scripts/gtm/job-market-scanner.py", "job_market_warn_b")
    assert "private overlay" not in capsys.readouterr().err


# --------------------------------------------------------------------------
# Codex r1 (C19): forward compatibility with the #3899 'outputs' section
# --------------------------------------------------------------------------
SYNTH_3899 = {**SYNTH, "outputs": {"job_market_dir": "/synthetic/private/job-market",
                                    "contact_report_dir": "/synthetic/private/contacts"}}


def test_outputs_section_is_a_known_section(tmp_path, monkeypatch):
    monkeypatch.setenv(ENV, str(_write(tmp_path, SYNTH_3899)))
    overlay = private_overlay.load()
    assert overlay["outputs"]["job_market_dir"] == "/synthetic/private/job-market"
    assert "outputs" in private_overlay.KNOWN_SECTIONS


@pytest.mark.parametrize("payload", [
    {"version": 1, "outputs": {"job_market_dir": ["not", "a", "string"]}},
    {"version": 1, "outputs": {"contact_report_dir": 3}},
    {"version": 1, "outputs": {"unknown_output": "/x"}},
    {"version": 1, "outputs": "not-an-object"},
])
def test_outputs_section_is_still_validated(tmp_path, monkeypatch, payload):
    monkeypatch.setenv(ENV, str(_write(tmp_path, payload)))
    with pytest.raises(private_overlay.PrivateOverlayError):
        private_overlay.load()


def test_config_written_for_3899_loads_in_every_3898_consumer(tmp_path, monkeypatch,
                                                                oauth_env):
    monkeypatch.setenv(ENV, str(_write(tmp_path, SYNTH_3899)))
    importlib.reload(importlib.import_module("scripts.email.state.accounts")) \
        .AccountScope.default()
    assert "synthetic-client.test" in _load_script(
        "scripts/email/gmail-digest.py", "fwd_digest").ACE_VIP_DOMAINS
    assert _load_script("scripts/email/gmail-archive-extract.py", "fwd_extract") \
        .load_routing()["synthetic-client.test"].startswith("archive/")
    assert _load_script("scripts/email/contact-normalizer.py", "fwd_norm") \
        .infer_category_ace("synthetic-client.test") == "client"
    assert _load_script("scripts/gtm/job-market-scanner.py", "fwd_scanner") \
        .is_priority_company("Synthetic Contractor Ltd")