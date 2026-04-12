2026-04-12T09:54:44.488513Z ERROR codex_core_skills::loader: failed to stat skills entry /mnt/local-analysis/workspace-hub/.claude/skills/skills (symlink): No such file or directory (os error 2)
OpenAI Codex v0.120.0 (research preview)
--------
workdir: /mnt/local-analysis/workspace-hub
model: gpt-5.4
provider: openai
approval: never
sandbox: workspace-write [workdir, /tmp, $TMPDIR, /home/vamsee/.codex/memories]
reasoning effort: medium
reasoning summaries: none
session id: 019d811d-bdf9-76a2-a8b5-a41949d28eae
--------
user
# Adversarial Plan Re-Review Request — Issue #2240

You are an independent adversarial reviewer. This is a SECOND PASS after the plan was revised in response to earlier MAJOR findings. Be skeptical and focus on whether the prior review gaps are now sufficiently addressed for plan approval.

## Context
Repository: /mnt/local-analysis/workspace-hub
Issue: #2240 feat(harness): macOS Hermes parity — install, config, and tool alignment
This is a PLAN review checkpoint, not implementation review.

Previous high-signal findings that triggered revision:
- missing consumer inventory for registry/readiness readers
- canonical macOS path / hostname mapping was unresolved
- downstream macOS/BSD readiness compatibility was under-modeled
- live macOS validation needed to remain deferred unless host was reachable

Current expectations for the revised plan:
- concrete macOS evidence included from repo sources
- consumer inventory is explicit in pseudocode/scope
- `scripts/readiness/nightly-readiness.sh` is included as an implementation surface
- hostname alias/path-resolution coverage is explicit
- live macOS validation remains deferred unless host is reachable

