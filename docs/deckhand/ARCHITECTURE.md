# Deckhand Architecture

Deckhand is an authenticated chatbot control plane for Hermes: an operator can drive `git`, `gh`, and `hub` actions on named repository scopes (`acma`, `doris`, `ecosystem`) from chat platforms while enforcement stays below the model. The design exists because prompt text is not an authorization boundary; the live path combines a closed gateway, scope authorization, per-scope fine-grained GitHub PAT shims, destructive-action denial, audit, and rate limiting so a model or tool path cannot silently exceed the selected scope. Glossary terms live in [`CONTEXT.md`](../../CONTEXT.md), deployment steps in [`DEPLOYMENT.md`](DEPLOYMENT.md), and member onboarding in [`ONBOARDING.md`](ONBOARDING.md).

## Enforcement Layers

| Layer | What it guarantees | Where it lives | Fail-closed behavior |
|---|---|---|---|
| 1. Closed gateway allowlist | Only explicitly allowlisted platform identities can reach Deckhand at all. Platform allowlists are `TELEGRAM_ALLOWED_USERS`, `WHATSAPP_ALLOWED_USERS`, and planned `TEAMS_ALLOWED_USERS`; the gateway stays closed. | `CONTEXT.md:54`, `CONTEXT.md:58`; `docs/deckhand/ONBOARDING.md:7`; `docs/deckhand/ONBOARDING.md:9`; `scripts/deckhand/add-member.sh:85`; `scripts/deckhand/add-member.sh:88`; `docs/deckhand/DEPLOYMENT.md:112` | Non-allowlisted senders are rejected before any Deckhand scope or tool decision. The docs explicitly reject `*_ALLOW_ALL_USERS` as the operating model. |
| 2. Scope authorization | A request resolves to one active scope. Route A requires the operator ID in `operators`; Route B authorizes any member of a bound group with `authorize_members: true`. | `scripts/deckhand/hermes-plugin/deckhand-scope/__init__.py:47`; `scripts/deckhand/hermes-plugin/deckhand-scope/__init__.py:62`; `scripts/deckhand/hermes-plugin/deckhand-scope/__init__.py:318`; `scripts/deckhand/hermes-plugin/deckhand-scope/__init__.py:344`; `scripts/deckhand/hermes-plugin/deckhand-scope/__init__.py:364`; `scripts/deckhand/hermes-plugin/deckhand-scope/__init__.py:380`; `src/deckhand/shim_resolve.py:46`; `src/deckhand/shim_resolve.py:113`; `config/deckhand/scopes.yml:24`; `config/deckhand/scopes.yml:31`; `config/deckhand/scopes.yml:33` | Unknown scope, missing identity, stale active-scope record, or unauthorized operator returns no scope/PAT and write attempts are denied. |
| 3. Scoped PAT shims | The real server-side boundary: each scope runs `git`, `gh`, and `hub` under its own fine-grained GitHub PAT env var name. An out-of-scope repo is invisible to that PAT and returns GitHub 404. | `config/deckhand/scopes.yml:20`; `config/deckhand/scopes.yml:47`; `config/deckhand/scopes.yml:72`; `scripts/deckhand/shims/git:31`; `scripts/deckhand/shims/git:35`; `scripts/deckhand/shims/git:43`; `scripts/deckhand/shims/git:72`; `scripts/deckhand/shims/git:78`; `scripts/deckhand/shims/git:105`; `scripts/deckhand/shims/gh:84`; `scripts/deckhand/shims/gh:85`; `scripts/deckhand/shims/hub:84`; `scripts/deckhand/protect-and-verify.sh:12`; `scripts/deckhand/protect-and-verify.sh:142` | No active scope exits `3`; missing PAT value exits `4`; ambient `GH_TOKEN`/`GITHUB_TOKEN` is unset before shim execution. |
| 4. No-destructive guard | Irreversible operations are denied separately from normal writes: repo/branch/tag/release deletion, force push/history rewrite, `reset --hard`, and `git clean`. | `config/deckhand/policy.yml:15`; `config/deckhand/policy.yml:17`; `src/deckhand/hook.py:42`; `src/deckhand/hook.py:95`; `src/deckhand/hook.py:107`; `src/deckhand/hook.py:228`; `src/deckhand/hook.py:256`; `src/deckhand/hook.py:291`; `src/deckhand/engine.py:66`; `src/deckhand/engine.py:68`; `scripts/deckhand/protect-and-verify.sh:8`; `scripts/deckhand/templates/deckhand-destructive-alarm.yml:16` | Suspicious or unparseable git-like commands are denied before engine policy. Destructive action classes are denied by the engine even for authorized scopes. |
| 5. Audit + rate-limit | Every allow/deny is recorded; allowed writes are rate-limited by operator, scope, and duplicate fingerprint. Runtime records PENDING before execution and FINAL after execution. | `config/deckhand/policy.yml:52`; `config/deckhand/policy.yml:66`; `config/deckhand/policy.yml:89`; `scripts/deckhand/hermes-plugin/deckhand-scope/__init__.py:162`; `scripts/deckhand/hermes-plugin/deckhand-scope/__init__.py:166`; `scripts/deckhand/hermes-plugin/deckhand-scope/__init__.py:175`; `scripts/deckhand/hermes-plugin/deckhand-scope/__init__.py:449`; `src/deckhand/audit.py:15`; `src/deckhand/ratelimit.py:15`; `src/deckhand/ratelimit.py:47`; `src/deckhand/ratelimit.py:59`; `src/deckhand/runtime.py:58`; `src/deckhand/runtime.py:82` | Rate-limit store/config errors deny writes. Audit append is best-effort at the plugin boundary but runtime persists DENY/PENDING/FINAL records around execution. |

