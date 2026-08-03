# Plan for #3555: Fleet-wide Codex requirements, trusted-repo YOLO, goals, and statuslines

> **Status:** draft
> **Complexity:** T3
> **Date:** 2026-08-02
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/3555
> **Client:** N/A
> **Lane:** lane:claude
> **Execution mode:** immediate attempted fleet rollout after plan approval, TDD implementation, and code review; no canary
> **Review artifacts:** historical `scripts/review/results/2026-07-16-plan-3555-{claude,codex,gemini}.md` and `2026-07-16-plan-3555-r2-codex.md`; fresh `scripts/review/results/2026-08-02-plan-3555-r3-{claude,codex,agy}.md`

> For agentic workers: follow this plan task by task. Write each named test first, observe the relevant failure, implement only enough to pass, rerun the focused and regression suites, and use pathspec commits. The user approval gate remains mandatory even when Codex runs with `--yolo`.

**Goal:** Every reachable, Codex-capable workstation and trusted repo will receive a repo-managed Codex baseline that enables default-mode requirement questions, persistent goals, multi-agent support, hooks, live web search, useful TUI telemetry, and a trusted-repo `--yolo` launcher with an explicit safe escape path; Claude goal/statusline behavior will converge under the same issue.

**Architecture:** Repo-tracked templates will remain canonical. A semantic, key-level merger will update only owned settings in `~/.codex/config.toml`. A cross-platform launcher will add `--yolo` only when the current Git root matches an attested trusted repo root, while `codex-safe` will always invoke the real CLI without the flag. Setup, update, verification, and equality collection will share the same installer and will report per-machine evidence without converting missing or unreachable machines into success.

**Tech stack:** Bash, Python 3 standard library, TOML, JSON, Node.js for the existing Claude renderer, Windows `.cmd` launchers, pytest, shell test harnesses, GitHub Actions-compatible checks.

---

## Global Constraints

- Implementation will not begin until fresh T3 adversarial plan review has no unresolved MAJOR finding and the user applies the approval gate.
- Tests will precede implementation in every task.
- The rollout will target all live, reachable Codex-capable machines in one wave; it will not use a canary. A machine will remain `UNREACHABLE`, `MISSING-EVIDENCE`, or `DIVERGES` until direct evidence supports equality.
- `--yolo` will bypass Codex sandbox/approval prompts only inside an exact trusted Git root. It will not bypass issue, plan, user-approval, TDD, review, legal, secret, or merge gates.
- The launcher will provide `codex-safe` and `CODEX_REAL_BIN` escape seams and will prevent wrapper recursion.
- The merger will preserve auth, trust, MCP/plugin, project, model, and machine-local keys outside the explicit owned-key set.
- Native Codex memories and automatic approval reviewers will remain excluded because they conflict with the repo-managed memory/approval model.
- The implementation will pin a CLI version only after the feature probe proves that exact version supports `default_mode_request_user_input`; the current candidate is `0.146.0`.
- Human-facing review material will remain HTML; lifecycle and harness artifacts will remain Markdown/TOML/scripts.

## Resource Intelligence Summary

### Existing repo code

- `config/agents/codex/config.toml` currently declares `model = "gpt-5.5"`, medium reasoning, and obsolete `[status_line]` syntax. It does not declare the approved feature baseline.
- `scripts/_core/sync-agent-configs.sh` currently parses `[status_line]` and performs managed-key sanitation. It will need semantic support for root keys plus `[features]`, `[agents]`, and `[tui]` without replacing unrelated tables.
- `scripts/install/codex-pin.env` currently pins `0.123.0`; `scripts/install/pin-codex.sh` installs that exact pin, and `scripts/setup/verify-setup.sh` reports drift against it.
- `scripts/setup/new-machine-setup.sh` already installs the Codex pin but does not install a repo-managed launcher or invoke canonical config sync afterward.
- `scripts/maintenance/update-harness-tools.sh` updates Codex independently and does not converge launcher/config state.
- `/home/vamsee/.local/bin/codex` on the planning host is an untracked Bash wrapper that unconditionally appends `--yolo`; no repository artifact owns or verifies it.
- `scripts/_core/sync_statusline.sh` and the Claude settings/statusline paths remain split, so the original #3555 Claude convergence scope will remain in this plan.
- `scripts/readiness/collect-equality.sh`, `collect-equality.ps1`, and `build-equality-matrix.py` form the existing per-machine evidence pipeline.