## Revised Plan Under Review

     1|# Plan for #2240: macOS Hermes parity — install, config, and tool alignment
     2|
     3|> Status: draft
     4|> Complexity: T2
     5|> Date: 2026-04-12
     6|> Issue: https://github.com/vamseeachanta/workspace-hub/issues/2240
     7|> Review artifacts: scripts/review/results/2026-04-12-plan-2240-claude.md | scripts/review/results/2026-04-12-plan-2240-codex.md | scripts/review/results/2026-04-12-plan-2240-gemini.md
     8|
     9|---
    10|
    11|## Resource Intelligence Summary
    12|
    13|### Existing repo code
    14|- Found: `config/agents/hermes/config.yaml.template` and `config/agents/hermes/SOUL.md` — repo-managed Hermes baseline artifacts already exist and define the shared config surface macOS should converge toward.
    15|- Found: `scripts/_core/sync-agent-configs.sh` contains `resolve_ws_hub_path()` and `sync_hermes_yaml_config()` — Hermes config sync is already path-aware, but only for workstations declared in readiness config.
    16|- Found: `scripts/readiness/harness-config.yaml` currently defines only `dev-primary`, `dev-secondary`, and `licensed-win-1` workstations for Hermes-related readiness/state handling; no macOS workstation is present.
    17|- Found: `config/workstations/registry.yaml` lists Linux and Windows machines only; `macbook-portable` is absent from the canonical workstation registry.
    18|- Gap: there is no repo-tracked macOS workstation entry, no macOS readiness report target, and no documented automation path for macOS Hermes parity checks.
    19|
    20|### Standards
    21|| Standard | Status | Source |
    22||---|---|---|
    23|| Control-plane adapter model | done | `docs/standards/CONTROL_PLANE_CONTRACT.md` |
    24|| Hard-stop policy for non-engineering harness work | not applicable to implementation gate, but planning still mandatory | `docs/standards/HARD-STOP-POLICY.md` |
    25|
    26|### LLM Wiki pages consulted
    27|- No relevant wiki pages found; this is machine/readiness configuration work and does not depend on domain wiki content.
    28|
    29|### Documents consulted
    30|- `docs/ops/hermes-weekly-cross-machine-parity-checklist.md` — explicitly places `macbook-portable` in scope and records current expected parity checks plus macOS-specific drift notes (launchd/manual scheduling, path conventions, Linux-only tooling exclusions).
    31|- `scripts/readiness/harness-config.yaml` — current workstation/readiness source used by nightly readiness and Hermes managed-key checks; reveals macOS is not yet represented.
    32|- `config/workstations/registry.yaml` — machine registry used by cron/tooling discovery; reveals Linux and Windows coverage only.
    33|- `config/agents/hermes/config.yaml.template` — shared Hermes baseline whose managed keys must be portable to macOS.
    34|- `config/agents/claude/memory-snapshots/network_machines.md` — records concrete macOS evidence: hostname `Vamsees-MacBook-Air.local`, user `krishna`, and workspace path `~/workspace-hub/`.
    35|- `scripts/readiness/nightly-readiness.sh` — downstream readiness runner uses hostname-derived report naming plus GNU/BSD-sensitive shell commands (`hostname -s`, `sed -i`, `stat -c`), so macOS parity cannot be planned as pure YAML-only scaffolding.
    36|- Related issue #1583 — baseline-definition issue for Hermes settings across machines.
    37|- Related issue #2089 — weekly review/gov issue that already expects Linux + macOS parity evidence.
    38|- Related issue #2094 — multi-machine readiness matrix work that should be reused rather than duplicated.
    39|
    40|### Gaps identified
    41|- No canonical `macbook-portable` workstation entry exists in repo control-plane files.
    42|- No readiness report path or managed path-substitution config exists for macOS.
    43|- No automated parity-check surface currently proves macOS can resolve `external_dirs`, skills, and knowledge paths.
    44|- No regression tests currently guard macOS workstation config additions.
    45|
    46|<!-- Verification: distinct sources >= 3. Current count: 7 -->
    47|
    48|---
    49|
    50|## Artifact Map
    51|
    52|| Artifact | Path |
    53||---|---|
    54|| This plan | `docs/plans/2026-04-12-issue-2240-macos-hermes-parity-install-config-and-tool-alignment.md` |
    55|| Workstation registry | `config/workstations/registry.yaml` |
    56|| Readiness config | `scripts/readiness/harness-config.yaml` |
    57|| Hermes sync logic | `scripts/_core/sync-agent-configs.sh` |
    58|| Weekly checklist updates | `docs/ops/hermes-weekly-cross-machine-parity-checklist.md` |
    59|| Tests | `tests/work-queue/test-harness-readiness.sh` |
    60|| Plan review — Claude | `scripts/review/results/2026-04-12-plan-2240-claude.md` |
    61|| Plan review — Codex | `scripts/review/results/2026-04-12-plan-2240-codex.md` |
    62|| Plan review — Gemini | `scripts/review/results/2026-04-12-plan-2240-gemini.md` |
    63|
    64|---
    65|
    66|## Deliverable
    67|
    68|A repo-tracked macOS Hermes parity contract that adds `macbook-portable` to the workstation/readiness model, verifies the shared Hermes baseline can be resolved on macOS, and documents/tests the acceptable platform-specific drift.
    69|
    70|---
    71|
    72|## Pseudocode
    73|
    74|```text
    75|add macbook_portable_to_registry():
    76|    declare canonical machine key, hostname aliases, workspace root, role, and capabilities
    77|
    78|add macbook_portable_to_harness_config():
    79|    declare ws_hub_path, report_path, optional ssh target, and Hermes managed-key checks
    80|
    81|inventory_consumers():
    82|    identify every script that reads registry.yaml or harness-config.yaml
    83|    decide whether each consumer needs code changes, tests, or explicit out-of-scope note
    84|
    85|audit_sync_and_readiness_compatibility():
    86|    verify resolve_ws_hub_path can map macOS hostname/alias to the intended workspace root
    87|    inspect nightly-readiness.sh and related readers for BSD/macOS-incompatible shell assumptions
    88|
    89|add regression tests():
    90|    assert macbook-portable entries parse correctly, aliases resolve, and existing Linux/Windows flows remain unchanged
    91|```
    92|
    93|---
    94|
    95|## Files to Change
    96|
    97|| Action | Path | Reason |
    98||---|---|---|
    99|| Modify | `config/workstations/registry.yaml` | add canonical `macbook-portable` machine identity/capabilities and hostname aliases |
   100|| Modify | `scripts/readiness/harness-config.yaml` | add macOS workstation path/report metadata for Hermes readiness flows |
   101|| Modify | `scripts/_core/sync-agent-configs.sh` | make macOS hostname/path resolution explicit and testable |
   102|| Modify | `scripts/readiness/nightly-readiness.sh` | audit/fix hostname/report naming and BSD/macOS shell compatibility where required |
   103|| Modify | `docs/ops/hermes-weekly-cross-machine-parity-checklist.md` | refine macOS evidence steps based on implementation details |
   104|| Modify | `tests/work-queue/test-harness-readiness.sh` | add regression coverage for the new workstation entry / readiness config parsing |
   105|| Update | `docs/plans/README.md` | add this plan to the index |
   106|
   107|---
   108|
   109|## TDD Test List
   110|
   111|| Test name | What it verifies | Expected input | Expected output |
   112||---|---|---|---|
   113|| `test_registry_includes_macbook_portable` | workstation registry includes the new macOS machine with expected role/capabilities | updated `registry.yaml` | parser finds `macbook-portable` with `os: macos` |
   114|| `test_registry_alias_maps_real_hostname` | real macOS hostname alias resolves to the canonical workstation key | alias `Vamsees-MacBook-Air.local` | workstation lookup resolves to `macbook-portable` |
   115|| `test_harness_config_includes_macos_report_path` | readiness config can emit/report macOS readiness state | updated `harness-config.yaml` | report path and ws_hub_path are present |
   116|| `test_sync_agent_configs_resolves_macos_ws_hub_path` | Hermes config sync resolves the macOS workspace path correctly | mocked hostname / config | resolved path equals macOS workspace root |
   117|| `test_nightly_readiness_macos_compatibility_guard` | readiness script avoids GNU-only shell assumptions that break on macOS | audited `nightly-readiness.sh` | no unsupported `grep -P` / brittle `sed -i` path remains in macOS code path |
   118|| `test_harness_readiness_regression_still_passes` | adding macOS metadata does not break existing readiness shell tests | updated configs | shell test suite passes |
   119|| `test_linux_windows_readiness_outputs_unchanged` | existing Linux/Windows readiness behavior is preserved | updated workstation/readiness config | prior report naming/paths still pass |
   120|
   121|
   122|---
   123|
   124|## Acceptance Criteria
   125|
   126|- [ ] Regression coverage passes: `bash tests/work-queue/test-harness-readiness.sh`
   127|- [ ] `macbook-portable` exists in `config/workstations/registry.yaml` with explicit OS/role/capabilities and hostname alias coverage
   128|- [ ] `scripts/readiness/harness-config.yaml` contains a macOS workstation entry with Hermes-compatible path/report metadata
   129|- [ ] `scripts/_core/sync-agent-configs.sh` resolves the canonical macOS workspace path and alias mapping in tests or explicit logic review
   130|- [ ] `scripts/readiness/nightly-readiness.sh` is audited/updated so macOS report generation does not rely on unsupported GNU-only shell behavior
   131|- [ ] `docs/ops/hermes-weekly-cross-machine-parity-checklist.md` reflects the implemented macOS parity contract
   132|- [ ] Residual macOS-specific drift is documented rather than left implicit
   133|- [ ] Live macOS validation remains explicitly out of scope unless the host is reachable during execution
   134|- [ ] Plan review artifacts are posted before implementation begins
   135|
   136|---
   137|
   138|## Adversarial Review Summary
   139|
   140|| Provider | Verdict | Key findings |
   141||---|---|---|
   142|| Claude | MAJOR | missing consumer inventory, unresolved macOS path contract, and insufficient downstream readiness-compatibility coverage |
   143|| Codex | MAJOR | producer files are named but reader coverage/path-contract decisions are still implicit; live validation must be deferred explicitly |
   144|| Gemini | MAJOR | macOS/BSD compatibility gaps in downstream readiness tooling and hostname-mapping assumptions are unaddressed |
   145|
   146|**Overall result:** FAIL (re-draft required before implementation)
   147|
   148|Revisions made based on review:
   149|- none yet — plan must be revised to inventory all config consumers, define the canonical macOS workspace path/hostname mapping, and include downstream readiness compatibility checks before re-review
   150|
   151|---
   152|
   153|## Risks and Open Questions
   154|
   155|- Risk: the actual macOS machine may not currently be reachable from this Linux host, so repo-side parity scaffolding may land before live validation on the device.
   156|- Risk: `sync-agent-configs.sh` may rely on Linux-oriented assumptions not revealed until a real macOS dry run occurs.
   157|- Risk: the canonical workstation registry currently omits macOS entirely, so downstream tooling may require follow-up normalization once the entry is added.
   158|- Open: should macOS use `schedule_variant: none` permanently, or should launchd-backed weekly automation eventually be modeled in the same registry?
   159|- Open: what is the canonical macOS workspace root path (`/Users/<user>/workspace-hub` vs alternate location) and should that be templated or fixed in repo metadata?
   160|
   161|---
   162|
   163|## Complexity: T2
   164|
   165|**T2** — the work is bounded to workstation/readiness configuration, one possible sync-logic adjustment, documentation, and regression tests; it is cross-machine but not a large architectural redesign.
   166|

