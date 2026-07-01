# Plan for #3331: Codex Frontier Harness and Memory Parity

> **Status:** draft
> **Complexity:** T3
> **Date:** 2026-07-01
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/3331
> **Client:** N/A
> **Project:** N/A
> **Lane:** lane:claude
> **Review artifacts:** scripts/review/results/2026-07-01-plan-3331-claude-r1.md | scripts/review/results/2026-07-01-plan-3331-claude.md | scripts/review/results/2026-07-01-plan-3331-codex.md | scripts/review/results/2026-07-01-plan-3331-gemini.md

---

## Resource Intelligence Summary

### Existing repo code

- `scripts/readiness/provider_harness_parity.py` will remain the main provider parity collector. Current Codex predicates prove runtime slice presence, `.codex/skills` adapter presence, and hard-gate text in the active Codex runtime. The Codex memory predicate will need a stdlib-only seam to consume per-surface freshness facts for `config/agents/codex/MEMORY.runtime.md`; it must not treat the global memory verdict as a Codex-specific verdict.
- `tests/readiness/test_provider_harness_parity.py` already pins Codex memory, skill-adapter, and active-runtime behavior. It will be extended before implementation so a stale or unsourced Codex readback slice fails red.
- `scripts/curation/audit_memory_freshness.py` already grades `.claude/memory/context.md`, `.claude/memory/agents.md`, `config/agents/codex/MEMORY.runtime.md`, `config/agents/gemini/MEMORY.runtime.md`, and `~/.hermes/memories/` against 36h/72h thresholds. The implementation will reuse this audit rather than inventing a parallel freshness check.
- `tests/curation/test_audit_memory_freshness.py` already tests freshness verdict boundaries, git-commit clocks for bridged surfaces, local Hermes mtime, and no absolute paths in emitted state.
- `scripts/agents/build-soul-runtime.sh`, `scripts/agents/soul-runtime-lib.sh`, and `scripts/enforcement/check-soul-runtime-drift.sh` already define the Codex `AGENTS.runtime.md` generation and drift gate. The implementation will fix the current generated-artifact drift and add targeted coverage only if the drift source needs stronger prevention.
- `scripts/memory/bridge-hermes-claude.sh` already owns cross-provider memory propagation. Section 7b regenerates `config/agents/codex/MEMORY.runtime.md` and `config/agents/gemini/MEMORY.runtime.md` on the designated slice owner, from git-tracked `.claude/memory/`.
- `scripts/memory/curate_readback_slice.py` already enforces deterministic, budget-capped, entry-boundary truncation for Codex/Hermes/Gemini readback slices.
- `.codex/hooks.json` contains Codex hook command strings. Several commands hardcode `/mnt/local-analysis/workspace-hub/...`; the implementation will convert those to repo-root or `WORKSPACE_HUB` resolution and add a regression guard.
- `scripts/enforcement/check-model-id-sourcing.sh` and `scripts/enforcement/model-id-baseline.txt` already implement the model-ID hardcode ratchet. This issue will bring the all-or-nothing ratchet back to green because a red global model-ID guard cannot serve as a frontier-model readiness gate.
- `config/agents/model-registry.yaml` and `config/agents/provider-capabilities.yaml` both describe Codex/Hermes model IDs and context windows. The implementation will document or enforce their authority boundary so frontier-model swaps do not require multiple independent edits.

### Standards

| Standard | Status | Source |
|---|---|---|
| Control-plane adapter topology | applicable | `docs/standards/CONTROL_PLANE_CONTRACT.md` defines `AGENTS.md` as canonical and `.codex/` as the Codex adapter surface. |
| Model-release readiness | applicable | `docs/standards/MODEL_RELEASE_READINESS_CONTRACT.md` requires context-budget awareness, truncation-safe artifacts, machine-readable rules, prompt-pack portability, and discoverability. |
| Model-release upgrade procedure | applicable | `docs/standards/MODEL_RELEASE_UPGRADE_PLAYBOOK.md` already separates provider-owned drift from repo-owned drift and has a Claude primary model-swap checklist; this issue will add Codex-specific readiness coverage. |
| No hardcoded absolute paths | applicable | `.claude/rules/coding-style.md` path handling plus `scripts/enforcement/check-no-abs-paths.sh` establish repo-root/env-var path handling. |
| Enforcement gradient | applicable | `.claude/rules/patterns.md` requires binary rules to move toward scripts/hooks when possible. |

