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
    declare hostname, os=macos, role, workspace root, schedule variant, and capabilities

add macbook_portable_to_harness_config():
    declare ws_hub_path, report_path, optional ssh target, and reuse Hermes managed-key checks

extend sync validation path_if_needed():
    ensure resolve_ws_hub_path can map the macOS hostname or fallback path cleanly

extend readiness/checklist docs():
    capture what parity means on macOS and what drift is acceptable

add regression tests():
    assert macbook-portable entries parse correctly and do not break readiness workflows
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Modify | `config/workstations/registry.yaml` | add canonical `macbook-portable` machine identity/capabilities |
| Modify | `scripts/readiness/harness-config.yaml` | add macOS workstation path/report metadata for Hermes readiness flows |
| Modify | `scripts/_core/sync-agent-configs.sh` | adjust hostname/path resolution only if current logic cannot map the macOS workstation cleanly |
| Modify | `docs/ops/hermes-weekly-cross-machine-parity-checklist.md` | refine macOS evidence steps based on implementation details |
| Modify | `tests/work-queue/test-harness-readiness.sh` | add regression coverage for the new workstation entry / readiness config parsing |
| Update | `docs/plans/README.md` | add this plan to the index |

---

## TDD Test List

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| `test_registry_includes_macbook_portable` | workstation registry includes the new macOS machine with expected role/capabilities | updated `registry.yaml` | parser finds `macbook-portable` with `os: macos` |
| `test_harness_config_includes_macos_report_path` | readiness config can emit/report macOS readiness state | updated `harness-config.yaml` | report path and ws_hub_path are present |
| `test_sync_agent_configs_resolves_macos_ws_hub_path` | Hermes config sync resolves the macOS workspace path correctly | mocked hostname / config | resolved path equals macOS workspace root |
| `test_harness_readiness_regression_still_passes` | adding macOS metadata does not break existing readiness shell tests | updated configs | shell test suite passes |

---

## Acceptance Criteria

- [ ] Regression coverage passes: `bash tests/work-queue/test-harness-readiness.sh`
- [ ] `macbook-portable` exists in `config/workstations/registry.yaml` with explicit OS/role/capabilities
- [ ] `scripts/readiness/harness-config.yaml` contains a macOS workstation entry with Hermes-compatible path/report metadata
- [ ] `scripts/_core/sync-agent-configs.sh` can resolve or explicitly document the macOS workspace path behavior
- [ ] `docs/ops/hermes-weekly-cross-machine-parity-checklist.md` reflects the implemented macOS parity contract
- [ ] Residual macOS-specific drift is documented rather than left implicit
- [ ] Plan review artifacts are posted before implementation begins

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | MAJOR | missing consumer inventory, unresolved macOS path contract, and insufficient downstream readiness-compatibility coverage |
| Codex | MAJOR | producer files are named but reader coverage/path-contract decisions are still implicit; live validation must be deferred explicitly |
| Gemini | MAJOR | macOS/BSD compatibility gaps in downstream readiness tooling and hostname-mapping assumptions are unaddressed |

**Overall result:** FAIL (re-draft required before implementation)

Revisions made based on review:
- none yet — plan must be revised to inventory all config consumers, define the canonical macOS workspace path/hostname mapping, and include downstream readiness compatibility checks before re-review

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
