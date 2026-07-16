# Plan for #3549: Registry-Driven Linux Connection Helpers with TDD

> **Status:** plan-review — amendment r2 MAJOR; implementation paused
> **Complexity:** T3
> **Date:** 2026-07-16
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/3549
> **Client:** N/A
> **Lane:** lane:claude
> **Review artifacts:** original r3 `scripts/review/results/2026-07-16-plan-3549-{claude,codex,gemini,disagreement}-round3.md`; amendment `scripts/review/results/2026-07-16-plan-3549-amendment-{security,governance,compatibility}-round{1,2}.md`

## Resource Intelligence Summary

### Existing repo code

- `src/workspace_hub/workstations/resolver.py` is the canonical YAML parser but
  currently rereads paths, silently overwrites cross-machine identifiers, and
  returns empty values; it will gain a bytes constructor and strict ownership.
- `scripts/lib/workstation-lib.sh` interpolates values into Python source and
  suppresses stderr, so connection code will not reuse it.
- Five SSH helpers plus `config/tabby/config.yaml` contain disagreeing target
  literals; they will be removed rather than reconciled.
- The two Linux registry records have SSH/address fields but no verification or
  freshness metadata, so current addresses will remain unusable.
- Resolver, operations-subprocess, PowerShell-contract, and conflict-marker tests
  provide the YAML fixture, fake executable, native-skip, staged-blob, NUL-safe,
  and narrow-sentinel precedents this plan will reuse.

### Standards

- Engineering calculation standards are not applicable. Repository security
  rules and the canonical runbook merged through PR #3553 are active.

### LLM Wiki pages consulted

- No relevant wiki applies; registry plus runbook will remain authoritative.

### Documents consulted