## Plugin

The live Hermes plugin is `scripts/deckhand/hermes-plugin/deckhand-scope/__init__.py`; `plugin.yaml` names it `deckhand-scope` and points Hermes at `__init__.py` (`scripts/deckhand/hermes-plugin/deckhand-scope/plugin.yaml:1`, `scripts/deckhand/hermes-plugin/deckhand-scope/plugin.yaml:3`). Registration adds `/scope`, `/whoami`, and the `pre_tool_call` hook (`scripts/deckhand/hermes-plugin/deckhand-scope/__init__.py:32`, `scripts/deckhand/hermes-plugin/deckhand-scope/__init__.py:39`, `scripts/deckhand/hermes-plugin/deckhand-scope/__init__.py:45`).

`/scope [name]` identifies the operator from Hermes session env, lists authorized scopes when no arg is given, rejects unknown/unauthorized scopes, and writes the active scope state under the operator/chat identity (`scripts/deckhand/hermes-plugin/deckhand-scope/__init__.py:47`, `scripts/deckhand/hermes-plugin/deckhand-scope/__init__.py:53`, `scripts/deckhand/hermes-plugin/deckhand-scope/__init__.py:64`, `scripts/deckhand/hermes-plugin/deckhand-scope/__init__.py:286`, `scripts/deckhand/hermes-plugin/deckhand-scope/__init__.py:297`). `/whoami` reports the stable platform ID for onboarding and logs the lookup (`scripts/deckhand/hermes-plugin/deckhand-scope/__init__.py:67`, `scripts/deckhand/hermes-plugin/deckhand-scope/__init__.py:74`, `scripts/deckhand/hermes-plugin/deckhand-scope/__init__.py:77`).

The `pre_tool_call` decision flow is:

