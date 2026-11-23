# Plan for #2742 (WF4): Windows/macOS Telegram-Hermes dispatch-parity design

> **Status:** adversarial-reviewed
> **Complexity:** T2 (design/doc deliverable — no code)
> **Date:** 2026-06-09
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2742 (WF4, parent epic #2998, ties F4 #2971 + WF3 #3000)
> **Client:** N/A
> **Review artifacts:** independent adversarial sweep folded below (Codex automated review stalls on stdin here).

---

## Context

#2742 is the **cross-platform parity planning** track (item 6 of the control-surface issue-tree:
"Windows/macOS stay status-only until an approved parity plan exists"). It asks HOW the no-SSH hosts
(`ace-win-1/2`, `macbook-portable`, `gali-linux-compute-1`) move from `telegram_mode: desktop-status-only`
to safe dispatch targets. The deliverable is a **design document** (the issue is explicit: "No
implementation occurs before user approval"; acceptance = documented recommendation + service model +
secret posture + readiness format + MVP checklist). No code.

This epic already built the pieces the parity plan must assemble:
- **F4 #2971** — the Telegram-as-venue contract (`docs/ops/telegram-venue-contract.md`, `venue_lease.py`,
  `venue_absence_detector.py`, `venue_audit.py`): single-active venue, ordered delivery, idempotency,
  PII-safe audit, absence detection.
- **WF3 #3000** — `dispatch_pull.py`: no-SSH hosts CLAIM lease-arbitrated work themselves (pull, not push).
- **WF1 #2999** — the reconciler converges Windows hosts (deny-list parity).
- **WF0 #3001** — `ace-win-*` naming + aliases.

**The recommendation falls out of the architecture:** no-SSH hosts cannot run an inbound bot (no inbound
SSH, corporate firewall blocks inbound — only outbound git/HTTPS works). So the parity model is
**coordinator-routed PULL worker**, NOT per-host bots: the single coordinator (`dev-primary`) owns the
Telegram bot + the venue; it ANNOUNCES claimable work; the no-SSH host's WF3 pull agent (scheduled via
WF2 Task Scheduler / launchd / cron) CLAIMS lease-arbitrated work and reports status outbound. This is a
**security win** — the bot token never leaves the coordinator; pull workers hold only outbound git creds.

---

## Resource Intelligence Summary

### Existing artifacts (assemble, don't reinvent)
- `docs/ops/telegram-hermes-multimachine-control-plane.md` — the Linux SSH-push control plane (Recommendation,
  Canonical state model, Host dispatch posture, Security/token handling, Token rotation, Rollback, MVP path).
  WF4's doc is its **cross-platform sibling**.
- `docs/ops/telegram-venue-contract.md` (F4) — venue consistency (single-active, ordered delivery, idempotency,
  PII-safe audit, absence detection) — the parity readiness/health substrate.
- `docs/ops/pull-dispatch-no-ssh.md` (WF3) — the pull agent + deckhand-trigger story WF4 formalizes.
- `.claude/skills/operations/telegram-hermes-bot/references/` — control-surface-issue-tree (item 6 = this plan),
  multimachine-readiness-audit, multihost-dispatch-readiness-and-redaction, 2720-mvp-continuation.
- `config/workstations/registry.yaml` `telegram_hermes` per machine — current posture: dev-primary=coordinator,
  dev-secondary=worker (both dispatch_enabled), ace-win-1/2 + macbook = desktop-status-only, gali = disabled.
- Cross-repo send-path: **deckhand#179** (the venue send-path; gated behind `VENUE_LEASE_ENABLED`).

### Gaps identified
- No documented promotion path from `desktop-status-only` → dispatch target for the no-SSH classes.
- The WF3 pull model + F4 venue contract aren't yet tied into a single per-class parity recommendation.

### Evidence
```
$ control-surface-issue-tree.md:20  "Windows/macOS stay status-only/manual until an approved parity plan exists"
$ registry: ace-win-1/2,macbook = telegram_mode: desktop-status-only, dispatch_enabled: false; gali = disabled
$ WF3 dispatch_pull.py = the pull claim path; F4 venue_* = the consistency/health layer
```

---

## Approach — produce `docs/ops/windows-macos-dispatch-parity.md` (new design doc)

A cross-platform sibling to the Linux control-plane runbook. Sections map 1:1 to the #2742 acceptance:

