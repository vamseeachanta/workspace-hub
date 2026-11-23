# Marker-Readiness Audit — #2566 / #2567 / #2568

Lane: Claude-3 MARKER-READINESS (overnight 6-lane run pack `/mnt/local-analysis/agent-logs/overnight-6lane-20260430-2000`).
Mode: read-only / planning-only. No file edits outside this plan, no commits, no GitHub mutations.
Audit timestamp: 2026-05-01 (HEAD `1aa2f6f47`).

## Context

The dispatch reports prior audits flagged that #2566/#2567/#2568 carry `status:plan-approved` on GitHub but lack committed `.planning/plan-approved/<issue>.md` markers in the local checkout. workspace-hub's gate (per project memory: `feedback_never_offer_to_self_label_plan_approved`, `project_issue_2460_approval_binding`) requires BOTH:

1. Live GitHub label `status:plan-approved` applied by the repo owner.
2. Committed `.planning/plan-approved/<issue>.md` marker on `main` referencing the approved plan path (and ideally the SHA).

Either alone is insufficient. This audit confirms which gate state currently holds for each issue and produces the exact (operator-run) command sequences to bring local-marker state into alignment without violating the `never self-approve` rule.

## Live state — verified 2026-05-01

| # | Title | State | Label `status:plan-approved` | Plan file (committed) |
|---|---|---|---|---|
| 2566 | test(naval-arch): full CI and package validation for yaw and rudder-stock sweep workflows | OPEN | YES (updated 2026-05-01T00:40:05Z) | `docs/plans/2026-04-30-issue-2566-full-ci-package-validation-yaw-rudder-stock.md` (commit `42d4e9496`) |
| 2567 | feat(naval-arch): standards-backed steering gear and rudder-stock design checks | OPEN | YES (updated 2026-05-01T00:41:52Z) | `docs/plans/2026-04-30-issue-2567-standards-backed-steering-gear-rudder-stock-checks.md` (commit `c2b3f91ac`) |
| 2568 | feat(naval-arch): preliminary turning-circle and tactical-diameter estimator input workflow | OPEN | YES (updated 2026-05-01T00:41:59Z) | `docs/plans/2026-04-30-issue-2568-turning-circle-tactical-diameter-estimator.md` (commit `e3e626a31`) |

Latest issue comments (2026-05-01 00:11–00:12 UTC) are the standard "Plan-review ready — approval requested" notes from `vamseeachanta` (owner). Each cites three cross-review artifacts under `scripts/review/results/2026-04-30-plan-25{6,7,8}-{claude,codex,gemini}.md`. Each comment ends with the explicit hard-stop: *"Implementation remains blocked until you explicitly approve/apply `status:plan-approved`."* The label has since been applied (label `updatedAt` timestamps post-date the comments), which is the GitHub-side approval signal.

## Local marker state — verified 2026-05-01

`.planning/plan-approved/` directory listing on HEAD `1aa2f6f47`:

- `2566.md` — **MISSING** (filesystem absent, `git ls-files` empty, `git log --all -- .planning/plan-approved/2566.md` empty).
- `2567.md` — **MISSING** (same verification).
- `2568.md` — **MISSING** (same verification).

Reference markers committed nearby for template fidelity:
- `.planning/plan-approved/2112.md` (Apr 29).
- `.planning/plan-approved/2070.md` (most recent — committed in `db4d6f383 chore(planning): record approved marker for issue 2070`).

## Gate verdict per issue

| # | GitHub gate | Local-marker gate | Implementation allowed now? |
|---|---|---|---|
| 2566 | PASS | **FAIL** | **NO** |
| 2567 | PASS | **FAIL** | **NO** |
| 2568 | PASS | **FAIL** | **NO** |

All three are double-blocked at the gate dispatch checks before any execution lane should pick them up: GitHub label is sufficient, but absent commits in `.planning/plan-approved/` mean any batch agent honoring the project's plan-approval contract must skip them.

## Marker text proposals (verbatim — to be written by operator only)

Pattern follows the `2070.md` template. Each marker is a separate file at `.planning/plan-approved/<issue>.md`. The plan paths below are the exact committed paths confirmed via `git ls-files`.

### `.planning/plan-approved/2566.md`
```
# Approval marker for issue #2566

User approval signal: live GitHub issue #2566 carries status:plan-approved, applied by repository owner before this scheduled execution lane. This marker records that external approval in this checkout; it is not self-approval.

Approved plan: docs/plans/2026-04-30-issue-2566-full-ci-package-validation-yaw-rudder-stock.md
```

### `.planning/plan-approved/2567.md`
```
# Approval marker for issue #2567

User approval signal: live GitHub issue #2567 carries status:plan-approved, applied by repository owner before this scheduled execution lane. This marker records that external approval in this checkout; it is not self-approval.

Approved plan: docs/plans/2026-04-30-issue-2567-standards-backed-steering-gear-rudder-stock-checks.md
```

### `.planning/plan-approved/2568.md`
```
# Approval marker for issue #2568

User approval signal: live GitHub issue #2568 carries status:plan-approved, applied by repository owner before this scheduled execution lane. This marker records that external approval in this checkout; it is not self-approval.

Approved plan: docs/plans/2026-04-30-issue-2568-turning-circle-tactical-diameter-estimator.md
```