1. Ignore non-gated tools; gate only `terminal` and `execute_code` (`scripts/deckhand/hermes-plugin/deckhand-scope/__init__.py:28`, `scripts/deckhand/hermes-plugin/deckhand-scope/__init__.py:97`).
2. For terminal calls, classify command actions with `hook.classify_command`; no git/gh/hub action is audited as allow and passes through (`scripts/deckhand/hermes-plugin/deckhand-scope/__init__.py:113`, `scripts/deckhand/hermes-plugin/deckhand-scope/__init__.py:115`, `scripts/deckhand/hermes-plugin/deckhand-scope/__init__.py:116`).
3. Read session identity, config, active scope, and group authorization (`scripts/deckhand/hermes-plugin/deckhand-scope/__init__.py:127`, `scripts/deckhand/hermes-plugin/deckhand-scope/__init__.py:128`, `scripts/deckhand/hermes-plugin/deckhand-scope/__init__.py:130`, `scripts/deckhand/hermes-plugin/deckhand-scope/__init__.py:131`).
4. Resolve the target repo from the current git remote and pass command/context to the pure hook/engine (`scripts/deckhand/hermes-plugin/deckhand-scope/__init__.py:137`, `scripts/deckhand/hermes-plugin/deckhand-scope/__init__.py:149`, `scripts/deckhand/hermes-plugin/deckhand-scope/__init__.py:419`).
5. Deny writes with missing/invalid scope or unresolved repo (`scripts/deckhand/hermes-plugin/deckhand-scope/__init__.py:154`, `scripts/deckhand/hermes-plugin/deckhand-scope/__init__.py:157`).
6. For allowed writes, run the file-backed rate limiter; deny on cap, duplicate, or store error (`scripts/deckhand/hermes-plugin/deckhand-scope/__init__.py:162`, `scripts/deckhand/hermes-plugin/deckhand-scope/__init__.py:166`, `scripts/deckhand/hermes-plugin/deckhand-scope/__init__.py:175`, `scripts/deckhand/hermes-plugin/deckhand-scope/__init__.py:178`).
7. Append an audit decision and block unless allowed or `DECKHAND_ENFORCE=report` (`scripts/deckhand/hermes-plugin/deckhand-scope/__init__.py:181`, `scripts/deckhand/hermes-plugin/deckhand-scope/__init__.py:182`, `scripts/deckhand/hermes-plugin/deckhand-scope/__init__.py:195`, `scripts/deckhand/hermes-plugin/deckhand-scope/__init__.py:520`).

For `execute_code`, the plugin scans Python source for git/gh re-entry patterns and blocks code-execution paths that should go through the command gate (`scripts/deckhand/hermes-plugin/deckhand-scope/__init__.py:199`, `scripts/deckhand/hermes-plugin/deckhand-scope/__init__.py:212`, `src/deckhand/hook.py:131`).

## Shims And Hermes Patches

The shims are PATH-level wrappers for `git`, `gh`, and `hub`. Each finds the real binary outside the shim directory, resolves the active scope's `pat_env` through `deckhand.shim_resolve`, reads the PAT value from `~/.hermes/deckhand/secrets.env` first and `~/.hermes/.env` second, then executes under the scoped credential (`scripts/deckhand/shims/git:9`, `scripts/deckhand/shims/git:31`, `scripts/deckhand/shims/git:35`, `scripts/deckhand/shims/git:43`, `scripts/deckhand/shims/git:66`, `scripts/deckhand/shims/git:72`, `scripts/deckhand/shims/gh:84`, `scripts/deckhand/shims/hub:84`). The `git` shim uses `GIT_ASKPASS`, clears ambient GitHub tokens, disables terminal prompting, and enables HTTP-path credential matching (`scripts/deckhand/shims/git:84`, `scripts/deckhand/shims/git:105`, `scripts/deckhand/shims/git:106`, `scripts/deckhand/shims/git:108`, `scripts/deckhand/shims/git:109`). The `gh` and `hub` shims set `GH_TOKEN` and `GITHUB_TOKEN` to the scoped PAT only for the child process (`scripts/deckhand/shims/gh:84`, `scripts/deckhand/shims/gh:85`, `scripts/deckhand/shims/hub:84`, `scripts/deckhand/shims/hub:85`).

Two local Hermes core patches make the shim and slash-command path work:

| Patch | What it changes | Why |
|---|---|---|
| `patches/hermes/01-path-shim-prepend.patch` | Prepends `~/.hermes/deckhand/shims` to Hermes tool PATH when the shim dir exists (`patches/hermes/01-path-shim-prepend.patch:7`, `patches/hermes/01-path-shim-prepend.patch:11`, `patches/hermes/01-path-shim-prepend.patch:15`). | Ensures tool executions resolve `git`, `gh`, and `hub` through Deckhand shims instead of ambient binaries. |
| `patches/hermes/02-scope-command-session-env.patch` | Builds session context before plugin slash-command dispatch, sets session env, and clears it afterward (`patches/hermes/02-scope-command-session-env.patch:11`, `patches/hermes/02-scope-command-session-env.patch:26`, `patches/hermes/02-scope-command-session-env.patch:28`, `patches/hermes/02-scope-command-session-env.patch:43`, `patches/hermes/02-scope-command-session-env.patch:45`). | Lets `/scope` and `/whoami` see `HERMES_SESSION_*` identity because Hermes otherwise dispatches plugin commands before tool session env is set. |

