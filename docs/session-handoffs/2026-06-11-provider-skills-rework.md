# Ecosystem Provider & Skills Rework — 2026-06-11

Session goal (user directive): review all skills in the repo ecosystem, understand the AI
providers (Claude / Codex / Hermes), and rework provider paths (CLAUDE.md, AGENTS.md,
codex configs, etc.) — "instructions written for prior models anchor Fable to stale
patterns, use your own judgment."

## Provider ground truth (verified against live config, 2026-06-11)

| Provider | What it actually is | Live model | Loaded surface |
|---|---|---|---|
| **Claude** | Interactive orchestration (Claude Code, Max subscription) | Fable 5 / Opus 4.8 / Sonnet 4.6 / Haiku 4.5 | root `CLAUDE.md` → `AGENTS.md` → `config/agents/claude/SOUL.runtime.md` |
| **Codex** | Adversarial-review lane + Hermes delegation target | **gpt-5.5** (`~/.codex/config.toml`) | `~/.codex/AGENTS.md` → symlink to `config/agents/codex/AGENTS.runtime.md` |
| **Hermes** | The cron/automation engine on ace-linux-1 | **gpt-5.5 via openai-codex provider** (`~/.hermes/config.yaml`) — NOT a Claude wrapper | `~/.hermes/SOUL.md` → symlink to `config/agents/hermes/SOUL.runtime.md` |
| **Gemini** | Third review lane / 1M-context overflow | gemini-3.1-pro-preview (registry claim; verify on live plan) | workspace `GEMINI.md` |

Key architecture: `config/agents/SHARED_SOUL.md` + per-provider `SOUL.delta.md` →
built runtime artifacts via `scripts/agents/build-soul-runtime.sh`. **Edit sources,
never `*.runtime.md`.** SOUL sources were reviewed and left unchanged — they are
model-agnostic and current.

## What was stale (two generations of drift)

1. **Hub registries (Feb-2026 generation)**: `claude-opus-4-6`, `claude-sonnet-4-5`,
   `gpt-4.1` as primaries; `routing-config.yaml` falsely claimed Hermes runs
   claude-sonnet-4.6 via copilot (it moved to gpt-5.5/codex after copilot's silent
   mid-session fallback broke context).
2. **Sibling repos (2025 claude-flow generation, ~70% of their `.claude/` trees)**:
   - `agents/` — 54 fictional swarm agent definitions (byzantine-coordinator, neural-*, hive-mind-*)
   - `commands/swarm|hive-mind|flow-nexus|sparc` — slash commands for MCP tools that never existed here
   - `settings.json` — `npx claude-flow@alpha` hooks firing (and failing) on EVERY Bash/Edit call;
     PreCompact hooks re-injecting "54 agents / GOLDEN RULE" propaganda into every compacted session;
     a standing `GIT_PRE_PUSH_SKIP=1 git push` allow rule (gate bypass)
   - `docs/CONTEXT_LIMITS.md` — token budgeting "Based on Claude 3.5/4 capabilities (200K context)"
   - Root `CLAUDE.md` gates pointing at the deprecated WRK-* work-queue (ecosystem is
     GitHub-issues-only via GSD since 2026-03-25)
   - "Task tool" naming throughout (harness tool is now `Agent`)

## Changes made (all commits LOCAL — not pushed; push was classifier-blocked pending owner authorization)

