# Plan for #2240: macOS Hermes parity — install, config, and tool alignment

> Status: draft
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

A repo-tracked macOS Hermes parity contract that adds `macbook-portable` to the workstation/readiness model, verifies the shared Hermes baseline can be resolved on macOS, and documents/tests the acceptable platform-specific drift.

---

## Pseudocode

```text
add macbook_portable_to_registry():
    declare canonical machine key, hostname aliases, workspace root, role, and capabilities

add macbook_portable_to_harness_config():
    declare ws_hub_path, report_path, optional ssh target, and Hermes managed-key checks

inventory_consumers():
    identify every script that reads registry.yaml or harness-config.yaml
    decide whether each consumer needs code changes, tests, or explicit out-of-scope note

audit_sync_and_readiness_compatibility():
    verify resolve_ws_hub_path can map macOS hostname/alias to the intended workspace root
    inspect nightly-readiness.sh and related readers for BSD/macOS-incompatible shell assumptions

add regression tests():
    assert macbook-portable entries parse correctly, aliases resolve, and existing Linux/Windows flows remain unchanged
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Modify | `config/workstations/registry.yaml` | add canonical `macbook-portable` machine identity/capabilities and hostname aliases |
| Modify | `scripts/readiness/harness-config.yaml` | add macOS workstation path/report metadata for Hermes readiness flows |
| Modify | `scripts/_core/sync-agent-configs.sh` | make macOS hostname/path resolution explicit and testable |
| Modify | `scripts/readiness/nightly-readiness.sh` | audit/fix hostname/report naming and BSD/macOS shell compatibility where required |
| Modify | `docs/ops/hermes-weekly-cross-machine-parity-checklist.md` | refine macOS evidence steps based on implementation details |
| Modify | `tests/work-queue/test-harness-readiness.sh` | add regression coverage for the new workstation entry / readiness config parsing |
| Update | `docs/plans/README.md` | add this plan to the index |

---

## TDD Test List

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| `test_registry_includes_macbook_portable` | workstation registry includes the new macOS machine with expected role/capabilities | updated `registry.yaml` | parser finds `macbook-portable` with `os: macos` |
| `test_registry_alias_maps_real_hostname` | real macOS hostname alias resolves to the canonical workstation key | alias `Vamsees-MacBook-Air.local` | workstation lookup resolves to `macbook-portable` |
| `test_harness_config_includes_macos_report_path` | readiness config can emit/report macOS readiness state | updated `harness-config.yaml` | report path and ws_hub_path are present |
| `test_sync_agent_configs_resolves_macos_ws_hub_path` | Hermes config sync resolves the macOS workspace path correctly | mocked hostname / config | resolved path equals macOS workspace root |
| `test_nightly_readiness_macos_compatibility_guard` | readiness script avoids GNU-only shell assumptions that break on macOS | audited `nightly-readiness.sh` | no unsupported `grep -P` / brittle `sed -i` path remains in macOS code path |
| `test_harness_readiness_regression_still_passes` | adding macOS metadata does not break existing readiness shell tests | updated configs | shell test suite passes |
| `test_linux_windows_readiness_outputs_unchanged` | existing Linux/Windows readiness behavior is preserved | updated workstation/readiness config | prior report naming/paths still pass |


---

## Acceptance Criteria

- [ ] Regression coverage passes: `bash tests/work-queue/test-harness-readiness.sh`
- [ ] `macbook-portable` exists in `config/workstations/registry.yaml` with explicit OS/role/capabilities and hostname alias coverage
- [ ] `scripts/readiness/harness-config.yaml` contains a macOS workstation entry with Hermes-compatible path/report metadata
- [ ] `scripts/_core/sync-agent-configs.sh` resolves the canonical macOS workspace path and alias mapping in tests or explicit logic review
- [ ] `scripts/readiness/nightly-readiness.sh` is audited/updated so macOS report generation does not rely on unsupported GNU-only shell behavior
- [ ] `docs/ops/hermes-weekly-cross-machine-parity-checklist.md` reflects the implemented macOS parity contract
- [ ] Residual macOS-specific drift is documented rather than left implicit
- [ ] Live macOS validation remains explicitly out of scope unless the host is reachable during execution
- [ ] Plan review artifacts are posted before implementation begins

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | MAJOR | missing consumer inventory, unresolved macOS path contract, and insufficient downstream readiness-compatibility coverage |
| Codex | MAJOR | rerun still requires explicit disposition of downstream registry/readiness consumers and a decided macOS path/alias contract |
| Gemini | MAJOR | rerun still flags planning-to-plan drift because consumer inventory remains implicit rather than enumerated in scope/files |

**Overall result:** FAIL after rerun (re-draft still required before implementation)

Revisions made based on review:
- first revision added concrete macOS evidence, brought `nightly-readiness.sh` into scope, and expanded alias/path-coverage tests
- rerun still requires an explicit consumer inventory/disposition list, a fixed canonical macOS workspace-path decision, and tighter boundaries on which downstream readers are in-scope vs follow-up work before approval

---

## Risks and Open Questions

- Risk: the actual macOS machine may not currently be reachable from this Linux host, so repo-side parity scaffolding may land before live validation on the device.
- Risk: `sync-agent-configs.sh` may rely on Linux-oriented assumptions not revealed until a real macOS dry run occurs.
- Risk: the canonical workstation registry currently omits macOS entirely, so downstream tooling may require follow-up normalization once the entry is added.
- Open: should macOS use `schedule_variant: none` permanently, or should launchd-backed weekly automation eventually be modeled in the same registry?
- Open: what is the canonical macOS workspace root path (`/Users/<user>/workspace-hub` vs alternate location) and should that be templated or fixed in repo metadata?

---

## Complexity: T2

**T2** — the work is bounded to workstation/readiness configuration, one possible sync-logic adjustment, documentation, and regression tests; it is cross-machine but not a large architectural redesign.