## Review Questions — answer ALL
1. Have the earlier MAJOR findings been materially addressed?
2. Is the implementation surface now complete enough for execution planning?
3. Are the revised tests sufficient and correctly targeted?
4. Is repo-side scope now appropriately bounded?
5. What residual risks remain, if any?
6. Final recommendation: ready for plan approval or still requires revision?

## Required output format
- Verdict: APPROVE, MINOR, or MAJOR
- Strengths
- Remaining gaps
- Residual risks
- Missing tests (if any)
- Scope creep concerns (if any)
- Weakest remaining assumption
- Most likely implementation failure mode
- Review confidence
warning: Codex's Linux sandbox uses bubblewrap and needs access to create user namespaces.
codex
Reviewing the revised plan against the actual repo surfaces it cites. I’m checking whether the claimed macOS evidence, consumer coverage, and downstream readiness scope are real enough to clear the prior MAJOR blockers.
2026-04-12T09:55:17.074724Z ERROR codex_core::tools::router: error=exec_command failed for `/bin/bash -lc "sed -n '1,220p' docs/ops/hermes-weekly-cross-machine-parity-checklist.md"`: CreateProcess { message: "Codex(Sandbox(Denied { output: ExecToolCallOutput { exit_code: 1, stdout: StreamOutput { text: \"\", truncated_after_lines: None }, stderr: StreamOutput { text: \"bwrap: loopback: Failed RTM_NEWADDR: Operation not permitted\\n\", truncated_after_lines: None }, aggregated_output: StreamOutput { text: \"bwrap: loopback: Failed RTM_NEWADDR: Operation not permitted\\n\", truncated_after_lines: None }, duration: 0ns, timed_out: false }, network_policy_decision: None }))" }
2026-04-12T09:55:17.197076Z ERROR codex_core::tools::router: error=exec_command failed for `/bin/bash -lc "sed -n '1,220p' scripts/readiness/harness-config.yaml"`: CreateProcess { message: "Codex(Sandbox(Denied { output: ExecToolCallOutput { exit_code: 1, stdout: StreamOutput { text: \"\", truncated_after_lines: None }, stderr: StreamOutput { text: \"bwrap: loopback: Failed RTM_NEWADDR: Operation not permitted\\n\", truncated_after_lines: None }, aggregated_output: StreamOutput { text: \"bwrap: loopback: Failed RTM_NEWADDR: Operation not permitted\\n\", truncated_after_lines: None }, duration: 0ns, timed_out: false }, network_policy_decision: None }))" }
2026-04-12T09:55:17.207081Z ERROR codex_core::tools::router: error=exec_command failed for `/bin/bash -lc "sed -n '1,220p' config/workstations/registry.yaml"`: CreateProcess { message: "Codex(Sandbox(Denied { output: ExecToolCallOutput { exit_code: 1, stdout: StreamOutput { text: \"\", truncated_after_lines: None }, stderr: StreamOutput { text: \"bwrap: loopback: Failed RTM_NEWADDR: Operation not permitted\\n\", truncated_after_lines: None }, aggregated_output: StreamOutput { text: \"bwrap: loopback: Failed RTM_NEWADDR: Operation not permitted\\n\", truncated_after_lines: None }, duration: 0ns, timed_out: false }, network_policy_decision: None }))" }
2026-04-12T09:55:17.217287Z ERROR codex_core::tools::router: error=exec_command failed for `/bin/bash -lc "sed -n '1,260p' scripts/readiness/nightly-readiness.sh"`: CreateProcess { message: "Codex(Sandbox(Denied { output: ExecToolCallOutput { exit_code: 1, stdout: StreamOutput { text: \"\", truncated_after_lines: None }, stderr: StreamOutput { text: \"bwrap: loopback: Failed RTM_NEWADDR: Operation not permitted\\n\", truncated_after_lines: None }, aggregated_output: StreamOutput { text: \"bwrap: loopback: Failed RTM_NEWADDR: Operation not permitted\\n\", truncated_after_lines: None }, duration: 0ns, timed_out: false }, network_policy_decision: None }))" }
codex
The shell sandbox is rejecting normal login-shell reads here, so I’m switching to plain non-login commands to inspect the cited files directly.
2026-04-12T09:55:28.766572Z ERROR codex_core::tools::router: error=exec_command failed for `/bin/sh -c "sed -n '1,220p' docs/ops/hermes-weekly-cross-machine-parity-checklist.md"`: CreateProcess { message: "Codex(Sandbox(Denied { output: ExecToolCallOutput { exit_code: 1, stdout: StreamOutput { text: \"\", truncated_after_lines: None }, stderr: StreamOutput { text: \"bwrap: loopback: Failed RTM_NEWADDR: Operation not permitted\\n\", truncated_after_lines: None }, aggregated_output: StreamOutput { text: \"bwrap: loopback: Failed RTM_NEWADDR: Operation not permitted\\n\", truncated_after_lines: None }, duration: 0ns, timed_out: false }, network_policy_decision: None }))" }
2026-04-12T09:55:28.927574Z ERROR codex_core::tools::router: error=exec_command failed for `/bin/sh -c "sed -n '1,220p' scripts/readiness/harness-config.yaml"`: CreateProcess { message: "Codex(Sandbox(Denied { output: ExecToolCallOutput { exit_code: 1, stdout: StreamOutput { text: \"\", truncated_after_lines: None }, stderr: StreamOutput { text: \"bwrap: loopback: Failed RTM_NEWADDR: Operation not permitted\\n\", truncated_after_lines: None }, aggregated_output: StreamOutput { text: \"bwrap: loopback: Failed RTM_NEWADDR: Operation not permitted\\n\", truncated_after_lines: None }, duration: 0ns, timed_out: false }, network_policy_decision: None }))" }
2026-04-12T09:55:28.933769Z ERROR codex_core::tools::router: error=exec_command failed for `/bin/sh -c "sed -n '1,220p' config/workstations/registry.yaml"`: CreateProcess { message: "Codex(Sandbox(Denied { output: ExecToolCallOutput { exit_code: 1, stdout: StreamOutput { text: \"\", truncated_after_lines: None }, stderr: StreamOutput { text: \"bwrap: loopback: Failed RTM_NEWADDR: Operation not permitted\\n\", truncated_after_lines: None }, aggregated_output: StreamOutput { text: \"bwrap: loopback: Failed RTM_NEWADDR: Operation not permitted\\n\", truncated_after_lines: None }, duration: 0ns, timed_out: false }, network_policy_decision: None }))" }
2026-04-12T09:55:28.949946Z ERROR codex_core::tools::router: error=exec_command failed for `/bin/sh -c "sed -n '1,260p' scripts/readiness/nightly-readiness.sh"`: CreateProcess { message: "Codex(Sandbox(Denied { output: ExecToolCallOutput { exit_code: 1, stdout: StreamOutput { text: \"\", truncated_after_lines: None }, stderr: StreamOutput { text: \"bwrap: loopback: Failed RTM_NEWADDR: Operation not permitted\\n\", truncated_after_lines: None }, aggregated_output: StreamOutput { text: \"bwrap: loopback: Failed RTM_NEWADDR: Operation not permitted\\n\", truncated_after_lines: None }, duration: 0ns, timed_out: false }, network_policy_decision: None }))" }
mcp: codex/list_mcp_resources started
mcp: codex/list_mcp_resources (completed)
codex
I can’t get local shell reads in this sandbox, so I’m verifying against the repository through the GitHub connector instead. That still lets me test whether the cited files and assumptions actually exist.
mcp: codex_apps/github_fetch_file started
mcp: codex_apps/github_fetch_file (completed)
mcp: codex_apps/github_fetch_file started
mcp: codex_apps/github_fetch_file (completed)
mcp: codex_apps/github_fetch_file started
mcp: codex_apps/github_fetch_file (completed)
mcp: codex_apps/github_fetch_file started
mcp: codex_apps/github_fetch_file (completed)
mcp: codex_apps/github_fetch_file started
mcp: codex_apps/github_fetch_file (completed)
mcp: codex_apps/github_fetch_file started
mcp: codex_apps/github_fetch_file (completed)
mcp: codex_apps/github_search started
mcp: codex_apps/github_search (completed)
codex
I’ve confirmed the macOS evidence sources are real. Now I’m checking whether the plan’s “inventory consumers” step is still too hand-wavy by identifying actual registry/readiness readers in the repo.
mcp: codex_apps/github_search started
mcp: codex_apps/github_search (completed)
mcp: codex_apps/github_search started
mcp: codex_apps/github_search (completed)
mcp: codex_apps/github_search started
mcp: codex_apps/github_search (completed)
mcp: codex_apps/github_search started
mcp: codex_apps/github_search (completed)
mcp: codex_apps/github_fetch_file started
mcp: codex_apps/github_fetch_file (completed)
mcp: codex_apps/github_fetch_file started
mcp: codex_apps/github_fetch_file (completed)
mcp: codex_apps/github_fetch_file started
mcp: codex_apps/github_fetch_file (completed)
mcp: codex_apps/github_fetch_file started
mcp: codex_apps/github_fetch_file (completed)
mcp: codex_apps/github_fetch_file started
mcp: codex_apps/github_fetch_file (completed)
codex
Verdict: MAJOR