## Operator command sequence (run tomorrow, by repo owner, on a clean main)

Run from `/mnt/local-analysis/workspace-hub`. Each issue gets its own atomic commit per the existing `chore(planning): record approved marker for issue <N>` pattern (so `/gsd:undo` and forensics remain per-issue reversible). All three commits are independent and may be batched in a single push.

Pre-flight (verify label still live + clean tree):
```bash
git status --short --branch                       # confirm clean except permitted dirty paths
git pull --ff-only origin main                    # take any owner-side updates first

for n in 2566 2567 2568; do
  gh issue view "$n" --repo vamseeachanta/workspace-hub \
    --json labels --jq '.labels[].name' | grep -qx 'status:plan-approved' \
    && echo "$n: label present" || echo "$n: LABEL MISSING — STOP"
done
```

If any prints `LABEL MISSING — STOP`, abort and re-check on GitHub before continuing.

Then, per issue (example shown for 2566; repeat verbatim with `2567` and `2568`):

```bash
cat > .planning/plan-approved/2566.md <<'EOF'
# Approval marker for issue #2566

User approval signal: live GitHub issue #2566 carries status:plan-approved, applied by repository owner before this scheduled execution lane. This marker records that external approval in this checkout; it is not self-approval.

Approved plan: docs/plans/2026-04-30-issue-2566-full-ci-package-validation-yaw-rudder-stock.md
EOF

git add .planning/plan-approved/2566.md
git commit -m "chore(planning): record approved marker for issue 2566"
```

After all three commits land:
```bash
git log --oneline -6
git push origin main
```

Notes:
- Use targeted `git add <path>` (workspace-hub `coding-style.md` forbids bulk `git add -A`/`.`).
- Do **not** use `--no-verify` — pre-commit hooks must run (cross-review/approval-binding rules enforce here).
- Do **not** force-push.
- Do **not** label or close any issue from these commits.
- If the workspace is dirty with the in-flight overnight skill files (it is), use a worktree per memory `feedback_hermes_active_preflight_check`: `git worktree add ../wh-marker-readiness main && cd ../wh-marker-readiness` and run the marker writes there. Otherwise, narrow `git add` keeps unrelated A/M files out of the marker commits.

## Ranking — which one comes next after #2112

Recommended order after #2112 (most recently committed approved marker is `2070`; `2112` referenced in dispatch is the Apr 29 marker), once marker state is fixed:

1. **#2566 first** — quality / CI hardening (T2). It validates the *existing* yaw + rudder-stock sweep workflows with full CI gates and clean-install/package-data smoke. Lowest blast radius (no new functional code) and creates the green baseline that #2567 needs.
2. **#2567 second** — new standards-backed steering-gear and rudder-stock design checks. Builds on the same domain code that #2566 just hardened, so any regressions in #2567 surface against a known-good gate. Higher functional risk than #2566.
3. **#2568 third** — preliminary turning-circle/tactical-diameter estimator *input* workflow. Independent of the rudder-stock thread, so it could even run in parallel with #2567, but because it is a brand-new estimator scaffold it should not jump ahead of CI-hardening (#2566) or the standards-backed-checks landing (#2567).

Sequencing rationale: land the test net before the new features that will exercise it; treat the independent estimator scaffold as the trailing item where its blast radius is lowest.

## Verification (after operator runs the sequence)

End-to-end self-check (read-only — safe for any agent to run):
```bash
ls .planning/plan-approved/2566.md .planning/plan-approved/2567.md .planning/plan-approved/2568.md
git log --oneline -- .planning/plan-approved/2566.md .planning/plan-approved/2567.md .planning/plan-approved/2568.md
git ls-files .planning/plan-approved/2566.md .planning/plan-approved/2567.md .planning/plan-approved/2568.md

for n in 2566 2567 2568; do
  echo "=== $n ==="
  gh issue view "$n" --repo vamseeachanta/workspace-hub --json labels --jq '.labels[].name' | grep -E 'status:'
done
```

Expected post-fix state for each issue: marker file present, single commit in log, listed in `git ls-files`, and live label still includes `status:plan-approved` (and only `status:plan-approved` from the `status:` family — no lingering `status:plan-review`).

## Critical files (read-only reference)

- `.planning/plan-approved/2070.md` — template marker (most recent, complete pattern).
- `.planning/plan-approved/2112.md` — older marker variant (one-line approval phrasing, also valid).
- `docs/plans/2026-04-30-issue-2566-full-ci-package-validation-yaw-rudder-stock.md`
- `docs/plans/2026-04-30-issue-2567-standards-backed-steering-gear-rudder-stock-checks.md`
- `docs/plans/2026-04-30-issue-2568-turning-circle-tactical-diameter-estimator.md`
- `scripts/review/results/2026-04-30-plan-{2566,2567,2568}-{claude,codex,gemini}.md` — adversarial review artifacts cited in the approval-request comments.
- Memory references: `feedback_never_offer_to_self_label_plan_approved.md`, `project_issue_2460_approval_binding.md`, `feedback_hermes_active_preflight_check.md`.
