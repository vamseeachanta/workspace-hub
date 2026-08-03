# Disagreement report — plan #3555 (2026-08-02)

## Verdicts

| Provider | Verdict |
|---|---|
| agy | UNAVAILABLE (agy CLI failed, rc=1: # agy dispatch failed (rc=1):  Waiting for authentication (timeout 60s)... Or, paste the authorization code here and press Enter: Error: authentication timed out. Error: authentication failed or timed out ) |
| claude | **MAJOR** |
| codex | MAJOR |

## Findings unique to each provider

A finding is 'unique to X' if its text appears in X's artifact but not
verbatim in any other provider's artifact.

### agy

- (none)

### claude

- **1. The trusted-root check is spoofable through git environment variables — empirically demonstrated. (Pseudocode line 185: `root := git rev-parse --show-toplevel or empty`)**
- From an untrusted directory:
- ```
- $ cd /tmp/.../untrusted && git rev-parse --show-toplevel
- fatal: not a git repository
- $ cd /tmp/.../untrusted && GIT_DIR=$TRUSTED/.git GIT_WORK_TREE=$TRUSTED git rev-parse --show-toplevel
- /tmp/tmp.yxEOYmJkYE/trusted        # ← reports TRUSTED while cwd is untrusted
- ```
- The launcher would then `exec real --yolo` (= `approval: never`, `sandbox: danger-full-access`, per the `codex exec` banner in the Codex `.err`) with the process's actual cwd untrusted. `GIT_DIR` is exported into every git hook, so invoking `codex` from any hook — this repo added a pre-push extension point in 13c39615f's parent 9cfe69501 — inherits it. Test list line 292/293 covers prefix collision and recursion; **no test covers `GIT_DIR`, `GIT_WORK_TREE`, or `GIT_CEILING_DIRECTORIES`**, and Task 3 step 4 does not mention sanitizing the environment before resolving the root.
- **2. Removing `model` from the template will silently strip every machine's local model setting — directly contradicting the plan's own Global Constraint.**
- Task 1 step 4: *"do not set a hardcoded model."* But `scripts/_core/sync-agent-configs.sh:409` hardcodes `managed_keys = {'model', 'model_reasoning_effort'}`, and `managed_line_re` (line 411) unconditionally deletes matching lines from the **local target** (call sites 703, 884) as well as the template (844). Once those keys leave the template, the sanitizer still deletes them from `~/.codex/config.toml` and nothing re-adds them — every rolled-out machine silently falls back to Codex's built-in default model. Global Constraint line 29 promises *"The merger will preserve auth, trust, MCP/plugin, project, **model**, and machine-local keys."* The plan never describes this managed→unowned migration, and no entry in the TDD Test List (lines 286–300) covers it.
- **3. "Validate candidate with installed Codex" (pseudocode line 178) cannot detect the failure modes this plan actually risks.**
- There is no `codex config` subcommand (verified via `codex config --help`, which prints top-level help). `codex doctor` under a candidate `CODEX_HOME` reported auth/terminal/git/runtime and **no config section at all**. What validation does exist is partial:
- | Probe | Result |
- |---|---|
- | broken TOML syntax | rc=1 ✓ |
- | invalid enum on known scalar (`personality`) | rc=1 ✓ |
- | **bogus root key** (`totally_bogus_key_xyz`) | **rc=0, silently accepted** |
- | **bogus `[features]` name** (`completely_made_up_feature`) | **rc=0, silently accepted** |
- | **bogus `[tui].status_line` field** (`not-a-real-field-xyz`) | **rc=0, silently accepted** |
- So a typo in any feature name or footer identifier passes validation and rolls out fleet-wide as a silent no-op. Acceptance Criterion line 307 requires those keys be *"effective"*, and line 305 requires `default_mode_request_user_input = true` be *"present in effective config"* — presence is satisfiable by echoing the file back. TDD test `test_canonical_config_owned_keys` (line 287) asserts *"Approved keys and footer are present"* in the template, i.e. it asserts the file contains what the implementer typed into it. None of these distinguishes effective from silently-ignored. The plan never names a validation command anywhere.
- **4. The fleet denominator is misstated; the "no canary, one wave" framing describes at most two hosts, one of which is unreachable by design.**
- Plan lines 112–116 present a *"Current registry probe"* listing 3 machines. `config/workstations/registry.yaml` declares **7**: `ace-linux-1`, `ace-linux-2`, `ace-win-1`, `ace-win-2`, `gpu-claw`, `Vamsees-MacBook-Air`, `shoerack`. Four are omitted without a stated exclusion rule — and the plan's own reasoning for adding `ace-linux-1` (empirical Codex contradicts declaration, line 58) applies identically to the four it never probed. This violates Acceptance Criterion line 313 (*"Every actual Codex-capable host is enumerated"*) inside the plan's own evidence block.
- Worse, of the two hosts that *do* declare codex, `ace-win-2` (lines 283–320) has `ssh: null`, `tailscale_ip: null`, `dispatch_enabled: false`, `sync_policy: manual-status-only`. It is not remotely actionable. Task 7 step 5 — *"Open a fresh interactive Codex session … on every reachable target"* — is unexecutable there without a human at the physical box, and the plan assigns every task to agentic workers (line 12) with no human-in-loop step. The Risks section (line 338) discusses *"immediate rollout blast radius"* and *"no canary by user direction"* as if the wave were wide; the actionable set is `ace-win-1` plus the planning host itself.
- **5. `config/agents/claude/statusline.mjs` does not exist, and the Tech stack's "Node.js for the existing Claude renderer" is false.**
- `git ls-files | grep -E '\.mjs$'` returns **zero results repo-wide**. The file is named in the Artifact Map (line 139) and in Task 4's Files list (line 238). The actual renderer that `scripts/_core/sync_statusline.sh:7` deploys is `SOURCE_SCRIPT="$WORKSPACE_HUB/.claude/statusline-command.sh"` — a Bash script, copied to `$target_dir/statusline-command.sh` (line 38) and wired via `jq` into `settings.json` (line 51). Task 4 step 3 (*"Implement the smallest … Claude renderer/deployment changes"*) and step 2 (*"cross-shell renderer fixtures"*) therefore target a non-existent artifact in a language the renderer isn't written in.
- **6. The fresh T3 review the plan gates on has already run and produced blocking-grade output, which the plan records as "PENDING".**
- `scripts/review/results/` contains, dated today:
- ```
- 2026-08-02-plan-3555-claude.md      0 bytes
- 2026-08-02-plan-3555-codex.md       0 bytes   (+ 532 KB .err, ends in hook noise, no VERDICT emitted)
- 2026-08-02-plan-3555-agy.md       439 bytes   UNAVAILABLE (auth timed out)
- 2026-08-02-plan-3555-claude.md.err          "this workspace has not been trusted"
- ```
- Two artifacts **exist but contain no parsable verdict**. Global Constraint line 24 and Task 7 step 2 (*"invalid output will block"*) — matching the repo's standing rule that an artifact which exists but fails verdict parsing is INVALID_OUTPUT and blocks rather than degrades — make this a blocked state, not the *"PENDING — fresh adversarial review required"* recorded at lines 326–328. Separately, the plan cites these artifacts at lines 10 and 143 with an **`r3-` infix** (`2026-08-02-plan-3555-r3-{claude,codex,agy}.md`) that the fanout does not produce; the Artifact Map points at filenames that will never exist.
- **7. Task 3 depends on an output Task 6 has not yet produced.**
- Task 3 step 4 (line 230) derives the launcher allowlist *"from the registry plus live attestation."* The registry reconciliation of `ace-linux-1` is Task 6 step 4 (line 264), and Task 6 step 4 further conditions it on *"a live attestation confirms that Codex is intended there."* Executing tasks in the stated order builds the trusted-root allowlist from a registry the plan has already identified as wrong (line 58), on the planning host that is the misdeclared entry.
- **8. Acceptance Criterion line 311 has no corresponding test.**
- *"Claude native goal and machine-wide statusline behavior remain covered from the original issue"* — the TDD Test List (lines 286–300) contains 15 entries; the only Claude-adjacent one is `test_goal_gate_survives_yolo` (line 297), which tests the approval gate, not statusline convergence. Task 4 step 2 describes cross-shell renderer fixtures that never appear in the test list. The original #3555 scope is the one part of this plan with acceptance but no named test.
- **9. Three of the four `[features]` keys are already `true` by default, making Acceptance Criterion line 307 non-discriminating.**
- ```
- goals        stable  true
- hooks        stable  true
- multi_agent  stable  true
- personality  stable  true
- ```
- Line 51 states the rationale (*"declaring them explicitly will make fleet intent auditable"*), which is defensible for the config. But AC line 307 asserts these are *"effective"* — that criterion passes on an untouched machine before any code is written, and combined with Finding 3 (bogus feature names accepted silently) it would also pass if the keys were misspelled. `default_mode_request_user_input` is the only one of the four that actually changes state.
- **10. Issue #3555 carries `gate:completeness`, which the Acceptance Criteria do not satisfy.**
- `gh issue view 3555` returns label `gate:completeness` — *"Opt-in: completeness score required before close (#2798)."* Task 7 step 7 (line 279) says *"Close only after acceptance criteria pass"*, and the Acceptance Criteria (lines 304–317) contain no completeness score. As written the plan reaches its own definition of done while the issue's close gate is unmet.

### codex

- **The trusted-root check does not contain YOLO execution.** Plan §Global Constraints line 27 and pseudocode lines 184–187 imply that exact-root matching bounds the approval/sandbox bypass. Installed Codex 0.146.0 describes `--dangerously-bypass-approvals-and-sandbox` as unsandboxed host execution and supports `-C/--cd` and `--add-dir`. Starting in an allowed root with `codex -C /untrusted/path` therefore passes the wrapper check before Codex changes roots; unsandboxed commands can also access paths outside the repository. The plan must either require external containment or explicitly accept host-wide access, and must reject or re-evaluate `-C`, `--cd`, and `--add-dir`.
- **`codex-safe` is not guaranteed safe.** Pseudocode lines 181–187 and Task 3 line 232 define safety only as “do not add `--yolo`.” Global Constraint line 29 deliberately preserves local approval and sandbox settings, so `codex-safe` may still inherit `approval_policy = "never"` and `sandbox_mode = "danger-full-access"`. Either rename it `codex-raw` or inject and test highest-precedence safe approval/sandbox settings.
- **Trust authorization is undefined and can be derived from non-authoritative inventory.** Task 3 line 230 generates the allowlist from the registry plus “live attestation,” but neither the plan nor `config/workstations/registry.yaml` defines who approves trust, expected repository origin, policy precedence, revocation, expiry, permissions, or case/UNC/junction normalization. Merely finding a checkout cannot authorize unsandboxed execution. The proposed `trusted-repos.yaml` needs an explicit user-approved schema and machine-local materialization contract.
- **Windows correctness is claimed from static inspection.** Task 3 line 228 proposes static `%*` checks, while TDD line 295 and Acceptance Criterion line 310 claim argument-boundary and quoting correctness. `cmd.exe` reparses `%*`; static text checks cannot prove handling of `%`, `!`, `^`, `&`, `|`, empty arguments, quotes, or trailing backslashes. `config/workstations/registry.yaml:245-247,297-299` declares Bash but not a native test runtime on the Windows targets. A real `cmd.exe` integration test with an argv-capture executable is required.
- **Fleet mutation is not transactional despite the rollback claim.** Tasks 1–6 independently mutate the CLI, config, trust policy, wrappers, PATH behavior, registry, and evidence, but define no cross-platform lock, transaction manifest, commit point, rollback command, or crash recovery. Meanwhile `scripts/maintenance/update-harness-tools.sh:163` invokes `codex update` through PATH, allowing a concurrent update or wrapper interception. Risks line 338 claims atomic installers and backups provide rollback, but only individual-file replacement and wrapper backup are planned.
- **Fleet completeness is circular.** Resource Intelligence line 58 admits the registry is incomplete. Rollout pseudocode lines 189–195 starts from declared Codex targets and adds empirical hosts only after they are already known; Task 6 line 264 handles only the known `ace-linux-1` discrepancy. No authoritative fleet enumeration command probes every active machine for Codex. Consequently Acceptance Criteria lines 313–314 cannot prove that every actual Codex-capable host was enumerated or that none remains unenumerated.
- **The Claude implementation target does not exist.** Artifact Map line 139 and Task 4 line 238 name `config/agents/claude/statusline.mjs`; it is absent from both the filesystem and `HEAD`. The tracked implementation is `.claude/statusline-command.sh` plus `.claude/statusline-combined.sh`, with tests under `tests/statusline/`. Those actual paths are omitted from the task’s file ownership and named-test contract, leaving Acceptance Criterion line 311 non-executable.
- **Mandatory workflow gates are omitted.** The plan header’s “Execution mode” is not one of the required `single-lane`, `parallel-readonly`, or `parallel-worktree` classifications from `.claude/skills/coordination/issue-planning-mode/SKILL.md` and `docs/standards/PARALLEL_FIRST_EXECUTION.md`. Tasks 1 and 5 overlap on `scripts/setup/verify-setup.sh` and `tests/setup/test_verify_setup.py` without serialization ownership. Task 7 line 279 also omits the mandatory completeness score, HTML artifact, metadata stamp, and owner-only `status:completeness-verified` gate required before closing #3555.
- **Review fixes are not bound to the rolled-out revision.** Task 7 line 274 says to resolve code-review MAJOR findings, then lines 275–278 proceed directly to rollout. It does not require fixes to be retested, committed, pushed, re-reviewed, or tied to a recorded commit SHA. The deployed artifacts can therefore differ from the reviewed artifacts.
- **Acceptance claims exceed the defined tests.** Task 3 lacks dynamic tests for installer backup, PATH precedence, rollback, or failure after each installation stage. Acceptance line 307 claims every setting is effective, but the named test at line 287 checks only canonical config structure. Task 7 line 277 provides no deterministic prompt, observable pass condition, timeout, or machine-readable evidence for Default-mode `request_user_input`. These checks can pass on declared/configured intent without proving runtime behavior.
- **The plan does not conform to its required template and contains a command-policy violation.** It omits the mandatory `## Files to Change` section required by `docs/plans/_template-issue-plan.md:160-168`; several generated outputs, fixtures, and test paths remain unnamed. Task 1 line 205 invokes bare `pytest`, contradicting the repository’s `uv run` requirement. A direct `scripts/enforcement/check-no-abs-paths.sh` scan also flags the machine-specific absolute path at plan line 43.

