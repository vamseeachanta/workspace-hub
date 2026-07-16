# Plan for #3549: Registry-Driven Linux Connection Helpers with TDD

> **Status:** draft
> **Complexity:** T3
> **Date:** 2026-07-16
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/3549
> **Client:** N/A
> **Lane:** lane:claude
> **Review artifacts:** scripts/review/results/2026-07-16-plan-3549-claude.md | scripts/review/results/2026-07-16-plan-3549-codex.md | scripts/review/results/2026-07-16-plan-3549-gemini.md

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
  rules are active; the canonical runbook remains pending through PR #3553.

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
- Four verified helper documents will be updated at their paths in the file map;
  the prior false `scripts/.../SCRIPT_ORGANIZATION.md` path will not be used.

### Gaps identified

- Missing: strict policy/overlay loader; shared safe launcher; connection tests;
  staged/commit endpoint guard; native Windows job. PR #3553 is now on `main`.

### Evidence (embedded verification)

**Issue statuses** (verified 2026-07-16 via `gh issue view`):

- `#3547` OPEN/needs-plan; `#3548` CLOSED/done/completeness-verified;
  `#3549` OPEN/needs-plan/priority-high/lane-claude; `#3550` OPEN/needs-plan;
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
| Registry parser | `src/workspace_hub/workstations/resolver.py` |
| Connection model | `src/workspace_hub/workstations/connection.py` |
| Shared CLI | `scripts/operations/connection/connect-workstation.py` |
| Resolver tests | `tests/workstations/test_connection_resolver.py` |
| Bash tests | `tests/operations/test_connection_helpers_bash.py` |
| PowerShell contract tests | `tests/operations/test_connection_helpers_ps1_contract.py` |
| PowerShell native tests | `tests/operations/test_connection_helpers_ps1_native.py` |
| Endpoint enforcement tests | `tests/enforcement/test_connection_helper_endpoints.py` |
| Governed-path manifest | `config/workstations/connection-governed-paths.yaml` |
| Completeness report | `docs/reports/2026-07-16-3549-completeness.html` |
| Plan review — Claude | `scripts/review/results/2026-07-16-plan-3549-claude.md` |
| Plan review — Codex | `scripts/review/results/2026-07-16-plan-3549-codex.md` |
| Plan review — Gemini | `scripts/review/results/2026-07-16-plan-3549-gemini.md` |

## Deliverable

A strict registry-policy and machine-local-overlay connection system will provide
hostname-first, explicit verified fallback through one shell-free Python command,
with thin Bash and PowerShell wrappers, redacted dry-run behavior, native Windows
verification, and staged-content recurrence protection.

## Exact Interface and Trust Contracts

The approved design specification section `Exact Runtime Contract` will be the normative schema and interface appendix. Implementation will follow its closed registry and overlay schemas, POSIX owner-assertion boundary, Windows fallback exit boundary, uv runtime, wrapper options, dry-run JSON, numeric exits, canonical-host SSH argv, and staged/commit enforcement modes.

The plan will additionally require:

- `WorkstationPathResolver.from_registry_bytes(raw_bytes)` with `from_registry_path` delegating to it, so digest and parse share one immutable read;
- same-machine duplicate identifiers accepted and cross-machine case-folded collisions rejected;
- generic wrappers requiring an explicit machine while `ssh-dev-secondary.sh` retains its fixed ID;
- inherited OpenSSH streams treated as local interactive output, not durable resolver logging;
- `git rev-parse --git-path hooks` plus normal-clone and linked-worktree installer tests; and
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

## Canonical Implementation Changed-Path Map

This table is the sole implementation changed-path authority; the navigation map
above authorizes no changes. The staged set will equal every `Modify`/`Create`
row plus a `Conditional` row only when its predicate is true. Any other path
will require plan amendment.

