# Plan for #3518: Keep setup-cron wrapper attestation synchronized

> **Status:** plan-review
> **Complexity:** T2
> **Date:** 2026-07-13
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/3518
> **Client:** N/A
> **Lane:** lane:claude
> **Execution mode:** parallel-readonly planning; single-lane implementation on an independent #3518 branch after approval
> **Review artifacts:** `scripts/review/results/2026-07-13-plan-3518-claude.md` | `scripts/review/results/2026-07-13-plan-3518-codex.md` | `scripts/review/results/2026-07-13-plan-3518-gemini.md`

---

## Resource Intelligence Summary

### Existing repo code

- `scripts/cron/setup-cron.sh` will remain the behavior source. PR #3515 replaced a schedule-variant skip with a registry `os=windows` skip so Linux `gpu-claw` receives cron tasks.
- `scripts/enforcement/scheduler_mutation_wrapper_attestations.py` still pins the pre-#3515 wrapper hash and its setup shape still requires the removed schedule-variant branch.
- `tests/enforcement/test_scheduler_mutation_task3.py` already has digest, reachability, dead-scope, early-exit, and mode mutants, but its live-source mutants leave the old digest pin in place. They can therefore reject at `_pinned()` without exercising `_setup_shape()`.
- `scripts/enforcement/check-scheduler-mutation-surfaces.py` reads staged/index blobs. RED/GREEN proof will therefore explicitly stage each path-scoped state instead of relying on working-tree edits.

### Standards and wiki

- Standards and client wiki pages: not applicable; this is a repository-local scheduler enforcement repair.
- `scripts/enforcement/scheduler_mutation_wrapper_attestations.py` implements the relevant layered contract: `_pinned()` enforces exact digest drift detection while setup attestation separately applies `_setup_shape()`. Current task-3 tests attempt reachability hardening, but the live-source mutants need the self-pinning correction described by this plan.

### Documents consulted

