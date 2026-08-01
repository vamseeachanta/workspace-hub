# Session handoff — ace-win-2 reconcile + dirty-work preservation + Windows tooling

- **Machine:** ace-win-2 (ACMA-WS014), Windows
- **Span:** 2026-06-25 → 2026-06-28
- **Scope:** `/reconcile-ecosystem` for this box → equality column refresh → preserve all dirty work across siblings → land Windows-native ecosystem tooling. Operational automation (not issue-gated).

## Outcome — done, nothing lost

Verified against reflogs throughout; the only deletions were two confirmed-merged branches and regenerable build artifacts.

### Equality (this box's column)
- CIM-backed collect succeeded; `compute` went MISSING-EVIDENCE → CONFORMS.
- State published **state-only** (Linux cron owns the matrix HTML): `chore: equality report from acma-ws014` — `334c18659` (06-26), `2d0a296f4` (06-27).
- Residual reds (harness/kanban/memory/skills/scheduler) are **stale-peer artifacts** — dev-primary/dev-secondary show identical verdicts; clear when the Linux boxes re-collect. `solvers` BELOW-BASELINE is **by design** (licence probe, PR #2850). 5 codex/hermes provider rows: re-judge after peers refresh.

### Dirty work preserved (per repo)
| Repo | Action | Commit |
|---|---|---|
| workspace-hub | sibling-layout sync feature (`repository_sync` + `scripts/sync/*`) | `5149f23ef` |
| workspace-hub | licensed-run harness (runtime data gitignored) | `7ad0ffd25` |
| workspace-hub | Windows reconcile pair + working-python guard probe + README | `5abc12ea1` |
| workspace-hub | matrix HTML UTF-8 fix | in main (peer dup; local `b3c2b4882` deduped) |
| deckhand | go-live handoff doc | `8e373da` |
| raw-to-knowledge-playbook | docs + **merge-resolved** GP-50/51 collision → renumbered GP-55/56 (footer GP-57); both sides kept | `345f15d` |
| llm-wiki-acma (private) | recovery-distribution handoff doc | `662ecc4` (pushed to private origin) |

- **digitalmodel** `output_610/` — generated solver output, intentionally left untracked (preserved on disk).
- **`#2998` branches** deleted (`feat/2998-equality-refresh-wrappers` b54a4c473, `fix/2998-win-equality-collector-gitbash` c2ded1d97) — squash-merged + gone upstream.

### Tooling landed (OS pairs maintained)
- NEW `scripts/windows/reconcile-ecosystem.ps1` — resolves real Git Bash (not WSL stub), drives the canonical `.sh`. Pairs with `scripts/readiness/reconcile-ecosystem.sh`.
- FIX `scripts/readiness/reconcile-ecosystem.sh` — probes for a *working* python (prefers `python3`, falls back to `python`) so the branch-guard runs on Windows.
- NEW `scripts/windows/README.md` — OS-pair map + host gotchas.

## Host gotchas (ace-win-2)
- **Agent Bash tool / `!` prefix hang** (WSL stub shadows Git Bash + UNC/PATH stall). Everything ran via the operator's own PowerShell terminal; results tee'd to `C:\ws\*.txt` for the agent to read.
- **`python3` = Microsoft Store stub** (exit 49); **`python` is real** (hermes venv, 3.11.15 + PyYAML). Reconcile guard now probes; collectors use `python`.
- **`equality-report.ps1` dies under PS 5.1** in `Clear-GeneratedMatrixReport` (native git-stderr → terminating error). Workaround = state-only manual commit (collect+build succeed first).
- **Matrix HTML cp1252 corruption** — fixed by `encoding="utf-8"` on `write_text` (build-equality-matrix.py).
- **Heavy peer push-race** — most pushes needed fetch + rebase(--autostash) + retry.

## Repo states at exit
- workspace-hub: clean, 0 ahead/behind, **no stashes**.
- deckhand / raw-to-knowledge-playbook: clean, pushed.
- llm-wiki-acma: pushed; **3 stashes parked** for operator review.
- digitalmodel: `output_610/` untracked (intentional).

## External actions taken
- Pushes to origin/main on workspace-hub, deckhand, raw-to-knowledge-playbook, and (operator) llm-wiki-acma. No other external/outbound actions.

## Next steps (all optional, operator-discretion)
1. Review/clear llm-wiki-acma's 3 parked stashes.
2. Disable the `python3`/`python` App Execution Aliases (Settings → Apps → Advanced → App execution aliases) so `python3` stops shadowing the Store stub.
3. Re-collect the Linux boxes, then re-judge residual equality divergences (run-order: real config drift only).
4. Future Windows reconciles: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\windows\reconcile-ecosystem.ps1 [-- --apply]` — no more hand-rolled wrappers.
