# Plan for #3524: Restore RDP Microphone Redirection from WS014 to RDS02

> **Status:** plan-approved
> **Complexity:** T2
> **Date:** 2026-07-14
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/3524
> **Client:** N/A
> **Project:** N/A
> **Lane:** lane:codex
> **Execution mode:** parallel-readonly for resource intelligence/review; single-lane for implementation and live two-machine remediation; approved by the user on 2026-07-14
> **Review artifacts (r1, blocking):** `scripts/review/results/2026-07-14-plan-3524-claude-r1.md` | `scripts/review/results/2026-07-14-plan-3524-codex-r1.md` | `scripts/review/results/2026-07-14-plan-3524-disagreement-r1.md`
> **Review artifacts (r2):** `scripts/review/results/2026-07-14-plan-3524-claude-r2.md` | `scripts/review/results/2026-07-14-plan-3524-codex-r2.md` | `scripts/review/results/2026-07-14-plan-3524-disagreement-r2.md`
> **Review artifact (r3, blocking):** `scripts/review/results/2026-07-14-plan-3524-codex-r3.md`
> **Review artifact (r4, final):** `scripts/review/results/2026-07-14-plan-3524-codex-r4.md`

---

## Resource Intelligence Summary

### Existing repo code

- Found: `docs/session-handoffs/2026-07-14-rdp-microphone-ws014-rds02-exit.md`
  records the current two-machine evidence, local artifact hashes, rollback boundary,
  and the exact next client-side checkpoint.
- Found: `scripts/windows/README.md` contains the repository's existing Windows-native
  PowerShell launchers and documents read-only command patterns. This is precedent for,
  not a formal mandate of, the proposed placement.
- Found: `tests/readiness/test_collect_equality_ps1_schema.py` demonstrates the
  accepted cross-platform test contract for PowerShell: Linux CI pins static/fixture
  behavior while owner-machine verification exercises native CIM and Windows APIs.
- Found: `tests/readiness/test_windows_scheduler_single_source.py` demonstrates a
  Windows-only execution test guarded by a platform/PowerShell availability check.
- Found locally on RDS02 but not tracked: `D:\ws\Repair-RdpMicrophone.ps1`, SHA-256
  `D48F23EBD968F68331F75CD2603C36794CE2C3A5310BE84212C5EC34EA5CE561`.
  It provides guarded Client and Server audits, optional repair, RDP-file backup,
  consent reset, JSON output, and event-channel classification. Its parser validation,
  Server audit, and `-Repair -WhatIf` execution have passed.
- Gap: no repo-owned RDP microphone diagnostic, test fixture, or Windows RDP audio
  runbook exists under `scripts/windows/`, `tests/readiness/`, or `docs/runbooks/`.
- Governance gap: `AGENTS.md` references `scripts/coordination/claim.py`, but that path
  is absent at `origin/main` as verified below. The documented shared claim could not
  be created; planning is isolated in branch `codex/3524-rdp-mic-plan`.

### Standards

| Standard | Status | Source |
|---|---|---|
| Issue planning and TDD | applicable | `.claude/skills/coordination/issue-planning-mode/SKILL.md` requires resource intelligence, reproduction, adversarial review, user approval, then tests first. |
| Parallel-first execution | applicable | `docs/standards/PARALLEL_FIRST_EXECUTION.md` classifies planning/review as `parallel-readonly`; live remediation is serialized because both ends of one RDP negotiation are tightly coupled. |
| Control-plane discoverability | applicable | `docs/standards/CONTROL_PLANE_CONTRACT.md` requires repo context to be discoverable from tracked entry points; `scripts/windows/README.md` is the existing index for Windows-native operational launchers. Neither source mandates the chosen path, which is a plan design decision. |
| Microsoft RDP capture property | applicable | Microsoft documents `audiocapturemode:i:1` as enabling local-device audio capture in the remote session: https://learn.microsoft.com/en-us/azure/virtual-desktop/rdp-properties |
| Microsoft Windows App redirection | applicable | Microsoft documents client/platform-specific redirection behavior, including that Windows App on Windows does not expose the same user-configurable redirection surface: https://learn.microsoft.com/en-us/windows-app/device-audio-folder-redirection-teams |
| Engineering standards | not applicable | This is Windows/RDP operational tooling, not an engineering calculation. |

### LLM Wiki pages consulted

- No relevant wiki pages. This issue is workstation/RDP operations owned by
  `workspace-hub`; it does not add domain knowledge or client content.

### Documents consulted

- GitHub issue #3524 — authoritative scope and acceptance criteria; live state is
  OPEN with `status:needs-plan`, `machine:multi`, and exactly one lane label,
  `lane:codex`.
- `docs/session-handoffs/2026-07-14-rdp-microphone-ws014-rds02-exit.md` — proves
  RDS02 services/policy/privacy are healthy while the active session has playback
  channels only and no capture endpoint.
