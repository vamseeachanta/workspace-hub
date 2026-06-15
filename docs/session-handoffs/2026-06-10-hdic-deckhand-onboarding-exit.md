# client-e Deckhand onboarding exit handoff — 2026-06-10

## Task

Create the client-e / H-D Independent Consulting Deckhand client channel for Howard Day, update onboarding collateral with the live Telegram link, and follow the existing Deckhand/client-wiki workflow instead of an ad hoc path.

## Current state

client-e is partially activated. The Telegram channel, private wiki scaffold, Deckhand scope binding, gateway allowlist, client voice prompt, and onboarding collateral are in place. Bot-backed wiki work is still blocked on the client-e repository credential.

## Completed

- Created live Telegram group `client-e` through the governed operator path:
  - chat id: `-5270275602`
  - invite: `https://t.me/+Vpx-nxiPMe5hOTkx`
  - audit evidence: `/mnt/dde/deckhand/audit/operator-actions.ndjson` rows 24-25 show approved create-group attempt and success.
- Created private GitHub repo: `https://github.com/vamseeachanta/llm-wiki-client-e`.
- Cloned and bootstrapped private wiki scaffold at `/mnt/local-analysis/llm-wiki-client-e`.
- Pushed initial scaffold commit:
  - `6432492 feat: bootstrap private client llm-wiki for client-e`
- Added client-e entry to `workspace-hub/config/client-wikis.yml`:
  - `short_name: client-e`
  - `repo: vamseeachanta/llm-wiki-client-e`
  - `local_working_clone: /mnt/local-analysis/llm-wiki-client-e/`
  - `status: bootstrapped`
  - `raw_roots: /mnt/ace/client-e/`
- Added Deckhand scope binding in `/mnt/local-analysis/deckhand/config/deckhand/scopes.yml`:
  - scope: `client-e`
  - repo: `vamseeachanta/llm-wiki-client-e`
  - pat env: `DECKHAND_PAT_client-e`
  - Telegram binding: `-5270275602`
  - `authorize_members: true`
- Updated Deckhand generic docs/config:
  - `/mnt/local-analysis/deckhand/docs/deckhand/ONBOARDING.md`
  - `/mnt/local-analysis/deckhand/config/deckhand/voice-client-channels.md`
- Synced gateway group allowlist:
  - `scripts/deckhand/sync-group-allowlist.sh --apply`
  - `scripts/deckhand/sync-group-allowlist.sh` now reports in sync.
- Added client-e channel prompt to live Hermes config:
  - `~/.hermes/config.yaml`
  - `telegram.channel_prompts['-5270275602']` exists.
- Restarted Hermes gateway:
  - `hermes gateway restart`
  - gateway active after restart, PID observed as `3349798`.
- Updated private strategy/onboarding collateral in `/mnt/local-analysis/aceengineer-strategy`:
  - `strategy/deckhand/outreach/2026-06-10-client-e-howard-day-onboarding.md`
  - `strategy/deckhand/onboarded-roster.md`
  - `strategy/deckhand/release/build/build_pamphlets.py`
  - `strategy/deckhand/release/deckhand-client-e-pamphlet.html`
  - `strategy/deckhand/release/pdf/deckhand-client-e-pamphlet.pdf`
  - `strategy/deckhand/release/assets/qr-client-e.svg`

## Verification run

- `PYTHONPATH=. uv run pytest tests/deckhand/test_scopes_bindings.py tests/deckhand/test_cross_client_isolation.py tests/deckhand/test_channel_prompts.py`
  - result: `62 passed, 1 skipped`
- `git diff --check`
  - passed in `deckhand`
  - passed in `aceengineer-strategy`
  - passed for `workspace-hub/config/client-wikis.yml`
- YAML parse:
  - `/mnt/local-analysis/deckhand/config/deckhand/scopes.yml` OK
  - `/mnt/local-analysis/workspace-hub/config/client-wikis.yml` OK
- Deny-list scan using `/mnt/local-analysis/workspace-hub/.legal-deny-list.yaml` over changed client-e text artifacts and PDF text:
  - result: pass
