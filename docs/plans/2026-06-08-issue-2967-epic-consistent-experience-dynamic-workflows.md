# Plan for #2967 (EPIC): consistent experience via dynamic workflows

> **Status:** draft → plan-review
> **Complexity:** T3 (systemic, cross-machine, multi-feature)
> **Date:** 2026-06-08
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2967
> **Children:** #2968 (F1) · #2969 (F2) · #2970 (F3) · #2971 (F4) · #2972 (F5)
> **Extends:** #2887 (equivalence measurement) · #2720 (Telegram control-plane contract)
> **Coordinates:** #2894 #2524 #2519 #2847 #2742
> **Client:** N/A
> **Decisions locked (user, 2026-06-08):** plan whole epic before approving any slice; failure-notification surface = JSONL (`logs/notifications/`) only, Telegram escalation deferred to F4.

---

## Resource Intelligence Summary

### Existing repo substrate (this plan EXTENDS, not greenfield)
- `config/workstations/registry.yaml` — already canonical for machine identity. Each machine carries `role`, `schedule_variant` (e.g. `full`), `storage`, `capabilities.agent_clis`, and a `telegram_hermes` block (`telegram_mode: coordinator|worker`, `dispatch_enabled`, `data_access_profile`, `bot_token_env`). **The role + schedule_variant + telegram_mode hooks already exist** — F1/F2/F3 extend this object, they do not invent it.
- `scripts/cron/setup-cron.sh` + `scripts/operations/workstation-status.sh` — already read `registry.yaml`; `setup-cron.sh` already keys off `schedule_variant`. F2's catalog plugs into this reader.
- `scripts/memory/bootstrap-machine.sh`, `scripts/readiness/remediate-harness.sh`, `scripts/readiness/compare-harness-state.sh`, `scripts/readiness/harness-config.yaml` — existing reconcile/compare primitives F1 builds on.
- `docs/ops/telegram-hermes-multimachine-control-plane.md` (#2720) — fail-closed git-ref-lease dispatch contract, `lease_ref = refs/heads/dispatch/leases/<issue>-<mode>`. F3 implements against this.
- `scripts/readiness/build-equality-matrix.py` + `collect-equality.sh` (#2801/#2887) — the measurement scoreboard F5 repairs.

### Verified divergence (live probe 2026-06-08, ace-linux-1 ↔ ace-linux-2)
| Surface | a1 `dev-primary` | a2 `dev-secondary` | Layer |
|---|---|---|---|
| project `.claude/settings.json` | md5 1c414c (10561B) | md5 1c414c (10561B) | git — EQUAL |
| user `~/.claude/settings.json` | 4010B (deny-list+hooks+effort) | 675B (none) | local — DIVERGENT |
| crontab | ~38 jobs | 9 jobs | local — DIVERGENT |
| `/mnt/workspace-hub` symlink | absent | present | local — hazard |
| role (de-facto) | orchestration/GitHub/NFS | comms-dispatch/client-wiki/OSS-sim | undeclared overlay |

### Gaps identified
- No machine **role-overlay** concept for the *local* layer (settings/hooks/skills) — only the git layer is reconciled today.
- No single declarative catalog for scheduled work; `schedule_variant` is a coarse on/off, not a per-job role tag.
- No live capability probe feeding dispatch — `registry.yaml` is declared, not measured.
- Telegram venue behavior is host-bound (lives on a2), not contract-defined.
- Equality matrix broken (see #2972) → divergence currently unmeasured.

### Evidence
- Probe commands + outputs recorded on #2967 (epic body) and #2972 (repro). Codex independent cross-review posted on #2967 (~23k tokens).
- Source count: 8 (registry.yaml, setup-cron.sh, bootstrap-machine.sh, #2720 doc, build-equality-matrix.py, live a1/a2 probe, #2887 body, Codex review). ✔

---

## Deliverable
A fleet where each machine converges to `git base + its declared role overlay`, scheduled work is one git-tracked role-tagged catalog, dispatch routes by measured capability, and the Telegram venue behaves identically regardless of host — with divergence continuously and loudly measured.

---

## Architecture — the four-layer backbone

```
 Layer 0  GIT BASE            project .claude/ (settings, skills, rules) — already EQUAL via git
 Layer 1  ROLE OVERLAY        registry.yaml.harness_profile → managed user-settings KEYS,
                              hook set, skill families, schedule_variant   [F1]
 Layer 2  WORKFLOW CATALOG    config/workstations/workflow-catalog.yaml → role-tagged jobs;
                              setup-cron.sh materializes this machine's subset             [F2]
 Layer 3  DISPATCH + ROUTING  capability-match dispatch (git-ref leases, #2720) + one
                              provider-routing policy; fed by LIVE probes not just declared  [F3]
 Layer 4  VENUE               Telegram delivery contract (idempotency/retry/audit), role
                              comms-dispatch reproduces it on any host                       [F4]
   �└─ MEASUREMENT (F5)        equality-matrix fixed + fail-loud → proves every layer converged
```

### Managed-surface contract (Codex finding #1 — blast-radius control)
Every local-state item is classified; the reconciler only ever touches the first class:

| Class | Examples | Reconciler action |
|---|---|---|
| **role-managed** | user-settings policy keys (deny-list, hooks, effortLevel), skill families, cron subset | converge to git declaration |
| **git-managed** | project `.claude/`, rules | already handled by git pull |
| **machine-private** | `/mnt/workspace-hub` symlink, GPU/sim config, local paths | leave untouched |
| **secret** | `~/.hermes/.env`, `~/.codex/auth.json`, `TELEGRAM_BOT_TOKEN` | **git declares required KEYS, never values; never written** |
| **intentionally-divergent** | theme, per-machine experiments | declared-divergent allowlist; reconciler skips |
| **uncataloged-live** (Codex MAJOR) | a live cron line / daemon not yet in the catalog (e.g. a2 deckhand escalation sweep, WhatsApp bridge) | **BLOCKS `--apply`** until explicitly classified as role-managed (catalog it) or machine-private/preserved. Never silently removed. |

**Decision Q1 (user, 2026-06-08): COMPOSABLE roles.** A machine carries a `roles: [...]` list; applied overlay = role-invariant `_base` + **union** of listed role overlays. Matches reality (a2 is both comms-dispatch and sim-worker) and keeps future single-purpose hosts expressible. Role definitions live in a new `config/workstations/harness-roles.yaml`; machines reference roles by name in `registry.yaml.harness_profile`:
```yaml
# config/workstations/harness-roles.yaml
roles:
  _base:                       # role-invariant — applied to EVERY managed machine
    user_settings_required_keys: [permissions.deny, hooks.Stop, hooks.SessionStart]
    skill_families: [core]
  control-plane:
    user_settings_required_keys: [effortLevel, env.REVIEW_GATE_STRICT]
    skill_families: [coordination, workspace-hub, research]
    schedule_jobs: [benchmarks, nightly-learning, memory-backup, equality-matrix, gtm]
  comms-dispatch:
    skill_families: [coordination, deckhand]
    schedule_jobs: [deckhand-member-audit, escalation-sweep, provider-utilization]
  sim-worker:
    skill_families: [engineering-sim]
    schedule_jobs: [solver-watch]
  licensed-solver:             # Q2: declared for routing, never converged (Windows/Task Scheduler)
    capabilities: [orcaflex, aqwa, ansys]

# registry.yaml  machines.<id>.harness_profile:
# dev-primary:    roles: [control-plane]              managed: true
# dev-secondary:  roles: [comms-dispatch, sim-worker] managed: true
# licensed-win-1: roles: [licensed-solver]            managed: false   # Q2 declare-only
# licensed-win-2: roles: [licensed-solver]            managed: false   # Q2 declare-only
# macbook-portable: deferred (Q2)
```
Apply = `_base ∪ role₁ ∪ role₂…`. **Conflict rule:** a key present in multiple overlays must be identical, else the reconciler **fails closed** (no silent last-writer-wins). `managed: true` is the per-machine opt-in gate before any write; `managed: false` hosts are declared for **F3 dispatch routing only**, never converged.

---

## Sequenced rollout (observability-first — Codex finding #4)

| Step | Feature | Mode | Gate |
|---|---|---|---|
| 1 | **F5** #2972 | implement | fix equality-matrix + fail-loud (JSONL). Make divergence visible FIRST. |
| 2 | **F1a** #2968 | inventory | classify all local state into the 5 classes above; commit the taxonomy. No writes. |
| 3 | **F1b** #2968 | dry-run | reconciler reports drift only (extends compare-harness-state.sh). No writes. |
| 4 | **F1c** #2968 | write (narrow) | enable write-mode for the **role-invariant** overlay only → closes a2 safety deny-list + hooks gap. **Additive key-level deep-merge only — never replace `settings.json` or hook arrays wholesale** (Codex MAJOR: a file/array replace could remove local Hermes/Telegram session exceptions). Merge required keys, preserve unrecognized local keys. |
| 5 | **F2** #2969 | shadow→cutover | catalog generates cron to a shadow file; diff vs live. **"Clean" is defined as: every preexisting enabled cron line is either cataloged or explicitly classified preserved — any uncataloged live line is a HARD BLOCK on cutover** (Codex MAJOR). Generated lines carry begin/end ownership markers; full `crontab -l` backup taken with a one-command restore; only the generated block is rewritten, non-generated lines preserved verbatim; post-cutover daemon health checks (Telegram/WhatsApp/deckhand/escalation) must pass. |
| 6 | **F3** #2970 | implement | capability-match dispatch + provider-routing policy + LIVE probes. |
| 7 | **F4** #2971 | implement | Telegram venue contract; role comms-dispatch reproduces it; pull JSONL→Telegram escalation here. |

Each step is its own plan + adversarial review + **user approval** before implementation. This epic plan authorizes the *sequence and contracts*, not the code.

---

## Per-feature deliverables & acceptance

**F5 #2972** — equality-matrix builds clean on a1+a2 (PEP-723 `dependencies=["pyyaml"]` + `uv run --script`, mirroring generate-agent-radar.py); fresh evidence committed; cron wrapper exits non-zero + writes a `logs/notifications/` JSONL record on failure (per user decision: JSONL only). *Detailed plan: `docs/plans/2026-06-08-issue-2972-equality-matrix-fix.md`.*

**F1 #2968** — `harness_profile` schema in registry.yaml + state-classification taxonomy committed + reconciler with `--dry-run` (default) / `--apply` (flagged). AC: dry-run on a2 reports the deny-list+hooks gap; `--apply` closes it; a re-run is a no-op (idempotent); secrets never read or written (proven by test).

**F2 #2969** — `workflow-catalog.yaml` (job: command, schedule, allowed_roles); `setup-cron.sh` materializes only this machine's role subset into a **marker-delimited generated block**, preserving all non-generated lines; shadow-diff mode. AC (strengthened per Codex MAJOR): (1) live `crontab -l` inventory committed as evidence before any change; (2) every preexisting enabled workspace-hub cron line is **either cataloged or explicitly classified preserved** — an uncataloged live line **blocks `--apply`**; (3) full crontab backup + documented one-command restore; (4) post-cutover `crontab -l` proves **zero unapproved net removals**; (5) post-cutover daemon health checks pass (Telegram/WhatsApp/deckhand/escalation on a2); (6) rerun is idempotent — no reorder/duplicate/mutation of preserved lines; (7) commands use `${REPO_ROOT}`, not absolute paths.

**F3 #2970** — capability-match dispatcher reading registry + LIVE probe; one provider-routing policy file (Claude=plan, Codex=review, Gemini=recon, Hermes=dispatch). AC: a request with capability X routes to the machine that *probes* capable (not just declares); stale self-report does not misroute (test with a forced-stale probe); lease timeout/renewal/split-brain handled (coordinate #2847).

**F4 #2971** — Telegram delivery contract: canonical bot ownership, chat/channel map, message schema, idempotency keys, retry/dead-letter, audit trail; comms-dispatch role overlay carries it. AC: same client request yields same result/status regardless of serving host; replayed message is idempotent; failed delivery lands in dead-letter + audit.

---

## TDD posture
Each feature lands test-first. Epic-level integration test (added with F2): given two fixture machines with roles `control-plane` and `comms-dispatch`, the reconciler + catalog produce role-correct settings/hooks/cron for each, idempotently, touching no secret.

---

## Adversarial Review Summary
| Provider | Verdict | Key findings |
|---|---|---|
| Codex (architecture, on #2967) | conditional-APPROVE | backbone right IFF managed-surface boundary + live probes + venue contract; observability-first ordering; don't promote settings wholesale — folded into this plan |
| Codex (this plan doc) | **MAJOR → resolved** | F2 cutover could silently drop a live a2 cron/daemon line (`setup-cron.sh --replace` overwrites whole crontab); taxonomy leaked on uncataloged-live items; F1c merge semantics unspecified; ACs too weak. **All folded:** added `uncataloged-live` blocking class, additive deep-merge for F1c, marker-block + backup/rollback + fail-closed + post-cutover daemon health checks + 7 strengthened F2 ACs. |
| Gemini | pending/optional | dispatch if quota available (T3 → 3-provider); degrade to T2 documented if 429 |

**Overall:** PASS — Codex MAJOR addressed in-plan; remaining gate is user approval (+ optional Gemini third opinion).

---

## Risks and Open Questions
- **Risk (Codex #1):** reconciler over-reach → mitigated by the 5-class taxonomy + dry-run default + per-machine `managed: true` opt-in.
- **Risk (Codex #2):** registry truth-vs-target staleness → F3 pairs declared capability with live probe.
- **Risk (Codex #3):** venue consistency ≠ control-plane consistency → F4 is a full delivery contract, not a config copy.
- **Risk:** `schedule_variant` is currently coarse; F2 must preserve existing `setup-cron.sh` behavior during shadow phase (no silent cron loss).
- **Resolved Q1 (2026-06-08):** COMPOSABLE roles (a machine has `roles: [...]`, overlay = `_base ∪ roles`). a1=[control-plane], a2=[comms-dispatch, sim-worker]. See §managed-surface schema above.
- **Resolved Q2 (2026-06-08):** declare `licensed-win-1/2` as `roles: [licensed-solver] managed: false` now (routing-only, never converged); defer `macbook-portable`.

## Complexity: T3
Systemic, multi-machine, five coordinated features; sequenced so each lands behind its own gate. This document is the architecture+sequencing contract; per-feature plans carry the TDD detail.