- GitHub issue #3403 and
  `docs/plans/2026-07-09-issue-3403-voice-dictation-vnc-contract.md` — establish
  that dictation is downstream of a usable microphone endpoint and that live
  hardware validation must be distinct from fixture/contract tests. #3403 is a
  Linux-local dictation issue and does not solve Windows RDP audio transport.
- GitHub issue #2998 — documents the Windows/no-SSH operational constraint; live
  WS014 work must use an operator/local PowerShell path rather than assuming remote
  automation from RDS02.
- GitHub issue #2816 and `tests/readiness/test_collect_equality_ps1_schema.py` —
  establish the existing owner-machine-verification pattern for PowerShell/CIM code.
- `scripts/windows/README.md` — identifies the Windows-native script location and
  Windows host gotchas.
- Drive-file index query `RDP microphone audio capture redirection Windows Server
  voice typing` at 2026-07-14T10:37:49Z returned no results. Coverage gaps were
  reported as `unreachable` for `ace_knowledge`, `dde_knowledge`,
  `og_standards_inventory`, `cad_readability`, and `master_document_index`;
  `og_standards_inventory`, `cad_readability`, and `master_document_index` also
  reported stale status. No drive document is relied upon by this plan.

### Gaps identified

- The exact client executable is not yet proven (`mstsc.exe`, `msrdc.exe`, or
  Windows App), so the correct per-application privacy and configuration surface
  is still unknown.
- For classic `mstsc.exe`, the exact effective `.rdp` profile/command line used for
  the failing connection has not been captured on WS014. A correct unused profile is
  not sufficient proof. MSRDC/Windows App must follow a separate configuration branch
  and must not be forced to supply an unrelated `.rdp` file.
- Client-side TerminalServices-RDPClient events have not been captured during a
  clean reproduction.
- The current local script does not yet have fixture-based tests for duplicate RDP
  property detection/canonicalization, encoding preservation, connection-scoped event
  classification, exact-scope consent backup/delete/restore, or truthful report behavior.
- The current local script writes an RDP profile with a fixed encoding during repair;
  implementation must preserve supported BOM/encoding and newline form, or reject
  an unsupported file without modifying it.
- The current script writes audit JSON into the current working directory by default;
  a review reproduction created unignored worktree residue. The repo-owned tool must
  use stdout-only output by default and write a file only when `-ReportPath` is explicit.
- Hardware success still requires an operator-controlled sign-out/reconnect and a
  real recording test. CI cannot negotiate a physical WS014 microphone into RDS02.

### Evidence (embedded verification)

**Issue statuses** (verified 2026-07-14T10:40:00Z via `gh issue view`):

```text
3524 OPEN [WRK] bug(workstations): RDP microphone input not negotiated from ace-win-2 to ace-win-1
     labels: bug, priority:medium, cat:operations, domain:workstations, machine:multi, status:needs-plan, lane:codex
3403 OPEN Repair Linux voice dictation rollout and VNC consistency contract
     labels include: status:plan-approved, lane:codex
2998 OPEN epic(workstations): extend consistent-experience backbone to Windows / no-SSH ecosystem
     labels include: status:needs-plan, machine:multi, lane:claude
2816 OPEN feat(workstations): collect-equality.ps1 — accurate Windows compute + restore RAM floor
     labels include both status:plan-review and status:plan-approved (pre-existing status drift)
```

**File existence** (verified 2026-07-14T10:40:00Z):

```text
EXISTS  docs/session-handoffs/2026-07-14-rdp-microphone-ws014-rds02-exit.md
EXISTS  scripts/windows/README.md
EXISTS  tests/readiness/test_collect_equality_ps1_schema.py
EXISTS  tests/readiness/test_windows_scheduler_single_source.py
MISSING scripts/windows/rdp-microphone.ps1
MISSING scripts/windows/lib/RdpMicrophone.psm1
MISSING tests/readiness/test_rdp_microphone_ps1_contract.py
MISSING tests/readiness/test_rdp_microphone_ps1_native.py
MISSING docs/runbooks/windows-rdp-microphone.md
MISSING scripts/coordination/claim.py
```

**Line excerpts** (`rg -n`, verified 2026-07-14T10:40:00Z):

```text
tests/readiness/test_collect_equality_ps1_schema.py:3:
  PowerShell cannot run on Linux CI, so these tests pin the contract the .ps1 must satisfy
tests/readiness/test_collect_equality_ps1_schema.py:16:
  The .ps1's own PowerShell logic ... is owner-machine-verified per the plan's owner runbook
tests/readiness/test_windows_scheduler_single_source.py:56:
  pytest.skip("PowerShell is required to execute the Windows renderer")
docs/session-handoffs/2026-07-14-rdp-microphone-ws014-rds02-exit.md:12-13:
  WS014 negotiates playback channels only. No remote capture endpoint or audio-input virtual channel exists
```

