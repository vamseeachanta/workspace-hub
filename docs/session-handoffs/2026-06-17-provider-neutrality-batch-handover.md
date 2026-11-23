# Session handoff — provider-neutrality harness batch (2026-06-17)

> For a fresh session to continue the harness / provider-neutrality work. Author: Claude (Opus 4.8, ace-linux-2). Companion to `2026-06-17-repo-ecosystem-sync-and-3187-lock-reaper.md`.

## TL;DR
A multi-provider session-log review (ace-linux-1 + ace-linux-2; Claude/Codex/Hermes/Gemini) produced a harness assessment → fed epic **#3058** ("make ecosystem invariants self-enforcing"). This session shipped the **install-doctor**, contributed to the **lock-reaper/sentinel**, and implemented + merged the **4-issue provider-neutrality batch**. All went through the full gate (plan → adversarial review → user approval → TDD → tests → PR). The harness is now materially more self-healing and provider-neutral.

## Shipped + merged (live on `main`)
- **#3184 install-doctor** (`scripts/maintenance/harness-install-doctor.sh`) — cron `11 */6`, repair arm for the report-only equivalence-sentinel (#3059). **Deployed live on ace-linux-1 + ace-linux-2.** PR #3185.
- **#3187 lock-reaper + return-to-main guard + sentinel drift dims** — landed via parallel session PR #3194; my `git_heal_index` live-holder hardening merged via #3197 (#3196).
- **Provider-neutrality batch (all merged):**
  - **#3192** (#3201) — `routing-config.yaml` `execution_contexts` cost ceiling + `docs/governance/2026-06-17-cost-ceiling-policy.md` (SSoT). **ADVISORY ONLY** (routers don't parse it yet — see #3205).
  - **#3191** (#3202) — `.claude/workflows/{issue-gate-chain,tdd-implementation,cross-provider-review-workflow}.yaml` + `schema/workflow.schema.json` + `tests/workflow/` (21 tests). Data, not enforcement.
  - **#3189** (#3203) — `.claude/memory/topics/INDEX.md` generator + `config/agents/gemini/MEMORY.runtime.md` + `GEMINI.md` read-pointer + `scripts/memory/recall.py` + skill. Bridge wired (`bridge-hermes-claude.sh`). 48 tests.
  - **#3190** (#3204) — `scripts/ai/build_skill_index.py` → `config/agents/skill-index-full.yaml` (833 skills) + `scripts/ai/skill_router.py` + `run_agent.py` `--query`/prepend/exit-code-fix; **agy = first-class in router, unsupported for dispatch** (no headless mode). 23 tests.

## Owner-pending (do these)
- **Close #3187 and #3184** — both still OPEN (completeness gate). Records are stamped; apply the owner verify-label fresh (after the last body edit) then close:
  ```
  gh issue edit 3187 --repo vamseeachanta/workspace-hub --remove-label status:completeness-verified
  gh issue edit 3187 --repo vamseeachanta/workspace-hub --add-label status:completeness-verified
  gh issue close 3187 --repo vamseeachanta/workspace-hub --reason completed
  # #3184: add label (absent) then close
  ```

## Open work — prioritized (all under epic #3058)
**Deferred follow-ups from this batch (ready to plan):**
1. **#3205 (HIGH)** — executed-router consolidation: make the #3192 cost ceiling actually ENFORCED (today advisory; `tier_router.sh`/`task-dispatcher.py` hold hardcoded chains — 3 drifted copies). Highest-leverage next.
2. #3206 — `provider_harness_parity.py`: assert the Gemini memory surface (needs `gemini` in `PROVIDERS`, scope the install/runtime checks).
3. #3207 — agy headless dispatch wrapper (promote agy from unsupported when `agy --help` exposes headless).
4. #3208 — skill-index coherence/drift check (curated graph vs full index) + `config/agents/README.md`.
5. #3186 — reconcile `~/.codex/skills` design (symlink-for-unification vs native `.system`) — not started.

