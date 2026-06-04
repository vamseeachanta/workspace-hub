# Tier-1 Indexing Freshness Report

Generated: 2026-06-04T03:30:59-05:00
Scope: `workspace-hub`, `digitalmodel`, `assetutilities`, `aceengineer-website`
Working directory: `/mnt/local-analysis/workspace-hub`
Mode: scheduled freshness audit; local report refresh only; no new cron jobs scheduled.

## Overall Status

Portfolio status: **red**

Material drift since the corrected 2026-06-03 baseline: **no material drift detected at the status level**.

Important correction to the stale prior `latest` report: the 2026-06-03 report body incorrectly marked sibling checkout surfaces for `digitalmodel`, `assetutilities`, and `aceengineer-website` as missing. This refresh used the requested nested path first and then sibling fallbacks under `/mnt/local-analysis/` when nested repos were absent. The sibling fallbacks are present and are the current inspected paths for those three repos.

## Status Summary

| Repo | Inspected path | Status | Status driver |
|---|---:|---:|---|
| `workspace-hub` | `/mnt/local-analysis/workspace-hub` | **red** | Missing repo-local operator map and registry; active broken legacy `.agent-os` links in `docs/README.md`; root/index/runtime noise weakens routing trust. |
| `digitalmodel` | `/mnt/local-analysis/digitalmodel` | **red** | Required canonical surfaces exist, but `README.md` still has an active broken `specs/data-needs.yaml` reference; source/docs cache noise remains. |
| `assetutilities` | `/mnt/local-analysis/assetutilities` | **yellow** | Required canonical surfaces exist and inspected links are clean; remaining issue is trusted-path Python cache/package noise. |
| `aceengineer-website` | `/mnt/local-analysis/aceengineer-website` | **red** | Missing machine-readable registry `docs/registry/module-routing.yaml`; test/script cache noise remains. |

## Per-Repo Findings

### workspace-hub — red

Canonical surfaces checked:
- `AGENTS.md` — present
- `README.md` — present
- `docs/README.md` — present
- `docs/maps/workspace-hub-operator-map.md` — **missing**
- `docs/registry/module-routing.yaml` — **missing**

Exact broken or stale references:
- `docs/README.md:300` -> `../.agent-os/product/mission.md` — broken legacy `.agent-os` target
- `docs/README.md:301` -> `../.agent-os/product/tech-stack.md` — broken legacy `.agent-os` target
- `docs/README.md:302` -> `../.agent-os/product/roadmap.md` — broken legacy `.agent-os` target
- `docs/README.md:303` -> `../.agent-os/product/decisions.md` — broken legacy `.agent-os` target
- `docs/README.md:264` includes `.agent-os/` in the repo structure tree as an active-looking path.

Noise observed in trusted/root paths:
- Root-level runtime/cache/log artifacts remain visible under trusted index scope, including `.coverage`, `.git/index.bak`, `.mypy_cache/`, `.baseline-cache/logs/pre-commit-quick.log`, multiple `.claude/**/cron.log` / maintenance logs, `.claude/state/uv-cache/**`, and `.planning/**/logs/*.log`.

Concise next actions:
1. Add a repo-local `docs/maps/workspace-hub-operator-map.md` or explicitly document the canonical alternative in current routing surfaces.
2. Add `docs/registry/module-routing.yaml` or document why workspace-hub is exempt from the registry contract.
3. Replace active `.agent-os` links in `docs/README.md` with current canonical surfaces only.
4. Move/cache-ignore runtime artifacts that sit inside trusted index paths.

2026-04-22 scorecard assumption check: **needs revision for workspace-hub**. It remains the control-plane repo, but the current routing/index surfaces are not yet trustworthy enough to be treated as green.

### digitalmodel — red

Canonical surfaces checked:
- `AGENTS.md` — present
- `README.md` — present
- `docs/README.md` — present
- `docs/maps/digitalmodel-operator-map.md` — present
- `docs/registry/module-routing.yaml` — present

Exact broken or stale references:
- `README.md:73` -> `specs/data-needs.yaml` — broken active routing/data-needs reference.

Noise observed in trusted paths:
- Python cache/package noise remains under `src/digitalmodel/**/__pycache__/`, `docs/domains/orcawave/L01_aqwa_benchmark/__pycache__/`, and `scripts/**/__pycache__/`.