**Reproduction proof** (refreshed inside the active RDS session):

The wrapper changed to `%TEMP%`, captured the UTC timestamp and exit code, ran the
script unchanged, and removed only the newly created temp JSON afterward. The fence
below is the complete, unedited wrapper output.

```text
WRAPPER_REPRODUCED_AT_UTC=2026-07-14T10:59:52.5984437Z
RDP Microphone Redirection Audit and Repair
Mode: AUDIT (read-only) | Role: Server

=== SERVER: ace-win-1 ===
[INFO   ] Session: ace-win-1; client ace-win-2; session RDP-Tcp#0.
[PASS   ] RDP user session: RDP-Tcp#0 from ace-win-2.
[PASS   ] AudioEndpointBuilder: Running; startup type Automatic.
[PASS   ] Audiosrv: Running; startup type Automatic.
[PASS   ] User microphone access: Value is 'Allow'; not denied.
[PASS   ] Desktop-app access: Value is 'Allow'; not denied.
[PASS   ] RDP application consent: No explicit RDP-client Deny entry found.
[INFO   ] LetAppsAccessMicrophone: Not configured.
[INFO   ] LetDesktopAppsAccessMicrophone: Not configured.
[PASS   ] TermService: Running.
[PASS   ] UmRdpService: Running.
[PASS   ] SessionEnv: Running.
[PASS   ] Audio capture: fDisableAudioCapture='0'.
[PASS   ] Audio playback: fDisableAudioRedirection=''.
[INFO   ] RDP-Tcp audio: AudioCaptureRedir=0; AudioMapping=0.
[FAIL   ] Remote capture endpoint: No capture endpoint exists in this session.
[FAIL   ] RDP audio-input channel: Recent events show playback channels only.
[PASS   ] Online speech: Accepted.

VERDICT: Microphone redirection is absent; the client did not negotiate audio input.
Run Client repair on WS014, sign out of RDS02, reconnect, and rerun Server audit.

Report: C:\Users\vamseea\AppData\Local\Temp\2\RdpMicAudit-Server-ace-win-1-20260714-055953.json
WRAPPER_SCRIPT_EXIT_CODE=2
```

- Reproduced at: 2026-07-14T10:59:52Z
- Failure mode observed matches issue claim: **YES** — policy and services pass,
  but the session has neither a capture endpoint nor an input virtual channel.
- A read-only remote-management probe from RDS02 to the active client address timed
  out, consistent with #2998's no-SSH/no-remote-management constraint. Client evidence
  must be gathered locally on WS014.
- Distinct source count: 10 (issue #3524, handoff, local script/audit, Microsoft RDP
  docs, Windows README, two PowerShell test patterns, issues #3403/#2998/#2816, and
  the drive-index query).

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-07-14-issue-3524-rdp-microphone-redirection.md` |
| Plan index | `docs/plans/README.md` |
| Windows entry point | `scripts/windows/rdp-microphone.ps1` |
| Pure/testable PowerShell helpers | `scripts/windows/lib/RdpMicrophone.psm1` |
| Cross-platform contract tests | `tests/readiness/test_rdp_microphone_ps1_contract.py` |
| Native Windows pytest wrapper | `tests/readiness/test_rdp_microphone_ps1_native.py` |
| Test fixtures | `tests/readiness/fixtures/rdp-microphone/` |
| Operator runbook and rollback | `docs/runbooks/windows-rdp-microphone.md` |
| Windows script index | `scripts/windows/README.md` |
| Plan review — Claude | `scripts/review/results/2026-07-14-plan-3524-claude-r1.md` |
| Plan review — Codex | `scripts/review/results/2026-07-14-plan-3524-codex-r1.md` |
| Plan review — disagreement r1 | `scripts/review/results/2026-07-14-plan-3524-disagreement-r1.md` |
| Plan review — Claude r2 | `scripts/review/results/2026-07-14-plan-3524-claude-r2.md` |
| Plan review — Codex r2 | `scripts/review/results/2026-07-14-plan-3524-codex-r2.md` |
| Plan review — disagreement r2 | `scripts/review/results/2026-07-14-plan-3524-disagreement-r2.md` |
| Plan review — Codex r3 | `scripts/review/results/2026-07-14-plan-3524-codex-r3.md` |
| Plan review — Codex r4 (final) | `scripts/review/results/2026-07-14-plan-3524-codex-r4.md` |

Live audit JSON remains host-local and is not committed because it may contain
machine/user identifiers and volatile event data.

---

## Deliverable

A repo-owned, tested Windows RDP microphone diagnostic/remediation tool and runbook
that identify the exact client-side layer suppressing audio input, apply only an
explicitly selected reversible profile/consent repair, and prove success through an
actual WS014 to RDS02 capture endpoint, recording smoke test, and remote voice-typing
check. Privacy and machine-policy changes remain audit-and-guidance only.

---

## Pseudocode

```text
function invoke_rdp_microphone(role, mode=Audit, target, rdp_file, report_path,
                               state_directory, reset_consent, restore_snapshot):
    collect identity, process, policy, service, privacy, endpoint, and event evidence
    default output_format to Json and emit exactly one JSON document on the success stream
    never emit Information/Verbose/human text in default Json mode
    support an explicit, mutually exclusive Human output format for interactive summaries
    never write a report file unless report_path is explicit
    never mutate machine/profile/registry state when mode is Audit or WhatIf
    in WhatIf, do not claim that a report or backup was written
    if role == Client:
        identify running RDP client executable, version, and command line
        classify client_type as mstsc, msrdc, windows_app, or unknown
        if client_type == mstsc:
            record the profile named by the command line, if any
            if no profile is named, record that mstsc default/settings state is in use
            require an explicit rdp_file only for profile repair; never guess among candidates
            parse all profile properties; mark a duplicated managed key ambiguous
        else if client_type in {msrdc, windows_app}:
            record package/client version and applicable admin-managed configuration surface
            do not require or repair an .rdp file unless the command line proves one is consumed
            if the effective redirection source cannot be read, stop repair as admin-managed/unresolved
        else:
            stop repair as unsupported-client until executable identity is resolved
        enumerate active local capture endpoints
        inspect global and executable-specific microphone consent
        inspect client RDP operational events and saved target consent
    if role == Server:
        inspect RDS policy/services/effective listener settings
        enumerate current-user capture endpoints
        accept reconnect_marker containing prior max RecordId and UTC time
        query only events newer than marker and within the target reconnect window
        require a target-session correlation key from LocalSessionManager/current session
        if the provider XML lacks or cannot match that key, classify event evidence inconclusive
        classify successful channel-connect events using schemas grounded in captured,
        sanitized RDS02 event XML; never infer success from EventId or token alone
        treat event evidence as supporting; require current-user endpoint plus recording for final success
    emit either machine JSON or a human summary, never both in the same output mode
    exit 0 only when role-specific health criteria pass; exit 2 for diagnosed failure

