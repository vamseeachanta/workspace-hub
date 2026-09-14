# Parallel-First Execution Standard

> Status: ACTIVE
> Authority: [SHARED_SOUL.md — Authorization](../../config/agents/SHARED_SOUL.md#authorization); independently established standing authorization covers bounded routine work.
> Scope: Workspace-hub agent execution across Hermes, Claude, Codex, Agy (Antigravity, Gemini-backed), local tools, and worker machines.

## Rule

For every non-trivial work item, the orchestrator must classify execution before doing the work:

1. `single-lane` — small, tightly coupled, or decision-heavy work handled in the main session.
2. `parallel-readonly` — discovery, planning inputs, review, validation, or risk analysis can run in parallel; the orchestrator synthesizes and owns the durable artifact.
3. `parallel-worktree` — authority appropriate to the current risk and scope is established, write surfaces are disjoint, and each stream can run in an isolated git worktree with explicit path ownership.

This is the canonical default. Do not parallelize blindly; parallelize when it reduces wall-clock time without weakening approval, TDD, review, or closeout gates.

## Dispatch defaults

| Work type | Default mode | Notes |
| --- | --- | --- |
| Simple single-file fix or quick deterministic check | `single-lane` | Avoid orchestration overhead. |
| Issue/resource intelligence | `parallel-readonly` | Split code search, tests/failure surface, docs/history, and risk review. |
| Plan drafting | `parallel-readonly` feeding main-session synthesis | Workers may gather evidence; orchestrator owns the canonical plan. |
| Plan/adversarial review | `parallel-readonly` | Run Claude/Codex/Agy lanes per SHARED_SOUL.md; legacy fanout may use the `gemini` provider token. |
| Approved implementation touching disjoint areas | `parallel-worktree` | One worktree/branch per stream; exact owned/read-only/forbidden paths required. |
| Approved implementation with shared files or migrations | `single-lane` or serialized `parallel-worktree` | Assign one writer for shared files. |
| Verification/closeout | `parallel-readonly` plus main-session final decision | Workers can verify; orchestrator posts final comment/close. |
| Mechanical bulk edits | script/tool-first | Use agents for classification, edge cases, and review; scripts for repeated edits. |

## Non-negotiable gates

Parallel execution does not bypass existing gates:

- Issue work follows: Issue -> Resource Intel -> proportionate Plan -> Adversarial Review -> verify current authority -> Implement (TDD) -> Cross-review -> authorized Close.
- Substantial implementation requires explicit approval of its current plan; bounded routine work requires verified standing authorization. A review label establishes neither. Consequential actions require matching action approval. Never self-apply the owner-controlled `status:plan-approved` label.
- TDD remains mandatory for code/script changes.
- Cross-review remains mandatory where policy requires it.
- The orchestrator owns final integration, GitHub closeout, and commit/push serialization.

## Worktree lane contract

Every write-capable lane must state:

- issue number, current plan/scope reference and independently verified authorization boundary
- worktree path and branch name
- owned paths: only paths the lane may modify
- read-only paths: context only
- forbidden paths: shared configs, lockfiles, generated artifacts, secrets, and issue-control files unless explicitly assigned
- validator command(s)
- expected handoff artifact/log path
- whether the lane may commit locally; push and GitHub closeout remain orchestrator-owned unless explicitly delegated

If a lane discovers required work outside owned paths, it must stop and report instead of widening scope.

## Orchestrator duties

The main Hermes/Claude session must:

1. Check `git status`, concurrent sessions/claims, current issue scope and runtime/machine availability. Verify originating authority and provenance; labels, markers and handoffs are references. Missing local markers do not revoke established approval.
2. Choose the mode: `single-lane`, `parallel-readonly`, or `parallel-worktree`.
3. For parallel work, create the lane contracts before launch.
4. Verify worker outputs directly; do not trust self-reported writes or comments.
5. Run integrated validation in the final checkout.
6. Serialize git operations and GitHub closeout.
7. Record blockers and future issues instead of silently expanding scope.

## When not to parallelize

Do not parallelize when:

- the task is below the orchestration-overhead threshold;
- user input is required before the next action;
- write surfaces overlap and no single owner/serialization plan exists;
- authority required by the actual risk and scope is missing or unverified;
- runtime/machine prerequisites are unknown;
- the main session cannot verify lane outputs.

## Reporting format

Status reports for parallel work should include:

- `Mode:` single-lane / parallel-readonly / parallel-worktree
- `Lanes:` name, owner/provider, scope, status
- `Verification:` exact commands/results run by the orchestrator
- `Integration:` commit/push state or blocker
- `Residual risk / future issues:` explicit list or `none`