`scripts/deckhand/install-hermes-b2.sh` drift-checks both patches, symlinks shims into the Hermes runtime tree, and applies the patches only with `--apply` (`scripts/deckhand/install-hermes-b2.sh:8`, `scripts/deckhand/install-hermes-b2.sh:12`, `scripts/deckhand/install-hermes-b2.sh:45`, `scripts/deckhand/install-hermes-b2.sh:89`). `scripts/deckhand/verify-hermes-b2.sh` verifies the shim directory, PATH resolution to shims, resolver output, and absence of ambient `GH_TOKEN` (`scripts/deckhand/verify-hermes-b2.sh:25`, `scripts/deckhand/verify-hermes-b2.sh:35`, `scripts/deckhand/verify-hermes-b2.sh:48`, `scripts/deckhand/verify-hermes-b2.sh:53`). `scripts/deckhand/protect-and-verify.sh` adds/verifies repo rulesets, checks PAT scope, and installs a detective alarm workflow without printing secrets (`scripts/deckhand/protect-and-verify.sh:8`, `scripts/deckhand/protect-and-verify.sh:12`, `scripts/deckhand/protect-and-verify.sh:142`, `scripts/deckhand/protect-and-verify.sh:163`).

## Config Model

`config/deckhand/scopes.yml` is the per-scope surface. It defines `repositories`, `operators`, `pat_env`, `channel_repo_bindings`, `authorize_members`, and `origin_bound_default` (`config/deckhand/scopes.yml:14`, `config/deckhand/scopes.yml:20`, `config/deckhand/scopes.yml:21`, `config/deckhand/scopes.yml:24`, `config/deckhand/scopes.yml:26`, `config/deckhand/scopes.yml:33`, `config/deckhand/scopes.yml:81`). `acma` and `doris` are private external POC scopes; `doris` includes a read-only reference repo flag (`config/deckhand/scopes.yml:17`, `config/deckhand/scopes.yml:44`, `config/deckhand/scopes.yml:51`). `ecosystem` is internal, glob-scoped, and external-disabled (`config/deckhand/scopes.yml:69`, `config/deckhand/scopes.yml:73`, `config/deckhand/scopes.yml:75`). The file states fail-closed behavior for unknown scope, repo absence, or unparseable config (`config/deckhand/scopes.yml:8`).

`config/deckhand/policy.yml` is the global enforcement surface. It declares `fail_closed`, destructive denylist, action/diff-risk defaults, reply clearance, stable-ID identity rules, audit sinks, enforcement layers, kill switches, rate limits, and elevation (`config/deckhand/policy.yml:11`, `config/deckhand/policy.yml:17`, `config/deckhand/policy.yml:26`, `config/deckhand/policy.yml:40`, `config/deckhand/policy.yml:47`, `config/deckhand/policy.yml:52`, `config/deckhand/policy.yml:73`, `config/deckhand/policy.yml:80`, `config/deckhand/policy.yml:89`, `config/deckhand/policy.yml:96`). Live block/report mode is controlled by `DECKHAND_ENFORCE` in the plugin (`scripts/deckhand/hermes-plugin/deckhand-scope/__init__.py:520`, `scripts/deckhand/hermes-plugin/deckhand-scope/__init__.py:523`).

`config/deckhand/platforms.yml` references platform credential env var names only: `TELEGRAM_BOT_TOKEN`, `TEAMS_CLIENT_ID`, `TEAMS_CLIENT_SECRET`, `TEAMS_TENANT_ID`; WhatsApp is documented as Baileys/QR-paired and fanout stays off (`config/deckhand/platforms.yml:3`, `config/deckhand/platforms.yml:9`, `config/deckhand/platforms.yml:11`, `config/deckhand/platforms.yml:13`, `config/deckhand/platforms.yml:16`, `config/deckhand/platforms.yml:27`).

## Data Flow

```text
chat message
  -> Hermes gateway closed allowlist
  -> session identity HERMES_SESSION_USER_ID / PLATFORM / CHAT_ID / THREAD_ID
  -> /scope state or channel_repo_bindings resolve active scope
  -> pre_tool_call hook classifies git/gh/hub or execute_code re-entry
  -> engine allow/deny: operator, scope, repo allowlist, destructive denylist, risk gates
  -> if write: rate-limit operator/scope/duplicate fingerprint
  -> PATH shim resolves pat_env and injects scoped PAT
  -> git/gh/hub reaches GitHub under scoped credential
  -> audit record append
```