function repair_rdp_profile(path, explicitly_selected_properties):
    require explicit -Repair and an explicit path
    detect supported encoding/BOM and newline form
    parse full file; flag duplicates as ambiguous rather than assuming resolution order
    modify only explicitly selected keys; capture repair changes only audiocapturemode
    collapse every selected key to one canonical value without touching unselected keys
    write candidate to a sibling temporary file
    parse candidate and verify exactly the selected key/value set
    copy original to timestamped backup without overwriting an existing backup
    atomically replace original; on verification/replacement failure attempt restoration
    verify and report the actual result; if ambiguous or restoration fails, stop without
    claiming success and provide the byte-equal backup path plus manual recovery command

function reset_target_consent(target):
    require -Repair -ResetConsent and exact target spelling
    require a writable state_directory outside the repository
    persist target, registry path, value name, value type, prior value, timestamp, and checksum
    verify snapshot is readable before deletion
    remove only the named value; never delete the LocalDevices key or other hosts
    print exact restore command referencing the snapshot

function restore_registry_snapshot(snapshot):
    require -Repair -RestoreSnapshot and validate snapshot schema/checksum
    restore the exact path/name/type/value captured by this tool
    refuse snapshots for paths outside the allowlisted RDP LocalDevices value

function audit_privacy_and_policy():
    report global/per-app privacy, elevation state, and RDP capture policy
    never write privacy or machine-policy registry values
    print client-type-specific Settings/admin guidance when a deny is found

function classify_audio_events(events, reconnect_marker):
    discard events at/before marker or outside reconnect window
    require each positive event to match the target session/activity correlation key
    if the key is absent, unusable, or unmatched: return inconclusive
    discard events that do not match a captured provider/schema and explicit connected state
    successful = parsed state is connected and severity/outcome is not close/warning/error
    failed_or_closed = parsed state/severity from captured close/failure XML fixtures
    input_connected = successful event whose exact parsed channel is an approved input channel
    playback_connected = successful event whose exact parsed channel is rdpsnd/AUDIO_PLAYBACK
    if input_connected and its provider/schema has an empirical successful-input fixture:
        return input-present-supporting-evidence
    if input_connected without that empirical fixture: return inconclusive
    if playback_connected: return playback-only
    return no-evidence

function live_two_machine_validation():
    run Client audit locally on WS014 against exact launched client/configuration surface
    select repair from evidence; do not apply every possible repair
    record server max event RecordId and UTC reconnect marker before disconnect
    save work and explicitly sign out of RDS02
    close all client instances, reconnect, and accept resource prompt
    run Server audit in the newly created session
    require active Remote Audio capture endpoint plus current-user recording;
    require connection-scoped input-channel evidence when available, never historic token matches
    record 3-5 seconds in a remote application and play back/inspect level
    verify keyboardhook/full-screen routing, then run Win+H in a text field
    if endpoint works but Win+H fails, diagnose speech/keyboard separately