- [Issue #3518](https://github.com/vamseeachanta/workspace-hub/issues/3518) records the inherited wrapper-attestation regression and is open with `bug` and `lane:claude`.
- [PR #3515](https://github.com/vamseeachanta/workspace-hub/pull/3515) merged the correct registry-OS behavior at `60f8c6f043039a40bba2f3e9cd51b673acbfdff3` while its Scheduler Mutation Surface Guard was failing.
- [Issue #3475](https://github.com/vamseeachanta/workspace-hub/issues/3475) and its plan establish the adjacent deterministic inventory/source-digest and source-attestation guard that #3518 must preserve; the issue is closed.
- `docs/document-intelligence/README.md` is the repository intelligence entry point. It identifies the drive index as the broad cross-source search surface; no scheduler-wrapper authority document was found there.
- Drive-index query `scheduler mutation wrapper attestation setup-cron` via `scripts/data/drive-index-search/search.py ... --json --caller plan-resource-intel` returned no relevant workspace-hub material; unrelated engineering-title matches were discarded and no external file content will be consumed.

### Gaps identified

- The setup wrapper pin and semantic shape do not describe current `main`.
- Existing semantic mutation tests can be masked by digest mismatch instead of proving `_setup_shape()` rejects unsafe behavior.
- Existing reachability coverage does not independently reject partial dead scope, an indented early exit, an OS-variable overwrite, or terminal delegation moved into conditional/dead scope.

### Evidence

**Issue states** (verified 2026-07-13):

```text
#3518 OPEN — fix(scheduler): keep setup-cron wrapper attestation pin synchronized
#3475 CLOSED — fix(cron): make reconciler deletion identity semantic and verify exact post-write state
PR #3515 MERGED — merge commit 60f8c6f043039a40bba2f3e9cd51b673acbfdff3
```

**File existence** (verified 2026-07-13):

```text
EXISTS scripts/cron/setup-cron.sh
EXISTS scripts/enforcement/scheduler_mutation_wrapper_attestations.py
EXISTS scripts/enforcement/check-scheduler-mutation-surfaces.py
EXISTS tests/enforcement/test_scheduler_mutation_task3.py
EXISTS docs/plans/2026-07-11-issue-3475-cron-semantic-ownership.md
EXISTS docs/document-intelligence/README.md
```

**Reproduction proof** (2026-07-13T22:08:51Z, immutable PR #3517 head `a8128e84c111f5ea54a35b4fda14ae6419b82262`):

```text
$ uv run python scripts/enforcement/check-scheduler-mutation-surfaces.py
ERROR: scripts/cron/setup-cron.sh: delegation attestation failed: setup-default-apply-v1
ERROR: scripts/cron/setup-cron.sh: delegation attestation failed: setup-dry-run-v1
ERROR: scripts/cron/setup-cron.sh: delegation attestation failed: setup-live-reload-v1
ERROR: scripts/cron/setup-cron.sh: delegation attestation failed: setup-remote-reject-v1
ERROR: scripts/cron/setup-cron.sh: delegation attestation failed: setup-windows-skip-v1
ERROR: dispositions must exactly cover migration-required surfaces
```

- Command exit: `1`.
- Current setup wrapper SHA-256: `1a5e5573d00d17c4a820a831549fb92a2dad100b5fbab5572afcefadd57c84c1`.
- Pinned SHA-256: `582d12ed794e9b7ad1b809ff99c32dd844178bfd7eed4f85f9de70edd14ec83d`.
- `_setup_shape()` requires `SCHEDULE_VARIANT == contribute-minimal`; current source uses `MACHINE_OS == windows`.
- Failure mode observed matches issue claim: **YES**.
- Distinct sources consulted: issue #3518, PR #3515, issue/plan #3475, the four affected code/test paths, the document-intelligence entry point, and the drive index.

---

## Artifact Map

| Artifact | Path |
|---|---|
| Plan | `docs/plans/2026-07-13-issue-3518-scheduler-wrapper-attestation.md` |
| Human plan | `docs/reports/2026-07-13-issue-3518-scheduler-wrapper-attestation-plan.html` |
| Tests | `tests/enforcement/test_scheduler_mutation_task3.py` |
| Implementation | `scripts/enforcement/scheduler_mutation_wrapper_attestations.py` |
| Runtime source, read-only | `scripts/cron/setup-cron.sh` |
| Reviews | `scripts/review/results/2026-07-13-plan-3518-{claude,codex,gemini}.md` |
| Delivery | independent #3518 branch/PR; draft PR #3517 will rebase after #3518 merges |

---

## Deliverable

The scheduler mutation guard will attest the current reachable registry-OS Windows skip, retain exact staged-blob pinning, and reject self-pinned unsafe mutants without changing live cron behavior.

---

## Pseudocode

```text
function evaluate_self_pinned(source_body):
    checker, records = current_contract() for this invocation only
    source: bytes = checker.attestation_source("setup-default-apply-v1")
    wrapper_module = sys.modules["scheduler_mutation_wrapper_attestations"]
    save records[source]
    save wrapper_module.WRAPPER_SHA256[source]
    set records[source] = source_body
    set wrapper_module.WRAPPER_SHA256[source] = sha256(source_body)
    call checker.evaluate_attestation(attestation, records, source)
    restore records[source] and wrapper_module.WRAPPER_SHA256[source] in finally (no sys.modules assignment)
    return verdict

test registry_os_windows_gate_contract:
    invoke evaluate_self_pinned separately for each baseline/attestation/mutant
    each invocation loads a fresh staged records dictionary
    assert the unmodified self-pinned baseline passes all five attestations
    for each semantic mutant:
        self-pin that exact mutant body
        assert it fails for source shape, not digest mismatch

mutants include:
    OS field or assignment-target change; predicate inversion or broadening; exit-code change
    remote rejection moved/removed; dry-run/apply split change; live-reload change
    partial dead scope around OS lookup/predicate; indented early exit before gate
    OS variable overwrite between lookup and comparison
    terminal exec moved into conditional/dead scope

concrete mutant constructions include:
    replace b'--field os)' with b'--field schedule_variant)'
    insert b'  MACHINE_OS="linux"\n' between the registry lookup and Windows predicate
    indent the MACHINE_OS lookup + predicate block beneath b'if false; then\n', retain decoy bytes, close with b'fi\n'
    insert b'  exit 0\n' inside an always-true block before the platform gate
    wrap the final exec line beneath b'if [[ "$DRY_RUN" == impossible ]]; then\n...\nfi\n'

update setup source-shape attestation:
    require reachable registry os lookup before an exact Windows predicate and exit 0
    require remote-host rejection after the platform skip
    retain dry-run/apply/live-reload and reachable terminal-exec ordering
    reject decoys, partial dead scope, variable overwrite, and conditional delegation
```

### Index-backed RED/GREEN sequence

1. Add `test_setup_self_pinned_baseline_accepts_registry_os_gate`, the self-pinned mutants, and the exact-pin assertion; stage **only** `tests/enforcement/test_scheduler_mutation_task3.py`. `git add` copies the working test bytes into the index but does not change filesystem import resolution: pytest always imports Python from the working-tree path. With no implementation working-tree edit yet, pytest imports the unchanged implementation. `current_contract()` separately executes `git ls-files -z` plus `git cat-file --batch-command -Z`, so its `records` come from the index. Capture RED specifically at the named baseline test because current `_setup_shape()` still requires the removed schedule-variant predicate.
2. Edit and stage `scripts/enforcement/scheduler_mutation_wrapper_attestations.py` with the new semantic shape while deliberately retaining the stale production pin. The staged blob and working file are identical immediately after `git add`; pytest imports that working file, while `current_contract()` loads the identical staged implementation/source records. Each test calls `load_checker()` afresh, obtains that checker's wrapper module from `sys.modules`, mutates only its `WRAPPER_SHA256[source]` dictionary entry, and restores it in `finally`. Run named semantic tests without xdist: they will pass; only the exact production-pin assertion will remain RED.
3. In the same uncommitted TDD sequence, `test_setup_wrapper_pin_matches_exact_staged_blob` will set `source = checker.attestation_source("setup-default-apply-v1")`, assert `records[source] == (ROOT / source.decode()).read_bytes()`, and assert `wrapper_module.WRAPPER_SHA256[source] == hashlib.sha256(records[source]).hexdigest()`. Update the production constant only after capturing this isolated RED.
4. Stage the refreshed implementation and run GREEN from the exact index state.
5. On the final PR merge ref, re-run the staged-blob equality/digest assertion before accepting CI.

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Modify | `tests/enforcement/test_scheduler_mutation_task3.py` | Add self-pinned RED coverage for current behavior and unsafe reachability/semantic mutants |
| Modify | `scripts/enforcement/scheduler_mutation_wrapper_attestations.py` | Attest the current reachable platform gate and refresh the exact staged-source digest |
| No change | `scripts/cron/setup-cron.sh` | Preserve the already-merged runtime behavior byte-for-byte |
| Update | `docs/plans/README.md` | Index the reviewed plan |
| Create | `docs/reports/2026-07-13-issue-3518-scheduler-wrapper-attestation-plan.html` | Human-facing plan |
| Create | `scripts/review/results/2026-07-13-plan-3518-*.md` | Preserve cross-provider adversarial review evidence |

---

## TDD Test List

| Test name | What it verifies | RED condition | Expected GREEN |
|---|---|---|---|
| self-pinned baseline | Current registry-OS source shape is accepted independently of the production pin | Shape requires removed branch | All five setup attestations pass |
| self-pinned OS field/target mutants | Lookup field and assignment target remain exact | Fixtures absent | Each exact-digest mutant fails shape |
| self-pinned predicate/exit mutants | Predicate cannot invert/broaden and skip remains exit 0 | Obsolete fixture/masked pin | Each exact-digest mutant fails shape |
| self-pinned remote/mode/reload mutants | Remote rejection, mode split, and live reload remain ordered | Masked by pin | Each exact-digest mutant fails shape |
| self-pinned partial-dead-scope mutants | OS lookup/predicate cannot be hidden while decoy fragments remain | Coverage absent | Mutants fail shape |
| self-pinned indented-exit/overwrite mutants | Indented early exit and OS overwrite cannot bypass the gate | Coverage absent | Mutants fail shape |
| self-pinned terminal-delegation mutants | Terminal exec remains reachable and unconditional | Coverage only covers whole-script dead scope | Conditional/dead terminal exec fails shape |
| `test_setup_wrapper_pin_matches_exact_staged_blob` | Constant equals SHA-256 of `current_contract()`'s index record and staged bytes equal working source | Current pin is stale | Staged blob, working source, and pin agree |
| existing task-3 suite | All mutation-surface contracts remain fail-closed | Current setup attestations fail | Suite passes |

---

## Acceptance Criteria

### Plan-review readiness

- [ ] Independent Claude and Codex plan-review artifacts contain no unresolved MAJOR findings; Gemini unavailability is preserved in its artifact and does not reduce the T2 minimum below two available providers.

### Implementation and closeout gates (future; run only after user approval)

- [ ] RED is captured after staging only the new tests: `git add -- tests/enforcement/test_scheduler_mutation_task3.py && uv run pytest tests/enforcement/test_scheduler_mutation_task3.py::test_setup_self_pinned_baseline_accepts_registry_os_gate -q`; expected exit `1` because unchanged `_setup_shape()` requires the removed schedule-variant predicate.
- [ ] The unmodified setup source self-pinned to its own SHA passes all five setup attestations before mutant assertions run.
- [ ] Every OS-field, assignment-target, predicate, exit, remote-rejection, mode-split, live-reload, reachability, overwrite, and terminal-exec mutant is self-pinned to its own exact bytes and fails semantic shape independently of `_pinned()`.
- [ ] Before the production pin changes, the staged semantic implementation passes the self-pinned baseline/mutant subset, while `uv run pytest tests/enforcement/test_scheduler_mutation_task3.py::test_setup_wrapper_pin_matches_exact_staged_blob -q` exits `1` on the stale constant.
- [ ] `test_setup_wrapper_pin_matches_exact_staged_blob` obtains `records` through `checker.read_index_records(ROOT)`, defines `source = checker.attestation_source("setup-default-apply-v1")`, asserts `records[source] == (ROOT / source.decode()).read_bytes()`, and asserts `wrapper_module.WRAPPER_SHA256[source] == hashlib.sha256(records[source]).hexdigest()`; it passes on the final PR merge ref.
- [ ] The #3518 implementation commit changes only the two enforcement/test files; governance commits may change only the plan, plan index, HTML report, and review artifacts enumerated above.
- [ ] Runtime source remains unchanged: `BASE_SHA=$(git merge-base HEAD origin/main) && git diff --exit-code "$BASE_SHA" -- scripts/cron/setup-cron.sh` exits `0`.
- [ ] Focused GREEN passes: `uv run pytest tests/enforcement/test_scheduler_mutation_task3.py -q` exits `0`.
- [ ] Guard GREEN passes: `uv run python scripts/enforcement/check-scheduler-mutation-surfaces.py` exits `0` with no `ERROR:` lines.
- [ ] The tested synthetic merge ref is recorded deterministically: `PR_NUMBER=$(gh pr view --json number --jq .number) && git fetch origin "pull/${PR_NUMBER}/merge" && MERGE_SHA=$(git rev-parse FETCH_HEAD) && printf 'PR=%s MERGE_SHA=%s\n' "$PR_NUMBER" "$MERGE_SHA"` exits `0`.
- [ ] Required PR checks pass: `PR_NUMBER=$(gh pr view --json number --jq .number) && gh pr checks "$PR_NUMBER" --watch` exits `0`; `gh pr checks "$PR_NUMBER" --json name,state,link` supplies the check URLs recorded with `MERGE_SHA` on issue #3518.
- [ ] Legal scan passes: `scripts/legal/legal-sanity-scan.sh --diff-only` exits `0`.
- [ ] T2 cross-provider code review from Claude and Codex has no unresolved MAJOR findings. Gemini will be included if non-interactive authentication is restored; otherwise its `UNAVAILABLE` artifact will be preserved and the two-provider minimum will remain Claude + Codex.
- [ ] After #3518 merges, draft PR #3517 will rebase onto the fix and rerun its guard; #3518 acceptance will not depend on #3517 changes.
- [ ] No live crontab, daemon, or scheduler state is mutated.

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | APPROVE after revision | Three rounds resolved staged-record mechanics, state isolation, concrete mutants, provider gates, and named executable TDD checkpoints |
| Codex | APPROVE after revision | Resolved self-pinned mutants, partial-dead-scope coverage, staged TDD order, and staged-blob digest provenance |
| Gemini | UNAVAILABLE | No non-interactive Gemini auth is configured; provider artifact records the failed invocation |

**Overall result:** PASS — Claude + Codex satisfy T2; Gemini unavailability is documented.

Revisions made after the first Codex review wave:

- Every semantic mutant will carry its own refreshed digest, with an unmodified self-pinned baseline assertion.
- Partial dead scope, indented early exit, OS overwrite, and conditional/dead terminal delegation are explicit required mutants.
- The index-backed RED/GREEN staging order and exact staged-blob pin provenance are executable gates.
- #3518 delivery is independent; #3517 will rebase after this fix instead of carrying it.
- Immutable reproduction SHA, exact command, universal intelligence entry point, issue/file evidence, and exact acceptance commands are recorded.
- The self-pinning helper will use the imported wrapper module's global dictionary with `try/finally`; `current_contract()`'s exact index loader, working-tree import behavior, named RED test, and same-sequence pin refresh checkpoint are explicit.
- Gemini is unavailable. The T2 plan-review gate will use independent Claude and Codex verdicts, and the separately labeled implementation-closeout section defines the later T2 code-review route with the same two available providers.

---

## Risks and Open Questions

- **Parser/reachability risk:** byte-fragment ordering alone cannot prove semantic reachability. Implementation will remain blocked if the planned self-pinned mutants require a parser-sized redesign; that would trigger replanning rather than a broad ad hoc checker.
- **Self-refresh risk:** changing only the hash could bless unsafe behavior. Shape tests will pass with the stale production pin before the exact staged-blob pin is refreshed.
- **Branch drift risk:** the final pin will be derived from the final staged blob and reverified on the PR merge ref, never copied from this plan's reproduction digest.
- **Integration risk:** #3517 may need a rebase and regenerated identity inventory after #3518 merges; that is downstream integration, not #3518 acceptance.
- **Live-state risk:** none in scope; implementation will not execute `setup-cron.sh` or modify crontab.

---

## Complexity: T2

Two enforcement/test files will change. The repair is security-adjacent, index-backed, and independently deliverable without changing runtime behavior.
