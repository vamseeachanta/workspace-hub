I've verified the plan's claims against the live repo. Notably, one thing I nearly reported as a MAJOR turned out to be wrong on closer inspection: the registry's endpoints are real, stored as `tailscale_ip: 10.1.0.1/10.1.0.2` (registry.yaml:20,186), so the plan's "address fields" and `address_present=2` are grounded — I'm not reporting that. Here is the review.

## Verdict

MAJOR

## Retrieval

- Read the full plan `docs/plans/2026-07-16-issue-3549-registry-connection-helpers.md` (lines 1–395).
- Verified every cited path exists/absent: all wrappers under `scripts/operations/connection/` present; `src/workspace_hub/workstations/resolver.py`, `scripts/lib/workstation-lib.sh`, `config/tabby/{config.yaml,QUICK_REFERENCE.md,INTERNET_ACCESS_SUMMARY.md}`, `config/workstations/registry.yaml`, `docs/modules/cli/{WORKSPACE_CLI.md,SCRIPT_ORGANIZATION.md}`, `scripts/enforcement/install-hooks.sh`, the design spec, and the three precedent test files all present. **`docs/ops/remote-linux-access.md` is MISSING on this branch.**
- Read `resolver.py` (lines 1–90): confirmed `from_registry_path` uses `read_text` (not bytes), `__init__` does last-write-wins `self._id_to_key[identifier.lower()] = key` across machines, `field_for` returns `""` — the plan's three "current behavior" claims are accurate; `from_registry_bytes` genuinely absent.
- `gh issue view` for #3547/#3548/#3549/#3550 and `gh pr view 3553`: issue-state claims in the plan's Evidence block all match reality.
- `git cat-file -e origin/main:docs/ops/remote-linux-access.md` → **NOT on origin/main**; `gh pr view 3553 --json files` → #3553 (still draft) is what delivers the runbook.
- Parsed `registry.yaml` with a Python probe: 7 machines; 4 linux records (dev-primary, dev-secondary, gpu-claw, gali-linux-compute-1), 3 with non-null `ssh`; endpoints stored as `tailscale_ip` on the 2 dev machines (10.1.0.1/10.1.0.2); `casefold_identifier_collisions=0` reproduced (no cross-machine collisions).
- `cat scripts/operations/connection/ssh-dev-secondary.sh`: confirmed hardcoded `10.1.0.2` + the BatchMode auth-probe fallback the plan proposes to remove.
- Inspected the three cited review-result files: `…claude.md` and `…codex.md` are **0 bytes**; `…gemini.md` already contains `UNAVAILABLE (gemini CLI failed, rc=1: no non-interactive gemini auth)`.
- Did NOT re-run the pytest baseline (`1 failed, 13 passed, 1 skipped`) — test files exist but exact counts are unverified.

## Findings

