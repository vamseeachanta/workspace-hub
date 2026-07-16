# Plan for #3555: Persistent goals and native Codex statusline machine pilot

> **Status:** draft
> **Complexity:** T3
> **Date:** 2026-07-16
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/3555
> **Client:** N/A
> **Lane:** lane:claude
> **Execution mode:** parallel-readonly for planning and review; single-lane for the `ace-win-2` pilot; parallel-worktree only for later approved, disjoint rollout validation
> **Review artifacts:** round 1 `scripts/review/results/2026-07-16-plan-3555-{claude,codex,gemini}.md`; round 2 `scripts/review/results/2026-07-16-plan-3555-r2-codex.md`

---

## Resource Intelligence Summary

### Existing repo code

- `config/agents/codex/config.toml` declares an obsolete root `[status_line]` table with underscore item names. Current Codex uses `[tui] status_line = [...]` with fixed hyphenated item identifiers.
- `C:\Users\vamseea\.codex\config.toml` currently uses `[tui] status_line = ["model-with-reasoning", "current-dir", "weekly-limit"]`; it omits remaining context and the five-hour window.
- `scripts/_core/sync-agent-configs.sh` owns machine config merge behavior, but its managed-section parser recognizes `[status_line]`, so it cannot safely own the current `[tui].status_line` key without revision.
- `config/agents/claude/settings.json` has no machine-global `statusLine`. Project `.claude/settings.json` invokes `.claude/statusline-combined.sh`, while `scripts/_core/sync_statusline.sh` distributes only `.claude/statusline-command.sh`; these paths produce split behavior across repos and machines.
- `.claude/hooks/gsd-statusline.js` renders a current todo or GSD phase. It does not represent the provider-native goal condition.
- `scripts/readiness/collect-equality.sh`, `scripts/readiness/collect-equality.ps1`, and `scripts/readiness/build-equality-matrix.py` provide the canonical machine evidence pipeline. The current matrix reports 4 of 5 active machines; `gpu-claw` has no evidence file.
- `config/workstations/registry.yaml` and `scripts/readiness/harness-config.yaml` disagree about the roster and record `ace-win-2` at `D:\workspace-hub`, while this pilot runs at `C:\ws\workspace-hub`.

### Product contracts

- Current Codex documentation defines `goals` as stable, `/goal` as the persistent task-goal command, `/statusline` as the native footer configurator, `/status` as the session/context view, and `/usage` as the account-usage view.
- Current Codex configuration defines the footer as `[tui] status_line = [...]`. The pilot will use only item identifiers accepted by the installed CLI, including `model-with-reasoning`, `current-dir`, `context-remaining`, `five-hour-limit`, and `weekly-limit` when the interactive selector confirms them.
- Current Claude Code documentation defines `/goal` as a native completion condition with an `◎ /goal active` indicator and status view. It defines `statusLine` as a user- or project-settings command that receives session JSON and may display context and cost data.
- Neither provider contract establishes arbitrary goal text as a Codex footer item. The implementation will use native goal/progress UI and will not fabricate a custom Codex footer field.

### Standards and governance

- `AGENTS.md` and `.claude/skills/coordination/issue-planning-mode/SKILL.md` require Issue → Resource Intel → Plan → adversarial review → user approval → TDD implementation → code review → close.
- `config/agents/SHARED_SOUL.md` is the canonical cross-provider instruction source. A goal-use rule will be added there and materialized through existing runtime builders, rather than copied independently into Claude and Codex harness files.
- `docs/standards/CONTROL_PLANE_CONTRACT.md` will remain the control-plane boundary if present at implementation; if the exact path differs on the reviewed commit, implementation will use the live canonical contract and record the substitution.

### Documents consulted

