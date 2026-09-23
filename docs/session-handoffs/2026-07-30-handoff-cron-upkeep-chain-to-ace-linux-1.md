# Handoff — cron upkeep chain, Mac → ace-linux-1

**Date:** 2026-07-30
**From:** Claude session on `macbook-portable`
**To:** an agent session on **ace-linux-1** (`dev-primary`, `/mnt/local-analysis/workspace-hub`)
**Why handed over:** every remaining blocker needs on-box evidence the Mac structurally cannot produce.

---

## Entry prompt

> Read `docs/session-handoffs/2026-07-30-handoff-cron-upkeep-chain-to-ace-linux-1.md` in
> workspace-hub. Fix the cron upkeep chain: issues #3709 → #3708 → #3707, plus #3711.
> All three existing plans failed independent adversarial review as MAJOR — read those
> reviews before writing anything. You are on the box that holds the real evidence; use it.
> Do not apply `status:plan-approved` to anything.

---

## State of the chain

| Issue | Title | Status | Independent review |
|---|---|---|---|
| #3707 | daily-cleanup has never disposed of anything (4 defects, dead scheduler) | `needs-plan` | **MAJOR** — 13 findings, 7 major |
| #3708 | no safe crontab re-apply path | `needs-plan` | **MAJOR** — premise proven wrong |
| #3709 | `plan_cutover` silently drops managed-block lines | `needs-plan` | **MAJOR** — 5 major |
| #3711 | `build-cron-identity-inventory.py` is host-dependent | `needs-plan` | not yet planned |

Dependency order is **#3709 → #3708 → #3707**. #3711 is independent but feeds the same
classification machinery, and **you are the only host that can fix it correctly** (see below).

Plan branches: `plan/3707-cron-upkeep-clockwork`, `plan/3708-crontab-reapply-path`,
`plan/3709-managed-block-classification`. Reviews live in `scripts/review/results/` on each
(that directory is gitignored at `.gitignore:577` — prior reviews were force-staged; do the same).

**Read these before planning anything:**
```
git show origin/plan/3709-managed-block-classification:scripts/review/results/2026-07-30-plan-3709-claude-r2.md
git show origin/plan/3708-crontab-reapply-path:scripts/review/results/2026-07-30-plan-3708-claude-r2.md
git show origin/plan/3707-cron-upkeep-clockwork:scripts/review/results/2026-07-30-plan-3707-claude-r2.md
```

---

## Why this is being handed to you specifically

Four things the Mac could not do. Each one blocked a review finding from being resolved.

1. **Live crontab evidence.** Every r2 review recorded "fleet crontabs — could not verify, no SSH".
   All D1 evidence in #3707 is *issue-supplied*, not measured. You have `crontab -l` locally, and
   `ssh ace2` for the second box.
2. **`check-scheduler-mutation-surfaces.py` will not run on macOS** — local git lacks
   `cat-file --batch-command -Z`. Two MAJOR findings on #3709 and #3708 rest on *static reading*
   of the attestation logic and are explicitly flagged for re-confirmation on Linux. Run the
   whole checker and the `--check-html` digest comparison; confirm or overturn them.
