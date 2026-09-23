"""Windows-native behavioral tests for the RDP microphone PowerShell module."""

from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import subprocess

import pytest


REPO_ROOT = Path(__file__).resolve().parents[2]
ENTRYPOINT = REPO_ROOT / "scripts" / "windows" / "rdp-microphone.ps1"
MODULE = REPO_ROOT / "scripts" / "windows" / "lib" / "RdpMicrophone.psm1"
FIXTURE = REPO_ROOT / "tests" / "readiness" / "fixtures" / "rdp-microphone" / "duplicate-capture.rdp"
EVENT_FIXTURES = REPO_ROOT / "tests" / "readiness" / "fixtures" / "rdp-microphone"
POWERSHELL = shutil.which("powershell") or shutil.which("pwsh")


pytestmark = pytest.mark.skipif(
    os.name != "nt" or POWERSHELL is None,
    reason="native Windows PowerShell is required",
)


def _run(command: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [POWERSHELL, "-NoLogo", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", command],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        timeout=60,
    )


def test_default_entrypoint_stdout_is_one_json_document(tmp_path: Path):
    result = subprocess.run(
        [POWERSHELL, "-NoLogo", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(ENTRYPOINT), "-Role", "Server"],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert result.returncode in (0, 2), result.stderr
    report = json.loads(result.stdout)
    assert report["Role"] == "Server"
    assert not list(tmp_path.glob("*.json"))


def test_duplicate_profile_repair_is_narrow_and_backed_up(tmp_path: Path):
    profile = tmp_path / "test.rdp"
    profile.write_bytes(FIXTURE.read_bytes())
    command = (
        f"Import-Module '{MODULE}' -Force; "
        f"$r=Repair-RdpMicProfile -Path '{profile}'; $r | ConvertTo-Json -Compress"
    )
    result = _run(command)
    assert result.returncode == 0, result.stderr
    outcome = json.loads(result.stdout)
    repaired = profile.read_text(encoding="utf-8")
    assert repaired.count("audiocapturemode:i:1") == 1
    assert "audiomode:i:0" in repaired
    assert "keyboardhook:i:1" in repaired
    backup = Path(outcome["BackupPath"])
    assert backup.read_bytes() == FIXTURE.read_bytes()


def test_profile_repair_preserves_utf16le_bom_and_crlf(tmp_path: Path):
    profile = tmp_path / "utf16.rdp"
    original_text = "full address:s:ace-win-1\r\naudiocapturemode:i:0\r\nkeyboardhook:i:1\r\n"
    profile.write_text(original_text, encoding="utf-16", newline="")
    original = profile.read_bytes()
    result = _run(
        f"Import-Module '{MODULE}' -Force; "
        f"Repair-RdpMicProfile -Path '{profile}' | ConvertTo-Json -Compress"
    )
    assert result.returncode == 0, result.stderr
    outcome = json.loads(result.stdout)
    with profile.open("r", encoding="utf-16", newline="") as stream:
        repaired = stream.read()
    assert repaired.count("audiocapturemode:i:1") == 1
    assert "\r\n" in repaired
    assert profile.read_bytes().startswith(b"\xff\xfe")
    assert Path(outcome["BackupPath"]).read_bytes() == original


def test_profile_whatif_does_not_write(tmp_path: Path):
    profile = tmp_path / "test.rdp"
    profile.write_bytes(FIXTURE.read_bytes())
    before = profile.read_bytes()
    result = _run(f"Import-Module '{MODULE}' -Force; Repair-RdpMicProfile -Path '{profile}' -WhatIf")
    assert result.returncode == 0, result.stderr
    assert profile.read_bytes() == before
    assert not list(tmp_path.glob("*.backup-*"))


@pytest.mark.parametrize(
    ("fault", "original_restored"),
    [("BeforeReplace", True), ("AfterReplace", True), ("RestoreFailure", False)],
)
def test_profile_replacement_faults_preserve_recovery_path(
    tmp_path: Path, fault: str, original_restored: bool
):
    profile = tmp_path / f"{fault}.rdp"
    profile.write_bytes(FIXTURE.read_bytes())
    original = profile.read_bytes()
    command = (
        f"$env:RDP_MIC_TEST_MODE='1'; Import-Module '{MODULE}' -Force; try{{Repair-RdpMicProfile -Path '{profile}' -FaultInjection '{fault}'|Out-Null}}"
        "catch{[pscustomobject]@{Caught=$true;Message=$_.Exception.Message}|ConvertTo-Json -Compress}"
    )
    result = _run(command)
    assert result.returncode == 0, result.stderr
    failure = json.loads(result.stdout)
    assert failure["Caught"] is True
    assert "BackupPath=" in failure["Message"]
    backups = list(tmp_path.glob("*.backup-*"))
    assert len(backups) == 1
    assert backups[0].read_bytes() == original
    assert (profile.read_bytes() == original) is original_restored


def test_profile_fault_injection_is_rejected_outside_test_mode(tmp_path: Path):
    profile = tmp_path / "test.rdp"
    profile.write_bytes(FIXTURE.read_bytes())
    result = _run(
        f"Remove-Item Env:RDP_MIC_TEST_MODE -ErrorAction SilentlyContinue; Import-Module '{MODULE}' -Force; "
        f"try{{Repair-RdpMicProfile -Path '{profile}' -FaultInjection BeforeReplace|Out-Null}}"
        "catch{[pscustomobject]@{Caught=$true;Message=$_.Exception.Message}|ConvertTo-Json -Compress}"
    )
    assert result.returncode == 0, result.stderr
    failure = json.loads(result.stdout)
    assert failure["Caught"] is True
    assert "disabled outside the native test harness" in failure["Message"]
    assert profile.read_bytes() == FIXTURE.read_bytes()
    assert not list(tmp_path.glob("*.backup-*"))


def test_entrypoint_whatif_remains_json_only_and_writes_nothing(tmp_path: Path):
    profile = tmp_path / "test.rdp"
    profile.write_bytes(FIXTURE.read_bytes())
    report_path = tmp_path / "should-not-exist.json"
    before = profile.read_bytes()
    result = subprocess.run(
        [
            POWERSHELL, "-NoLogo", "-NoProfile", "-ExecutionPolicy", "Bypass",
            "-File", str(ENTRYPOINT), "-Role", "Client", "-RdpFile", str(profile),
            "-ClientType", "Mstsc", "-ConfigurationSource", str(profile),
            "-Repair", "-WhatIf", "-ReportPath", str(report_path),
        ],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert result.returncode in (0, 2), result.stderr
    parsed = json.loads(result.stdout)
    assert parsed["Mode"] == "WhatIf"
    assert parsed["Changes"][0]["WhatIf"] is True
    assert profile.read_bytes() == before
    assert not report_path.exists()
    assert not list(tmp_path.glob("*.backup-*"))


def test_human_repair_prints_backup_and_rollback_details(tmp_path: Path):
    profile = tmp_path / "test.rdp"
    profile.write_bytes(FIXTURE.read_bytes())
    result = subprocess.run(
        [
            POWERSHELL, "-NoLogo", "-NoProfile", "-ExecutionPolicy", "Bypass",
            "-File", str(ENTRYPOINT), "-Role", "Client", "-RdpFile", str(profile),
            "-ClientType", "Mstsc", "-ConfigurationSource", str(profile),
            "-Repair", "-OutputFormat", "Human",
        ],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert result.returncode in (0, 2), result.stderr
    assert "CHANGE/ROLLBACK:" in result.stdout
    assert "BackupPath" in result.stdout
    assert list(tmp_path.glob("*.backup-*"))


@pytest.mark.parametrize("client_type", ["MSRDC", "WindowsApp"])
def test_modern_clients_refuse_classic_profile_repair(tmp_path: Path, client_type: str):
    profile = tmp_path / "test.rdp"
    profile.write_bytes(FIXTURE.read_bytes())
    result = subprocess.run(
        [
            POWERSHELL, "-NoLogo", "-NoProfile", "-ExecutionPolicy", "Bypass",
            "-File", str(ENTRYPOINT), "-Role", "Client", "-RdpFile", str(profile),
            "-ClientType", client_type, "-ConfigurationSource", str(profile), "-Repair",
        ],
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert result.returncode == 2
    report = json.loads(result.stdout)
    assert "only a proven classic mstsc profile" in report["Error"]
    assert profile.read_bytes() == FIXTURE.read_bytes()


def test_explicit_unknown_client_refuses_profile_repair(tmp_path: Path):
    profile = tmp_path / "test.rdp"
    profile.write_bytes(FIXTURE.read_bytes())
    result = subprocess.run(
        [
            POWERSHELL, "-NoLogo", "-NoProfile", "-ExecutionPolicy", "Bypass",
            "-File", str(ENTRYPOINT), "-Role", "Client", "-RdpFile", str(profile),
            "-ClientType", "Unknown", "-ConfigurationSource", str(profile), "-Repair",
        ],
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert result.returncode == 2
    report = json.loads(result.stdout)
    assert "only a proven classic mstsc profile" in report["Error"]
    assert profile.read_bytes() == FIXTURE.read_bytes()


def test_explicit_report_path_writes_parseable_json(tmp_path: Path):
    report_path = tmp_path / "server-audit.json"
    result = subprocess.run(
        [
            POWERSHELL, "-NoLogo", "-NoProfile", "-ExecutionPolicy", "Bypass",
            "-File", str(ENTRYPOINT), "-Role", "Server", "-ReportPath", str(report_path),
        ],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert result.returncode in (0, 2), result.stderr
    stdout_report = json.loads(result.stdout)
    file_report = json.loads(report_path.read_text(encoding="utf-8"))
    assert file_report["SchemaVersion"] == 1
    assert file_report["TimestampUtc"] == stdout_report["TimestampUtc"]


def test_unwritable_report_path_still_returns_structured_json(tmp_path: Path):
    impossible = tmp_path / "missing-parent" / "audit.json"
    result = subprocess.run(
        [
            POWERSHELL, "-NoLogo", "-NoProfile", "-ExecutionPolicy", "Bypass",
            "-File", str(ENTRYPOINT), "-Role", "Server", "-ReportPath", str(impossible),
        ],
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert result.returncode == 2
    report = json.loads(result.stdout)
    assert report["ExitCode"] == 2
    assert "ReportPath write failed" in report["Error"]


def test_event_classifier_fails_closed_without_correlation():
    events = json.dumps([
        {"RecordId": 11, "TimeUtc": "2026-07-14T11:00:01Z", "Channel": "AUDIO_INPUT", "State": "Connected"}
    ]).replace("'", "''")
    command = (
        f"Import-Module '{MODULE}' -Force; "
        f"$events=ConvertFrom-Json '{events}'; "
        "$r=Get-RdpMicEventVerdict -Events @($events) -AfterRecordId 10 -TargetCorrelation 'session-2'; "
        "$r | ConvertTo-Json -Compress"
    )
    result = _run(command)
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout)["Verdict"] == "inconclusive"


def test_event_classifier_separates_playback_from_empirical_input():
    events = json.dumps([
        {"RecordId": 11, "Correlation": "session-2", "Channel": "AUDIO_PLAYBACK_DVC", "State": "Connected"},
        {"RecordId": 12, "Correlation": "session-2", "Channel": "AUDIO_INPUT_DVC", "State": "Connected"},
    ]).replace("'", "''")
    command = (
        f"Import-Module '{MODULE}' -Force; $events=ConvertFrom-Json '{events}'; "
        "$playback=Get-RdpMicEventVerdict -Events @($events) -AfterRecordId 10 -TargetCorrelation 'session-2'; "
        "$input=Get-RdpMicEventVerdict -Events @($events) -AfterRecordId 10 -TargetCorrelation 'session-2' -EmpiricalInputChannels @('AUDIO_INPUT_DVC'); "
        "[pscustomobject]@{Playback=$playback.Verdict;Input=$input.Verdict} | ConvertTo-Json -Compress"
    )
    result = _run(command)
    assert result.returncode == 0, result.stderr
    verdicts = json.loads(result.stdout)
    assert verdicts == {
        "Playback": "playback-only",
        "Input": "input-present-supporting-evidence",
    }


def test_empirical_playback_xml_parser_distinguishes_connect_and_close():
    connected = EVENT_FIXTURES / "playback-connected.xml"
    closed = EVENT_FIXTURES / "playback-closed.xml"
    command = (
        f"Import-Module '{MODULE}' -Force; "
        f"$a=ConvertFrom-RdpMicEventXml -Xml (Get-Content '{connected}' -Raw); "
        f"$b=ConvertFrom-RdpMicEventXml -Xml (Get-Content '{closed}' -Raw); "
        "[pscustomobject]@{A=$a;B=$b} | ConvertTo-Json -Compress -Depth 5"
    )
    result = _run(command)
    assert result.returncode == 0, result.stderr
    parsed = json.loads(result.stdout)
    assert parsed["A"]["State"] == "Connected"
    assert parsed["A"]["Channel"] == "AUDIO_PLAYBACK_DVC"
    assert parsed["B"]["State"] == "Closed"


def test_server_endpoint_verdict_rejects_unrelated_active_capture():
    command = (
        f"Import-Module '{MODULE}' -Force; "
        "$ordinary=[pscustomobject]@{Name='USB Microphone';Active=$true;IsRedirected=$false}; "
        "$remote=[pscustomobject]@{Name='Remote Audio';Active=$true;IsRedirected=$true}; "
        "$bad=Get-RdpMicEndpointVerdict -Role Server -Endpoints @($ordinary); "
        "$good=Get-RdpMicEndpointVerdict -Role Server -Endpoints @($ordinary,$remote); "
        "[pscustomobject]@{Bad=$bad.Passed;Good=$good.Passed} | ConvertTo-Json -Compress"
    )
    result = _run(command)
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout) == {"Bad": False, "Good": True}


def test_consent_reset_restore_round_trip_and_conflict_refusal(tmp_path: Path):
    target = "CODEX-RDP-MIC-" + os.urandom(6).hex()
    state = tmp_path / "state"
    command = (
        f"Import-Module '{MODULE}' -Force; $path='HKCU:\\Software\\Microsoft\\Terminal Server Client\\LocalDevices'; "
        "if(-not(Test-Path $path)){New-Item -Path $path -Force|Out-Null}; "
        f"$name='{target}'; New-ItemProperty -LiteralPath $path -Name $name -Value 204 -PropertyType DWord -Force|Out-Null; "
        f"try{{$reset=Reset-RdpMicTargetConsent -TargetHost $name -StateDirectory '{state}' -Confirm:$false; "
        "$missing=$null -eq (Get-Item $path).GetValue($name,$null); $absoluteRestore=$reset.RestoreCommand.StartsWith('powershell.exe -NoProfile -ExecutionPolicy Bypass -File \"') -and $reset.RestoreCommand.Contains(':\\'); "
        "$restore=Restore-RdpMicConsentSnapshot -SnapshotPath $reset.SnapshotPath -Confirm:$false; "
        "$roundtrip=(Get-Item $path).GetValue($name,$null) -eq 204; Remove-ItemProperty -LiteralPath $path -Name $name; "
        "$reset2=$null; New-ItemProperty -LiteralPath $path -Name $name -Value 204 -PropertyType DWord|Out-Null; "
        f"$reset2=Reset-RdpMicTargetConsent -TargetHost $name -StateDirectory '{state}' -Confirm:$false; "
        "$originalSnapshot=[IO.File]::ReadAllText($reset2.SnapshotPath); $bad=$originalSnapshot|ConvertFrom-Json; $bad.SHA256='0'*64; "
        "[IO.File]::WriteAllText($reset2.SnapshotPath,($bad|ConvertTo-Json -Depth 6)); $tamper=$false; "
        "try{Restore-RdpMicConsentSnapshot -SnapshotPath $reset2.SnapshotPath -Confirm:$false|Out-Null}catch{$tamper=$true}; "
        "$stillMissing=$null -eq (Get-Item $path).GetValue($name,$null); [IO.File]::WriteAllText($reset2.SnapshotPath,$originalSnapshot); "
        "New-ItemProperty -LiteralPath $path -Name $name -Value 999 -PropertyType DWord|Out-Null; $conflict=$false; "
        "try{Restore-RdpMicConsentSnapshot -SnapshotPath $reset2.SnapshotPath -Confirm:$false|Out-Null}catch{$conflict=$true}; "
        "$preserved=(Get-Item $path).GetValue($name,$null) -eq 999; "
        "[pscustomobject]@{Missing=$missing;AbsoluteRestore=$absoluteRestore;RoundTrip=$roundtrip;Tamper=$tamper;StillMissing=$stillMissing;Conflict=$conflict;Preserved=$preserved}|ConvertTo-Json -Compress} "
        "finally{Remove-ItemProperty -LiteralPath $path -Name $name -ErrorAction SilentlyContinue}"
    )
    result = _run(command)
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout) == {
        "Missing": True,
        "AbsoluteRestore": True,
        "RoundTrip": True,
        "Tamper": True,
        "StillMissing": True,
        "Conflict": True,
        "Preserved": True,
    }


def test_consent_reset_verification_and_race_fail_without_deletion(tmp_path: Path):
    target = "CODEX-RDP-MIC-" + os.urandom(6).hex()
    neighbor = target + "-NEIGHBOR"
    state = tmp_path / "state"
    command = (
        f"Import-Module '{MODULE}' -Force; $path='HKCU:\\Software\\Microsoft\\Terminal Server Client\\LocalDevices'; "
        "if(-not(Test-Path $path)){New-Item -Path $path -Force|Out-Null}; "
        f"$name='{target}';$neighbor='{neighbor}'; "
        "New-ItemProperty -LiteralPath $path -Name $name -Value 204 -PropertyType DWord -Force|Out-Null; "
        "New-ItemProperty -LiteralPath $path -Name $neighbor -Value 77 -PropertyType DWord -Force|Out-Null; "
        f"try{{$badSnapshot=$false;try{{Reset-RdpMicTargetConsent -TargetHost $name -StateDirectory '{state}' -Confirm:$false "
        "-BeforeRemoveValidation {param($snapshot,$key,$target)[IO.File]::AppendAllText($snapshot,'corrupt')}|Out-Null}catch{$badSnapshot=$true}; "
        "$originalPreserved=(Get-Item $path).GetValue($name,$null) -eq 204; "
        "$race=$false;try{Reset-RdpMicTargetConsent -TargetHost $name -StateDirectory '" + str(state) + "' -Confirm:$false "
        "-BeforeRemoveValidation {param($snapshot,$key,$target)Set-ItemProperty -LiteralPath $key -Name $target -Value 205}|Out-Null}catch{$race=$true}; "
        "$newerPreserved=(Get-Item $path).GetValue($name,$null) -eq 205; $neighborPreserved=(Get-Item $path).GetValue($neighbor,$null) -eq 77; "
        "[pscustomobject]@{BadSnapshot=$badSnapshot;OriginalPreserved=$originalPreserved;Race=$race;NewerPreserved=$newerPreserved;NeighborPreserved=$neighborPreserved}|ConvertTo-Json -Compress} "
        "finally{Remove-ItemProperty -LiteralPath $path -Name $name -ErrorAction SilentlyContinue;Remove-ItemProperty -LiteralPath $path -Name $neighbor -ErrorAction SilentlyContinue}"
    )
    result = _run(command)
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout) == {
        "BadSnapshot": True,
        "OriginalPreserved": True,
        "Race": True,
        "NewerPreserved": True,
        "NeighborPreserved": True,
    }
