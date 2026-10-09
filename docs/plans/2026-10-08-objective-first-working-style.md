# Plan: Move the ecosystem to an objective-first, coordinator + parallel-subagent working style

- Date: 2026-10-08
- Suggested home: `workspace-hub/docs/plans/2026-10-08-objective-first-working-style.md`
- Source of the style: Matt Maher, "The New Way to Work With AI" (YouTube, 7 Oct 2026, 18:42). Built from the video's chapters and description; the transcript itself would not load.
- Evidence base: workspace-hub at `f460708b` (2026-10-08) plus digitalmodel, assetutilities, worldenergydata, raw-to-knowledge-playbook, aceengineer-agents and deckhand-sandbox. Private repos (deckhand, llm-wiki-*) were not read.
- **Gap:** ws014 (acma-ws014 = ace-win-2) is 115 commits behind with 239 uncommitted files (fleet snapshot `docs/reports/fleet-snapshots/2026-10-08.json`). Its newest work is not in this analysis. Phase 0 fixes that first.

---

## 1. The target working style (from the video)

| # | Move | What it means for us |
|---|------|----------------------|
| 1 | **Ask for the outcome, not the steps** | An issue states the result, how we'll know it's done, and the constraints. The agent works out the steps. |
| 2 | **Run subagents in parallel** | Independent pieces go out at once, not one after another. |
| 3 | **Explore several options** | For open questions, ask for 3–5 different directions, then pick. |
| 4 | **Give agents different jobs** | Typical split: *build it*, *check what's missing*, *draft the update*, all running together. |
| 5 | **Keep one coordinating partner** | One main session you keep talking to. It dispatches, holds the big picture, and integrates. |
| 6 | **Steer mid-flight and review what comes back** | Change emphasis while work runs, and review results rather than processes. |

## 2. Where the ecosystem is today

**What already fits (keep it):**
- `docs/standards/PARALLEL_FIRST_EXECUTION.md` already defines the coordinator model (single-lane / parallel-readonly / parallel-worktree, lane contracts, orchestrator owns integration).
- `docs/standards/SUBAGENT_CONTEXT_ISOLATION.md`: the coordinator stays light and verifiers see results, not process.
- `aceengineer-agents` (intake → specialist → hook-enforced verifier) is the cleanest working example of distinct jobs.
- Worktree isolation, TDD culture, `docs/standards/MODEL_RELEASE_UPGRADE_PLAYBOOK.md` for model swaps.
- The deterministic-only rule for the licensed OrcaFlex dispatch chain.

**What works against it:**

| Friction | Evidence |
|----------|----------|
| Step-driven, serial gate chain on every item | Issue → Resource Intel → Plan → Adversarial Review → TDD → Cross-review → Close (`AGENTS.md`, `docs/work-queue-workflow.md`) |
| Review loops instead of review-of-returns | 345 files in `scripts/review/results/`, rounds up to `codex-r4`, 3-provider fan-out |
| Stale model routing | `config/agents/model-registry.yaml` pins `claude-opus-4-8[1m]` / `claude-sonnet-4-6`; `.codex/config.toml` says `gpt-5.5` vs registry `gpt-5.6-sol`; Gemini "retired" but still a default reviewer; 100+ hardcoded old IDs across repos |
| Claude sessions in libraries may see almost no rules | Library `.claude/CLAUDE.md` stubs (7–8 lines) point to a root adapter that no longer exists; the hub retired repo `CLAUDE.md` on 2026-08-01 in favour of native `AGENTS.md` discovery plus the `workspace-soul.md` runtime link (`.claude/rules/coding-style.md`), and that migration is staged per host |
| Too much surface per session | 3,132 skills (incl. gaming/leisure), 166 commands, 39 agents (33 `gsd-*`), 21 hooks, 377-line `settings.json` |
| Work tracked in many places | GitHub issues + `.claude/work-queue/` + `.planning/` (STATE.md stuck at 2026-04-21) + 676 `docs/plans/` + loose `issue-*-impl.diff` / `draft_*` / `gmail_*` at repo root |
| Shared lock lives in a private repo | `../llm-wiki/scripts/coordination/claim.py` must be reachable or shared work blocks |
| ws014 drift | 115 behind, 239 dirty, unreachable 09-30/10-04/10-05; 16 GB RAM with ~2.2 GB free; path disagreement (`D:\workspace-hub` vs `C:\ws\workspace-hub`) |

