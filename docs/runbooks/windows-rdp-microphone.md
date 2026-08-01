# RDP microphone redirection: WS014 to RDS02

Use this runbook when playback works in an RDP session but `Remote Audio` is absent
under **Sound > Recording**, applications cannot record, or `Win+H` does nothing.
The repository tool is audit-first and commented. It does not restart Remote Desktop
Services, sign out users, or write microphone privacy and machine policy.

## 1. Audit both ends

On WS014, in a normal PowerShell window owned by the connecting user:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\windows\rdp-microphone.ps1 -Role Client -TargetHost ace-win-1 -OutputFormat Human
```

If classic `mstsc.exe` is launched with a specific profile, audit that exact file:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\windows\rdp-microphone.ps1 -Role Client -TargetHost ace-win-1 -RdpFile "$env:USERPROFILE\Desktop\RDS02.rdp"
```

Inside the current RDS02 session:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\windows\rdp-microphone.ps1 -Role Server -OutputFormat Human
```

Default output is one JSON document on stdout. Nothing is written unless an explicit
`-ReportPath` is supplied. Reports may contain workstation/user identifiers; keep them
outside repositories.

## 2. Select only the repair supported by the audit

For classic `mstsc.exe`, repair an explicitly identified `.rdp` file:

```powershell
# Preview first; this creates no candidate, backup, or report.
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\windows\rdp-microphone.ps1 -Role Client -ClientType Mstsc -ConfigurationSource "$env:USERPROFILE\Desktop\RDS02.rdp" -RdpFile "$env:USERPROFILE\Desktop\RDS02.rdp" -Repair -WhatIf -OutputFormat Human

# Apply: only audiocapturemode is canonicalized to audiocapturemode:i:1.
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\windows\rdp-microphone.ps1 -Role Client -ClientType Mstsc -ConfigurationSource "$env:USERPROFILE\Desktop\RDS02.rdp" -RdpFile "$env:USERPROFILE\Desktop\RDS02.rdp" -Repair -OutputFormat Human
```

`-ClientType Mstsc` and `-ConfigurationSource` are an explicit operator assertion that
the selected profile controls this target connection; this avoids guessing from an
unrelated or already-closed process. The original file is retained beside it as
`.backup-<timestamp>`. Human output includes `BackupPath`. Rollback:

```powershell
Copy-Item -LiteralPath '<BackupPath printed by the tool>' -Destination '<original .rdp path>' -Force
```

For MSRDC or Windows App, do not assume that an arbitrary `.rdp` file controls the
connection. Use its administrator-managed redirection settings. The tool reports the
client type and refuses to guess.

If the saved resource prompt decision is suspected, reset only the exact target value.
This requires a checksummed snapshot and prints the rollback command:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\windows\rdp-microphone.ps1 -Role Client -TargetHost ace-win-1 -Repair -ResetConsent -StateDirectory "$env:LOCALAPPDATA\RdpMicState" -OutputFormat Human
```

Consent rollback:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\windows\rdp-microphone.ps1 -Role Client -Repair -RestoreSnapshot '<SnapshotPath>' -OutputFormat Human
```

Privacy or policy denials are guidance-only. Correct user privacy in **Settings >
Privacy & security > Microphone**, or ask the administrator to correct effective RDP
and AppPrivacy policy. The tool deliberately does not write those values.

## 3. Reconnect and prove transport

1. Save work and fully **sign out** of RDS02; disconnecting alone is insufficient.
2. Close every RDP client instance on WS014.
3. Reopen the exact audited connection. For classic Remote Desktop Connection, expand
   **Show Options > Local Resources > More** and select **Microphones and other audio
   recording devices**. Accept the resource-security prompt for the exact target.
4. In the new RDS02 session, run `mmsys.cpl`. Under **Recording**, require an active
   `Remote Audio` or `Remote Audio Microphone` endpoint.
5. In Sound Recorder, Teams, or the intended browser/application, select that input and
   record 3-5 seconds. Play it back. This recording is the decisive end-to-end proof.
6. Only after recording succeeds, use the RDP session full-screen and press `Win+H`.
   `keyboardhook:i:2` routes Windows combinations remotely only in full-screen mode.

RdpCoreTS events are supporting evidence only. On a shared host, an event without a
reliable target-session correlation is `inconclusive`; playback tokens or historic
events must never be treated as microphone success.

## Exit codes

- `0`: the role-specific audit found no decisive failure.
- `2`: a failure, unsafe/ambiguous request, or missing endpoint was diagnosed.
