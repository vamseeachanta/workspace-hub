# Rewire L8: prune keep list (proposal, no moves yet)

- Issue: workspace-hub#4005 (layer L8 of RFC #3997, epic #3993). Tier B.
- Status: **PROPOSAL.** Nothing is moved or deleted by this document. Moves wait for the owner's keep-list board card.
- Inventory taken 2026-10-09 at `origin/main` 22467edb, on ace-linux-1.
- Per-skill rows: [2026-10-09-rewire-l8-prune-inventory.csv](2026-10-09-rewire-l8-prune-inventory.csv) (`skill_path, family, claude_session_mentions_16d, proposal, reason`).

## 1. Summary

| Surface | Today | Keep | Retire candidates | Notes |
|---|---:|---:|---:|---|
| Skills (active `SKILL.md`, outside `_archive/`) | 1,032 | 434 | 598 (496 now + 102 after rollout) | 2,100 more already sit in `.claude/skills/_archive/` (3,132 total) |
| Agents (`.claude/agents/`) | 39 (+5 new roles in this PR = 44) | 8 | 36 | 6 L3 roles + 2 domain specialists |
| Hooks (`.claude/settings.json`) | 28 wired entries, 26 unique scripts | 10 | 16 | RFC's "21" predates recent additions |
| Commands (`.claude/commands/`) | 166 | 67 (review later) | 99 | `gsd/` 81 + `sparc/` 18 go with their agents |

Targets from #4005: skills about 400, agents = role set + named specialists, every hook has a keep/drop reason. The keep list lands at 434 skills, or 374 if the marine duplicate decision (section 7) goes to `aceengineer-agents`.

## 2. Usage evidence

- **No reliable skill-usage log exists.** `.claude/state/skill-invocations/` and `skill-usage-report/` stopped on 2026-06-15 (Hermes logs).
- Claude transcripts were scanned on ace-linux-1 (879 files, retained back to 2026-09-23), ace-linux-2 and ws014.
  - Explicit Skill-tool calls to hub skills: one (`reconcile-ecosystem`). Everything else was built-in or plugin skills.
  - `SKILL.md` paths read in sessions: 111 distinct hub skills on ace-linux-1. Most reads were the old gate chain: `issue-planning-mode` 2,203, `pre-completion-cleanup-audit` 1,856, `work-queue` 324, `shared-risk-workflow` 279, `resource-intelligence` 208, `work-queue-workflow` 178, `workflow-gatepass` 152.
- Codex sessions mention about 5,600 skills per skill path. That is the skill catalogue Codex loads into every session, not real use. It shows what the catalogue costs, but it cannot be used to rank skills.
- No `subagent_type` call to any repo agent appears in the retained Claude transcripts on ace-linux-1.

The `claude_session_mentions_16d` column in the CSV is this ace-linux-1 count.

## 3. Skills

### 3.1 Rules (first match wins; the CSV records the rule per skill)

| Rule | Proposal |
|---|---|
| Off-topic families: creative, gaming, leisure, travel, apple, smart-home, social-media, media, red-teaming, mlops, science, marketing, business-marketing, autonomous-ai-agents, test-dummy-validation | retire now |
| `_internal/{builders,documentation,meta}` (template fragments parsed as skills, e.g. `step-1-name`), `_core/bash` (generic bash fragments) | retire now |
| `development/sparc`, claude-flow `development/github/*` swarm leftovers, unused doc-tool wrappers | retire now |
| Generic business templates (`business/{marketing,content-design,customer-support,product,enterprise-search,productivity,communication}`), generic `productivity/*` tool wrappers, `ai/prompting`, Gemini skills | retire now |
| Auto-learned session notes (`workspace-hub/learned/*`, `workspace-hub-learned/*`) with no session use | retire now |
| Old gate-chain process skills (plan review, gatepass, work-queue, overnight waves, adversarial-review prompts, closeout loops) | **retire after rollout**: they still back the current chain, so they move only when RFC W2 D5 removes that chain from `AGENTS.md` |
| Domain: `engineering/*` (incl. marine-offshore 60, standards, cad, cfd, drilling), `digitalmodel/*`, `data/*`, `field-dev-code-recon` | keep |
| Infrastructure and owner workflows: remaining `workspace-hub`, `coordination`, `github`, `operations`, `devops`, `email`, `memory`, `mcp`, LLM-wiki `research/*`, business admin/finance/legal/sales, tax | keep |

