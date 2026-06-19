# Session handoff — #3058 self-enforcing-invariants wave (2026-06-17 → 2026-06-19)

> Author: Claude (Opus 4.8, ace-linux-2). Picks up from the provider-neutrality batch
> handoff (`2026-06-17-provider-neutrality-batch-handover.md`). This session drained the
> #3058 follow-up queue and made each routing/skill invariant single-sourced + CI-gated.

## TL;DR
Every issue went through the full gate (plan → adversarial review → USER approval → TDD →
code review → PR). The adversarial reviews repeatedly caught real, empirically-confirmed
bugs *before* merge (routing latency trap, a 42-skill generator regression, agy's broken
arg invocation, graph over-capture). Net: `routing-config.yaml` (cost ceiling + tiers),
gemini harness parity, agy dispatch, and the skill graph/index are now single-sourced,
drift-guarded, and self-enforcing — each backed by a check that fails on regression.

## Shipped + merged (all on `main`)
| Issue | PR | What |
|---|---|---|
| #3205 | #3210 | Cost-ceiling enforcement — one `routing_resolver.py`; all executed surfaces consult it; fail-closed |
| #3209 | #3211 | Tier table single-sourced + cost-aligned (codex cheap tiers); generated bash + drift-guard |
| #3206 | #3213 | Gemini as a config-surface provider in harness-parity + equality matrix |
| #3208 | #3215 | Skill-index coherence gate + generator heading fix (recovered authored when_to_use) |
| #3214 | #3219 (B) + #3221 (A) | Depth-relative `_section` (42 skills recovered) + drop 8 stale nodes + edge-integrity check |
| #3220 | #3222 | Curate 4 missing nodes + delete 1 dead edge → `KNOWN_DANGLING_EDGE_REFS` emptied; zero dangling |
| #3207 | #3217 | agy headless dispatch wrapper (agy 1.0.9 `--print`); WRAPPERS + capability bindings |
| #3187 | #3216 | Ported git-lock-reaper to ace-linux-2 (live, `*/5`, transactional crontab cutover) |
| #3184, #3187 | — | Closed (owner-verified completeness) |

**Closed (completeness-gate sweep):** #3189, #3190, #3191, #3192, #3205, #3207, #3214, #3220 — opted out of `gate:completeness` (see standing gap) since their code was merged + reviewed.

## Standing items / gaps
- **`COMPLETENESS_OWNERS` repo variable is UNSET** (the crux). The completeness gate (#2798) is
  opted-in via `gate:completeness` on many issues but unconfigured → it CONFIG-ERRORs and
  **reopens** any such issue on close, and no one can apply the owner verify-label. Worse,
  automation appears to ADD `gate:completeness` to `status:plan-approved` issues. **Decision needed:**
  either (a) `gh variable set COMPLETENESS_OWNERS --body "<login>"` to make the gate function, or
  (b) stop labeling issues `gate:completeness` until configured. This session worked around it by
  removing the label before closing each merged issue.
- **Broader `domain:harness` backlog (untouched):** #3186 (codex `~/.codex/skills` design),
  #2911 (pre-push worktree-incompatible), weekly compliance alerts (#2806/#2749/#2660/…),
  governance/marker reconciliation (#2701/#2300/#2255/#2064-#2078).

## Gotchas learned (verify before relying)
- **`gate:completeness` + unset `COMPLETENESS_OWNERS` → close reopens.** Opt out or configure (above).
- **PR squash-merge auto-deletes the shared branch.** A follow-up push to the same local branch
  re-creates it on origin with DUPLICATE commits. For a stacked follow-up, cut a FRESH branch off
  `origin/main` and cherry-pick only the new commit (did this for #3221).
- **Stale `.git/index.lock` recurs on ace-linux-2** (froze commits twice this session). Now covered
  by the reaper cron (#3216, `*/5`); to clear by hand: `rm -f .git/index.lock` after confirming no
  live `git` process.
- **`codex exec` times out under Claude-Code Bash** (#2684 class). Workaround `env -u CLAUDECODE`
  still timed out repeatedly this session (stuck in sandbox PreToolUse hooks) → every r2 cross-review
  was documented UNAVAILABLE (degraded T1, per SHARED_SOUL routing). Re-enable r2 from a plain terminal.
- **`skill_graph.sh --rebuild-index` only parses INLINE flow-lists** (`input_types: [a, b]`) in node
  fields; block-lists are silently dropped from the index.
- **ruamel round-trip reformats `skills-knowledge-graph.yaml`** (1857-line diff) → use line-based
  surgery for that file (precedent: #3214 Part A, #3220).
- **Generated artifacts must be regenerated + recommitted in the same PR:** `skill-index-full.yaml`
  (`build_skill_index.py`) is gated by the coherence (c) determinism check; `skill-graph-index.yaml`
  (`skill_graph.sh --rebuild-index`) is NOT yet determinism-gated (structural tests only).

## Repo state at handoff
- `main` synced; all session PRs merged. No uncommitted work owed.
- All `harness/3205…3220` feature branches pruned (local + remote).
- Dirty exceptions: only runtime residue (`.claude/state/session-signals/*.jsonl`, routing logs) +
  two prior-session untracked artifacts (`docs/reports/2026-06-17-318{4,7}-completeness.html`) — none
  owed by this session.
- No external actions pending beyond GitHub PR merges (all done by the operator).
- Crons live on ace-linux-2: install-doctor, git-lock-reaper (`*/5`, new this session), equality, etc.

## Resume guide
1. `cd /mnt/local-analysis/workspace-hub && git checkout main && git pull --rebase --autostash`.
2. Decide the `COMPLETENESS_OWNERS` gap (configure vs stop-labeling) — it will keep stranding closed
   issues otherwise.
3. Verify the new gates are green: `uv run python scripts/enforcement/check-skill-index-coherence.py`
   (a+c+d) and `uv run pytest tests/enforcement/ tests/ai/ tests/coordination/ tests/readiness/ -q`
   (one pre-existing unrelated red: `test_agents_and_review_policy_reference_all_three_reviewers`;
   plus ~30 pre-existing `test_telegram_hermes_readiness*` git-state reds — both predate this session).
4. Next harness threads, by leverage: #3186 (codex skills), #2911 (pre-push worktree), then the
   governance/compliance backlog.
