# RDP microphone ace-win-2 to ace-win-1 — implementation-ready handoff

Issue: https://github.com/vamseeachanta/workspace-hub/issues/3524

Lane: `lane:codex`

State: implementation complete; live two-machine validation remains

## Durable implementation

- Entry point: `scripts/windows/rdp-microphone.ps1`
- Helper module: `scripts/windows/lib/RdpMicrophone.psm1`
- Runbook: `docs/runbooks/windows-rdp-microphone.md`
- Tests: `tests/readiness/test_rdp_microphone_ps1_contract.py` and
  `tests/readiness/test_rdp_microphone_ps1_native.py`
- Review evidence: `scripts/review/results/2026-07-14-impl-3524-codex-r1.md`
  through `-r4.md`; final verdict `APPROVE`
- Implementation tip before this handoff: `c0ae4d7cf`

The tool is audit-first, extensively commented, and emits exactly one JSON document
by default. It never restarts services, signs out users, or writes privacy/machine
policy. Mutations are limited to an explicit classic `.rdp` capture property and an
exact checksummed target-consent reset/restore. Profile and consent rollback paths are
printed in Human mode.

## Verification completed on ace-win-1

- Focused suite: `26 passed`
- Both PowerShell files: Windows PowerShell 5.1 parser pass
- Legal deny-list equivalent scan: 23 patterns, zero violations
- Live Server audit: JSON parsed, exit `2`, no active redirected Remote Audio capture
  endpoint, required services pass, `fDisableAudioCapture=0`, event evidence
  `inconclusive`, and no default report file was created
- Existing readiness bundle: 31 tests passed and 6 unrelated tests could not launch
  `bash` because Git Bash is not installed/available on this host

## Next operator steps on ace-win-2

Run from the same commit on ace-win-2:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\windows\rdp-microphone.ps1 -Role Client -TargetHost ace-win-1 -OutputFormat Human
```

Identify the actual client/configuration source. For an explicitly confirmed classic
profile, preview and apply only if the audit supports it:

```powershell
$rdp = "$env:USERPROFILE\Desktop\ace-win-1.rdp"
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\windows\rdp-microphone.ps1 -Role Client -ClientType Mstsc -ConfigurationSource $rdp -RdpFile $rdp -Repair -WhatIf -OutputFormat Human
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\windows\rdp-microphone.ps1 -Role Client -ClientType Mstsc -ConfigurationSource $rdp -RdpFile $rdp -Repair -OutputFormat Human
```

Do not apply the classic-profile repair to MSRDC or Windows App. If cached resource
consent is the evidence-selected fault, use the runbook's exact target reset with a
state directory outside the repository.

Then save work, fully sign out of ace-win-1, close all client instances, reconnect with
microphone resources enabled, and require:

1. Active `Remote Audio` under `mmsys.cpl -> Recording`.
2. A successful 3-5 second recording and playback in the intended remote application.
3. Full-screen RDP, then `Win+H` voice typing.

Do not close issue #3524 until those three live proofs are recorded. RdpCoreTS events
without reliable target-session correlation remain supporting/inconclusive evidence,
not transport success.