| Action | Path | Reason |
|---|---|---|
| Modify | `config/workstations/registry.yaml` | Replace unusable address fields for governed Linux machines with strict hostname-first policy and opaque fallback references; no live value will be guessed |
| Modify | `src/workspace_hub/workstations/resolver.py` | Add `from_registry_bytes` with `from_registry_path` delegation and cross-machine collision rejection without breaking workspace-path behavior |
| Create | `src/workspace_hub/workstations/connection.py` | Own strict policy, overlay, digest, route, redaction, and argv construction |
| Create | `scripts/operations/connection/connect-workstation.py` | Provide the single cross-platform CLI and shell-free OpenSSH launch boundary |
| Modify | `scripts/operations/connection/connect-workspace-tailscale.sh` | Become a thin shared-CLI wrapper with explicit machine/fallback/dry-run options |
| Modify | `scripts/operations/connection/connect-workspace-tailscale.ps1` | Match the Bash wrapper through safe argument arrays |
| Modify | `scripts/operations/connection/ssh-dev-secondary.sh` | Remove authentication-probe fallback and delegate to the shared CLI |
| Modify | `scripts/operations/connection/connect-workspace-linux.sh` | Remove target/user defaults and delegate to the shared CLI |
| Modify | `scripts/operations/connection/connect-workspace-windows.ps1` | Remove command strings and delegate to the shared CLI |
| Modify | `config/tabby/config.yaml` | Preserve unrelated preferences while removing tracked endpoint and operator defaults |
| Create | `config/workstations/connection-governed-paths.yaml` | Declare migrated, prohibited-doc, protocol-constant, and deferred connection surfaces for local and CI enforcement |
| Create | `scripts/enforcement/check-connection-helper-endpoints.py` | Inspect exact staged blobs for recurrence without whole-file exemptions |
| Modify | `scripts/enforcement/install-hooks.sh` | Invoke the workspace-scoped endpoint guard when present |
| Create | `tests/workstations/test_connection_resolver.py` | Drive strict resolver and overlay behavior first |
| Create | `tests/operations/test_connection_helpers_bash.py` | Drive Bash parity, argv safety, and non-executing dry-run |
| Create | `tests/operations/test_connection_helpers_ps1_contract.py` | Enforce static PowerShell safety and parity on Linux |
| Create | `tests/operations/test_connection_helpers_ps1_native.py` | Exercise native wrapper behavior when PowerShell exists |
| Create | `tests/enforcement/test_connection_helper_endpoints.py` | Prove staged-blob, NUL-safe, self-safe enforcement |
| Create | `.github/workflows/connection-helper-parity.yml` | Set up Python and uv; run Linux commit-blob enforcement and focused tests; run native PowerShell tests on Windows without allowing skip |
| Conditional | `docs/ops/remote-linux-access.md` | After rebasing onto merged PR #3553, modify only if `connect-workstation.py`, `machine-local fallback overlay`, or `--dry-run` is absent; otherwise preserve it and record the three-token preflight |
| Modify | `config/tabby/QUICK_REFERENCE.md` | Replace verified stale helper guidance with the shared CLI contract |
| Modify | `config/tabby/INTERNET_ACCESS_SUMMARY.md` | Remove verified address-coupled helper guidance and route to the runbook |
| Modify | `docs/modules/cli/WORKSPACE_CLI.md` | Replace the verified stale helper reference with the shared CLI invocation |
| Modify | `docs/modules/cli/SCRIPT_ORGANIZATION.md` | Record the shared CLI and wrapper responsibilities at the verified existing path |
| Modify | `docs/plans/README.md` | Index this plan |

`scripts/operations/connection/vnc-ace-linux-2.sh` will remain unchanged because
#3550 owns VNC disposition. Sync helpers will remain unchanged unless a failing
test proves that sanitizing Tabby configuration requires a narrow template path;
that outcome will stop implementation and return for plan amendment rather than
silently expanding the reviewed changed-path manifest.

## TDD Test List

| Test group | Required failing nodes before implementation | Green contract |
|---|---|---|
| Registry bytes and identity | path delegates to one bytes read; same-machine duplicate; cross-machine key/hostname/alias/SSH collisions | immutable validated snapshot and compatible path rewriting |
| Closed connection policy | unknown keys, wrong types, unsafe hostname, missing SSH, invalid reference/issue/age | exact schema from the approved design |
| POSIX overlay integrity | missing, symlink, wrong owner/type/mode, unsafe parent, repo-internal path | owner-controlled regular file or exit 5 |
| Fallback attestation | malformed/out-of-range, unverified, stale, policy-digest mismatch; canonical field mutations and unrelated edits | one synthetic verified fixture; stable per-machine digest; Windows exit 4 |
| SSH argv and host identity | missing/mismatched known host, injected user/target, implicit retry, caller options | canonical destination, fixed HostName/HostKeyAlias, strict checking, one launch |
| CLI and diagnostics | deterministic JSON, raw-value canaries, missing runtimes, child stderr, TTY, interrupt | redacted resolver output; inherited child streams; numeric exits |
| Bash wrappers | non-repo CWD, spaced checkout, missing uv, dry-run, exact argv/exits | thin delegation; fixed secondary ID; explicit generic machine |
| PowerShell wrappers | unsafe command strings, legacy methods, option/exit drift, native skip | argument arrays; hostname parity; native Windows proof |
| Tabby and live inventory | every target-bearing SSH surface classified; tracked endpoint/operator defaults | exact governed manifest; unrelated preferences preserved |
| Endpoint guard | added/modified/deleted/odd path, temporary index, TOCTOU, commit blobs, sentinel adjacency, self-artifacts | same-blob staged and head-ref verdicts without raw values |
| Hook and CI wiring | duplicate insertion, normal clone, linked worktree, installed positive control, Windows skip | git-path hook resolution and non-skipping Linux/Windows jobs |

Synthetic addresses and secret controls will be assembled at runtime. Protocol
network constants will use one cited same-line sentinel; no whole-file exemption
will exist. Exact RED/GREEN commands appear in the implementation sequence.

## Implementation Sequence

1. **Dependency and discovery gate:** the implementation branch will update from
   merged #3553 on `main`; the live helper manifest, issue labels,
   parallel sessions, and inherited baseline will be rechecked before editing.
