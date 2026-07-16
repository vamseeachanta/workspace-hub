# Plan for #3554: Windows equality publisher false success without `flock`

> **Status:** draft
> **Complexity:** T2
> **Date:** 2026-07-16
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/3554
> **Client:** N/A
> **Lane:** lane:claude
> **Execution mode:** parallel-readonly planning; single-lane implementation after approval
> **Review artifacts:** `scripts/review/results/2026-07-16-plan-3554-claude.md` | `scripts/review/results/2026-07-16-plan-3554-codex.md` | `scripts/review/results/2026-07-16-plan-3554-gemini.md`

---

## Resource Intelligence Summary

### Existing repo code

- `scripts/readiness/publish-equality.sh:48-51` unconditionally invokes `flock -n 9`. A missing executable returns 127, but the `||` branch classifies every nonzero result as active contention and exits 0.
- `scripts/readiness/publish-equality.sh:63-133` already provides the cross-host correctness primitive: fetch the remote branch, create an isolated sparse worktree, commit only allowlisted equality artifacts, fast-forward push, and retry after a race.
- `scripts/readiness/equality-matrix-cron.sh:30-33` trusts publisher exit status. A false zero therefore produces a pass notification and `equality-matrix-cron OK` even when no evidence reaches the remote.
- `tests/readiness/test_publish_equality.py` supplies a real bare-origin fixture and coverage for freshness, allowlisting, dirty/diverged checkout independence, dry-run behavior, and cleanup. It has no missing-tool, concurrent-publisher, or retry-exhaustion coverage.
- `tests/readiness/test_equality_matrix_cron_deps.py` checks only static fail-loud markers; it does not execute the wrapper with a failing publisher.

### Standards and operational contracts

- `docs/standards/CONTROL_PLANE_CONTRACT.md` requires repo-owned provider-neutral behavior; a Windows-scheduled Bash path cannot depend silently on a Linux-only executable.
- `docs/plans/2026-06-08-issue-2972-equality-matrix-fix.md` establishes that equality cron failures will notify and exit nonzero rather than disappear into logs.
- `docs/plans/2026-07-11-issue-3463-cron-singleton-runtime-health.md` rejects silent-success contention for correctness-critical jobs and requires durable, distinct failure evidence.
- `config/scheduled-tasks/schedule-tasks.yaml:31-50` assigns the equality-matrix Bash path to Windows machines and describes origin publication as part of the task contract.

### Documents and history consulted