- [#3547](https://github.com/vamseeachanta/workspace-hub/issues/3547),
  [#3548](https://github.com/vamseeachanta/workspace-hub/issues/3548),
  [#3549](https://github.com/vamseeachanta/workspace-hub/issues/3549), and
  [#3550](https://github.com/vamseeachanta/workspace-hub/issues/3550) establish
  rollout order, helper scope, TDD, runbook authority, and VNC exclusion.
- [PR #3553](https://github.com/vamseeachanta/workspace-hub/pull/3553), the
  approved design, and `docs/ops/remote-linux-access.md` establish registry →
  runbook → helper → local state, hostname-first access, conventional host-key
  verification, explicit fallback, and no published observed endpoint.
- [#3435](https://github.com/vamseeachanta/workspace-hub/issues/3435) owns broad
  worktree-aware hook installation; [#3552](https://github.com/vamseeachanta/workspace-hub/issues/3552)
  owns the ruleless Gitleaks configuration repair.
- The Drive index search for `remote ssh workstation helper tailscale` returned
  no relevant Drive files. `master_document_index` had coverage gap reason
  `unreachable`; no client paths or unrelated document results will enter this
  plan.
- Three verified helper documents will be updated at their paths in the amended
  file map; the oversized `WORKSPACE_CLI.md` and broken menu move to #3561, and
  the prior false `scripts/.../SCRIPT_ORGANIZATION.md` path will not be used.

### Gaps identified

- Missing: strict policy/overlay loader; shared safe launcher; connection tests;
  staged/commit endpoint guard; native Windows job. PR #3553 is now on `main`.

### Evidence (embedded verification)

**Issue statuses** (verified 2026-07-16 via `gh issue view`):

- `#3547` OPEN/needs-plan; `#3548` CLOSED/done/completeness-verified; `#3549`
  OPEN/needs-plan/priority-high/lane-claude/gate-completeness; `#3550` OPEN/needs-plan;
  PR #3553 was merged as `24d6c66d44b151d3a5800c421190b018a679e73c`.
  Live states will be rechecked before implementation.

**File and drift probe** (verified 2026-07-16; scalar values redacted by design):

```text
machines=7
casefold_identifier_collisions=0
linux_records:ssh_present=2;address_present=2;verification_metadata_present=0
governed_existing_files=6;ipv4_literal_counts=[1,1,2,1,1,2]
new_connection_core_cli_and_tests_exist=False
```

**Inherited test baseline** (reproduced 2026-07-16):

```text
$ uv run pytest tests/workstations/test_machine_path_resolver.py \
    tests/workstations/test_registry.py \
    tests/workstations/test_dev_secondary_ground_truth.py -q
............F.s
FAILED tests/workstations/test_registry.py::TestRegistryCrossReference::test_registry_capabilities_cover_task_requires
1 failed, 13 passed, 1 skipped in 1.40s
```

The inherited failure concerns Windows capability coverage for the unrelated
`ecosystem-reconcile` task. The implementation will compare this exact node and
will not report a new regression when the same node remains red.

**Source count:** 15 distinct issue, file, test, policy, and Drive-index sources.

## Navigation Artifact Map

| Artifact | Path |
|---|---|
| Approved design | `docs/superpowers/specs/2026-07-15-3549-registry-connection-helpers-design.md` |
| This plan | `docs/plans/2026-07-16-issue-3549-registry-connection-helpers.md` |
| Human-facing plan | `docs/reports/2026-07-16-issue-3549-registry-connection-helpers-plan.html` |
| Completeness report | `docs/reports/<completion-date>-3549-completeness.html` |
| Plan review round 3 | `scripts/review/results/2026-07-16-plan-3549-{claude,codex,gemini,disagreement}-round3.md` |

## Deliverable

A strict registry-policy and machine-local-overlay connection system will provide
hostname-first, explicit verified fallback through one shell-free Python command,
with thin Bash and PowerShell wrappers, redacted dry-run behavior, native Windows
verification, and staged-content recurrence protection.

## Exact Interface and Trust Contracts

The approved design specification section `Exact Runtime Contract` will be the normative schema and interface appendix. Implementation will follow its closed registry and overlay schemas, POSIX owner-assertion boundary, Windows fallback exit boundary, uv runtime, wrapper options, dry-run JSON, numeric exits, canonical-host SSH argv, and staged/commit enforcement modes.

The plan will additionally require:

- `WorkstationPathResolver.from_registry_bytes(raw_bytes)` with `from_registry_path` delegating to it, so digest and parse share one immutable read;
- duplicate YAML keys rejected before either registry or overlay validation;
- same-machine duplicate identifiers accepted and cross-machine case-folded collisions rejected;
- generic wrappers requiring an explicit machine while `ssh-dev-secondary.sh` retains its fixed ID;
- inherited OpenSSH streams treated as local interactive output, not durable resolver logging;
- an idempotent `install-hooks.sh --connection-endpoint-only` mode using `git rev-parse --git-path hooks`; full linked-worktree installer repair remains #3435; and
- the checked governed-path manifest covering registry, core, CLI, wrappers, Tabby, endpoint-prohibited docs, and the deferred #3550 VNC row.

## Pseudocode

```text
function load_registry_snapshot(path):
    raw_bytes = read path exactly once
    build records through WorkstationPathResolver.from_registry_bytes(raw_bytes)
    validate all records and reject cross-machine identifier collisions
    return immutable validated records

function canonical_connection_policy(snapshot, identifier):
    machine = resolve exactly one key, hostname, alias, or SSH identifier
    validate closed policy and safe ASCII DNS hostname
    project every security-relevant field into versioned canonical ASCII JSON
    return policy and lowercase SHA-256 of the canonical bytes

function load_verified_fallback(path, policy, policy_digest, now):
    require safe POSIX parent/file owner, type, mode, and non-worktree path
    parse one read through the closed schema and standard IP library
    require policy, digest, protocol range, evidence, and freshness match
    return immutable address without logging raw data

function build_ssh_argv(policy, route, optional_user):
    argv = [ssh, fixed StrictHostKeyChecking=yes]
    append validated user as separate -l argument when present
    for fallback append fixed HostName and canonical HostKeyAlias options
    append canonical hostname as positional destination
    return argv

function run_connection(args):
    snapshot and policy = load and resolve once
    route = explicit verified fallback or default hostname
    argv = build_ssh_argv(policy, route, args.user)
    if dry_run: print deterministic redacted JSON and return success
    inherit terminal with shell=false; map interrupt to 130; return SSH exit

function endpoint_guard(staged_manifest):
    select NUL-delimited paths through the checked governed manifest
    read each selected staged or head-commit blob once
    classify patterns without raw output; honor narrow same-line sentinels
    fail with path, line, and violation class
```

## Reviewed Implementation Amendment

The focused addendum at
`docs/plans/2026-07-16-issue-3549-amendment.md` will supersede this plan's
changed-path table and define the revision-bound approval, review-driven TDD,
line-limit, error-mapping, platform, and #3561 deferral contracts. Implementation
will remain paused until its final review has no MAJOR finding and the user
supplies both approval signals named there.

## Canonical Candidate Changed-Path Map

The complete, sole candidate path authority is the table in
`docs/plans/2026-07-16-issue-3549-amendment.md`. It will be evaluated from
`d9db0d7665c66736ae185e462213c92da9a65d82`; no path in this base document will
extend that table implicitly.

## TDD Test List

| Test group | Required failing nodes before implementation | Green contract |
|---|---|---|
| Registry bytes and identity | path delegates to one bytes read; same-machine duplicate; cross-machine key/hostname/alias/SSH collisions | immutable validated snapshot and compatible path rewriting |
| Closed connection policy | duplicate/unknown keys, wrong types, unsafe hostname, missing SSH, invalid reference/issue/age | rejecting YAML loader and exact schema |
| POSIX overlay integrity | missing, symlink, wrong owner/type/mode, unsafe parent, repo-internal path | owner-controlled regular file or exit 5 |
| Fallback attestation | future verification; reversed/overlong expiry; stale or policy-digest mismatch; field mutations and unrelated edits | ordered policy-bounded timestamps; stable digest; Windows exit 4 |
| SSH argv and host identity | missing/mismatched known host, injected user/target, implicit retry, caller options | canonical destination, fixed HostName/HostKeyAlias, strict checking, one launch |
| CLI and diagnostics | deterministic JSON, raw-value canaries, missing runtimes, child stderr, TTY, interrupt | redacted resolver output; inherited child streams; numeric exits |
| Bash wrappers | non-repo CWD, spaced checkout, missing uv, dry-run, exact argv/exits | thin delegation; fixed secondary ID; explicit generic machine |
| PowerShell wrappers | unsafe command strings, legacy methods, option/exit drift, native skip | argument arrays; hostname parity; native Windows proof |
| Tabby and live inventory | every target-bearing SSH surface classified; tracked endpoint/operator defaults | exact governed manifest; unrelated preferences preserved |
| Endpoint guard | added/modified/deleted/odd path, temporary index, TOCTOU, commit blobs, sentinel adjacency, self-artifacts | same-blob staged and head-ref verdicts without raw values |
| Hook and CI wiring | endpoint-only duplicate insertion in normal/linked worktree; full normal install; Windows skip | git-path endpoint mode; legacy installer deferred; non-skipping CI |

Synthetic addresses and secret controls will be assembled at runtime. Protocol
network constants will use one cited same-line sentinel; no whole-file exemption
will exist. Exact RED/GREEN commands appear in the implementation sequence.

## Implementation Sequence

1. **Dependency and discovery gate:** a fresh implementation worktree will be
   created only after `git merge-base --is-ancestor 24d6c66d HEAD` succeeds; the
   pre-merge planning worktree will never be reused. Live paths, labels, parallel
   sessions, and the inherited baseline will be rechecked before editing.
2. **Slice A — registry bytes and policy:** tests for `from_registry_bytes`,
   path delegation, duplicate YAML keys, same-machine duplicates, collisions, and the
   closed registry policy will fail first:
   `uv run pytest tests/workstations/test_machine_path_resolver.py tests/workstations/test_connection_resolver.py -k 'registry or identifier or policy' -q`.
   Only `resolver.py`, `connection.py`, and the synthetic tests will change before
   that command reaches green.
3. **Slice B — POSIX overlay and digest:** missing, malformed/duplicate, symlink,
   owner, mode, parent, range, future/reversed/overlong timestamps, mutation/stability,
   legacy-field, unrelated-edit, and digest mismatch nodes
   will fail first with
   `uv run pytest tests/workstations/test_connection_resolver.py -k 'overlay or fallback or digest' -q`.
   The minimum overlay loader will then reach green; Windows fallback will remain
   an explicit exit-4 boundary.
4. **Slice C — CLI and interactive launch:** dry-run JSON, numeric exits,
   canonical-host configuration, strict host-key behavior, inherited stderr,
   TTY, and interrupt nodes will fail first with
   `uv run pytest tests/workstations/test_connection_cli.py -q`.
   The focused command module and thin executable CLI will then implement the
   minimum shell-free argv and launch behavior. RED tests will forbid abbreviated
   options, require 126 for unexecutable clients, require 130 for child SIGINT,
   and prove overlay failures retain their domain exit instead of becoming a
   registry error.
5. **Slice D — one Bash tracer:** `connect-workspace-tailscale.sh` delegation,
   non-repo CWD, checkout path with spaces, missing uv, dry-run, and exact argv
   nodes will fail first in `tests/operations/test_connection_helpers_bash.py`.
   One thin wrapper will reach green before the pattern expands.
6. **Slice E — remaining wrappers and Tabby:** tests will first fail for the
   other Bash wrapper, fixed secondary wrapper, both PowerShell wrappers, removed
   legacy methods, explicit machine requirement, and tracked Tabby defaults.
   The wrappers/config will then reach green. Windows CI will install Python and
   uv, run `uv sync --locked`, and preflight `pwsh`; absence will fail as
   `INFRASTRUCTURE_FAILURE` before pytest. Required-native mode will use a Windows
   `.cmd` fake SSH shim and will fail rather than skip when capability is absent.
   Native tests will invoke each PowerShell wrapper from a non-repository CWD and
   a copied checkout path containing spaces, capture argv through the `.cmd` shim,
   prove hostname-mode quoting, and prove Windows fallback exits 4 before SSH.
   The pre-existing dead `scripts/workspace` menu remains deferred to #3561.
7. **Slice F — staged and commit enforcement:** temporary-index tests will fail
   first with
   `uv run pytest tests/enforcement/test_connection_helper_endpoints.py -q`.
   The manifest, stdlib checker, CI mode, and endpoint-only hook mode will reach
   green in normal and linked fixtures; the full legacy installer stays under #3435.
8. **Documentation and full regression:** the three scoped helper documents and the
   conditional runbook when its predicate fires will be updated without endpoint
   examples. The sorted changed paths will be compared with the canonical map.
9. **Artifact review and closeout:** adversarial code review, legal/security
   scans, exact staged-tree verification, issue summary, completeness gate, and
   cleanup audit will run before closeout.

## Acceptance Criteria

- [ ] The implementation branch starts from a descendant of merged #3553 commit
  `24d6c66d44b151d3a5800c421190b018a679e73c`.
- [ ] The user explicitly applies `status:plan-approved`; the implementing agent
  does not self-apply it.
- [ ] The initial Slice A/B/C focused tests retain their recorded RED evidence;
  every amendment correction adds a new failing review-driven test before its
  production correction.
- [ ] Registry connection policy is strict, hostname-first, and contains no
  usable observed fallback address.
- [ ] A fallback address is accepted only from an explicit, current, verified,
  digest-bound, POSIX-owner-controlled machine-local overlay; Windows fallback
  returns the documented unsupported exit without claiming ACL parity.
- [ ] No SSH failure class triggers an automatic second destination.
- [ ] Host-key verification remains enabled and fallback uses the canonical
  host-key alias.
- [ ] All five SSH wrappers delegate through one shell-free Python command.
- [ ] `config/tabby/config.yaml` contains no endpoint or operator defaults while
  unrelated terminal preferences remain intact.
- [ ] Dry-run is deterministic, redacted, and invokes no external process.
- [ ] Resolver, wrapper, and dry-run errors contain field paths and stable classes
  but no raw rejected values, endpoints, identities, environment dumps, or
  overlay contents. Inherited interactive OpenSSH stderr remains an explicitly
  local terminal boundary.
- [ ] Exact staged-blob enforcement covers the governed manifest, added files,
  odd filenames, `connection_command.py`, `test_connection_cli.py`, and TOCTOU
  cases without whole-file exemptions or self-blocking.
- [ ] `uv run python scripts/enforcement/check-connection-helper-endpoints.py --staged`
  passes, and CI commit mode passes with
  `--base-ref origin/main --head-ref HEAD`.
- [ ] `install-hooks.sh --connection-endpoint-only` resolves the real hook path,
  remains idempotent in normal/linked worktrees, and bypasses unrelated legacy steps.
- [ ] Focused tests pass:
  `uv run pytest tests/workstations/test_connection_resolver.py tests/workstations/test_connection_cli.py tests/operations/test_connection_helpers_bash.py tests/operations/test_connection_helpers_ps1_contract.py tests/operations/test_connection_helpers_ps1_native.py tests/enforcement/test_connection_helper_endpoints.py -q`.
- [ ] Existing resolver tests pass:
  `uv run pytest tests/workstations/test_machine_path_resolver.py -q`.
- [ ] The inherited workstation baseline has no new failing node beyond the
  recorded `ecosystem-reconcile` capability failure and expected machine-local
  skip.
- [ ] `bash -n` and `shellcheck` pass for every governed Bash wrapper.
- [ ] The Windows job distinguishes pre-pytest `INFRASTRUCTURE_FAILURE`, then
  passes native hostname-mode tests in required mode with no skip path; fallback
  confirms exit 4.
- [ ] The candidate index tree is frozen with `git write-tree`; paths changed from
  `d9db0d7665c66736ae185e462213c92da9a65d82` equal the canonical map with evidence
  for the conditional row; working-tree files equal staged blobs; and the
  diff-only legal scan passes.
- [ ] The published Gitleaks v8.30.1 release and checksum manifest are reverified;
  the pinned procedure proves defaults with runtime exit 23, then scans the candidate tree
  with finding exit 24. Every review edit restarts all scans.
- [ ] Code/artifact adversarial review is complete and all MAJOR findings are
  resolved or explicitly returned to the user.
- [ ] A summary comment is posted on #3549 before closeout.
- [ ] Closeout records candidate paths, the HEAD-bound module snapshot, measured
  changed-code coverage including `connect-workstation.py`, and evidence checklist; calls
  `classify(...)` then `score_code(..., issue_number=3549)` from
  `completeness_score`; writes `result.to_dict()` to `RECORD.json`; and renders
  with `uv run python scripts/workflow/render_completeness_html.py 3549
  "Registry-driven connection helpers" < RECORD.json`. The exact record is
  stamped into the issue body's fenced `completeness` block.
- [ ] An owner other than the closing actor applies
  `status:completeness-verified`; the server completeness Action succeeds; and
  the pre-completion cleanup audit reports no unexpected residue.

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | MINOR (r3) | Artifact paths plus sparse-review limitations; paths corrected |
| Codex | MAJOR (r3) | YAML duplicates, time bounds, hidden residue, hook scope, paths, uv; corrected inline |
| Gemini | UNAVAILABLE (r3) | No noninteractive credentials; round-3 stub retained |

**Overall result:** USER DECISION REQUIRED. Codex remained MAJOR for three rounds
while Claude reached MINOR; policy stops automatic cycling at this disagreement.

**Implementation amendment reviews r1/r2:** MAJOR in all three local adversarial
lanes. The live `status:plan-approved` label is removed, `status:plan-review`
remains, and no local approval marker exists. The focused addendum will require a
round-3 result with no MAJOR finding before renewed user approval.

**Inline r3 corrections:** reject duplicate YAML keys; close timestamp ordering;
delete tracked FUSE residue; narrow hook worktree scope; use revisioned artifacts
and `uv run python`. No fourth Codex verdict will be manufactured.

## Risks and Open Questions

- **Risk — dependency drift:** implementation will verify its base descends from the merged #3553 commit before RED tests begin.
- **Risk — old endpoints remain in Git history:** current-tree cleanup will not
  erase historical commits. No history rewrite will occur without separate user
  authorization.
- **Risk — registry strictness affects path consumers:** collision validation
  will be added with regression tests so workspace-path rewriting continues to
  accept all currently valid identifiers.
- **Risk — projection omission:** explicit closed-field mutation tests and a versioned canonical format will ensure every security-relevant policy change invalidates the overlay while unrelated valid edits do not.
- **Risk — local overlay permissions differ by OS:** documentation and tests will
  enforce the POSIX owner/mode/symlink boundary. Windows hostname access will be
  supported, while address fallback will fail explicitly until native ACL
  enforcement receives its own reviewed design.
- **Risk — scanner false positives or self-blocking:** the checker will parse only
  exact governed paths and will use runtime-constructed test values plus narrow
  line sentinels.
- **Risk — current Gitleaks configuration replaces defaults:** closeout will use
  pinned default rules plus a positive control rather than the ruleless custom
  file. Ecosystem-wide repair remains owned by
  [#3552](https://github.com/vamseeachanta/workspace-hub/issues/3552) instead of
  being silently expanded into #3549.
- **Risk — hook installer worktree assumptions generalize beyond this guard:**
  #3549 will fix and test the endpoint-guard insertion path. Broader installer
  hardening remains owned by
  [#3435](https://github.com/vamseeachanta/workspace-hub/issues/3435).
- **Risk — the workspace menu remains a dead caller:** its paths are already
  nonexistent and the 575-line file cannot join this scope without a reviewed
  split and product decisions. #3561 will own that repair after #3549; #3549 will
  neither claim compatibility nor reintroduce a default machine.
- **Open questions:** none. The user approved the Option 2 architecture and the
  durable design artifact before this plan was drafted.

## Complexity: T3

**T3** — the issue will change a security-sensitive data boundary and executable
behavior across Python, Bash, PowerShell, YAML, Tabby configuration, Git staged
state, documentation, and Linux/Windows CI. Three independent adversarial review
lanes will be required at both plan and code/artifact stages.
