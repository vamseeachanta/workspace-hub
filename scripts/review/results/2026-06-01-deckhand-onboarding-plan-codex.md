**Deckhand Onboarding Runbook**

Read-only result. I did not modify files. The requested recon file `scripts/review/results/2026-06-01-deckhand-wiring-recon-codex.md` is missing at that exact path, so anything dependent on that artifact is **UNVERIFIED**.

**Ground Truth**
- Scope config: [scopes.yml](/mnt/local-analysis/workspace-hub/config/deckhand/scopes.yml:17)
- Enforcement plugin: [__init__.py](/mnt/local-analysis/workspace-hub/scripts/deckhand/hermes-plugin/deckhand-scope/__init__.py:1)
- Glossary: [CONTEXT.md](/mnt/local-analysis/workspace-hub/CONTEXT.md:35)
- Roadmap risks: [2026-06-01-deckhand-improvement-roadmap.md](/mnt/local-analysis/workspace-hub/docs/plans/2026-06-01-deckhand-improvement-roadmap.md:10)
- Env var names present in `~/.hermes/.env`: `TELEGRAM_ALLOWED_USERS`, `DECKHAND_PAT_ACMA`, `DECKHAND_PAT_DORIS`. Secret values were not printed.

**Current Mechanics**
Deckhand has two authorization layers:
1. Telegram gateway layer: `TELEGRAM_ALLOWED_USERS` controls who can talk to Hermes. Hermes checks this allowlist by Telegram numeric `user_id`; no allowlist means fail-closed unless allow-all is set. Evidence: `/home/vamsee/.hermes/hermes-agent/gateway/platforms/telegram.py:552`, `/home/vamsee/.hermes/hermes-agent/gateway/run.py:6761`.
2. Deckhand scope layer: each scope has `operators`, and the plugin denies writes unless the sender is authorized for the resolved scope. Evidence: [__init__.py](/mnt/local-analysis/workspace-hub/scripts/deckhand/hermes-plugin/deckhand-scope/__init__.py:55), [engine.py](/mnt/local-analysis/workspace-hub/src/deckhand/engine.py:58).

Scope selection today is DM-bound unless `/scope` is usable. The plugin would support `/scope` state, but current facts say the `/scope` command is unavailable until a Hermes core patch. Without `/scope`, `_scope_from_binding()` selects a scope by exact `platform + chat_id`, then checks the operator is listed. Evidence: [__init__.py](/mnt/local-analysis/workspace-hub/scripts/deckhand/hermes-plugin/deckhand-scope/__init__.py:253), [__init__.py](/mnt/local-analysis/workspace-hub/scripts/deckhand/hermes-plugin/deckhand-scope/__init__.py:280).

**Add User To ACMA**
1. Get the person’s stable Telegram numeric ID. Use the numeric sender/user id, not username/display name. Confirm the DM `chat_id`; for current POC it is treated as the same numeric id.
2. Add that id to `TELEGRAM_ALLOWED_USERS` in `~/.hermes/.env`, comma-separated with existing ids.
3. Add that same id to `scopes.acma.operators` in [scopes.yml](/mnt/local-analysis/workspace-hub/config/deckhand/scopes.yml:24).
4. Add one `channel_repo_bindings` entry under `acma` for that user’s DM:
   ```yaml
   - platform: telegram
     channel_id: "<telegram_numeric_dm_chat_id>"
     repo: vamseeachanta/llm-wiki-acma
   ```
   Existing ACMA binding is the owner DM to `llm-wiki-acma`: [scopes.yml](/mnt/local-analysis/workspace-hub/config/deckhand/scopes.yml:26).
5. Restart Hermes gateway so `.env` changes are loaded. Command shape is `hermes gateway restart`; system install uses `sudo $(which hermes) gateway restart --system`. Evidence: `.claude/skills/autonomous-ai-agents/hermes-agent/SKILL.md:145`.
6. Verify from that user’s Telegram DM: an allowed read command should work; a write from inside `llm-wiki-acma` should be allowed; destructive commands should block.

