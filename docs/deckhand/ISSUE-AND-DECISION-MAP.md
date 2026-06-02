# Deckhand — Issue & Decision Map

> Navigable index of every Deckhand issue, governance decision, plan, and review artifact.
> Entry point for a fresh session to recover full state and history.
> Companion docs (same dir): `ARCHITECTURE.md`, `REPO-DOMAIN-MAP.md`, `FILE-INVENTORY.md`, glossary at repo-root `CONTEXT.md`.
> Generated under [#2944](https://github.com/vamseeachanta/workspace-hub/issues/2944). Host for all live work: ace-linux-2. As of 2026-06-02.

---

## 1. Issue table

All issues are in repo `workspace-hub`, label `deckhand`, OPEN. [#2931](https://github.com/vamseeachanta/workspace-hub/issues/2931) is the **epic/parent**; the rest are children.

| # | Title | State | Status label | Domain | One-line |
|---|---|---|---|---|---|
| [#2931](https://github.com/vamseeachanta/workspace-hub/issues/2931) | Plan Deckhand named repository scopes & scope policy | OPEN | plan-review **+** plan-approved (mixed) | security, notification | **EPIC.** Defines named scopes (ecosystem/acma/doris), repo-scope policy, no-delete guardrail, audit. Parent of all below. |
| [#2936](https://github.com/vamseeachanta/workspace-hub/issues/2936) | Rotate Deckhand PATs by 2026-06-08 (transcript exposure) | OPEN | needs-plan | security, ops | Two fine-grained PATs (`*_ACMA`, `*_DORIS`) pasted into transcript 2026-06-01 → treat as exposed, regenerate + revoke by 2026-06-08. |
| [#2937](https://github.com/vamseeachanta/workspace-hub/issues/2937) | Seamless member-onboarding guide (living doc) | OPEN | needs-plan | notification, ops | Maintain `docs/deckhand/ONBOARDING.md`, one section per connected platform; Telegram section done, others stubbed. |
| [#2938](https://github.com/vamseeachanta/workspace-hub/issues/2938) | Wire + harden rate-limit / abuse controls (live enforcement) | OPEN | needs-plan | security, ops | Policy + pure logic exist but live `pre_tool_call` plugin does NOT yet enforce caps; wire per-operator/per-scope limits, LLM-turn quota, gh backoff. |
| [#2939](https://github.com/vamseeachanta/workspace-hub/issues/2939) | Connect WhatsApp platform — channels + onboarding | OPEN | needs-plan | notification, ai-orchestration | Pair via Baileys, add acma/doris WhatsApp groups→scopes, onboard by E.164. Mirrors Telegram model. |
| [#2940](https://github.com/vamseeachanta/workspace-hub/issues/2940) | Migrate WhatsApp off personal number → dedicated bot number | OPEN | (no status label) | notification | Child of #2939. WhatsApp live on owner's **personal** number; ban-risk to personal comms; original deadline 2026-06-08 (now relaxed — see GTM note). |
| [#2941](https://github.com/vamseeachanta/workspace-hub/issues/2941) | Connect Microsoft Teams platform (Bot Framework) | OPEN | plan-review | notification, ai-orchestration | Teams via Bot Framework webhook; **blocked** on client ingress decision (D2) + Azure app registration. Has a full plan doc. |
| [#2942](https://github.com/vamseeachanta/workspace-hub/issues/2942) | install-hermes-b2.sh should symlink the deckhand-scope plugin | OPEN | (no status label) | ai-orchestration | Installer symlinks shims but not the `deckhand-scope` plugin → `/scope` won't load on a fresh machine until linked by hand. Low priority. |
| [#2943](https://github.com/vamseeachanta/workspace-hub/issues/2943) | Encrypt scoped PATs at rest (keyring / age / systemd) | OPEN | (no status label) | security, notification | Follow-up to 2026-06-02 partial hardening (PATs moved to chmod-600 `secrets.env`); still plaintext at rest → encrypt via age/keyring/LoadCredential. |
| [#2944](https://github.com/vamseeachanta/workspace-hub/issues/2944) | Aggressively document all work + fresh-session knowledge map | OPEN | (no status label) | documentation, ai-orchestration | This documentation effort. Owner-authorized 2026-06-02 to bypass plan gate (docs are non-destructive, PR-reviewable). |

### Relationships
- **Parent/child:** [#2931](https://github.com/vamseeachanta/workspace-hub/issues/2931) (epic) → all of #2936–#2944. [#2940](https://github.com/vamseeachanta/workspace-hub/issues/2940) is also a child of [#2939](https://github.com/vamseeachanta/workspace-hub/issues/2939) (WhatsApp connect).
- **Siblings / relates:** [#2939](https://github.com/vamseeachanta/workspace-hub/issues/2939)↔[#2937](https://github.com/vamseeachanta/workspace-hub/issues/2937) (onboarding doc) and [#2901](https://github.com/vamseeachanta/workspace-hub/issues/2901) (platform parity). [#2943](https://github.com/vamseeachanta/workspace-hub/issues/2943)↔[#2936](https://github.com/vamseeachanta/workspace-hub/issues/2936) (PAT lifecycle). [#2938](https://github.com/vamseeachanta/workspace-hub/issues/2938) board task `t_d94406ab`.
- **External relates (not deckhand-labelled here):** [#2900](https://github.com/vamseeachanta/workspace-hub/issues/2900) (fanout board), [#2902](https://github.com/vamseeachanta/workspace-hub/issues/2902) (delivery-group contract), [#2903](https://github.com/vamseeachanta/workspace-hub/issues/2903) (reply-policy guardrails), [#2741](https://github.com/vamseeachanta/workspace-hub/issues/2741) (destructive-action canary), [#2798](https://github.com/vamseeachanta/workspace-hub/issues/2798) (completeness gate, applied to #2931).

---

## 2. Current status snapshot — LIVE / PLANNED / DEFERRED

**LIVE**
- **Telegram** — primary GTM channel. Bot `@the_deckhand_bot`, phone-less, gateway-closed (numeric-ID allowlist + group membership routes scope). acma + doris scopes live.
- **WhatsApp** — running in bot mode via Baileys, paired on the **owner's personal number** (demand-driven posture; ban-risk explicitly accepted by owner 2026-06-02, "leave it running, decide later"). acma/doris WhatsApp groups served.
- **PAT compartmentalization** — partial hardening shipped 2026-06-02: PATs moved out of general `.env` into a dedicated chmod-600 `secrets.env` read only by the git/gh/hub shims (still plaintext at rest).
- **Rate-limit (partial)** — policy + pure logic exist and enforce in the pure module; **NOT yet wired into the live `pre_tool_call` plugin** ([#2938](https://github.com/vamseeachanta/workspace-hub/issues/2938)).

**PLANNED**
- **Teams** ([#2941](https://github.com/vamseeachanta/workspace-hub/issues/2941), plan-review) — blocked on client ingress decision **D2** + Azure app registration; net-new public HTTPS ingress required on ace-linux-2.
- **PAT rotation** ([#2936](https://github.com/vamseeachanta/workspace-hub/issues/2936)) — regenerate + revoke exposed tokens (original due 2026-06-08).
- **PAT at-rest encryption** ([#2943](https://github.com/vamseeachanta/workspace-hub/issues/2943)) — age / keyring / systemd LoadCredential.
- **Live rate-limit enforcement** ([#2938](https://github.com/vamseeachanta/workspace-hub/issues/2938)) — wire caps into the live gateway path.
- **Installer plugin symlink** ([#2942](https://github.com/vamseeachanta/workspace-hub/issues/2942)) — add plugin `ln -sfn` to installer.

**DEFERRED / RELAXED**
- **WhatsApp dedicated-number migration** ([#2940](https://github.com/vamseeachanta/workspace-hub/issues/2940)) — the 2026-06-08 deadline is **relaxed to demand-driven** by the GTM strategy note (NOT yet edited on the issue; owner said "decide later"). Prefer official Business Cloud API when a client funds it, over a speculative second number.

---

## 3. Decision log

| Date | Decision | Status | One-line |
|---|---|---|---|
| 2026-06-01 | Scope enforcement below the model | **proposed — NOT plan-approved** | Per-scope policy enforced in 3 layers (model=guidance only, process git/gh interceptor, server scoped fine-grained PAT); every allow+deny audited. `docs/governance/2026-06-01-deckhand-scope-enforcement-below-model-decision.md`. |
| 2026-06-01 | Scope/routing orthogonality | **proposed — NOT plan-approved** | A *scope* (which repos + permission) is orthogonal to *routing* (delivery group / origin chat); coupled only by sensitivity-clearance. Prevents silent fanout of private-repo activity. `docs/governance/2026-06-01-deckhand-scope-routing-orthogonality-decision.md`. |
| 2026-06-02 | Channel GTM strategy — Telegram-led, others demand-driven | **RECOMMENDED DIRECTION — owner leaning, NOT ratified** | Lead GTM with Telegram (free phone-less bot identity); WhatsApp/Signal/Teams stood up per client engagement, client owns its number, engagement funds official no-ban path. Only *firm* call: leave WhatsApp POC running as-is, decide later. `docs/governance/2026-06-02-deckhand-channel-gtm-strategy-decision.md`. |

Both 2026-06-01 decisions await the formal [#2931](https://github.com/vamseeachanta/workspace-hub/issues/2931) plan gate (plan → adversarial review → user approval → implement); they are design-session conclusions, not ratified.

---

## 4. Plan index (`docs/plans/`)

| Plan file | Issue | Status |
|---|---|---|
| `2026-06-01-issue-2941-deckhand-teams-connect.md` | [#2941](https://github.com/vamseeachanta/workspace-hub/issues/2941) | plan-review (T2; blocked on owner D1 + client D2) |
| `2026-06-01-issue-2931-deckhand-message-lifecycle-poc.md` | [#2931](https://github.com/vamseeachanta/workspace-hub/issues/2931) | proposed — POC scope only, NOT plan-approved (Mermaid flowcharts) |
| `2026-06-01-deckhand-improvement-roadmap.md` | [#2931](https://github.com/vamseeachanta/workspace-hub/issues/2931) | synthesis (Claude + codex zoom-out); tiered backlog, not a gated plan |
| `2026-06-01-deckhand-delegation-plan.md` | [#2931](https://github.com/vamseeachanta/workspace-hub/issues/2931) | lane/delegation plan (active working doc) |
| `2026-05-31-issue-2900-deckhand-board-level-plan.md` | [#2900](https://github.com/vamseeachanta/workspace-hub/issues/2900) | draft (T3; not in adversarial review) |
| `2026-05-31-issue-2900-deckhand-multiplatform-fanout-preliminary-plan.md` | [#2900](https://github.com/vamseeachanta/workspace-hub/issues/2900) | preliminary-draft (T3; not in review) |

---

## 5. Review-artifact index (`scripts/review/results/`)

All dated 2026-06-01. Titles only:
- `2026-06-01-deckhand-audit-code-review.md`
- `2026-06-01-deckhand-b2-plan-codex.md`
- `2026-06-01-deckhand-delegation-codex.md`
- `2026-06-01-deckhand-engine-code-review.md`
- `2026-06-01-deckhand-hook-adversarial-codex.md`
- `2026-06-01-deckhand-hook-hardening-verification.md`
- `2026-06-01-deckhand-onboarding-plan-codex.md`
- `2026-06-01-deckhand-pipeline-code-review.md`
- `2026-06-01-deckhand-platform-connectivity-and-terminology-codex.md`
- `2026-06-01-deckhand-runtime-code-review.md`
- `2026-06-01-deckhand-whatsapp-identity-recon.md`
- `2026-06-01-deckhand-wiring-recon-codex.md`
- `2026-06-01-deckhand-zoomout-codex.md`

---

## 6. Glossary

Canonical glossary lives at repo-root `CONTEXT.md` (`# Deckhand`). It defines the load-bearing terms that keep scope and routing from collapsing into one overloaded word:
- **scope** — named set of repos + permission policy ("which repos, read/write/destructive?"); e.g. `ecosystem`, `acma`, `doris`.
- **channel** — a single reachable transport destination (a Telegram chat, Slack `#channel`, Discord channel, contact); what `gateway/channel_directory.py` enumerates.
- **delivery group** — a named set of channels a notification fans out to (#2902).
- **fanout** — sending one explicit notification to every channel in a delivery group.
- **permission level** — what a scope authorizes against its repos: read vs write (write ≠ destructive).
- **sensitivity / clearance** — a scope declares a sensitivity (acma=private, ecosystem=internal); a delivery group declares the clearances it may receive. The single coupling between otherwise-orthogonal scope and routing.
- **operator** — an authorized sender; gateway allowlist (`*_ALLOWED_USERS`/pairing) plus each scope's own operator list.
- **destructive operation** — irreversible action denied separately from write: repo/branch/tag/release deletion, force-push/history rewrite, `reset --hard`, `clean`.

---

## 7. Open threads / next actions (pick-up list for a fresh session)

1. **Ratify or revise the GTM strategy note** ([#2940](https://github.com/vamseeachanta/workspace-hub/issues/2940) deadline still says 2026-06-08 on the issue but is unmodified — reconcile with the demand-driven recommendation).
2. **PAT rotation** ([#2936](https://github.com/vamseeachanta/workspace-hub/issues/2936)) — exposed tokens still need regen + revoke (due 2026-06-08); needs-plan.
3. **Wire live rate-limit enforcement** ([#2938](https://github.com/vamseeachanta/workspace-hub/issues/2938)) — gate before scaling members; needs-plan. Tied to roadmap Tier-1 "single audited enforcement seam" + "prove the 7 bypass paths".
4. **Encrypt PATs at rest** ([#2943](https://github.com/vamseeachanta/workspace-hub/issues/2943)) — choose age vs keyring vs systemd LoadCredential.
5. **Teams** ([#2941](https://github.com/vamseeachanta/workspace-hub/issues/2941)) — await owner D1 (tenant/identity model) + client D2 (public-ingress mechanism) before build; T2 cross-review still pending.
6. **Installer plugin symlink** ([#2942](https://github.com/vamseeachanta/workspace-hub/issues/2942)) — quick fix: add `ln -sfn` for `deckhand-scope` + assert `/scope` registers in `verify-hermes-b2.sh`.
7. **Onboarding living doc** ([#2937](https://github.com/vamseeachanta/workspace-hub/issues/2937)) — keep `ONBOARDING.md` current as each platform/member comes online.
8. **Formal plan gate for [#2931](https://github.com/vamseeachanta/workspace-hub/issues/2931)** — the two 2026-06-01 governance decisions remain *proposed*; ratification flows through the plan-approval gate.