| Repo | Commit | Scope |
|---|---|---|
| workspace-hub | `79c521cdd` | model-registry/provider-capabilities/routing-config/ai-agents-registry → Fable 5 / Opus 4.8 / gpt-5.5 generation; Hermes role corrected; 6 scripts' hardcoded model maps updated (session-params, overnight-batch-planner, cost-tracker, ai-usage-summary, cross-review fallback, update-model-ids replacement map); GSD workflows Task→Agent tool; dspy skill examples → sonnet-4-6 |
| assetutilities | `46e994d` (pilot) | archive claude-flow era (agents/commands/docs/600-line CLAUDE.md → `.claude/_archive/claude-flow-era/`), clean settings.json + settings.local.json, root adapter → GitHub-issue gates |
| assethold | `b52209b` | same as pilot |
| teamresumes | `cce5c45` | same as pilot |
| aceengineer-admin | `b4eb229` | same (settings were already clean) |
| achantas-data | `bdd19c8` | same |
| hobbies | `a87c08e` | same |
| sabithaandkrishnaestates | `26c3882` | same |
| achantas-media | `8a78ac9` | root adapter line only (no `.claude/` tree) |
| CAD-DEVELOPMENTS | `1b0c98a` | minimal: archived stock swarm commands, Task→Agent tool in root CLAUDE.md (rest of its tree is current-gen) |

Everything archived via `git mv` into `.claude/_archive/claude-flow-era/` with a README —
fully reversible, history preserved, nothing deleted.

## Deliberately left alone

- **digitalmodel** (branch `feature/frps-ssr-global-riser-model`, dirty) and
  **worldenergydata** (branch `rework/bsee-adapters`, dirty, plus an unresolved merge
  conflict in `.claude/skills/bsee-data-extractor/SKILL.md`) — in-flight parallel
  sessions; touching their trees risks contaminating those branches. Their engineering
  skills (22 OrcaFlex/OrcaWave/mooring skills; 18 energy-data skills) are the crown
  jewels and must be preserved in any future sweep.
- **aceengineer-website** — sitting on stale branch `overnight/deepening-2026-05-24`; fix after it lands/dies.
- **acma-projects-freeze-work** — frozen snapshot; left untouched on purpose.
- **wshub-phase0 / wshub-wt-3027** — worktree copies of workspace-hub; canonical fix lives in workspace-hub.
- **Vendored third-party repos** (CAD-DEVELOPMENTS/{claude-flow,ruv-swarm,flow-nexus}) — not ours to edit.
- **Library reference docs** in hub skills (dspy/pandasai/lm-eval `references/`) — old model IDs
  there mirror upstream library docs; faithful examples, not operational config.
- **Memory snapshots & `_archive/` skills** — audit-trail / lesson content; old model mentions are historical record.
- **`.agents/skills/`** — a provider-fork of `.claude/skills/` (e.g., a mechanical
  `dspy.Codex(...)` variant). Left as-is; consolidation is a separate decision.
- **`config/agents/claude/SOUL.delta.md` + SHARED_SOUL.md** — reviewed, current, unchanged.

## CLOSEOUT — session exit (2026-06-11, final)

