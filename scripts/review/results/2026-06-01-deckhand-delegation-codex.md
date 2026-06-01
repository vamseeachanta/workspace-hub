## VERDICT: CHANGES-REQUESTED

## Missing tasks (ranked, with where they slot in the sequence)

1. **Publish/reconcile artifacts before approval.** Slot: before [#2931](https://github.com/vamseeachanta/workspace-hub/issues/2931) can be approved. The reviewed plan/config artifacts are currently untracked (`docs/plans/...`, `config/deckhand/`, review artifacts), while [#2931](https://github.com/vamseeachanta/workspace-hub/issues/2931) is only `status:plan-review`. Owner approval against untracked/local-only artifacts is not a durable gate.

2. **Scoped PAT provisioning task.** Slot: before any write-capable test, canary, or external tester access. The POC says per-scope fine-grained PAT is mandatory (`docs/plans/2026-06-01-issue-2931-deckhand-message-lifecycle-poc.md:140`, `:164`), but there is no board task/issue for PAT creation, repository restriction verification, token env-var naming, rotation, revocation, or proof that each scope uses only its PAT.

3. **Bypass-test suite task.** Slot: after PAT provisioning and before hook/shim acceptance. The plan names 7 bypass paths (`...poc.md:158`) and says tests should cover bypass paths (`:162`), but the board has no explicit test task to prove `execute_code`, MCP stdio, direct `gh`, checkpoint git, CLI destructive git, internal probes, and release script paths are denied or contained.

4. **Canary plan approval task.** Slot: before live cutover. Board task `t_3d352af0` maps to [#2741](https://github.com/vamseeachanta/workspace-hub/issues/2741), but that issue is still `status:needs-plan`; it cannot be used as a live guardrail until planned, reviewed, approved, and implemented.

5. **Operator-ID intake and authorization task.** Slot: before external members test. `config/deckhand/operators.yml:13-32` has no members and empty `acma`/`doris` operator groups. The delegation plan lists this as owner input (`...delegation-plan.md:46`) but not as a blocking board task with validation.

6. **Rollback/kill-switch task.** Slot: before external testing. Missing: disable Deckhand writes globally, revoke one scope token, disable one operator, disable one platform, revert PATH shim/hook, and verify audit after rollback.

7. **Rate-limit / abuse-control task.** Slot: before external testing. Missing controls for Telegram/group spam, repeated write requests, GitHub secondary-rate-limit handling, retry budgets, and “submitted too quickly” throttling.

8. **Repo membership decision task.** Slot: before PAT repository restriction. `acma-projects` is archived and `llm-wiki-doris` is planned (`...poc.md:153-154`, `config/deckhand/scopes.yml:20`, `:30`). Those cannot remain “OPEN” while provisioning real write tokens.

## Misassignment / delegation gaps

The high-level split is directionally sound: Claude/main owns synthesis and governance; Codex owns recon, adversarial review, and post-approval build (`...delegation-plan.md:7-12`).

Gaps:

- Codex should own **schema/parser test design** for the YAML surface, not just build hooks. Claude-authored YAML is fine, but Codex should verify fail-closed parsing, missing-file behavior, unknown keys, invalid repo bindings, and policy overrides.
- Codex should own **bypass harness design** for the 7 bypass paths. This is not just implementation; it is adversarial containment testing.
- PAT provisioning should not be assigned to Codex as a blind build task. It needs an owner/operator step for token creation plus a Codex verification step that inspects effective permissions without exposing secrets.
- Board/issue reconciliation should be delegated to Codex or another reviewer before approval. The current board says “12 ready tasks,” but the real dependencies are not encoded.

## Sequencing & gate risks

- **Plan-approved gate is still closed.** [#2931](https://github.com/vamseeachanta/workspace-hub/issues/2931) is live `status:plan-review`; no `.planning/plan-approved/2931.md` exists. Any live cutover before owner label/marker is a governance failure.

- **POC scope contradicts guardrail floor.** The POC boundary says per-scope PAT provisioning is out of scope/recon-blocked (`...poc.md:19`), but the go-live floor makes PAT mandatory (`:140`). This must be resolved before approval.

- **Build sequence puts PAT too late.** Tests/config are listed before PAT provisioning (`...poc.md:162-164`). Any test that touches real repos before scoped PAT proof can run under ambient credentials and falsely pass.

- **Diff-risk gate is underspecified.** `policy.yml:30-38` defines thresholds/protected paths, but there is no approval model for elevated edits, no diff parser contract, no rename/binary/submodule handling, and no proof it runs before PR creation.

- **Origin-bound default is enabled while bindings are empty.** `scopes.yml:46-51` enables origin-bound default; `data-locations.yml:28` has `channel_repo_bindings: []`. That is fail-closed if implemented correctly, but it needs an explicit test because a fallback to prose would reopen the prior blocker.

## Board hygiene findings

- Live board DB has 12 tasks, all `ready`, and no `task_links`. That is wrong for a gated tree: `t_3d352af0` depends on [#2931](https://github.com/vamseeachanta/workspace-hub/issues/2931) approval and [#2741](https://github.com/vamseeachanta/workspace-hub/issues/2741) planning; fanout tasks depend on [#2901](https://github.com/vamseeachanta/workspace-hub/issues/2901)/[#2902](https://github.com/vamseeachanta/workspace-hub/issues/2902)/[#2903](https://github.com/vamseeachanta/workspace-hub/issues/2903).

- `t_d36d4625` comment claims `config/deckhand/repository-allowlists.yml`, but the actual config is split across `scopes.yml`, `operators.yml`, `policy.yml`, `data-locations.yml`, and `platforms.yml`. The POC still cites the missing path at `...poc.md:156` and `:163`.

- `t_df8756ca / t_7cfe94f6 / t_7731a586` are grouped as “operational,” but their issues differ materially: [#2563](https://github.com/vamseeachanta/workspace-hub/issues/2563) is `status:plan-approved`, while [#1881](https://github.com/vamseeachanta/workspace-hub/issues/1881) and [#1885](https://github.com/vamseeachanta/workspace-hub/issues/1885) have no `status:plan-approved` label. Split or block them.

- `t_a6d843ec` maps to [#2906](https://github.com/vamseeachanta/workspace-hub/issues/2906), which already has a “Deckhand” decision in the issue body but remains `status:needs-plan`. Either close/relabel as decision captured, or keep it out of the live cutover path.

## Config-externalization gaps

The “all config in YAML, nothing in code, industry-generic” goal is achievable, but not complete as scoped.

Missing or weak surfaces:

- **Token binding:** no per-scope `pat_env` / credential reference. `policy.yml:70` only says `scoped_pat: true`.
- **Tenant policy overrides:** `scopes.yml:22` has only a commented `action_policy`.
- **Approval/elevation policy:** protected path edits require elevated approval (`policy.yml:34`), but no YAML defines approvers, expiry, evidence, or denial behavior.
- **Rate limits:** no per-operator/per-scope/per-platform rate policy.
- **Rollback/kill switches:** no YAML for disabling a scope, operator, platform, write mode, or all external testers.
- **Audit durability proof:** `data-locations.yml:12-15` leaves raw audit sink as a placeholder/default path, not a verified durable private sink.
- **Channel bindings:** `data-locations.yml:28` is empty, so origin-bound default cannot be tested for real repos yet.
- **Repo metadata:** archived/planned/read-only repo state is comments only, not typed config.
- **Platform credentials:** Telegram has `token_env`; WhatsApp has no session/QR store reference; Teams lacks webhook/public endpoint/config references beyond env names.

Read-only evidence note: `hermes kanban list/show` could not run in this sandbox because it attempted to create `/home/vamsee/.hermes/.../kanban.db.init.lock`; I inspected the board DB read-only with SQLite `immutable=1` instead.
