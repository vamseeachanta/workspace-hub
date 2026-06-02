# Deckhand — knowledge map & fresh-session resume

> **Deckhand** is an authenticated chatbot that lets an **operator** drive `git`/`gh` actions on named
> repository **scopes** (acma, doris, ecosystem) from chat platforms, with enforcement **below the model**:
> scope authorization, no-destructive guard, per-scope fine-grained PAT (the real boundary), full audit,
> rate-limiting, and a closed gateway allowlist. Live host: **ace-linux-2**. Epic:
> [#2931](https://github.com/vamseeachanta/workspace-hub/issues/2931).

This folder is the **engine-side knowledge map**. Client/GTM/strategy material lives in the private
`aceengineer-strategy` repo (`strategy/deckhand/`).

## Read these in order (cold start)
1. **This file** — orientation + resume runbook (below).
2. [`REPO-DOMAIN-MAP.md`](REPO-DOMAIN-MAP.md) — *where every piece of work lives and why* (the routing contract).
3. [`ARCHITECTURE.md`](ARCHITECTURE.md) — the bot internals + the 5 enforcement layers (file:line grounded).
4. [`ISSUE-AND-DECISION-MAP.md`](ISSUE-AND-DECISION-MAP.md) — every issue, decision, plan, review artifact + open threads.
5. [`FILE-INVENTORY.md`](FILE-INVENTORY.md) — exhaustive manifest of every Deckhand file.
6. [`DEPLOYMENT.md`](DEPLOYMENT.md) — stand Deckhand up for a new client/machine.
7. [`ONBOARDING.md`](ONBOARDING.md) — per-platform member onboarding (generic process).
8. `../../CONTEXT.md` — glossary (scope vs channel vs delivery group, operator, etc.).

## Where the work lives (routing — full detail in REPO-DOMAIN-MAP.md)
| Repo | Holds |
|---|---|
| **workspace-hub** | The **engine**: code (`scripts/deckhand/`, `src/deckhand/`), config (`config/deckhand/`), Hermes patches (`patches/hermes/`), tests (`tests/deckhand/`), these docs. All infra issues. |
| **aceengineer-strategy** (private) | **All client info + GTM/strategy** — Teams GTM section, channel strategy, onboarded roster, business decisions. (`strategy/deckhand/`) |
| **llm-wiki-&lt;client&gt;** | Client domain knowledge/data (per `.claude/rules/wiki-sibling-routing.md`). |
| **Hermes** (upstream) | The gateway; required core patches tracked in `patches/hermes/`. |
| **ace-linux-2 host** | Runtime state, never committed (see below). |

## Status snapshot (2026-06-02)
- **Telegram** — LIVE (`@the_deckhand_bot`); acma + doris scopes; route-B group bindings; rate-limit live. **GTM-lead channel.**
- **WhatsApp** — LIVE (bot mode) but on the **owner's personal number** (Baileys ban-risk **accepted**, demand-driven; decide later). Groups created, bindings pre-staged awaiting `@g.us` JIDs.
- **Teams** — PLANNED ([#2941](https://github.com/vamseeachanta/workspace-hub/issues/2941), plan-review). Internal-only (D1 decided); blocked on client ingress decision (D2) + Azure app reg.
- **PAT hardening** — scoped PATs moved to `~/.hermes/deckhand/secrets.env` (chmod 600, shim-only); out of `.env` general-search + process env. Rotation pending [#2936](https://github.com/vamseeachanta/workspace-hub/issues/2936); at-rest encryption [#2943](https://github.com/vamseeachanta/workspace-hub/issues/2943).

## Issues (epic + children)
[#2931](https://github.com/vamseeachanta/workspace-hub/issues/2931) (epic) · [#2936](https://github.com/vamseeachanta/workspace-hub/issues/2936) PAT rotation · [#2937](https://github.com/vamseeachanta/workspace-hub/issues/2937) onboarding doc · [#2938](https://github.com/vamseeachanta/workspace-hub/issues/2938) rate-limit · [#2939](https://github.com/vamseeachanta/workspace-hub/issues/2939) WhatsApp · [#2940](https://github.com/vamseeachanta/workspace-hub/issues/2940) WhatsApp dedicated identity · [#2941](https://github.com/vamseeachanta/workspace-hub/issues/2941) Teams · [#2942](https://github.com/vamseeachanta/workspace-hub/issues/2942) installer plugin-symlink · [#2943](https://github.com/vamseeachanta/workspace-hub/issues/2943) PAT at-rest encryption · [#2944](https://github.com/vamseeachanta/workspace-hub/issues/2944) this documentation.
All tagged `deckhand` + `repo:workspace-hub`. Tag future Deckhand issues the same; client/strategy work → `repo:aceengineer-strategy`.

## Runtime/host state (ace-linux-2 — never committed)
```text
~/.hermes/.env                              # gateway + platform tokens
~/.hermes/deckhand/secrets.env              # chmod 600 scoped PATs (shim-only)
~/.hermes/plugins/deckhand-scope            # symlink → scripts/deckhand/hermes-plugin/deckhand-scope
~/.hermes/whatsapp/session/                 # WhatsApp pairing (creds.json)
${DECKHAND_AUDIT_DIR:-/mnt/dde/deckhand/audit}/decisions.ndjson   # audit  # abs-path-allowed
```

## Fresh-session resume runbook
1. **Orient:** read this file → REPO-DOMAIN-MAP → ARCHITECTURE → ISSUE-AND-DECISION-MAP.
2. **Confirm host:** you're on ace-linux-2. `hermes gateway status` → active; `curl -s http://127.0.0.1:3000/health` → WhatsApp connected.
3. **Confirm enforcement loads:** `/scope` registers (plugin symlink present); shims resolve PATs from `secrets.env`.
4. **Check live state:** `gh issue list --repo vamseeachanta/workspace-hub --label deckhand --state open` for open threads; the dashboard `docs/reports/deckhand-dashboard.html` for the running picture.
5. **Pick up open threads** (see ISSUE-AND-DECISION-MAP "open threads"): rotate PATs (#2936), Teams D2 (client) + Azure (#2941), installer plugin-symlink (#2942), reconcile #2940 deadline, resolve #2931 mixed status labels.
6. **Respect the gates:** plan→approve→implement for non-doc work; never self-approve; client/strategy artifacts route to aceengineer-strategy.
