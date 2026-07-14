# Session handoff — RDP microphone WS014 to RDS02 (2026-07-14)

**Issue:** [workspace-hub#3524](https://github.com/vamseeachanta/workspace-hub/issues/3524)

**State at exit:** open, `status:needs-plan`, `lane:codex`

**Scope:** ACMA-WS014 microphone redirection into ACMA-HOU-RDS02

## Outcome

The fault is isolated to RDP client negotiation: RDS02 permits audio capture and
its required services are healthy, but WS014 negotiates playback channels only.
No remote capture endpoint or audio-input virtual channel exists in the active
RDS session.

The issue contains the evidence, reproduction, acceptance criteria, and proposed
next investigation. No repository implementation was started because the issue
has not passed the required plan, adversarial-review, and user-approval gates.

## Durable state

- GitHub issue: `workspace-hub#3524`
- Repository: `vamseeachanta/workspace-hub`
- Issue labels at exit:
  - `bug`
  - `priority:medium`
  - `cat:operations`
  - `domain:workstations`
  - `machine:multi`
  - `status:needs-plan`
  - `lane:codex`
- Microsoft reference:
  <https://learn.microsoft.com/en-us/azure/virtual-desktop/rdp-properties>

## Verified RDS02 evidence

Environment:

- Host: `ACMA-HOU-RDS02`
- OS: Windows Server 2025 Standard, build 26100
- Client reported by the active session: `ACMA-WS014`
- Session: `RDP-Tcp#0`, session ID 2

Passing checks:

- `AudioEndpointBuilder` and `Audiosrv` are running and Automatic.
- `TermService`, `UmRdpService`, and `SessionEnv` are running.
- `fDisableAudioCapture=0`.
- Current-user microphone and desktop-application privacy values are `Allow`.
- Terminal Services WMI reports `AudioCaptureRedir=0` and `AudioMapping=0`.
- Online speech privacy is accepted.
- The `en-US` speech capability is installed.

Failing, decisive checks:

- `HKCU\Software\Microsoft\Windows\CurrentVersion\MMDevices\Audio\Capture`
  is absent in the RDS user session.
- `Get-PnpDevice -Class AudioEndpoint -PresentOnly` reports no audio endpoint.
- RdpCoreTS Operational events contain `rdpsnd`, `AUDIO_PLAYBACK_DVC`, and
  `AUDIO_PLAYBACK_LOSSY_DVC` connections.
- No `AUDIN`, `AUDIO_INPUT`, or `AUDIO_CAPTURE` event is present.
- `Remote Audio` is therefore absent from `mmsys.cpl -> Recording`.
- Redirected client drives are also absent, supporting the conclusion that the
  effective client resource set is more restrictive than the server policy.

## Local diagnostic artifacts

These files are intentionally outside the dirty `workspace-hub` checkout and
were not promoted into the repository before issue plan approval:

| Artifact | SHA-256 |
|---|---|
| `D:\ws\Repair-RdpMicrophone.ps1` | `D48F23EBD968F68331F75CD2603C36794CE2C3A5310BE84212C5EC34EA5CE561` |
| `D:\ws\RdpMicAudit-Server-ACMA-HOU-RDS02-20260714-050409.json` | `383C54951B0C3F66C31EAC45986533CC37DD1A8446E563263D037B33E38B7A08` |

`Repair-RdpMicrophone.ps1` is a commented two-ended tool. Audit mode is
read-only. Repair requires `-Repair`; consent reset additionally requires
`-ResetConsent`. It backs up an RDP profile before editing and never restarts
Remote Desktop Services or signs out users. Its PowerShell parser check passed,
its Server audit reproduced the failure, and its `-Repair -WhatIf` path ran
without a runtime error.

## Exact next checkpoint

Start on ACMA-WS014, not RDS02. First read issue #3524 and revalidate live state.
Then run the client audit against the exact RDP profile that the user launches:

```powershell
Set-ExecutionPolicy -Scope Process Bypass
.\Repair-RdpMicrophone.ps1 `
  -Role Client `
  -TargetHost ACMA-HOU-RDS02 `
  -RdpFile "$env:USERPROFILE\Documents\Default.rdp"
```

Replace `Default.rdp` with the actual launched file if different. Record:

1. The RDP process path, version, and command line (`mstsc`, `msrdc`, or Windows
   App).
2. The exact RDP profile content and effective `audiocapturemode` value.
3. The active local capture endpoint.
4. Global and per-application microphone privacy for the actual client process.
5. Client-side TerminalServices-RDPClient Operational events during connection.

Only after inspecting the audit output, use the guarded repair if appropriate:

```powershell
.\Repair-RdpMicrophone.ps1 `
  -Role Client `
  -TargetHost ACMA-HOU-RDS02 `
  -RdpFile "$env:USERPROFILE\Documents\Default.rdp" `
  -Repair `
  -ResetConsent
```

Fully sign out of RDS02, close all RDP client windows, reconnect using the
audited profile, expand **Show Details**, and permit microphones. Then verify
inside RDS02:

```powershell
.\Repair-RdpMicrophone.ps1 -Role Server
```

Success requires both an active capture endpoint and evidence of an input/capture
channel. `Win+H` should be tested only afterward, with `keyboardhook:i:2` or a
full-screen RDP window.

## Governance boundary for the next session

Issue #3524 is intake-only. Before promoting the local script or changing
workspace readiness automation:

1. Perform resource intelligence.
2. Create the canonical issue plan.
3. Run adversarial plan review.
4. Apply `status:plan-review`.
5. Obtain explicit user approval and `status:plan-approved`.
6. Implement with tests, cross-review, and verification artifacts.

## Dirty-worktree preservation

At handoff creation, `workspace-hub` was already dirty with unrelated machine
equality, curation, and state artifacts. Those changes belong to other work and
must not be reverted, overwritten, or included in an RDP-microphone commit.

Pre-handoff repository identity was:

- branch: `main`
- `HEAD`: `c813b3d3b7a0944f9e05ccf6a3d3a77bd62c3e8e`
- `origin/main`: `c813b3d3b7a0944f9e05ccf6a3d3a77bd62c3e8e`
- ahead/behind: `0/0`

## External actions

- Created GitHub issue #3524 as explicitly requested.
- No email, chat message, machine restart, service restart, sign-out, or other
  external action was performed.
