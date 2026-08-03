# Plan for #3555: Fleet-wide Codex requirements, trusted-repo YOLO, goals, and statuslines

> **Status:** draft — Task 2 architecture re-review required
> **Complexity:** T3
> **Date:** 2026-08-02
> **Revision:** 2026-08-03 — Task 2 CST/semantic-preservation replan
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/3555
> **Client:** N/A
> **Lane:** lane:claude
> **Execution mode:** single-lane implementation and rollout after plan approval, TDD, and code review; parallel-readonly provider review; no canary
> **Review artifacts:** historical `scripts/review/results/2026-07-16-plan-3555-{claude,codex,gemini}.md`, `2026-07-16-plan-3555-r2-codex.md`, and `2026-08-02-plan-3555-{claude,codex,agy}.md`; replacement machine-parseable T3 artifacts will be recorded after this revision

> For agentic workers: follow this plan task by task. Write each named test first, observe the relevant failure, implement only enough to pass, rerun the focused and regression suites, and use pathspec commits. The user approval gate remains mandatory even when Codex runs with `--yolo`.

**Goal:** Every reachable, Codex-capable workstation and trusted repo will receive a repo-managed Codex baseline that enables default-mode requirement questions, persistent goals, multi-agent support, hooks, live web search, useful TUI telemetry, and a trusted-repo `--yolo` launcher with an explicit safe escape path; Claude goal/statusline behavior will converge under the same issue.

**Architecture:** Repo-tracked templates will remain canonical. A standalone PEP 723 merger pinned and locked to TOMLKit `0.15.1` will perform comment-preserving CST edits for only the owned Codex paths; an independent `tomllib` projection will reject any staged document whose unowned semantics differ from the source. A cross-platform launcher will add `--yolo` only when the current Git root matches a user-approved trusted repo root and no directory-changing argument escapes it, while `codex-safe` will inject workspace-write/on-request safety flags. Setup, update, verification, and equality collection will share one locked transaction and will report per-machine evidence without converting missing or unreachable machines into success.

**Tech stack:** Bash, Python 3.11+, TOMLKit `0.15.1` via a committed PEP 723 uv script lock, Python `tomllib`, TOML, JSON, the existing Node.js GSD statusline sub-renderer, Windows `.cmd` launchers, pytest, shell test harnesses, GitHub Actions-compatible checks.

---

## Global Constraints

- Implementation will not begin until fresh T3 adversarial plan review has no unresolved MAJOR finding and the user applies the approval gate.
- Tests will precede implementation in every task.
- The fleet denominator will begin with all seven registry machines, not only machines already declaring Codex. The rollout will target every reachable host empirically confirmed or owner-declared Codex-capable in one wave; it will not use a canary. A machine will remain `NOT-CODEX-TARGET`, `UNREACHABLE`, `MISSING-EVIDENCE`, or `DIVERGES` until direct evidence supports another state.
- `--yolo` will bypass Codex sandbox/approval prompts only after user-approved trust authorization. This is an authorization trigger, not OS containment: accepted YOLO execution has host-wide authority. The launcher will reject or safely downgrade Git-environment spoofing and directory-expanding arguments. It will not bypass issue, plan, user-approval, TDD, review, legal, secret, or merge gates.
- The launcher will provide `codex-safe` and `CODEX_REAL_BIN` escape seams and will prevent wrapper recursion.
- The merger will migrate `model` and `model_reasoning_effort` from the old managed set to preserved machine-local keys before the canonical template drops them; it will preserve auth, trust, MCP/plugin, project, and every other key outside the new explicit owned-key set.
- The merger will not carry a hand-written TOML lexer. It will mutate a grammar-complete CST and will fail closed unless an independent semantic projection proves that every unowned path and value is unchanged. Comment-bearing destructive shrinks will fail closed rather than relocating or discarding comments.
- The installer will take a cross-platform user lock, stage CLI/config/launchers/trust policy together, validate the staged state, write a transaction manifest, commit atomically where the platform allows, and expose one rollback command for crash recovery.
- Native Codex memories and automatic approval reviewers will remain excluded because they conflict with the repo-managed memory/approval model.
- The implementation will pin a CLI version only after the feature probe proves that exact version supports `default_mode_request_user_input`; the current candidate is `0.146.0`.
- Human-facing review material will remain HTML; lifecycle and harness artifacts will remain Markdown/TOML/scripts.

## Resource Intelligence Summary

### Existing repo code