- [#3555](https://github.com/vamseeachanta/workspace-hub/issues/3555) defines the Claude/Codex pilot and the three distinct predicates: goal attachment, visible goal/progress, and usage/context telemetry.
- [#2887](https://github.com/vamseeachanta/workspace-hub/issues/2887) is the parent machine/provider-equivalence epic.
- [#2893](https://github.com/vamseeachanta/workspace-hub/issues/2893) contains approved, branch-only statusline-provider coverage, but its locked premise that Codex has no native statusline is stale and its implementation commit is not on `origin/main`.
- [#2844](https://github.com/vamseeachanta/workspace-hub/issues/2844) specifies Codex five-hour and staleness visibility; #3555 will use native five-hour display and will not silently absorb unrelated cache-refresh work.
- `docs/session-handoffs/2026-07-13-codex-yolo-config-exit.md` records recent machine-local Codex configuration work and reinforces preservation of local-only settings during sync.
- Drive-file search for `agent goal statusline machine equivalence` returns no relevant prior deliverable. Its major indexes report `unreachable` on this Windows host; this is a coverage gap, not evidence that no external artifact exists.
- Official Claude Code references: [goal mode](https://code.claude.com/docs/en/goal) and [custom status line](https://code.claude.com/docs/en/statusline).
- Official [Codex manual](https://developers.openai.com/codex/codex-manual.md) sections consulted through the current OpenAI manual helper: configuration reference, `/goal`, `/statusline`, `/status`, and `/usage`.

### Gaps identified

- No canonical cross-provider rule requires a meaningful native goal after a substantive interactive request begins.
- No single deployment path installs consistent Claude statusline behavior machine-wide and across sibling repos.
- The canonical Codex template and sync tests do not express the current `[tui].status_line` schema.
- No matrix evidence separates installed goal contract, visible native goal capability, and context/usage footer capability.
- No current fleet report supports an “all machines” claim: one active machine is missing, two roster entries disagree, and the Windows checkout path is stale.

### Evidence

**Issue statuses** (verified 2026-07-16 via `gh issue view`):

- `#3555` — OPEN, `status:needs-plan`, `lane:claude` — persistent goals and native Codex statusline pilot.
- `#2893` — OPEN, `status:plan-approved` — branch-only provider-coverage implementation; no implementation PR is present.
- `#2887` — OPEN — parent machine/provider-equivalence epic.

**Current Codex probes** (2026-07-16, `ace-win-2`):

```text
$ codex --version
codex-cli 0.144.5

$ codex features list | select goals
goals  stable  true

$ ~/.codex/config.toml [tui]
status_line = ["model-with-reasoning", "current-dir", "weekly-limit"]
```

**Machine coverage probe** (2026-07-16):

```text
matrix roster: 5 active + 2 unreachable
active evidence present: 4/5
missing active report: gpu-claw
registry-only: gali-linux-compute-1
harness-only: home-win
live ace-win-2 checkout: C:\ws\workspace-hub
recorded ace-win-2 checkout: D:\workspace-hub
```

**Reproduction proofs:**

```text
$ compare config/agents/codex/config.toml with ~/.codex/config.toml
canonical: [status_line] enabled/items
live 0.144.5: [tui] status_line = [...]

$ inspect live footer item set
["model-with-reasoning", "current-dir", "weekly-limit"]
```

- Reproduced at: 2026-07-16T10:55Z
- Failure mode matches the issue: **YES** — the repo template is schema-stale and the live footer omits remaining context and five-hour usage.
- Distinct sources: 15.

---

## Scope and Semantic Contract

1. **Substantive interactive session:** a Claude Code or Codex CLI session will become substantive after the user requests multi-step work, issue work, implementation, monitoring, or another task with a verifiable completion condition. Read-only one-shot questions, status checks, and trivial commands will not be forced into a synthetic goal.
2. **Goal authorization and attachment:** after a substantive request is known, the runtime instruction will consult [#2695](https://github.com/vamseeachanta/workspace-hub/issues/2695), the current weekly picklist, and `.claude/rules/goal-invocation.md` before invoking the provider-native goal mechanism. A pre-approval planning goal may perform resource intelligence, planning, and plan review only and will stop at the user approval gate. An execution goal will require live `status:plan-approved` evidence, the local approval marker, and runner allocation. An explicit user override will be recorded. Idle sessions and trivial/read-only one-shots may display no goal.
3. **Goal visibility:** Claude will use its native `◎ /goal active` indicator/status; Codex will use native goal/progress UI. The plan will not require arbitrary goal text inside Codex's fixed footer.
4. **Telemetry visibility:** provider statusline/footer configuration will show context and usage independently of the goal surface.
5. **Non-interactive boundary:** `claude -p` and `codex exec` have no persistent TUI footer. They will receive the goal condition in their invocation/task metadata and will be graded as non-visual, not falsely marked visually equivalent.
6. **Fleet claim:** each machine will remain `PENDING`, `MISSING-EVIDENCE`, or `UNREACHABLE` until live evidence from that machine supports the row. Configuration intent alone will not produce `EQUAL`.

---

## Artifact Map

| Artifact | Path |
|---|---|
| Canonical plan | `docs/plans/2026-07-16-issue-3555-goal-statusline-machine-pilot.md` |
| Human reviewer | `docs/reports/2026-07-16-issue-3555-goal-statusline-plan.html` |
| Goal-use rule source | `config/agents/SHARED_SOUL.md` |
| Goal invocation gate | `.claude/rules/goal-invocation.md` |
| Generated runtimes | `config/agents/claude/SOUL.runtime.md`, `config/agents/codex/AGENTS.runtime.md`, `config/agents/codex/SOUL.runtime.md` |
| Runtime builder | `scripts/agents/build-soul-runtime.sh` |
| Claude machine settings | `config/agents/claude/settings.json` |
| Claude renderer | `config/agents/claude/statusline.mjs` |
| Codex machine config | `config/agents/codex/config.toml` |
| Config deployment | `scripts/_core/sync-agent-configs.sh` |
| Claude sibling deployment | `scripts/_core/sync_statusline.sh` |
| Machine setup verification | `scripts/setup/verify-setup.sh` |
| Equality collector | `scripts/readiness/collect-equality.sh` |
| Equality renderer | `scripts/readiness/build-equality-matrix.py` |
| Pilot attestation | `docs/reports/2026-07-16-issue-3555-ace-win-2-session-ux.json` |
| Sync tests | `scripts/_core/tests/test_sync_agent_configs.sh`, `scripts/_core/tests/test_sync_agent_helpers.sh` |
| Statusline tests | `tests/statusline/` |
| Equality tests | `tests/readiness/test_collect_equality.py`, `tests/readiness/test_collect_equality_ps1_schema.py`, `tests/readiness/test_build_equality_matrix.py` |
| Plan reviews | `scripts/review/results/2026-07-16-plan-3555-{claude,codex,gemini}.md`, then `scripts/review/results/2026-07-16-plan-3555-r*-{claude,codex,gemini}.md` |
| Code reviews | `scripts/review/results/2026-07-16-code-3555-r*-{claude,codex,gemini}.md` |

---

## Deliverable

The repository will provide a tested, current-schema, machine-deployable Claude/Codex session-UX contract in which substantive interactive work attaches a native goal, native goal progress remains visible, Codex shows remaining context plus five-hour and weekly headroom, and the equality matrix reports per-machine evidence without overstating fleet coverage.

---

## Proposed Implementation

### Phase 0 — Empirical provider attestation

Before any interactive attestation is produced, implementation will add schema/privacy validator tests, observe them fail, implement the validator, and observe them pass. It will then run fresh interactive Claude and Codex sessions on `ace-win-2` in a disposable test repository. A named human verifier will use a PTY-backed session or direct TUI observation, record the provider UI result, and write it through the validated attestation path to `docs/reports/2026-07-16-issue-3555-ace-win-2-session-ux.json`. It will:

```text
record provider and CLI version
start a bounded goal with an objective that completes without repo mutation
verify native active-goal indicator/status is visible
open the native status/statusline selectors in a PTY-backed or directly observed TUI
record the exact accepted footer item identifiers
clear the bounded goal
store only provider version, accepted footer IDs, visibility booleans, timestamp, and verifier method
reject goal text, transcripts, token values, credentials, client identifiers, and private task text
stop if either provider lacks the required native goal surface
```

If native Codex goal progress is not persistently visible, the implementation will return #3555 to plan review rather than substituting an unsupported custom footer.

### Phase 1 — Goal contract and generated runtimes

`config/agents/SHARED_SOUL.md` and `.claude/rules/goal-invocation.md` will define one compatible must-fire contract. Every substantive goal will first validate catalog/picklist routing or record an explicit user override. A pre-approval planning goal will be bounded to intelligence, planning, and review and will stop at user approval; an execution goal will require the existing approval and runner predicates. Goals will never widen authority, invent completion criteria, or apply to trivial/read-only one-shots. `scripts/agents/build-soul-runtime.sh` and its tests will verify that `config/agents/claude/SOUL.runtime.md`, `config/agents/codex/AGENTS.runtime.md`, and `config/agents/codex/SOUL.runtime.md` inherit the rule exactly once.

### Phase 2 — Native statusline configuration and safe sync

The Codex template will move to current syntax:

```toml
[tui]
status_line = [
  "model-with-reasoning",
  "current-dir",
  "context-remaining",
  "five-hour-limit",
  "weekly-limit"
]
status_line_use_colors = true
```

The exact list will be pinned to the Phase-0 accepted identifiers. `sync-agent-configs.sh` will manage only `tui.status_line` and `tui.status_line_use_colors`; it will preserve unrelated `[tui]` keys, plugin state, trust entries, approval/sandbox settings, and machine-local model choices.

Claude user settings will point to one installed, home-relative cross-platform Node renderer sourced from `config/agents/claude/statusline.mjs`. The same synthetic JSON fixture will be executed through Linux Bash, Windows Git Bash, and Windows PowerShell. Installation will fail atomically before config replacement when Node or the installed renderer is unavailable. `sync-agent-configs.sh` and `sync_statusline.sh` will converge on this source. Project-local GSD enrichment may remain optional, but model/context/usage and native `/goal` visibility will remain consistent across machines.

### Phase 3 — Setup, reconciliation, and fail-closed verification

`scripts/setup/new-machine-setup.sh` and the scheduled `scripts/maintenance/update-harness-tools.sh` path will call the canonical config sync rather than duplicate it. Tests will prove neither path writes the legacy Claude `statusBarEnabled` setting or bypasses the installed renderer. `verify-setup.sh` will parse the effective JSON/TOML and validate semantic fields rather than grepping for a setting name. Dry-run will remain side-effect free; failed validation will preserve the prior config atomically.

### Phase 4 — Equality evidence and `ace-win-2` pilot

The equality schema will add separate dimensions:

```text
session_goal_policy      = installed authorization/attachment rule
claude_goal_surface      = native goal capability + fresh visibility attestation
codex_goal_surface       = stable goal capability + fresh visibility attestation
claude_statusline_config = valid installed renderer + cross-shell verification
codex_statusline_config  = accepted native footer items + current config schema
```

Collector evidence will include provider version, configuration hash, semantic capability flags, and freshness. It will consume only the attestation schema and will fail closed if forbidden content is present; it will not inspect or publish goal text. Builder grading will use `PARITY`, `DIVERGES`, `MISSING-EVIDENCE`, `STALE-CHECKOUT`, and `UNREACHABLE` consistently with existing rows.

The pilot will update only `ace-win-2` after tests and code review pass. Fleet rollout will remain a separately observable step: each active machine will run config sync, fresh-session verification, and equality collection. Missing `gpu-claw`, unreachable machines, registry drift, and stale checkout paths will remain explicit rather than being normalized away.

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Modify | `config/agents/SHARED_SOUL.md` | define the cross-provider substantive-session goal contract |
| Modify | `.claude/rules/goal-invocation.md` | reconcile visible-goal policy with catalog, picklist, approval, and runner gates |
| Modify | `config/agents/claude/SOUL.runtime.md`, `config/agents/codex/AGENTS.runtime.md`, `config/agents/codex/SOUL.runtime.md` | materialize the canonical rule through `scripts/agents/build-soul-runtime.sh` |
| Modify | `config/agents/codex/config.toml` | adopt current native `[tui].status_line` syntax |
| Modify | `config/agents/claude/settings.json` | install one machine-global Claude statusline command |
| Create | `config/agents/claude/statusline.mjs` | provide one cross-platform, repo-managed Claude renderer |
| Modify | `scripts/_core/sync-agent-configs.sh` | merge current Codex TUI keys and Claude settings atomically |
| Modify | `scripts/_core/sync_statusline.sh` | remove split-brain sibling behavior and use the canonical Claude source |
| Modify | `scripts/setup/verify-setup.sh` | validate effective goal/statusline semantics |
| Modify | `scripts/setup/new-machine-setup.sh`, `scripts/maintenance/update-harness-tools.sh` | call the canonical sync path without duplicating config logic |
| Modify | `scripts/readiness/collect-equality.sh` | emit the five new goal/statusline dimensions |
| Modify | `scripts/readiness/build-equality-matrix.py` | render and remediate the new dimensions |
| Modify | `scripts/_core/tests/test_sync_agent_configs.sh` | TDD current-schema merge and local-key preservation |
| Modify | `scripts/_core/tests/test_sync_agent_helpers.sh` | TDD helper/install convergence |
| Modify/Create | `tests/statusline/*` | TDD portable Claude output and Codex item contract |
| Modify | `tests/readiness/test_collect_equality.py` | TDD collector evidence and fail-closed states |
| Modify | `tests/readiness/test_collect_equality_ps1_schema.py` | keep Windows delegated schema exact |
| Modify | `tests/readiness/test_build_equality_matrix.py` | TDD row rendering, freshness, and remediation |
| Create | `docs/reports/2026-07-16-issue-3555-ace-win-2-session-ux.json` | retain de-identified pilot capability evidence |
| Update | `docs/plans/README.md` | index this plan |
| Create | `docs/reports/2026-07-16-issue-3555-goal-statusline-plan.html` | provide the human review surface |

No machine registry or checkout-path mutation will occur in this issue unless the user separately approves a scoped revision; #3555 will report the drift and use it to constrain coverage claims.

---

## TDD Test List

| Test | Verification | Expected result |
|---|---|---|
| `test_codex_template_uses_current_tui_status_line` | template parses with `[tui]` array and accepted IDs | pass only for current syntax |
| `test_codex_sync_replaces_only_managed_tui_keys` | local plugins, trust, sandbox, model, terminal title, and other TUI keys survive | byte/semantic preservation outside managed keys |
| `test_codex_sync_migrates_legacy_status_line_atomically` | legacy table and current key do not coexist | one valid current key |
| `test_codex_invalid_item_fails_before_replace` | unsupported footer ID enters template | nonzero; original target unchanged |
| `test_claude_user_settings_install_portable_statusline` | Linux Bash, Windows Git Bash, and Windows PowerShell run the same fixture | identical valid output and home-relative executable resolution |
| `test_claude_statusline_install_fails_without_node` | renderer dependency absent | nonzero; prior settings and renderer unchanged |
| `test_claude_project_and_sibling_paths_use_canonical_source` | workspace-hub and fixture sibling repo | consistent model/context/usage contract |
| `test_goal_rule_materializes_for_claude_and_codex` | build runtimes from SHARED_SOUL | both contain the rule once |
| `test_goal_rule_preserves_approval_and_trivial_boundaries` | rule contract fixture | no auto-approval and no synthetic trivial goal |
| `test_goal_rule_requires_catalog_picklist_and_runner_predicates` | planning and execution fixtures | planning stops at approval; execution requires approval marker and runner |
| `test_attestation_schema_and_privacy_fail_before_pilot` | no validator implementation yet; fixtures include allowed and forbidden fields | observed red before Phase-0 evidence generation |
| `test_setup_dry_run_has_no_side_effects` | clean temp HOME | no created/changed config |
| `test_setup_failure_preserves_prior_config` | invalid staged template | original hashes unchanged |
| `test_new_machine_setup_delegates_to_canonical_sync` | setup fixture with command spy | canonical sync called; no direct `statusBarEnabled` write |
| `test_scheduled_update_delegates_to_canonical_sync` | maintenance fixture with command spy | canonical sync called; no legacy settings mutation |
| `test_collector_emits_session_ux_dimensions` | Linux fixture | exact five-row schema with semantic evidence |
| `test_windows_collector_schema_matches_shell` | PowerShell delegated fixture | exact same dimension names |
| `test_matrix_never_upgrades_missing_live_evidence` | config present but no fresh pilot evidence | `MISSING-EVIDENCE`, not `PARITY` |
| `test_matrix_renders_goal_and_statusline_rows` | mixed fleet fixture | correct cells, group count, and remediation |
| `test_goal_text_is_not_collected` | evidence fixture contains synthetic objective | output omits objective/transcript content |
| `test_attestation_rejects_forbidden_content` | fixture includes goal text, token value, credential, or client/private text | fail closed before evidence publication |
| `test_codex_template_item_ids_match_validated_attestation` | schema-valid PTY/direct-observation fixture from installed CLI | template IDs exactly match the accepted IDs recorded by the named verifier |

Tests will be written and observed failing before implementation changes. In particular, the attestation validator and privacy rejection tests will turn red before any Phase-0 JSON is created. Codex offers no noninteractive strict-config/statusline rendering command in CLI `0.144.5`, so TUI rendering will be a named, timestamped PTY/direct-observation attestation whose accepted IDs are then checked automatically against the template. The focused suite will run before each multi-file edit; the full relevant suite and legal diff scan will run before review.

---

## Acceptance Criteria

- [ ] Schema/privacy tests fail first, then Phase-0 evidence identifies exact Claude and Codex native goal UI and accepted Codex footer IDs on `ace-win-2` through a named PTY/direct-observation verifier.
- [ ] Substantive interactive Claude/Codex tasks attach native goals only after catalog/picklist routing or a recorded user override; planning goals stop at approval and execution goals require approval plus runner evidence.
- [ ] Claude native goal indicator/status remains visible while the goal is active.
- [ ] Codex native goal/progress remains visible while the goal is active; no custom footer capability is claimed.
- [ ] Codex footer shows model/reasoning, directory/project, remaining context, five-hour limit, and weekly limit with current accepted identifiers.
- [ ] Config sync preserves all unrelated machine-local keys and fails atomically on invalid input.
- [ ] Claude global/project/sibling statusline paths converge on one repo-tracked source.
- [ ] Machine setup and scheduled harness reconciliation call the same config sync path.
- [ ] Equality collection and rendering expose separate goal-policy, Claude/Codex goal-surface, and Claude/Codex statusline-config rows.
- [ ] `ace-win-2` pilot passes fresh interactive verification and publishes fresh local evidence.
- [ ] Fleet report enumerates all 5 active and 2 unreachable roster entries and names registry disagreement; it makes no unsupported “all machines” claim.
- [ ] Focused sync/statusline/readiness suites pass; full affected test suites show no regression.
- [ ] `scripts/legal/legal-sanity-scan.sh --diff-only` passes.
- [ ] T3 adversarial code/artifact review has no unresolved MAJOR finding.
- [ ] Completeness score and owner-only completeness label meet the closure threshold before closing #3555.
- [ ] A GitHub implementation summary comment is posted before closure.

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | UNAVAILABLE | CLI OAuth is expired; fanout retained the unavailable artifact. |
| Codex | MAJOR (r1, r2) | Round 1 found the goal-gate conflict, Windows coverage gap, and unnamed evidence. Round 2 found attestation-before-test sequencing, setup-path bypass coverage, and a nonexistent noninteractive Codex rendering probe. This revision addresses all six findings. |
| Gemini | UNAVAILABLE | Noninteractive authentication is unavailable; fanout retained the unavailable artifact. |

**Overall result:** FAIL / REVISED — two Codex rounds found blocking defects; the main session applied the distinct round-2 findings inline per the r3 loop-break rule. Provider-diversity requirements remain unmet while Claude and Gemini authentication are unavailable; implementation remains blocked and the plan is not approval-ready.

---

## Risks and Open Questions

- **Native UI risk:** Codex may expose a goal status view without a continuously visible goal row. Phase 0 will fail closed and return the plan for user decision instead of inventing a footer field.
- **Version skew:** footer item IDs may differ across installed Codex versions. The collector will report version capability, and rollout will require the supported baseline or an explicit expected divergence.
- **Merge risk:** replacing the root legacy table with `[tui]` can overwrite unrelated TUI settings if implemented as whole-table replacement. Tests will enforce key-level ownership.
- **Claude precedence risk:** project settings can override user settings. Tests will cover workspace-hub, a sibling repo, and a repo without project settings.
- **Hot-path risk:** statusline scripts execute frequently. The Claude renderer will avoid network access and unbounded Git commands; cached quota data will remain bounded and visibly stale where applicable.
- **Privacy risk:** goals may contain client or private details. Equality evidence will record only capability/state booleans and hashes, never goal text or transcripts.
- **Authorization risk:** making goals ubiquitous could bypass the existing `/goal` catalog, picklist, approval, and runner gates. The reconciled rule and tests will preserve each predicate and bound pre-approval goals to planning/review.
- **Windows runtime risk:** Claude selects Git Bash when present and PowerShell otherwise. One Node renderer and three-shell fixture execution will keep behavior equivalent without maintaining divergent shell implementations.
- **Fleet drift:** missing reports, roster mismatch, and incorrect Windows checkout paths prevent a fleet-complete claim. This issue will surface them and will not opportunistically relocate repos.
- **Stranded branch risk:** #2893 implementation is not on main. #3555 will reuse compatible concepts only after comparing its branch; it will not merge or close #2893 implicitly.
- **User decision after Phase 0:** if native Codex does not keep goal progress continuously visible, the user must choose between accepting `/goal`/status visibility or filing an upstream product request. The approved plan will not authorize an unsupported emulation.

---

## Complexity: T3

The change crosses provider-native UI contracts, generated runtime instructions, atomic user-config merge logic, Windows/Linux deployment, and fleet evidence. It requires a three-provider plan review, TDD across shell/Python/PowerShell fixtures, an `ace-win-2` pilot, and code-stage T3 review.
