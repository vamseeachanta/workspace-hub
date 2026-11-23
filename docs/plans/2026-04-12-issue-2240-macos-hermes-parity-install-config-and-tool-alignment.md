# Plan for #2240: macOS Hermes parity — install, config, and tool alignment

> Status: adversarial-reviewed
> Complexity: T2
> Date: 2026-04-12
> Issue: https://github.com/vamseeachanta/workspace-hub/issues/2240
> Review artifacts: scripts/review/results/2026-04-12-plan-2240-claude.md | scripts/review/results/2026-04-12-plan-2240-codex.md | scripts/review/results/2026-04-12-plan-2240-gemini.md

---

## Resource Intelligence Summary

### Existing repo code
- Found: `config/agents/hermes/config.yaml.template` and `config/agents/hermes/SOUL.md` — repo-managed Hermes baseline artifacts already exist and define the shared config surface macOS should converge toward.
- Found: `scripts/_core/sync-agent-configs.sh` contains `resolve_ws_hub_path()` and `sync_hermes_yaml_config()` — Hermes config sync is already path-aware, but only for workstations declared in readiness config.
- Found: `scripts/readiness/harness-config.yaml` currently defines only `dev-primary`, `dev-secondary`, and `licensed-win-1` workstations for Hermes-related readiness/state handling; no macOS workstation is present.
- Found: `config/workstations/registry.yaml` lists Linux and Windows machines only; `macbook-portable` is absent from the canonical workstation registry.
- Gap: there is no repo-tracked macOS workstation entry, no macOS readiness report target, and no documented automation path for macOS Hermes parity checks.

### Standards
| Standard | Status | Source |
|---|---|---|
| Control-plane adapter model | done | `docs/standards/CONTROL_PLANE_CONTRACT.md` |
| Hard-stop policy for non-engineering harness work | not applicable to implementation gate, but planning still mandatory | `docs/standards/HARD-STOP-POLICY.md` |

### LLM Wiki pages consulted
- No relevant wiki pages found; this is machine/readiness configuration work and does not depend on domain wiki content.

### Documents consulted
- `docs/ops/hermes-weekly-cross-machine-parity-checklist.md` — explicitly places `macbook-portable` in scope and records current expected parity checks plus macOS-specific drift notes (launchd/manual scheduling, path conventions, Linux-only tooling exclusions).
- `scripts/readiness/harness-config.yaml` — current workstation/readiness source used by nightly readiness and Hermes managed-key checks; reveals macOS is not yet represented.
- `config/workstations/registry.yaml` — machine registry used by cron/tooling discovery; reveals Linux and Windows coverage only.
- `config/agents/hermes/config.yaml.template` — shared Hermes baseline whose managed keys must be portable to macOS.
- `config/agents/claude/memory-snapshots/network_machines.md` — records concrete macOS evidence: hostname `Vamsees-MacBook-Air.local`, user `krishna`, and workspace path `~/workspace-hub/`.
- `scripts/readiness/nightly-readiness.sh` — downstream readiness runner uses hostname-derived report naming plus GNU/BSD-sensitive shell commands (`hostname -s`, `sed -i`, `stat -c`), so macOS parity cannot be planned as pure YAML-only scaffolding.
- `scripts/operations/workstation-status.sh` — reads `config/workstations/registry.yaml`, resolves host identity via registry hostnames/aliases, and treats empty SSH targets as `no-ssh`; relevant consumer that may remain unchanged but must be dispositioned.
- `scripts/maintenance/ai-tools-status.sh` — enumerates `workstations:` from `scripts/readiness/harness-config.yaml`, so any macOS harness-config entry will change its machine set and drift snapshot behavior.
- `scripts/monitoring/cron-health-check.sh` — resolves hostnames/aliases from `config/workstations/registry.yaml`; relevant consumer for alias-safe parsing and host classification.
- `scripts/readiness/compare-harness-state.sh` — currently hardcodes `ace-linux-2` + `licensed-win-1`, so it must be explicitly declared unchanged for this issue or split to follow-up work.
- Related issue #1583 — baseline-definition issue for Hermes settings across machines.
- Related issue #2089 — weekly review/gov issue that already expects Linux + macOS parity evidence.
- Related issue #2094 — multi-machine readiness matrix work that should be reused rather than duplicated.

### Gaps identified
- No canonical `macbook-portable` workstation entry exists in repo control-plane files.
- No readiness report path or managed path-substitution config exists for macOS.
- No automated parity-check surface currently proves macOS can resolve `external_dirs`, skills, and knowledge paths.
- No regression tests currently guard macOS workstation config additions.

