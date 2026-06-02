# Deckhand — deployment & operator-setup guide (from scratch)

> Stand up Deckhand **for a new client/scope or on a new machine** so we do not reinvent the
> wiring next time. Host of record: ace-linux-2. Epic: [#2931](https://github.com/vamseeachanta/workspace-hub/issues/2931).
> This is the **deployment/operator** companion to the **member-onboarding** doc
> [`ONBOARDING.md`](ONBOARDING.md) — for adding *people* to an already-live scope, go there.
> Glossary (scope / channel / operator / destructive / sensitivity): root [`CONTEXT.md`](../../CONTEXT.md).
>
> Governance this guide implements:
> [scope↔routing orthogonality](../governance/2026-06-01-deckhand-scope-routing-orthogonality-decision.md),
> [enforcement-below-model](../governance/2026-06-01-deckhand-scope-enforcement-below-model-decision.md),
> [channel GTM strategy](../governance/2026-06-02-deckhand-channel-gtm-strategy-decision.md).

---

## 1. What this guide is / prerequisites

A **scope** = a named set of repositories + the permission/identity/data policy over them
(`acma`, `doris`, `ecosystem`). Onboarding a new client = **add one section to
`config/deckhand/scopes.yml` + mint one PAT** — no code change (this is by design).

**Enforcement is below the model.** The chat agent never gets a license to do anything; four
layers under it decide and execute: (1) `pre_tool_call` hook (allow/deny + audit + rate-limit),
(2) PATH-level git/gh shims that inject the per-scope PAT, (3) the per-scope **fine-grained
GitHub PAT** — the real server-side boundary (out-of-scope repo → 404), (4) GitHub branch
rulesets + a destructive-event alarm workflow on each repo. The local hook has known bypass
paths; **the scoped PAT is the load-bearing boundary** (`config/deckhand/policy.yml` §enforcement).

**Prerequisites before you start:**

- **Hermes gateway installed** as a systemd *user* service on the host and runnable as `hermes`
  (`hermes gateway restart`, `hermes send`, `hermes whatsapp`). Tree default: `~/.hermes/hermes-agent`
  (override `HERMES_AGENT_TREE`).
- **`python3` with `pyyaml`** on PATH (the shims, resolver, and `protect-and-verify.sh` need it).
- **`gh` authenticated** as an admin who can create rulesets / install workflows on the scope repos.
- **node/npm** only if you will connect the **WhatsApp** Baileys bridge.
- **A clone of `workspace-hub`** on the host — all configs/scripts/shims live in-repo and are
  referenced by relative path; the installer symlinks the shims into the runtime tree.
- **Secrets live in `~/.hermes/.env`** (runtime path, never committed). PATs and platform tokens
  go there by **env-var name** only; `config/*.yml` reference names, never values.
- **GitHub org access to mint fine-grained PATs** scoped to exactly the new scope's repos.

Runtime state lives under `~/.hermes/`:
`~/.hermes/.env` (secrets) · `~/.hermes/deckhand/shims/` (installed git/gh/hub shims) ·
`~/.hermes/deckhand/active-scope/<platform>/<chat>/<operator>.json` (per-session `/scope`) ·
`~/.hermes/deckhand/ratelimit/` (rate-limit counters) · audit raw store at
the `${DECKHAND_AUDIT_DIR}` raw store (durable-private; default in `policy.yml`, shown in §4a).

---

## 2. Define a new scope

Add one self-contained section under `scopes:` in `config/deckhand/scopes.yml`. Use the existing
`acma` / `doris` sections as the template. Fail-closed everywhere: unknown scope / repo not listed
/ unparseable config ⇒ DENY (`policy.yml` `fail_closed: true`).

```yaml
  # ====================== CLIENT: <newclient> ======================
  <newclient>:
    sensitivity: private              # private routes only to cleared delivery groups
    permission: write                 # read + write; destructive is denied globally (policy.yml)
    pat_env: DECKHAND_PAT_<NEWCLIENT> # NAME of the env var holding the PAT — no secret here
    repositories:
      - vamseeachanta/llm-wiki-<newclient>
      # - vamseeachanta/<newclient>   # add a reference repo if needed (see read-only flag below)
    # repository_flags:               # optional: mark a repo read-only (writes denied by engine)
    #   vamseeachanta/<newclient>: { reference: true, read_only: true }
    operators: []                     # route-A explicit operators (stable platform IDs); see §4
    data_root: "/mnt/ace/<newclient>/"   # off-repo source-of-truth, or null    # abs-path-allowed
    channel_repo_bindings: []         # filled in §4 once a channel exists
```

Notes that match the live behaviour:

- `operators` are **stable platform IDs** (Telegram numeric id, WhatsApp E.164, Teams AAD oid) —
  **never** display names (`policy.yml` `identity.require_stable_platform_id`).
- A reference repo flagged `read_only: true` is reachable for reads but writes are denied by the
  engine even though it's in the allowlist (see `doris` → `vamseeachanta/doris`).
- External testers may only be placed in scopes listed in `poc_external_scope_allowlist`
  (`[acma, doris]`); they are **never** added to `ecosystem` (`external_disabled: true`).
- `ecosystem` uses a glob (`owner:vamseeachanta/*`) resolved at load — concrete repos only get a
  per-scope PAT; the glob scope is internal-operators-only.

**Mint the fine-grained PAT (the real boundary):**

1. GitHub → Settings → Developer settings → **Fine-grained personal access tokens** → Generate.
2. **Resource owner** = `vamseeachanta`; **Repository access = Only select repositories** →
   pick **exactly** the repos in this scope's `repositories:` (no more).
3. Permissions: Contents `Read and write`, Pull requests `Read and write`, Metadata `Read`
   (add others only if a workflow needs them). Keep it minimal.
4. Put the value in `~/.hermes/.env` under the **exact `pat_env` name** from the scope:

   ```bash
   # ~/.hermes/.env   (runtime only — never committed)
   DECKHAND_PAT_<NEWCLIENT>=github_pat_xxxxxxxx
   ```

5. The PAT IS the server-side boundary: a request for any repo **outside** this token's selected
   set returns **404** even if every other layer were bypassed. Prove it in §5 (`verify-pat`).

---

## 3. Connect a platform

Keep the gateway **CLOSED** on every platform: add specific IDs to `*_ALLOWED_USERS`, never set any
`*_ALLOW_ALL_USERS`. Status today (per the [dashboard](../reports/deckhand-dashboard.html) and the
[GTM strategy note](../governance/2026-06-02-deckhand-channel-gtm-strategy-decision.md)):
**Telegram = live and the GTM-lead channel; WhatsApp = live but on the owner's personal number,
demand-driven (not pushed for GTM); Teams = planned**. For per-member detail on any platform, use
[`ONBOARDING.md`](ONBOARDING.md) — this section is connect-only.

### Telegram — LIVE (lead channel)

1. BotFather → create the bot → copy the token → `~/.hermes/.env`:
   `TELEGRAM_BOT_TOKEN=<token>` (referenced by name in `config/deckhand/platforms.yml`).
2. BotFather `/setprivacy` → **Disable** (group privacy OFF) so member numeric IDs are capturable
   from the gateway log. `platforms.yml` keeps `group_privacy_mode: true` for menu behaviour.
3. Add the bot to each client's Telegram group.
4. Allowlist specific operators (gateway stays closed):
   `TELEGRAM_ALLOWED_USERS=<id1>,<id2>` (managed via `add-member.sh`, §7b).
5. `hermes gateway restart`.

### WhatsApp — LIVE (demand-driven, currently owner's personal number)

> Baileys is the **unofficial** protocol; running it on a personal number carries ban risk
> ([#2940](https://github.com/vamseeachanta/workspace-hub/issues/2940)). Per the GTM note, do **not**
> pre-acquire a number for the POC; when a client needs WhatsApp, prefer the official Business Cloud
> API funded by that engagement.

1. `~/.hermes/.env`: `WHATSAPP_ENABLED=true`, `WHATSAPP_MODE=bot` (self-chat mode can't do groups),
   `WHATSAPP_ALLOWED_USERS=<E.164 digits>`.
2. Pair the device: `hermes whatsapp` → scan the QR.
3. Verify live: `curl -s http://127.0.0.1:3000/health` → `{"status":"connected"}`.
4. Capture each group's `@g.us` JID from a **non-bot** member's post (the bridge does not log the
   bot's own `fromMe` messages), then bind it in `scopes.yml` (§4). Full capture procedure in
   [`ONBOARDING.md`](ONBOARDING.md#whatsapp).

### Microsoft Teams — PLANNED ([#2941](https://github.com/vamseeachanta/workspace-hub/issues/2941), plan-review)

Not connected. Requires Azure app registration + a public HTTPS webhook to `/api/messages`
(no ingress on the box yet) and a tenant decision (D1 internal-only vs guests, D2 cloudflared
tunnel). Env names already reserved in `platforms.yml`:
`TEAMS_CLIENT_ID` / `TEAMS_CLIENT_SECRET` / `TEAMS_TENANT_ID`; allowlist `TEAMS_ALLOWED_USERS`;
member ID = AAD object id.

---

## 4. Install enforcement

### 4a. Plugin + shims + core patches (one installer)

The Hermes plugin lives at `scripts/deckhand/hermes-plugin/deckhand-scope/` (registers `/scope`,
`/whoami`, and the `pre_tool_call` hook). The shims are `scripts/deckhand/shims/{git,gh,hub}`. Two
Hermes **core patches** are required (re-apply after any Hermes update):

- `patches/hermes/01-path-shim-prepend.patch` → `tools/environments/local.py`: prepends
  `~/.hermes/deckhand/shims` to the tool PATH so git/gh resolve to the shims (not the bare binary).
- `patches/hermes/02-scope-command-session-env.patch` → `gateway/run.py`: sets session env for
  plugin slash-commands so `/scope` and `/whoami` can see the operator identity (Hermes otherwise
  dispatches plugin commands before session identity is set).

Install (dry-run first — it checks patch drift and prints planned actions):

```bash
scripts/deckhand/install-hermes-b2.sh            # dry-run: drift-check + planned shim symlinks
scripts/deckhand/install-hermes-b2.sh --apply    # symlink shims into ~/.hermes/deckhand/shims, apply patches
hermes gateway restart                           # reload tools/environments/local.py
```

**The plugin must be symlinked into Hermes' user-plugin dir** — Hermes discovers user plugins at
`~/.hermes/plugins/<name>/`. The installer does **not** create this link yet (it only handles shims +
patches), so do it explicitly:

```bash
ln -sfn "$(pwd)/scripts/deckhand/hermes-plugin/deckhand-scope" ~/.hermes/plugins/deckhand-scope
hermes gateway restart
```

> ⚠ Known gap: `install-hermes-b2.sh` symlinks shims but not the plugin (the link above is manual on a
> fresh machine). Folding it into the installer is a follow-up. Verify discovery: after restart, the
> `/scope` command must appear (`HERMES_PLUGINS_DEBUG=1` surfaces verbose plugin-discovery logs) before
> relying on enforcement.

State locations (created on first use): audit raw store at
`${DECKHAND_AUDIT_DIR}/decisions.ndjson` (default path defined in `policy.yml`, shown verbatim in
§5d); redacted public summary `docs/reports/deckhand-audit-summary.html`; rate-limit counters
`~/.hermes/deckhand/ratelimit/`.

### 4b. Repo guards (rulesets + destructive-event alarm)

`scripts/deckhand/protect-and-verify.sh` derives the repo list **from `scopes.yml`** (no hardcoding):

```bash
scripts/deckhand/protect-and-verify.sh protect             # branch ruleset: block force-push + branch/tag deletion
scripts/deckhand/protect-and-verify.sh verify              # list rulesets per scope repo
scripts/deckhand/protect-and-verify.sh deploy-detective --apply   # install the destructive-event alarm workflow
scripts/deckhand/protect-and-verify.sh verify-detective    # confirm the alarm workflow is present
```

> Rulesets on **private** repos need GitHub Pro/Team; the script prints `UNAVAILABLE` and skips
> gracefully there. The scoped-PAT boundary + the hook still apply regardless.

### 4c. Bind a channel/group to the scope

Edit the scope's `channel_repo_bindings:` in `scopes.yml`. Two routes (orthogonal to which
*platform* the reply goes to):

```yaml
    channel_repo_bindings:
      # Route A — explicit operator's DM bound to a repo (operator must be in `operators:`)
      - platform: telegram
        channel_id: "<operator_numeric_id>"
        repo: vamseeachanta/llm-wiki-<newclient>
      # Route B — a GROUP bound to the scope; ANY group member is authorized for it
      - platform: telegram
        channel_id: "<group_chat_id>"          # e.g. "-5109954935"
        repo: vamseeachanta/llm-wiki-<newclient>
        authorize_members: true
```

- **Route A** resolves the scope only for a listed operator on that bound channel.
- **Route B** (`authorize_members: true`) authorizes any member of the bound group for that scope
  (the resolver appends the member as an effective operator at decision time). The owner still
  confirms each member by name + ID before allowlisting (golden rule, `ONBOARDING.md`).
- For WhatsApp, set `channel_id: "<jid>@g.us"` (captured per §3) and `authorize_members: true`.
- Run `hermes gateway restart` after any `scopes.yml` binding change.

---

## 5. Verify (acceptance checklist)

Run these on the host after install. They prove enforcement is real, not prompt-deep.

**(a) Shims resolve + ambient token absent (read-only B2 check):**
```bash
scripts/deckhand/verify-hermes-b2.sh
# expects: shim dir exists; sample PATH resolves git/gh/hub to ~/.hermes/deckhand/shims;
#          resolver returns the scope's pat_env name; GH_TOKEN absent from ambient env.
```

**(b) Scope isolation — identity → expected PAT env name.** Feed a session identity and confirm the
resolver maps it to the right `DECKHAND_PAT_*` (and to *nothing* for an unauthorized identity):
```bash
HERMES_SESSION_USER_ID=<operator_id> \
HERMES_SESSION_PLATFORM=telegram \
HERMES_SESSION_CHAT_ID=<bound_chat_id> \
PYTHONPATH=src python3 -m deckhand.shim_resolve
# expect: DECKHAND_PAT_<SCOPE>     (unauthorized identity → empty output, exit 3)
```

**(c) PAT boundary — own repos reachable, out-of-scope returns 404:**
```bash
scripts/deckhand/protect-and-verify.sh verify-pat
# per scope: "reaches <own repo> OK" for each in-scope repo;
#            "WARN token over-broad — reaches out-of-scope <repo>" if the PAT is too wide (must NOT appear).
```
Manual spot-check of the 404 boundary under a scope PAT:
```bash
set -a; . ~/.hermes/.env; set +a
GH_TOKEN="$DECKHAND_PAT_<SCOPE>" gh api repos/vamseeachanta/llm-wiki-<newclient> -q .full_name   # OK
GH_TOKEN="$DECKHAND_PAT_<SCOPE>" gh api repos/vamseeachanta/<some-other-repo>                     # 404
```

**(d) Reads allowed, force-push DENIED, audit row written.** From a scoped Hermes chat session
(or the scoped terminal): a read (`git status`, `gh repo view <in-scope>`) is allowed; a
**force-push is DENIED** with a block message. Confirm the audit trail recorded the DENY:
```bash
tail -n 5 "${DECKHAND_AUDIT_DIR:-/mnt/dde/deckhand/audit}/decisions.ndjson"   # abs-path-allowed
# expect a DENY row for the force-push (decision, reason, operator, scope, repos, outcome).
```

**(e) Rate-limit caps a flood.** Issue more writes than `rate_limits.per_operator_writes_per_hour`
(default 30) / `per_scope_writes_per_hour` (default 60) within the hour window; further writes are
DENIED with a rate-limit reason and audited; reads remain unaffected.

---

## 6. Per-client repeatable checklist

Copy-paste for the next client/scope:

```text
[ ] Scope block added to config/deckhand/scopes.yml (sensitivity, permission, pat_env, repositories, data_root)
[ ] Fine-grained PAT minted, scoped to EXACTLY this scope's repos, value in ~/.hermes/.env as <pat_env>
[ ] protect-and-verify.sh verify-pat → reaches own repos, NO out-of-scope WARN
[ ] Platform connected + CLOSED allowlist (TELEGRAM_/WHATSAPP_/TEAMS_ALLOWED_USERS; no *_ALLOW_ALL_USERS)
[ ] channel_repo_bindings added (route A explicit operators and/or route B authorize_members group)
[ ] install-hermes-b2.sh --apply  (shims + 2 core patches)  +  hermes gateway restart
[ ] protect-and-verify.sh protect  +  deploy-detective --apply  (repo guards)
[ ] Members onboarded  → docs/deckhand/ONBOARDING.md (owner confirms each by name + ID)
[ ] Verification passed → §5 (a)-(e): shims resolve, identity→PAT, 404 boundary, force-push DENY+audit, rate-limit
```

---

## 7. Example prompts & commands

### 7a. Example operator chat prompts (what an operator types to Deckhand)

| Operator types in the bound channel | What Deckhand does |
|---|---|
| `/whoami` | Replies with the operator's numeric platform ID + platform + chat — used to get the ID for allowlisting. |
| `/scope` | Shows the active scope and the scopes this operator is authorized for. |
| `/scope acma` | Sets the active scope to `acma` (only if the operator is in `acma.operators`); persists per session. |
| "what's the latest on the README in `llm-wiki-acma`?" | **Read** — allowed; runs under the `acma` PAT. |
| "create a branch `feature/x` in `llm-wiki-acma` and open a PR" | **Write** — allowed (PR-only); branch + PR created via the `acma` PAT; ALLOW row audited. |
| "force-push to clean up history" | **DENIED** — force-push is destructive (`policy.yml`); block message + DENY audit row. |
| "push to `digitalmodel`" (from an `acma` session) | **DENIED / 404** — repo not in the `acma` PAT's selected set; the token cannot even see it. |
| Same request in an uncleared/shared channel | Generic "continue in DM" reply (no repo names / PR URLs) per `reply_clearance`. |

### 7b. Example setup/CLI commands (what the admin runs)

Member management (real flags from `scripts/deckhand/add-member.sh`):
```bash
# Dry-run (default): show what would change
scripts/deckhand/add-member.sh <numeric_id> --scope acma

# Apply: allowlist + (route-A) add to scope operators + auto-named welcome to the group
scripts/deckhand/add-member.sh <numeric_id> --scope doris --name "Full Name" --apply

# Route-B group member (group is authorize_members): allowlist only, no scope operators flag
scripts/deckhand/add-member.sh <numeric_id> --apply

# Explicit route-A operator entry (requires --scope), suppress the welcome
scripts/deckhand/add-member.sh <numeric_id> --scope acma --operator --no-welcome --apply

# WhatsApp member (E.164 digits, optional leading +)
scripts/deckhand/add-member.sh <e164_digits> --platform whatsapp --scope acma --apply

# List current allowlist count + scope operators
scripts/deckhand/add-member.sh --list
scripts/deckhand/add-member.sh --list --platform whatsapp
```

Gateway + install + guards:
```bash
hermes gateway restart                                       # reload after any env/config change
scripts/deckhand/install-hermes-b2.sh --apply                # shims + 2 core patches
scripts/deckhand/protect-and-verify.sh protect               # branch rulesets
scripts/deckhand/protect-and-verify.sh deploy-detective --apply  # destructive-event alarm workflow
```

Verification:
```bash
scripts/deckhand/verify-hermes-b2.sh                         # shims resolve; ambient GH_TOKEN absent
scripts/deckhand/protect-and-verify.sh verify-pat            # PAT reaches only own repos
HERMES_SESSION_USER_ID=<id> HERMES_SESSION_PLATFORM=telegram HERMES_SESSION_CHAT_ID=<chat> \
  PYTHONPATH=src python3 -m deckhand.shim_resolve            # identity → expected DECKHAND_PAT_*
```

---

## See also

- [`ONBOARDING.md`](ONBOARDING.md) — per-member onboarding (capture IDs, confirm, allowlist, welcome).
- [`CONTEXT.md`](../../CONTEXT.md) — Deckhand glossary (scope / channel / operator / destructive / sensitivity).
- [`config/deckhand/scopes.yml`](../../config/deckhand/scopes.yml) · [`policy.yml`](../../config/deckhand/policy.yml) · [`platforms.yml`](../../config/deckhand/platforms.yml).
- Governance: [scope↔routing orthogonality](../governance/2026-06-01-deckhand-scope-routing-orthogonality-decision.md) · [enforcement-below-model](../governance/2026-06-01-deckhand-scope-enforcement-below-model-decision.md) · [channel GTM strategy](../governance/2026-06-02-deckhand-channel-gtm-strategy-decision.md).
- Issues: [#2931](https://github.com/vamseeachanta/workspace-hub/issues/2931) (epic) · [#2937](https://github.com/vamseeachanta/workspace-hub/issues/2937) (onboarding) · [#2939](https://github.com/vamseeachanta/workspace-hub/issues/2939) (WhatsApp) · [#2940](https://github.com/vamseeachanta/workspace-hub/issues/2940) (WhatsApp dedicated identity) · [#2941](https://github.com/vamseeachanta/workspace-hub/issues/2941) (Teams).
