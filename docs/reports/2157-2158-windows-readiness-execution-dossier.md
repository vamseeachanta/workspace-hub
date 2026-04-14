# Windows Readiness Execution Dossier for #2157 and #2158

Date: 2026-04-14
Repo: `vamseeachanta/workspace-hub`
Worktree: `/mnt/local-analysis/worktrees/workspace-hub-issue-2157-2158`
Issues:
- `#2157` feat(operations): implement native PowerShell probe collector for Windows readiness bundles
- `#2158` feat(operations): add Git Bash launcher and path-normalization bridge for Windows evidence writer

## Live gate status

These issues are not execution-approved in the current live state. This dossier is planning-only and is intended to make later execution bounded, testable, and non-overlapping.

## Resource intelligence used

- GitHub issue `#2157`: collector-only Windows probe scope, deliverables, and parent issue links.
- GitHub issue `#2158`: launcher/path-bridge scope, dry-run expectations, and writer dependency.
- [docs/modules/ai/readiness-evidence-bundle.schema.yaml](/mnt/local-analysis/worktrees/workspace-hub-issue-2157-2158/docs/modules/ai/readiness-evidence-bundle.schema.yaml): existing cross-platform bundle contract from `#2151`.
- [scripts/analysis/readiness_bundle_schema.py](/mnt/local-analysis/worktrees/workspace-hub-issue-2157-2158/scripts/analysis/readiness_bundle_schema.py): current schema validator entrypoint.
- [tests/analysis/test_readiness_bundle_schema.py](/mnt/local-analysis/worktrees/workspace-hub-issue-2157-2158/tests/analysis/test_readiness_bundle_schema.py): existing Linux/Windows fixture coverage and normalized enum assertions.
- [config/workstations/registry.yaml](/mnt/local-analysis/worktrees/workspace-hub-issue-2157-2158/config/workstations/registry.yaml): canonical machine identity and Windows workspace roots.
- [src/workspace_hub/workstations/resolver.py](/mnt/local-analysis/worktrees/workspace-hub-issue-2157-2158/src/workspace_hub/workstations/resolver.py): existing shared workspace-path normalization logic.
- [tests/workstations/test_machine_path_resolver.py](/mnt/local-analysis/worktrees/workspace-hub-issue-2157-2158/tests/workstations/test_machine_path_resolver.py): existing Windows/Linux path-rewrite contract.
- [scripts/windows/setup-scheduler-tasks.ps1](/mnt/local-analysis/worktrees/workspace-hub-issue-2157-2158/scripts/windows/setup-scheduler-tasks.ps1): current scheduler integration surface using Git Bash task actions.
- [scripts/readiness/nightly-readiness.sh](/mnt/local-analysis/worktrees/workspace-hub-issue-2157-2158/scripts/readiness/nightly-readiness.sh): current Linux-oriented readiness writer surface that downstream Windows work must eventually feed through `#2150`.
- [docs/plans/2026-04-10-single-terminal-claude-agent-team-prompts-2150-2159.md](/mnt/local-analysis/worktrees/workspace-hub-issue-2157-2158/docs/plans/2026-04-10-single-terminal-claude-agent-team-prompts-2150-2159.md): prior bounded ownership guidance for `#2157` and `#2158`.
- [docs/plans/2026-04-10-top3-issue-assessment-dossiers.md](/mnt/local-analysis/worktrees/workspace-hub-issue-2157-2158/docs/plans/2026-04-10-top3-issue-assessment-dossiers.md): earlier sequencing recommendation keeping `#2150`, `#2157`, and `#2158` behind schema/fixture/resolver foundations.

## Current-state summary

- The schema and validator work expected from `#2151` is already present in repo state.
- The shared machine/path resolver expected from `#2155` is also present in repo state.
- There is no native PowerShell readiness probe collector under `scripts/windows/`.
- There is no dedicated Git Bash launcher/path-bridge for the Windows readiness writer under `scripts/windows/`.
- Current Windows scheduled tasks call Git Bash directly and point `NightlyReadiness` at [scripts/readiness/nightly-readiness.sh](/mnt/local-analysis/worktrees/workspace-hub-issue-2157-2158/scripts/readiness/nightly-readiness.sh), so `#2158` must not silently widen into scheduler rewiring.
- The repo’s current test tree differs from the older prompt pack: `tests/reporting/` does not exist. Future execution should target `tests/analysis/`, `tests/workstations/`, and `tests/fixtures/readiness/`.

## Shared vs Separate Concerns

### Shared foundations already available

- Bundle contract and vocabulary: [docs/modules/ai/readiness-evidence-bundle.schema.yaml](/mnt/local-analysis/worktrees/workspace-hub-issue-2157-2158/docs/modules/ai/readiness-evidence-bundle.schema.yaml)
- Bundle validator: [scripts/analysis/readiness_bundle_schema.py](/mnt/local-analysis/worktrees/workspace-hub-issue-2157-2158/scripts/analysis/readiness_bundle_schema.py)
- Windows machine identity and workspace roots: [config/workstations/registry.yaml](/mnt/local-analysis/worktrees/workspace-hub-issue-2157-2158/config/workstations/registry.yaml)
- Shared workspace path rewriting: [src/workspace_hub/workstations/resolver.py](/mnt/local-analysis/worktrees/workspace-hub-issue-2157-2158/src/workspace_hub/workstations/resolver.py)

