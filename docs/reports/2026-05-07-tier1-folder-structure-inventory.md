# Tier-1 Folder/File Structure Inventory — 2026-05-07

Purpose: initial, non-mutating inventory for repo-by-repo folder/file structure refactoring. This is evidence for `workspace-hub#2397` and the approved tier-1 refactor umbrella `workspace-hub#1962`.

## Scope

Canonical active scope from user memory/current request:

1. `workspace-hub` (this repo root)
2. `digitalmodel`
3. `assetutilities`
4. `worldenergydata`
5. `assethold`
6. `aceengineer-website`
7. `aceengineer-strategy`

## Live state snapshot

| Repo | Branch | Ahead/behind | Tracked dirty? | Canonical paths present | Immediate structure signals |
|---|---:|---:|---:|---|---|
| `workspace-hub` | `main` | `0/0` | yes | `.claude`, `.github`, `config`, `docs`, `scripts`, `src`, `tests` | Major root clutter: many embedded repos, provider/cache/worktree dirs, stray root files such as `**Complexity:**`, `**Date:**`, `**Issue:**`, `**Review`, `**Status:**`, plus generated/session artifacts. Dirty tracked state is limited to `.claude/state/session-signals/2026-05-07.jsonl` and `logs/orchestrator/hermes/skill-patches.jsonl`. |
| `digitalmodel` | `main` | `0/0` | no | `.claude`, `.github`, `config`, `docs`, `scripts`, `src`, `tests` | Python package layout is present and clean. Drift candidates: `benchmark_output`, `build`, `cache`, `dist`, `logs`, `memory`, `outputs`, `results`, `site`, `test_output_ss`, and several generated coverage files at root. |
| `assetutilities` | `main` | `0/0` | no | `.claude`, `.github`, `config`, `docs`, `scripts`, `src`, `tests` | Strong package layout, but has `src/assetutilities/tests` (explicit repo-structure anti-pattern), duplicated agent/slash-command surfaces, and root output dirs: `build`, `dist`, `htmlcov`, `logs`, `results`, `site`. |
| `worldenergydata` | `fix/worldenergydata-ci-readiness-20260507` | `0/0` | yes | `.claude`, `.github`, `config`, `docs`, `scripts`, `src`, `tests` | Not on `main`; has live tracked modifications in `src/worldenergydata/bsee/...`. Structure drift candidates: `_archive`, `backups`, `logs`, `output`, `results`, `site`, `test_output`, `systemd`, and root generated files. Defer structural moves until branch/dirty state is resolved. |
| `assethold` | `main` | `0/0` | no | `.claude`, `.github`, `config`, `docs`, `scripts`, `src`, `tests` | Has a malformed Windows-path directory literally named `src\\assethold\\tests\\test_data\\analysis\\Portfolio\\results\\Data` at repo root; also legacy `modules`, `agents`, `_coding_agents`, `business`, `dev_tools`, `htmlcov`, `site`, backup CLAUDE files, and mixed dependency artifacts. |
| `aceengineer-website` | `main` | `0/0` | no | `.claude`, `.github`, `config`, `docs`, `scripts`, `tests` | Static-site layout, no `src` expected without a frontend migration decision. Drift candidates: `blog_output`, `dist`, `logs`, root generated `stats.json`, and multiple phase-plan markdown files at root. Need website-specific allowed-root contract before moves. |
| `aceengineer-strategy` | `main` | `0/0` | no | `.claude` only | Content/strategy repo, not a Python package. Missing common control-plane paths (`AGENTS.md`, `.github`, `docs`) by current tier-1 expectations. Needs a content-repo exception/contract rather than Python repo normalization. |

## Initial repo-by-repo order recommendation

1. `digitalmodel` — first implementation candidate. It is clean, on `main`, high business/engineering value, and listed first in approved umbrella `workspace-hub#1962`. Start with low-risk generated-output/root-clutter boundaries; avoid domain package moves until a repo-specific plan is approved.
2. `assetutilities` — high leverage because other repos depend on it; must explicitly handle `src/assetutilities/tests` and public API compatibility.
3. `assethold` — clear structural defect (`src\\...` literal path) but depends on `assetutilities`; should follow shared-utility stabilization.
4. `worldenergydata` — defer until current non-main branch and dirty tracked changes are reconciled.
5. `aceengineer-website` — needs static-site-specific contract.
6. `aceengineer-strategy` — needs content-repo contract/exception, not source-tree normalization.
7. `workspace-hub` — broadest control-plane cleanup; should be handled as a dedicated governance/root-cleanup issue after per-repo rules are sharpened, or in parallel as docs-only contract work.

## Existing issue/workflow anchors

- `workspace-hub#1962` — approved tier-1 refactor umbrella (`status:plan-approved`, local marker exists).
- `workspace-hub#2397` — folder-structure contract epic with local draft plan, but no approval marker and no live `status:plan-review` label at inventory time.
- No exact existing `digitalmodel` issue was found for `chore(repo-structure): normalize digitalmodel folder/file structure`.

## Non-goals for this inventory

- No file moves performed.
- No generated artifacts deleted.
- No branch/worktree cleanup performed.
- No implementation without a repo-specific issue, plan, adversarial review, and user approval gate.