1. **[MAJOR] The load-bearing dependency (PR #3553) is a stale DRAFT orphaned by an already-CLOSED issue, and the plan treats "it will land" as certain.** Plan AC #1 (line 285), Risk §1 (line 359), and Impl step 1 (line 238) gate all of Slice A+ on #3553 merging. Verified: #3553 is `state=OPEN draft=true merged=null`, its runbook is NOT on `origin/main`, yet its issue #3548 is already `CLOSED / status:done / status:completeness-verified`. So the runbook was marked complete-and-verified while its artifact never merged, and no open issue now drives #3553 to `main`. #3549 is therefore blocked on an unowned draft. The plan must reconcile this contradictory upstream state (or land #3553) before it is approvable — not merely list it as a risk.

2. **[MAJOR] Self-contradicting closeout gate: AC "changed-path manifest equals the reviewed file map" points at two different, non-equal tables.** AC line 326 demands the frozen `git write-tree` changed-path set equal "the reviewed file map." But the plan contains two disjoint lists: the **Artifact Map** (lines 100–117, 16 rows) and **Files to Change** (lines 182–208, ~26 rows). Paths in Files-to-Change but absent from the Artifact Map include `.github/workflows/connection-helper-parity.yml`, `scripts/enforcement/check-connection-helper-endpoints.py`, `scripts/enforcement/install-hooks.sh`, `config/tabby/QUICK_REFERENCE.md`, `config/tabby/INTERNET_ACCESS_SUMMARY.md`, `docs/modules/cli/WORKSPACE_CLI.md`, `docs/modules/cli/SCRIPT_ORGANIZATION.md`, `docs/ops/remote-linux-access.md`, and `docs/plans/README.md`. Whichever table the gate reads, the equality check is either guaranteed to fail or references a non-existent "file map." Designate one canonical changed-path list.

3. **[MINOR] `docs/ops/remote-linux-access.md` is listed as `Modify` (line 203) but does not exist on this branch or `origin/main`.** It is created by #3553 (confirmed in that PR's file list). "Modify" is only valid post-dependency; the row should be marked dependency-conditional, and its omission from the Artifact Map (feeds finding 2) should be fixed.

4. **[MINOR] The T3 3-lane adversarial-review gate is asserted while one lane is already dead and two artifacts are empty.** Header line 9 and the Artifact Map cite three `2026-07-16-plan-3549-*.md` results; the Claude and Codex files are 0 bytes and the Gemini file already records `UNAVAILABLE … no non-interactive gemini auth`. Per the SOUL Cross-Review Routing contract, a Gemini outage degrades T3→T2 and must be documented as UNAVAILABLE — but the Adversarial Review Summary (lines 345–351) still lists Gemini as a live PENDING lane. Reconcile the T3 claim with the degraded reality or explicitly record the T2 fallback.

5. **[MINOR] Whole-file registry digest binding likely makes the "verified fallback" feature dead-on-arrival.** The overlay binds the accepted fallback IP to `SHA-256(entire registry bytes)` (Pseudocode lines 153–158; Risk §4 lines 367–369). `registry.yaml` is high-churn (per-machine `repos:` lists, `readiness_freshness_thresholds`, added machines). Any unrelated edit invalidates every machine's fallback attestation and silently degrades all users to hostname-only until manual re-attestation. The plan accepts this as "safety over partial-field digest complexity," but the practical effect is that the fallback path — the feature's whole point — will usually be invalid. Recommend binding the digest to the specific machine's connection-relevant subtree, not the whole file.

6. **[MINOR] The new required Windows CI job has no skip escape hatch and can wedge as a permanently-red required check.** Slice E / AC (lines 266–268, 322–324) require the GH-hosted Windows runner to have `pwsh`, install uv, run `uv sync --locked`, provide a `.cmd` fake-SSH shim, and treat *any* native-test skip as a job failure. This is a deliberate anti-silent-no-op choice, but on a brand-new workflow a provisioning flake (uv/pwsh) fails the required job for infra reasons with no degradation path. Add an infra-vs-test failure distinction so runner flakiness doesn't block merges indefinitely.

## Blockers

- Finding 1 — reconcile the contradictory #3548-closed / #3553-draft / runbook-not-on-main state (or land #3553) before implementation; the plan currently depends on an unowned stale draft.
- Finding 2 — collapse the Artifact Map vs Files-to-Change divergence into one canonical changed-path list so the `git write-tree` closeout gate (AC line 326) is well-defined.

`★ Insight ─────────────────────────────────────`
- **Retrieval skepticism cuts both ways.** The plan's "address fields" reads like a fabrication until you find the registry stores endpoints under `tailscale_ip` — verifying before reporting killed what would have been a false MAJOR. An adversarial reviewer's own findings need the same evidence bar they demand of the plan.
- **The sharpest defects were relational, not local.** Every individual file/claim checked out; the two blockers are *cross-artifact* contradictions (a closed issue vs. an unmerged draft; two file lists a single AC treats as one). Whole-repo/whole-plan consistency checks surface what per-line reading cannot.
- **"Fail-closed" is not automatically "safe."** Binding a per-machine credential to a whole-file hash is fail-closed but self-defeating on a high-churn file — a good reminder that a conservative-sounding mechanism can quietly disable the very feature it guards.
`─────────────────────────────────────────────────`
