# Coordinator Protocol

> Status: ACTIVE (rewire L3, workspace-hub#4000; RFC #3997, epic #3993)
> Authority: [SHARED_SOUL.md](../../config/agents/SHARED_SOUL.md) and [HARD-STOP-POLICY.md](HARD-STOP-POLICY.md). Nothing here changes TDD, hard-stop or authorization rules.
> Builds on: [PARALLEL_FIRST_EXECUTION.md](PARALLEL_FIRST_EXECUTION.md) (modes, lane contracts, reporting format) and [SUBAGENT_CONTEXT_ISOLATION.md](SUBAGENT_CONTEXT_ISOLATION.md).

The objective (one GitHub issue) is the unit of work. One coordinator session
reads the label queue, dispatches role agents and Codex lanes, verifies what
comes back, integrates, and writes only real decisions to the owner.

## 1. Inputs

| Input | Source | Owner of the source |
|---|---|---|
| Objective brief (Outcome, Done when, Constraints / must not, Out of scope, Return format, Risk tier) | issue written from the objective template | L1, #3998 / #3989 (`.github/ISSUE_TEMPLATE/objective.*`, `/objective <issue#>`) |
| Queue state | labels `lane:{claude,codex}` x `dispatch:{ready,active,blocked,done}`, plus `decision:*` when the owner is needed | L2, #3999 |
| Where work may run | [config/agents/host-role-routing.yaml](../../config/agents/host-role-routing.yaml) | this standard |
| Licensed solver routing | `.claude/memory/kanban/routing-rules.yaml` (deterministic, unchanged) | dispatch |

The `/objective` command and the template are built in L1; this standard
defines what the coordinator does once a brief exists.

## 2. Roles

One coordinator plus six role agents in `.claude/agents/`. Frontmatter uses
model aliases (`opus`, `sonnet`, `haiku`), never pinned IDs.

| Role | Job | Default model | Tools | Writes? |
|---|---|---|---|---|
| coordinator | read queue, classify mode, write lane contracts, dispatch, verify, integrate, label, close | strongest available (`opus`) | all | integration, push, labels, closeout (only it) |
| `scout` | find code, data, prior work, risks | `haiku` (raise to `sonnet`) | Read, Glob, Grep, Bash (read-only use) | no |
| `builder` | implement one lane in its own worktree, TDD | `sonnet` (raise to `opus` for hard engineering) | Read, Write, Edit, Bash, Glob, Grep; `isolation: worktree` | owned paths only; local commits if the contract allows |
| `gap-checker` | what is missing or wrong vs. "Done when" | `sonnet`, fresh context | Read, Glob, Grep, Bash (read-only use) | no |
| `explorer` | 3-5 distinct options for an open question | `sonnet` | Read, Glob, Grep, WebSearch, WebFetch | no |
| `reporter` | draft the issue comment, PR body, update or wiki page | `sonnet` (`haiku` for short notes) | Read, Glob, Grep, Write (draft path only) | drafts only |
| `verifier` | independent check of the returned result | `opus`, fresh context | Read, Glob, Grep, Bash (tests, read-only use) | no |
| Codex lane | bounded implementation, tests, discovery | Codex default model | Codex runner on Linux | its worktree and branch only |

Domain specialists that stay alongside the roles: `orcaflex-specialist`,
`cfd-lane-operator` (see the L8 keep list,
[2026-10-09-rewire-l8-prune-keep-list.md](../plans/2026-10-09-rewire-l8-prune-keep-list.md)).

## 3. The loop

For each objective the coordinator:

1. **Pick.** Take open issues with `dispatch:ready`, ordered by priority, then age. Skip any with a `decision:*` label.
2. **Classify.** Choose `single-lane`, `parallel-readonly` or `parallel-worktree` per PARALLEL_FIRST_EXECUTION.md, and the risk tier from the brief.
3. **Route.** For each lane, choose provider and host from `host-role-routing.yaml`:
   `lane:codex` goes to the Codex lane runner on Linux; `lane:claude` runs as role subagents on the coordinator host, or as worktree builder lanes on a Linux host when the coordinator host is at its cap.
4. **Contract.** Write a lane contract per write-capable lane (issue, worktree path, branch, owned / read-only / forbidden paths, validator commands, return path). Post the contracts as one issue comment.
5. **Start.** Flip `dispatch:ready -> dispatch:active`. Launch all independent lanes in one batch.
6. **Steer.** The owner talks only to the coordinator ("shift emphasis to X", "drop lane Y", "show what's back"). Lanes return results, not narration.
7. **Check returns.** `gap-checker` against Done when; `verifier` for Tier A/B (Tier C: owner reads the return). Max 2 fix rounds, then a `decision:*` card.
8. **Integrate.** Coordinator alone commits the integration, pushes, opens or updates the PR, and runs the validators in the final checkout. Cross-provider review follows L5 (#4002): Claude-authored PRs get a Codex review lane, Codex-authored PRs get a Claude `verifier`.
9. **Close out.** Comment the result on the issue in the PARALLEL_FIRST_EXECUTION reporting format, flip `dispatch:active -> dispatch:done` (or `dispatch:blocked` with the blocker), and close when Done when is met and merge policy allows.

## 4. Host routing (summary)

The table lives in [config/agents/host-role-routing.yaml](../../config/agents/host-role-routing.yaml).

| Host (registry id) | Role | AI lanes | Local lane cap |
|---|---|---|---|
| ace-win-2 (ws014) | coordinator / admin and documents | claude, codex | 2 |
| dev-primary (ace-linux-1) | Codex lanes, heavy builders, coordinator resume | codex, claude | 6 |
| dev-secondary (ace-linux-2) | second lane host | codex, claude | 4 |
| ace-win-1 | licensed tool runner, separate AI accounts | none from the coordinator | 0 |
| gpu-claw | deterministic sim / CFD runner | none | 0 |
| cloud sessions | overflow, no client data, no licensed work | claude | as quota allows |

Rules:

- **ws014 cap.** At most 2 concurrent local AI lanes on ace-win-2. A third is refused and routed to a Linux host.
- **Licensed hosts are tool runners.** They run deterministic scripts through the existing licensed dispatch path. No model sits in the licensed chain, and AI lanes never drive a licensed tool.
- **Separate accounts.** A host signed in to other AI accounts (ace-win-1) is not a lane target. Work that needs an AI session there goes through the owner, or is written as an objective that the host's own session picks up. Results come back as issue comments or PRs. The coordinator never drives another account's session.
- **Client data** stays on the hosts and repos the client-data contract allows; it never goes to cloud overflow.

## 5. Stall rule

An issue with `dispatch:active` for more than 48 h and no issue comment raises a
`decision:*` board card (L4, #4001). State lives in issues and labels, not in a
session, so any `resume_on` host can take over a stalled coordinator.

## 6. Out of scope here

- The objective template and `/objective` command (L1, #3998 / #3989).
- Label migration and retiring `.claude/work-queue/` and `.planning/` (L2, #3999).
- Board generation and write-back (L4, #4001); tier-aware gates and auto-merge (L5, #4002).
- The dispatch-loop script itself; this standard is its specification.
