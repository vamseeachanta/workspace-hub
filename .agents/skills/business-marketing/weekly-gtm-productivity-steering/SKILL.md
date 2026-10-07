---
name: weekly-gtm-productivity-steering
description: "Turn interactive weekly GTM priorities into agent-executable packets and run productivity-flow reviews that reduce owner orchestration time."
version: 1.0.0
category: business-marketing
tags: [gtm, weekly-targets, productivity, orchestration, business-brain]
---

# Weekly GTM Productivity Steering

## When to Use

Use this skill when the user wants to:
- establish or update this week's GTM targets interactively;
- convert a weekly business target into GitHub issues, agent prompts, or artifacts;
- review the owner's work pattern and suggest productivity hacks;
- update Business Brain / repo-backed memory with weekly GTM priorities;
- shift routine orchestration from user-managed gates toward evidence-threshold agent self-cycling.

Class of task: interactive business/GTM steering notes become durable repo-backed context plus bounded agent work packets and productivity improvements.

## Operating Principles

1. The owner should provide direction, ideas, GTM priorities, and strategic approvals.
2. Agents should self-cycle research, issue decomposition, plan drafting, artifact creation, review, verification, and outbound tracking where gates allow.
3. Weekly targets must be concrete enough to produce external-facing artifacts, not just internal repo work.
4. Productivity-hack reviews should reduce owner orchestration time and increase GTM/artifact flow.
5. Do not relax hard gates by assertion; track evidence thresholds over time.

## Workflow

0. **Run Business Brain reverse prompting when the next work is not already obvious**
   - Read `docs/BUSINESS_BRAIN.md`, live GitHub issue state, recent handoffs/session summaries, and current repo routing surfaces.
   - Ask for ranked, executable work packets rather than generic ideas.
   - Optimize explicitly for: client conversion, owner-orchestration reduction, useful provider throughput, hard-gate preservation, and reuse of existing issues.
   - Require every recommendation to name: GitHub issue, owning repo, artifact, agent/provider lane, verification evidence, and whether user approval is needed.
   - Treat the output as an intake mechanism for issue updates, plan drafts, prompt packs, cron jobs, or skills — not as free-form brainstorming.

1. **Capture the weekly target**
   - Restate the target in one sentence.
   - Identify the desired external artifact(s): brochure, capability chart, email packet, demo report, outreach list, landing page, etc.
   - Identify the target audience/persona.

2. **Decompose into agent packets**
   - Research/list hygiene packet.
   - Artifact/collateral creation packet.
   - Evidence/legal/provenance review packet.
   - Outbound/send tracking packet.
   - Follow-up/GitHub issue creation packet.

3. **Run productivity-flow review**
   - Audit recent sessions, GitHub throughput, GTM artifacts, context handoffs, repeated friction points, provider/tool bottlenecks, and user-interruption points.
   - Propose practical changes that reduce owner orchestration time.
   - Convert accepted changes into repo issues or prompt packs.

4. **Update durable context**
   - Patch `docs/BUSINESS_BRAIN.md` for canonical business context.
   - Patch `.claude/memory/templates/agents-template.md` when all agents need the fact.
   - Use Hermes memory only for durable user preferences, not temporary weekly task progress.

5. **Verify and commit context changes**
   - Run legal sanity when public-facing artifacts, raw data, client/prospect lists, or repo docs are touched:
     ```bash
     bash scripts/legal/legal-sanity-scan.sh --diff-only
     ```
   - Commit only intended context files.
   - Rebase/push if remote moved.

## GitHub Issue + Overnight Lane Execution Pattern

Session-specific references:
- `references/business-brain-48h-gtm-reverse-prompt-packet.md` — proven Business Brain → parent issue → child-lane prompt pack → bounded delegation → GitHub update pattern from the vessel-contractor GTM wave.
- `references/owner-default-approval-followthrough.md` — how to execute when the owner approves recommended GTM defaults: patch repo artifacts, create follow-up issues, reconcile labels, verify, commit, and post rollup comments.
- `references/gtm-blocker-removal-continuation.md` — how to continue a GTM stream after a blocker-removal issue closes: sync main safely, promote the upstream artifact gate, then harden downstream brochure/send work without sending outreach.

When a weekly GTM target is concrete enough to execute, convert it into a small linked issue set rather than one broad umbrella issue:

1. Search existing GitHub issues first and reuse/link umbrellas instead of duplicating them.
2. Create bounded child issues for the major artifact streams, typically:
   - research/list hygiene;
   - capability charts or proof artifacts;
   - brochure/collateral + send-tracker boundary;
   - productivity-flow review.