1. **Recommendation (the decision).** Three host classes:
   - *Coordinator* (`dev-primary`) — owns the Telegram bot + venue; unchanged.
   - *SSH worker* (`dev-secondary`) — push-dispatch as today.
   - *No-SSH pull worker* (`ace-win-1/2`, `macbook`, `gali`) — **coordinator-routed pull worker**: NO
     inbound bot; runs the WF3 pull agent on a schedule, claims lease-arbitrated work, reports outbound.
   Per-host inbound bots are **rejected** (no inbound reach + token sprawl). Status-only is the pre-promotion state.
   - **Enum constraint (verified):** `telegram_mode` is validated against a CLOSED set
     `{coordinator, worker, desktop-status-only, disabled}` (`scripts/telegram_dispatch/policy.py:21`,
     invalid → `DispatchPolicyError`). So a promoted no-SSH host uses the EXISTING `telegram_mode: worker`
     — the pull-vs-push distinction is **derived from `ssh: null`** (no push reach ⇒ the dispatcher must
     use `dispatch_pull.py`), NOT a new mode value. WF4 is doc-only and must NOT change the enum.
2. **Service model per OS.** Windows = Task Scheduler (WF2) runs `dispatch_pull.py` + `equality-report.ps1`;
   macOS = launchd agent; gali (linux no-SSH) = cron. NO inbound daemon on pull workers; coordinator keeps
   its hermes gateway.
3. **Secret storage & allowlist posture.** Bot token + `TELEGRAM_ALLOWED_USERS` live ONLY on the coordinator.
   Pull workers need only outbound git creds (`gh auth`) — no bot token. Authority is the registry
   `data_access_profile` + the git-ref lease; the coordinator enforces the venue allowlist (F4 single-active gating).
4. **Readiness evidence (mirror Linux).** A pull worker is healthy iff its equality self-report (WF2/WF5) is
   fresh AND it heartbeats claims/reports within the freshness threshold; `venue_absence_detector.py` (F4)
   flags silent-stop; evidence format = the same `equality-<machine>.yaml` + readiness report the Linux hosts emit.
5. **MVP promotion checklist (per machine class).** status-only → pull-worker gates: (a) reconciler converged
   (WF1); (b) `gh auth` + `pyyaml` present; (c) scheduled pull task registered (WF2); (d) fresh equality
   self-report (WF2/WF5); (e) a dry-run claim proven (`dispatch_pull --machine X`); (f) lease ref namespace
   reachable on origin; (g) registry flip `dispatch_enabled: true` + `telegram_mode: worker` (existing enum;
  `ssh: null` keeps it a pull worker) — operator step.
6. **Rollback & token rotation.** Demote = unregister the scheduled task + flip registry back to status-only
   (no token to rotate on the worker — rotation stays a coordinator-only concern, simpler than the SSH model).

Cross-link the new doc from the Linux runbook ("Cross-platform parity → see windows-macos-dispatch-parity.md")
and note the deckhand#179 send-path dependency for the announce side.

## Files to add / modify
- `docs/ops/windows-macos-dispatch-parity.md` (NEW — the WF4 deliverable)
- `docs/ops/telegram-hermes-multimachine-control-plane.md` (1 cross-reference line under its parity note)
- No code, no registry mutation (registry flips are the operator step in the MVP checklist, not this PR).

## Implementation order
1. Write the parity doc (6 sections above), grounding each claim in the existing artifact it assembles.
2. Add the cross-ref line in the Linux runbook.
3. Check the #2742 acceptance boxes against the doc sections.
4. Land via GitHub API → PR; durable record + acceptance mapping on #2742.

## Verification
- Each of the 6 #2742 acceptance checkboxes maps to a named doc section (table in the PR body).
- All cross-references resolve (the cited files exist on origin/main: venue contract, pull-dispatch doc,
  registry fields, deckhand#179).
- Internal consistency: the recommendation (pull worker, token-on-coordinator-only) is consistent with
  WF3's `dispatch_pull.py` (outbound claim) and F4's single-active venue gating — no contradiction.
- Enum safety: the doc uses only valid `telegram_mode` values (`worker`, not an invented `pull-worker`),
  so the dispatch-policy validator + `tests/telegram_dispatch/test_dispatch_policy.py` stay green.
- No code paths changed → no test impact (doc-only); `validate-schedule.py` still green (unchanged).

## Risks / mitigations
- **Recommendation is a user-owned decision** → presented for endorsement at approval; the architecture
  (no inbound reach on no-SSH hosts) strongly constrains it to pull-worker, but the user can redirect.
- **Doc drift vs deckhand send-path (#179, separate repo)** → the doc states the announce side depends on
  deckhand#179 behind `VENUE_LEASE_ENABLED`; pull-claim works without it (git-ref source), so parity isn't
  blocked on the cross-repo send-path.
- **Scope creep into implementation** → WF4 is doc-only by issue mandate; registry flips + scheduling are
  referenced as downstream operator/WF2 steps, not done here.
- **FUSE / shared tree** → land via GitHub API; durable record on #2742 ( `.planning/` scratch self-cleans).
