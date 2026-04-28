# Session: Gmail Inbox Manageability Stream — 2026-04-27

> **Machine:** ace-linux-2
> **User:** vamsee.achanta@aceengineer.com
> **Duration:** ~2 hours
> **Outcome:** Inbox manageability moved from open question to measurable system with graduation criterion.

## Why this session existed

User asked: "review gmail features/issues. Let us see what work can be accomplished to get more manageable and sane mailboxes." 50-thread sample of `aceengineer.com` inbox showed ~80% bulk noise (newsletters, marketing, Dependabot), ~5% genuine signal. Five open GitHub issues clustered around the "email-as-queue" workflow ([#2017](https://github.com/vamseeachanta/workspace-hub/issues/2017) parent, plan-approved) but none were shipping inbox-side cleanup.

## Decisions taken

| Decision | Rationale | Captured at |
|---|---|---|
| Filter-first cleanup over per-thread automation | ~76% of volume is filterable; per-thread state machine is for the residue | Memory `feedback_gmail_filter_first_over_per_thread.md` reaffirmed |
| MCP scope-bump > browser automation for Gmail mutation | Consistency (single transport for read+mutation), avoid extension compute credits | New memory: `project_gmail_mcp_scope_bump_decision.md` |
| Close [#2019](https://github.com/vamseeachanta/workspace-hub/issues/2019) as superseded; file [#2528](https://github.com/vamseeachanta/workspace-hub/issues/2528) for residue | ~60% of #2019's stated work was already done by [#2488](https://github.com/vamseeachanta/workspace-hub/issues/2488); fresh smaller-scope issue is cleaner than re-litigating | Issue close comment + new issue body |
| Daily remote routine until graduated | Inbox cleanup is a multi-day effort; daily measurement closes the feedback loop | Routine `trig_01JtTcPPmVfZv6g9K846o7oN` + tracker [#2529](https://github.com/vamseeachanta/workspace-hub/issues/2529) |
| Push the misbundled commit (option α) rather than rewrite | Email artifacts shipped correctly; rewriting during active Hermes contention introduces risk for cosmetic gain | Final commit `7725baa4a` on main |

## Probe evidence (durable)

**MCP Gmail mutation scope reverified 2026-04-27.** `mcp__claude_ai_Gmail__create_label` returned `"Request had insufficient authentication scopes."` Confirms `reference_gmail_mcp_scope.md` is still accurate; documented in that memory. Schema-vs-OAuth ambiguity resolved: schema permissive, server enforces grant.

## Artifacts shipped

### Repo (commit `7725baa4a`)
- `docs/email/2026-04-27-filter-installation-runbook.md` (7,125 bytes) — human-readable rules + preflight + verification checklist
- `docs/email/gmail-filters-2026-04-27.xml` (6,305 bytes) — 6 entries, machine-importable via Gmail Settings → Filters → Import, preflight inline

### GitHub
- [#2527](https://github.com/vamseeachanta/workspace-hub/issues/2527) — user-action gate for OAuth `gmail.modify` scope-bump (unblocks [#2423](https://github.com/vamseeachanta/workspace-hub/issues/2423))
- [#2528](https://github.com/vamseeachanta/workspace-hub/issues/2528) — successor to [#2019](https://github.com/vamseeachanta/workspace-hub/issues/2019), tight T1 scope: retire 6 deprecated email skills + update `gmail-triage` content
- [#2529](https://github.com/vamseeachanta/workspace-hub/issues/2529) — daily inbox manageability tracker (auto-comment thread)
- [#2019](https://github.com/vamseeachanta/workspace-hub/issues/2019) — closed as superseded; stale `wip:ace-linux-1` label removed

### Remote routine
- `daily-inbox-manageability` (`trig_01JtTcPPmVfZv6g9K846o7oN`) — cron `0 12 * * *` UTC = 7:00 AM Central
- First run: ~2026-04-28 07:05 AM CT
- Graduation criteria built into prompt; agent self-recommends disable when met for 3 consecutive days
- MCP: claude.ai Gmail connector (read+compose only; mutation will activate after [#2527](https://github.com/vamseeachanta/workspace-hub/issues/2527))
- Manage: https://claude.ai/code/routines/trig_01JtTcPPmVfZv6g9K846o7oN

### Auto-memory (persists across sessions)
- `reference_gmail_mcp_scope.md` — updated with 2026-04-27 reverification evidence
- `project_gmail_mcp_scope_bump_decision.md` — new, records architecture decision for downstream work

## What user needs to do (after this session)

1. **Install filters** (~3 minutes when browser is open):
   - Gmail → Settings → Inbox → uncheck "Override filters for important"
   - Create new label `gh-dependabot`
   - Settings → Filters and Blocked Addresses → Import filters → upload `docs/email/gmail-filters-2026-04-27.xml`
   - Review entries → check "Apply filter to existing conversations" → Create
2. **Re-authorize claude.ai Gmail MCP with `gmail.modify` scope** when convenient — unblocks [#2423](https://github.com/vamseeachanta/workspace-hub/issues/2423) automation. User-only action; no engineering work needed.
3. **Read tomorrow's daily report** on [#2529](https://github.com/vamseeachanta/workspace-hub/issues/2529) — first datapoint, will show pre-filter baseline if filters not yet installed.
4. **Pick up [#2528](https://github.com/vamseeachanta/workspace-hub/issues/2528)** when ready (T1, ~30-60 min) — retire 6 deprecated email skills.

## Defects / footguns surfaced

### Multi-agent commit serialization (recurring pattern)
Hermes ran a `git add` + `git commit` cycle at 20:51:57 that swept this session's untracked email files into a commit titled "docs(sessions): capture 2026-04-27 photo fix + travel skill build" — completely unrelated workstream. Files landed at correct content; commit message is misleading. `git blame` on `docs/email/gmail-filters-2026-04-27.xml` will surface the wrong context. Per `feedback_multi_agent_commit_serialization.md` this is the Nth occurrence of this race; we did not pause to fix message because Hermes was still active and reset operations during contention are themselves hazardous (`feedback_retry_loop_reset_hazard.md`).

**Mitigation deferred**: when convenient, rewrite the commit message via amend (it's still on `main` head as `7725baa4a`'s message); or accept the misattribution as documentation cost.

### Cross-machine untracked-file rebase conflict
When pulling origin into local, 8 untracked files in `docs/plans/machine-prompts/2026-04-27/execution/` and `scripts/operations/agent-execution/` blocked rebase because origin had committed identical content. Resolved by byte-comparing each (all IDENTICAL), then `rm`-ing locals so rebase could pull cleanly. Pattern worth remembering: "verify identical → rm → retry" for cross-machine duplicate-write races.

## Open threads after this session

- Filters not yet installed (user-action gate)
- OAuth scope-bump not yet performed (user-action gate)
- [#2528](https://github.com/vamseeachanta/workspace-hub/issues/2528) consolidation residue not yet executed
- Daily routine has not yet had its first run; first signal arrives ~2026-04-28 07:05 AM CT
- 14 unstaged tracked-file modifications + 5 untracked paths in working tree — parallel-agent state, not this session's work, left as-is for whichever agent owns them

## Stream graph

```
"review gmail features/issues" (user)
  └─→ scope: 5 open issues, sample inbox (50 threads)
      └─→ probe: MCP mutation scope (FAIL — confirms memory)
          └─→ runbook (Option A) + scope-bump issue #2527 (Option D)
              └─→ Resource Intel for #2019 (Option B)
                  └─→ finding: ~60% already done; close + file #2528 (Option γ)
                      └─→ daily routine + tracker #2529
                          └─→ XML import companion to runbook
                              └─→ commit (race with Hermes) → push → DONE
```

Each step's output became input to the next — that's the compound shape `workspace-hub:compound` skill describes. The runbook informed the routine prompt; the routine surfaced the need for filter coverage; the XML made filter installation 30 seconds instead of 30 minutes.