<!-- Verification: distinct sources >= 3. Current count: 7 -->

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-04-12-issue-2240-macos-hermes-parity-install-config-and-tool-alignment.md` |
| Workstation registry | `config/workstations/registry.yaml` |
| Readiness config | `scripts/readiness/harness-config.yaml` |
| Hermes sync logic | `scripts/_core/sync-agent-configs.sh` |
| Weekly checklist updates | `docs/ops/hermes-weekly-cross-machine-parity-checklist.md` |
| Tests | `tests/work-queue/test-harness-readiness.sh` |
| Plan review — Claude | `scripts/review/results/2026-04-12-plan-2240-claude.md` |
| Plan review — Codex | `scripts/review/results/2026-04-12-plan-2240-codex.md` |
| Plan review — Gemini | `scripts/review/results/2026-04-12-plan-2240-gemini.md` |

---

## Deliverable

A repo-tracked macOS Hermes parity contract that adds `macbook-portable` to the workstation/readiness model using canonical path `/Users/krishna/workspace-hub` and hostname alias `Vamsees-MacBook-Air.local`, verifies the shared Hermes baseline can be resolved on macOS, and documents/tests the acceptable platform-specific drift.

### Explicit consumer disposition for this issue
- `scripts/_core/sync-agent-configs.sh`: in scope — must resolve canonical macOS path and hostname alias deterministically
- `scripts/readiness/nightly-readiness.sh`: in scope — only the code paths needed for macOS report naming/path compatibility and BSD-safe baseline updates
- `scripts/maintenance/ai-tools-status.sh`: in scope — must tolerate/reflect the added macOS `workstations:` entry in harness-config
- `scripts/operations/workstation-status.sh`: verify unchanged behavior via tests; no code change unless registry parsing fails with macOS entry
- `scripts/monitoring/cron-health-check.sh`: verify unchanged behavior via tests; no code change unless alias resolution breaks
- `scripts/readiness/compare-harness-state.sh`: explicitly out of scope for this issue; leave unchanged and capture any needed extension as follow-up work

---

## Pseudocode

```text
add macbook_portable_to_registry():
    declare canonical machine key, hostname alias Vamsees-MacBook-Air.local, workspace root /Users/krishna/workspace-hub, role, and capabilities

add macbook_portable_to_harness_config():
    declare ws_hub_path /Users/krishna/workspace-hub, report_path, optional ssh target, and Hermes managed-key checks

disposition_consumers():
    keep workstation-status.sh and cron-health-check.sh unchanged if alias-aware tests pass
    update ai-tools-status.sh if macOS harness-config entry changes machine enumeration semantics
    leave compare-harness-state.sh out of scope and document follow-up if macOS report comparison is later required

audit_sync_and_readiness_compatibility():
    verify resolve_ws_hub_path maps macOS hostname/alias to /Users/krishna/workspace-hub
    restrict nightly-readiness.sh edits to macOS report naming, alias handling, and BSD-safe commands used in those paths

add regression tests():
    assert macbook-portable entries parse correctly, aliases resolve, ai-tools-status tolerates the new harness-config entry, and existing Linux/Windows flows remain unchanged
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Modify | `config/workstations/registry.yaml` | add canonical `macbook-portable` machine identity/capabilities, hostname alias, and canonical workspace path |
| Modify | `scripts/readiness/harness-config.yaml` | add macOS workstation path/report metadata for Hermes readiness flows |
| Modify | `scripts/_core/sync-agent-configs.sh` | make macOS hostname/path resolution explicit and testable |
| Modify | `scripts/readiness/nightly-readiness.sh` | limit changes to macOS report naming, alias handling, and BSD-safe shell behavior in touched code paths |
| Modify | `scripts/maintenance/ai-tools-status.sh` | ensure harness-config enumeration tolerates the new macOS workstation entry and expected reachability semantics |
| Modify | `docs/ops/hermes-weekly-cross-machine-parity-checklist.md` | refine macOS evidence steps based on implementation details |
| Modify | `tests/work-queue/test-harness-readiness.sh` | add regression coverage for the new workstation entry / readiness config parsing |
| Create or Modify | `scripts/monitoring/tests/test_cron_health_check.sh` | verify registry alias parsing and unchanged cron-health behavior with macOS entry |
| Update | `docs/plans/README.md` | add this plan to the index |

**Explicitly unchanged in this issue unless tests prove otherwise:**
- `scripts/operations/workstation-status.sh`
- `scripts/readiness/compare-harness-state.sh`

---