```

---

## Phased Execution

### Phase 0 — reproduce and freeze pre-change evidence (read-only)

Use the already executed Server audit plus native manual WS014 commands to freeze the
pre-change state; do not rely on the untested local script's Client result as authoritative.
Record the executable, command line, local capture endpoint, privacy entries, machine
policy, and client operational events. For mstsc, also record the profile/configuration
source; for MSRDC/Windows App, record that client's package/admin surface. Do not repair.
Also verify the delivery prerequisite on WS014: `git --version`, presence of a
`workspace-hub` clone, and `git ls-remote https://github.com/vamseeachanta/workspace-hub`
or authenticated `gh auth status`. Record a browser-only HTTPS fallback if git/gh is
unavailable. Export the actually available RdpCoreTS playback-connect/close/failure XML
on RDS02, de-identify user/host/activity values, and use those captures as fixture
provenance. Do not require a successful-input fixture before repair: until a real,
correlated successful-input event is captured, positive event classification is
`inconclusive` and the endpoint plus recording remain the decisive proof.

### Plan-review publication gate — before approval or implementation

Force-add the revision-stamped planning review artifacts with explicit paths, commit
the plan/index/reviews, push them to remote `main`, and verify the remote commit and
artifact paths. Only then apply `status:plan-review` and request user approval. This
gate is part of planning and must complete before Phase 1 begins.

### Phase 1 — TDD and repo-owned diagnostic

Write fixture/contract tests first and observe failure. Refactor the host-local script
into a thin entry point plus pure helper module. Preserve audit as the default and keep
all mutations behind `-Repair`; consent reset/restore remain separately gated. Push the
reviewed implementation to a temporary issue branch (permitted because this is a
multi-machine workflow), record its commit SHA, and have the WS014 operator fetch that
exact commit. If git/gh is unavailable but HTTPS browser access works, download the
entry point and module from GitHub's commit-pinned file view and verify published
SHA-256 hashes with `Get-FileHash` before execution. If neither path exists, stop and
record a transfer prerequisite; do not use broken RDP drive redirection or unverified
clipboard content as the transfer path.

### Phase 2 — client evidence gate with the tested tool

Run the exact branch/commit locally on WS014. Emit JSON to stdout or use an explicit
host-local `-ReportPath` outside any repository. Prove client type and the applicable
configuration source. If the client/configuration source remains unresolved, stop with
an admin/operator decision rather than associating an arbitrary `.rdp` file.

### Phase 3 — evidence-selected repair

Apply only the repair supported by Phase 2: profile correction, per-user/per-app
privacy guidance, exact target-consent reset, or administrative escalation. Automated
mutation is limited to explicitly selected RDP profile keys and exact target consent;
privacy and machine policy are not written by the tool. Back up profiles and consent,
verify snapshots, and print tested rollback commands before reconnect.

### Phase 4 — clean-session proof

Fully sign out, reconnect, and require the two decisive current-user proofs: an active
Remote Audio capture endpoint and an actual remote recording. Fresh connection-bounded
input-channel events count as supporting evidence only when both a reliable target-session
correlation key and sanitized empirical successful-input fixture exist; otherwise record
them as inconclusive. If a real correlated success event is produced, preserve its
sanitized XML and add the positive classifier test before claiming event support. Test
`Win+H` only after endpoint and recording pass.

### Phase 5 — documentation and closeout

Document root cause, exact fix, rollback, client-type differences, and the live evidence.
Run focused/full tests, legal/security scan, implementation cross-review, and the issue
completeness gate before closure. Force-add any revision-stamped implementation-review
artifacts with explicit paths, then commit, push, and verify them before closure.

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | `scripts/windows/rdp-microphone.ps1` | Commented Client/Server audit and guarded repair entry point. |
| Create | `scripts/windows/lib/RdpMicrophone.psm1` | Pure profile/event/privacy helpers that can be tested without changing the machine. |
| Create | `tests/readiness/test_rdp_microphone_ps1_contract.py` | Linux-CI-readable static/fixture contract and safety tests. |
| Create | `tests/readiness/test_rdp_microphone_ps1_native.py` | Pytest-discovered Windows-only wrapper that invokes PowerShell helper behavior against temporary fixtures and skips elsewhere. |
| Create | `tests/readiness/fixtures/rdp-microphone/` | Duplicate settings, encoding, event-log, and consent/privacy fixtures. |
| Create | `docs/runbooks/windows-rdp-microphone.md` | Two-machine operator steps, decision tree, success proof, rollback, and privacy boundary. |
| Update | `scripts/windows/README.md` | Add the tool, audit/repair examples, and operator-only reconnect warning. |
| Update | `docs/plans/README.md` | Index this plan and maintain its gate status. |

No production RDP profile, registry hive, service, or live audit JSON is committed.

