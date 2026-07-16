# Plan for #3549: Registry-Driven Linux Connection Helpers with TDD

> **Status:** draft
> **Complexity:** T3
> **Date:** 2026-07-16
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/3549
> **Client:** N/A
> **Lane:** lane:claude
> **Review artifacts:** scripts/review/results/2026-07-16-plan-3549-claude.md | scripts/review/results/2026-07-16-plan-3549-codex.md | scripts/review/results/2026-07-16-plan-3549-gemini.md

---

## Resource Intelligence Summary

### Existing repo code

- `src/workspace_hub/workstations/resolver.py` contains the canonical
  `WorkstationPathResolver`, which loads the workstation registry and resolves
  keys, hostnames, aliases, and SSH identifiers. Its identifier map currently
  uses last-write-wins assignment and its generic field lookup returns an empty
  string for missing data, so the connection path will add strict ambiguity and
  missing-value handling without creating a second YAML parser.
- `scripts/lib/workstation-lib.sh` wraps the resolver through interpolated Python
  source and suppressed stderr. The connection implementation will not reuse
  this interface because environment-controlled strings must not become source
  code and connection errors must fail visibly.
- Five SSH helper scripts and `config/tabby/config.yaml` contain independently
  maintained target literals. Their values disagree, so the implementation will
  remove rather than reconcile them.
- `config/workstations/registry.yaml` contains seven machine records. The two
  Linux development records contain SSH and address fields but no provenance,
  verification, or freshness metadata. Existing address values will remain
  unusable and will not be promoted to verified state.
- `tests/workstations/test_machine_path_resolver.py` supplies the existing
  temporary-YAML resolver convention. Pytest subprocess tests under
  `tests/operations/` supply the Bash fake-executable pattern. PowerShell tests
  under `tests/readiness/` supply static Linux contracts and optional native
  execution when `pwsh` or `powershell` exists.
- `scripts/enforcement/check-no-conflict-markers.sh` supplies the staged-blob,
  NUL-safe, same-blob, narrow-sentinel enforcement precedent. The new endpoint
  check will follow that threat model and will not add whole-file exemptions.

### Standards

| Standard | Status | Source |
|---|---|---|
| External engineering calculation standards | Not applicable | #3549 changes operational connection tooling, not a calculation module |
| Repository security baseline | Active | `.claude/rules/security.md`, `SHARED_SOUL.md` hard gates |
| Canonical remote-access policy | Pending integration dependency | `docs/ops/remote-linux-access.md` on PR #3553 |

### LLM Wiki pages consulted

- No relevant wiki page applies. The durable authority will remain the
  workstation registry plus the canonical operational runbook; no client or
  engineering-domain knowledge will be added.

### Documents consulted