**Add User To DORIS**
1. Get the person’s stable Telegram numeric ID and confirm the DM `chat_id`.
2. Add that id to `TELEGRAM_ALLOWED_USERS` in `~/.hermes/.env`.
3. Add that id to `scopes.doris.operators` in [scopes.yml](/mnt/local-analysis/workspace-hub/config/deckhand/scopes.yml:43).
4. Add one `channel_repo_bindings` entry under `doris`:
   ```yaml
   - platform: telegram
     channel_id: "<telegram_numeric_dm_chat_id>"
     repo: vamseeachanta/llm-wiki-doris
   ```
   Current Doris has no binding: [scopes.yml](/mnt/local-analysis/workspace-hub/config/deckhand/scopes.yml:45).
5. Restart Hermes gateway for `.env`.
6. Verify from that user’s Telegram DM: writes should target `vamseeachanta/llm-wiki-doris`; `vamseeachanta/doris` should be readable/reference only.

**Doris Gap**
Doris is not usable through DM-bound scope selection until it has a `channel_repo_bindings` entry. The scope exists, has `DECKHAND_PAT_DORIS`, has operator `8748731589`, and lists both repos, but `channel_repo_bindings: []` means origin-bound resolution has nothing to match.

Also verify `DECKHAND_PAT_DORIS` effective permissions before live use. It must cover:
- `vamseeachanta/llm-wiki-doris` with intended write capability.
- `vamseeachanta/doris` with read-only/reference capability.

The config marks `vamseeachanta/doris` as `{ reference: true, read_only: true }`; engine denies writes when a target repo has `read_only`. Evidence: [scopes.yml](/mnt/local-analysis/workspace-hub/config/deckhand/scopes.yml:38), [engine.py](/mnt/local-analysis/workspace-hub/src/deckhand/engine.py:75).

**Multi-User Reality**
With DM-bound scope selection, one Telegram DM has one effective binding at a time. Multiple users can coexist for the same scope by adding one binding per user DM.

Limitation: a single user authorized for both `acma` and `doris` cannot cleanly drive both scopes from the same Telegram DM at the same time. The binding match returns the first matching scope in config order, and `acma` appears before `doris`. So if user `X` has both:
- `acma.channel_repo_bindings[].channel_id: X`
- `doris.channel_repo_bindings[].channel_id: X`

then the DM will resolve to `acma` first under current ordering. Quantified: today it is effectively **one active DM-bound scope per Telegram DM**. The `/scope` core patch becomes necessary as soon as one operator needs to switch between `acma` and `doris` from the same DM.

**PAT Recommendation**
For first external onboarding, use one shared fine-grained PAT per scope, not per user, if the immediate goal is controlled POC operation. The audit already records `operator`, `platform`, `scope`, `repos`, command, and decision in the plugin. Evidence: [__init__.py](/mnt/local-analysis/workspace-hub/scripts/deckhand/hermes-plugin/deckhand-scope/__init__.py:360).

But this is only acceptable if actions do not need GitHub-native per-human attribution. If client-facing audit needs GitHub commits/PRs attributable to each operator, move to per-user tokens or GitHub App user-to-server attribution later. Current larger blocker is more basic: the plugin explicitly does **not** inject scope PATs, so allowed `git/gh` still run with ambient credentials until B2 scoped-PAT executor. Evidence: [__init__.py](/mnt/local-analysis/workspace-hub/scripts/deckhand/hermes-plugin/deckhand-scope/__init__.py:1), roadmap [line 13](/mnt/local-analysis/workspace-hub/docs/plans/2026-06-01-deckhand-improvement-roadmap.md:13).

**First External User Checklist**
- Confirm external user’s stable Telegram numeric id and DM chat id.
- Add id to `TELEGRAM_ALLOWED_USERS`.
- Add id only to intended scope `operators`; never `ecosystem`.
- Add exactly one DM binding for that user initially: either `acma` or `doris`, not both, until `/scope` works.
- Confirm `DECKHAND_ENFORCE` is block mode, not report mode. Env name exists; value not inspected.
- Confirm `DECKHAND_PAT_ACMA` / `DECKHAND_PAT_DORIS` exist and have least privilege. Values not inspected.
- Restart gateway after `.env`.
- Run a non-destructive smoke test from the external Telegram DM.
- Run a destructive-command negative test and confirm it blocks.
- Inspect audit for the external operator id, scope, repo, and decision.

**Blockers Before Safe External Live Write**
- B2 scoped-PAT executor is not landed; allowed commands still use ambient credentials.
- Doris lacks a DM binding.
- A user needing both ACMA and Doris from one DM needs `/scope` core patch or separate routing.
- Requested wiring recon artifact is missing at the specified path, so live wiring assertions from that file are **UNVERIFIED**.