### Shared concerns that should remain read-only for these issues

- Scheduler registration surface: [scripts/windows/setup-scheduler-tasks.ps1](/mnt/local-analysis/worktrees/workspace-hub-issue-2157-2158/scripts/windows/setup-scheduler-tasks.ps1)
- Existing nightly readiness writer/orchestrator: [scripts/readiness/nightly-readiness.sh](/mnt/local-analysis/worktrees/workspace-hub-issue-2157-2158/scripts/readiness/nightly-readiness.sh)
- Canonical Windows bundle fixture: [tests/fixtures/readiness/windows-valid.yaml](/mnt/local-analysis/worktrees/workspace-hub-issue-2157-2158/tests/fixtures/readiness/windows-valid.yaml)

### Separate issue slices

- `#2157` should stay collector-only:
  - emit normalized probe JSON
  - no bundle writing
  - no scheduler changes
  - no repo-wide path-refactor work
- `#2158` should stay launcher/path-bridge-only:
  - render and execute the writer command line safely
  - bridge native and POSIX workspace/drop paths
  - support dry-run/debug output
  - no scheduler rewiring and no PowerShell collector logic

## Likely implementation surfaces

### Issue #2157

Purpose: native Windows probe collection with a stable intermediate JSON contract that `#2150` can consume.

Bounded create surfaces:
- `scripts/windows/windows-readiness-probe-collector.ps1`
- `tests/analysis/test_windows_readiness_probe_collector.py`
- `tests/fixtures/readiness/windows-probe-collector-healthy.json`
- `tests/fixtures/readiness/windows-probe-collector-degraded.json`
- `tests/fixtures/readiness/windows-probe-collector-partial-permission.json`

Read-only dependency surfaces:
- `config/workstations/registry.yaml`
- `docs/modules/ai/readiness-evidence-bundle.schema.yaml`
- `tests/fixtures/readiness/windows-valid.yaml`

Contract notes:
- Output should be probe JSON, not the final readiness bundle YAML.
- Probe fields should map cleanly into existing bundle sections:
  - machine identity
  - workspace-root evidence
  - access-mode evidence
  - ai-cli evidence
  - licensed-tool raw observations / source metadata
- Licensed-tool probing should remain capability detection, not schema-authoritative verdict logic. Final pass/warn/fail mapping belongs in the writer.

### Issue #2158

Purpose: reliable Windows invocation and path normalization for the future writer entrypoint from `#2150`.

Bounded create surfaces:
- `scripts/windows/windows-readiness-launcher.ps1`
- `tests/workstations/test_windows_readiness_launcher.py`
- `tests/fixtures/readiness/windows-launcher-path-cases.yaml`

Likely modify surfaces only if execution requires them:
- `docs/modules/ai/WEEKLY_ECOSYSTEM_EXECUTION_AND_INTELLIGENCE_REVIEW.md`

Read-only dependency surfaces:
- `src/workspace_hub/workstations/resolver.py`
- `tests/workstations/test_machine_path_resolver.py`
- `scripts/windows/setup-scheduler-tasks.ps1`
- `config/workstations/registry.yaml`

Contract notes:
- The launcher should not own the writer’s business logic.
- The launcher should treat the writer entrypoint as an input dependency; if `#2150` is still absent, `#2158` can only land a dry-run/skeleton/test contract.
- Reuse the existing resolver as a read-only normalization authority where possible; do not expand `#2158` into a repo-wide resolver rewrite.

## Exact path contracts for future implementation

### Shared contract

- Allowed dependency reads:
  - `config/workstations/registry.yaml`
  - `docs/modules/ai/readiness-evidence-bundle.schema.yaml`
  - `scripts/analysis/readiness_bundle_schema.py`
  - `src/workspace_hub/workstations/resolver.py`
  - `tests/analysis/test_readiness_bundle_schema.py`
  - `tests/workstations/test_machine_path_resolver.py`
  - `scripts/windows/setup-scheduler-tasks.ps1`
  - `scripts/readiness/nightly-readiness.sh`
- Not owned by either issue:
  - `scripts/readiness/**`
  - `config/workstations/**`
  - broad `src/workspace_hub/**` refactors
  - scheduler registration changes

### Issue #2157 owned path contract

- Create only:
  - `scripts/windows/windows-readiness-probe-collector.ps1`
  - `tests/analysis/test_windows_readiness_probe_collector.py`
  - `tests/fixtures/readiness/windows-probe-collector-healthy.json`
  - `tests/fixtures/readiness/windows-probe-collector-degraded.json`
  - `tests/fixtures/readiness/windows-probe-collector-partial-permission.json`