- `config/agents/codex/config.toml` currently declares `model = "gpt-5.5"`, medium reasoning, and obsolete `[status_line]` syntax. It does not declare the approved feature baseline.
- Frozen feature commit `723d58e426ddbb189bf7fe2ccf0b497236b270b4` contains the first four Task 2 fix rounds. Its embedded constrained TOML lexer will remain frozen and will be replaced rather than extended because valid TOML can still cause silent deletion of an unowned following table.
- `scripts/_core/sync-agent-configs.sh` will retain transaction, dry-run, and atomic-replace responsibilities. TOML mutation will move to a focused locked helper instead of remaining embedded in the shell script.
- `scripts/install/codex-pin.env` currently pins `0.123.0`; `scripts/install/pin-codex.sh` installs that exact pin, and `scripts/setup/verify-setup.sh` reports drift against it.
- `scripts/setup/new-machine-setup.sh` already installs the Codex pin but does not install a repo-managed launcher or invoke canonical config sync afterward.
- `scripts/maintenance/update-harness-tools.sh` updates Codex independently and does not converge launcher/config state.
- `~/.local/bin/codex` on the planning host is an untracked Bash wrapper that unconditionally appends `--yolo`; no repository artifact owns or verifies it.
- `scripts/_core/sync_statusline.sh` and the Claude settings/statusline paths remain split, so the original #3555 Claude convergence scope will remain in this plan.
- `scripts/readiness/collect-equality.sh`, `collect-equality.ps1`, and `build-equality-matrix.py` form the existing per-machine evidence pipeline.

### Product and configuration contract

- Codex CLI `0.146.0` exposes `default_mode_request_user_input` as an under-development feature whose source description is “Allow request_user_input in Default collaboration mode.”
- The current stable configuration reference documents `plan_mode_reasoning_effort`, `personality`, `web_search`, `[features]`, `[agents]`, and `[tui].status_line`/`resume_cwd`.
- `goals`, `multi_agent`, and `hooks` are stable in the inspected CLI; declaring them explicitly will make fleet intent auditable.
- The supported footer identifiers selected for this work are `model-with-reasoning`, `context-remaining`, `current-dir`, `five-hour-limit`, and `weekly-limit`.
- `status_line_use_colors` does not appear in the current official manual and will not be introduced.
- Native goals will remain distinct from TUI telemetry; the plan will not fabricate arbitrary goal text as a footer field.
- TOMLKit `0.15.1` supports Python `>=3.9`, carries an MIT license, and describes itself as style-preserving, including comments, indentation, whitespace, and internal ordering. Its documented array-of-table placement caveat will require semantic/comment and idempotence assertions rather than a blanket byte-position promise.

### Fleet and governance sources

- `config/workstations/registry.yaml` declares seven machines and declares Codex for `ace-win-1` and `ace-win-2`, but not for `ace-linux-1`; the current planning host runs Codex `0.146.0`, so the declared capability roster is incomplete. `ace-win-2` has no remote transport and will require a named human local verification or remain `UNREACHABLE`.
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
- Official TOMLKit package metadata: https://pypi.org/project/tomlkit/0.15.1/
- Official TOMLKit source and style-preservation contract: https://github.com/python-poetry/tomlkit/tree/0.15.1
- Drive-file search from the July planning round returned no relevant deliverable; inaccessible drive indexes remain a coverage limitation, not negative proof.

### Gaps identified

- No repo-managed cross-platform Codex launcher will enforce user-authorized trusted-root YOLO, Git-environment hardening, directory-argument checks, recursion safety, argument preservation, and an enforced-safe escape path.
- No canonical config will enable `default_mode_request_user_input = true` across the fleet.
- No grammar-complete, comment-preserving merger with an independent unowned-semantic equality guard will own the new nested keys while preserving unrelated local TOML state.
- No fleet registry/equality dimension will distinguish declared Codex capability, installed version, feature state, launcher mode, trusted-root set, and config hash.
- No rollout command will probe all seven registered machines, distinguish non-target from unreachable, and produce explicit per-machine attempted/succeeded/unreachable evidence.
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
registry machines: ace-linux-1, ace-linux-2, ace-win-1, ace-win-2,
                   gpu-claw, Vamsees-MacBook-Air, shoerack