## 3. What the latest models change

- **Briefs can be shorter and outcome-shaped.** Current frontier models (Opus 5.5, Sonnet 5.5, Haiku 5.5; Fable 5.1 where access exists) plan multi-step work well on their own. Long prescriptive instructions now cost more than they help.
- **One strong independent verifier beats four review rounds.** Keep adversarial review for high-risk work; for routine work a single fresh-context verifier is enough.
- **Coordinator + cheap workers.** Use the strongest model as coordinator and for hard reasoning; Sonnet/Haiku-tier for search, recon, drafting, bulk checks.
- **Less scaffolding.** GSD-style phase files and 3,000-skill libraries were compensating for weaker models. Keep only skills that encode *your* domain knowledge (OrcaFlex, API 2RD, DNV, fatigue, FDAS) or *your* infrastructure.

## 4. Transition plan

Each phase is itself written as an objective, so it can be run in the new style.

### Phase 0 — Land ws014 and freeze (day 1)

**Outcome:** GitHub reflects all real work; nothing new piles onto the old process during the switch.
- On each host: run `scripts/readiness/reconcile-ecosystem.sh` (Windows: `scripts\windows\reconcile-ecosystem.ps1`) in report mode, then `--apply` for the AUTO-SAFE subset (ff-only pulls, guard-gated cleanup). Preserve dirty work on a **local** branch `wip/<host>-2026-10-08` instead of stashing. Don't discard anything.
- workspace-hub is **public**: push a WIP branch only after a secrets/client-data review; otherwise move that content to a private repo.
- Triage that branch: real work → issues/PRs; scratch → `_archive/`.
- Move root clutter (`issue-*-impl.diff`, `*-review.md`, `draft_*`, `final_*`, `sendready_*`, `gmail_*`, `issue2_*`, `nohup.out`, empty `Defines`/`Planning`) to `_archive/2026-10-root-cleanup/`. Personal email drafts belong in a private repo, not the public hub.
- Freeze: no new skills, hooks, or standards until Phase 4.

**Done when:** fleet snapshot shows every reachable host (ace-linux-1, ace-linux-2, acma-ws014, acma-hou-rds02) 0 behind / ~0 dirty, and the hub root holds only project files.

### Phase 1 — Model refresh and instruction plumbing (week 1)

**Outcome:** every session, in every repo, loads the right rules and the current models.
- Follow `MODEL_RELEASE_UPGRADE_PLAYBOOK.md` (Primary Model Swap checklist) to update `config/agents/model-registry.yaml`:
  - coordinator / hard reasoning: `claude-opus-5-5` (or `claude-fable-5-1` where your account has it)
  - balanced worker: `claude-sonnet-5-5`
  - fast / bulk / distill: `claude-haiku-5-5` (update `distill-provider-sessions.py`, which runs `--model haiku`)
  - Prefer aliases (`opus`, `sonnet`, `haiku`) in agent frontmatter so the next release needs no edits.