**Broader #3058 / provider-neutrality landscape (pre-existing, NOT touched this session):**
- **#3114** — Omnigent-lens umbrella: make the ecosystem AI-provider- & OS/machine-equivalent (extends #2887/#2967/#3058). The strategic parent for this whole theme.
- **#3116** — G1 portable agent-definition format (define once, run on any harness). `run_agent.py` + `config/agents/agent-defs/*.agent.yaml` + `provider-capabilities.yaml` capability_bindings already exist as the substrate.
- **#3118** — G3 MCP-first tool exposure (provider-portable tools).
- **#3137 / #3138** — skill-invocation instrumentation (capture Skill-tool calls + backfill from transcripts) — the missing "real usage signal" that blocks skill retirement.

## Key context / gotchas (verify before relying — see auto-memory)
Read these memory files first (`~/.claude/projects/-mnt-local-analysis/memory/`):
- **`routing-config-is-advisory.md`** — routing-config tier/context maps are documentary; runtime routers hold hardcoded chains + don't parse it. Editing it does NOT change routing (the crux of #3205).
- **`harness-provider-neutrality-state.md`** — config/agents/ is the SSoT layer; install drifts per machine; corrected several false "gaps".
- **`gsd-hooks-cross-repo-propagation.md`** — "Cannot find module gsd-*.js" = satellite repos reference hooks resolving only in workspace-hub (not missing files).
- Ecosystem facts: `cron-report-pipeline-roles.md`, `deckhand-live-host.md`, model IDs in `config/agents/model-registry.yaml` (never hardcode — Model-ID Sourcing Guard).

Operating gotchas learned this session:
- **Parallel-work collision is real**: a concurrent session implemented #3187 and merged #3194 while I had a duplicate (#3195, closed). Before implementing a plan-approved issue, re-check `gh pr list --search <issue#>` + in-flight branches RIGHT BEFORE coding.
- **ace-linux-1 (primary) parks off `main`** on handoff branches + had a stale `.git/index.lock` (froze git ~5h). Its pre-push hook runs the FULL digitalmodel suite (pushes take minutes). Don't casually `git push` there.
- **Guards that bite**: Model-ID Sourcing Guard flags literal model-IDs even in comments (and shifting baselined lines); abs-path baseline; harness-file-size (CLAUDE/AGENTS/GEMINI/MEMORY.md ≤20 lines); skill-content scanner flags `uv run` (MEDIUM, non-blocking). Append-at-EOF to avoid shifting baselined lines.
- **Completeness gate (#2798)**: every `status:plan-approved` close auto-reopens unless a `completeness {json}` record is on the body AND `status:completeness-verified` is applied (fresh, after the last body edit) by an owner ≠ the agent.
- **Gates honored**: never self-apply `status:plan-approved` / `status:completeness-verified`; plan→review→USER approves→TDD→cross-review. Plan-stage used 1 adversarial Claude lens; full cross-provider `scripts/review/plan-review-fanout.sh` recommended at CODE stage before merge.

## How to resume
1. `cd /mnt/local-analysis/workspace-hub && git checkout main && git pull --rebase --autostash origin main`
2. Read the memory files above + this handoff.
3. Verify state: `gh issue list --repo vamseeachanta/workspace-hub --label domain:harness --state open`.
4. Highest-leverage next: **plan #3205** (executed-router consolidation) — it turns the advisory cost ceiling into real enforcement and collapses the 3 drifted routing copies.
5. New cron is live; check it's running: `uv run --script scripts/cron/cron-audit.py | grep -E 'install-doctor|git-lock-reaper|return-to-main'`.

## Repo/branch state at handoff
- `main` synced (all batch PRs merged). Local feature branches `harness/319x-*` are merged + can be pruned.
- No uncommitted work owed. Cron deployed (install-doctor live both boxes; lock-reaper/guard live on ace-linux-1 via #3194).