---

## TDD Test List

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| `test_entrypoint_defaults_to_stdout_audit` | Native invocation is machine-parseable and cannot mutate or create files. | Default invocation captured with stdout/stderr separated. | Entire stdout parses as exactly one JSON document; no human prefix/suffix and no file/registry mutation. |
| `test_human_and_json_output_are_mutually_exclusive` | Interactive text cannot contaminate machine output. | Default Json and explicit Human invocations. | JSON mode has JSON-only stdout; Human mode has no JSON contract and cannot be combined with Json. |
| `test_explicit_report_path_is_required_for_file_output` | Audit residue cannot land in a repo by accident. | No path, explicit temp path, and `-WhatIf`. | No file by default/WhatIf; file only at explicit path. |
| `test_repair_requires_explicit_profile` | Classic-client repair cannot guess a profile. | `-Repair` without `-RdpFile`. | Guidance and no write. |
| `test_duplicate_rdp_key_is_reported_ambiguous` | Audit does not assume undocumented duplicate ordering. | Fixture with two capture values. | Duplicate/ambiguous classification. |
| `test_profile_repair_modifies_only_selected_key` | Mic repair does not alter playback/keyboard choices. | Capture-only selection plus unrelated keys. | One `audiocapturemode:i:1`; unrelated bytes logically unchanged. |
| `test_profile_repair_collapses_selected_duplicates` | Selected ambiguous key is canonicalized safely. | Duplicate capture keys. | Exactly one selected key/value. |
| `test_profile_repair_preserves_supported_encoding_and_newlines` | Supported profile forms round-trip. | ASCII/UTF-8 BOM/UTF-16LE and CRLF fixtures. | Encoding/newline preserved; unsupported input fails closed. |
| `test_profile_backup_and_candidate_rollback` | Original is recoverable across replacement boundaries. | Temporary profile with injected validation failure, replacement failure, ambiguous replacement outcome, and restoration failure. | Unique byte-equal backup; original restored when provable; ambiguous/restore failure stops with backup path and manual recovery command without claiming success. |
| `test_whatif_changes_nothing_and_claims_nothing_written` | `-WhatIf` is truthful. | Repair/report/snapshot flags with WhatIf. | No writes; simulated actions only. |
| `test_reset_consent_requires_verified_snapshot` | Destructive consent reset cannot precede backup proof. | Temporary allowlisted registry subtree. | Verified snapshot before removal. |
| `test_reset_consent_removes_exact_target_only` | Consent reset is narrow. | Target plus other alias/FQDN values. | Only named value removed. |
| `test_restore_consent_snapshot_round_trip` | Consent repair is reversible. | Snapshot created by tool. | Exact type/name/value restored. |
| `test_rejects_snapshot_outside_allowlist_or_bad_checksum` | Restore cannot write arbitrary registry state. | Tampered/path-injected snapshots. | Refusal and no registry change. |
| `test_privacy_and_policy_are_audit_only` | Tool cannot automatically write privacy/policy. | Static source inspection and denied fixtures. | Findings/guidance only; no setter path. |
| `test_client_type_mstsc_profile_branch` | Classic client records command-line configuration source. | mstsc process fixtures with/without profile. | Explicit profile or documented default-state branch. |
| `test_client_type_modern_has_no_forced_rdp_file` | MSRDC/Windows App does not inherit mstsc assumptions. | Modern-client process fixture. | Package/admin surface or unresolved stop; no guessed profile. |
| `test_unknown_client_blocks_repair` | Unsupported client cannot be mutated. | Unknown executable fixture. | Repair-blocked result. |
| `test_playback_connect_is_not_input_success` | Playback-only connect remains failure. | Sanitized, empirically captured playback-connect XML after marker. | `playback-only`. |
| `test_unattested_input_connect_is_inconclusive` | A guessed input schema cannot become success evidence. | Schema-shaped input event without an empirical successful-input fixture. | `inconclusive`. |
| `test_empirical_input_connect_after_marker_is_supporting_evidence` | Post-repair regression/provenance: a real successful input connect can be recognized after live capture; this is not part of the initial RED cycle. | Post-repair sanitized, empirically captured and correlated input-connect XML; conditional test/fixture added only if obtained. | `input-present-supporting-evidence`; otherwise no positive fixture or claim. |
| `test_input_close_failure_or_token_text_is_not_success` | Token-only/close/error messages cannot false-pass. | Sanitized captured close/failure XML plus synthetic token-only text. | No input-success evidence. |
| `test_events_before_marker_or_other_activity_are_excluded` | Old/uncorrelated user events cannot satisfy reconnect proof. | Mixed RecordId/time/ActivityId fixtures. | Only correlated window retained. |
| `test_missing_or_unusable_session_correlation_is_inconclusive` | Shared-host events cannot be attributed by time alone. | Fresh event with absent/unmatched/unparseable target correlation fields. | `inconclusive`; never supporting evidence. |
| `test_missing_capture_registry_is_failure` | Server audit fails without current-user endpoint. | Empty capture fixture. | Exit 2 and actionable verdict. |
| `test_json_allowlist_excludes_secret_values` | Reports cannot serialize arbitrary registry data. | Credential/token sentinel fields. | Sentinels absent. |
| `test_no_service_restart_signout_or_policy_write` | Shared RDS safety boundary is structural. | Source inspection. | No TermService restart, sign-out, or policy setter. |
| `test_native_fixture_smoke` | Pytest wrapper invokes native PowerShell helpers. | Temporary files/test registry subtree on Windows. | Exit 0; skipped on non-Windows. |

