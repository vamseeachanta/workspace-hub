# Plan for #3728: CI stale command-identity inventory red-lights every PR

> **Status:** draft
> **Complexity:** T2
> **Date:** 2026-08-05
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/3728
> **Client:** N/A
> **Lane:** lane:claude
> **Review artifacts:** scripts/review/results/2026-08-05-plan-3728-claude.md | ...-codex.md | ...-agy.md

---

## Resource Intelligence Summary

### Existing repo code

- `scripts/enforcement/scheduler_mutation_delegation.py:112-123` — `_validate_inventory_digest()`: hashes git-index bytes of eight source files and compares to `inventory["input_digest"]`. When the digest mismatches, it emits the bare string `"identity inventory input digest is stale"` with no hint of which input changed or how to fix it. This is the check that is currently failing on every PR.
- `scripts/cron/build-cron-identity-inventory.py` — the regeneration tool. Accepts `--check` (exit-code-only), `--dry-run`, or no flags (write mode). The eight hashed inputs are: `config/scheduled-tasks/schedule-tasks.yaml`, `config/workstations/registry.yaml`, `config/workstations/harness-state-classes.yaml`, and five scripts under `scripts/cron/` (`build-cron-identity-inventory.py`, `cron_render.py`, `cron_transaction.py`, `cron_line_model.py`, `cron_identity.py`).
- `docs/reports/issue-3475-command-identity-inventory.json` — the inventory artifact. Current committed state has `"input_digest": "b8fe099c..."` and `75 identities` across dev-primary, dev-secondary, gpu-claw. Issue body reports a regenerated draft has 75 identities total (72→75 delta = +6 added, −4 removed for the primary machine slice; total count may differ per machine).
- Prior plan `docs/plans/2026-07-11-issue-3475-cron-semantic-ownership.md` — established the original identity contract and the `input_digest` mechanism. T2 complexity, `lane:claude`, completed (issue #3475 is the parent issue, referenced throughout).
- Prior plan `docs/plans/2026-07-30-issue-3711-host-independent-identity-inventory.md` — addresses host-path dependency in `cron_render.py:workspace_hub_path()`. `status:plan-review`. Related but orthogonal: #3711 fixes cross-machine path resolution; #3728 fixes a stale digest on dev-primary. The #3711 plan notes that its fix may change the inventory output and should precede or be coordinated with any digest bump.

### Standards

| Standard | Status | Source |
|---|---|---|
| Scheduler identity contract | done (basis) | `docs/plans/2026-07-11-issue-3475-cron-semantic-ownership.md` |
| Scheduler mutation safety | done | `.claude/rules/scheduler-mutation-safety.md` |
| Merge-authorization rule 7 | done | `.claude/rules/merge-authorization.md` (bars UNSTABLE merges) |

### Documents consulted

- Issue #3728 body — identifies the root cause (one or more of the 8 source files changed without inventory regeneration), states the identity delta (+6/−4), and calls for an improved error message.
- `docs/plans/2026-07-30-issue-3711-host-independent-identity-inventory.md` — establishes a sequencing dependency: if #3711 lands first, the inventory baseline will shift again. Plan must declare ordering explicitly.
- `config/workstations/registry.yaml` — 7 machines; the inventory covers dev-primary, dev-secondary, gpu-claw (3 of 7 currently checked out on ace-linux-1 at last measurement, per memory: `feedback_verify_coverage_assumptions`).

### Gaps identified

- The +6/−4 identity delta is unknown until `build-cron-identity-inventory.py` is run on a current checkout of `origin/main` — the executor must run this and audit before committing.
- `.claude/rules/scheduler-mutation-safety.md` content not yet read; executor must verify the audit procedure it specifies before regenerating.
- Coordination with #3711 (status:plan-review) is unresolved: if #3711 lands before this issue, the newly committed digest will be stale again. The plan specifies a sequencing rule in Acceptance Criteria.

### Evidence (embedded verification)

**Issue state** (verified 2026-08-05 via `gh issue view`):
- `#3728` — OPEN — "CI: stale command-identity inventory red-lights every PR, including docs-only ones"
- `#3711` — OPEN, `status:plan-review` — "host-independent cron identity inventory"

**File existence** (verified 2026-08-05 via `ls /mnt/local-analysis/workspace-hub/`):
- EXISTS: `scripts/enforcement/scheduler_mutation_delegation.py`
- EXISTS: `scripts/cron/build-cron-identity-inventory.py`
- EXISTS: `docs/reports/issue-3475-command-identity-inventory.json` (75 identities, `input_digest: b8fe099c...`)

**Line excerpt** (`sed -n '112,123p' scripts/enforcement/scheduler_mutation_delegation.py`):
```
def _validate_inventory_digest(inventory, records, errors):
    sources = [b"config/scheduled-tasks/schedule-tasks.yaml", b"config/workstations/registry.yaml",
               b"config/workstations/harness-state-classes.yaml", b"scripts/cron/build-cron-identity-inventory.py",
               b"scripts/cron/cron_render.py", b"scripts/cron/cron_transaction.py",
               b"scripts/cron/cron_line_model.py", b"scripts/cron/cron_identity.py"]
    digest = hashlib.sha256(b"cron-identity-input-v1\0")
    for source in sorted(sources):
        digest.update(struct.pack(">Q", len(source)) + source)
        body = records[source]
        digest.update(struct.pack(">Q", len(body)) + body)
    if inventory.get("input_digest") != digest.hexdigest():
        errors.append("identity inventory input digest is stale")
```

**Gap proof** (no per-source drift identification in the error path):
- `grep -n "drifted\|which.*source\|regenerat" scripts/enforcement/scheduler_mutation_delegation.py` → 0 hits — confirms no existing diagnostic identifies which source drifted.

**Reproduction proof**:
- N/A for direct reproduction (CI is red; running the local check requires `uv`). Issue body confirms the failure mode on PRs #3718, #3719, #3722, #3727 — all `mergeStateStatus=UNSTABLE`. Matched failure mode: "identity inventory input digest is stale" on Scheduler Mutation Surface Guard.

<!-- Verification: 5 distinct sources: issue body (#3728), prior plan (#3475), prior plan (#3711), scheduler_mutation_delegation.py, build-cron-identity-inventory.py. Count: 5 ≥ 3 ✓ -->

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-08-05-issue-3728-cron-identity-inventory-regeneration.md` |
| Regenerated inventory | `docs/reports/issue-3475-command-identity-inventory.json` |
| Improved error message | `scripts/enforcement/scheduler_mutation_delegation.py` |
| Tests | `tests/enforcement/test_scheduler_mutation_delegation.py` (new or extend existing) |
| Plan review — Claude | `scripts/review/results/2026-08-05-plan-3728-claude.md` |
| Plan review — Codex | `scripts/review/results/2026-08-05-plan-3728-codex.md` |
| Plan review — Agy | `scripts/review/results/2026-08-05-plan-3728-agy.md` |

---

## Deliverable

A regenerated `docs/reports/issue-3475-command-identity-inventory.json` with an audited, correct identity set, plus an improved error message in `scheduler_mutation_delegation.py` that names the specific drifted input and prints the remedy command — unblocking all open PRs from the `UNSTABLE` state.

---

## Pseudocode

```
# Step 1: identify which of the 8 sources drifted
# Run on origin/main checkout:
uv run scripts/cron/build-cron-identity-inventory.py --check
# → exits non-zero if stale; compare hashes manually to isolate which file changed

# Step 2: audit the identity delta
uv run scripts/cron/build-cron-identity-inventory.py --dry-run > /tmp/new-inventory.json
# diff old vs new: jq .identities docs/reports/issue-3475-command-identity-inventory.json
# identify the 6 added and 4 removed task_ids by name
# for each added: verify the cron entry is intentional (check schedule-tasks.yaml + registry.yaml)
# for each removed: verify the cron entry was removed intentionally
# if any identity is suspicious: STOP and file a comment on #3728

# Step 3: improve _validate_inventory_digest error message
# In scheduler_mutation_delegation.py:_validate_inventory_digest():
#   After computing digest, if mismatch:
#     identify which source's index-blob hash changed by computing per-source hashes
#     emit: "identity inventory input digest is stale (changed source: <name>)"
#     emit: "To fix: uv run scripts/cron/build-cron-identity-inventory.py"
#   (The per-source identification requires reading stored hashes — store per-source subs in inventory OR compute inline for diff)

# Step 4: write regression test
# test: scheduler_mutation_delegation rejects a PR with a stale digest
# test: error message now contains the drifted source name

# Step 5: regenerate and commit
uv run scripts/cron/build-cron-identity-inventory.py  # writes docs/reports/...json
git add docs/reports/issue-3475-command-identity-inventory.json
git add scripts/enforcement/scheduler_mutation_delegation.py
git commit -m "fix(ci): regenerate cron identity inventory + improve stale-digest diagnostic"
```

---

## Files to Change

| File | Change |
|---|---|
| `docs/reports/issue-3475-command-identity-inventory.json` | Regenerated with correct identity set after audit |
| `scripts/enforcement/scheduler_mutation_delegation.py` | Improve `_validate_inventory_digest()` error message to name which source drifted and print the remedy command |
| `tests/enforcement/test_scheduler_mutation_delegation.py` | Add/extend: test that stale-digest error message now includes source name |

---

## TDD Test List (red → green)

1. **`test_stale_digest_names_drifted_source`** — Mutate one of the 8 source bytes in a fixture inventory; call `_validate_inventory_digest()`; assert the error message contains the drifted source's logical path. RED (current: message is bare string). GREEN after improvement.
2. **`test_stale_digest_includes_remedy`** — Same fixture; assert error message contains the string `build-cron-identity-inventory.py`. RED now. GREEN after.
3. **`test_clean_digest_passes`** — Use a real-inventory fixture with a matching digest; assert no errors added. Should be GREEN before and after (regression guard).
4. **`test_regenerated_inventory_passes_check`** — After regeneration, run `build-cron-identity-inventory.py --check` via subprocess; assert exit code 0. GREEN after regeneration commits.

---

## Acceptance Criteria

- [ ] `scripts/cron/build-cron-identity-inventory.py --check` exits 0 on `origin/main` after the commit.
- [ ] The Scheduler Mutation Surface Guard CI job turns green on at least one open PR that was UNSTABLE before this fix.
- [ ] The identity delta (+6/−4) is documented in the commit message or PR description, naming each added and removed `task_id`.
- [ ] `_validate_inventory_digest()` error message names the specific drifted source file and prints the `uv run ...build-cron-identity-inventory.py` remedy command.
- [ ] TDD tests 1–3 are red before the error-message change and green after; test 4 is green after regeneration.
- [ ] `scripts/legal/legal-sanity-scan.sh` passes.
- [ ] **Sequencing**: if issue #3711 (host-independent inventory) is merged before this plan's implementation begins, the executor must re-run `build-cron-identity-inventory.py` on the new `origin/main` rather than the snapshot from this plan's drafting date. The plan is valid regardless of ordering, but the identity delta audit must be performed on whichever `origin/main` is current at implementation time.

---

## Risks and Open Questions

1. **Identity delta audit is blocking**: if any of the 6 new identities are not recognized as intentional scheduler additions, the executor must stop and escalate rather than committing. The plan requires human sign-off on the delta.
2. **#3711 sequencing**: if #3711 lands concurrently, it changes the inventory baseline. The executor should check `git log --oneline origin/main -5` before running `--dry-run` to confirm #3711 has or has not landed.
3. **Per-source hashing storage**: improving the error message to name the drifted source requires either (a) computing each source's hash inline and comparing pair-wise, or (b) storing per-source hashes in the inventory JSON. Option (a) is simpler and preferred; option (b) changes the inventory schema and may require #3711 coordination.
4. **CI re-trigger**: after the commit, open PRs must be re-triggered (push a fixup or request re-run) to confirm the guard turns green.