- [#3549](https://github.com/vamseeachanta/workspace-hub/issues/3549) fixes the
  helper-remediation scope, TDD requirement, and fail-closed acceptance criteria.
- [#3547](https://github.com/vamseeachanta/workspace-hub/issues/3547) establishes
  the parent rollout sequence.
- [#3548](https://github.com/vamseeachanta/workspace-hub/issues/3548) and
  [PR #3553](https://github.com/vamseeachanta/workspace-hub/pull/3553) establish
  registry → runbook → helper → machine-local state as the authority hierarchy.
- `docs/superpowers/specs/2026-07-15-3549-registry-connection-helpers-design.md`
  records the user-approved Option 2 architecture: public registry policy plus a
  machine-local verified fallback overlay.
- `docs/ops/remote-linux-access.md` on PR #3553 requires MagicDNS/hostname-first
  connections, conventional OpenSSH host-key verification, no silent public
  fallback, and no observed endpoint publication.
- [#3550](https://github.com/vamseeachanta/workspace-hub/issues/3550) owns VNC and
  secondary-machine rollout, so `vnc-ace-linux-2.sh` will remain excluded.
- The Drive index search for `remote ssh workstation helper tailscale` returned
  no relevant Drive files. `master_document_index` had coverage gap reason
  `unreachable`; no client paths or unrelated document results will enter this
  plan.
- `config/tabby/QUICK_REFERENCE.md`, `config/tabby/INTERNET_ACCESS_SUMMARY.md`,
  `docs/modules/cli/WORKSPACE_CLI.md`, and `scripts/operations/connection/SCRIPT_ORGANIZATION.md`
  contain stale helper references and will be updated only where the final CLI
  contract changes their current guidance.

### Gaps identified

- No strict connection-policy model or local-overlay loader exists.
- No shared command owns resolution, redacted dry-run, and shell-free OpenSSH
  launch across Bash and PowerShell.
- No connection-specific test rejects duplicate identifiers, malformed policy,
  stale attestation, silent fallback, unsafe hostnames, or raw-value diagnostics.
- No exact-path staged-blob check prevents endpoint and operator defaults from
  returning to governed helpers.
- No native Windows CI job exercises the PowerShell wrapper.
- The #3548 authority is not yet on `main`; implementation will not begin until
  PR #3553 lands.

### Evidence (embedded verification)

**Issue statuses** (verified 2026-07-16 via `gh issue view`):

- `#3547` — OPEN — secure remote Linux access architecture and staged rollout —
  `status:needs-plan`.
- `#3548` — CLOSED — canonical remote Linux access architecture and runbook —
  `status:done`, `status:completeness-verified`.
- `#3549` — OPEN — registry-driven Linux connection helpers with TDD —
  `status:needs-plan`, `priority:high`, `lane:claude`.
- `#3550` — OPEN — secondary-machine rollout and verification —
  `status:needs-plan`.
- `PR #3553` — OPEN, draft — mergeable state will be rechecked immediately
  before implementation.

**File and drift probe** (verified 2026-07-16; scalar values redacted by design):

```text
machines=7
casefold_identifier_collisions=0
dev-primary:ssh_present=True;tailscale_ip_present=True;verification_metadata_present=False
dev-secondary:ssh_present=True;tailscale_ip_present=True;verification_metadata_present=False
connect-workspace-tailscale.sh:exists=True;ipv4_literal_count=1
connect-workspace-tailscale.ps1:exists=True;ipv4_literal_count=1
ssh-dev-secondary.sh:exists=True;ipv4_literal_count=2
connect-workspace-linux.sh:exists=True;ipv4_literal_count=1
connect-workspace-windows.ps1:exists=True;ipv4_literal_count=1
config/tabby/config.yaml:exists=True;ipv4_literal_count=2
src/workspace_hub/workstations/connection.py:exists=False
scripts/operations/connection/connect-workstation.py:exists=False
tests/workstations/test_connection_resolver.py:exists=False
```

The probe will parse assignments and YAML and will emit only booleans and counts.
It will not print target or operator values.

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

---

## Artifact Map

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
| Plan review — Claude | `scripts/review/results/2026-07-16-plan-3549-claude.md` |
| Plan review — Codex | `scripts/review/results/2026-07-16-plan-3549-codex.md` |
| Plan review — Gemini | `scripts/review/results/2026-07-16-plan-3549-gemini.md` |

---

## Deliverable

A strict registry-policy and machine-local-overlay connection system will provide
hostname-first, explicit verified fallback through one shell-free Python command,
with thin Bash and PowerShell wrappers, redacted dry-run behavior, native Windows
verification, and staged-content recurrence protection.

---

## Pseudocode

```text
function load_registry_snapshot(path):
    raw_bytes = read path exactly once
    payload = safe YAML parse raw_bytes
    require mapping with supported schema
    build machine records through WorkstationPathResolver
    reject wrong types and case-folded identifier collisions
    return immutable records and SHA-256(raw_bytes)

function resolve_connection_policy(snapshot, identifier):
    machine = resolve exactly one key, hostname, alias, or SSH identifier
    require closed connection-policy object
    hostname = validate ASCII DNS name without option or shell syntax
    require fallback policy and opaque reference to have strict types
    return canonical machine key, hostname, and fallback policy

function load_verified_fallback(path, policy, registry_digest, now):
    raw_bytes = read path exactly once
    overlay = safe YAML parse raw_bytes with closed schema
    require machine key, opaque reference, and registry digest match policy
    address = parse with standard IP library
    require address belongs to cited Tailscale protocol networks
    require verified state, evidence reference, and unexpired timestamps
    return immutable address without logging it

function build_ssh_argv(policy, route, optional_user):
    argv = [ssh executable]
    if optional_user exists: validate and append as separate -l argument
    if route is hostname: append canonical hostname
    if route is fallback:
        append fixed HostKeyAlias option using canonical hostname
        append verified overlay address as one argument
    reject caller-supplied SSH options and insecure host-key overrides
    return argv

function run_connection(args):
    registry_snapshot = load_registry_snapshot(args.registry)
    policy = resolve_connection_policy(snapshot, args.machine)
    route = hostname unless args.fallback is explicitly true
    if fallback: route = load_verified_fallback(...)
    argv = build_ssh_argv(policy, route, args.user)
    if dry_run: print deterministic redacted JSON and return success
    return subprocess.run(argv, shell=false).returncode

function endpoint_guard(staged_manifest):
    enumerate added or modified paths with NUL delimiters
    select only the exact governed helper and Tabby paths
    read every selected staged blob once
    parse address and operator-target patterns without printing raw matches
    allow only narrow same-line forensic sentinels in approved test locations
    fail with path, line, and violation class
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Modify | `config/workstations/registry.yaml` | Replace unusable address fields for governed Linux machines with strict hostname-first policy and opaque fallback references; no live value will be guessed |
| Modify | `src/workspace_hub/workstations/resolver.py` | Add typed parsing support and global case-folded identifier collision rejection without breaking workspace-path behavior |
| Create | `src/workspace_hub/workstations/connection.py` | Own strict policy, overlay, digest, route, redaction, and argv construction |
| Create | `scripts/operations/connection/connect-workstation.py` | Provide the single cross-platform CLI and shell-free OpenSSH launch boundary |
| Modify | `scripts/operations/connection/connect-workspace-tailscale.sh` | Become a thin shared-CLI wrapper with explicit machine/fallback/dry-run options |
| Modify | `scripts/operations/connection/connect-workspace-tailscale.ps1` | Match the Bash wrapper through safe argument arrays |
| Modify | `scripts/operations/connection/ssh-dev-secondary.sh` | Remove authentication-probe fallback and delegate to the shared CLI |
| Modify | `scripts/operations/connection/connect-workspace-linux.sh` | Remove target/user defaults and delegate to the shared CLI |
| Modify | `scripts/operations/connection/connect-workspace-windows.ps1` | Remove command strings and delegate to the shared CLI |
| Modify | `config/tabby/config.yaml` | Preserve unrelated preferences while removing tracked endpoint and operator defaults |
| Create | `scripts/enforcement/check-connection-helper-endpoints.py` | Inspect exact staged blobs for recurrence without whole-file exemptions |
| Modify | `scripts/enforcement/install-hooks.sh` | Invoke the workspace-scoped endpoint guard when present |
| Create | `tests/workstations/test_connection_resolver.py` | Drive strict resolver and overlay behavior first |
| Create | `tests/operations/test_connection_helpers_bash.py` | Drive Bash parity, argv safety, and non-executing dry-run |
| Create | `tests/operations/test_connection_helpers_ps1_contract.py` | Enforce static PowerShell safety and parity on Linux |
| Create | `tests/operations/test_connection_helpers_ps1_native.py` | Exercise native wrapper behavior when PowerShell exists |
| Create | `tests/enforcement/test_connection_helper_endpoints.py` | Prove staged-blob, NUL-safe, self-safe enforcement |
| Create | `.github/workflows/connection-helper-parity.yml` | Run focused Python and native PowerShell tests on Linux and Windows |
| Modify | `docs/ops/remote-linux-access.md` | Document the hostname-first helper, explicit local fallback overlay, and redacted dry-run without endpoints |
| Modify | `config/tabby/QUICK_REFERENCE.md` | Replace stale helper guidance with the shared CLI contract |
| Modify | `config/tabby/INTERNET_ACCESS_SUMMARY.md` | Remove address-coupled helper guidance and route to the runbook |
| Modify | `docs/modules/cli/WORKSPACE_CLI.md` | Update helper invocation only if the current command surface is referenced |
| Modify | `scripts/operations/connection/SCRIPT_ORGANIZATION.md` | Record the shared CLI and wrapper responsibilities |
| Modify | `docs/plans/README.md` | Index this plan |

`scripts/operations/connection/vnc-ace-linux-2.sh` will remain unchanged because
#3550 owns VNC disposition. Sync helpers will remain unchanged unless a failing
test proves that sanitizing Tabby configuration requires a narrow template path.

---

## TDD Test List

| Test name | What it will verify | Expected result |
|---|---|---|
| `test_registry_rejects_casefolded_identifier_collision` | Key, hostname, alias, and SSH identifiers cannot collide | Typed ambiguity error without raw values |
| `test_connection_policy_rejects_unknown_or_wrong_type_fields` | Policy schema will be closed and typed | Schema error naming only the field path |
| `test_resolves_key_hostname_alias_and_ssh_identifier` | All canonical identifier forms will map to one machine | Same canonical key |
| `test_hostname_route_is_default` | MagicDNS/SSH hostname will be preferred | One hostname route, no overlay read |
| `test_missing_hostname_fails_before_launch` | Missing registry authority cannot fall through | Stable nonzero resolver exit |
| `test_hostname_injection_corpus_is_rejected` | Controls, whitespace, option markers, URL and shell syntax cannot become targets | No child process or marker-file side effect |
| `test_fallback_requires_explicit_flag` | A failed hostname SSH process cannot select another target | Exactly one SSH invocation |
| `test_fallback_overlay_missing_or_malformed_fails_closed` | Overlay absence and invalid YAML/types cannot launch | No child process |
| `test_fallback_rejects_unverified_stale_or_mismatched_attestation` | Verification, freshness, machine, reference, and digest are binding | Typed failure without raw values |
| `test_fallback_rejects_non_tailscale_address` | Address must belong to cited protocol networks | Typed range error |
| `test_verified_fallback_uses_host_key_alias` | Fallback will retain canonical host-key identity | Fixed safe argv and one invocation |
| `test_registry_and_overlay_are_each_read_once` | Validation and launch will share immutable snapshots | One open per selected file |
| `test_dry_run_is_deterministic_and_executes_nothing` | Dry-run will be read-only and redacted | Stable JSON; zero external calls |
| `test_errors_never_echo_canary_values_or_environment` | Diagnostics will not leak invalid inputs or environment | Only field path and error class |
| `test_optional_user_is_validated_and_passed_as_argv` | User selection cannot inject a target string | Separate `-l` argument or rejection |
| `test_bash_wrappers_delegate_without_parsing_or_eval` | Bash will contain no YAML/JSON parsing or command construction | Shared CLI receives exact argv |
| `test_bash_dry_run_invokes_no_clients` | Wrapper dry-run will remain non-executing | Fake clients record zero calls |
| `test_bash_propagates_resolver_and_ssh_exit_codes` | Failures will remain actionable | Stable exit mapping |
| `test_powerShell_contract_uses_argument_arrays` | PowerShell will avoid command strings and `Invoke-Expression` | Static contract passes |
| `test_powerShell_contract_matches_bash_options` | Supported machine/fallback/dry-run semantics will align | Option and exit-code parity |
| `test_powerShell_native_dry_run_and_launch` | Windows wrapper behavior will match the shared resolver | Native fake-client proof |
| `test_governed_manifest_covers_every_target_bearing_ssh_surface` | Coverage claims will equal the live filesystem | Every SSH surface classified |
| `test_tabby_config_contains_no_endpoint_or_operator_defaults` | Tracked terminal configuration will no longer publish identity | Zero governed matches |
| `test_endpoint_guard_reads_added_staged_blobs` | New files will not bypass the scanner | Positive control fails |
| `test_endpoint_guard_is_nul_safe_and_same_blob_consistent` | Odd filenames and working-tree/index races will not bypass | Staged content controls verdict |
| `test_endpoint_guard_sentinel_is_line_scoped` | Forensic fixtures cannot create a blanket exemption | Unsuffixed adjacent violation still fails |
| `test_endpoint_guard_does_not_block_its_own_artifacts` | Scanner, tests, plan, and reviews remain committable | Negative controls pass |
| `test_windows_workflow_runs_native_powerShell_suite` | Cross-platform parity cannot rely on static assertions alone | Workflow contract selects Windows runner |

Synthetic test addresses will be assembled at runtime from integer components so
plans, reviews, fixtures, and scanner source will not contain live-looking
endpoint strings. Protocol-network constants in implementation will carry a
narrow same-line sentinel and official Tailscale source citation; the sentinel
will not exempt any adjacent line or whole file.

---

## Implementation Sequence

1. **Dependency and discovery gate:** PR #3553 will land; the implementation
   branch will update from `main`; the live helper manifest, issue labels,
   parallel sessions, and inherited baseline will be rechecked before editing.
2. **RED — resolver and overlay:** strict-schema, ambiguity, hostname, fallback,
   redaction, digest, and single-read tests will be written and shown failing.
3. **GREEN — connection core:** the minimum typed parser/model and safe argv
   builder will be implemented until resolver tests pass.
4. **RED — wrappers and Tabby:** Bash, PowerShell, inventory, and no-default tests
   will be written and shown failing against current helpers.
5. **GREEN — wrappers and configuration:** the five SSH helpers and Tabby config
   will delegate to the shared CLI without endpoint or operator defaults.
6. **RED/GREEN — staged enforcement:** scanner threat-model tests will precede the
   staged-blob checker and hook wiring.
7. **Cross-platform proof:** the focused Linux and Windows workflow will prove
   Python, Bash/static PowerShell, and native PowerShell behavior.
8. **Documentation and regression:** the runbook and directly affected helper
   references will be updated without endpoint examples or duplicated policy.
9. **Artifact review and closeout:** adversarial code review, legal/security
   scans, exact staged-tree verification, issue summary, completeness gate, and
   cleanup audit will run before closeout.

---

## Acceptance Criteria

- [ ] PR #3553 is merged and the implementation branch starts from a descendant
  of the merged #3548 authority.
- [ ] The user explicitly applies `status:plan-approved`; the implementing agent
  does not self-apply it.
- [ ] The initial focused tests demonstrate RED failures for current drift before
  implementation files change.
- [ ] Registry connection policy is strict, hostname-first, and contains no
  usable observed fallback address.
- [ ] A fallback address is accepted only from an explicit, current, verified,
  digest-bound machine-local overlay.
- [ ] No SSH failure class triggers an automatic second destination.
- [ ] Host-key verification remains enabled and fallback uses the canonical
  host-key alias.
- [ ] All five SSH wrappers delegate through one shell-free Python command.
- [ ] `config/tabby/config.yaml` contains no endpoint or operator defaults while
  unrelated terminal preferences remain intact.
- [ ] Dry-run is deterministic, redacted, and invokes no external process.
- [ ] Errors contain field paths and stable classes but no raw rejected values,
  endpoints, identities, environment dumps, or overlay contents.
- [ ] Exact staged-blob enforcement covers the governed manifest, added files,
  odd filenames, and TOCTOU cases without whole-file exemptions or self-blocking.
- [ ] Focused tests pass:
  `uv run pytest tests/workstations/test_connection_resolver.py tests/operations/test_connection_helpers_bash.py tests/operations/test_connection_helpers_ps1_contract.py tests/operations/test_connection_helpers_ps1_native.py tests/enforcement/test_connection_helper_endpoints.py -q`.
- [ ] Existing resolver tests pass:
  `uv run pytest tests/workstations/test_machine_path_resolver.py -q`.
- [ ] The inherited workstation baseline has no new failing node beyond the
  recorded `ecosystem-reconcile` capability failure and expected machine-local
  skip.
- [ ] `bash -n` and `shellcheck` pass for every governed Bash wrapper.
- [ ] The Windows CI job passes native PowerShell wrapper tests.
- [ ] `scripts/legal/legal-sanity-scan.sh --diff-only`, the applicable secret
  scan, and the staged endpoint guard pass against the exact proposed tree.
- [ ] Code/artifact adversarial review is complete and all MAJOR findings are
  resolved or explicitly returned to the user.
- [ ] A summary comment is posted on #3549 before closeout.
- [ ] Completeness verification and the pre-completion cleanup audit report no
  unexpected residue.

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | PENDING | Defect-hunting review will inspect architecture, scope, and gate correctness |
| Codex | PENDING | Defect-hunting review will inspect security, staged-state, and TDD completeness |
| Gemini | PENDING | Defect-hunting review will inspect cross-platform behavior and self-blocking enforcement |

**Overall result:** PENDING

Revisions made based on review:

- Pending.

---

## Risks and Open Questions

- **Risk — dependency not landed:** PR #3553 is still draft. Implementation will
  stop until its reviewed authority is present on `main`.
- **Risk — old endpoints remain in Git history:** current-tree cleanup will not
  erase historical commits. No history rewrite will occur without separate user
  authorization.
- **Risk — registry strictness affects path consumers:** collision validation
  will be added with regression tests so workspace-path rewriting continues to
  accept all currently valid identifiers.
- **Risk — global registry digest invalidates local fallback after unrelated
  edits:** this conservative behavior will fail closed and require re-attestation;
  the plan will prefer safety over partial-field digest complexity.
- **Risk — local overlay permissions differ by OS:** documentation and tests will
  enforce POSIX mode expectations where available and will validate the Windows
  ACL guidance through review and native workflow behavior.
- **Risk — scanner false positives or self-blocking:** the checker will parse only
  exact governed paths and will use runtime-constructed test values plus narrow
  line sentinels.
- **Open questions:** none. The user approved the Option 2 architecture and the
  durable design artifact before this plan was drafted.

---

## Complexity: T3

**T3** — the issue will change a security-sensitive data boundary and executable
behavior across Python, Bash, PowerShell, YAML, Tabby configuration, Git staged
state, documentation, and Linux/Windows CI. Three independent adversarial review
lanes will be required at both plan and code/artifact stages.
