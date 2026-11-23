---
name: equivalence-publish-health
description: Diagnose and fix a machine whose equivalence-state fingerprint publish is absent, stale, or gate-length slow (the wh#3500 pre-push RUN_ALL deadlock signature). Use when the equality matrix shows PUBLISH-GATED / PUBLISH-STALE / MISSING-EVIDENCE on the publish-health row, or the sentinel reports absent-fingerprint / publish-slow divergences.
---

# Equivalence publish health — triage and fix

The machine-equivalence sentinel (`scripts/monitoring/equivalence-sentinel.sh`, daily cron)
publishes each box's fingerprint to the `equivalence-state` git ref. A box whose publish
cannot land is INVISIBLE to drift detection — and the #3500 incident showed the publish
itself can be deadlocked by the repo's own pre-push hook.

## The deadlock signature (wh#3500)

`refs/heads/equivalence-state` is a **disconnected plumbing-built chain** (hash-object /
mktree / commit-tree). The pre-push hook cannot attribute its diff, so:

1. Remote ref absent → every push gates as **new-branch `RUN_ALL`** → full tier-1 suites +
   coverage (60+ min, FUSE-heavy, holds the uv cache lock machine-wide).
2. The hour-long gate keeps the push from completing → **the ref is never created** →
   next cycle repeats. The gate blocks the very push that would end the gating.

Also note: a merge-base fallback (#3198) does NOT fix this — the state chain has no
merge-base with `origin/main`, so "conservative RUN_ALL" catches it every time.

## How it surfaces

| Surface | Signal |
|---|---|
| Equality matrix (`build-equality-matrix.py`) | `publish_health` row: **PUBLISH-GATED** (failed/>60s), **PUBLISH-STALE** (>26h), **MISSING-EVIDENCE** (never published) |
| Sentinel divergences | `absent-fingerprint` (roster machine missing from the ref), `publish-slow` (fingerprint carries `last_publish_duration_s` > 60) |
| Locally on the box | `.claude/state/equivalence/publish-health.json` (`{ts, duration_s, rc}`) |

## Triage (run on the affected box)

```bash
git ls-remote origin refs/heads/equivalence-state          # ref exists at all?
cat .claude/state/equivalence/publish-health.json           # last publish outcome
grep -c GIT_PRE_PUSH_SKIP scripts/monitoring/equivalence_state.py   # 0 = pre-#3500 script
ps -eo pid,etimes,args | grep -E "run-all-tests|pytest"      # gate currently burning?
```

- **Script pre-dates the fix** (grep = 0): sync the checkout to main (`git fetch origin
  main` + fast-forward). The fixed `equivalence_state.py` pushes with `GIT_PRE_PUSH_SKIP=1`
  — the hook's **audited** soft bypass (each use logs one JSONL line to
  `logs/hooks/pre-push-bypass.jsonl`). Never hand-strip the hook instead.
- **Ref absent remotely**: one successful publish creates it and breaks the loop for the
  whole fleet (existing-ref pushes diff as state-files-only and exit the hook early).
  Run `bash scripts/monitoring/equivalence-sentinel.sh` once, confirm it returns in seconds.
- **Sentinel never installed**: check the box's cron (`setup-cron.sh --check`) — an
  absent-fingerprint machine with no sentinel cron needs the cron, not a hook fix.
- **publish-health.json missing but sentinel runs**: the sentinel pre-dates #3502; sync main.

## Related

- Issues: wh#3500 (deadlock + fix), wh#3502 (this monitoring), wh#3198 (hook merge-base fix)
- Skill: `worktree-pre-push-bypass-for-tier1-checks` (the same audited bypass for worktree pushes)
- Memory: `reference_ace_linux_1_oom_hang_2026_07_12` (incident that surfaced the deadlock)
- Registry roster consumed by the absent check: `config/workstations/registry.yaml`
  (`schedule_variant != none` ⇒ expected to publish daily)