3. Comment on parent/related issues with the child issue links so the weekly target is traceable.
4. Create a repo-owned prompt pack under `docs/plans/overnight-prompts/<date>-weekly-gtm-targets/` with one prompt per child issue and a `results/` directory.
5. Each prompt must preserve gates: no outreach/contacting people, no private contact details in public repo files, no `status:plan-approved` mutation, and only `status:plan-review` when canonical plan + adversarial review evidence are complete.
6. Launch bounded planning/research/productivity lanes in named tmux sessions and log to `logs/night-runs/`.
7. Monitor by tmux/process liveness and expected `results/issue-<N>-summary.md` artifacts; zero-byte Claude logs are inconclusive while processes are alive.
8. Commit the prompt pack after legal sanity scan, and use a scheduled monitor for long-running lanes.

## Reverse Prompt Templates

Use these when the user asks “what should we do next?” or when Business Brain context should drive autonomous work discovery.

### Daily dispatch reverse prompt

```text
Read Business Brain, open GitHub issues, recent session handoffs, and current repo state.

What are the 3–5 highest-value things agents should do today?

Constraints:
- Prefer work tied to #2016 client conversion.
- Prefer external-facing artifacts over internal-only cleanup.
- Do not create duplicate issues.
- Do not bypass plan/review/approval gates.
- Use existing plan-approved issues where possible.
- Spend provider capacity deliberately; do not leave useful Claude/Codex/Gemini capacity idle.

Return a table:
1. Action
2. GitHub issue
3. Repo
4. Agent/provider
5. Expected artifact
6. Verification
7. Blocker / owner decision needed
```

### 48-hour GTM execution packet reverse prompt

```text
Using Business Brain, #2016, and the current open GTM issues, design the next 48-hour agent execution packet.

Prioritize getting client-facing GTM materials ready.

Return:
1. exact task packets,
2. which agent/provider should run each,
3. required source files/repos,
4. expected artifact paths,
5. verification steps,
6. what needs user approval before sending anything externally.
```

### Owner-orchestration reduction reverse prompt

```text
Review the last week of work: GitHub issue movement, agent handoffs, review churn, repeated prompts, stalled approvals, and manual owner interventions.

Find where the owner spent avoidable time.

Return:
1. Top owner-interruption points.
2. Which ones agents can self-cycle next time.
3. Which need a cron job.
4. Which need a reusable skill.
5. Which need better GitHub labels/statuses.
6. Which hard gates can become evidence-threshold gates later, and what evidence is needed.
7. Three changes to reduce owner orchestration time this week.
```

## Example Weekly Target Shape

For a target like: "this week, vessel capability charts sent to all vessel contractors":

| Packet | Output |
|---|---|
| Contractor research | researched vessel-contractor list with source/provenance |
| Capability charts | evidence-backed vessel capability charts |
| Brochure | concise, client-ready brochure tied to proof paths |
| Legal/evidence check | public/private separation, no unsupported claims |
| Outbound tracking | send list, status, follow-up dates, response notes |

## Productivity-Hack Review Checklist

- Where did the owner spend avoidable time making routing/approval decisions?
- Which repeated prompts should become reusable prompt packs or cron lanes?
- Which hard gates are causing slowdown because evidence thresholds are missing?
- Which provider capacity is underused relative to useful work available?
- Which GitHub issue statuses/labels are stale or blocking self-cycling?
- Which artifacts are missing proof paths, legal scans, or acceptance evidence?
- What can agents do without asking next time?

## Pitfalls

- Capturing weekly goals only in chat and not repo-backed context.
- Creating broad goals without artifact/send-list acceptance criteria.
- Letting productivity reviews become generic advice instead of issue/prompt changes.
- Relaxing user approval gates before metrics prove agent rigor is safe.
- Mixing prospect/client-sensitive data into public-facing artifacts without legal/provenance review.
- Treating `UNAVAILABLE`, empty, wrapper-failed, or retrieval-failed Codex/Gemini artifacts as satisfying a live non-Claude review gate; they are blocker evidence only.
- Jumping to brochure/outbound execution before upstream target-matrix and capability-chart plan/evidence hygiene has cleared review-readiness.
- After the owner approves defaults, re-asking instead of executing the approved defaults; apply them repo-first, create implied follow-up issues, reconcile labels, verify, commit/push, and comment.
- Partially patching long Markdown table/index rows without rereading them; always re-read patched rows and run count/string checks because malformed rows can silently preserve stale prose.