## Runtime And Host State

Host of record is `ace-linux-2` (`docs/deckhand/DEPLOYMENT.md:4`, `docs/reports/deckhand-dashboard.html:56`). Runtime state is not committed:

```text
~/.hermes/.env
~/.hermes/deckhand/secrets.env            # chmod 600; scoped PAT values
~/.hermes/plugins/deckhand-scope          # symlink to plugin directory
~/.hermes/whatsapp/session                # WhatsApp pairing/session state
~/.hermes/deckhand/active-scope/...       # /scope state
~/.hermes/deckhand/ratelimit/...          # live write counters
${DECKHAND_AUDIT_DIR:-/mnt/dde/deckhand/audit}/decisions.ndjson  # abs-path-allowed
```

The secret split is documented in deployment prerequisites: scoped PATs live in `~/.hermes/deckhand/secrets.env` with mode `600`, while other platform secrets live in `~/.hermes/.env` (`docs/deckhand/DEPLOYMENT.md:39`, `docs/deckhand/DEPLOYMENT.md:43`, `docs/deckhand/DEPLOYMENT.md:191`). The plugin symlink is manual today (`docs/deckhand/DEPLOYMENT.md:177`, `docs/deckhand/DEPLOYMENT.md:182`, `docs/deckhand/DEPLOYMENT.md:186`). The audit default path comes from `policy.yml` (`config/deckhand/policy.yml:66`, `config/deckhand/policy.yml:68`). WhatsApp is QR-paired through Hermes and has a local health check (`docs/deckhand/DEPLOYMENT.md:137`, `docs/deckhand/DEPLOYMENT.md:139`, `docs/deckhand/DEPLOYMENT.md:140`).

## Platform Status

| Platform | Status | Evidence |
|---|---|---|
| Telegram | LIVE | Deployment calls Telegram the live lead channel (`docs/deckhand/DEPLOYMENT.md:112`, `docs/deckhand/DEPLOYMENT.md:115`, `docs/deckhand/DEPLOYMENT.md:119`); onboarding lists connected Telegram groups for `acma` and `doris` (`docs/deckhand/ONBOARDING.md:19`, `docs/deckhand/ONBOARDING.md:23`). |
| WhatsApp | LIVE, bot mode, owner's personal number, demand-driven | Deployment says WhatsApp is live but demand-driven and currently on the owner's personal number (`docs/deckhand/DEPLOYMENT.md:130`, `docs/deckhand/DEPLOYMENT.md:137`); onboarding confirms connected bot mode and the personal-number warning (`docs/deckhand/ONBOARDING.md:63`, `docs/deckhand/ONBOARDING.md:65`, `docs/deckhand/ONBOARDING.md:67`); the GTM note says leave the POC running as-is and decide later (`docs/governance/2026-06-02-deckhand-channel-gtm-strategy-decision.md:23`). |
| Teams | PLANNED | Deployment marks Teams planned under [#2941](https://github.com/vamseeachanta/workspace-hub/issues/2941) and requiring Azure app registration plus public HTTPS webhook (`docs/deckhand/DEPLOYMENT.md:145`, `docs/deckhand/DEPLOYMENT.md:147`); `platforms.yml` keeps Teams disabled with env names reserved (`config/deckhand/platforms.yml:16`, `config/deckhand/platforms.yml:18`). |

## Existing Docs

Do not duplicate these surfaces:

- [`DEPLOYMENT.md`](DEPLOYMENT.md): setup and operator guide.
- [`ONBOARDING.md`](ONBOARDING.md): member onboarding per platform.
- [`CONTEXT.md`](../../CONTEXT.md): glossary.
- [`2026-06-01-deckhand-scope-routing-orthogonality-decision.md`](../governance/2026-06-01-deckhand-scope-routing-orthogonality-decision.md): scope/routing separation.
- [`2026-06-01-deckhand-scope-enforcement-below-model-decision.md`](../governance/2026-06-01-deckhand-scope-enforcement-below-model-decision.md): enforcement-below-model rationale.
- [`2026-06-02-deckhand-channel-gtm-strategy-decision.md`](../governance/2026-06-02-deckhand-channel-gtm-strategy-decision.md): Telegram-led and demand-driven channel strategy.