**Strengths**
- The revised plan does materially improve the evidence base. The cited repo sources do in fact establish macOS scope and concrete machine facts:
  - [docs/ops/hermes-weekly-cross-machine-parity-checklist.md](/mnt/local-analysis/workspace-hub/docs/ops/hermes-weekly-cross-machine-parity-checklist.md) already names `macbook-portable` and documents expected macOS drift.
  - [config/agents/claude/memory-snapshots/network_machines.md](/mnt/local-analysis/workspace-hub/config/agents/claude/memory-snapshots/network_machines.md) records `Vamsees-MacBook-Air.local`, user `krishna`, and `~/workspace-hub/`.
  - [scripts/readiness/nightly-readiness.sh](/mnt/local-analysis/workspace-hub/scripts/readiness/nightly-readiness.sh) really is a relevant implementation surface and does contain BSD-sensitive logic such as `hostname -s`, `date -d`, `stat -c`, and `sed -i`.
- The plan now correctly pulls `scripts/readiness/nightly-readiness.sh` into scope.
- The pseudocode at least acknowledges consumer inventory and hostname/path-resolution as first-class concerns.
- The repo-side/live-host boundary is stated: live macOS validation remains deferred unless reachable.

**Remaining gaps**
- The core prior blocker is not fully closed: the canonical macOS path contract is still unresolved inside the plan itself. The resource intel cites `~/workspace-hub/`, but the plan’s own “Open” item still asks whether the canonical root is `/Users/<user>/workspace-hub` or something else. That means the plan has evidence but has not converted it into a decision.
- The consumer inventory is still not explicit enough for execution. The plan says `inventory_consumers()` but does not enumerate resulting scope decisions for actual readers already visible in repo sources:
  - [scripts/cron/setup-cron.sh](/mnt/local-analysis/workspace-hub/scripts/cron/setup-cron.sh)
  - [scripts/operations/workstation-status.sh](/mnt/local-analysis/workspace-hub/scripts/operations/workstation-status.sh)
  - [scripts/readiness/compare-harness-state.sh](/mnt/local-analysis/workspace-hub/scripts/readiness/compare-harness-state.sh)
  - [scripts/readiness/remediate-harness.sh](/mnt/local-analysis/workspace-hub/scripts/readiness/remediate-harness.sh)
