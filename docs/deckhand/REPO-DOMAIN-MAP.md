# Deckhand — Repo & Domain Map

> **Purpose:** the authoritative "where does each piece of Deckhand work live, and why" map for the repo ecosystem. This is the backbone for resuming Deckhand work in a fresh session.
> **Epic:** [#2931](https://github.com/vamseeachanta/workspace-hub/issues/2931) · doc-map issue [#2944](https://github.com/vamseeachanta/workspace-hub/issues/2944) · **Host:** ace-linux-2.
> **Routing contract decided by owner 2026-06-02.** Sibling docs: `ARCHITECTURE.md`, `FILE-INVENTORY.md`, `ISSUE-AND-DECISION-MAP.md` (this file does not duplicate them).

---

## 1. Governing routing rules (the contract)

These five rules govern where every Deckhand artifact lives. They are owner-decided and authoritative; resolve any placement question against them.

1. **`workspace-hub` = the Deckhand ENGINE.** Generic, multi-tenant code / config / enforcement / tests + generic operator docs. **Never client-specific.** Engine domains: `ai-orchestration`, `platform-infra`, `notification`, `security`.

2. **`aceengineer-strategy` (PRIVATE) = ALL client-related info + work.** GTM/strategy material, client engagements, onboarded client/member rosters, business/positioning decisions. Owner ruling: *"all client related info and work should go into aceengineer-strategy repo."* Verified present: `vamseeachanta/aceengineer-strategy` (visibility `PRIVATE`).

3. **`llm-wiki-<client>` (e.g. `llm-wiki-acma`, `llm-wiki-doris`) = client domain knowledge/data**, per [`.claude/rules/wiki-sibling-routing.md`](../../.claude/rules/wiki-sibling-routing.md). Generic *sanitized* knowledge promotes up to the generic `llm-wiki` via the abstraction gate. One sibling per client (suffix form); projects nest as `projects/<slug>/` folders.

4. **Hermes = the upstream chat gateway Deckhand plugs into** (systemd user service). Deckhand's required *core* patches are tracked in [`patches/hermes/`](../../patches/hermes/) and applied to the local Hermes install; **Hermes itself is a separate project**, not vendored here.

5. **Host/runtime state on ace-linux-2 = NOT in any repo.** Secrets and machine-local state live only under `~/.hermes/` (and the off-repo audit store). See §5.

---

## 2. The repo/runtime split at a glance

| Surface | What it holds | In git? |
|---|---|---|
| **workspace-hub** | Engine code, config templates, enforcement, tests, generic operator docs, Hermes patch set | Yes (this repo) |
| **aceengineer-strategy** (private) | Client engagements, GTM decks, strategy/positioning decisions, client + member rosters | Yes (separate private repo) |
| **llm-wiki-`<client>`** | Per-client domain knowledge/data; project subtrees | Yes (per-client private repos) |
| **Hermes** (upstream) | The chat gateway runtime; Deckhand registers as a plugin + applies patch set | Separate project; install lives at `~/.hermes/hermes-agent` |
| **ace-linux-2 host state** | Secrets, PATs, session files, plugin symlink, audit store | **No** — runtime only (§5) |

---

## 3. Master artifact → location map

Legend: **Current** = where it physically is today. **Correct** = where the contract says it belongs. Rows where Current ≠ Correct are listed in §4.

| Artifact / area | Current location | Correct repo | Domain | Rationale |
|---|---|---|---|---|
| Scope decision engine (`engine.py`, `pipeline.py`, `runtime.py`, `hook.py`, `audit.py`, `ratelimit.py`, `shim_resolve.py`) | `src/deckhand/` | workspace-hub | `ai-orchestration` / `security` | Generic, multi-tenant enforcement core; no client identifiers. |
| Scope/policy config | `config/deckhand/scopes.yml`, `config/deckhand/policy.yml` | workspace-hub | `security` | Multi-tenant config; `acma`/`doris` are **example** scope sections — onboarding a client = add a section, no code change. Channel IDs/operators here are platform IDs, not client PII (legal-safe by design). |
| Hermes core patches | `patches/hermes/01-path-shim-prepend.patch`, `02-scope-command-session-env.patch` | workspace-hub | `platform-infra` | Deckhand's required patches to upstream Hermes; tracked here, applied to local install. Tagged `repo:hermes` on issues. |
| Hermes-scope plugin | `scripts/deckhand/hermes-plugin/deckhand-scope/` | workspace-hub | `ai-orchestration` | Generic plugin registered into Hermes; symlinked into `~/.hermes/plugins/`. |
| PATH shims (`git`, `gh`, `hub`) | `scripts/deckhand/shims/` | workspace-hub | `platform-infra` / `security` | Generic wrappers enforcing scope at the `git`/`gh` boundary; installed to `~/.hermes/deckhand/shims`. |
| Setup / protection / onboarding tooling | `scripts/deckhand/` (`add-member.sh`, `protect-and-verify.sh`, `install-hermes-b2.sh`, `verify-hermes-b2.sh`, `templates/`) | workspace-hub | `platform-infra` / `security` | Config-driven, derives from `scopes.yml`; generic across clients/machines. |
| Tests | `tests/deckhand/` | workspace-hub | (matches code under test) | Engine + tooling tests; no client data. |
| Generic operator docs | `docs/deckhand/DEPLOYMENT.md`, `docs/deckhand/ONBOARDING.md` (**process only**), this map | workspace-hub | `platform-infra` | Generic deploy/onboarding *process*. **Member rosters are NOT generic** — see §4. |
| Scope-enforcement / orthogonality decisions | `docs/governance/2026-06-01-deckhand-scope-enforcement-below-model-decision.md`, `…-scope-routing-orthogonality-decision.md` | workspace-hub | `security` / `ai-orchestration` | Engine-architecture decisions, client-agnostic. |
| **Channel GTM strategy decision** | `docs/governance/2026-06-02-deckhand-channel-gtm-strategy-decision.md` | **aceengineer-strategy** | strategy | Business positioning/spend-posture decision → §4 relocation. |
| **Teams enterprise GTM deck** | `docs/gtm/deckhand-teams-enterprise-connectivity.html` | **aceengineer-strategy** | strategy | Client-facing GTM material → §4 relocation. |
| **Onboarded member roster** | name+ID table in `docs/deckhand/ONBOARDING.md` | **aceengineer-strategy** | strategy/client | Named real people mapped to client channels = client info → §4 relocation. |
| Client domain knowledge / data | `llm-wiki-acma`, `llm-wiki-doris` (+ off-repo `data_root`s) | llm-wiki-`<client>` | — | Per rule 3; never in workspace-hub. |
| Generic sanitized knowledge | generic `llm-wiki` | llm-wiki (generic) | — | Promoted from client wikis only via the abstraction gate. |
| Secrets / PATs / session / audit store | `~/.hermes/…`, off-repo audit dir | **none (runtime)** | `security` | Per rule 5; never committed (§5). |

---

## 4. RELOCATIONS NEEDED (client/strategy artifacts currently in workspace-hub)

These are in `workspace-hub` today but the contract (rules 1+2) places them in **`aceengineer-strategy`**. Move them; leave only the generic engine/process behind.

1. **`docs/gtm/deckhand-teams-enterprise-connectivity.html`** — client-facing enterprise GTM deck (Teams connectivity positioning). → **aceengineer-strategy** (GTM). Nothing generic to retain in workspace-hub.

2. **`docs/governance/2026-06-02-deckhand-channel-gtm-strategy-decision.md`** — business strategy/spend-posture decision (Telegram-led GTM, demand-driven other channels). → **aceengineer-strategy** (strategy). It is a *business* decision, not an engine-architecture decision; contrast the two `2026-06-01-deckhand-scope-*` governance docs, which are engine decisions and **stay**.

3. **Onboarded-member roster in `docs/deckhand/ONBOARDING.md`** — the "Onboarded so far" table maps **named real people → client channels** (acma/doris) with platform IDs. That is **client info** → **aceengineer-strategy**. **workspace-hub keeps only the generic onboarding *process*** (the two-layer auth model, capture-ID steps, `add-member.sh` usage). Replace the live roster with a pointer to the private roster in aceengineer-strategy.

**Legal rule (binding):** no client identifiers in workspace-hub code or tracked content. Enforced by `scripts/legal/legal-sanity-scan.sh` against the root [`.legal-deny-list.yaml`](../../.legal-deny-list.yaml) (client project names/codenames; `block` severity). Named client members in a tracked roster are the same class of leak the deny-list guards against — route them to the private repo. Note: stable **platform IDs** in `scopes.yml` (Telegram numeric IDs, E.164) are *not* names and are acceptable in the engine config; **display names are not.**

> Mechanics of the move (PR-only target repos): aceengineer-strategy is private; relocate via copy-in + delete-here in a single change set, opened as a PR (do not self-merge client-strategy moves). This map only records *what* moves and *why*; the relocation PR is tracked under [#2944](https://github.com/vamseeachanta/workspace-hub/issues/2944).

---

## 5. Host/runtime state on ace-linux-2 (NOT in any repo)

Per rule 5 — secrets and machine-local state live only under the runtime tree; never commit. (Runtime `~/.hermes` paths are allowed in docs; the repo's `check-no-abs-paths.sh` targets repo-internal hardcoded paths, not `~/.hermes`.)

| Runtime item | Path | Notes |
|---|---|---|
| Hermes gateway env | `~/.hermes/.env` | Gateway allowlists (`*_ALLOWED_USERS`), provider env. Gateway stays **closed**. |
| Deckhand scoped PATs | `~/.hermes/deckhand/secrets.env` | `chmod 600`; one fine-grained `DECKHAND_PAT_<SCOPE>` per scope (the real boundary; out-of-scope repo → 404). Rotate by 2026-06-08 ([#2936](https://github.com/vamseeachanta/workspace-hub/issues/2936)). |
| Plugin symlink | `~/.hermes/plugins/deckhand-scope` → `scripts/deckhand/hermes-plugin/deckhand-scope/` | Installed by `install-hermes-b2.sh`. |
| PATH shims | `~/.hermes/deckhand/shims/` ← `scripts/deckhand/shims/` | `git`/`gh`/`hub` wrappers prepended via patch `01`. |
| WhatsApp session | `~/.hermes/whatsapp/session` | Baileys session on owner's personal number (ban risk accepted; [#2940](https://github.com/vamseeachanta/workspace-hub/issues/2940)). |
| Audit store (raw) | `$DECKHAND_AUDIT_DIR/decisions.ndjson` (default under the host archive disk) | Path configured in `config/deckhand/policy.yml`; durable private store, never public. HTML summary renders to `docs/reports/`. |
| Hermes install | `~/.hermes/hermes-agent` | Upstream Hermes; patch set from `patches/hermes/` re-applied after Hermes updates. |

---

## 6. Domain tagging (GitHub label scheme)

Applied to Deckhand issues today (verified on the live label set):

- **`deckhand`** — every Deckhand issue carries this (color `#5319e7`; "Deckhand chatbot (Hermes-gateway scoped git/gh ops)").
- **Repo-routing labels** (which repo the work targets):
  - `repo:workspace-hub` — ecosystem engine (`#0e8a16`).
  - `repo:aceengineer-strategy` — client + GTM/strategy (`#b60205`).
  - `repo:hermes` — targets upstream Hermes; patches tracked in workspace-hub (`#1d76db`).
- **Engine domains** (`domain:*`): `domain:ai-orchestration`, `domain:platform-infra`, `domain:notification`, `domain:security` (+ `domain:platform-compat` where relevant).
- **Category** (`cat:*`): typically `cat:ai-orchestration` or `cat:operations` for Deckhand work.

**Rule for tagging future Deckhand issues:**
1. Always add `deckhand`.
2. Add exactly the `repo:*` label(s) for the repo the work lands in — use **`repo:aceengineer-strategy`** for any client/GTM/strategy work (per rule 2), **`repo:workspace-hub`** for engine work, **`repo:hermes`** when patching the upstream gateway.
3. Add the matching `domain:*` from the four engine domains (rule 1) and a `cat:*`.
4. If an issue spans engine + client, split it or apply both `repo:*` labels and keep client content out of the workspace-hub portion (§4 legal rule).
