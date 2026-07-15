"""Safety and interface contracts for the RDP microphone tool (#3524)."""

from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
ENTRYPOINT = REPO_ROOT / "scripts" / "windows" / "rdp-microphone.ps1"
MODULE = REPO_ROOT / "scripts" / "windows" / "lib" / "RdpMicrophone.psm1"
RUNBOOK = REPO_ROOT / "docs" / "runbooks" / "windows-rdp-microphone.md"


def test_expected_artifacts_exist():
    assert ENTRYPOINT.is_file()
    assert MODULE.is_file()
    assert RUNBOOK.is_file()


def test_entrypoint_is_a_commented_audit_first_tool():
    text = ENTRYPOINT.read_text(encoding="utf-8")
    assert ".SYNOPSIS" in text and ".DESCRIPTION" in text
    assert "[ValidateSet('Client', 'Server')]" in text
    assert "[ValidateSet('Json', 'Human')]" in text
    assert "[switch]$Repair" in text
    assert "[string]$ReportPath" in text
    assert "ConvertTo-Json" in text
    assert "Write-Host" not in text
    assert "Write-Information" not in text


def test_mutation_scope_excludes_policy_privacy_and_session_disruption():
    text = (ENTRYPOINT.read_text() + MODULE.read_text()).lower()
    forbidden = (
        "restart-service termservice",
        "stop-service termservice",
        "logoff.exe",
        "shutdown.exe",
        "set-itemproperty hklm:\\software\\policies",
        "new-itemproperty hklm:\\software\\policies",
        "set-itemproperty hkcu:\\software\\microsoft\\windows\\currentversion\\capabilityaccessmanager",
    )
    for token in forbidden:
        assert token not in text
    assert "privacy and machine policy are audit-only" in text


def test_profile_and_consent_repairs_are_explicit_and_reversible():
    entry = ENTRYPOINT.read_text()
    module = MODULE.read_text()
    assert "-Repair requires -RdpFile" in entry
    assert "BackupPath" in module
    assert "Restore-RdpMicConsentSnapshot" in module
    assert "SHA256" in module
    assert "LocalDevices" in module
    assert "audiocapturemode" in module


def test_readme_and_runbook_document_two_machine_sequence():
    readme = (REPO_ROOT / "scripts" / "windows" / "README.md").read_text()
    runbook = RUNBOOK.read_text()
    assert "rdp-microphone.ps1" in readme
    for token in ("WS014", "RDS02", "Remote Audio", "Win+H", "rollback"):
        assert token.lower() in runbook.lower()