One manual override: `coordination/pre-completion-cleanup-audit` is kept, because `AGENTS.md` still names it as a closeout step.

### 3.2 Counts by family

| Family | Active | Keep | Retire now | Retire after rollout |
|---|---:|---:|---:|---:|
| workspace-hub | 150 | 30 | 105 | 15 |
| _internal | 129 | 6 | 123 | 0 |
| engineering | 89 | 89 | 0 | 0 |
| data | 85 | 85 | 0 | 0 |
| business | 74 | 30 | 44 | 0 |
| development | 72 | 51 | 18 | 3 |
| workspace-hub-learned | 70 | 1 | 32 | 37 |
| coordination | 60 | 34 | 0 | 26 |
| _core | 53 | 7 | 46 | 0 |
| software-development | 35 | 6 | 10 | 19 |
| mlops | 21 | 0 | 21 | 0 |
| creative | 20 | 0 | 20 | 0 |
| github | 19 | 17 | 0 | 2 |
| operations | 17 | 17 | 0 | 0 |
| email | 16 | 10 | 6 | 0 |
| research | 15 | 11 | 4 | 0 |
| ai | 15 | 6 | 9 | 0 |
| productivity | 11 | 3 | 8 | 0 |
| autonomous-ai-agents | 9 | 0 | 9 | 0 |
| travel, marketing, science, media, apple, social-media, gaming, business-marketing, smart-home, red-teaming, leisure, test-dummy-validation | 43 | 0 | 43 | 0 |
| digitalmodel, devops, memory, finance, mcp + 7 single-skill families | 25 | 25 | 0 | 0 |
| **Total** | **1,032** | **434** | **496** | **102** |

### 3.3 Duplicates

| Duplicate set | Size | Proposal |
|---|---:|---|
| hub `engineering/marine-offshore/*` and `aceengineer-agents` `plugins/ace-marine-dynamics` | 60 of 60 hub marine skills share a basename | **owner decision** (section 7) |
| `raw-to-knowledge-playbook` skills and `aceengineer-agents` `plugins/ace-knowledge` | 14 of 14 | keep `aceengineer-agents` as the source; playbook links to it |
| Same basename twice inside the hub's active tree (e.g. `naval-architecture`, `session-corpus-audit`, `sync`, `gmail-data-extraction`) | 12 | resolved by the moves: one copy kept |
| Near-duplicate auto-learned notes (e.g. 7 `diagnose-*-venv-shebang-*`, 6 `portable-baseline-*`) | about 100 | retired with the learned family |

## 4. Agents

| Agent | Proposal | Reason |
|---|---|---|
| `scout`, `builder`, `gap-checker`, `reporter`, `verifier` (new), `explorer` (re-scoped) | keep | L3 role set (docs/standards/COORDINATOR_PROTOCOL.md) |
| `orcaflex-specialist` | keep | domain specialist |
| `cfd-lane-operator` | keep | domain specialist; runs the CFD lanes |
| `code-reviewer` | retire | replaced by `verifier` |
| `quirk-logger` | retire | covered by `scout` + `reporter`; no recorded use |
| `universal/` | retire | README only; describes subdirectories that no longer exist |
| `gsd-*` (33) | retire | GSD phase scaffolding; replaced by the objective flow. Retire with `commands/gsd/` (81), `.claude/get-shit-done/` and the `gsd-*` hooks |

Keep 8, retire 36.

## 5. Hooks