- Because those readers are not dispositioned, the implementation surface is still ambiguous: are they intentionally unchanged, expected to pick up the new machine automatically, or expected to need follow-up issues? The plan needs that stated, not deferred to implementation discovery.
- The revised plan still contains a stale adversarial-review section saying “FAIL” and “Revisions made: none yet.” For a second-pass approval checkpoint, that is process-significant drift in the plan artifact itself.
- Hostname alias coverage is still underspecified in implementation terms. [scripts/_core/sync-agent-configs.sh](/mnt/local-analysis/workspace-hub/scripts/_core/sync-agent-configs.sh) currently resolves by substring matching workstation names, not hostname/alias fields. The plan notes this generally, but it does not state the exact intended matching contract.

**Residual risks**
- The most likely risk is that `macbook-portable` gets added to YAML files, but one or more registry/readiness consumers continue using old assumptions and silently ignore or mis-handle the new machine.
- `nightly-readiness.sh` portability work can easily widen from “make macOS report naming work” into “general BSD shell compatibility sweep” unless tightly scoped.
- If the path contract stays unresolved until implementation, tests may be written against one form (`~/workspace-hub`) while runtime code emits another (`/Users/krishna/workspace-hub`).

**Missing tests**
- Missing a test that `setup-cron.sh` maps the macOS hostname or alias to `schedule_variant: none` and does not fall through to `contribute`.
- Missing a test that `workstation-status.sh` parses a registry containing `macbook-portable` without regressing existing fleet output.
- Missing a test for the actual hostname/alias resolution contract in `sync-agent-configs.sh`; current proposed tests cover resolved path, but not the precise alias-to-canonical-key mapping behavior.
- Missing a test or explicit out-of-scope note for `compare-harness-state.sh` if macOS report artifacts are expected to exist but not yet participate in cross-machine comparison.