- Do not modify:
  - `scripts/readiness/nightly-readiness.sh`
  - `scripts/windows/setup-scheduler-tasks.ps1`
  - `src/workspace_hub/workstations/resolver.py`

### Issue #2158 owned path contract

- Create only:
  - `scripts/windows/windows-readiness-launcher.ps1`
  - `tests/workstations/test_windows_readiness_launcher.py`
  - `tests/fixtures/readiness/windows-launcher-path-cases.yaml`
- Optional documentation update:
  - `docs/modules/ai/WEEKLY_ECOSYSTEM_EXECUTION_AND_INTELLIGENCE_REVIEW.md`
- Do not modify:
  - `scripts/readiness/nightly-readiness.sh`
  - `scripts/windows/setup-scheduler-tasks.ps1`
  - `src/workspace_hub/workstations/resolver.py` unless a separate approval explicitly widens scope

## Likely tests needed

### Issue #2157

- Fixture-backed contract test for healthy probe output.
- Fixture-backed contract test for degraded probe output when one or more AI CLIs or licensed tools are absent.
- Fixture-backed contract test for partial-permission output where some probes are missing but the collector still emits normalized keys.
- Field-presence and quoting test for paths with spaces in `D:\workspace-hub`.
- Live PowerShell smoke only on Windows-capable execution hosts:
  - collector exits zero
  - writes JSON
  - preserves required top-level keys

### Issue #2158

- Dry-run launcher rendering test for default Git installation path.
- Dry-run launcher rendering test for non-default Git path.
- Path bridge tests covering:
  - `D:\workspace-hub`
  - `/d/workspace-hub`
  - `/D/workspace-hub`
  - paths with spaces
  - missing `cygpath`
- Missing-writer dependency test proving the launcher fails loudly when the `#2150` writer entrypoint is absent.
- Manual/runbook snippet assertion if a docs update is included.

### Shared regression anchors to keep running

- `uv run pytest tests/analysis/test_readiness_bundle_schema.py -q`
- `uv run pytest tests/workstations/test_machine_path_resolver.py -q`

## Sequencing recommendation

Recommended execution order for the actual implementation wave:

1. Confirm `#2150` target writer contract and exact entrypoint path.
2. Execute `#2157` first as a collector-only slice.
3. Execute the remaining `#2150` writer composition work that consumes the collector output.
4. Execute `#2158` after the writer entrypoint exists, so the launcher can target something real.
5. Defer scheduler-registration changes to follow-on issue `#2163` if launcher wiring proves necessary.

If only one of these two issues can move first, `#2157` is the lower-risk starting point because it has fewer cross-surface dependencies.

## Blockers and unknowns

- Hard blocker: neither `#2157` nor `#2158` is execution-approved in the live issue state.
- Functional blocker for `#2158`: the final writer entrypoint from `#2150` is not yet present in the repo.
- Design unknown for `#2157`: whether licensed-tool probe output should include per-tool detail or only the minimal facts needed for the writer’s summary mapping.
- Platform unknown for `#2158`: whether the team wants the launcher to prefer `bash.exe`, `git-bash.exe`, or an explicit configured path from the workstation environment.
- Scope risk: the old prompt pack references `tests/reporting/`, but the current repo tree does not have that directory. Future execution should use `tests/analysis/` and `tests/workstations/` instead.
- Integration risk: `scripts/windows/setup-scheduler-tasks.ps1` currently launches Git Bash directly. Any attempt to change that inside `#2158` will widen scope into scheduler work and should be rejected unless separately approved.

## Execution-readiness verdict

- `#2157`: ready for a bounded collector-only implementation once plan approval exists.
- `#2158`: partially ready; path contract is clear, but full completion still depends on the writer entrypoint from `#2150`.

## Concise issue comment drafts

### Comment for #2157

Planning-only readiness pass completed. Current repo state already provides the shared schema, validator, registry, and workspace-path resolver, so `#2157` can stay narrowly scoped to a new PowerShell probe collector plus fixture-backed tests. Recommended owned surfaces are `scripts/windows/windows-readiness-probe-collector.ps1`, `tests/analysis/test_windows_readiness_probe_collector.py`, and collector fixtures under `tests/fixtures/readiness/`. Main blockers are the live plan gate and the need to keep licensed-tool detail as probe output only, with final bundle verdict mapping left to `#2150`.

### Comment for #2158

Planning-only readiness pass completed. `#2158` should stay a launcher/path-bridge slice and reuse the existing shared resolver and registry as read-only dependencies rather than widening into scheduler or repo-wide path-refactor work. Recommended owned surfaces are `scripts/windows/windows-readiness-launcher.ps1`, `tests/workstations/test_windows_readiness_launcher.py`, and a launcher-path fixture file under `tests/fixtures/readiness/`, with an optional runbook update in `docs/modules/ai/WEEKLY_ECOSYSTEM_EXECUTION_AND_INTELLIGENCE_REVIEW.md`. Main blockers are the live plan gate and the missing final writer entrypoint from `#2150`, which means full launcher completion should wait until that target exists.
