# Session handoff — gpu-claw machine-equivalence reconcile + onboarding

**Date:** 2026-07-22 → 2026-07-23 · **Machine:** gpu-claw · **Runner:** Claude (Opus 4.8) · **Issues:** #3507 (complete), #3593, #3594 (filed)

## What was done

1. **Reconcile machine-equivalence analysis** (read-only first): fingerprint → collect → compare found 16 divergences; root-caused to (a) this clone 195 commits stale since Jul 13, (b) the ghost `unknown.json` blob from the pre-#3516 role-keyed publish scheme.
2. **Fast-forwarded** workspace-hub `231830597..f850b2cea` (+195); later ffs to `44cf1be23` as fleet main advanced.
3. **First equality collect** published `equality-gpu-claw.yaml` (commits `2b3b216fd`, `f47b35a11`) — matrix 5/5 machines active reporting.
4. **Managed crons applied** via transactional `cron_apply.py` (`--allow-live-reload`; live deckhand daemon untouched by the change): `equality-report` (Mon 04:30), `equivalence-sentinel` (17 */6), and — after commit `2df0a6f55` landed fleet-side — `repository-sync` (0 */4).
5. **Sentinel verified end-to-end**: published machine-keyed `gpu-claw.json` (role `contribute-minimal` auto-resolved from registry per #3516 fix `c23e0eca3`), self-cleaned the `unknown.json` ghost. Overnight cron cycle confirmed live (`logs/monitoring/equivalence-sentinel-2026-07-23.log`).
6. **Fleet compare after onboarding: 16 → 5 divergences**; all remaining are other machines' (ace-win-1/2 absent #3505/#3506, dev-primary session-analysis cron age unknown, dev-primary behind).
7. **Issues filed**: #3593 (repo-sync exclusion — core ask overtaken by `2df0a6f55`, commented with on-box verification; owner to close or rescope to the 8 remaining excluded jobs) and #3594 (registry gpu-claw entry stale: notes still say clone-pending/uv-missing). #3507 carries progress + completion + cross-link comments.

## Repo states at exit

| Repo | State |
|---|---|
| workspace-hub | main, tracks origin; **behind-origin and modified equality state/report files are EXPECTED steady-state residue** — 5 machines continuously rebuild the shared matrix; the new 4-hourly repository-sync cron owns catch-up |
| digitalmodel, deckhand, deckhand-licensed-runs-queue | untouched this session (clean per the Jul 22 reconcile report; one guard-approved squash-merged branch deletion each in digitalmodel/llm-wiki-acma remains available via `reconcile-ecosystem.sh --apply`, not run) |

## No-external-action status

All external writes were sanctioned-path: equality publishes via `publish-equality.sh`, fingerprint via `equivalence_state.py`, cron via `cron_apply.py`, issue comments via `gh`. No self-merges, no label mutations, no closes.

## Next steps

1. **Owner:** close #3593 as overtaken (or rescope to the 8 still-excluded jobs); plan-approve #3594 (T1 single-file registry edit).
2. **Any session:** plan #3594 per issue-planning-mode when batching small work.
3. **Watch:** ace-win-1/2 fingerprint absence (#3505/#3506) still the fleet's remaining equivalence gap.