**Scope creep concerns**
- The nightly-readiness changes are the main scope-creep vector. “Audit/fix BSD/macOS compatibility” is broader than needed unless restricted to the code paths touched by macOS report generation and baseline updates.

**Weakest remaining assumption**
- That consumer inventory can remain a pseudocode step instead of being converted into explicit scope decisions before approval.

**Most likely implementation failure mode**
- A partial parity landing where `registry.yaml` and `harness-config.yaml` gain `macbook-portable`, but `setup-cron.sh`, `workstation-status.sh`, or `sync-agent-configs.sh` still derive behavior from legacy hostname conventions and therefore misclassify or ignore the Mac.

**Review confidence**
- High

Answers to the review questions:
1. Earlier MAJOR findings were only partially addressed. Evidence and downstream readiness awareness improved, but canonical path/alias decisions and explicit consumer disposition are still incomplete.
2. No. The implementation surface is improved but not complete enough for execution planning because reader impacts are still implicit.
3. No. The revised tests are useful but too concentrated on readiness/sync surfaces and miss key registry consumers.
4. Mostly, but the `nightly-readiness.sh` scope needs a tighter boundary to avoid turning into a broad BSD hardening task.
5. Residual risks are silent consumer breakage, unresolved path normalization, and accidental portability-scope expansion.
6. Final recommendation: still requires revision.
tokens used
290,096
Verdict: MAJOR

