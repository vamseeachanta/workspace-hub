# Issue #2758 Plan — Agent/runtime folder architecture contract

- Issue: [#2758](https://github.com/vamseeachanta/workspace-hub/issues/2758) — Clarify agent/runtime folder architecture to reduce human and agent confusion
- Date: 2026-05-19
- Status: draft
- Complexity: T3
- Parallel-first classification: parallel-readonly for inventory/review; single-lane for plan/doc/script edits; no repo moves in this issue

## Resource Intelligence Summary

### Sources consulted

| Source | Finding | Plan impact |
|---|---|---|
| GitHub issue [#2758](https://github.com/vamseeachanta/workspace-hub/issues/2758) | The issue requires a durable architecture contract that distinguishes canonical source, generated runtime artifacts, local-only user-home state, caches, bridge outputs, symlinks, sibling tier-1 repo folders, and `workspace-hub` subfolders. | The deliverable will be an explicit authority map plus validation guardrails, not a folder migration. |
| `config/agents/SHARED_SOUL.md:1-6,85-90` | The current canonical identity contract says `SHARED_SOUL.md` and provider deltas produce committed runtime artifacts, and that local runtime state must be reconciled against repo-tracked canonical files. | The plan will preserve this canonical/source/runtime split and make it visible in a human-facing architecture doc. |
| `scripts/agents/build-soul-runtime.sh:1-61` | Runtime identity files are generated from repo-tracked canonical sources; outputs include provider `SOUL.runtime.md` files and Codex `AGENTS.runtime.md`. | The contract will mark these outputs as generated artifacts that agents must not edit directly. |
| `scripts/agents/install-soul-runtime.sh:1-87` | Local home-directory runtime files are symlinked/backed up per provider, with provider-specific loader differences for Hermes, Codex, and Gemini. | The contract will include per-provider/per-machine symlink/install shapes and cross-OS caveats. |
| `config/agents/hermes/config.yaml.template:35-46` | Hermes external skill directories are rendered from a machine-specific `__WS_HUB_PATH__`, and the template still names historical/nested repo paths alongside tier-1 repos. | The plan will require machine-specific path rendering to use an explicit registry and to distinguish sibling repos from `workspace-hub` subfolders. |
| `scripts/readiness/harness-config.yaml:22-76` | Existing readiness config has a `tier1_repos` list, workstation `ws_hub_path` entries, and Hermes health checks, but it does not yet encode per-machine repo placement or multi-user runtime overlays. | The plan will add a normalized machine/repo/user registry or extend an existing one instead of scattering placement facts across scripts. |
| `scripts/setup/emit-machine-status.sh:1-26` and `scripts/setup/aggregate-machine-status.sh:1-172` | The #2751 machine-status flow emits per-machine baselines and aggregates fleet status from repo-tracked baseline files. | The validation shape will reuse this per-machine baseline/aggregator pattern for folder-authority and repo-placement drift checks. |
| Related issues [#2754](https://github.com/vamseeachanta/workspace-hub/issues/2754), [#2755](https://github.com/vamseeachanta/workspace-hub/issues/2755), [#2756](https://github.com/vamseeachanta/workspace-hub/issues/2756), [#2757](https://github.com/vamseeachanta/workspace-hub/issues/2757) | Machine-specific repo-placement decisions are separate planning issues for ace-linux-1, ace-linux-2, licensed-win-1, and licensed-win-2. | This issue will provide the architecture vocabulary and registry schema those machine issues will consume, without deciding every machine's final repo set here. |
| Related issues [#2751](https://github.com/vamseeachanta/workspace-hub/issues/2751), [#2397](https://github.com/vamseeachanta/workspace-hub/issues/2397), [#2732](https://github.com/vamseeachanta/workspace-hub/issues/2732) | Cross-platform setup, canonical folder structure, and mount/folder taxonomy are adjacent workstreams that can conflict if this issue invents another authority source. | This plan will define integration points and avoid duplicating setup/mount governance already covered by those issues. |

### Gaps to close

- No single doc will currently answer “repo folder vs `workspace-hub` subfolder vs user-home runtime folder” across machines, repos, providers, and users.
- No machine/repo/user matrix will currently define whether a tier-1 repo should be absent, read-only, write-capable, license-bound, data-bound, or cache-only on a given machine.
- No validation check will currently fail when agents edit generated runtime files, when symlinks point to stale repo roots, or when Hermes skill external dirs mix sibling repos and internal subfolders incorrectly.
- No multi-user policy will currently separate shared repo-tracked state from per-user secrets, auth, caches, memories, and provider-local config overlays.

## Artifact Map

| Artifact | Path | Purpose |
|---|---|---|
| Plan | `docs/plans/2026-05-19-issue-2758-agent-runtime-folder-architecture-contract.md` | This approval artifact. |
| Architecture doc | `docs/architecture/agent-runtime-folder-authority.md` | Canonical human-facing source/runtime/local/cache/bridge authority map. |
| Registry schema | `config/workstations/repo-placement.schema.yaml` | Declarative schema for machine × repo × user placement decisions. |
| Registry data | `config/workstations/repo-placement.yaml` | Initial normalized matrix for known machines, tier-1 repos, and user scopes. |
| Validator | `scripts/validation/check-agent-runtime-authority.sh` | Fail-closed check for generated-file edits, broken symlinks, stale repo roots, duplicate skill roots, and unsafe local/runtime confusion. |
| Tests | `tests/validation/test_agent_runtime_authority.py` | Fixture-backed tests for Linux, Windows/Git Bash, multi-user, missing repo, broken symlink, and generated-file edit cases. |
| README/index update | `docs/plans/README.md` | Plan index row for #2758. |
| Review artifacts | `scripts/review/results/2026-05-19-plan-2758-*.md` | Plan-stage adversarial review results. |
| Follow-up issue bundle | GitHub issues linked from [#2758](https://github.com/vamseeachanta/workspace-hub/issues/2758) | Separate approval-gated tickets for any migration, setup changes, or repo-placement implementation. |

## Deliverable

After approval and implementation, workspace-hub will have a repo-tracked architecture contract, machine/repo/user placement registry, and validation check that make agent/runtime/repo folder authority explicit without moving existing files in this issue.

## Scope

### In scope

- Define folder classes: workspace root, sibling tier-1 repo, `workspace-hub` subfolder, provider canonical source, generated runtime artifact, local user-home runtime file, cache, bridge output, secret/auth store, mount/data root, report/output root.
- Define authority levels: canonical repo source, generated repo artifact, local runtime symlink, local-only secret/auth, cache/disposable, bridge output, external dependency, deprecated/legacy.
- Define machine compatibility: Linux, Windows/Git Bash, future macOS, SSH-reachable vs local-only, licensed vs non-licensed, control-plane vs worker.
- Define repo compatibility: absent, present-readonly, present-write-capable, data-bound, license-bound, cache-only, deprecated, external-submodule, forbidden.
- Define user compatibility: shared repo checkout, per-user home runtime, per-user provider auth, per-user memory, service account, least-privilege collaborator, guest/read-only user.
- Add validation that is read-only except for test fixtures and documented outputs.
- Link follow-up issues for machine-specific decisions and migration work.

### Out of scope

- Moving, renaming, deleting, or cloning tier-1 repositories.
- Changing provider auth, secrets, API keys, tokens, or user-local credentials.
- Replacing the existing #2751 cross-platform setup implementation.
- Deciding all final repo placements for [#2754](https://github.com/vamseeachanta/workspace-hub/issues/2754), [#2755](https://github.com/vamseeachanta/workspace-hub/issues/2755), [#2756](https://github.com/vamseeachanta/workspace-hub/issues/2756), or [#2757](https://github.com/vamseeachanta/workspace-hub/issues/2757). This issue will provide the framework those decisions will use.

## Proposed Architecture

### 1. Authority model

The architecture doc will define a small authority taxonomy and require every relevant path to be assigned exactly one primary class:

| Class | Definition | Examples | Agent rule |
|---|---|---|---|
| `canonical-repo-source` | Human-authored source-of-truth tracked in git. | `config/agents/SHARED_SOUL.md`, provider deltas, scripts, docs. | Agents may edit only inside approved issue scope. |
| `generated-repo-artifact` | Tracked output generated from canonical source. | `config/agents/*/SOUL.runtime.md`, `config/agents/codex/AGENTS.runtime.md`. | Agents must regenerate via script; direct edits fail validation. |
| `local-runtime-link` | Machine/user home path pointing at repo artifact. | `~/.hermes/SOUL.md`, `~/.codex/AGENTS.md`. | Agents may inspect; installer owns changes. |
| `local-secret-auth` | Per-user secret/auth state. | `~/.hermes/.env`, `~/.codex/auth.json`, GitHub token stores. | Never commit, print, or copy into repo. |
| `local-cache` | Disposable runtime cache/session state. | Provider caches, browser profiles, temp output. | Safe to clean only by explicit cleanup policy. |
| `bridge-output` | Repo-tracked or local synchronization output between systems. | memory bridge exports, machine baseline reports. | Update through bridge scripts; preserve provenance. |
| `sibling-tier1-repo` | Separate repo checkout adjacent to `workspace-hub`. | `/mnt/local-analysis/digitalmodel`, `/mnt/local-analysis/assetutilities`. | Treat as a separate git repository with its own gates. |
| `workspace-hub-subfolder` | Directory inside the `workspace-hub` repo. | `docs/`, `config/`, `.claude/skills/`. | Governed by workspace-hub issues and hooks. |
| `mount-or-data-root` | Data or shared storage root outside repo source. | `/mnt/ace`, Windows drive roots, external mounts. | Data-governance and secret rules apply; no accidental repo ingest. |

### 2. Placement matrix model

The registry will express machine × repo × user decisions as data, not comments in scripts:

```yaml
schema_version: 1
machines:
  ace-linux-1:
    os_family: linux
    roles: [control-plane, hermes-primary]
    workspace_roots:
      - /mnt/local-analysis
    users:
      vamsee:
        home: /home/vamsee
        provider_runtime: enabled
    repos:
      workspace-hub:
        desired_state: write-capable
        checkout_kind: repo-root
        canonical_path: /mnt/local-analysis/workspace-hub
      digitalmodel:
        desired_state: decision-pending
        issue: 2754
```

The schema will allow each repo placement to record:

- `desired_state`: `absent`, `present-readonly`, `write-capable`, `decision-pending`, `deprecated`, `forbidden`.
- `checkout_kind`: `sibling-tier1-repo`, `workspace-hub-subfolder`, `submodule`, `external-mount`, `cache-only`.
- `canonical_path`: machine-local absolute path or Windows path with explicit OS family.
- `owner_user`: user or service account expected to own writes.
- `allowed_users`: users allowed to run agents against the checkout.
- `write_policy`: `none`, `branch-only`, `main-serialized`, `worktree-required`.
- `data_access`: `none`, `readable-raw-data`, `llm-wiki-private`, `llm-wiki-public`, or issue-linked custom value.
- `license_access`: `none`, `orcaflex`, `orcawave`, `aqwa`, or other controlled capability.
- `source_issue`: machine placement issue or follow-up issue.
- `last_verified`: timestamp emitted by validation, not hand-authored in the plan.

### 3. Multi-user model

The architecture will treat shared repo paths and user-local runtime state as separate layers:

- Repo-tracked docs, config templates, scripts, and generated artifacts will be shared.
- Provider auth, gateway credentials, local model caches, browser sessions, SSH keys, and memory stores will remain per-user.
- Installer/validator scripts will resolve `$HOME` for the invoking user and will not assume `/home/vamsee` except in machine-specific registry entries.
- Multi-user failures will be explicit: wrong owner, repo writable by an unintended user, symlink into another user home, unreadable external skill dir, or shared cache holding credentials.

### 4. Cross-platform model

The validator and docs will cover:

- Linux absolute paths (`/mnt/local-analysis/...`, `/home/<user>/...`).
- Windows/Git Bash paths (`D:\workspace-hub`, `/d/workspace-hub`) without assuming POSIX symlink behavior.
- SSH-reachable machines and local-only machines.
- Case sensitivity differences and path normalization.
- Missing checked-out repos as valid when `desired_state: absent` or `decision-pending`.

## Pseudocode

### `load_registry(path)`

```text
read YAML registry
validate schema_version
for each machine:
    require os_family, workspace_roots, users, repos
    normalize paths according to os_family
    reject secrets or token-like values in registry
return normalized registry object
```

### `inspect_current_machine(registry, machine_id, user)`

```text
resolve machine entry by explicit flag or hostname aliases
resolve invoking user entry from HOME and username
for each configured repo:
    classify path as present, missing, git repo, subfolder, symlink, or mount
    collect git root and remote URL if present
for each provider runtime path:
    classify as symlink, plain file, missing, broken symlink, secret/auth, cache
return observed state without mutating filesystem
```

### `check_authority_rules(observed, registry)`

```text
for each generated repo artifact:
    verify generated header and source build script reference
    fail if direct edit is staged without source changes or regenerated outputs
for each local runtime link:
    verify target matches repo artifact for this machine/user
    warn if provider does not load that file but path exists
for each repo placement:
    compare desired_state to observed state
    fail if write-capable path is not a git repo or wrong remote
    fail if absent/forbidden path is present and untracked by exception
for each skill external dir:
    verify path belongs to expected sibling repo or workspace-hub subfolder class
return pass/warn/fail findings
```

### `emit_report(findings, output)`

```text
render machine summary table
render repo placement matrix
render provider runtime/symlink matrix
render multi-user risks
render follow-up issue suggestions for unresolved findings
write report only when explicitly requested by caller
exit non-zero on FAIL findings in enforcement mode
```

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | `docs/architecture/agent-runtime-folder-authority.md` | Human-facing architecture contract and authority map. |
| Create | `config/workstations/repo-placement.schema.yaml` | Machine/repo/user registry shape and allowed enum values. |
| Create | `config/workstations/repo-placement.yaml` | Initial known machine and tier-1 repo decision matrix with `decision-pending` for unresolved placements. |
| Create | `scripts/validation/check-agent-runtime-authority.sh` | Read-only validation entry point usable by humans, CI, and machine-status jobs. |
| Create | `tests/validation/test_agent_runtime_authority.py` | TDD coverage for registry parsing, path classification, symlink checks, generated artifact checks, and multi-user safety. |
| Update | `scripts/setup/aggregate-machine-status.sh` or companion status docs | Integrate folder-authority report only if the approved implementation can do so without destabilizing #2751. Otherwise create a follow-up issue. |
| Update | `docs/plans/README.md` | Add plan index row for #2758. |
| Create comments | GitHub issues #2754-#2757 | Link machine-specific repo-placement decisions back to the architecture contract after plan review. |

## TDD Test List

| Test | Verification | Input | Expected output |
|---|---|---|---|
| `test_registry_accepts_machine_repo_user_matrix` | Schema accepts valid multi-machine, multi-repo, multi-user registry. | Fixture with Linux, Windows, two users, and tier-1 repos. | Parser returns normalized registry. |
| `test_registry_rejects_secret_like_values` | Registry cannot become a secret store. | Fixture containing token-like key/value. | Validation fails with redacted diagnostic. |
| `test_path_classifier_distinguishes_sibling_repo_from_workspace_subfolder` | Prevents repo-folder vs subfolder confusion. | Fixture paths under `/mnt/local-analysis/digitalmodel` and `/mnt/local-analysis/workspace-hub/docs`. | Classifications are `sibling-tier1-repo` and `workspace-hub-subfolder`. |
| `test_generated_runtime_direct_edit_requires_source_change` | Direct edits to generated artifacts are blocked. | Git fixture with changed `SOUL.runtime.md` and unchanged sources. | Validator returns FAIL. |
| `test_generated_runtime_change_with_source_and_rebuild_passes` | Regenerated artifacts are permitted. | Git fixture with changed source and matching generated outputs. | Validator returns PASS. |
| `test_local_runtime_symlink_target_matches_machine_root` | Symlink drift is detected. | Fixture `~/.codex/AGENTS.md` pointing at stale workspace root. | Validator returns FAIL with stale target. |
| `test_windows_path_normalization_does_not_require_posix_symlink` | Windows compatibility is explicit. | Fixture with `D:\workspace-hub` and Git Bash-style path. | Validator normalizes without requiring symlink. |
| `test_decision_pending_repo_can_be_missing` | Placement planning does not force clones. | Registry marks `llm-wiki` as `decision-pending`; path missing. | Validator returns WARN or PASS per mode, not FAIL. |
| `test_forbidden_repo_presence_fails` | Policy can prevent unintended sensitive checkouts. | Registry marks repo `forbidden`; path exists. | Validator returns FAIL. |
| `test_multi_user_home_runtime_is_not_cross_linked` | User-local runtime state stays user-scoped. | Fixture symlink from one user home into another. | Validator returns FAIL. |
| `test_skill_external_dirs_are_classified` | Hermes skill roots do not mix unknown path classes. | Fixture config with known sibling repo, workspace-hub subfolder, and unknown dir. | Unknown dir produces FAIL or WARN. |
| `test_report_redacts_home_auth_and_token_paths` | Diagnostics do not leak secrets. | Fixture with auth path names and token-like text. | Report redacts sensitive values. |

## Acceptance Criteria

- [ ] `docs/architecture/agent-runtime-folder-authority.md` will define all folder classes and authority levels for provider runtime, repo source, sibling repos, local homes, caches, bridge outputs, mounts, and generated artifacts.
- [ ] The architecture doc will include a per-provider/per-machine table for Hermes, Claude, Codex, and Gemini across ace-linux-1, ace-linux-2, licensed-win-1, and licensed-win-2.
- [ ] The architecture doc will include a multi-user section that distinguishes shared repo state from per-user secrets/auth/caches/memory.
- [ ] `config/workstations/repo-placement.yaml` will represent known machines and candidate tier-1 repos without asserting unverified coverage as fact.
- [ ] The registry will link unresolved machine-specific decisions to [#2754](https://github.com/vamseeachanta/workspace-hub/issues/2754), [#2755](https://github.com/vamseeachanta/workspace-hub/issues/2755), [#2756](https://github.com/vamseeachanta/workspace-hub/issues/2756), and [#2757](https://github.com/vamseeachanta/workspace-hub/issues/2757).
- [ ] Validation will pass on missing repos that are intentionally `absent` or `decision-pending` and fail on forbidden repos, stale symlinks, generated artifact direct edits, and cross-user runtime links.
- [ ] Tests will be written before implementation and will cover Linux, Windows/Git Bash, multi-repo, multi-machine, and multi-user cases.
- [ ] The implementation will not move, rename, delete, clone, or sync repositories.
- [ ] Any migration or repo-placement action discovered during implementation will become a separate GitHub issue instead of being executed under #2758.
- [ ] Existing SOUL runtime build/install behavior will remain compatible unless a separate approved follow-up issue changes it.
- [ ] `scripts/legal/legal-sanity-scan.sh` will pass.
- [ ] Plan-stage adversarial review will complete before `status:plan-review` is applied.

## Issues That May Arise

| Risk / issue | Why it matters | Mitigation |
|---|---|---|
| Registry becomes another stale authority source | A new matrix can drift from setup scripts, harness config, and issue labels. | The validator will compare registry paths against live filesystem observations and existing machine baseline reports; docs will designate a single canonical registry and name any derived surfaces. |
| Plan accidentally claims coverage across machines not currently reachable | Per-machine coverage has historically been partial. | The registry will support `unknown`/`decision-pending`; validation will report observed coverage without claiming all machines were checked. |
| Multi-user state leaks secrets or auth paths | Provider home directories contain credentials and private memory. | Registry will store only path classes and non-secret metadata; validator will redact and reject token-like values. |
| Windows path and symlink behavior differs from Linux | Git Bash path normalization and symlink permissions can break checks. | Tests will include Windows-style fixtures and validation will not require POSIX symlink semantics on Windows. |
| Agents edit generated runtime files directly | Generated artifacts look like normal Markdown and are committed for review. | Generated headers plus validator checks will fail direct staged edits unless sources are updated and runtime build output is consistent. |
| Sibling repo vs `workspace-hub` subfolder remains visually ambiguous | `/mnt/local-analysis/digitalmodel` and `workspace-hub/digitalmodel` mean different things if both appear. | The authority doc will define visual vocabulary and the registry will require `checkout_kind` classification for every path. |
| Machine-specific repo placement work overlaps with #2754-#2757 | This issue could grow into four machine setup decisions. | #2758 will define the decision framework only; each machine issue will consume the framework and make final placement decisions. |
| #2751 setup work and this registry conflict | Cross-platform setup may already own machine bootstrap facts. | Implementation will either extend #2751-compatible config or open a follow-up; it will not fork a parallel setup system. |
| Runtime path checks break active providers | Strict validation can block working local sessions. | First implementation will support report-only mode and enforcement mode separately, and will preserve existing runtime symlinks. |
| External skill dirs include absent repos by design | Not every machine will host every tier-1 repo. | Missing external dirs will be allowed when the registry marks the repo absent/decision-pending; write-capable missing repos will fail. |
| Shared caches and bridge outputs are confused with source | Reports/memory exports may look authoritative. | Authority taxonomy will label bridge outputs and caches separately and include provenance/update commands. |
| Remote collaborators or future users lack same usernames/home paths | The design must support multiple users. | Registry will model user aliases and per-user runtime overlays without assuming `vamsee` except for current machine entries. |

## Adversarial Review Routing

- Complexity: T3 because the work crosses providers, machines, repos, operating systems, validation scripts, and governance docs.
- Required review: default 3-provider plan-stage review using `scripts/review/plan-review-fanout.sh docs/plans/2026-05-19-issue-2758-agent-runtime-folder-architecture-contract.md`.
- Review stance: reviewers must hunt for defects, especially stale authority sources, cross-user secret leakage, Windows path failures, plan/scope overreach into machine placement, and validator false positives that would block generated artifacts or approved setup work.

## Implementation Sequence After Approval

1. Write failing tests for registry parsing, path classification, generated artifact edit detection, symlink drift, Windows path normalization, missing/forbidden repos, multi-user home isolation, and redaction.
2. Add the registry schema and minimal initial registry with `decision-pending` entries for unresolved machine/repo decisions.
3. Implement the read-only validator to satisfy tests.
4. Draft the architecture doc using the authority taxonomy and registry examples.
5. Run targeted tests and legal/security scan.
6. Run the validator against the current machine in report-only mode and record any follow-up issues instead of mutating repo placement.
7. Update linked machine issues with comments pointing to the approved contract.
8. Run code/artifact adversarial review before closeout.

## Open Questions for User Approval

1. Should the initial registry include only the four current machines (`ace-linux-1`, `ace-linux-2`, `licensed-win-1`, `licensed-win-2`), or should it reserve placeholders for future machines/users now?
2. Should repo placement default to `decision-pending` for every candidate tier-1 repo on every machine, or should `workspace-hub` default to required/present everywhere?
3. Should validation start as report-only for one cycle before being allowed to fail CI/pre-commit?
4. Should the registry live under `config/workstations/` as proposed, or should it be folded into the existing `scripts/readiness/harness-config.yaml` to avoid another config root?

## Status / Gate

This draft will require adversarial plan review and user approval before any implementation. It must not be self-approved, and it must not trigger repo movement or machine setup actions by itself.