declared Codex:    ace-win-1, ace-win-2
empirical drift:  ace-linux-1 runs Codex but does not declare it
remote gap:       ace-win-2 has no SSH/Tailscale transport
```

Reproduction date: 2026-08-02. The stale canonical schema, disabled default-mode input feature, untracked unconditional wrapper, stale version pin, and registry drift match the expanded issue scope.

**Task 2 architecture reproduction** (2026-08-02 against frozen feature SHA `723d58e426ddbb189bf7fe2ccf0b497236b270b4`):

```text
input:  status_line = ["""tail""""] followed by [plugins.keep]
input_valid=True
sync_rc=0
output_valid=True
plugins_after=None
```

The real sync path accepts valid input, exits successfully, and emits valid TOML while deleting the unowned table. Four adversarial fix rounds separately expose header recognition, semantic key/type classification, backslash parity, and multiline delimiter-run defects. This reproduction will remain RED until the CST merger and semantic-preservation guard replace the constrained lexer.

Distinct sources: 16.

---

## Artifact Map

| Artifact | Path |
|---|---|
| Canonical plan | `docs/plans/2026-07-16-issue-3555-goal-statusline-machine-pilot.md` |
| Approved design | `docs/superpowers/specs/2026-08-02-codex-fleet-config-design.html` |
| Human plan report | `docs/reports/2026-07-16-issue-3555-goal-statusline-plan.html` |
| Codex config | `config/agents/codex/config.toml` |
| User-approved trust policy | `config/agents/codex/trusted-repos.yaml` |
| POSIX launchers | `config/agents/codex/launcher/codex`, `config/agents/codex/launcher/codex-safe` |
| Windows launchers | `config/agents/codex/launcher/codex.cmd`, `config/agents/codex/launcher/codex-safe.cmd` |
| Launcher installer | `scripts/agents/install-codex-launcher.sh` |
| Config sync | `scripts/_core/sync-agent-configs.sh` |
| Locked TOML CST merger | `scripts/agents/codex_config_merge.py`, `scripts/agents/codex_config_merge.py.lock` |
| Version pin | `scripts/install/codex-pin.env`, `scripts/install/pin-codex.sh` |
| Setup/update/verify | `scripts/setup/new-machine-setup.sh`, `scripts/maintenance/update-harness-tools.sh`, `scripts/setup/verify-setup.sh` |
| Claude convergence | `.claude/statusline-command.sh`, `.claude/statusline-combined.sh`, `scripts/_core/sync_statusline.sh` |
| Fleet evidence | `config/workstations/registry.yaml`, `scripts/readiness/collect-equality.sh`, `scripts/readiness/collect-equality.ps1`, `scripts/readiness/build-equality-matrix.py` |
| Launcher/config tests | `tests/setup/test_codex_launcher.sh`, `scripts/_core/tests/test_sync_agent_configs.sh`, `scripts/_core/tests/test_sync_agent_configs_edge_cases.sh`, `tests/setup/test_codex_config_merge.py`, `tests/setup/test_verify_setup.py` |
| Equality tests | `tests/readiness/test_collect_equality.py`, `tests/readiness/test_collect_equality_ps1_schema.py`, `tests/readiness/test_build_equality_matrix.py` |
| Plan reviews | `scripts/review/results/2026-08-02-plan-3555-{claude,codex,agy}.md` |
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
  parse both documents with TOMLKit CST and independently with tomllib or fail before write
  require canonical semantic paths and values to equal owned_codex_keys exactly
  remove model and model_reasoning_effort from the legacy managed-key deletion set
  remove only legacy root status_line; reject non-table features/agents/tui roots
  replace only owned_codex_keys through CST nodes
  mutate an existing tui.status_line array in place; fail closed if shrinking would discard comments
  render staged text and parse it independently with tomllib
  local_unowned := semantic_projection(local) minus owned_codex_keys and legacy root status_line
  staged_unowned := semantic_projection(staged) minus owned_codex_keys and empty owned-only containers
  require staged_unowned == local_unowned or discard staged output
  require every staged owned value == canonical value or discard staged output
  validate typed enums with an isolated CODEX_HOME CLI load
  compare `codex features list` before/after and require request_user_input false -> true
  validate footer identifiers against the version-pinned source allowlist and TUI attestation
  atomically replace local config only after validation

resolve_real_codex():
  prefer validated CODEX_REAL_BIN
  otherwise select the platform package-manager binary outside launcher directory
  reject a path resolving to codex or codex-safe wrapper

launch_codex(args, safe=false):
  real := resolve_real_codex()
  reject or normalize caller-supplied yolo/approval/sandbox config before policy evaluation
  if safe: exec real with normalized args plus final workspace-write/on-request controls
  reject Git root resolution when any GIT_* discovery override is set
  root := git rev-parse --show-toplevel under a scrubbed Git-discovery environment
  trusted := canonicalize(root) exactly matches a user-approved, non-revoked root
  validate -C/--cd and --add-dir targets; downgrade unless every target remains inside root
  if trusted: exec real --yolo args  # user accepts host-wide authority here
  otherwise: exec real --sandbox workspace-write --ask-for-approval on-request with args

rollout():
  enumerate every active machine in the registry
  probe each reachable machine for Codex; record NOT-CODEX-TARGET or UNREACHABLE explicitly
  reconcile empirical Codex hosts with owner intent before mutating registry or trust policy
  for every target in the same rollout wave:
    install pinned CLI, merge config, install launchers, run verification, collect evidence
  render each target as EQUAL, DIVERGES, MISSING-EVIDENCE, or UNREACHABLE
  never collapse partial attempted coverage into fleet-complete
```

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Modify | `config/agents/codex/config.toml` | Declare the owned fleet baseline without a model override |
| Create | `config/agents/codex/trusted-repos.yaml` | Define versioned owner authorization, origins, roots, expiry, and revocation |
| Create | `config/agents/codex/launcher/codex`, `codex-safe`, `codex.cmd`, `codex-safe.cmd` | Provide POSIX and Windows launch behavior |
| Create | `scripts/agents/install-codex-launcher.sh` | Lock, stage, validate, commit, and roll back the complete install transaction |
| Create | `scripts/agents/codex_config_merge.py`, `scripts/agents/codex_config_merge.py.lock` | Provide a pinned style-preserving CST merger with an independent semantic guard |
| Modify | `scripts/_core/sync-agent-configs.sh` and its shell tests | Delegate nested-key mutation while retaining dry-run and atomic replacement |
| Create | `tests/setup/test_codex_config_merge.py` | Exercise the merger API, semantic preservation, comment behavior, and locked dependency failures |
| Modify | `scripts/install/codex-pin.env`, `pin-codex.sh` | Pin and install the verified feature baseline |
| Modify | `scripts/setup/new-machine-setup.sh`, `scripts/maintenance/update-harness-tools.sh`, `scripts/setup/verify-setup.sh` | Share the transactional deployment path |
| Modify | `.claude/statusline-command.sh`, `.claude/statusline-combined.sh`, `scripts/_core/sync_statusline.sh`, `tests/statusline/` | Converge the real tracked Claude renderer paths |
| Modify | `config/workstations/registry.yaml`, readiness collectors/builder/tests | Establish the seven-host denominator and direct evidence contract |
| Create | `tests/setup/test_codex_launcher.sh`, `tests/setup/windows/capture-argv.cmd` | Cover POSIX behavior and live `cmd.exe` argv capture |
| Create | `docs/reports/2026-08-02-issue-3555-codex-fleet-rollout.html` | Publish immutable-SHA, per-host rollout evidence |
| Update | this plan, plan HTML, `docs/plans/README.md`, review artifacts | Preserve lifecycle traceability |

## Detailed TDD Implementation Tasks

### Task 0 — Establish the fleet denominator and owner-authorized trust manifest

**Files:** `config/workstations/registry.yaml`, `config/agents/codex/trusted-repos.yaml`, `tests/setup/test_codex_trusted_repos.py`, `docs/reports/2026-08-02-issue-3555-codex-fleet-rollout.html`.

1. Enumerate all seven registry machines and record transport, reachability, declared CLIs, live Codex probe result, checkout roots, and exact Git origins. A reachable machine without Codex will become `NOT-CODEX-TARGET`; a machine without a usable transport will become `UNREACHABLE`, not omitted.
2. Write failing schema tests for `version`, `approval_issue`, `approved_by`, `approved_at`, exact repository identity/origin, machine alias, canonical root, optional expiry, and revocation. Live discovery will never authorize trust by itself.
3. Define deterministic root normalization: resolve symlinks/junctions, normalize drive/UNC spelling, case-fold on Windows, reject nonexistent roots, and require the observed origin to match the exact approved repository identity.
4. Encode the owner-approved policy from this plan: only registered repo-ecosystem checkouts with an exact registered origin will qualify; the materialized per-machine manifest and SHA will be posted to #3555 before launcher activation. Any out-of-policy root will require a later explicit owner approval.
5. Render machine-local allowlists with owner-only permissions and an expiry/revocation check; do not derive authorization from a broad organization prefix or directory parent.
6. Run `uv run pytest -q tests/setup/test_codex_trusted_repos.py` and the registry schema tests.
7. Serialize all later tasks behind the committed denominator/trust schema because they share setup and verification paths.

### Task 1 — Pin and validate the Codex feature baseline

**Files:** `scripts/install/codex-pin.env`, `scripts/install/pin-codex.sh`, `config/agents/codex/config.toml`, `tests/setup/test_verify_setup.py`, `scripts/setup/verify-setup.sh`.

1. Write failing tests that require the pin, canonical config, and verifier to agree on one exact CLI version and require `codex features list` to expose `default_mode_request_user_input`.
2. Run `uv run pytest -q tests/setup/test_verify_setup.py` and retain the expected RED output.
3. Set the verified pin to `0.146.0`; add a fixture seam so tests do not require network installation.
4. Replace the obsolete Codex template with the approved owned keys and documented `[tui]` schema; do not set a hardcoded model or native memories.
5. Make verification fail closed when the CLI is older, the feature is absent, typed enums fail an isolated `CODEX_HOME` load, or `codex features list` does not differentially change `default_mode_request_user_input` from false to true. Validate footer identifiers against the version-pinned source allowlist plus a recorded TUI selector attestation because the CLI silently accepts unknown footer strings.
6. Rerun the focused tests and `bash scripts/setup/verify-setup.sh --strict` against a temporary home.
7. Commit with `git commit -m "feat(codex): pin fleet feature baseline" -- scripts/install/codex-pin.env scripts/install/pin-codex.sh config/agents/codex/config.toml scripts/setup/verify-setup.sh tests/setup/test_verify_setup.py`.

### Task 2 — Implement merge-safe nested Codex configuration

**Files:** `scripts/agents/codex_config_merge.py`, `scripts/agents/codex_config_merge.py.lock`, `scripts/_core/sync-agent-configs.sh`, `scripts/_core/tests/test_sync_agent_configs.sh`, `scripts/_core/tests/test_sync_agent_configs_edge_cases.sh`, `scripts/_core/tests/test_sync_agent_helpers.sh`, `tests/setup/test_codex_config_merge.py`, `tests/readiness/test_sync_agent_configs_sso.py`.

**Interface:** `uv run --script --locked scripts/agents/codex_config_merge.py CANONICAL LOCAL OUTPUT` will either write one validated staged document and exit 0 or write nothing and exit nonzero. The shell caller will retain temporary-file placement, dry-run purity, atomic rename, and rollback.

1. Add a focused Python RED test that invokes the frozen feature implementation at `723d58e426ddbb189bf7fe2ccf0b497236b270b4` with `status_line = ["""tail""""]` followed by `[plugins.keep]` and requires the unowned table to survive. Record `input_valid=True`, `sync_rc=0`, `output_valid=True`, and the current failing `plugins_after=None` evidence.
2. Add table-driven RED fixtures for every R1–R4 defect class: arrays-of-tables, bracket-bearing quoted headers, quoted/whitespace dotted keys, inline tables with braces in comments, sentinel-like path components, incompatible root value types, newline-less headers, backslash runs, and four/five-quote multiline terminators. Each fixture will assert parsed unowned semantics, comment preservation where applicable, and real same-file second-run byte identity.
3. Add RED semantic-guard tests that deliberately delete, insert, mutate, relocate, or type-change one unowned root/nested/table/array-of-table value after CST rendering. Every mutation will fail before `OUTPUT` is created and will leave `LOCAL` byte-identical in normal and dry-run flows.
4. Add RED tests for root/table/suffix comments, comments inside the five-entry `tui.status_line` array, and a comment-bearing local array that must shrink. The first cases will preserve comments; the destructive shrink will fail closed unless every removed node is comment-free.
5. Create `scripts/agents/codex_config_merge.py` with PEP 723 metadata pinned to `tomlkit==0.15.1`; generate and commit its adjacent lock with `uv lock --script scripts/agents/codex_config_merge.py`. The runtime command will use `uv run --script --locked`; missing uv, missing/stale lock, dependency resolution failure, malformed input, or incompatible root shape will produce no output.
6. Parse canonical and local documents through TOMLKit and independently through `tomllib`. Validate that the canonical semantic document contains the eleven owned paths with exact values and contains none of the forbidden model/native-memory/reviewer keys before any mutation.
7. Remove only legacy root `status_line`, then update the eleven owned paths through TOMLKit nodes. Preserve normal, quoted, dotted, inline, and out-of-order table representations where TOMLKit supports them; mutate an existing statusline array in place to retain element comments and fail closed on comment-bearing destructive shrink.
8. Implement a recursive semantic projection that removes exactly the eleven owned paths, legacy root `status_line`, and empty containers created solely by owned paths. Parse rendered output with `tomllib` and require projected staged semantics to equal projected local semantics and every staged owned value to equal canonical before writing `OUTPUT`.
9. Replace the embedded `CODEX_TOML_MERGER` lexer in `sync-agent-configs.sh` with the locked helper call. Retain shell-owned same-directory staging for normal mode, platform temporary staging for dry-run, comparison, atomic rename, and rollback. Update copied-workspace fixtures to include the helper and lock.
10. Run the standard wired sync entrypoint twice, the focused Python merger suite, helpers, SSO/Hermes readiness regressions, lock-tamper and offline-cache probes, `bash -n`, ShellCheck, Ruff, `git diff --check`, and the diff-only legal scan. Commit only the named Task 2 paths with a conventional pathspec commit.

### Task 3 — Install trusted-repo YOLO launchers with a safe escape

**Files:** `config/agents/codex/trusted-repos.yaml`, `config/agents/codex/launcher/codex`, `config/agents/codex/launcher/codex-safe`, `config/agents/codex/launcher/codex.cmd`, `config/agents/codex/launcher/codex-safe.cmd`, `scripts/agents/install-codex-launcher.sh`, `tests/setup/test_codex_launcher.sh`.

1. Write failing tests using a fake real CLI to capture argv for trusted root, untrusted root, non-Git directory, spaces, quotes, repeated flags, missing real binary, recursion, safe-mode cases, all Git discovery overrides (`GIT_DIR`, `GIT_WORK_TREE`, `GIT_CEILING_DIRECTORIES`, `GIT_COMMON_DIR`, `GIT_INDEX_FILE`, `GIT_OBJECT_DIRECTORY`), symlink/junction/prefix collisions, caller-supplied YOLO/sandbox/approval config, and `-C`/`--cd`/`--add-dir` escapes.
2. Add a real `cmd.exe` integration test on `ace-win-1` using an argv-capture helper for `%`, `!`, `^`, `&`, `|`, empty arguments, quotes, spaces, and trailing backslashes. Repeat it through a named human local run on `ace-win-2` or retain that host as `UNREACHABLE`; static inspection alone will not satisfy Windows correctness.
3. Run the launcher suite and observe RED because the repo-managed artifacts do not exist.
4. Resolve Git roots with Git override variables removed and refuse YOLO if any such variable was supplied. Exact user-approved canonical-path and origin matching will be mandatory; prefix matching and discovery-derived trust will be forbidden.
5. Parse `-C`, `--cd`, and `--add-dir` before launch. Any target outside the same approved root will downgrade to enforced safe mode; unknown directory-changing syntax will fail closed. The implementation and report will state that accepted YOLO remains host-wide authority, not filesystem containment.
6. Make `codex-safe` and every untrusted fallback reject caller-supplied YOLO, remove conflicting approval/sandbox flags and `-c` overrides, and append `--sandbox workspace-write --ask-for-approval on-request` at final CLI precedence. Test that hostile argv and local config cannot override the enforced values.
7. Acquire one per-user deployment lock; stage the pinned CLI pointer, merged config, trust manifest, POSIX/Windows launchers, and PATH verification in a transaction directory. Write a manifest and backups, validate every staged artifact, commit the set, and provide `install-codex-launcher.sh --rollback <transaction-id>` plus interrupted-transaction recovery.
8. Ensure scheduled `codex update` calls the real binary under the same lock rather than resolving through the wrapper.
9. Run shellcheck where available, focused launcher/transaction suites, live `cmd.exe` integration, and real trusted/untrusted/safe smoke tests.
10. Commit the named launcher, policy, installer, and test paths only.

### Task 4 — Preserve goal authorization and converge Claude statusline behavior

**Files:** `config/agents/SHARED_SOUL.md`, `.claude/rules/goal-invocation.md`, `scripts/agents/build-soul-runtime.sh`, `.claude/statusline-command.sh`, `.claude/statusline-combined.sh`, `scripts/_core/sync_statusline.sh`, `tests/statusline/`, existing runtime tests.

1. Write failing tests that require `--yolo` to remain subordinate to the issue/plan/user-approval gates and that require the goal rule to appear exactly once in generated runtimes.
2. Add named failing renderer tests for Linux Bash, Windows Git Bash, and a real Windows execution path; cover workspace-hub, a sibling repo, and a repo without project settings.
3. Implement the smallest policy/runtime and Claude renderer/deployment changes necessary to satisfy those tests.
4. Rebuild generated runtime artifacts using `scripts/agents/build-soul-runtime.sh`; do not hand-edit generated files.
5. Run runtime coherence, statusline, harness-size, and generated-artifact tests.
6. Commit canonical sources, generated outputs, and tests with explicit pathspecs.

### Task 5 — Integrate setup, scheduled updates, and semantic verification

**Files:** `scripts/setup/new-machine-setup.sh`, `scripts/maintenance/update-harness-tools.sh`, `scripts/setup/verify-setup.sh`, `tests/setup/test_new_machine_setup.py`, `tests/setup/test_verify_setup.py`.

This task will start only after Task 1 commits its changes to the shared verifier/test paths; it will extend that baseline and will not run concurrently with Task 1.

1. Add failing tests that require both setup and scheduled maintenance to call the canonical locked transaction in order and require update operations to bypass the launcher.
2. Assert dry-run purity, noninteractive behavior, retry-safe idempotence, lock exclusion, injected failure after every transaction stage, crash recovery, rollback, PATH precedence, and preservation of the prior working install.
3. Implement shared calls instead of duplicated config/wrapper logic.
4. Run focused setup/update tests and the broader setup regression suite.
5. Commit the named paths only.

### Task 6 — Add fleet truth and reconcile the target roster

**Files:** `config/workstations/registry.yaml`, `scripts/readiness/collect-equality.sh`, `scripts/readiness/collect-equality.ps1`, `scripts/readiness/build-equality-matrix.py`, existing readiness tests and fixtures.

1. Write failing Bash, PowerShell-schema, and Python tests for `codex_declared`, `codex_version`, `request_user_input_enabled`, `config_hash`, `launcher_mode`, `trusted_roots_hash`, and evidence freshness.
2. Add fixtures for registry drift, empirically present Codex, unreachable host, stale report, safe-only launcher, and partial rollout.
3. Assert that only direct fresh evidence can produce `EQUAL`; declared intent or successful SSH alone will not.
4. Consume the Task-0 seven-host denominator. Reconcile `ace-linux-1` only after owner-policy validation; do not infer any machine's target status from current declaration or reachability alone.
5. Implement collectors and renderer changes without publishing auth material, paths outside allowed repo-root metadata, prompts, goal text, transcripts, or token values.
6. Run the focused readiness tests and matrix regression suite.
7. Commit registry, collectors, renderer, fixtures, and tests with explicit pathspecs.

### Task 7 — Review, immediate rollout, and durable evidence

**Files:** `scripts/review/results/2026-08-02-code-3555-r1-{claude,codex,agy}.md`, `docs/reports/2026-08-02-issue-3555-codex-fleet-rollout.html`, [#3555](https://github.com/vamseeachanta/workspace-hub/issues/3555).

1. Run focused suites, full relevant regressions, `scripts/legal/legal-sanity-scan.sh`, no-absolute-path enforcement, harness-size checks, and shell/static analysis.
2. Push one candidate commit, record its immutable SHA, and dispatch adversarial T3 code review against that SHA. Every fix will be tested, committed, pushed, and reviewed within the iteration cap; any post-review mutation will invalidate the verdict. Provider outage may degrade T3 to T2 only with a valid `UNAVAILABLE` artifact; invalid output will block and cap exhaustion will return to the user.
3. Enumerate live Codex targets from the reconciled registry and equality evidence immediately before rollout and record the exact set.
4. Attempt the same approved installer sequence on every reachable target in one wave. Do not stop after the first success and do not call any one host a canary.
5. Run a deterministic PTY script in one approved trusted repo and one untrusted directory on every reachable target. It will record the exact version/config SHA, `features list` false-to-true differential, launcher argv, effective approval/sandbox banner, footer selector values, timeout, and pass/fail. A named human will run the same script locally on `ace-win-2` or that host will remain `UNREACHABLE`.
6. Collect fresh equality evidence, render the HTML report, and label each target `EQUAL`, `DIVERGES`, `MISSING-EVIDENCE`, or `UNREACHABLE` with timestamp and command evidence.
7. Comment the implementation/test/review/rollout summary on #3555. Before close, compute the mandatory completeness score, publish its HTML artifact and metadata stamp, and request the owner-only `status:completeness-verified` label. Close only after acceptance criteria and that gate pass; otherwise leave it open with exact residue and next action.
8. Run `.claude/skills/coordination/pre-completion-cleanup-audit/SKILL.md` and resolve unexpected worktrees, stashes, temp clones, locks, and untracked artifacts before completion.

## TDD Test List

| Test | Required result |
|---|---|
| `test_codex_pin_exposes_default_mode_input` | Exact pinned CLI advertises the feature |
| `test_canonical_config_owned_keys` | Approved keys and footer are present; unsupported keys are absent |
| `test_sync_preserves_unowned_nested_tables` | Local trust/MCP/plugin/project/model values survive |
| `test_sync_migrates_legacy_model_ownership` | Dropping the template model never deletes a machine choice |
| `test_sync_malformed_toml_rolls_back` | No partial replacement occurs |
| `test_merge_four_quote_terminator_preserves_following_table` | The frozen R4 silent-loss reproduction becomes green |
| `test_merge_all_r1_r4_toml_forms` | Every reviewed valid-TOML defect class preserves unowned semantics |
| `test_unowned_semantic_projection_rejects_any_mutation` | Delete/insert/mutate/relocate/type-change faults produce no output |
| `test_comment_bearing_statusline_shrink_fails_closed` | CST edits never silently discard comments |
| `test_locked_merger_dependency_fails_atomically` | Missing/stale lock or dependency failure leaves target untouched |
| `test_feature_probe_is_differential` | Isolated CLI state changes request input from false to true |
| `test_footer_ids_match_pinned_allowlist` | Silent-acceptance cannot hide a misspelled footer item |
| `test_launcher_trusted_root_adds_yolo_once` | Fake CLI receives one `--yolo` plus original argv |
| `test_launcher_untrusted_root_is_safe` | No `--yolo` outside exact trusted root |
| `test_untrusted_fallback_overrides_hostile_local_config` | Workspace-write/on-request wins at CLI precedence |
| `test_launcher_rejects_git_env_spoofing` | Git override variables cannot authorize YOLO |
| `test_launcher_downgrades_directory_escape` | `-C`/`--cd`/`--add-dir` outside root cannot retain YOLO |
| `test_launcher_rejects_prefix_collision` | `/repo-evil` cannot match `/repo` |
| `test_launcher_prevents_recursion` | Wrapper paths cannot resolve as real CLI |
| `test_codex_safe_enforces_workspace_write_on_request` | Safe entry overrides dangerous local settings everywhere |
| `test_windows_cmd_forwards_argv_live` | Real `cmd.exe` preserves adversarial argument boundaries |
| `test_transaction_rolls_back_each_stage` | CLI/config/trust/wrappers/PATH recover as one unit |
| `test_transaction_lock_excludes_update` | Scheduled update cannot race installation |
| `test_setup_update_share_installer` | Both lifecycle paths converge through one implementation |
| `test_goal_gate_survives_yolo` | Plan/user approval remains mandatory |
| `test_claude_statusline_machine_and_project_precedence` | Original Claude statusline scope works in three repo shapes |
| `test_all_registry_hosts_classified` | Every one of seven machines has an evidence state |
| `test_equality_requires_fresh_direct_evidence` | Intent and stale evidence cannot produce equality |
| `test_partial_rollout_not_fleet_complete` | Unreachable/missing targets remain explicit |
| `test_evidence_rejects_sensitive_content` | No secrets/prompts/transcripts/token values enter reports |

## Acceptance Criteria

- [ ] Fresh T3 review artifacts are parsable; all Claude/Codex MAJOR findings are resolved inline under the iteration-cap rule, and the user applies `status:plan-approved`.
- [ ] An isolated before/after `codex features list` probe reports `default_mode_request_user_input` false before and true after candidate config on every reachable Codex target.
- [ ] The exact installed CLI version supports the feature; pin/config/verifier agree.
- [ ] The canonical owned-key test proves explicit goals/multi-agent/hooks intent, and live probes prove their recognized feature names/state; default-on behavior without the canonical declarations will not satisfy the criterion. Live/typed probes also verify web search, high plan reasoning, pragmatic personality, resume-CWD, interrupt messaging, and the five pinned statusline identifiers.
- [ ] Config sync uses the committed TOMLKit `0.15.1` PEP 723 lock, contains no hand-written TOML lexer, is atomic/idempotent/dry-run safe, preserves required comments, and proves by independent semantic projection that every unowned local path and value is unchanged.
- [ ] Every R1–R4 silent-loss reproduction passes, and injected unowned delete/insert/mutate/relocate/type-change faults fail closed without creating staged output or changing the target.
- [ ] Plain `codex` adds `--yolo` exactly once only for user-approved roots with matching origins; Git env spoofing and directory escape arguments downgrade safely.
- [ ] `codex-safe` and untrusted fallback enforce workspace-write/on-request despite hostile local config.
- [ ] POSIX and live `cmd.exe` launcher argument/quoting/recursion tests pass.
- [ ] The complete CLI/config/trust/launcher/PATH transaction supports locking, per-stage failure rollback, and crash recovery.
- [ ] Claude native goal and machine-wide statusline behavior remain covered from the original issue.
- [ ] Setup and scheduled maintenance invoke the same pin/config/launcher/verification path.
- [ ] All seven registry machines are probed or explicitly unreachable; every actual Codex-capable host is either a passing target or has an explicit non-success state.
- [ ] No report claims fleet completion while any target is unenumerated, stale, missing, divergent, or unreachable.
- [ ] Focused and relevant regression tests, legal scan, enforcement scripts, and adversarial code review pass.
- [ ] #3555 receives an implementation summary comment with commit, tests, review, and rollout evidence.
- [ ] Completeness score, HTML artifact, metadata stamp, and owner-only `status:completeness-verified` gate pass before close.
- [ ] Pre-completion cleanup audit returns CLEAN or EXPECTED with named residue.

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Claude (historical July r1) | UNAVAILABLE | Authentication unavailable; not evidence for the expanded plan |
| Codex (historical July r1/r2) | MAJOR | Pilot scope, config schema, evidence privacy, and fleet-claim defects; incorporated into this revision |
| Gemini (historical July r1) | UNAVAILABLE | Historical provider unavailable; AGY will be used for fresh review |
| Claude (2026-08-02, superseded) | MAJOR | Git env spoofing, model-key deletion, silent config acceptance, seven-host roster, nonexistent renderer, ordering, coverage, and completeness defects informed the prior revision; the artifact is historical because it fails the current generic verdict parser |
| Codex (2026-08-02, superseded) | MAJOR | Host-wide YOLO risk, directory escapes, safe-mode semantics, trust authorization, live Windows tests, transaction rollback, denominator, immutable review SHA, and template gaps informed the prior revision; the artifact is historical because it fails the current generic verdict parser |
| AGY (2026-08-02, superseded) | UNAVAILABLE | Authentication timed out; the artifact is historical because it fails the current generic verdict parser |
| Task 2 code review rounds 1–4 | MAJOR — replan required | Four distinct valid-TOML silent-loss classes require a grammar-complete CST plus an independent semantic-preservation postcondition |
| Replacement T3 plan review | PENDING | Claude, Codex, and AGY outputs will be machine-parseable; valid UNAVAILABLE may degrade T3 to T2, while INVALID_OUTPUT will block |

**Overall result:** NOT APPROVAL-READY — implementation will remain frozen at `723d58e426ddbb189bf7fe2ccf0b497236b270b4` until the revised Task 2 architecture receives fresh, machine-parseable adversarial review with no unresolved MAJOR finding. The issue will move from `status:needs-plan` to `status:plan-review` only after that evidence is pushed, then will stop for renewed owner approval.

## Risks and Open Questions

- **Under-development feature:** `default_mode_request_user_input` may change upstream. The exact pin and live feature probe will make failure explicit; upgrades will not float silently.
- **Approval bypass risk:** `--yolo` is intentionally host-wide authority and exact-root matching is authorization, not containment. Owner-approved roots/origins, Git-env and directory-argument downgrade, enforced safe fallback, revocation, and governance tests will bound when that authority activates.
- **Windows quoting risk:** `.cmd` parsing differs from POSIX shells. Fake-CLI argument capture and static tests will cover metacharacter/space cases before rollout.
- **Roster drift:** `ace-linux-1` contradicts the registry, while four other hosts were not in the initial three-host probe. All seven registry machines will be classified before any denominator claim.
- **Immediate rollout blast radius:** there will be no canary by user direction. Atomic installers, backups, dry-run/verification, and `codex-safe` will provide rollback and continued access.
- **Locked CST dependency:** the merger will depend on TOMLKit `0.15.1` through a committed PEP 723 uv lock rather than the full workspace environment. Missing uv, missing/stale lock, unavailable dependency cache/network, license drift, or hash mismatch will fail before local config changes; setup/rollout evidence will attest the exact lock and package hash.
- **CST normalization:** TOMLKit may normalize physical placement for nested array-of-table declarations. Acceptance will require unchanged unowned parsed semantics, preserved comments, and second-run byte identity; it will not require first-run byte identity for formatting that the documented CST intentionally normalizes.
- **Review tooling drift:** existing plan-fanout artifacts and the generic validator disagree on verdict syntax. Replacement reviews will be validated before they count; an artifact that exists but parses as `INVALID_OUTPUT` will block rather than degrade the provider count.
- **Provider availability:** a valid `UNAVAILABLE` review artifact may degrade T3 to T2; malformed or unparsable output will block.

## Complexity: T3

Cross-platform launch behavior, a security-relevant approval bypass, nested config preservation, provider UX convergence, roster reconciliation, and live multi-machine rollout require three-provider adversarial review and system-level regression coverage.