- Fix Codex drift: one source for the Codex model (`registry` reads live `~/.codex/config.toml`, or vice versa).
- Remove Gemini from default review routing (`config/ai-tools/provider-routing-policy.yaml`, `AI_REVIEW_ROUTING_POLICY.md`, `GEMINI.md`) to match #3573.
- Finish the staged Claude runtime migration rather than adding files: run `scripts/agents/claude_runtime_state.py` on each host and move every host to NATIVE_VERIFIED (`~/.claude/rules/workspace-soul.md` symlink, `AGENTS.md` discovery verified). Then remove the dangling "root CLAUDE.md (adapter)" pointer from the library stubs.
  - **Correction (2026-10-08):** the first version of this plan said to add a root `CLAUDE.md`. That contradicts the 2026-08-01 retirement in `.claude/rules/coding-style.md` and is withdrawn; the migration above replaces it.
- Replace hardcoded `/mnt/github/workspace-hub` and `/d/workspace-hub` in library hook commands with an env var (e.g. `$WORKSPACE_HUB`), set per machine in `registry.yaml`.
- Sweep old model IDs (`claude-sonnet-4.5`, `gpt-4`, `gpt-4.1`, `o3`) — script-first, agents for edge cases.

**Done when:** `claude_runtime_state.py` reports NATIVE_VERIFIED on every reachable host, `check-soul-deployment-drift.sh` exits 0, and a fresh `claude` session opened in digitalmodel can state the hub rules; `grep` finds no pinned 4.x IDs outside `_archive/` and audit history.

### Phase 2 — Introduce the objective brief and coordinator protocol (week 1–2)

**Outcome:** a new issue can be written as an objective and run by one coordinator with parallel jobs.

1. **Objective issue template** — `.github/ISSUE_TEMPLATE/objective.md`:
   - *Outcome* (one or two sentences)
   - *Done when* (checkable)
   - *Constraints / must not* (codes, licence rules, client data)
   - *Out of scope*
   - *Return format* (PR, report, table, wiki page)
   - *Risk tier* (A/B/C — see Phase 4)
2. **Five standard job roles** (agents in `.claude/agents/`, replacing most of the 33 `gsd-*`):

   | Role | Job | Default model | Writes? |
   |------|-----|---------------|---------|
   | `scout` | find code, data, prior work, risks | haiku/sonnet | no |
   | `builder` | implement in its own worktree, TDD | sonnet (opus for hard engineering) | yes, owned paths only |
   | `gap-checker` | what's missing / wrong vs. "Done when" | sonnet, fresh context | no |
   | `explorer` | 3–5 distinct options for open questions | sonnet | no |
   | `reporter` | draft the issue comment / client update / wiki page | sonnet/haiku | drafts only |
   | `verifier` | independent check of the returned result | opus, fresh context | no |

3. **Coordinator command** — `/objective <issue#>`: reads the brief, picks a mode per `PARALLEL_FIRST_EXECUTION.md`, writes lane contracts, launches lanes in one batch, then stays available for steering. Status uses the standard's reporting format.
4. **Steering:** you talk only to the coordinator. "Shift emphasis to X", "drop lane Y", "show me what's back" are normal mid-run instructions. Lanes report results, not narration.
5. Rewrite `AGENTS.md` around this flow: *Objective → Coordinator classifies → Parallel jobs → Verify returns → Integrate → Close*. Keep TDD, hard-stops and authorization lines as they are.

**Done when:** the template, five role agents and `/objective` exist, and a dry run on a closed issue produces lane contracts.

### Phase 3 — Pilot on three real objectives (week 2–3)

**Outcome:** evidence that the new style is faster without lowering quality.

| Pilot | Repo | Why |
|-------|------|-----|
| An OrcaFlex post-processing feature (Tier A) | digitalmodel | Tests the style on your hardest engineering work |
| Document ingestion into a client wiki (Tier B/C) | llm-wiki-* (run from ws014) | Matches ws014's current admin/document role |
| Fleet health dashboard objective (Tier B) | workspace-hub | Explore 3 designs, build one, gap-check, draft the update |

Track per pilot against a comparable old-style issue: wall-clock to close, review rounds, rework commits, tokens, and your own review time. Write a one-page result per pilot.

**Done when:** all three closed; decision recorded on what to keep.