Concise next actions:
1. Fix or remove `README.md:73` `specs/data-needs.yaml` reference.
2. Clean and prevent `__pycache__` / `*.pyc` artifacts in source, docs, and scripts paths.
3. Keep `docs/registry/module-routing.yaml` and `docs/maps/digitalmodel-operator-map.md` synchronized when modules move.

2026-04-22 scorecard assumption check: **partially holds but needs revision**. `digitalmodel` still has the strongest engineering source/test structure and has the required routing surfaces, but an active broken README reference keeps it red.

### assetutilities — yellow

Canonical surfaces checked:
- `AGENTS.md` — present
- `README.md` — present
- `docs/README.md` — present
- `docs/maps/assetutilities-operator-map.md` — present
- `docs/registry/module-routing.yaml` — present

Exact broken or stale references:
- None detected in inspected canonical surfaces.

Noise observed in trusted paths:
- Python cache/package noise remains under `src/assetutilities/**/__pycache__/`, including common readers, visualization, webscraping, and module utility subpackages.

Concise next actions:
1. Clean `src/assetutilities/**/__pycache__/` and `*.pyc` artifacts.
2. Keep the operator map and registry as the canonical placement surfaces for future issue work.
3. Preserve yellow status until trusted source paths are clean or the noise is proven ignored/non-indexed.

2026-04-22 scorecard assumption check: **holds with hygiene caveat**. Prior code-placement concerns are improved by present canonical surfaces; index hygiene remains the blocker to green.

### aceengineer-website — red

Canonical surfaces checked:
- `AGENTS.md` — present
- `README.md` — present
- `docs/README.md` — present
- `docs/maps/aceengineer-website-operator-map.md` — present
- `docs/registry/module-routing.yaml` — **missing**

Exact broken or stale references:
- None detected in inspected canonical surfaces.

Noise observed in trusted paths:
- Python cache/package noise remains under `scripts/**/__pycache__/` and `tests/**/__pycache__/`.

Concise next actions:
1. Add `docs/registry/module-routing.yaml` for machine-readable routing, or explicitly document a current canonical registry alternative.
2. Clean `scripts/**/__pycache__/`, `tests/**/__pycache__/`, and `*.pyc` artifacts.
3. Keep website edit routing anchored to `AGENTS.md`, `README.md`, `docs/README.md`, and `docs/maps/aceengineer-website-operator-map.md` until the registry exists.

2026-04-22 scorecard assumption check: **needs revision**. The website has understandable human-facing routing surfaces, but the missing registry keeps durable machine routing incomplete.

## Portfolio-Level Drift and Trust Notes

- No new status-level drift detected versus the corrected 2026-06-03 baseline.
- The local `latest` report was stale before this refresh because it reported sibling fallback repos as missing. That stale evidence is corrected here.
- Do not use or recommend legacy `.agent-os` reference patterns. Existing `.agent-os` references above are reported only as broken/stale references to remove or replace.
- The 2026-04-22 tier-1 indexing scorecard assumptions still hold only directionally. They need repo-specific revision where current evidence differs:
  - `workspace-hub`: control-plane strength remains, routing/index hygiene is red.
  - `digitalmodel`: source/test strength remains, but active README broken reference is red.
  - `assetutilities`: routing surfaces are now present; status is yellow due to index hygiene, not missing surfaces.
  - `aceengineer-website`: human routing exists; machine-readable registry remains missing.

## Next Actions

1. Fix `workspace-hub/docs/README.md` broken legacy `.agent-os` links and add/declare current canonical operator map + registry surfaces.
2. Fix `digitalmodel/README.md:73` `specs/data-needs.yaml` reference.
3. Add `aceengineer-website/docs/registry/module-routing.yaml` or documented current registry alternative.
4. Clean trusted-path runtime/cache noise in all four repos, prioritizing `workspace-hub` root/index noise and `src/**/__pycache__` in engineering packages.

## Verification Notes

- Local report refreshed at `docs/reports/tier-1-indexing-freshness-latest.md`.
- No new cron jobs scheduled.
- This report intentionally uses current canonical routing surfaces only.