### Product and configuration contract

- Codex CLI `0.146.0` exposes `default_mode_request_user_input` as an under-development feature whose source description is “Allow request_user_input in Default collaboration mode.”
- The current stable configuration reference documents `plan_mode_reasoning_effort`, `personality`, `web_search`, `[features]`, `[agents]`, and `[tui].status_line`/`resume_cwd`.
- `goals`, `multi_agent`, and `hooks` are stable in the inspected CLI; declaring them explicitly will make fleet intent auditable.
- The supported footer identifiers selected for this work are `model-with-reasoning`, `context-remaining`, `current-dir`, `five-hour-limit`, and `weekly-limit`.
- `status_line_use_colors` does not appear in the current official manual and will not be introduced.
- Native goals will remain distinct from TUI telemetry; the plan will not fabricate arbitrary goal text as a footer field.

### Fleet and governance sources

- `config/workstations/registry.yaml` declares Codex for `ace-win-1` and `ace-win-2`, but not for `ace-linux-1`; the current planning host runs Codex `0.146.0`, so the declared roster is incomplete.
- [#3555](https://github.com/vamseeachanta/workspace-hub/issues/3555) is OPEN with `status:needs-plan` and retains the original persistent-goal/statusline objective.
- [#2887](https://github.com/vamseeachanta/workspace-hub/issues/2887) is the parent workstation/provider-equivalence epic.
- `config/agents/SHARED_SOUL.md` and `.claude/rules/goal-invocation.md` will remain the policy sources for goal authorization; `--yolo` will not expand their authority.
- `docs/standards/CONTROL_PLANE_CONTRACT.md` will remain the runtime/config boundary.
- The 2026-07-16 #3555 plan and reviews provide historical defect evidence but do not authorize the materially expanded 2026-08-02 fleet scope.

### External sources consulted

- Official OpenAI configuration reference: https://developers.openai.com/codex/config-reference
- Official Codex feature registry source: https://github.com/openai/codex/blob/main/codex-rs/features/src/lib.rs
- Official Codex manual: https://developers.openai.com/codex/codex-manual.md
- Official Claude Code goal and statusline references: https://code.claude.com/docs/en/goal and https://code.claude.com/docs/en/statusline
- Drive-file search from the July planning round returned no relevant deliverable; inaccessible drive indexes remain a coverage limitation, not negative proof.

### Gaps identified

- No repo-managed cross-platform Codex launcher will enforce trusted-root `--yolo`, recursion safety, argument preservation, and a non-YOLO escape path.
- No canonical config will enable `default_mode_request_user_input = true` across the fleet.
- No tested merger will own the new nested keys while preserving unrelated local TOML state.
- No fleet registry/equality dimension will distinguish declared Codex capability, installed version, feature state, launcher mode, trusted-root set, and config hash.
- No rollout command will enumerate the actual live target set and produce explicit per-machine attempted/succeeded/unreachable evidence.
- Claude machine-wide statusline convergence from the original issue remains incomplete.

### Evidence (embedded verification)

**Issue status** (verified 2026-08-02 via `gh issue view`):

```text
#3555 OPEN  status:needs-plan  lane:claude
#2887 OPEN  parent machine/provider-equivalence epic
```

**Current CLI probe** (2026-08-02 on the planning host):

```text
$ codex --version
codex-cli 0.146.0
$ codex features list | grep default_mode_request_user_input
default_mode_request_user_input  under development  false
```

**Current repo probe:**

```text
config/agents/codex/config.toml       EXISTS; obsolete [status_line]
scripts/install/codex-pin.env         EXISTS; CODEX_PIN_VERSION=0.123.0
scripts/_core/sync-agent-configs.sh   EXISTS; recognizes [status_line]
config/agents/codex/launcher/         MISSING
tests/setup/test_codex_launcher.sh    MISSING
```

**Current registry probe:**

```text
ace-linux-1  agent_clis=[claude, gemini]       # live Codex contradicts declaration
ace-win-1    agent_clis=[claude, codex, gemini]
ace-win-2    agent_clis=[claude, codex, gemini]
```

Reproduction date: 2026-08-02. The stale canonical schema, disabled default-mode input feature, untracked unconditional wrapper, stale version pin, and registry drift match the expanded issue scope.

Distinct sources: 14.

---

## Artifact Map

| Artifact | Path |
|---|---|
| Canonical plan | `docs/plans/2026-07-16-issue-3555-goal-statusline-machine-pilot.md` |
| Approved design | `docs/superpowers/specs/2026-08-02-codex-fleet-config-design.html` |
| Human plan report | `docs/reports/2026-07-16-issue-3555-goal-statusline-plan.html` |
| Codex config | `config/agents/codex/config.toml` |
| Trusted-root policy | `config/agents/codex/trusted-repos.yaml` |
| POSIX launchers | `config/agents/codex/launcher/codex`, `config/agents/codex/launcher/codex-safe` |
| Windows launchers | `config/agents/codex/launcher/codex.cmd`, `config/agents/codex/launcher/codex-safe.cmd` |
| Launcher installer | `scripts/agents/install-codex-launcher.sh` |
| Config sync | `scripts/_core/sync-agent-configs.sh` |
| Version pin | `scripts/install/codex-pin.env`, `scripts/install/pin-codex.sh` |
| Setup/update/verify | `scripts/setup/new-machine-setup.sh`, `scripts/maintenance/update-harness-tools.sh`, `scripts/setup/verify-setup.sh` |
| Claude convergence | `config/agents/claude/statusline.mjs`, `scripts/_core/sync_statusline.sh` |
| Fleet evidence | `config/workstations/registry.yaml`, `scripts/readiness/collect-equality.sh`, `scripts/readiness/collect-equality.ps1`, `scripts/readiness/build-equality-matrix.py` |
| Launcher/config tests | `tests/setup/test_codex_launcher.sh`, `scripts/_core/tests/test_sync_agent_configs.sh`, `tests/setup/test_verify_setup.py` |
| Equality tests | `tests/readiness/test_collect_equality.py`, `tests/readiness/test_collect_equality_ps1_schema.py`, `tests/readiness/test_build_equality_matrix.py` |
| Plan reviews | `scripts/review/results/2026-08-02-plan-3555-r3-{claude,codex,agy}.md` |
| Code reviews | `scripts/review/results/2026-08-02-code-3555-r1-{claude,codex,agy}.md` |
| Rollout report | `docs/reports/2026-08-02-issue-3555-codex-fleet-rollout.html` |

## Deliverable

The repository will provide a tested and auditable fleet configuration/deployment path that enables Codex requirement questions by default, persistent goals and useful telemetry, and trusted-repo YOLO launch behavior with safe fallback, while preserving local settings and reporting machine-level rollout truth.

## Semantic Contract and Pseudocode

```text
owned_codex_keys := {
  plan_mode_reasoning_effort = "high",
  personality = "pragmatic",
  web_search = "live",
  features.default_mode_request_user_input = true,
  features.goals = true,
  features.multi_agent = true,
  features.hooks = true,
  agents.enabled = true,
  agents.interrupt_message = true,
  tui.resume_cwd = "session",
  tui.status_line = [model-with-reasoning, context-remaining, current-dir,
                     five-hour-limit, weekly-limit]
}

merge_codex_config(local, canonical):
  parse both TOML documents or fail before write
  replace only owned_codex_keys
  preserve every unowned root key, table, comment-compatible value, and secret-free local setting
  validate candidate with installed Codex
  atomically replace local config only after validation

resolve_real_codex():
  prefer validated CODEX_REAL_BIN
  otherwise select the platform package-manager binary outside launcher directory
  reject a path resolving to codex or codex-safe wrapper

launch_codex(args, safe=false):
  real := resolve_real_codex()
  if safe: exec real with args unchanged
  root := git rev-parse --show-toplevel or empty
  trusted := canonicalize(root) exactly matches an installed attested trusted root
  if trusted: exec real --yolo args
  otherwise: exec real args and emit concise safe-mode reason

rollout():
  derive declared targets from registry
  add empirical Codex hosts only after attestation and registry reconciliation
  for every target in the same rollout wave:
    install pinned CLI, merge config, install launchers, run verification, collect evidence
  render each target as EQUAL, DIVERGES, MISSING-EVIDENCE, or UNREACHABLE
  never collapse partial attempted coverage into fleet-complete
```

## Detailed TDD Implementation Tasks

### Task 1 — Pin and validate the Codex feature baseline

**Files:** `scripts/install/codex-pin.env`, `scripts/install/pin-codex.sh`, `config/agents/codex/config.toml`, `tests/setup/test_verify_setup.py`, `scripts/setup/verify-setup.sh`.

1. Write failing tests that require the pin, canonical config, and verifier to agree on one exact CLI version and require `codex features list` to expose `default_mode_request_user_input`.
2. Run `pytest -q tests/setup/test_verify_setup.py` and retain the expected RED output.
3. Set the verified pin to `0.146.0`; add a fixture seam so tests do not require network installation.
4. Replace the obsolete Codex template with the approved owned keys and documented `[tui]` schema; do not set a hardcoded model or native memories.
5. Make verification fail closed when the CLI is older, the feature is absent, or effective config differs.
6. Rerun the focused tests and `bash scripts/setup/verify-setup.sh --strict` against a temporary home.
7. Commit with `git commit -m "feat(codex): pin fleet feature baseline" -- scripts/install/codex-pin.env scripts/install/pin-codex.sh config/agents/codex/config.toml scripts/setup/verify-setup.sh tests/setup/test_verify_setup.py`.

### Task 2 — Implement merge-safe nested Codex configuration

**Files:** `scripts/_core/sync-agent-configs.sh`, `scripts/_core/tests/test_sync_agent_configs.sh`, `scripts/_core/tests/test_sync_agent_helpers.sh`.

1. Add failing fixtures containing unrelated root keys, `[tui]` siblings, project trust entries, MCP/plugin tables, comments, paths with spaces, and malformed TOML.
2. Assert exact ownership of the approved key set, preservation of every unowned value, idempotence, dry-run purity, and atomic rollback on parse/validation failure.
3. Run both shell test files and observe RED against the current `[status_line]` parser.
4. Implement a TOML-aware helper or constrained parser with explicit table/key ownership; remove legacy owned syntax only when the replacement validates.
5. Rerun focused tests twice to prove idempotence, then run the existing sync regression suite.
6. Commit only the three named paths with a conventional pathspec commit.

### Task 3 — Install trusted-repo YOLO launchers with a safe escape

**Files:** `config/agents/codex/trusted-repos.yaml`, `config/agents/codex/launcher/codex`, `config/agents/codex/launcher/codex-safe`, `config/agents/codex/launcher/codex.cmd`, `config/agents/codex/launcher/codex-safe.cmd`, `scripts/agents/install-codex-launcher.sh`, `tests/setup/test_codex_launcher.sh`.

1. Write failing tests using a fake real CLI to capture argv for trusted root, untrusted root, non-Git directory, spaces, quotes, repeated flags, missing real binary, recursion, and `codex-safe` cases.
2. Add static Windows tests that verify `%*` forwarding, explicit non-wrapper real-binary resolution, quoting, trusted-root lookup, and safe entry behavior.
3. Run the launcher suite and observe RED because the repo-managed artifacts do not exist.
4. Implement exact canonical-path matching from a generated machine-local allowlist derived from the registry plus live attestation. Prefix matching and current-directory string matching will be forbidden.
5. Install wrappers atomically into the user-local bin directory before the package-manager binary; preserve an existing unknown wrapper as a timestamped backup and report it.
6. Ensure plain `codex` adds one `--yolo` only in a trusted root; outside it, invoke normal Codex without `--yolo`. Ensure `codex-safe` never adds it.
7. Run shellcheck where available, the focused launcher suite, and a real `codex --version` smoke test from trusted and untrusted temporary repos.
8. Commit the named launcher, policy, installer, and test paths only.

### Task 4 — Preserve goal authorization and converge Claude statusline behavior

**Files:** `config/agents/SHARED_SOUL.md`, `.claude/rules/goal-invocation.md`, `scripts/agents/build-soul-runtime.sh`, `config/agents/claude/statusline.mjs`, `scripts/_core/sync_statusline.sh`, existing runtime/statusline tests.

1. Write failing tests that require `--yolo` to remain subordinate to the issue/plan/user-approval gates and that require the goal rule to appear exactly once in generated runtimes.
2. Add failing cross-shell renderer fixtures for Linux Bash, Windows Git Bash, and PowerShell-shaped paths/input.
3. Implement the smallest policy/runtime and Claude renderer/deployment changes necessary to satisfy those tests.
4. Rebuild generated runtime artifacts using `scripts/agents/build-soul-runtime.sh`; do not hand-edit generated files.
5. Run runtime coherence, statusline, harness-size, and generated-artifact tests.
6. Commit canonical sources, generated outputs, and tests with explicit pathspecs.

### Task 5 — Integrate setup, scheduled updates, and semantic verification

**Files:** `scripts/setup/new-machine-setup.sh`, `scripts/maintenance/update-harness-tools.sh`, `scripts/setup/verify-setup.sh`, `tests/setup/test_new_machine_setup.py`, `tests/setup/test_verify_setup.py`.

1. Add failing tests that require both setup and scheduled maintenance to call the canonical pin, config merge, launcher installer, and verifier in order.
2. Assert dry-run purity, noninteractive behavior, retry-safe idempotence, failure propagation, and preservation of the prior working install.
3. Implement shared calls instead of duplicated config/wrapper logic.
4. Run focused setup/update tests and the broader setup regression suite.
5. Commit the named paths only.

### Task 6 — Add fleet truth and reconcile the target roster

**Files:** `config/workstations/registry.yaml`, `scripts/readiness/collect-equality.sh`, `scripts/readiness/collect-equality.ps1`, `scripts/readiness/build-equality-matrix.py`, existing readiness tests and fixtures.

1. Write failing Bash, PowerShell-schema, and Python tests for `codex_declared`, `codex_version`, `request_user_input_enabled`, `config_hash`, `launcher_mode`, `trusted_roots_hash`, and evidence freshness.
2. Add fixtures for registry drift, empirically present Codex, unreachable host, stale report, safe-only launcher, and partial rollout.
3. Assert that only direct fresh evidence can produce `EQUAL`; declared intent or successful SSH alone will not.
4. Reconcile `ace-linux-1` in the registry only after a live attestation confirms that Codex is intended there; enumerate every declared Codex target rather than assuming the July roster.
5. Implement collectors and renderer changes without publishing auth material, paths outside allowed repo-root metadata, prompts, goal text, transcripts, or token values.
6. Run the focused readiness tests and matrix regression suite.
7. Commit registry, collectors, renderer, fixtures, and tests with explicit pathspecs.

### Task 7 — Review, immediate rollout, and durable evidence

**Files:** `scripts/review/results/2026-08-02-code-3555-r1-{claude,codex,agy}.md`, `docs/reports/2026-08-02-issue-3555-codex-fleet-rollout.html`, [#3555](https://github.com/vamseeachanta/workspace-hub/issues/3555).

1. Run focused suites, full relevant regressions, `scripts/legal/legal-sanity-scan.sh`, no-absolute-path enforcement, harness-size checks, and shell/static analysis.
2. Push the reviewed commit, dispatch adversarial T3 code review, and resolve every MAJOR before rollout. Provider outage may degrade T3 to T2 only with a valid `UNAVAILABLE` artifact; invalid output will block.
3. Enumerate live Codex targets from the reconciled registry and equality evidence immediately before rollout and record the exact set.
4. Attempt the same approved installer sequence on every reachable target in one wave. Do not stop after the first success and do not call any one host a canary.
5. Open a fresh interactive Codex session in one attested trusted repo and one untrusted directory on every reachable target; verify default-mode requirement input capability, statusline fields, trusted-root YOLO, and safe-mode behavior.
6. Collect fresh equality evidence, render the HTML report, and label each target `EQUAL`, `DIVERGES`, `MISSING-EVIDENCE`, or `UNREACHABLE` with timestamp and command evidence.
7. Comment the implementation/test/review/rollout summary on #3555. Close only after acceptance criteria pass; otherwise leave it open with exact residue and next action.
8. Run `.claude/skills/coordination/pre-completion-cleanup-audit/SKILL.md` and resolve unexpected worktrees, stashes, temp clones, locks, and untracked artifacts before completion.

## TDD Test List

| Test | Required result |
|---|---|
| `test_codex_pin_exposes_default_mode_input` | Exact pinned CLI advertises the feature |
| `test_canonical_config_owned_keys` | Approved keys and footer are present; unsupported keys are absent |
| `test_sync_preserves_unowned_nested_tables` | Local trust/MCP/plugin/project/model values survive |
| `test_sync_malformed_toml_rolls_back` | No partial replacement occurs |
| `test_launcher_trusted_root_adds_yolo_once` | Fake CLI receives one `--yolo` plus original argv |
| `test_launcher_untrusted_root_is_safe` | No `--yolo` outside exact trusted root |
| `test_launcher_rejects_prefix_collision` | `/repo-evil` cannot match `/repo` |
| `test_launcher_prevents_recursion` | Wrapper paths cannot resolve as real CLI |
| `test_codex_safe_never_adds_yolo` | Safe entry remains available everywhere |
| `test_windows_cmd_forwards_argv` | Windows launcher preserves argument boundaries |
| `test_setup_update_share_installer` | Both lifecycle paths converge through one implementation |
| `test_goal_gate_survives_yolo` | Plan/user approval remains mandatory |
| `test_equality_requires_fresh_direct_evidence` | Intent and stale evidence cannot produce equality |
| `test_partial_rollout_not_fleet_complete` | Unreachable/missing targets remain explicit |
| `test_evidence_rejects_sensitive_content` | No secrets/prompts/transcripts/token values enter reports |

## Acceptance Criteria

- [ ] Fresh T3 plan review has no unresolved MAJOR, and the user applies `status:plan-approved`.
- [ ] `default_mode_request_user_input = true` is present in effective config on every reachable declared Codex target.
- [ ] The exact installed CLI version supports the feature; pin/config/verifier agree.
- [ ] Goals, multi-agent, hooks, live web search, high plan reasoning, pragmatic personality, resume-CWD, interrupt messaging, and the five approved statusline fields are effective.
- [ ] Config sync is atomic, idempotent, dry-run safe, and preserves all unowned local settings.
- [ ] Plain `codex` adds `--yolo` exactly once in attested trusted roots and nowhere else; `codex-safe` never adds it.
- [ ] POSIX and Windows launcher argument/quoting/recursion tests pass.
- [ ] Claude native goal and machine-wide statusline behavior remain covered from the original issue.
- [ ] Setup and scheduled maintenance invoke the same pin/config/launcher/verification path.
- [ ] Every actual Codex-capable host is enumerated and either has fresh passing evidence or an explicit non-success state.
- [ ] No report claims fleet completion while any target is unenumerated, stale, missing, divergent, or unreachable.
- [ ] Focused and relevant regression tests, legal scan, enforcement scripts, and adversarial code review pass.
- [ ] #3555 receives an implementation summary comment with commit, tests, review, and rollout evidence.
- [ ] Pre-completion cleanup audit returns CLEAN or EXPECTED with named residue.

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Claude (historical July r1) | UNAVAILABLE | Authentication unavailable; not evidence for the expanded plan |
| Codex (historical July r1/r2) | MAJOR | Pilot scope, config schema, evidence privacy, and fleet-claim defects; incorporated into this revision |
| Gemini (historical July r1) | UNAVAILABLE | Historical provider unavailable; AGY will be used for fresh review |
| Claude (2026-08-02 r3) | PENDING | Fresh adversarial review required |
| Codex (2026-08-02 r3) | PENDING | Fresh adversarial review required |
| AGY (2026-08-02 r3) | PENDING | Fresh adversarial review required |

**Overall result:** PENDING — the user has approved the design spec, not the implementation plan gate. The issue will move to `status:plan-review` only after fresh review has no unresolved MAJOR.

## Risks and Open Questions

- **Under-development feature:** `default_mode_request_user_input` may change upstream. The exact pin and live feature probe will make failure explicit; upgrades will not float silently.
- **Approval bypass risk:** `--yolo` is intentionally high-trust. Exact-root matching, safe fallback, and governance tests will keep its scope bounded.
- **Windows quoting risk:** `.cmd` parsing differs from POSIX shells. Fake-CLI argument capture and static tests will cover metacharacter/space cases before rollout.
- **Roster drift:** `ace-linux-1` contradicts the registry. Empirical attestation will precede registry change and any fleet denominator claim.
- **Immediate rollout blast radius:** there will be no canary by user direction. Atomic installers, backups, dry-run/verification, and `codex-safe` will provide rollback and continued access.
- **Provider availability:** a valid `UNAVAILABLE` review artifact may degrade T3 to T2; malformed or unparsable output will block.

## Complexity: T3

Cross-platform launch behavior, a security-relevant approval bypass, nested config preservation, provider UX convergence, roster reconciliation, and live multi-machine rollout require three-provider adversarial review and system-level regression coverage.
