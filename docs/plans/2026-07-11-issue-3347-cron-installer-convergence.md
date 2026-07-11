# Plan for #3347: Converge setup-cron on the transactional installer

> **Status:** adversarial-reviewed
> **Complexity:** T2
> **Date:** 2026-07-11
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/3347
> **Client:** N/A
> **Lane:** lane:codex
> **Review artifacts:** `scripts/review/results/2026-07-11-plan-3347-claude.md` | `scripts/review/results/2026-07-11-plan-3347-codex.md` | `scripts/review/results/2026-07-11-plan-3347-codex-r2.md` | `scripts/review/results/2026-07-11-plan-3347-gemini.md`

---

## Resource Intelligence Summary

### Existing repo code

- `scripts/cron/setup-cron.sh` will remain the operator-facing compatibility entrypoint, but its Linux install path will stop independently extracting `schedule + script basename` keys and appending lines. That current loop compares schedule and basename in separate whole-crontab searches, so two different lines can jointly produce a false match and commands outside `scripts/` have no stable basename.
- `scripts/cron/cron_apply.py` and `scripts/cron/cron_transaction.py` already provide the target transaction: strict managed-block parsing, explicit external/catalog fingerprints, duplicate convergence, `flock`, compare-and-swap, backup, post-write preservation verification, and rollback.
- `scripts/cron/cron_render.py` already supplies shared machine selection and rendering. The implementation will not create a third renderer or fingerprint vocabulary.
- `config/workstations/harness-state-classes.yaml` already identifies duplicated `notification-purge` lines as catalog-owned when that task is selected. `deckhand-api-presence-sync` has no equivalent explicit installed fingerprint, so the current transactional preview fails closed on its two live duplicates.
- `tests/cron/test_a1_preserved.py` already proves transactional notification-purge deduplication, but its real-catalog check hard-codes four `preserved_external` rows while the live catalog has eight. Because #3347 changes ownership metadata, the implementation will replace that brittle count with semantic owner/task assertions and will keep the whole real-catalog file in the acceptance suite.

### Standards

Not applicable — this is scheduler infrastructure, not an engineering-calculation change. The applicable local standards are the issue lifecycle, TDD, fail-closed crontab transaction, legal scan, and user-gated live mutation rules.

### LLM Wiki pages consulted

No relevant wiki pages. No wiki content will change.

### Documents consulted