3. **#3711 is unfixable from a Mac by construction.** `build-cron-identity-inventory.py` resolves
   workspace roots by touching the filesystem, and macOS resolves `/home` →
   `/System/Volumes/Data/home`, which poisons `gpu-claw`'s rendered lines. A Mac session already
   published a wrong claim from this and had to retract it (PR #3710, `a60e50d80` → `7ac7ce445`).
   You render it correctly.
4. **ace2 has zero hygiene visibility.** No `.claude/state/cron-health/`, no
   `.claude/state/repo-ecosystem-hygiene/` — both YAML tasks are `machines: [dev-primary, ...]`.
   Its 14/14 install claim is **unverified**; no ace2 crontab exists in any evidence set.

---

## The findings you must design against

These are the independently-verified defects. Do not re-derive them; do not ignore them.

### #3709 — five MAJOR

- **The "unification" is at the wrong seam.** The shared artifact takes the classifier *closure*
  as an argument, leaving two independent context builders — already divergent **today**:
  `build_audit_context` yields 10 preservation fingerprints, `build_ownership_context` yields 11.
  They agree only because `classify_line_detail` never reads `catalog_commands` (a dead parameter)
  and discards the difference. **Fixing this at the closure layer leaves the root bug latent.**
- **Preservation is checked *after* exact `line_identities`,** and `_bind_identity` has no collision
  check against preservation fingerprints. Injecting the llm-wiki corpus-ingest line into identities
  returns `cataloged` → deleted. `legacy_exact_lines` (3 live rows) is the reachable route. This is a
  live path to silently killing another repo's 6-hourly job.
- **Fail-open regression:** returning `records: []` on `parse_crontab` error makes `cron-audit`
  exit **0** on a duplicate-marker crontab where it exits **1** today — i.e. it goes quiet on exactly
  the state a half-completed `--replace` leaves behind.
- **The intent report's bypass already exists:** the pseudocode exempts `cataloged` lines, and 3 of
  the 51 absent ace1 occurrences are `cataloged`. A `legacy_exact_lines` YAML row is a
  non-interactive acknowledgement flag.
- **Self-certifying attestation rewrite:** the plan's own pseudocode shape flips
  `python-postwrite-preservation-multiset-v1` to `False` while authorising the rewrite of
  `_preservation_shape` without naming the replacement token set.

Also: `scheduler_mutation_contract.py` is **exactly 400 lines**, the enforced ceiling — one
`ATT_SOURCES` addition breaks `test_enforcement_modules_obey_size_limits`.

**Verified clean, do not re-litigate:** `derive_cron_classifier_branches` is genuinely preserved
(all 12 attestations stay `True` even under a preservation-first reorder); whitespace/ordering
normalisation; `_trailing_newline`; registry identity resolution.

### #3708 — premise wrong, needs re-scoping not re-planning

The issue asserts the fail-closed audit blocks the re-apply path. **It does not.**
`cron_transaction.py:209-217` classifies only `before + after`; all 47 uncataloged lines sit inside
the managed block and are discarded by `_rebuild_lines` without classification. Re-derive this
issue's scope *after* #3709 lands — "no safe re-apply path" may become accurate for the first time,
or dissolve.

**Drop the command-only matcher work entirely.** The rendered `notification-purge` line is
byte-identical to its `legacy_exact_lines` entry, so it already classifies and dedupes via an
existing green test. A command-only identity is schedule-insensitive and would silently revert a
deliberately retuned local purge — contravening `scheduler-mutation-safety.md` line 5.

The **44 / 2 / 1** classification of the 47 lines is correct and independently re-derived; reuse it.

### #3707 — seven MAJOR, one of which is dangerous

- **Fixing `SAFE_BRANCH_RE` arms a dormant auto-merge.** It has two consumers: `daily-cleanup.sh:139`
  (`branch -d`) and `:162`→`:186`
  (`checkout main && merge --ff-only && push origin main && branch -d && push origin --delete`).
  The second is inert today for *two* reasons — the regex matches nothing **and** `bash -c` at `:185`
  can't see the unexported `git_q` from `:56`, so it exits 127. Repair the regex and it arms on every
  branch ≤10 commits ahead authored by `noreply@anthropic.com` (`:173`). **Address this first.**
- **`gh` is fail-OPEN:** `:141` and `:202` end `|| echo 0`, so rate-limit/auth failure reads as
  "no open PR, safe to delete". `:202` is uncapped at ~300+ calls/run.
- **Squash detection is name-based** (`headRefName`, never `headRefOid`) and `worktree_guard.py:72-74`
  has no ahead/unpushed check → reused branch name after a merged PR = force-delete of live commits.
- **An SSOT already exists** and the plan ignores it: `daily-cleanup.sh:21` sources
  `scripts/lib/tier1-repos.sh`, which provides `resolve_tier1_repo_path()` (#3127, marker-validated,
  fail-closed). The plan invents a registry reader keyed on `tier1_baseline` — a key present under
  **dev-primary only** — silently widening the destructive set from 5 repos to 8.
- **`.wt-owner` is inert *and* an escalation.** Exactly one executable creator exists
  (`publish-equality.sh:138`, a throwaway); the ~54 real worktrees come from prose in
  `.claude/skills/**`. `mark-owner` validates nothing, and the same marker gates
  `repo-housekeeping.sh:189-197`'s `git add -A && commit` — so marking a live worktree sweeps human
  WIP into an auto-commit.
- **`CLEANUP_NOOP` would alarm permanently** — "eligible" is never made disjoint from
  "blocked by policy", and the 54 unmarked worktrees stay eligible-but-blocked forever.
- **The plan silently inverts an existing policy:** `reconcile-ecosystem.sh:100-101` sets
  `DESTRUCTIVE_OK=0` on dev-primary deliberately. That is *this box*, holding 100% of the backlog.
  Decide and state the task's `machines:` list explicitly.

---

## Process requirements — these are why the last three plans failed

**Self-review is not the adversarial gate.** Three for three, plans self-reviewed as MINOR and failed
independent review as MAJOR. The mechanism is consistent: a self-review checks whether the plan is
internally consistent; an independent pass reads the code the plan proposes to change. Dispatch a
*different* provider, and brief it with concrete attack classes.

**Every TDD row must state whether it passes on today's `main`, with the command that proves it.**
Prior plans shipped 6/20 and 9/18 rows already green; on #3709 an independent check found **3 of 9
RED claims were false**, including two "can't test this on macOS" excuses that were simply wrong.
A row that is green today is not a test of the change.

**Never apply `status:plan-approved`, and never offer to.** The owner approves. Stop at
`status:plan-review`.

---

## Boundaries

- Do **not** mutate any crontab outside the reviewed transaction path. `setup-cron.sh --replace` is
  hard-disabled (#2969) and must stay so until #3709/#3708 land.
- The **Hermes gateway stays down** by owner decision (dead since 2026-06-16, survived 3 reboots).
  `daily-cleanup` must run from system cron only. Do not revive it.
- Do not run `git stash clear` or unfiltered drop loops — repo memory documents prior damage.
- `preserved_external` (llm-wiki corpus ingest, `0 */6 * * *`) must survive verbatim. It is owned by
  a different repo.
- Windows Task Scheduler is out of scope; `cron_apply.py main()` currently has **no OS guard** and
  isolation lives only in `setup-cron.sh` — the file #3708 proposes to rewrite.

---

## Known-good context

**Working and correctly reporting — do not "fix":** `repo-ecosystem-hygiene-audit.sh` (daily 05:35,
has been reporting this debt for 8+ days), `cron-health-check.sh` (correctly flags
`repository-sync: RUNTIME_ERROR`), the `cron_runtime.py` singleton (not wedged), `git-lock-reaper`,
`return-to-main-guard`. **Detection works; nothing consumes it** — that is the through-line.

**Fleet equality state as of handoff:** dev-primary 27/27, dev-secondary 26/27, gpu-claw 25/27,
ace-win-1/2 18/27 each. #3702 (equality artifacts out of tree) merged as `02f5cfa87f`; its on-box
verification is still outstanding and is a separate task from this chain.

**Environment:** `uv` is at `~/.local/bin/uv` and is **not on the non-interactive SSH PATH** — always
`bash -lc`. `reconcile-ecosystem.sh` does not fetch before scanning, so "0 actions" is not evidence
of health (#3704).