Tests are written and observed RED before implementation. Tests that touch temporary
HKCU paths must use a test-specific subtree and clean it in `finally`; they must never
write actual Terminal Server policy or actual RDP consent values.

---

## Acceptance Criteria

- [ ] Phase 0 client evidence records the exact RDP client executable/version/command
  line and its applicable configuration source; an exact `.rdp` profile is required
  only when the identified client/command line actually consumes one.
- [ ] Initial implementation tests (excluding the conditional post-repair empirical
  regression/provenance test) are written first and observed failing:
  `uv run pytest tests/readiness/test_rdp_microphone_ps1_contract.py -v` and
  `uv run pytest tests/readiness/test_rdp_microphone_ps1_native.py -v` on Windows.
- [ ] Focused contract and native Windows tests pass after implementation.
- [ ] Existing Windows readiness tests pass:
  `uv run pytest tests/readiness/test_collect_equality_ps1_schema.py tests/readiness/test_windows_scheduler_single_source.py -v`.
- [ ] PowerShell parser validation passes for the `.ps1` entry point and `.psm1`
  module; pytest collection/execution validates the Python native-test wrapper.
- [ ] Default native invocation emits exactly one parseable JSON document to stdout with
  no Information/human text and creates no report file; Human mode is explicit and
  mutually exclusive; a report file is written only for explicit `-ReportPath`;
  `-WhatIf` creates neither report nor backup.
- [ ] Any repaired `.rdp` profile has a byte-verifiable backup and a documented rollback command.
- [ ] Consent reset, if used, requires a verified snapshot, removes only the explicitly
  named target value, prints a restore command, and passes a restore round trip.
- [ ] Privacy and machine-policy findings remain audit/guidance only; the tool contains
  no automated write path for those values.
- [ ] After a full RDS sign-out and reconnect, fresh connection-bounded RdpCoreTS evidence
  supports a successful audio-input channel only when reliable target-session correlation
  and an empirical success schema are available. Otherwise event evidence is explicitly
  inconclusive; the current-user endpoint plus real recording remain sufficient decisive
  transport proof and no event-success claim is made.
- [ ] `mmsys.cpl -> Recording` shows an active Remote Audio capture endpoint in the
  new RDS02 session.
- [ ] A remote application records 3-5 seconds from the WS014 microphone and the
  recording/level meter proves usable input.
- [ ] With `keyboardhook:i:2` **and** a full-screen classic RDP session (or another
  separately documented client setting that sends Windows combinations remotely),
  `Win+H` reaches a remote text field and transcribes speech. Keyboard routing is an
  explicit user-selected setting and is not changed by capture repair. If microphone recording succeeds but voice typing
  does not, the issue remains open or a separately scoped product limitation is
  documented and linked; transport success must not be conflated with Win+H success.
- [ ] `docs/runbooks/windows-rdp-microphone.md` documents the proven root cause,
  classic/modern client distinction, repair, rollback, privacy implications, and
  operator-controlled sign-out.
- [ ] `scripts/windows/README.md` links the runbook and shows audit-first commands.
- [ ] No live report containing volatile user/machine detail is committed; default
  stdout behavior and explicit host-local `-ReportPath` are covered by tests.
- [ ] Revision-stamped final review artifacts are force-added explicitly, committed,
  pushed, and verified on remote `main` before `status:plan-review` is applied.
- [ ] Legal/security scan passes: `bash scripts/legal/legal-sanity-scan.sh`.
- [ ] Implementation receives non-MAJOR cross-review artifacts before closeout.
- [ ] Completeness score/report and owner-only completeness verification satisfy
  issue #2798 policy before the issue is closed.

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Claude r1 | MINOR | Correct citations; prevent audit JSON worktree residue; make Phase 0 executable; avoid duplicate-key assumptions/fixed three-property repair; use existing pytest discovery. |
| Codex r1 | MAJOR | Resolve audit/report contradiction, branch by client type, correlate events, constrain/test mutations and rollback, correct keyboardhook semantics, reject token-only input evidence. |
| Claude r2 | MINOR | Persist review evidence; reconcile Gemini/map rows; use verbatim reproduction; verify WS014 transfer; fix parser wording; ground event fixtures empirically. |
| Codex r2 | UNAVAILABLE | Windows argument-list limit prevented the repository fan-out wrapper from passing the revised plan. |
| Codex r3 | MAJOR | Separate JSON/human output, remove circular positive fixture, publish reviews before the gate, fail closed without correlation, and strengthen replacement rollback tests. |
| Codex r4 | MINOR | Align restore truthfulness, mark the conditional fixture post-repair, make event support conditional, and index final review artifacts. No blockers. |

