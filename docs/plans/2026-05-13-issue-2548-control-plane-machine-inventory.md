# Plan for #2548: feat(control-plane): inventory machine software/auth and dispatch OrcaFlex/AQWA runs to licensed-win-1

> **Status:** draft
> **Complexity:** T1
> **Date:** 2026-05-13
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2548
> **Review artifacts:** scripts/review/results/2026-05-13-plan-2548-claude.md | ...-codex.md | ...-gemini.md

---

## Resource Intelligence Summary

### Existing repo code

- EXISTS: `config/workstations/registry.yaml` — machine capability registry covering all 7 machines (hostname, os, role, workspace_root, ssh, tailscale_ip, capabilities, repos). **Gap:** no per-machine AI-provider auth state column; no smoke/run commands; `dev-secondary.workspace_root = /mnt/workspace-hub` is stale (actual: `/mnt/local-analysis/workspace-hub`).
- EXISTS: `docs/BUSINESS_BRAIN.md:46-61` — §Machines table (Machine, Role, OS, Primary Use only); line 61 states "Machine inventory must answer: installed programs, license availability, AI-provider auth state, repo checkout locations, run/smoke-test commands." **Gap:** none of those five dimensions appear in the table itself.
- EXISTS: `docs/ops/2026-05-04-multimachine-baseline-inventory.md` — detailed baseline with repo placement policy, mount matrix, §5 engineering program availability (OrcaFlex/AQWA absent from Linux; licensed Windows hosts are the targets). Confirms licensed-win-1 `ssh: null` — no remote SSH access.
- EXISTS: `queue/job-schema.yaml` — solver queue schema; `solver: "orcawave | orcaflex"` only; licensed-win-1 polls via `git pull` every 30 minutes. **Gap:** AQWA not supported (tracked by #2641).
- EXISTS: `scripts/solver/submit-job.sh` — Git-backed dispatch: `submit-job.sh <solver> <input_file> [description]` creates a YAML in `queue/pending/`, commits, pushes. Smoke-test command exists.
- EXISTS: `queue/failed/wamit-val-hemisphere/result.yaml` — evidence of live OrcaWave dispatch; queue path `D:\workspace-hub\...` confirms licensed-win-1 polls and runs from that Windows path.
- GAP: No per-machine AI-provider auth state documented anywhere. No unified `docs/ops/machine-inventory.md`.

### Standards

Not applicable — this is an infrastructure documentation issue.

### LLM Wiki pages consulted

No relevant wiki pages for machine inventory.

### Documents consulted

- `config/workstations/registry.yaml` — canonical machine capability data; all 7 machines defined
- `docs/ops/2026-05-04-multimachine-baseline-inventory.md` — detailed program/tool availability per host
- `docs/BUSINESS_BRAIN.md:46-74` — §Machines + §AI Provider Accounts; identifies the inventory requirement; 201-line doc (at limit)
- `scripts/solver/submit-job.sh` — existing dispatch CLI (orcawave/orcaflex via git queue)
- `queue/job-schema.yaml` — queue contract; confirmed orcawave/orcaflex support; AQWA is gap
- Related issue #2641 — `2026-05-04-issue-2641-multimachine-solver-inbox-ingestion.md` plan covers AQWA queue extension; **#2548 must NOT overlap that scope**

### Gaps identified

- No unified machine inventory doc covering all 5 BUSINESS_BRAIN.md required dimensions per machine
- Per-machine AI-provider auth state not recorded anywhere
- AQWA dispatch not yet in queue schema (out of scope for #2548 — tracked by #2641)
- licensed-win-1/licensed-win-2: `ssh: null` — physical access required for direct verification; plan scopes these as "document from registry + mark unverified"
- `dev-secondary.workspace_root` stale in registry.yaml

### Evidence (embedded verification)

**Issue status** (verified 2026-05-13 via GitHub MCP):
- `#2548` — OPEN — feat(control-plane): inventory machine software/auth and dispatch OrcaFlex/AQWA runs to licensed-win-1
- `#2641` — OPEN — feat(solver-queue): hands-off multi-machine inbox ingestion (has plan `2026-05-04-issue-2641-multimachine-solver-inbox-ingestion.md`)

**File existence** (`ls -la` 2026-05-13):
- EXISTS: `config/workstations/registry.yaml` (154 lines, 7 machines)
- EXISTS: `docs/BUSINESS_BRAIN.md` (201 lines)
- EXISTS: `docs/ops/2026-05-04-multimachine-baseline-inventory.md`
- EXISTS: `queue/job-schema.yaml`
- EXISTS: `scripts/solver/submit-job.sh`
- MISSING (new — this plan creates): `docs/ops/machine-inventory.md`

**Line excerpts** (`grep -n` 2026-05-13):
```
# config/workstations/registry.yaml:39 (dev-secondary)
  workspace_root: /mnt/workspace-hub    ← STALE; actual is /mnt/local-analysis/workspace-hub

# queue/job-schema.yaml:14
  solver: "orcawave | orcaflex"         ← AQWA not yet supported

# docs/BUSINESS_BRAIN.md:61
Machine inventory must answer: installed programs, license availability,
AI-provider auth state, repo checkout locations, run/smoke-test commands,
and what work may be dispatched safely.
```

**Gap proofs**:
- `grep -c "auth_state\|smoke_command\|run_command" config/workstations/registry.yaml` → 0 → confirms no auth/smoke fields in registry
- `ls docs/ops/ | grep machine-inventory` → (empty) → confirms no existing inventory doc

**Reproduction proofs**:
N/A — this is a documentation/inventory issue; no runtime failure to reproduce. Skip intentional.

<!-- Verification: distinct sources: (1) config/workstations/registry.yaml, (2) docs/BUSINESS_BRAIN.md, (3) docs/ops/2026-05-04-multimachine-baseline-inventory.md, (4) queue/job-schema.yaml, (5) scripts/solver/submit-job.sh, (6) #2641. Current count: 6 — exceeds minimum 3 ✓ -->

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-05-13-issue-2548-control-plane-machine-inventory.md` |
| New inventory doc | `docs/ops/machine-inventory.md` |
| Registry fix | `config/workstations/registry.yaml` (update `dev-secondary.workspace_root`) |
| BUSINESS_BRAIN.md update | `docs/BUSINESS_BRAIN.md` (add pointer to inventory doc) |
| Plan review — Claude | `scripts/review/results/2026-05-13-plan-2548-claude.md` |
| Plan review — Codex | `scripts/review/results/2026-05-13-plan-2548-codex.md` |
| Plan review — Gemini | `scripts/review/results/2026-05-13-plan-2548-gemini.md` |

---

## Deliverable

A new `docs/ops/machine-inventory.md` covering all 7 machines with the five BUSINESS_BRAIN.md-required dimensions (programs/licenses, AI-provider auth state, repo checkouts, smoke/run commands, dispatch readiness), plus a documented OrcaFlex dry-run workflow using the existing git-backed queue, with `docs/BUSINESS_BRAIN.md` updated to point to it and `config/workstations/registry.yaml` corrected for the stale `dev-secondary` workspace_root.

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | `docs/ops/machine-inventory.md` | Main deliverable: 7-machine inventory table with all 5 required dimensions |
| Modify | `config/workstations/registry.yaml:43` | Fix stale `workspace_root: /mnt/workspace-hub` → `/mnt/local-analysis/workspace-hub` |
| Modify | `docs/BUSINESS_BRAIN.md` | Replace machine table prose with pointer to `docs/ops/machine-inventory.md`; keep <200-line budget |

---

## TDD Test List

This is a T1 documentation issue. Tests are verification commands, not pytest suites.

| Verification step | Command | Expected result |
|---|---|---|
| Inventory covers all 7 machines | `grep -c "^| ace-linux-1\|^| ace-linux-2\|^| licensed-win-1\|^| licensed-win-2\|^| macbook-portable\|^| gali-linux-compute-1\|^| home-win\|^| acma-ws014" docs/ops/machine-inventory.md` | ≥7 rows |
| No stale workspace path in registry | `grep "mnt/workspace-hub" config/workstations/registry.yaml` | (empty output) |
| BUSINESS_BRAIN.md within 200-line budget | `wc -l docs/BUSINESS_BRAIN.md` | ≤200 |
| BUSINESS_BRAIN.md points to inventory doc | `grep "machine-inventory" docs/BUSINESS_BRAIN.md` | match found |
| No absolute hardcoded paths in new doc | `scripts/enforcement/check-no-abs-paths.sh docs/ops/machine-inventory.md` | exit 0 |
| OrcaFlex smoke workflow command is valid | `bash -n scripts/solver/submit-job.sh` | exit 0 (syntax check) |

---

## Acceptance Criteria

- [ ] `docs/ops/machine-inventory.md` exists and covers all known machines from BUSINESS_BRAIN.md §Machines
- [ ] Each machine row explicitly records: (a) installed programs/licenses, (b) AI-provider auth state or "unverified — no SSH", (c) repo checkout locations, (d) smoke/run command or "N/A", (e) dispatch readiness or explicit blocker
- [ ] OrcaFlex dry-run workflow is documented: `scripts/solver/submit-job.sh orcaflex <input> "smoke test"` → pushes to `queue/pending/` → licensed-win-1 picks up via 30-min git-poll
- [ ] AQWA dispatch is documented as gap: "not yet in queue schema — tracked by #2641"
- [ ] licensed-win-1 and licensed-win-2 Windows-host sections explicitly note `ssh: null` and mark unverified fields with "requires physical verification"
- [ ] `config/workstations/registry.yaml` `dev-secondary.workspace_root` corrected to `/mnt/local-analysis/workspace-hub`
- [ ] `docs/BUSINESS_BRAIN.md` machine section updated to link to `docs/ops/machine-inventory.md`; line count stays ≤200
- [ ] No absolute paths in new doc (`scripts/enforcement/check-no-abs-paths.sh docs/ops/machine-inventory.md` exits 0)

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

- **Risk:** licensed-win-1 and licensed-win-2 have `ssh: null` — executor cannot remotely verify programs/licenses. Plan scopes Windows hosts as "document from registry.yaml + baseline inventory; mark unverified." If user can provide a manual inventory snapshot from the physical machine, it should replace the placeholder.
- **Risk:** `docs/BUSINESS_BRAIN.md` is at 201 lines (over the 200-line cap stated in the doc itself). The machine section update must shrink to compensate — pointer to `docs/ops/machine-inventory.md` plus a 1-line summary is sufficient.
- **Risk:** AQWA queue schema extension (needed for full smoke workflow) is tracked by #2641. This plan documents the AQWA dispatch as "gap — pending #2641" to avoid scope overlap with that issue's plan.
- **Open:** Should `home-win` and `acma-ws014` machines from BUSINESS_BRAIN.md be included in the inventory table? They appear in the BUSINESS_BRAIN.md machine table but not in `config/workstations/registry.yaml`. Recommend: include as stub rows in the inventory doc with "registry entry: none — add to registry.yaml before scheduling work."

---

## Complexity: T1

**T1** — three files, no new code module. Creates one documentation file, patches one registry value, and updates one pointer in BUSINESS_BRAIN.md. All source data already exists in registry.yaml and the baseline inventory doc.
