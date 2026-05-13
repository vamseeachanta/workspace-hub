# Plan for #2646: feat(workstations): package ace-linux-2 direct-work SSH/VNC handoff runbook

> **Status:** draft
> **Complexity:** T1
> **Date:** 2026-05-13
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2646
> **Review artifacts:** scripts/review/results/2026-05-13-plan-2646-claude.md | ...-codex.md | ...-gemini.md

---

## Resource Intelligence Summary

### Existing repo code

- EXISTS: `scripts/operations/connection/vnc-ace-linux-2.sh` — opens SSH tunnel on port 5900, checks if x11vnc is running on ace-linux-2, auto-starts it if absent, launches `xtigervncviewer localhost:5900`. The script is self-contained and handles x11vnc auth/display detection.
- EXISTS: `scripts/operations/connection/ssh-dev-secondary.sh` — SSH to ace-linux-2 using `dev-secondary` alias with Tailscale fallback to `10.1.0.2`. Interactive or command-mode.
- EXISTS: `scripts/operations/workstation-handoff.sh` — bundles GSD planning state (phase/WRK context) into a portable tar.gz. **Covers state transfer, not operator-facing handoff instructions.** The new runbook complements, does not replace, this script.
- EXISTS: `config/workstations/registry.yaml:38-61` — ace-linux-2 defined as `dev-secondary`; capabilities: `agent_clis: [claude]`, full open-source FEA/CFD stack (blender, openfoam, freecad, gmsh, paraview, calculix, meshio, capytaine, tmux, uv, git); `workspace_root: /mnt/workspace-hub` (**stale** — actual `/mnt/local-analysis/workspace-hub`).
- EXISTS: `docs/ops/2026-05-04-multimachine-baseline-inventory.md:§4` — AI program availability matrix confirms claude, codex, gemini, hermes, gh, git, uv, tmux all present on ace-linux-2. SSH to ace-linux-2 confirmed working per live checks on 2026-05-05.
- EXISTS: `scripts/preflight/hermes_preflight.py` + `docs/plans/2026-05-02-issue-2523-hermes-preflight.md` — Hermes preflight checker at plan-review; the runbook preflight section should reference this rather than reinvent tool-presence checks.
- GAP: No operator-facing `ace-linux-2` direct-work handoff doc exists. `workstation-handoff.sh` bundles state; it does not provide SSH/VNC modes, copy-paste worker prompt template, or return protocol.

### Standards

Not applicable — this is an infrastructure documentation issue.

### LLM Wiki pages consulted

No relevant wiki pages for ace-linux-2 handoff runbook.

### Documents consulted

- `scripts/operations/connection/vnc-ace-linux-2.sh` — exact VNC tunnel + viewer invocation; source for VNC-needed mode section
- `scripts/operations/connection/ssh-dev-secondary.sh` — SSH fallback logic; source for SSH-only mode section
- `config/workstations/registry.yaml:38-61` — ace-linux-2 capability and path data
- `docs/ops/2026-05-04-multimachine-baseline-inventory.md` — §7 minimum readiness tasks before deploying work from ace-linux-2; §4 AI program availability
- `docs/plans/2026-05-02-issue-2523-hermes-preflight.md` — confirms preflight checker is in plan-review; runbook can reference it as a future integration point

### Gaps identified

- No ace-linux-2 direct-work handoff runbook exists; operator/agent must reconstruct paths from memory or multiple files
- ace-linux-2 `workspace_root` in `config/workstations/registry.yaml` is stale (`/mnt/workspace-hub` vs actual `/mnt/local-analysis/workspace-hub`)
- No copy/paste worker prompt template for agents launched on ace-linux-2
- No standardized return protocol: where logs/results go, what GitHub comment format to post

### Evidence (embedded verification)

**Issue statuses** (verified 2026-05-13 via GitHub MCP):
- `#2646` — OPEN — feat(workstations): package ace-linux-2 direct-work SSH/VNC handoff runbook
- `#2523` — OPEN — Hermes preflight checker (at `status:plan-review`)
- `#2641` — OPEN — solver-queue multi-machine ingestion