**Overall result:** READY FOR USER REVIEW — Codex r3 blockers were revised and Codex r4
returned MINOR with no blockers. Implementation remains prohibited until explicit user
approval and the `status:plan-approved` transition.

Revisions made based on review:

- Default audit now writes JSON to stdout only; file output requires explicit `-ReportPath`.
- Client evidence/repair branches now distinguish mstsc, MSRDC, Windows App, and unknown clients.
- Event evidence now requires successful connect events inside a reconnect RecordId/time/activity boundary and remains supporting evidence rather than the sole success proof.
- Automated mutations are narrowed to selected profile keys and exact consent; privacy/policy are audit-only.
- Consent reset now requires a verified, checksummed, allowlisted restoration snapshot and tested round trip.
- Profile repair changes only selected keys; microphone repair no longer changes playback or keyboard routing.
- Duplicate RDP properties are reported ambiguous and canonicalized only when explicitly repaired; no undocumented ordering is assumed.
- Native PowerShell testing now uses a pytest-discovered Windows-only wrapper under `tests/readiness/`.
- `keyboardhook:i:2` is correctly paired with full-screen operation.
- Review artifacts are explicitly force-added/pushed before label transition; nonexistent
  Gemini rows are removed and disagreement artifacts are indexed.
- Reproduction evidence is now complete wrapper output, including the legacy script's
  default report write that motivates stdout-only behavior.
- WS014 delivery now has a tested git/auth prerequisite, commit-pinned HTTPS fallback,
  SHA-256 verification, and a fail-closed prerequisite state.
- PowerShell parser validation and Python pytest validation are separated correctly.
- Event parsing fixtures must originate from sanitized real RDS02 XML; EventId/token
  presence alone cannot define success.
- Default machine output is exactly one JSON document; Human output is explicit and
  mutually exclusive, with native whole-stdout parsing required by tests.
- A successful-input fixture is no longer circularly required before repair. Positive
  event support stays inconclusive until a real correlated success event is captured.
- Planning reviews are force-added, committed, pushed, and remotely verified in a
  pre-approval publication gate rather than implementation closeout.
- Event classification fails closed when the target-session correlation key is absent,
  unusable, or unmatched.
- Replacement rollback tests cover replacement, ambiguous-outcome, and restore failures.

---

## Risks and Open Questions

- **Risk — client identity:** `.rdp` settings are irrelevant if the user actually
  launches a client that consumes a different configuration surface. Phase 0 identifies
  the executable manually; the tested tool later branches by client type and blocks
  repair when the modern-client/admin surface cannot be read.
- **Risk — shared RDS host:** service or TermService restarts could disrupt other users.
  The tool forbids them; any later administrator restart is a separately approved,
  scheduled operator action.
- **Risk — user data:** signing out closes the user's remote applications. The tool
  prints the requirement but never performs sign-out.
- **Risk — privacy/security:** microphone redirection grants the remote session access
  to local audio. Consent reset and privacy repair must be explicit and narrowly scoped.
- **Risk — RDP product defect:** if a fresh minimal classic-mstsc connection with an
  active local endpoint still never offers input, resolution may require Microsoft/client
  servicing outside this repository. Preserve client and server event evidence and keep
  #3524 open with a linked external blocker rather than claiming success.
- **Risk — test boundary:** Linux CI cannot exercise Windows Core Audio or RDP virtual
  channels. Contract tests plus native owner-machine tests and a live recording smoke are
  all required; none substitutes for the others.
- **Open question:** which RDP client executable and profile are actually used on WS014?
  Phase 0 resolves this without a mutation.
- **Risk — event correlation:** RdpCoreTS is shared on a multi-user host. RecordId/time/
  ActivityId filtering reduces false attribution, but current-user endpoint plus a real
  recording remain the decisive success proof.
- **Open question:** does the expanded security prompt persist microphone permission for
  the exact target alias, FQDN, or address being launched? Phase 0 records all aliases but
  repair may touch only the explicitly selected value.
- **Governance:** issue #2816 has pre-existing simultaneous plan-review/plan-approved
  labels; this unrelated drift is recorded but not changed by #3524.

---

## Complexity: T2

**T2** — one Windows entry point plus a helper module, fixture/native tests, a runbook,
and operator-gated validation across two machines. The work is bounded but not trivial
because the client configuration surface is not yet identified and hardware negotiation
cannot be fully simulated in CI.
