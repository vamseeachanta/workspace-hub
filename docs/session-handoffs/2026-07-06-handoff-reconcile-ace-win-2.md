---
machine: ace-win-2 (ACMA-WS014)
session: machine equivalence reconcile
date: 2026-07-06
external_actions: git pushes only
---

# Handoff - ace-win-2 Machine Equivalence Reconcile

## Completed
- Recovered `C:/ws/digitalmodel` from detached mid-rebase on `.gitignore`.
- Preserved the `output_610/` ignore change on PR https://github.com/vamseeachanta/digitalmodel/pull/1457 because direct `main` push is blocked by repository rules.
- Restored local `digitalmodel/main` to `origin/main`; checkout is clean.
- Refreshed and pushed workspace-hub equality artifacts:
  - `27afe953f` - initial ace-win-2 equality report refresh.
  - `9a9585b37` - ace-win-2 curation/skill/memory sidecars plus refreshed matrix.
- Ran `scripts/curation/curate-session-memory.ps1` with UTF-8 env workaround:
  - `PYTHONUTF8=1`
  - `PYTHONIOENCODING=utf-8`
- Repaired shared skill-link health for sibling repos without leaving git dirt:
  - `aceengineer-admin`
  - `assetutilities`
  - `deckhand`
  - `digitalmodel`
  - `llm-wiki`
  - `worldenergydata`
- Added local-only deckhand `.git/info/exclude` entries for `.claude/skills/{guidelines,meta,workflows}/` so shared Windows junctions do not dirty that checkout.

## Verified Clean
- `workspace-hub` clean except this handoff before commit.
- `digitalmodel`, `aceengineer-admin`, `assetutilities`, `deckhand`, `llm-wiki`, and `worldenergydata` clean on `main`.
- `git diff --cached --check` passed before equality-sidecar commit.
- `bash scripts/legal/legal-sanity-scan.sh --diff-only` passed before equality-sidecar commit.

## Remaining Expected Gaps
- `llm-wiki-acma` still has 6 pre-existing dirty paths and 3 parked stashes. Previous note still applies: do not blindly apply `stash@{0}`; it was reported to reintroduce CRLF corruption and delete `README.md`.
- `ace-win-2` solver row remains below baseline because the Windows solver probe reports `present` rather than `licensed`; this is operator-only follow-up.
- `ace-win-2` Hermes provider rows remain divergent because local Hermes memory/skill/runtime surfaces are absent.
- `memory_freshness` remains missing evidence because the owner-gated memory bridge heartbeat is absent; bridge commit is owner-gated to dev-primary.
- `scheduler` remains drifted on this Windows host until Task Scheduler/cron parity is reconciled.

## Operational Notes
- Do not use PowerShell `Remove-Item` on junctions that point into `workspace-hub`; it followed provider-adapter junctions and emptied the canonical `.claude/skills` target. The skill tree was restored with `git restore --worktree -- .claude/skills`.
- `scripts/skills/resync-skill-links.sh --apply` also rewrites provider adapter links; after applying shared skill links, restore tracked `.codex/skills` and `.gemini/skills` symlink files in sibling repos.
- The Windows curation wrapper currently needs UTF-8 environment variables to avoid a cp1252 `UnicodeEncodeError` on the delta character in its status line.