| Event | Hook | Proposal | Reason |
|---|---|---|---|
| PreToolUse | `config-protection-pretooluse.sh` | keep | safety: blocks weakening lint configs and removing safety gates |
| PreToolUse | `skill-content-pretooluse.sh` | keep | safety: scans skill files for injected content before Read |
| PostToolUse | `gsd-read-injection-scanner.js` | keep | safety: prompt-injection scan of Read output (rename out of `gsd-` when GSD goes) |
| PreToolUse | `cross-review-gate.sh` | keep, then modify | becomes tier-aware under L5 (#4002) |
| PreToolUse | `session-governor-check.sh` | keep, then modify | keep the error-loop hard stop; drop the per-session tool-call ceiling (old-model compensation) |
| PostToolUse | `error-loop-tracker.sh` | keep | feeds the error-loop hard stop |
| Pre/PostToolUse | `session-logger.sh` | keep | session telemetry; the only local evidence for usage questions like this one |
| Stop | `consume-signals.sh` | keep | the one Stop-time signal capture kept |
| SessionStart/End | `session-review-page.sh` | keep | owner-facing session review page (#3316) |
| UserPromptSubmit | `ecosystem-data-nudge.sh` | keep | one line pointing to domain data sources; fails open |
| PreToolUse | `plan-approval-gate.sh` | retire | already a no-op since #3943 |
| PreToolUse | `gsd-prompt-guard.js` | retire | guards `.planning/` writes; `.planning/` retires in L2 (#3999) |
| PreToolUse | `gsd-read-guard.js` | retire | compensates non-Claude models skipping read-before-edit |
| PreToolUse | `gsd-workflow-guard.js` | retire | nudges edits into GSD commands |
| PreToolUse | `gsd-validate-commit.sh` | retire | no-op unless `.planning/config.json` opts in |
| PostToolUse | `gsd-context-monitor.js` | retire | context warnings for weaker models; depends on the GSD statusline bridge |
| PostToolUse | `gsd-phase-boundary.sh` | retire | `.planning/` reminder; opt-in no-op |
| PostToolUse | `capture-corrections.sh` | retire | feeds skill-candidate generation, which this prune shrinks |
| PreCompact | `context-budget-monitor.sh` | retire | prints a compaction banner; old-model compensation |
| Stop | `emit-session-quality-signals.sh` | retire | per-WRK counts from the retired work-queue era; duplicates `consume-signals.sh` |
| Stop | `session-review.sh` | retire | duplicate Stop-time capture for the nightly analysis; keep one capture path |
| Stop / SessionStart | `skill-nudge-stop.sh`, `skill-nudge-start.sh` | retire (2) | push for more skills, the opposite of this layer |
| SessionStart | `gsd-check-update.js` | retire | GSD self-update |
| SessionStart | `daily-learning-tip.sh` | retire | noise at session start |
| SessionStart | `gsd-session-state.sh` | retire | prints `.planning/STATE.md` (stale since 2026-04-21) |

Keep 10, retire 16. Deny lists live in `permissions.deny` (owner-only, `config/agents/claude/settings.json`), and secret scanning lives in pre-commit. Neither is a Claude hook, so neither is touched here.

## 6. How the moves run (after approval)

1. Move each `retire-now` skill to `.claude/skills/_archive/<family>/...`. Leave `retire-after-rollout` in place until `AGENTS.md` drops the old chain.
   - `scripts/enforcement/check-skill-index-coherence.py` (a) accepts basenames under archived `_*` families, so curated graph nodes stay green.
   - Regenerate `config/agents/skill-index-full.yaml` with `scripts/ai/build_skill_index.py` so check (c) stays green.
2. Confirm that `_archive/` is not loaded into sessions (Claude skill discovery, and the Codex catalogue on ace-linux-1). If it is, the archive needs a path outside `.claude/skills/` plus a coherence-check update. That is one Codex lane.
3. Agents and commands: move to `.claude/agents/_archive/` and `.claude/commands/_archive/`. Hooks: remove the entries from `.claude/settings.json` (owner-protected file; owner applies, or approves a PR), then archive the scripts.
4. Smoke test: open a fresh session in workspace-hub and digitalmodel and confirm there are no missing-skill or missing-hook errors (#4005 done-when).

## 7. Decision to request (one board card, `decision:ecosystem`)

**Approve the keep list:** skills keep 434 / retire 598 (496 now, 102 after rollout), agents keep 8 / retire 36, hooks keep 10 / retire 16. Also choose the single source for the 60 duplicated marine skills:
- (A) **recommended:** `aceengineer-agents` `ace-marine-dynamics`. The hub copies retire, and the hub keep list drops to 374.
- (B) the hub `engineering/marine-offshore`. The plugin copies retire in `aceengineer-agents`.

Side note for L7 (#4004), not part of this prune: 42 auto-learned notes on personal tax and finance workflows sit in the public hub. They are retired here, but their history is public. Decide whether they also go to the private repo.