**File existence** (`ls` 2026-05-13):
- EXISTS: `scripts/operations/connection/vnc-ace-linux-2.sh`
- EXISTS: `scripts/operations/connection/ssh-dev-secondary.sh`
- EXISTS: `scripts/operations/workstation-handoff.sh`
- EXISTS: `config/workstations/registry.yaml`
- EXISTS: `docs/ops/2026-05-04-multimachine-baseline-inventory.md`
- EXISTS: `scripts/preflight/hermes_preflight.py`
- MISSING (new — this plan creates): `docs/ops/ace-linux-2-handoff-runbook.md`

**Line excerpts** (`grep/head` 2026-05-13):
```
# config/workstations/registry.yaml:43 (stale workspace_root)
  workspace_root: /mnt/workspace-hub      ← STALE; actual: /mnt/local-analysis/workspace-hub

# scripts/operations/connection/vnc-ace-linux-2.sh:3-4
ACE2_HOST="vamsee@ace-linux-2"
LOCAL_PORT=5900                            ← confirmed VNC tunnel target

# docs/ops/2026-05-04-multimachine-baseline-inventory.md:87
| `claude` | present | present |          ← confirms claude present on ace-linux-2
```

**Gap proofs**:
- `ls docs/ops/ | grep handoff` → (empty) → no existing handoff runbook
- `grep -l "worker prompt\|handoff mode\|return protocol" docs/ops/` → (empty) → confirms gap

**Reproduction proofs**:
N/A — this is a documentation issue; no runtime failure to reproduce. Skip intentional.