- [Issue #3347](https://github.com/vamseeachanta/workspace-hub/issues/3347) — reports cross-schedule false-SKIP and append-only false-ADD behavior in `setup-cron.sh`.
- `docs/plans/2026-06-08-issue-2969-cron-catalog-role-tagging.md` — establishes the fail-closed transactional cutover and forbids guessing ownership or replacing external entries.
- `docs/plans/2026-07-11-issue-3463-cron-singleton-runtime-health.md` — explicitly leaves legacy installer convergence to #3347 while extending explicit catalog ownership.
- `docs/ops/scheduled-tasks.md` — currently documents both legacy setup and transactional apply as install paths; it will be revised to make one transactional implementation authoritative.
- Drive-file index query `cron schedule fingerprint duplicates` — returned project-schedule documents unrelated to cron installation, so no drive file is relevant. `master_document_index` was excluded with reason `unreachable`; other queried indexes were available, with the recorded staleness warnings.

### Gaps identified

- Linux setup still has two write-capable implementations with different safety and idempotence rules.
- `setup-cron.sh --dry-run` lists desired entries but does not compare them transactionally against the live crontab, so it hides ownership blockers and duplicate-removal effects.
- `deckhand-api-presence-sync` lacks an explicit installed fingerprint suitable for its `.claude/skills/.../catalog_delta.py` command.
- The current fingerprint vocabulary has substring-based `command_contains`; it cannot assert a shell-token boundary for the presence-sync script. A new validated `command_token` predicate will be required rather than describing metadata the matcher cannot enforce.
- `cron_apply.py` defaults backup tags to `manual`, so a compatibility wrapper that delegates repeated applies without a unique tag would overwrite the previous recovery artifact.
- No regression test invokes the setup compatibility entrypoint twice against an injectable crontab and proves the second plan is byte-identical with zero duplicate additions.
- The wrapper does not parse `--machine`; physical-host variant selection currently occurs before delegation, so explicit Windows-target behavior needs a defined ordering and regression coverage.
- Operator docs do not yet state that live apply will require a separate reviewed preview and explicit approval after implementation.

### Evidence (embedded verification)

**Issue statuses** (verified 2026-07-11T19:25:32Z):

- [#3347](https://github.com/vamseeachanta/workspace-hub/issues/3347) — OPEN — `status:needs-plan`, `lane:codex`.
- [#2969](https://github.com/vamseeachanta/workspace-hub/issues/2969) — CLOSED — transactional cron catalog foundation.
- [#3463](https://github.com/vamseeachanta/workspace-hub/issues/3463) — CLOSED — singleton runtime and explicit ownership hardening.

**Reproduction proofs** (read-only on `ace-linux-1`, 2026-07-11T19:25:32Z):

```text
$ timeout 15 bash scripts/cron/setup-cron.sh --dry-run
Host: ace-linux-1 → cron_variant: full
Found 56 task(s) for ace-linux-1
DRY RUN — would install the following crontab entries:
  50 */6 * * * ... bash scripts/readiness/equality-matrix-cron.sh ...
  30 4 * * * ... find logs/notifications/ ... -delete ...
  0 5 * * 0 ... .claude/skills/business-marketing/deckhand-api-presence-sync/catalog_delta.py ...
(no changes made)

$ timeout 15 uv run --script scripts/cron/cron_apply.py --machine ace-linux-1 --json
{
  "status": "abort",
  "reason": "uncataloged live cron line(s): [...]",
  "uncataloged": [
    "0 5 * * 0 ... deckhand-api-presence-sync/catalog_delta.py ...",
    "0 5 * * 0 ... deckhand-api-presence-sync/catalog_delta.py ..."
  ]
}

$ timeout 5 crontab -l | rg -n 'equality|notification|deckhand-api-presence'
31:30 4 * * 1 ... scripts/readiness/collect-equality.sh ...
67:# equality-matrix-refresh: daily matrix rebuild ... manual repair per #3347
69:50 */6 * * * ... scripts/readiness/equality-matrix-cron.sh ...
44:30 4 * * * ... find logs/notifications/ ... -delete ...
72:30 4 * * * ... find logs/notifications/ ... -delete ...
66:0 5 * * 0 ... deckhand-api-presence-sync/catalog_delta.py ...
73:0 5 * * 0 ... deckhand-api-presence-sync/catalog_delta.py ...
```

The original daily equality absence has been manually repaired and its canonical cadence is now six-hourly, but duplicate notification/deckhand lines remain. The transactional path correctly refuses unknown ownership; the legacy setup path still cannot represent or safely converge this state. The issue will therefore narrow from “widen the regex” to “retire the duplicate append algorithm and complete explicit ownership.”

Execution mode for implementation will be **single-lane** because wrapper behavior, transaction ownership metadata, and integration tests share the same control flow and should be changed serially.

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-07-11-issue-3347-cron-installer-convergence.md` |
| Human-facing plan | `docs/reports/2026-07-11-issue-3347-cron-installer-convergence-plan.html` |
| Compatibility entrypoint | `scripts/cron/setup-cron.sh` |
| Transaction engine | `scripts/cron/cron_apply.py`, `scripts/cron/cron_transaction.py` |
| Catalog ownership | `config/scheduled-tasks/schedule-tasks.yaml` |
| Tests | `tests/cron/test_setup_cron.py`, `tests/cron/test_cron_apply.py`, `tests/cron/test_cron_transaction.py`, `scripts/cron/tests/test_validate_schedule.py` |
| Operator docs | `docs/ops/scheduled-tasks.md` |
| Review artifacts | `scripts/review/results/2026-07-11-plan-3347-*.md` |

---

## Deliverable

`setup-cron.sh` will become a compatibility wrapper over the single fail-closed transactional installer, with explicit ownership for the remaining Deckhand presence-sync duplicates and repeat-run idempotence coverage.

---

## Pseudocode

```text
setup_cron(args):
    parse --machine, --dry-run, --replace, and --allow-live-reload strictly
    resolve the requested machine (or physical hostname) through cron_render context
    if the resolved target is Windows/contribute-minimal: print Task Scheduler guidance and exit
    if --replace: reject as unsafe
    translate --dry-run to cron_apply default preview
    translate normal invocation to cron_apply --apply
    pass the resolved canonical --machine and explicit --allow-live-reload only when supplied
    exec cron_apply so its exit status and fail-closed reason remain authoritative

transactional_preview(live_crontab, selected_catalog):
    classify every live line using external and catalog fingerprints
    abort on unknown ownership or malformed managed markers
    replace all selected catalog-owned duplicates with one rendered managed entry
    preserve external lines byte-for-byte and with multiplicity
    return deterministic new_text without writing

catalog_ownership(deckhand_presence_sync):
    require a command_token predicate with shell-token boundaries for catalog_delta.py
    require workspace-hub cwd basename
    reject merely similar commands or repository names

unique_backup_tag():
    if caller supplied --ts: validate and use it
    otherwise generate UTC timestamp with subsecond/process uniqueness
    create the backup with exclusive semantics; never overwrite an existing recovery point
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Modify | `scripts/cron/setup-cron.sh` | Remove the append-only fingerprint loop and delegate Linux preview/apply to `cron_apply.py` while preserving safe CLI compatibility. |
| Modify | `scripts/cron/cron_apply.py` | Generate collision-resistant default backup tags and refuse backup overwrite. |
| Modify | `scripts/cron/cron_transaction.py` | Add enforceable token-boundary matching for `command_token`. |
| Modify | `config/scheduled-tasks/schedule-tasks.yaml` | Add an exact installed fingerprint for `deckhand-api-presence-sync`. |
| Modify | `scripts/cron/validate-schedule.py` | Validate field names/types/non-empty values and require a conjunctive command-plus-cwd installed identity. |
| Create | `tests/cron/test_setup_cron.py` | Test compatibility routing, no direct crontab writes, exit propagation, and dry-run/apply argument mapping. |
| Modify | `tests/cron/test_cron_apply.py` | Prove duplicate equality, notification, and Deckhand entries converge transactionally and a second plan is byte-identical. |
| Modify | `tests/cron/test_cron_transaction.py` | Prove exact ownership does not absorb similar external commands or repository names. |
| Modify | `tests/cron/test_a1_preserved.py` | Replace the stale ownership-row count with semantic real-catalog assertions and retain the suite as a required gate. |
| Modify | `scripts/cron/tests/test_validate_schedule.py` | Cover valid and invalid installed fingerprints. |
| Modify | `docs/ops/scheduled-tasks.md` | Document one authoritative transactional install path and the separate live-apply approval gate. |
| Modify | `docs/plans/README.md` | Index this plan and reconcile the closed #3463 row. |

---

## TDD Test List

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| `test_setup_cron_dry_run_delegates_to_transaction_preview` | compatibility preview exposes ownership blockers and changes | subprocess wrapper `--dry-run` with stubbed `uv`/transaction | `cron_apply.py` invoked without `--apply`; exit code propagated |
| `test_setup_cron_default_delegates_to_transaction_apply` | normal Linux setup uses the safe writer | subprocess wrapper with no args | `cron_apply.py --apply`; no shell `crontab -` write path |
| `test_setup_cron_entrypoint_twice_is_idempotent` | actual wrapper argument/env behavior cannot re-add entries | invoke wrapper twice using a temp fake `crontab` command and real transaction modules | second installed text byte-identical; no duplicate growth |
| `test_setup_cron_replace_remains_disabled` | destructive replace stays blocked | `--replace` | nonzero exit; no transaction apply |
| `test_setup_cron_passes_live_reload_only_explicitly` | comms protection is not bypassed implicitly | with/without flag | flag forwarded only when operator supplied it |
| `test_setup_cron_machine_windows_exits_before_linux_transaction` | explicit target controls scheduler branch | `--machine licensed-win-1` | Task Scheduler guidance; transaction not invoked |
| `test_setup_cron_machine_linux_passes_canonical_id` | aliases resolve before delegation | `--machine ace-linux-1` | transaction receives `--machine dev-primary` |
| `test_deckhand_presence_fingerprint_matches_exact_owned_line` | remaining live duplicates become catalog-attributable | current exact command and cwd | catalog-owned classification |
| `test_deckhand_presence_fingerprint_rejects_similar_external_line` | ownership remains fail-closed | similar basename/repository | uncataloged or preserved external, never catalog-owned |
| `test_command_token_requires_shell_token_boundaries` | suffix/prefix/path-lookalikes cannot satisfy ownership | exact token and mutated neighboring characters | exact matches; lookalikes reject |
| `test_cutover_converges_all_known_duplicate_families` | equality/manual repair, notification ×2, Deckhand ×2 converge | bounded live-shape fixture | one rendered entry per selected task; comments/external lines preserved |
| `test_second_cutover_plan_is_byte_identical` | repeated setup cannot ADD again | first plan output as second input | identical `new_text`; zero duplicate growth |
| `test_unknown_line_still_aborts` | convergence does not weaken external safety | fixture plus unknown cron | abort, no write |
| `test_installed_fingerprint_schema_is_fail_closed` | catalog cannot declare a broad or malformed ownership claim | unknown fields, wrong types, empty lists/members, one-field broad substring | validator error; valid command-token-plus-cwd passes |
| `test_equality_tasks_with_shared_wrapper_both_render_once` | shared script paths no longer cause cross-schedule false-SKIP | weekly and six-hourly tasks | both schedules present exactly once |
| `test_default_backup_tags_are_unique_and_exclusive` | repeated applies retain separate recovery points | two applies without `--ts`, forced collision fixture | distinct backups or explicit abort; earlier backup unchanged |
| `test_real_catalog_ownership_semantics_without_brittle_count` | real ownership catalog remains parseable as it grows | live state-class YAML | required owners/task IDs present; no hard-coded total |

---

## Acceptance Criteria

- [ ] RED evidence will be captured for every new regression before production changes.
- [ ] `setup-cron.sh` will contain no independent append/dedupe algorithm and no direct `crontab -` write.
- [ ] Linux preview and apply will use `cron_apply.py`; Windows guidance and disabled `--replace` behavior will remain intact.
- [ ] The current bounded live-shape fixture will converge equality, notification, and Deckhand duplicates to one canonical entry each while preserving unrelated lines.
- [ ] A second transaction over the first output will be byte-identical.
- [ ] Unknown or ambiguous ownership will continue to abort without writes.
- [ ] Repeated default applies will create distinct, non-overwritten backup artifacts or fail explicitly on a forced collision.
- [ ] `uv run pytest tests/cron/test_setup_cron.py tests/cron/test_cron_apply.py tests/cron/test_cron_transaction.py tests/cron/test_a1_preserved.py scripts/cron/tests/test_validate_schedule.py -q` will pass.
- [ ] The broader issue-scoped cron suite `uv run pytest tests/cron scripts/cron/tests -q` will pass without excluding the real-catalog test.
- [ ] `bash -n scripts/cron/setup-cron.sh`, `shellcheck scripts/cron/setup-cron.sh`, `uv run --no-project python scripts/cron/validate-schedule.py`, `git diff --check`, and `scripts/legal/legal-sanity-scan.sh --diff-only` will pass.
- [ ] Code/artifact adversarial review will complete with no unresolved MAJOR findings.
- [ ] Implementation evidence will be posted to #3347 before closure.
- [ ] Live crontab mutation will remain a separate operator-approved step after a fresh bounded preview; this implementation issue will not silently apply the cutover.

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | UNAVAILABLE (r1) | Isolated checkout was not trusted by Claude CLI; no user-level trust settings were changed. |
| Codex | MAJOR (r1) → MINOR (r2) | r1 required enforceable token matching, unique backups, twice-invoked wrapper integration, pre-branch machine routing, fail-closed schema validation, and the real-catalog test. r2 verified those fixes and requested only exact schedule-validator syntax plus review-state reconciliation. |
| Gemini | UNAVAILABLE (r1) | No configured non-interactive authentication. |

**Overall result:** PASS with review-diversity degradation — Codex has no unresolved MAJOR findings; Claude and Gemini were unavailable and produced no substantive signal.

Revisions made after r1:

- Added `cron_transaction.py` token-boundary matcher work and negative tests.
- Added `cron_apply.py` unique/exclusive backup behavior and collision tests.
- Added a real twice-invoked setup entrypoint integration test using a fake crontab seam.
- Defined `--machine` parsing before Windows/Linux branching and added both target tests.
- Expanded fingerprint schema validation to types, non-empty members, allowed fields, and conjunctive identity.
- Brought `test_a1_preserved.py` into scope for a narrow semantic repair and the required suite.
- Replaced the vague ShellCheck gate with an exact command.
- Replaced the remaining generic schedule-validation phrase with its exact command and reconciled Claude's unavailable status after Codex r2 MINOR.

---

## Risks and Open Questions

- **Risk — wrapper compatibility:** existing automation may call setup with no flag and expect an immediate append. Delegation will preserve apply intent but will now correctly abort on unknown ownership or live comms unless explicitly authorized.
- **Risk — ownership overreach:** adding a broad `.claude/skills` regex would absorb unrelated tasks. The plan will use task-specific structured metadata instead.
- **Risk — manual comments:** the equality repair comments are ignore lines and will be preserved; the managed block will own the actual task entries after cutover.
- **Risk — rollout separation:** passing tests will not prove the live crontab was changed. A post-merge bounded preview and explicit user approval will be required before apply.
- **Open question for review:** whether `setup-cron.sh --dry-run` should print human text or JSON by default. The plan will preserve human-readable wrapper output while tests will assert the transaction result, not formatting details.

---

## Complexity: T2

**T2** — the fix will consolidate two installer paths across shell, Python transaction metadata, tests, and operator documentation without changing scheduler architecture.