## TDD Test List

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| `test_registry_includes_macbook_portable` | workstation registry includes the new macOS machine with expected role/capabilities | updated `registry.yaml` | parser finds `macbook-portable` with `os: macos` |
| `test_registry_alias_maps_real_hostname` | real macOS hostname alias resolves to the canonical workstation key | alias `Vamsees-MacBook-Air.local` | workstation lookup resolves to `macbook-portable` |
| `test_harness_config_includes_macos_report_path` | readiness config can emit/report macOS readiness state | updated `harness-config.yaml` | report path and ws_hub_path are present |
| `test_sync_agent_configs_resolves_macos_ws_hub_path` | Hermes config sync resolves the macOS workspace path correctly | mocked hostname / config | resolved path equals `/Users/krishna/workspace-hub` |
| `test_nightly_readiness_macos_compatibility_guard` | readiness script avoids GNU-only shell assumptions in touched macOS code paths | audited `nightly-readiness.sh` | no unsupported command pattern remains in macOS path/report code paths |
| `test_ai_tools_status_tolerates_macos_workstation_entry` | ai-tools-status handles the added macOS harness-config entry without breaking snapshot generation | updated `harness-config.yaml` + mocked unreachable macOS host | YAML snapshot still renders with macOS marked unreachable/expected |
| `test_cron_health_registry_alias_parsing_unchanged` | cron-health still resolves registry hostnames/aliases correctly when macOS entry is added | updated `registry.yaml` | existing cron-health test suite passes |
| `test_harness_readiness_regression_still_passes` | adding macOS metadata does not break existing readiness shell tests | updated configs | shell test suite passes |
| `test_linux_windows_readiness_outputs_unchanged` | existing Linux/Windows readiness behavior is preserved | updated workstation/readiness config | prior report naming/paths still pass |


---

## Acceptance Criteria

- [ ] Regression coverage passes: `bash tests/work-queue/test-harness-readiness.sh`
- [ ] `macbook-portable` exists in `config/workstations/registry.yaml` with explicit OS/role/capabilities and hostname alias coverage
- [ ] `scripts/readiness/harness-config.yaml` contains a macOS workstation entry with Hermes-compatible path/report metadata
- [ ] `scripts/_core/sync-agent-configs.sh` resolves the canonical macOS workspace path `/Users/krishna/workspace-hub` and alias mapping in tests or explicit logic review
- [ ] `scripts/readiness/nightly-readiness.sh` is audited/updated only for the macOS report/alias/BSD-safe code paths needed by this issue
- [ ] `scripts/maintenance/ai-tools-status.sh` tolerates the added macOS harness-config entry without breaking output generation
- [ ] `scripts/monitoring/tests/test_cron_health_check.sh` (or equivalent cron-health coverage) passes with the new macOS registry entry present
- [ ] `docs/ops/hermes-weekly-cross-machine-parity-checklist.md` reflects the implemented macOS parity contract
- [ ] Residual macOS-specific drift is documented rather than left implicit
- [ ] Live macOS validation remains explicitly out of scope unless the host is reachable during execution
- [ ] Plan review artifacts are posted before implementation begins

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | APPROVE with MINOR | final draft now fixes canonical macOS path/alias contract and explicit consumer disposition; remaining work is implementation risk, not planning risk |
| Codex | APPROVE | final lightweight rerun confirms downstream consumer disposition, canonical contract, and tightened nightly-readiness scope are explicit |
| Gemini | APPROVE | final lightweight rerun confirms prior blockers are resolved and scope is appropriately bounded |

**Overall result:** PASS — ready for user approval

Revisions made based on review:
- first revision added concrete macOS evidence, brought `nightly-readiness.sh` into scope, and expanded alias/path-coverage tests
- second revision fixed the canonical macOS contract to `/Users/krishna/workspace-hub` + `Vamsees-MacBook-Air.local`, explicitly dispositioned downstream consumers, added `ai-tools-status.sh` / cron-health coverage, and kept `compare-harness-state.sh` out of scope as follow-up work
- final lightweight rerun from Codex and Gemini approved the plan with no remaining MAJOR blockers

---

## Risks and Open Questions

- Risk: the actual macOS machine may not currently be reachable from this Linux host, so repo-side parity scaffolding may land before live validation on the device.
- Risk: `scripts/_core/sync-agent-configs.sh` and `scripts/readiness/nightly-readiness.sh` may have path/hostname assumptions not fully covered until consumer tests are in place.
- Risk: adding a macOS workstation to registry/readiness metadata could change machine enumeration in `ai-tools-status.sh` and similar readers if not explicitly covered.
- Open: none on canonical macOS path — use `/Users/krishna/workspace-hub` with hostname alias `Vamsees-MacBook-Air.local` as the repo contract for this issue.
- Open: if `compare-harness-state.sh` later needs macOS support, capture that as a separate follow-up instead of expanding this issue.

---

## Complexity: T2

**T2** — the work is bounded to workstation/readiness configuration, one possible sync-logic adjustment, documentation, and regression tests; it is cross-machine but not a large architectural redesign.
