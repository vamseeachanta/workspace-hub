> Git-tracked snapshot from Claude auto-memory. Captured: 2026-05-22
> Source: /home/vamsee/.claude/projects/-mnt-local-analysis-workspace-hub/memory/feedback_subagent_write_phantom.md

---
name: Subagent Write claim phantom files
description: Subagent Write tool calls can return success while the file does not land on disk — main session must independently ls every claimed write before believing it
type: feedback
originSessionId: f0b82690-86aa-4409-8f19-0896e0cba0cb
---
When a subagent claims to have written a file with the Write tool, the main session MUST independently verify the file exists on disk via `ls -la` before believing the claim or referencing the file in subsequent turns.

**Why:** On 2026-05-03, two subagents in different waves (marine_ops triage initial draft + solvers/orcaflex triage initial draft) reported successful Write tool calls. Their transcripts showed Write returning without error and the agents' final summaries plausibly described the artifacts they had "produced." Independent verification at recovery time found neither file existed at the claimed path. The failure mode is silent — the agent's success summary reads as truth, no error surfaces, and downstream turns happily reference the phantom path. The cascade in this session was caught only when an attempted commit found `git status --short docs/plans/2026-05-03-*.md` returned nothing — that contradiction is what surfaced the phantom. Recovery cost was ~2 turns to re-spawn the agents with a proof-of-write protocol and re-verify.

The cost of trusting a phantom-Write report compounds across turns: main-session synthesis assumes the file exists, issue bodies cite the path, plan citations link to it, downstream subagent prompts pass the path as input. Each turn that elapses before the contradiction surfaces multiplies the recovery cost.

**How to apply:**

- When dispatching any plan-creating, doc-writing, or memory-writing subagent: the prompt MUST require the agent to run `ls -la <path>; wc -l <path>; wc -c <path>; head -3 <path>` after the final Write and INCLUDE the raw output in its report. No verification block = treat the report as unverified.
- When the main session receives a subagent report claiming a Write success: independently re-run `ls -la <path>` before commit, before referencing the file in later turns, and before dispatching downstream agents that consume the file. The agent's own verification is necessary but not sufficient — the main session re-check is load-bearing.
- If `ls` shows file size 0 or path-not-found, the Write failed silently — re-dispatch the agent with explicit "your previous write did not land; here is the verification command output proving the file is missing; write again and include the verification block in your report."
- Issue bodies, plan citations, and downstream subagent prompts must NOT reference a file path until that path has been ls-verified by the main session.

**Don't apply when:** the subagent's deliverable is a GitHub issue (verifiable via `gh issue view`), a comment (`gh issue comment` returns the URL on success), or a label change (`gh issue view --jq .labels`). For GitHub state, the API itself is the verification surface — but the same trust-but-verify principle applies: independently re-query via `gh` before treating the side effect as real.

**Cross-references:**

- `feedback_attestation_enables_contradiction_detection.md` — the broader principle that contradiction-detection beats charitable reading; phantom Writes are a special case where the contradiction is plan-prose-vs-disk-state.
- `feedback_check_parallel_work.md` — verification before action; same family of "look before you leap" rules.
- CLAUDE.md "Trust but verify" clause — this entry is a concrete operationalization for the subagent Write surface.