**Strengths**
- The revised plan does materially improve the evidence base. The cited repo sources do in fact establish macOS scope and concrete machine facts:
  - [docs/ops/hermes-weekly-cross-machine-parity-checklist.md](/mnt/local-analysis/workspace-hub/docs/ops/hermes-weekly-cross-machine-parity-checklist.md) already names `macbook-portable` and documents expected macOS drift.
  - [config/agents/claude/memory-snapshots/network_machines.md](/mnt/local-analysis/workspace-hub/config/agents/claude/memory-snapshots/network_machines.md) records `Vamsees-MacBook-Air.local`, user `krishna`, and `~/workspace-hub/`.
  - [scripts/readiness/nightly-readiness.sh](/mnt/local-analysis/workspace-hub/scripts/readiness/nightly-readiness.sh) really is a relevant implementation surface and does contain BSD-sensitive logic such as `hostname -s`, `date -d`, `stat -c`, and `sed -i`.
- The plan now correctly pulls `scripts/readiness/nightly-readiness.sh` into scope.
- The pseudocode at least acknowledges consumer inventory and hostname/path-resolution as first-class concerns.
- The repo-side/live-host boundary is stated: live macOS validation remains deferred unless reachable.

**Remaining gaps**
- The core prior blocker is not fully closed: the canonical macOS path contract is still unresolved inside the plan itself. The resource intel cites `~/workspace-hub/`, but the plan’s own “Open” item still asks whether the canonical root is `/Users/<user>/workspace-hub` or something else. That means the plan has evidence but has not converted it into a decision.
- The consumer inventory is still not explicit enough for execution. The plan says `inventory_consumers()` but does not enumerate resulting scope decisions for actual readers already visible in repo sources:
  - [scripts/cron/setup-cron.sh](/mnt/local-analysis/workspace-hub/scripts/cron/setup-cron.sh)
  - [scripts/operations/workstation-status.sh](/mnt/local-analysis/workspace-hub/scripts/operations/workstation-status.sh)
  - [scripts/readiness/compare-harness-state.sh](/mnt/local-analysis/workspace-hub/scripts/readiness/compare-harness-state.sh)
  - [scripts/readiness/remediate-harness.sh](/mnt/local-analysis/workspace-hub/scripts/readiness/remediate-harness.sh)
