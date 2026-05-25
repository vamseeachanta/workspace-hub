# Session handoff — crash recovery + ecosystem merge consolidation

- **Window:** 2026-05-23 (unexpected shutdown) → 2026-05-25
- **Machine:** ace-linux-1
- **Scope:** recover uncommitted work after an unexpected shutdown; consolidate pending merges across the repo ecosystem.

## Outcome summary

Nothing was lost. Everything genuinely at risk was committed and pushed. One item remains intentionally unpushed pending CI verification (worldenergydata, below).

### Landed & pushed
- **Config migration (2026-05-22 skills/AGENTS.md canonicalization)** committed + pushed to `main` across 8 repos: aceengineer-admin/-strategy/-website, achantas-data/-media, CAD-DEVELOPMENTS (rebased — origin is bakkiprasad5669's, had diverged), kaggle-rogii-2026, teamresumes. `scripts/enforcement/` left untracked (machine-local convention).
- **llm-wiki**: 11 standards commits pushed (`35fa0b6d..df5241f2`).
- **llm-wiki-acma**: Sirocco B1528/#2760 report committed + pushed (`1d81308..25606ef`).
- **workspace-hub**: `issue/2778-llm-wiki-routing-from-main` merged into `main` (`4c349d3b6`) + `#2775` SSO reference docs recovered (`568dcd3ec`). Conflict on `.claude/rules/calc-citation-contract.md` resolved by keeping #2778's version (main's deletion was an accidental auto-sync artifact — README still listed the rule active). 27/27 #2778 tests GREEN. Commit gate cleared via sanctioned per-line `scanner-allow:` sentinel (no --no-verify). Fleet has since advanced main past this (now `3bfcbe769`, synced).
- **worldenergydata #398** (Dependabot scrapy 2.13.4→2.16.0): squash-merged (`5466b880`). scrapy is legacy-only in repo; CI green.

### Preserved on origin (durable)
- `workspace-hub` branches: `recovery/crash-20260523-authored` (`aca670f3` — authored work snapshot; content now on main), `issue/2778-llm-wiki-routing-from-main`, `preserved/2026-05-21-routine-sync-run`.

### Branch cleanup (verify-then-delete via merge-tree no-op test)
- **Deleted (content byte-identical to main):** workspace-hub `issue-2389-provenance-claude`, `issue-2767-disposition-codex`, `issue-2766-ace-linux-1-normalization`, `issue-2769-backup-disposition-claude`; aceengineer-website `fix/14-blog-merge-conflict`.
- **Skipped — hold content NOT in main (tip SHAs recorded for re-push within gc window):**
  - worldenergydata `codex/burn-20260511-worldenergydata-bundle` (`a5ade8ef`) — GENUINE unmerged work (see below)
  - worldenergydata `docs/handoff-2026-05-03-lt-epic-closed` (`10cc2126`) — stale; add/add conflicts in data catalog/metadata (epic #373 closed)
  - worldenergydata `plan/411-bsee-war-bridge` (`9d7b7610`) — stale; executed-plan artifact (#411 closed)
  - aceengineer-website `codex/burn-20260427-issue-2357` (`8910c615`) — stale; config-migration divergence (skills relocated on main)
  - assethold `fix/50-settings-merge-conflict` (`fe84b89d`) — stale; main resolved settings.json differently (#50 closed)

## RESOLVED — 2026-05-25 (follow-up session)

The single open item below was completed: worldenergydata's reconciled merge is **verified and merged to `origin/main`**.

- Verified via PR #433 (`verify/codex-burn-20260511-merge` → main): all CI green — Test Python 3.10/3.11/3.12, Type Check, Security, Lint.
- The local `uv run pytest/black/isort` hang was bypassed using version-pin-matched standalone tools (`~/.local/bin/black 25.9.0`, `isort 8.0.1`, `uvx flake8`); two PR-introduced **formatting-only** lint nits (Black on `production_api12.py`, isort on the new smoke test) were fixed.
- Landed via fast-forward push `5466b880..ecbba21b` (local `main == origin/main`, zero divergence for the active session). PR #433 MERGED.
- `codex/burn-20260511-worldenergydata-bundle` deleted (merge now on main); temp `verify/...` branch auto-deleted on merge.
- The 4 stale skipped branches were also deleted (with explicit confirmation): worldenergydata `docs/handoff-2026-05-03-lt-epic-closed`, `plan/411-bsee-war-bridge`; aceengineer-website `codex/burn-20260427-issue-2357`; assethold `fix/50-settings-merge-conflict`. SHAs recorded in the follow-up session log for gc-window recovery.

---

## OPEN ITEM — needs next-session action  (RESOLVED above; retained for history)

### worldenergydata `codex/burn-20260511` merge — reconciled locally, NOT pushed
- **Local `main` = `5343dbee`** (0 behind / 5 ahead of `origin/main`). This is a clean reconciled merge of `origin/codex/burn-20260511-worldenergydata-bundle` + current main.
- **Content (genuine, relevant, verified):** api12 NPV→FDAS refactor (`production_api12.py` routes through `fdas.core.financial.calculate_npv`; all import targets confirmed present on main; main never diverged on that file), bounded CLI smoke-test harness (`scripts/audit/cli_smoke_verify.py` + tests), #353 scheduler timeout-validation doc.
- **Why unpushed:** local test run (`uv run pytest` on `test_production_api12_npv_fdas.py` + cli smoke tests) hit a **uv build hang** (timeout, EXIT=124) — could not verify locally. Per verify-before-push, NOT pushed to main.
- **NEXT STEP:** verify the 3 test files pass (via CI by opening a PR from `codex/burn-20260511` → main, or a working venv), then push `main` (or merge the PR) and delete `codex/burn-20260511`. The reconciled merge is reproducible (clean) if local `main` is reset.
- **Dirty exception:** `scripts/enforcement/` untracked (machine-local vendored hook — expected, do not commit).

### Remaining triage (low priority)
- 4 stale skipped branches above were force-deleted 2026-05-25 after explicit confirmation (see RESOLVED block). ✓

## Repo states at exit
- All repos `main == origin/main` EXCEPT worldenergydata (5 ahead, unpushed — above).
- workspace-hub: fleet ACTIVE (gateway up, ~262 kanban workers), on `main`, synced.
- No external actions pending (no emails/PRs/issues awaiting), except the worldenergydata CI verification.