**Everything landed. Epic [#3040](https://github.com/vamseeachanta/workspace-hub/issues/3040) CLOSED with all 8 children closed.**
All 13 repos verified `main == origin/main`. `.codex/skills.bak` deleted by owner.

| Surface | Final state |
|---|---|
| Issues | #3036, #3037, #3038, #3039, #3040 (wshub) + digitalmodel#695 + worldenergydata#467 + aceengineer-website#17 — ALL CLOSED |
| PRs | assetutilities#87, digitalmodel#697, worldenergydata#468 — ALL MERGED (squash; protected mains) |
| worldenergydata extras | 3 conflict-corrupted skills repaired (bsee-data-extractor, npv-analyzer, production-forecaster); `tests/test_agent_doc_clean.py` generalized to scan all 49 live `.claude` docs |
| aceengineer-website | overnight branch safe-deleted (0 unique commits); its leftovers stashed — the stash contains a policy-violating `GIT_PRE_PUSH_SKIP` allow rule: **drop it, never restore** |
| hermes-model-switching skill | gpt-5.5 documented; 4 owner-applied visible-text `scanner-allow:hermes_env_access` sentinels (two human-run rounds — HTML-comment form trips `html_comment_injection`) |

**Dirty-state exceptions left deliberately (not this session's to clean):**
- workspace-hub: pre-existing tracked modifications from parallel sessions, incl. the live **#2889 session's** plan + signals (its 2 newer files were preserved across this session's 29-commit rebase and restored as tracked modifications; byte backups at `/tmp/wshub-preserve-2889/`); a redundant `autostash` stash entry (content already applied) is safe to drop
- digitalmodel: `feature/frps-ssr-global-riser-model` checkout, dirty — in-flight FRPS session; local `main` reconciled to origin's squash twin
- worldenergydata: `rework/bsee-adapters` checkout, dirty — in-flight; rebasing onto updated main will encounter the already-resolved SKILL.md conflicts

**No external/outward actions beyond:** GitHub issues/PRs/comments in the user's own repos and pushes the owner authorized.

**Next steps (none blocking):**
1. #2889 session: commit its restored plan/signals when it closes out; drop the redundant autostash
2. After FRPS + bsee-adapters branches merge: nothing claude-flow-related remains to do (already handled on main via worktrees)
3. Next model release: update `config/agents/model-registry.yaml` (`latest_models` + `context_windows_k`) — scripts now read it; R-MODEL-DRIFT will flag live-config drift nightly

## ADDENDUM — same-session issue sweep + resolution (later on 2026-06-11)

All open items were converted to GitHub issues and immediately resolved where
agent-permitted. Tracking epic: [workspace-hub#3040](https://github.com/vamseeachanta/workspace-hub/issues/3040)
(authoritative status table in its comments). Highlights:
- [#3037](https://github.com/vamseeachanta/workspace-hub/issues/3037) CLOSED — Gemini live-verified: 2.5-pro primary, 3.1-pro-preview 429s on Pro plan
- [#3039](https://github.com/vamseeachanta/workspace-hub/issues/3039) CLOSED — `.agents/skills` is a LIVE Gemini CLI surface; KEEP + README
- [#3038](https://github.com/vamseeachanta/workspace-hub/issues/3038) core shipped — `scripts/lib/model-registry.sh` reader, 2 script migrations, R-MODEL-DRIFT nightly check
- [#3036](https://github.com/vamseeachanta/workspace-hub/issues/3036) HUMAN-GATED — scanner-allow one-liner posted for owner
- digitalmodel#695 / worldenergydata#467 / aceengineer-website#17 — implemented on each repo's local `main` via git worktrees (in-flight branches untouched); wed's 12 committed conflict blocks resolved (WAR/APD superset kept)
- CAD-DEVELOPMENTS phase-2 done (13 stock dirs archived; origin is collaborator-owned — no upstream issue)

The push list now covers **13 repos** (see #3040 comment).

## Open items / follow-ups (original list — see #3040 for live status)

1. **Push the 10 local commits** (blocked for agent; owner runs):
   `for r in workspace-hub assetutilities assethold teamresumes aceengineer-admin achantas-data hobbies sabithaandkrishnaestates achantas-media CAD-DEVELOPMENTS; do git -C /mnt/local-analysis/$r push; done`
   (workspace-hub is also 28 commits behind origin — pull/rebase first there.)
2. **hermes-model-switching SKILL.md** edits (gpt-5.5 note) are staged-but-uncommitted in
   workspace-hub: pre-existing `~/.hermes/.env` mentions trip the new skill-content
   security scanner (CRITICAL/exfiltration). Owner decision: allowlist the doc or reword it.
3. **`.codex/skills.bak/`** (57 superseded codex skill adapters, untracked) — recommend deleting; agent deletion was classifier-blocked.
4. **digitalmodel + worldenergydata** — run the same modernization (script preserved at
   `/tmp/modernize_repo.sh`, pilot pattern in assetutilities commit) once their branches merge.
   Also resolve the bsee-data-extractor SKILL.md merge conflict.
5. **Gemini model verification** — registry says gemini-3.1-pro-preview; verify against the live Google AI Pro plan.
6. Phase-2 candidates: remaining claude-flow stock commands in CAD-DEVELOPMENTS
   (sparc/stream-chain/truth/verify/pair/training), `.agents/skills` fork consolidation,
   making `overnight-batch-planner.py`/`session-params.py` read model IDs from the registry
   instead of hardcoding (the registry is currently aspirational, not operational SSoT).