<!-- Verification: distinct sources: (1) vnc-ace-linux-2.sh, (2) ssh-dev-secondary.sh, (3) config/workstations/registry.yaml, (4) docs/ops/2026-05-04-multimachine-baseline-inventory.md, (5) workstation-handoff.sh, (6) hermes-preflight plan #2523. Current count: 6 ✓ -->

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-05-13-issue-2646-ace-linux-2-handoff-runbook.md` |
| New runbook | `docs/ops/ace-linux-2-handoff-runbook.md` |
| Registry fix | `config/workstations/registry.yaml` (update `dev-secondary.workspace_root`) |
| Plan review — Claude | `scripts/review/results/2026-05-13-plan-2646-claude.md` |
| Plan review — Codex | `scripts/review/results/2026-05-13-plan-2646-codex.md` |
| Plan review — Gemini | `scripts/review/results/2026-05-13-plan-2646-gemini.md` |

---

## Deliverable

A new `docs/ops/ace-linux-2-handoff-runbook.md` covering: SSH-only and VNC-needed handoff modes (with exact script references), a copy/paste worker prompt template for ace-linux-2 agents, a preflight checklist (SSH health + tool presence + workspace path), and a return protocol (log location + GitHub comment format). Companion fix: stale `workspace_root` corrected in `config/workstations/registry.yaml`.

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | `docs/ops/ace-linux-2-handoff-runbook.md` | Main deliverable: operator-facing runbook |
| Modify | `config/workstations/registry.yaml:43` | Fix stale `workspace_root: /mnt/workspace-hub` → `/mnt/local-analysis/workspace-hub` |

---

## TDD Test List

T1 documentation issue. Tests are verification commands, not pytest suites.

| Verification step | Command | Expected result |
|---|---|---|
| Runbook covers SSH-only mode | `grep -c "SSH-only\|ssh-dev-secondary\|ssh-only" docs/ops/ace-linux-2-handoff-runbook.md` | ≥1 |
| Runbook covers VNC mode | `grep -c "VNC\|vnc-ace-linux-2\|xtigervncviewer" docs/ops/ace-linux-2-handoff-runbook.md` | ≥1 |
| Worker prompt template present | `grep -c "copy.paste\|worker prompt\|ISSUE_NUMBER\|issue_number" docs/ops/ace-linux-2-handoff-runbook.md` | ≥1 |
| Return protocol present | `grep -c "return protocol\|log.*location\|GitHub comment" docs/ops/ace-linux-2-handoff-runbook.md` | ≥1 |
| Security guards present | `grep -c "secret\|token\|OrcaFlex\|OrcaWave\|AQWA" docs/ops/ace-linux-2-handoff-runbook.md` | ≥1 (explicitly forbidden) |
| Stale workspace_root cleared | `grep "mnt/workspace-hub" config/workstations/registry.yaml` | (empty) |
| Script paths referenced in runbook exist | `bash -n scripts/operations/connection/vnc-ace-linux-2.sh && bash -n scripts/operations/connection/ssh-dev-secondary.sh` | both exit 0 |

---

## Acceptance Criteria

- [ ] `docs/ops/ace-linux-2-handoff-runbook.md` exists and includes:
  - **SSH-only mode**: exact command referencing `scripts/operations/connection/ssh-dev-secondary.sh`; when to use (no GUI needed); one-liner remote command form
  - **VNC-needed mode**: exact command referencing `scripts/operations/connection/vnc-ace-linux-2.sh`; reconnect procedure; prerequisite (display running on ace-linux-2)
  - **Preflight checklist**: SSH reachable, VNC/tunnel reachable (when needed), workspace path `/mnt/local-analysis/workspace-hub` synced, branch/worktree ownership explicit, required tools present
  - **Worker prompt template**: copy/paste block with `ISSUE_NUMBER`, `WORKSPACE`, allowed paths, forbidden paths, test/validation commands, completion/blocker return format
  - **Return protocol**: where logs go (`docs/reports/` or GitHub issue comment), what comment format to post, how to signal blocker vs completion
  - **Security section**: explicit "do NOT store secrets/tokens in logs or comments; do NOT assume OrcaFlex/OrcaWave/AQWA available on ace-linux-2"
- [ ] `config/workstations/registry.yaml` `dev-secondary.workspace_root` updated to `/mnt/local-analysis/workspace-hub`
- [ ] Script paths cited in runbook verified to exist: `scripts/operations/connection/vnc-ace-linux-2.sh`, `scripts/operations/connection/ssh-dev-secondary.sh`
- [ ] Runbook does NOT invent a new dispatch infrastructure — it documents use of existing scripts
- [ ] No absolute paths in new doc that conflict with path-handling rules (`scripts/enforcement/check-no-abs-paths.sh docs/ops/ace-linux-2-handoff-runbook.md` exits 0)

---

## Adversarial Review Summary

<!-- Filled in after adversarial review completes. Do not post to GitHub until populated. -->

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | — | — |
| Codex | — | — |
| Gemini | — | — |

---

## Risks and Open Questions

- **Risk:** ace-linux-2 `workspace_root` in registry.yaml is stale. The runbook must cite the corrected path (`/mnt/local-analysis/workspace-hub`) and the registry fix is part of this issue's scope so both land together.
- **Risk:** #2645 (normalize ace-linux-2 repo/mount/path readiness) is still open — the Tier-1 repo clones may not exist yet. The runbook should note this: "Tier-1 repos on ace-linux-2 may not be present; check with `ls /mnt/local-analysis/` before assigning work that requires them. See #2645 for baseline normalization."
- **Risk:** `workstation-handoff.sh` bundles planning state into tar.gz. The new runbook is additive, not a replacement. Ensure the runbook cross-references `workstation-handoff.sh` for phase/WRK context bundling so they stay coherent.
- **Open:** Should the runbook include a `tmux`-session setup pattern for long-running ace-linux-2 work? The issue body doesn't mention it but ace-linux-2 has `tmux` and parallel work is expected. Recommend: include a minimal tmux one-liner as an optional appendix so users don't rediscover it per-session.
- **Open:** #2523 (Hermes preflight checker) is at plan-review. The runbook preflight checklist should either reference the preflight script path once it lands or note "run `scripts/preflight/hermes_preflight.py` once #2523 is approved and implemented." Flag this dependency explicitly.

---

## Complexity: T1

**T1** — two files: one new documentation file and one config line fix. All required information is already documented in existing scripts and registry; this plan assembles it into an operator-facing artifact.