- [#3554](https://github.com/vamseeachanta/workspace-hub/issues/3554) defines the live Windows failure and publication invariant.
- [#3342](https://github.com/vamseeachanta/workspace-hub/issues/3342) defines divergence-proof equality publication through a sparse worktree.
- [#3511](https://github.com/vamseeachanta/workspace-hub/issues/3511) owns Windows equivalence-sentinel fingerprint/state-ref safety; this plan will not absorb that unmerged scope.
- [#3526](https://github.com/vamseeachanta/workspace-hub/issues/3526) owns a Windows report-only scheduled reconciliation audit.
- [#3557](https://github.com/vamseeachanta/workspace-hub/issues/3557) owns dirty-checkout `STALE-CHECKOUT` action classification.
- Drive-file search for `Windows equality publish lock` returned no relevant files. Coverage gaps reported verbatim: `unreachable` for `ace_knowledge`, `dde_knowledge`, `og_standards_inventory`, `cad_readability`, and `master_document_index`.

### Gaps identified

- The publisher has no cross-platform execution path when `flock` is absent.
- The existing local host lock does not coordinate the actual cross-machine contention domain at `origin/main`.
- The retry contract does not have deterministic tests for two publishers racing on the same remote or for exhausted retries.
- The cron wrapper has no behavioral proof that publisher failure suppresses pass/OK output and propagates nonzero.

### Evidence

**Issue statuses** (verified 2026-07-16):

- `#3342` — CLOSED — always-committed equality matrix.
- `#3511` — OPEN / `status:plan-approved` — Windows sentinel byte/interpreter/scheduler hardening.
- `#3526` — OPEN / `status:needs-plan` — Windows report-only ecosystem audit.
- `#3554` — OPEN / `status:needs-plan` — this publisher defect.
- `#3557` — OPEN / `status:needs-plan` — reconciler no-progress classification.

**Reproduction proof** (2026-07-16T19:55Z, `ace-win-2`, Git Bash):

```text
$ command -v flock || true
$ bash scripts/readiness/publish-equality.sh --dry-run; echo "publish_rc=$?"
scripts/readiness/publish-equality.sh: line 51: flock: command not found
publish-equality: another publish in flight; skipping
publish_rc=0
```

Focused baseline on this machine:

```text
$ uv run pytest -q tests/readiness/test_publish_equality.py
7 failed, 2 passed
```

The failures will show the same missing-`flock` false-contention path. The two passing negative/cleanup cases will not prove publication.

Distinct sources consulted: 12.

---

## Artifact Map

| Artifact | Path |
|---|---|
| Canonical plan | `docs/plans/2026-07-16-issue-3554-windows-equality-publisher.md` |
| Human-facing plan | `docs/reports/2026-07-16-issue-3554-windows-equality-publisher-plan.html` |
| Publisher | `scripts/readiness/publish-equality.sh` |
| Publisher tests | `tests/readiness/test_publish_equality.py` |
| Cron propagation tests | `tests/readiness/test_equality_matrix_cron_deps.py` |
| Review artifacts | `scripts/review/results/2026-07-16-plan-3554-*.md` |

---

## Deliverable

The equality publisher will run on Linux and Windows Git Bash without a host-local `flock` dependency, will converge concurrent publishers through bounded remote-aware retries, and will fail loudly when publication cannot be proven.

## Design decision

The implementation will remove the host-local `flock` gate rather than replace it with a lock-directory fallback. A local lock cannot serialize publishers on different machines, while stale-owner recovery introduces PID-reuse, crash-recovery, TTL-stealing, and owner-cleanup hazards. The existing fetch plus fast-forward push transaction already arbitrates the shared remote state. The implementation will strengthen and test that global transaction.

## Pseudocode

```text
publish(max_attempts, retry_delays):
    validate max_attempts and retry configuration
    for attempt_number in 1..max_attempts:
        clean any publisher-owned temporary worktree
        fetch remote branch
        create unique sparse worktree at fetched remote head
        copy only locally newer, stamped equality evidence
        optionally rebuild the matrix from the union in the sparse worktree
        reject every staged path outside the equality allowlist
        if nothing is newer: return success(noop)
        commit the scoped artifacts
        if dry-run: return success(dry-run)
        push HEAD to the configured remote branch using fast-forward semantics
        if push succeeds: return success(pushed)
        if attempts remain: wait bounded delay and retry from a fresh fetch
    notify failure and return nonzero

equality_cron():
    collect local evidence or fail
    build local matrix or fail
    invoke publisher
    if publisher is nonzero: emit fail notification; never emit pass or OK
    otherwise emit pass notification describing pushed/noop result
```

The public retry interface will be:

- `--max-attempts N` — positive integer, default `3`;
- `--retry-delay-seconds N` — nonnegative integer, default `2`.

Unknown flags, missing values, nonnumeric values, zero attempts, and negative delays will exit 2 before any fetch, worktree, commit, or push. Tests will pass `--retry-delay-seconds 0`; production callers will retain bounded delay without changing their current command lines.

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Modify | `scripts/readiness/publish-equality.sh` | remove the non-portable local gate; implement bounded configurable remote-aware retry with truthful outcomes |
| Modify | `tests/readiness/test_publish_equality.py` | add Windows/no-`flock`, concurrent publisher, retry, and failure tests using the existing real Git fixture |
| Modify if behavioral test requires a seam | `scripts/readiness/equality-matrix-cron.sh` | preserve fail-loud propagation and make success text truthful; no change if tests prove the current wrapper sufficient |
| Modify | `tests/readiness/test_equality_matrix_cron_deps.py` | add behavioral failure-propagation coverage |
| Update | `docs/plans/README.md` | index this plan |
| Modify | `docs/reports/2026-07-16-issue-3554-windows-equality-publisher-plan.html` | keep the existing human-facing plan artifact synchronized with reviewed revisions |

## TDD Test List

Tests will be written and observed RED before implementation changes.

| Test | Contract |
|---|---|
| `test_publishes_when_flock_is_absent` | a MINGW-like PATH without `flock` will publish newer evidence instead of reporting contention |
| `test_concurrent_publishers_converge` | two isolated clones publishing different fresh machine evidence to one bare remote will both terminate cleanly and the final remote will contain both newest records |
| `test_same_checkout_concurrent_publishers_converge` | two publisher processes sharing one checkout/common Git directory will converge or truthfully noop without stranded worktrees, persistent Git locks, corruption, or false success |
| `test_push_race_refetches_and_rebuilds` | a deterministic first-push race will cause a fresh fetch/rebuild/commit rather than force-push or stale overwrite |
| `test_retry_exhaustion_fails_loud` | repeated injected push failures will return nonzero after the configured bound and will not claim success |
| `test_retry_configuration_rejects_invalid_values` | zero, negative, or nonnumeric attempts/delays will fail closed before Git mutation |
| `test_noop_after_peer_publishes_same_evidence` | retry after a peer publishes equivalent/newer evidence will converge as a truthful noop |
| `test_temp_worktrees_cleaned_after_each_attempt` | success, retry, and exhausted failure will leave no publisher-owned worktree residue |
| `test_cron_propagates_publisher_failure` | publisher nonzero will produce cron nonzero plus fail notification, with no pass notification or `OK` line |
| `test_cron_success_claim_matches_publisher_outcome` | pushed/noop success will remain explicit and will not overstate a skipped or failed publication |

Existing freshness, allowlist, dry-run, dirty/diverged checkout, rebuild, and cleanup tests will remain mandatory regression coverage.

## Acceptance Criteria

- [ ] `uv run pytest -q tests/readiness/test_publish_equality.py tests/readiness/test_equality_matrix_cron_deps.py` will pass on Linux and `ace-win-2` Git Bash.
- [ ] `command -v flock` may be absent; `bash scripts/readiness/publish-equality.sh --dry-run` will still execute the publisher and return a truthful result.
- [ ] Two concurrent publishers targeting one bare remote will converge without force push, reset, evidence regression, or abandoned worktrees.
- [ ] Two concurrent publisher processes sharing one checkout/common Git directory will terminate cleanly with no persistent `.git` lock, missing registered worktree, or publisher-owned temporary directory.
- [ ] Retry exhaustion will emit the existing failure notification and exit nonzero.
- [ ] `equality-matrix-cron.sh` will never print `OK` or emit a pass notification after publisher failure.
- [ ] The staged-path allowlist and strictly-newer evidence rule will remain unchanged.
- [ ] No implementation will modify sentinel/state-ref code, scheduler catalog membership, reconciler classification, evidence schema, or matrix semantics.
- [ ] `bash -n scripts/readiness/publish-equality.sh scripts/readiness/equality-matrix-cron.sh` will pass.
- [ ] `bash scripts/legal/legal-sanity-scan.sh --diff-only` and the targeted security scan will pass.
- [ ] Code-stage adversarial review will complete before closeout.
- [ ] Implementation evidence will be posted to [#3554](https://github.com/vamseeachanta/workspace-hub/issues/3554).
- [ ] A supervised `ace-win-2` run of `bash scripts/readiness/reconcile-ecosystem.sh --apply --equality` will show evidence reaching `origin/main`; [#3557](https://github.com/vamseeachanta/workspace-hub/issues/3557) may still independently block a clean-equivalence verdict while the checkout is dirty.

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | UNAVAILABLE r1 | CLI failed before returning a review |
| Codex | MAJOR r1; re-review pending | same-checkout concurrency and retry interface were under-specified; both will be patched before re-review |
| Gemini | UNAVAILABLE r1 | no non-interactive credentials were configured |

**Overall result:** PENDING — implementation will remain blocked.

## Risks and Open Questions

- **Risk — deterministic concurrency testing:** tests will use isolated local bare remotes and explicit test seams for retry timing; they will not depend on public-network race timing.
- **Risk — same-repository Git metadata contention:** simultaneous local publishers may race in the shared Git common directory. The bounded retry will treat Git lock/push failures as retryable only as a whole attempt and will clean publisher-owned worktrees before retrying.
- **Risk — same-repository cleanup interaction:** the test will inventory registered worktrees, publisher-owned temporary directories, and persistent Git lock files after two same-checkout publishers finish; success will require both processes to terminate and all three inventories to be clean.
- **Risk — retry classification:** the publisher will not parse locale-dependent Git error text. It will retry a bounded failed attempt from a fresh fetch, then fail loudly.
- **Risk — collection TOCTOU:** `collect-equality.sh` currently writes its YAML directly while the publisher reads it. Atomic collection output is adjacent but outside #3554 unless implementation tests prove it blocks correctness; a follow-on issue will capture it rather than silently widening scope.
- **Open question for review:** whether the cron pass message must distinguish `pushed`, `noop`, and `dry-run`, or whether truthful publisher output plus wrapper success is sufficient.

### Review revision r1

- The plan will add same-checkout concurrent publisher coverage, not only separate-clone remote contention.
- The retry interface will be fixed as `--max-attempts` and `--retry-delay-seconds` with validated defaults and pre-mutation rejection.
- The existing HTML plan artifact is now correctly classified as `Modify`.

## Complexity: T2

Cross-platform process behavior, real Git concurrency, retry exhaustion, and cron failure propagation require multiple deterministic tests across two scripts, but the design remains bounded to one publisher transaction.