### LLM Wiki pages consulted

- No LLM wiki pages will be consulted. This is workspace-hub control-plane work and does not touch wiki content.

### Documents consulted

- [#3331](https://github.com/vamseeachanta/workspace-hub/issues/3331) — current issue body defines the Codex frontier-model parity objective and acceptance criteria.
- [#3058](https://github.com/vamseeachanta/workspace-hub/issues/3058) — parent hardening epic; this issue will convert manual provider/model parity checks into standing invariants.
- [#3043](https://github.com/vamseeachanta/workspace-hub/issues/3043) — existing model parity epic; this issue will reuse its model-swap lessons without becoming a Claude/Opus parity duplicate.
- [#3114](https://github.com/vamseeachanta/workspace-hub/issues/3114) — provider-equivalence umbrella; this issue will focus on Codex runtime/memory/model-release readiness, not portable agent-definition design.
- [#2889](https://github.com/vamseeachanta/workspace-hub/issues/2889) and `docs/plans/2026-06-10-issue-2889-provider-harness-parity.md` — prior provider harness parity work that produced the current collector.
- `docs/standards/MODEL_RELEASE_UPGRADE_PLAYBOOK.md` — procedural companion for provider/model release adoption.
- `docs/standards/MODEL_RELEASE_READINESS_CONTRACT.md` — readiness dimensions and canonical anchor obligations.
- `docs/standards/CONTROL_PLANE_CONTRACT.md` — adapter topology and Codex adapter role.

### Gaps identified

- Codex `AGENTS.runtime.md` can drift when skill families change. The current runtime artifact is out of sync with regenerated sources.
- Codex memory parity is mechanically present but not semantically strong enough: the parity collector accepts a non-empty readback slice without checking `surfaces.codex_runtime`. The broader memory bridge currently reports `MEMORY-EXPIRED` because `.claude/memory/context.md` is old; that global verdict will be documented as a bridge-health signal, not as proof that Codex's own slice is stale.
- Codex hook portability is incomplete: `.codex/hooks.json` carries absolute workspace paths that will not survive alternate checkout roots or machines.
- Model-ID sourcing is not green before the next model swap: the ratchet has unbaselined new literals and stale baseline entries. This issue will reconcile all new and stale entries required for `check-model-id-sourcing.sh --enforce` to pass.
- Codex frontier-model upgrade steps are implicit. The existing playbook has a worked Claude primary-model checklist but no Codex-specific checklist covering CLI version, `config/agents/codex/config.toml`, `~/.codex/config.toml` sync, active `~/.codex/AGENTS.md`, memory bridge, hooks, skill adapter, and parity probes.
- `config/agents/model-registry.yaml` and `config/agents/provider-capabilities.yaml` need a clearer authority boundary for Codex/Hermes model IDs and context windows.

### Evidence

**Issue statuses** (verified 2026-07-01T20:53:35Z via `gh issue view` / `gh issue list`):
- [#3331](https://github.com/vamseeachanta/workspace-hub/issues/3331) — OPEN — `feat(codex): frontier-model harness and memory parity hardening`
- [#3058](https://github.com/vamseeachanta/workspace-hub/issues/3058) — OPEN — `Epic: Harden the repo ecosystem — enforce equivalence, model-sourcing, parity baselines, retrieval`
- [#3043](https://github.com/vamseeachanta/workspace-hub/issues/3043) — OPEN — `Model parity: make the repo ecosystem equivalent for Opus and Fable (run on multiple machines)`
- [#3114](https://github.com/vamseeachanta/workspace-hub/issues/3114) — OPEN — `feat(ecosystem): Omnigent-lens — make repo ecosystem AI-provider- & OS/machine-equivalent`
- [#2889](https://github.com/vamseeachanta/workspace-hub/issues/2889) — plan-index row shows implemented/pending closeout; the collector remains live.

**Branch baseline** (`git status --short --branch --untracked-files=no`, 2026-07-01T20:53:35Z):
```
## feat/plan-3331-codex-frontier-readiness...origin/main
```

**File existence** (`test -f` and source reads, 2026-07-01T20:53:35Z):
- EXISTS: `scripts/readiness/provider_harness_parity.py`
- EXISTS: `tests/readiness/test_provider_harness_parity.py`
- EXISTS: `scripts/curation/audit_memory_freshness.py`
- EXISTS: `tests/curation/test_audit_memory_freshness.py`
- EXISTS: `scripts/agents/build-soul-runtime.sh`
- EXISTS: `scripts/enforcement/check-soul-runtime-drift.sh`
- EXISTS: `scripts/memory/bridge-hermes-claude.sh`
- EXISTS: `scripts/memory/curate_readback_slice.py`
- EXISTS: `.codex/hooks.json`
- EXISTS: `scripts/enforcement/check-model-id-sourcing.sh`
- EXISTS: `config/agents/model-registry.yaml`
- EXISTS: `config/agents/provider-capabilities.yaml`
- EXISTS: `docs/standards/MODEL_RELEASE_UPGRADE_PLAYBOOK.md`

**Runtime drift proof** (`bash scripts/enforcement/check-soul-runtime-drift.sh`, 2026-07-01T20:53:35Z):
```
OK     hermes/SOUL.runtime.md
OK     claude/SOUL.runtime.md
OK     codex/SOUL.runtime.md
DRIFT  codex/AGENTS.runtime.md — committed artifact differs from rebuilt sources
```

**Provider parity proof** (`uv run --no-project python scripts/readiness/provider_harness_parity.py --workspace . --home "$HOME" --format yaml`, 2026-07-01T20:53:35Z):
```
codex:
  present: true
  installed: true
  "memory:read": {status: present, reason: codex_memory_runtime_found}
  "skills:invoke": {status: present, reason: codex_skill_adapter_found}
  "workflow:gates": {status: present, reason: codex_agents_runtime_active}
hermes:
  "memory:read": {status: present, reason: hermes_memory_store_found}
  "skills:invoke": {status: present, reason: hermes_skill_registry_found}
  "workflow:gates": {status: present, reason: hermes_soul_runtime_active}
```

**Memory freshness proof** (`uv run --no-project python scripts/curation/audit_memory_freshness.py --stdout`, 2026-07-01T20:53:38Z):
```
"context_md": {"present": true, "age_hours": 127.885, "signal": "git-commit"}
"codex_runtime": {"present": true, "age_hours": 0.432, "signal": "git-commit"}
"hermes_memories": {"present": true, "age_hours": 11.477, "signal": "file-mtime"}
"freshness": "MEMORY-EXPIRED"
```

**Model ID sourcing proof** (`bash scripts/enforcement/check-model-id-sourcing.sh --enforce`, 2026-07-01T20:53:35Z):
```
model-id-sourcing: 1129 in-scope literal(s), 12 NOT in baseline, 44 STALE baseline entries
```

**Hook portability proof** (`sed -n '1,220p' .codex/hooks.json`, 2026-07-01T20:53:35Z):
```
"command": "bash '/mnt/local-analysis/workspace-hub/.codex/hooks/session-governor-check.sh'"
"command": "bash '/mnt/local-analysis/workspace-hub/.codex/hooks/plan-approval-gate.sh'"
"command": "node '/mnt/local-analysis/workspace-hub/.codex/hooks/gsd-context-monitor.js'"
```

**Reproduction proofs**:
- N/A — this is governance/control-plane hardening, not a single alleged runtime failure. The current failing gates are reproduced above and will become red tests/checks where they are not already covered.

Minimum distinct source count: 12.

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-07-01-issue-3331-codex-frontier-harness-memory-parity.md` |
| Plan index | `docs/plans/README.md` |
| Provider parity collector | `scripts/readiness/provider_harness_parity.py` |
| Provider parity tests | `tests/readiness/test_provider_harness_parity.py` |
| Memory freshness audit | `scripts/curation/audit_memory_freshness.py` |
| Memory freshness tests | `tests/curation/test_audit_memory_freshness.py` |
| Codex runtime generator | `scripts/agents/build-soul-runtime.sh` |
| Codex runtime drift gate | `scripts/enforcement/check-soul-runtime-drift.sh` |
| Memory bridge | `scripts/memory/bridge-hermes-claude.sh` |
| Readback slice curator | `scripts/memory/curate_readback_slice.py` |
| Codex hooks | `.codex/hooks.json` |
| Hook portability test | `tests/readiness/test_codex_hook_portability.py` |
| Optional Codex hook allowlist | `config/quality/codex-hook-portability-allowlist.txt` |
| Model ID guard | `scripts/enforcement/check-model-id-sourcing.sh` |
| Model ID baseline | `scripts/enforcement/model-id-baseline.txt` |
| Model registry | `config/agents/model-registry.yaml` |
| Provider capabilities | `config/agents/provider-capabilities.yaml` |
| Model release playbook | `docs/standards/MODEL_RELEASE_UPGRADE_PLAYBOOK.md` |
| Model release readiness docs tests | `tests/docs/test_workspace_hub_model_release_readiness.py` |
| Legal/security scan | `scripts/legal/legal-sanity-scan.sh` |
| Plan review — Claude | `scripts/review/results/2026-07-01-plan-3331-claude.md` |
| Plan review — Codex | `scripts/review/results/2026-07-01-plan-3331-codex.md` |
| Plan review — Gemini | `scripts/review/results/2026-07-01-plan-3331-gemini.md` |

---

## Deliverable

Codex will have a tested frontier-model readiness path that keeps its loaded runtime, memory readback, hooks, model-source data, and release checklist equivalent to Claude/Hermes before the next Codex model swap.

---

## Pseudocode

```
test_codex_memory_parity_requires_fresh_bridge_surface():
    build temp workspace with codex runtime, codex memory slice, claude memory files
    provide freshness JSON with global freshness MEMORY-EXPIRED
    set surfaces.context_md.age_hours to 128 and surfaces.codex_runtime.age_hours to 1
    collect provider harness readiness with that freshness JSON
    assert codex memory parity remains present because the Codex surface is fresh

test_codex_memory_parity_degrades_when_codex_runtime_surface_is_expired():
    build temp workspace with codex runtime and codex memory slice
    provide freshness JSON with surfaces.codex_runtime.age_hours greater than MEMORY_EXPIRED_H
    collect provider harness readiness with that freshness JSON
    assert codex memory parity reports degraded/absent with a Codex-specific stale reason

test_codex_hooks_are_repo_root_portable():
    parse .codex/hooks.json as JSON
    walk each hooks.*[].hooks[].command
    reject hardcoded /mnt/local-analysis/workspace-hub, /home/<user>, /Users/<user>, and drive-letter roots
    allow commands that derive WORKSPACE_HUB or git rev-parse --show-toplevel
    allow future absolute-path exceptions only through an exact-command allowlist with forensic comments

test_model_registry_capability_boundary_is_documented():
    load config/agents/model-registry.yaml and config/agents/provider-capabilities.yaml
    assert Codex provider capability values either reference registry-owned ids or carry documented comments
    assert context-window values agree with the documented authority rule

test_upgrade_playbook_has_codex_frontier_checklist():
    read docs/standards/MODEL_RELEASE_UPGRADE_PLAYBOOK.md
    assert a Codex frontier-model checklist exists
    assert it names config/agents/codex/config.toml, sync-agent-configs, active AGENTS runtime, memory bridge, hooks, model-id guard, parity collector

implementation_flow():
    write failing tests for memory freshness, hook portability, model authority, and playbook coverage
    run focused tests to confirm red
    regenerate Codex AGENTS runtime from canonical sources
    update provider parity/freshness integration through stdlib-only JSON consumption, not by importing audit_memory_freshness.py
    replace absolute Codex hook paths with repo-root/env-var resolution
    reconcile every model ID baseline/literal required for check-model-id-sourcing.sh --enforce to pass
    add Codex checklist to model release playbook
    run focused tests, drift gates, model-id guard, provider parity, memory freshness, legal scan
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Modify | `config/agents/codex/AGENTS.runtime.md` | Regenerate stale Codex runtime artifact from canonical sources. |
| Modify | `scripts/readiness/provider_harness_parity.py` | Add freshness-aware Codex memory readiness through optional stdlib-only JSON consumption so non-empty stale slices do not pass as equivalent. |
| Modify | `tests/readiness/test_provider_harness_parity.py` | Write red tests for stale Codex memory/readback semantics before collector changes. |
| Modify | `scripts/curation/audit_memory_freshness.py` | Only if the implementation needs a machine-readable helper or constants export; the parity collector must not import this module directly. |
| Modify | `tests/curation/test_audit_memory_freshness.py` | Cover any new helper or semantics added for provider parity consumption. |
| Modify | `.codex/hooks.json` | Replace absolute workspace-root commands with portable repo-root or `WORKSPACE_HUB` resolution. |
| Create | `tests/readiness/test_codex_hook_portability.py` | Prevent Codex hook commands from regressing to machine-local absolute paths. |
| Create | `config/quality/codex-hook-portability-allowlist.txt` | Only if a reviewed absolute-path exception is unavoidable; entries must be exact-command scoped, not blanket path exemptions. |
| Modify | `scripts/enforcement/model-id-baseline.txt` | Update baseline only after deciding each new/stale occurrence is intentional or cleaned up. |
| Modify | `config/agents/model-registry.yaml` | Update comments/fields only where needed for Codex frontier-model authority and context-window semantics. |
| Modify | `config/agents/provider-capabilities.yaml` | Reconcile Codex/Hermes model/context fields with registry authority or document why capability metadata intentionally differs. |
| Modify | `docs/standards/MODEL_RELEASE_UPGRADE_PLAYBOOK.md` | Add Codex-specific frontier-model readiness checklist. |
| Modify | `tests/docs/test_workspace_hub_model_release_readiness.py` | Assert the Codex checklist and required operational paths remain discoverable. |
| Modify | `docs/plans/README.md` | Index this plan. |

---

## TDD Test List

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| `test_codex_memory_read_ignores_global_expired_when_codex_surface_is_fresh` | A stale Claude/global surface does not falsely degrade fresh Codex memory | Temp workspace with Codex runtime, memory file, freshness JSON where `context_md` is expired and `codex_runtime` is fresh | `memory:read` remains present for Codex |
| `test_codex_memory_read_degrades_when_codex_runtime_surface_expired` | Codex memory parity fails on a stale Codex readback slice | Temp workspace with Codex runtime, memory file, freshness JSON where `codex_runtime` is expired | Codex memory readiness is degraded/absent with a Codex-specific stale reason |
| `test_codex_memory_read_accepts_fresh_runtime_slice_without_freshness_json` | Backward-compatible collector behavior remains usable when no freshness JSON is supplied | Temp workspace with Codex runtime and non-empty memory slice | `memory:read` is present for Codex and reason records no freshness evidence |
| `test_codex_hook_commands_do_not_hardcode_workspace_root` | Codex hooks are portable across checkout roots | Live `.codex/hooks.json` plus optional exact-command allowlist | No command contains `/mnt/local-analysis/workspace-hub`, `/home/`, `/Users/`, or drive-letter roots unless explicitly allowlisted by exact command |
| `test_codex_hooks_parse_as_json_after_portability_change` | Hook edits preserve valid JSON shape | Live `.codex/hooks.json` | JSON parses and `hooks` object exists |
| `test_upgrade_playbook_has_codex_frontier_model_checklist` | The release playbook has Codex-specific swap steps | `docs/standards/MODEL_RELEASE_UPGRADE_PLAYBOOK.md` | Checklist names Codex config sync, active runtime, memory bridge, hooks, skill adapter, model-id guard, provider parity |
| `test_model_registry_provider_capabilities_codex_boundary` | Codex/Hermes model ID/context-window authority is explicit | `config/agents/model-registry.yaml`, `config/agents/provider-capabilities.yaml` | Test passes only when documented authority is represented consistently |
| `test_model_id_sourcing_guard_green_after_full_cleanup` | Model ID hardcode ratchet is clean after full planned cleanup | `bash scripts/enforcement/check-model-id-sourcing.sh --enforce` | Exit 0 |
| `test_soul_runtime_drift_green_after_regen` | Codex runtime artifacts match generator output | `bash scripts/enforcement/check-soul-runtime-drift.sh --quiet` | Exit 0 |

---

## Acceptance Criteria

- [ ] Plan passes T3 adversarial review with Claude, Codex, and Gemini artifacts or explicit `UNAVAILABLE` files.
- [ ] The issue remains blocked from implementation until the user applies `status:plan-approved`.
- [ ] `bash scripts/enforcement/check-soul-runtime-drift.sh` passes.
- [ ] `uv run --no-project python scripts/readiness/provider_harness_parity.py --workspace . --home "$HOME" --format yaml` reports Codex, Claude, and Hermes memory/skills/gates present with any expected divergences explicitly classified.
- [ ] Codex-specific freshness passes: the provider parity check consumes per-surface freshness evidence and treats `surfaces.codex_runtime` as fresh. A global `MEMORY-EXPIRED` caused only by non-Codex surfaces is documented as out-of-scope or routed to a separate bridge-health issue/comment.
- [ ] `bash scripts/enforcement/check-model-id-sourcing.sh --enforce` passes after all new and stale model-ID occurrences are sourced, annotated, removed, or baselined.
- [ ] `.codex/hooks.json` contains no hardcoded `/mnt/local-analysis/workspace-hub` commands.
- [ ] Codex frontier-model checklist exists in `docs/standards/MODEL_RELEASE_UPGRADE_PLAYBOOK.md`.
- [ ] Focused tests pass: `uv run pytest tests/readiness/test_provider_harness_parity.py tests/readiness/test_codex_hook_portability.py tests/curation/test_audit_memory_freshness.py tests/docs/test_workspace_hub_model_release_readiness.py -v`.
- [ ] Legal/security scan passes: `scripts/legal/legal-sanity-scan.sh`.
- [ ] Completeness evidence is produced before close per [#2798](https://github.com/vamseeachanta/workspace-hub/issues/2798).

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Claude R1 | MAJOR | R1 found three blockers: global freshness verdict falsely coupled to Codex, global `MEMORY-EXPIRED` AC was out of scope, and model-id all-or-nothing AC conflicted with narrow cleanup language. |
| Claude R2 | UNAVAILABLE | Re-review timed out with `rc=124: no stderr captured`; no final no-MAJOR signal. |
| Codex | UNAVAILABLE | R1 CLI timed out with `Reading additional input from stdin...`; no review signal. |
| Gemini | UNAVAILABLE | R1 CLI failed authentication with `IneligibleTierError`; no review signal. |

**Overall result:** BLOCKED — the revised plan addresses R1 findings but requires a fresh no-MAJOR adversarial review before it can be surfaced for user approval or moved to `status:plan-review`.

Revisions made based on review:
- Use per-surface `surfaces.codex_runtime` freshness instead of the global `freshness` verdict for Codex memory parity.
- Remove the acceptance criterion that required global `MEMORY-EXPIRED` to clear inside this Codex-scoped issue; route non-Codex staleness as bridge-health evidence instead.
- Make full `check-model-id-sourcing.sh --enforce` cleanup in scope so the ratchet becomes a valid model-swap gate.
- Specify the stdlib-only freshness seam for `provider_harness_parity.py`.
- Specify exact-command allowlisting for any unavoidable Codex hook portability exception.

---

## Risks and Open Questions

- **Risk:** Running `bridge-hermes-claude.sh --commit` from this planning branch could create a memory-bridge commit race with the production daily bridge. The implementation will either run bridge refresh from the canonical owner workflow or explicitly separate bridge refresh from code changes.
- **Risk:** `provider_harness_parity.py` currently uses only Python standard library for Windows collector compatibility. Any freshness integration must preserve that portability by consuming structured JSON written by `audit_memory_freshness.py`, not by importing that module or adding PyYAML dependencies.
- **Risk:** `.codex/hooks.json` may intentionally need some commands to run before a repository root is discoverable. The implementation will use a small portable shell wrapper expression already present in later Stop hooks, or document any unavoidable exception with a test-level allowlist.
- **Risk:** `provider-capabilities.yaml` may intentionally express usable context for `codex-cli` rather than raw OpenAI model context for `gpt-5.5`. The implementation will document that boundary instead of forcing false equality.
- **Risk:** Model-ID ratchet cleanup may touch historical memory snapshots and unrelated scripts. The issue will still make the all-or-nothing guard green, because leaving it red would make the next Codex model swap unverifiable.

---

## Complexity: T3

**T3** — this is cross-provider control-plane work touching Codex runtime generation, memory bridge freshness, hooks, model registry/capability policy, model-release documentation, and enforcement tests. It requires T3 adversarial plan review before user approval.
