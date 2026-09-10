# Disagreement report — plan #3524 (2026-07-14)

## Verdicts

| Provider | Verdict |
|---|---|
| claude-r1 | MINOR |
| claude | MINOR |
| codex-r1 | MAJOR |
| codex | UNAVAILABLE (codex CLI failed, rc=126: timeout: failed to run command 'codex': Argument list too long ) |
| disagreement-r1 | | Provider | Verdict | |

## Findings unique to each provider

A finding is 'unique to X' if its text appears in X's artifact but not
verbatim in any other provider's artifact.

### claude-r1

(no findings unique to this provider)

### claude

- **Adversarial-review evidence is host-local only — the gate's audit trail is not durable.** `scripts/review/results/` is gitignored (`.gitignore:577`) and `git ls-files` shows no 3524 artifact tracked, while 136 prior-issue artifacts (including the full 3403 r1–r5 series the plan's naming follows) were force-added and committed. The plan header calls the r1 artifacts "blocking" and the Artifact Map lists six review paths, but as written all of them live only on ace-win-1. Machine loss or cleanup destroys the exact evidence the user-approval gate depends on. The plan must state the durability mechanism (force-add per precedent) or the artifacts are effectively uncited.
- **Artifact Map / Review Summary / header disagree about Gemini and disagreement-r1.** Artifact Map line 198 lists `…-plan-3524-gemini-r1.md` — the file does not exist (glob verified), the header's r1 list (line 11) omits Gemini, and the Review Summary (line 467) says "Gemini r1 PENDING — Not yet run." T2 requires 2 providers, so either delete the Gemini rows or mark them expected-UNAVAILABLE per the `scripts/review/results/` convention. The map also omits `disagreement-r1.md`, which the header cites and which exists.
- **The "Reproduction proof" block is presented as verbatim output but is edited.** Template §Reproduction proofs requires a "verbatim tail of output." My independent re-run shows the script emits no `REPRODUCED_AT_UTC=` line (plan line 155 — injected by the runner), and the plan's excerpt elides real output lines including the trailing `Report: C:\...\RdpMicAudit-….json` line — which is precisely the default-report-write residue hazard the plan itself flags at lines 102–104. The failure mode is genuine (I reproduced it), but an edited excerpt labeled as script output is the exact "trick the reviewer" shape the future-tense/verbatim rules exist to prevent. Re-paste unedited output; put the timestamp outside the fence.
- **Phase 1→2 transfer to ace-win-2 rests on an unverified capability.** Phase 1 (lines 325–327) has "the ace-win-2 operator fetch that exact commit," but nothing in the plan's evidence establishes that ace-win-2 has a workspace-hub clone, git, or GitHub credentials — and the plan's own evidence (lines 174–176, #2998) documents that remote access to ace-win-2 is constrained and drive redirection is broken. If ace-win-2 cannot fetch, Phase 2 blocks with no named fallback. Add a Phase 0 check (does ace-win-2 have git+auth?) and a fallback transfer path with hash verification.
- **AC line 424 applies "PowerShell parser validation" to a Python file.** "PowerShell parser validation passes for the entry point, module, and native test" — the native test is `tests/readiness/test_rdp_microphone_ps1_native.py`, a pytest file; PowerShell parser validation is meaningless for it. Scope the criterion to the `.ps1`/`.psm1` and use pytest collection for the `.py`.
- **Event ID 132 semantics are pinned in pseudocode and three TDD rows with no cited source.** `classify_audio_events` (lines 284–292) hardcodes "successful = EventId 132 and message says channel was connected," and tests at lines 398–400 encode it, but neither cited Microsoft URL documents RdpCoreTS event IDs. This is the same defect class Claude r1's finding on last-value-wins semantics identified: a fixture test can encode a guess as a contract. The plan should state that event fixtures are captured from real RdpCoreTS XML on ace-win-1 (empirical grounding) rather than authored from assumed message shapes.

### codex-r1

(no findings unique to this provider)

### codex

- (none)

### disagreement-r1

- A finding is 'unique to X' if its text appears in X's artifact but not
- verbatim in any other provider's artifact.
- ### claude-r1
- ### claude
- **Miscitation** — the Standards table claims `CONTROL_PLANE_CONTRACT.md` "require[s] repo-owned Windows tooling." The contract, read in full, is about AGENTS.md entry points and provider adapters; it says nothing about tooling placement. The conclusion survives via `scripts/windows/README.md`, but this citation is wrong.
- **Observed worktree contamination with no plan mechanism** — my verification re-run wrote `RdpMicAudit-Server-…json` into the repo worktree root (the script reports to CWD), and `git check-ignore` exit 1 proves nothing ignores it. The AC "No live report … is committed" states an outcome with no mechanism: no default report path outside the repo, no `-ReportPath` in the pseudocode, no `.gitignore` entry, no TDD row pinning report location.
- **Phase 0 has no executable path to ace-win-2** — the only diagnostic lives on ace-win-1, the repo tool is built in Phase 1 (*after* Phase 0), drive redirection is broken per the plan's own evidence, and #2998 rules out remote management. No transfer mechanism is named. Compounding it: the script's **Client** audit — the code path Phase 0 and Phase 2 repair selection depend on — is the one path the plan admits is unexercised (only parser, Server audit, and `-Repair -WhatIf` have passed).
- **Unverified behavioral assumption pinned as a test contract** — `test_rdp_last_property_wins` asserts "actual last-value-wins" duplicate-key semantics with no evidence source; the cited Microsoft page doesn't document duplicate resolution, and behavior may differ across mstsc/msrdc/Windows App — the exact client ambiguity Phase 0 exists to resolve.
- **Internal inconsistency** — `repair_rdp_profile` unconditionally enforces `audiomode:i:0` and `keyboardhook:i:2` alongside `audiocapturemode:i:1`, while Phase 2 mandates "apply only the repair supported by Phase 0." Writing keyboard-routing and playback values during a mic repair is the scope creep the plan forbids elsewhere.
- **`tests/windows/` is new and unwired** — the directory doesn't exist, isn't flagged as new, and no harness discovers the native test beyond a manual AC command; live precedent puts platform-guarded Windows tests under `tests/readiness/` where pytest handles them.
- **Cosmetic template drift** — TDD table drops the template's input/output columns; artifact naming `-claude-r1.md` deviates from the template but matches dominant repo convention (not a defect).
- Checks producing no finding: all file-existence and hash claims, all four issue-state claims, all quoted excerpts, the Step 1.5 reproduction (independently re-reproduced), the plan-index README diff (draft-status row, future-tense compliant).
- ### codex