- Route probe:
  - command: `HERMES_SESSION_USER_ID=8748731589 HERMES_SESSION_PLATFORM=telegram HERMES_SESSION_CHAT_ID=-5270275602 PYTHONPATH=src python3 -m deckhand.shim_resolve`
  - result: `DECKHAND_PAT_client-e`
- App token probe:
  - command: `PYTHONPATH=src python3 -m deckhand.app_token DECKHAND_PAT_client-e`
  - result: `rc=1`

## Blocker

`DECKHAND_PAT_client-e` is not yet available.

Observed:

- Existing scopes mint GitHub App installation tokens.
- `client-e (DECKHAND_PAT_client-e): NOT SET — skip` from `scripts/deckhand/protect-and-verify.sh verify-pat`.
- Attempt to add `llm-wiki-client-e` to the GitHub App installation via API failed:
  - command shape: `gh api -X PUT user/installations/${installation_id}/repositories/${repo_id}`
  - result: GitHub `403`, "You do not have permission to modify this app on vamseeachanta."
- `/mnt/ace` is not mounted/present on this host, so `/mnt/ace/client-e/` still needs real raw bucket or mount confirmation before raw source ingestion.

## Required next action

Choose one credential path:

1. Preferred: in GitHub UI, add `vamseeachanta/llm-wiki-client-e` to the existing `deckhand-scopes` GitHub App installation.
2. Fallback: run `scripts/deckhand/add-scope-pat.sh client-e` and paste a fine-grained PAT scoped only to `vamseeachanta/llm-wiki-client-e`.

Then run:

```bash
cd /mnt/local-analysis/deckhand
PYTHONPATH=src python3 -m deckhand.app_token DECKHAND_PAT_client-e >/tmp/client-e.token && test -s /tmp/client-e.token && rm /tmp/client-e.token
scripts/deckhand/protect-and-verify.sh verify-pat | rg 'client-e|WARN|FAIL|NOT SET'
PYTHONPATH=. uv run pytest tests/deckhand/test_scopes_bindings.py tests/deckhand/test_cross_client_isolation.py tests/deckhand/test_channel_prompts.py
scripts/deckhand/sync-group-allowlist.sh
hermes gateway status
```

Finally, send a canary in the client-e Telegram group that confirms the group resolves to `client-e` and can read/write `llm-wiki-client-e`.

## Dirty state to preserve

### workspace-hub

Expected client-e dirty file:

- `M config/client-wikis.yml`

Unrelated pre-existing dirty files observed; do not sweep:

- `?? docs/session-handoffs/2026-06-10-handoff-lane-system-quota-truth.md`
- `?? tests/statusline/test_quota_staleness.bats`

### deckhand

Expected client-e dirty files:

- `M config/deckhand/scopes.yml`
- `M config/deckhand/voice-client-channels.md`
- `M docs/deckhand/ONBOARDING.md`

Unrelated pre-existing dirty state observed; do not sweep:

- issue 206 plan/review files under `docs/plans/` and `scripts/review/results/`
- `docs/deckhand/ISSUE-AND-DECISION-MAP.md`
- `docs/plans/README.md`
- many `__pycache__` modifications/untracked files generated by active parallel work and test runs

### aceengineer-strategy

Expected client-e dirty files:

- `M strategy/deckhand/onboarded-roster.md`
- `M strategy/deckhand/release/build/build_pamphlets.py`
- `?? strategy/deckhand/outreach/2026-06-10-client-e-howard-day-onboarding.md`
- `?? strategy/deckhand/release/assets/qr-client-e.svg`
- `?? strategy/deckhand/release/deckhand-client-e-pamphlet.html`
- `?? strategy/deckhand/release/pdf/deckhand-client-e-pamphlet.pdf`

### llm-wiki-client-e

Clean at commit `6432492`.

## External action status

- Telegram group was created intentionally.
- GitHub private repo was created intentionally.
- Hermes gateway was restarted intentionally after allowlist and prompt updates.
- No client outreach message was sent.
- No client-e canary was sent because credential gate is still closed.