### Phase 4 — Right-size the gates by risk (week 3–4)

**Outcome:** heavy process only where it protects something.

| Tier | Examples | Gates |
|------|----------|-------|
| **A** | Licensed solver dispatch, code-check calcs (API 2RD, DNV-OS-F201/F101), client deliverables, fatigue results | TDD + independent `verifier` + Codex second opinion + your sign-off. Deterministic-only dispatch unchanged. |
| **B** | Library code, tooling, scripts | TDD + one independent `verifier`. Max 2 fix rounds, then escalate to you. |
| **C** | Docs, wiki pages, admin, drafts | `gap-checker` optional; you review the return. |

- Plan step becomes "proportionate": Tier C needs only the objective brief.
- Make `cross-review-gate.sh` tier-aware instead of blocking every PR.
- Decide what replaces `claim.py` when llm-wiki is unreachable (e.g. a lock ref in the hub itself), so coordination isn't a single point of failure.

### Phase 5 — Prune and consolidate (month 2)

**Outcome:** a session starts with only what it needs.
- Skills: keep domain (engineering/marine-offshore, OrcaFlex, standards, fatigue) and infrastructure skills; archive off-topic categories (gaming, leisure, apple, etc.). Target a few hundred, not 3,132. Merge the duplicated knowledge skills between raw-to-knowledge-playbook and aceengineer-agents into one source.
- Hooks: audit the 21 wired hooks; keep safety (deny lists, licence rules, secret scanning) and drop ones that only compensated for older models (e.g. tool-call ceilings set for weaker runs).
- One repo manifest (merge `repos.conf`, `repo-map.yaml`, registry lists, `domain_coverage.py`); add `aceengineer-agents`.
- One tracking system: GitHub issues. Retire `.claude/work-queue/`; archive stale `.planning/`.
- Overnight `claude -p` pipelines become an objective queue: each night's job is an objective brief; the morning output is returns to review.
- Remove leftovers: `.hive-mind/`, `.swarm/`, `.SLASH_COMMAND_ECOSYSTEM/`, digitalmodel's `sub-agents/` and `propagation-rules.yaml`.

## 5. ws014-specific actions

- Treat ws014 as an **admin/document coordinator host**, not a lane farm: 16 GB RAM (~2.2 GB free) supports at most 2 local parallel lanes. Send heavier lanes to the Linux boxes or cloud sessions.
- Finish #3545 (Claude Remote Control under a dedicated Windows profile) so you can steer the coordinator from your phone while travelling.
- Settle one checkout path and update `registry.yaml`, `machine-inventory.md` (listed twice) and the `ssh: null` field.
- Keep the licensed lane deterministic; agents only write the scripts it runs (current rule — unchanged).
- Investigate the account fingerprint mismatch on ace-win-2 (`docs/reports/ai-account-usage.md` L33–34) before routing paid work through it.

## 6. What does not change

- TDD for code and calculations.
- Hard-stop and authorization policy (`HARD-STOP-POLICY.md`, `SHARED_SOUL.md`).
- No LLM in the licensed dispatch chain; one Orcina Flex seat rules.
- Secrets and client-data handling (`agent-data-handling-contract.md`).
- Coordinator alone owns integration, push and issue closeout.

## 7. Success measures (review at end of month 2)

- Median time from objective to closed issue down ≥40% on Tier B/C.
- Review rounds per PR ≤2 (today up to 4+).
- Zero pinned stale model IDs outside archives.
- ws014 never more than 10 commits behind or 20 dirty files in fleet snapshots.
- Your hands-on time per objective: brief + steering + final review only.

## 8. First three objectives to file today

1. **Phase 0:** "GitHub reflects all ws014 work and the hub root is clean." (Tier C)
2. **Phase 1:** "Every session in every repo loads hub rules and current models." (Tier B)
3. **Phase 2:** "Objective template, five role agents and `/objective` exist and dry-run on a closed issue." (Tier B)
