# Handoff — agy Gemini lane + genuine statusline usage (rollout runbook)

**Date:** 2026-06-14 · **Issues:** [#3086], [#3087] · **Status:** code landed on `origin/main`; per-machine rollout in progress.

## What landed (all on `origin/main`)

The Antigravity CLI (`agy`) is now the ecosystem's quota-independent **Gemini delegation lane** (complements Claude Code = primary, Codex = review).

| Commit(s) | Change |
|---|---|
| `701fa73ab` | `scripts/agents/set-antigravity-default-model.sh` + `bootstrap-machine.sh` §2.10 — pin agy default model = **Gemini 3.1 Pro (High)** (idempotent merge; unconditional, converges even pre-install) |
| `4656c7051`, `b01ea6c9d` | `scripts/ai/assessment/gemini-usage.py` (SSoT) + `query_gemini` rewired — genuine Gemini usage, no fake `estimated` entry |
| `4445736d0`, `528674370` (+parser) | Statusline `G:` shows **genuine usage LEFT + days-to-reset** from a manual `/usage` snapshot + live 429 detection |

### How the `G:` segment works (why it's not auto-magic)
agy persists **no** quota to disk — `/usage` is TUI-only (no subcommand/JSON; `gemini -p "/stats model"` just prompts the model, doesn't read usage). So genuine usage comes from two free local signals, **most-recent wins**:
- **Manual snapshot** — you paste `/usage` into `scripts/ai/assessment/agy-usage-snapshot.py`; it captures `% remaining` + reset countdown ("Refreshes in Hh Mm") for the weekly and 5-hour windows.
- **Live 429** — the gemini CLI writes `/tmp/gemini-client-error-*.json` on exhaustion; parsed for a real reset. A 429 only overrides when **newer** than the last snapshot.

`G:` shows the **binding window** (least % left) as `G:<%left>·<Nd>` (e.g. `G:100%·6.6d`), `?` when the snapshot is stale (>48h), dim `G:-%` when no signal. The number is **usage left** (remaining), not spent — same as C:/O:.

## Per-machine rollout

| Machine | agy installed | Status |
|---|---|---|
| local workstation | yes | ✅ done (model pinned, snapshot captured, `G:100%·6.6d` verified) |
| ace-linux-2 | (user-run) | ✅ done manually by user 2026-06-14 |
| ace-linux-1 | ? | ⏳ pending — run runbook below |
| Windows (`D:\workspace-hub`) | ? | ⏳ pending — run runbook below (use `python`, Git Bash) |

## Runbook (run on each remaining machine)

```
1. cd <workspace-hub>            # Linux: /mnt/local-analysis/workspace-hub | Windows: /d/workspace-hub
   git pull

2. bash scripts/agents/set-antigravity-default-model.sh
   # verify: cat ~/.gemini/antigravity-cli/settings.json  → "model": "Gemini 3.1 Pro (High)"
   # (pre-stages correctly even if agy not yet installed)

3. bash scripts/memory/bootstrap-machine.sh          # ensures statusline wired (skip if already)
   printf '{}' | bash .claude/statusline-command.sh --usage-tail   # sanity: shows C:|O:|G:

4. # once agy is installed + logged in:
   #   in agy: /usage  → copy panel
   uv run scripts/ai/assessment/agy-usage-snapshot.py   # paste, Ctrl-D  (Windows: python ...)
   printf '{}' | bash .claude/statusline-command.sh --usage-tail   # expect G:<NN>%·<N.N>d
```

**Notes:** Step 4 needs a human (`/usage` is TUI-only). Re-run step 4 after future `/usage` reads to refresh the %; days-to-reset counts down on its own between captures. If agy isn't installed yet, do 1–3 now (G: shows dim `G:-%`), do 4 after install.

## Constraints / gotchas (recorded for the next session)
- **Cannot push from this checkout**: direct `main` push is classifier-denied; the pre-push coverage gate FAILs on absent sibling repos (`assetutilities`/`digitalmodel`/`worldenergydata`). Bypass = `SKIP_COVERAGE_REASON` (worked), but commits actually reach origin via the **parallel sync flow** or a user `!`-push. Verify with `git merge-base --is-ancestor <sha> origin/main`.
- **Shared-worktree hazard**: a parallel session repeatedly swept this session's uncommitted changes into its own commits + pushed them (clean, but watch for partial sweeps — `providers.sh` once landed before its `gemini-usage.py` dependency; graceful `||` fallback prevented breakage).

## Next steps
1. Run the runbook on **ace-linux-1** and **Windows**.
2. After the 5-hour Gemini window resets, refresh the snapshot to keep `G:` current.
3. Optional cleanup (noted on #3087): the repo-tracked `config/ai-tools/agent-quota-latest.json` still shows the old fake Gemini entry until a quota cron regenerates it via the fixed `query_gemini` — self-resolving.

[#3086]: https://github.com/vamseeachanta/workspace-hub/issues/3086
[#3087]: https://github.com/vamseeachanta/workspace-hub/issues/3087