- Because those readers are not dispositioned, the implementation surface is still ambiguous: are they intentionally unchanged, expected to pick up the new machine automatically, or expected to need follow-up issues? The plan needs that stated, not deferred to implementation discovery.
- The revised plan still contains a stale adversarial-review section saying “FAIL” and “Revisions made: none yet.” For a second-pass approval checkpoint, that is process-significant drift in the plan artifact itself.
- Hostname alias coverage is still underspecified in implementation terms. [scripts/_core/sync-agent-configs.sh](/mnt/local-analysis/workspace-hub/scripts/_core/sync-agent-configs.sh) currently resolves by substring matching workstation names, not hostname/alias fields. The plan notes this generally, but it does not state the exact intended matching contract.

**Residual risks**
- The most likely risk is that `macbook-portable` gets added to YAML files, but one or more registry/readiness consumers continue using old assumptions and silently ignore or mis-handle the new machine.
- `nightly-readiness.sh` portability work can easily widen from “make macOS report naming work” into “general BSD shell compatibility sweep” unless tightly scoped.
- If the path contract stays unresolved until implementation, tests may be written against one form (`~/workspace-hub`) while runtime code emits another (`/Users/krishna/workspace-hub`).

**Missing tests**
- Missing a test that `setup-cron.sh` maps the macOS hostname or alias to `schedule_variant: none` and does not fall through to `contribute`.
- Missing a test that `workstation-status.sh` parses a registry containing `macbook-portable` without regressing existing fleet output.
- Missing a test for the actual hostname/alias resolution contract in `sync-agent-configs.sh`; current proposed tests cover resolved path, but not the precise alias-to-canonical-key mapping behavior.
- Missing a test or explicit out-of-scope note for `compare-harness-state.sh` if macOS report artifacts are expected to exist but not yet participate in cross-machine comparison.

**Scope creep concerns**
- The nightly-readiness changes are the main scope-creep vector. “Audit/fix BSD/macOS compatibility” is broader than needed unless restricted to the code paths touched by macOS report generation and baseline updates.

**Weakest remaining assumption**
- That consumer inventory can remain a pseudocode step instead of being converted into explicit scope decisions before approval.

**Most likely implementation failure mode**
- A partial parity landing where `registry.yaml` and `harness-config.yaml` gain `macbook-portable`, but `setup-cron.sh`, `workstation-status.sh`, or `sync-agent-configs.sh` still derive behavior from legacy hostname conventions and therefore misclassify or ignore the Mac.

**Review confidence**
- High

Answers to the review questions:
1. Earlier MAJOR findings were only partially addressed. Evidence and downstream readiness awareness improved, but canonical path/alias decisions and explicit consumer disposition are still incomplete.
2. No. The implementation surface is improved but not complete enough for execution planning because reader impacts are still implicit.
3. No. The revised tests are useful but too concentrated on readiness/sync surfaces and miss key registry consumers.
4. Mostly, but the `nightly-readiness.sh` scope needs a tighter boundary to avoid turning into a broad BSD hardening task.
5. Residual risks are silent consumer breakage, unresolved path normalization, and accidental portability-scope expansion.
6. Final recommendation: still requires revision.
