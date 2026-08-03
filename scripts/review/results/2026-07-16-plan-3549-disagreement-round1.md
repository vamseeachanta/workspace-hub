# Disagreement report — plan #3549 (2026-07-16)

## Verdicts

| Provider | Verdict |
|---|---|
| claude | MAJOR |
| codex | MAJOR |
| gemini | UNAVAILABLE (gemini CLI failed, rc=1: no non-interactive gemini auth configured (GEMINI_API_KEY/GOOGLE_API_KEY/~/.gemini/oauth_creds.json) ) |

## Findings unique to each provider

A finding is 'unique to X' if its text appears in X's artifact but not
verbatim in any other provider's artifact.

### claude

- **[MAJOR] The load-bearing dependency (PR #3553) is a stale DRAFT orphaned by an already-CLOSED issue, and the plan treats "it will land" as certain.** Plan AC #1 (line 285), Risk §1 (line 359), and Impl step 1 (line 238) gate all of Slice A+ on #3553 merging. Verified: #3553 is `state=OPEN draft=true merged=null`, its runbook is NOT on `origin/main`, yet its issue #3548 is already `CLOSED / status:done / status:completeness-verified`. So the runbook was marked complete-and-verified while its artifact never merged, and no open issue now drives #3553 to `main`. #3549 is therefore blocked on an unowned draft. The plan must reconcile this contradictory upstream state (or land #3553) before it is approvable — not merely list it as a risk.
- **[MAJOR] Self-contradicting closeout gate: AC "changed-path manifest equals the reviewed file map" points at two different, non-equal tables.** AC line 326 demands the frozen `git write-tree` changed-path set equal "the reviewed file map." But the plan contains two disjoint lists: the **Artifact Map** (lines 100–117, 16 rows) and **Files to Change** (lines 182–208, ~26 rows). Paths in Files-to-Change but absent from the Artifact Map include `.github/workflows/connection-helper-parity.yml`, `scripts/enforcement/check-connection-helper-endpoints.py`, `scripts/enforcement/install-hooks.sh`, `config/tabby/QUICK_REFERENCE.md`, `config/tabby/INTERNET_ACCESS_SUMMARY.md`, `docs/modules/cli/WORKSPACE_CLI.md`, `docs/modules/cli/SCRIPT_ORGANIZATION.md`, `docs/ops/remote-linux-access.md`, and `docs/plans/README.md`. Whichever table the gate reads, the equality check is either guaranteed to fail or references a non-existent "file map." Designate one canonical changed-path list.
- **[MINOR] `docs/ops/remote-linux-access.md` is listed as `Modify` (line 203) but does not exist on this branch or `origin/main`.** It is created by #3553 (confirmed in that PR's file list). "Modify" is only valid post-dependency; the row should be marked dependency-conditional, and its omission from the Artifact Map (feeds finding 2) should be fixed.
- **[MINOR] The T3 3-lane adversarial-review gate is asserted while one lane is already dead and two artifacts are empty.** Header line 9 and the Artifact Map cite three `2026-07-16-plan-3549-*.md` results; the Claude and Codex files are 0 bytes and the Gemini file already records `UNAVAILABLE … no non-interactive gemini auth`. Per the SOUL Cross-Review Routing contract, a Gemini outage degrades T3→T2 and must be documented as UNAVAILABLE — but the Adversarial Review Summary (lines 345–351) still lists Gemini as a live PENDING lane. Reconcile the T3 claim with the degraded reality or explicitly record the T2 fallback.
- **[MINOR] Whole-file registry digest binding likely makes the "verified fallback" feature dead-on-arrival.** The overlay binds the accepted fallback IP to `SHA-256(entire registry bytes)` (Pseudocode lines 153–158; Risk §4 lines 367–369). `registry.yaml` is high-churn (per-machine `repos:` lists, `readiness_freshness_thresholds`, added machines). Any unrelated edit invalidates every machine's fallback attestation and silently degrades all users to hostname-only until manual re-attestation. The plan accepts this as "safety over partial-field digest complexity," but the practical effect is that the fallback path — the feature's whole point — will usually be invalid. Recommend binding the digest to the specific machine's connection-relevant subtree, not the whole file.
- **[MINOR] The new required Windows CI job has no skip escape hatch and can wedge as a permanently-red required check.** Slice E / AC (lines 266–268, 322–324) require the GH-hosted Windows runner to have `pwsh`, install uv, run `uv sync --locked`, provide a `.cmd` fake-SSH shim, and treat *any* native-test skip as a job failure. This is a deliberate anti-silent-no-op choice, but on a brand-new workflow a provisioning flake (uv/pwsh) fails the required job for infra reasons with no degradation path. Add an infra-vs-test failure distinction so runner flakiness doesn't block merges indefinitely.

### codex

- Plan AC lines 325-327 requires “the changed-path manifest equals the reviewed file map,” and implementation line 277 says it will compare the changed-path set with “this plan’s artifact map,” but the Artifact Map at lines 98-117 is not the Files to Change table at lines 180-208. Required changed files missing from the Artifact Map include `.github/workflows/connection-helper-parity.yml`, `scripts/enforcement/check-connection-helper-endpoints.py`, `scripts/enforcement/install-hooks.sh`, `config/tabby/QUICK_REFERENCE.md`, `config/tabby/INTERNET_ACCESS_SUMMARY.md`, `docs/modules/cli/WORKSPACE_CLI.md`, `docs/modules/cli/SCRIPT_ORGANIZATION.md`, `docs/ops/remote-linux-access.md`, and `docs/plans/README.md`. This makes the closeout equality gate ambiguous and likely impossible to satisfy.
- Plan line 203 marks `docs/ops/remote-linux-access.md` as `Modify`, and lines 44-47 treat it as consulted authority, but the file is absent in this worktree and `git ls-files docs/ops/remote-linux-access.md` returns nothing. PR #3553 does create it, but `gh pr view 3553` shows that PR is still OPEN/draft. The plan needs to make this row explicitly dependency-conditional or describe the post-merge rebase point as the source of the file before it can be modified.
- Plan AC lines 329-331 requires “Pinned Gitleaks default rules” and an archive scan, but the plan has no artifact or command that pins or installs Gitleaks. Local verification found `gitleaks: MISSING`; the existing `scripts/security/secrets-scan.sh` lines 21 and 62 use the repo `.gitleaks.toml` and fail if `gitleaks` is not already installed, which conflicts with the AC’s “without using the repository’s currently ruleless custom configuration” requirement.
- Plan AC lines 336-338 gives `uv run python scripts/workflow/render_completeness_html.py 3549 "Registry-driven connection helpers"` as the render command, but `scripts/workflow/render_completeness_html.py` line 72 reads JSON from stdin via `json.load(sys.stdin)`. The plan does not specify the completeness JSON producer or stdin redirection, so the acceptance command is incomplete and not reproducible.

### gemini

- (none)