2. **Slice A — registry bytes and policy:** tests for `from_registry_bytes`,
   path delegation, same-machine duplicates, cross-machine collisions, and the
   closed registry policy will fail first:
   `uv run pytest tests/workstations/test_machine_path_resolver.py tests/workstations/test_connection_resolver.py -k 'registry or identifier or policy' -q`.
   Only `resolver.py`, `connection.py`, and the synthetic tests will change before
   that command reaches green.
3. **Slice B — POSIX overlay and digest:** missing, malformed, symlink, owner,
   mode, parent, range, evidence, freshness, canonical policy mutation/stability,
   legacy-field, unrelated-edit, and digest mismatch nodes
   will fail first with
   `uv run pytest tests/workstations/test_connection_resolver.py -k 'overlay or fallback or digest' -q`.
   The minimum overlay loader will then reach green; Windows fallback will remain
   an explicit exit-4 boundary.
4. **Slice C — CLI and interactive launch:** dry-run JSON, numeric exits,
   canonical-host configuration, strict host-key behavior, inherited stderr,
   TTY, and interrupt nodes will fail first with
   `uv run pytest tests/workstations/test_connection_resolver.py -k 'cli or dry_run or ssh or interrupt' -q`.
   The CLI will then implement the minimum shell-free argv and launch behavior.
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
7. **Slice F — staged and commit enforcement:** temporary-index tests will fail
   first with
   `uv run pytest tests/enforcement/test_connection_helper_endpoints.py -q`.
   The manifest, stdlib checker, CI mode, and `install-hooks.sh` wiring through
   `git rev-parse --git-path hooks` will then reach green in both a normal clone
   and linked worktree fixture.
8. **Documentation and full regression:** the four stale helper documents and the
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
- [ ] The initial focused tests demonstrate RED failures for current drift before
  implementation files change.
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
  odd filenames, and TOCTOU cases without whole-file exemptions or self-blocking.
- [ ] `python scripts/enforcement/check-connection-helper-endpoints.py --staged`
  passes, and CI commit mode passes with
  `--base-ref origin/main --head-ref HEAD`.
- [ ] `install-hooks.sh` resolves hooks through `git rev-parse --git-path hooks`,
  remains idempotent, and is tested in normal and linked-worktree repositories.
- [ ] Focused tests pass:
  `uv run pytest tests/workstations/test_connection_resolver.py tests/operations/test_connection_helpers_bash.py tests/operations/test_connection_helpers_ps1_contract.py tests/operations/test_connection_helpers_ps1_native.py tests/enforcement/test_connection_helper_endpoints.py -q`.
- [ ] Existing resolver tests pass:
  `uv run pytest tests/workstations/test_machine_path_resolver.py -q`.
- [ ] The inherited workstation baseline has no new failing node beyond the
  recorded `ecosystem-reconcile` capability failure and expected machine-local
  skip.
- [ ] `bash -n` and `shellcheck` pass for every governed Bash wrapper.
- [ ] The Windows job distinguishes pre-pytest `INFRASTRUCTURE_FAILURE`, then
  passes native hostname-mode tests in required mode with no skip path; fallback
  confirms exit 4.
- [ ] The candidate index tree is frozen with `git write-tree`; changed paths
  equal the canonical map with evidence for the conditional row; working-tree
  files equal staged blobs; and the diff-only legal scan passes.
- [ ] The design's checksum-verified Gitleaks v8.30.1 procedure proves embedded
  defaults with runtime exit 23, then scans the exact archived candidate tree
  with finding exit 24. Every review edit restarts all scans.
- [ ] Code/artifact adversarial review is complete and all MAJOR findings are
  resolved or explicitly returned to the user.
- [ ] A summary comment is posted on #3549 before closeout.
- [ ] Closeout records candidate paths, the HEAD-bound module snapshot, measured
  changed-code coverage, and evidence checklist in a JSON input; calls
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
| Claude | MAJOR (r1) | Unmerged dependency and competing file maps; corrected before r2 |
| Codex | MAJOR (r1) | File map, Gitleaks pin, and completeness command gaps; corrected before r2 |
| Gemini | UNAVAILABLE (r1) | No noninteractive credentials on this runner; canonical stub retained |

**Overall result:** PENDING r2. Gemini unavailability degrades T3 to Claude+Codex
T2; a substantive verdict will never be reclassified as unavailable.

**Revisions:** merged #3553; made one changed-path authority; pinned the default-rules scan; completed the score/render contract; narrowed digest scope; separated Windows infrastructure failure from required-native test results.

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
- **Open questions:** none. The user approved the Option 2 architecture and the
  durable design artifact before this plan was drafted.

## Complexity: T3

**T3** — the issue will change a security-sensitive data boundary and executable
behavior across Python, Bash, PowerShell, YAML, Tabby configuration, Git staged
state, documentation, and Linux/Windows CI. Three independent adversarial review
lanes will be required at both plan and code/artifact stages.
