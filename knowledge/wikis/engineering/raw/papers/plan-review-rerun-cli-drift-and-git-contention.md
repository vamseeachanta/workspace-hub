# Archived Skill: `plan-review-rerun-cli-drift-and-git-contention`

Original path: `/home/vamsee/.hermes/skills/workspace-hub-learned/plan-review-rerun-cli-drift-and-git-contention`
Archived into: `/home/vamsee/.hermes/skills/.archive/umbrella-2026-04-29/workspace-hub-learned/plan-review-rerun-cli-drift-and-git-contention`
Consolidation date: 2026-04-29

---

---
name: plan-review-rerun-cli-drift-and-git-contention
description: Recover iterative plan-review work when provider CLI wrappers drift, fresh reviews expose stale governance text, and active git pre-push processes make committing unsafe.
version: 1.0.0
category: workspace-hub-learned
tags: [planning, adversarial-review, codex, gemini, governance, git-contention]
---

# Plan Review Rerun: CLI Drift + Governance Hygiene + Git Contention

Use this when hardening a `status:plan-review` issue through repeated adversarial review waves, especially when provider dispatch partially fails or another agent/process is actively using git.

## Trigger conditions

- A plan has old review waves (`r2`, `r3`, etc.) and new review findings against newer text.
- Provider fanout returns `UNAVAILABLE` due CLI syntax drift, not a substantive review.
- A fresh review identifies stale plan metadata, stale issue-status claims, or stale approval-artifact wording.
- `git add`, `git status`, `git commit`, or `git push` are blocked by active pre-push/git processes or `.git/index.lock`.

## Workflow

1. Revalidate live state before editing.
   - `gh issue view <issue> --json labels,state,comments,url`
   - Read the plan header, `## Adversarial Review Summary`, and `docs/plans/README.md` row.
   - Check local approval marker only after live labels: `.planning/plan-approved/<issue>.md`.

2. Treat provider wrapper failure as a tool problem, not review signal.
   - Current Codex CLI may reject `codex exec --no-interactive` with rc=2.
   - If `plan-review-fanout.sh` emits `UNAVAILABLE (codex CLI failed ... unexpected argument '--no-interactive')`, rerun Codex without `--no-interactive` or record Codex as unavailable.
   - Do not count an UNAVAILABLE artifact as approval.

3. Patch the actual plan blockers from substantive providers.
   - Example: if Gemini says tests install a dependency directly and bypass `pyproject.toml`, change the plan to reinstall from project metadata (`uv pip install --python <venv>/bin/python -e .`) rather than `pip install package`.
   - If adding a dependency absent from `uv.lock`, prefer bare `uv lock` plus diff inspection over `uv lock --upgrade-package <pkg>`.
   - If TDD-red tests might fail at collection time, require imports inside test functions so each intended test fails for the expected reason.
   - If a plan requires creating a follow-up issue, include that GitHub action in the explicit scope boundary.
   - For TOML/structured config edits, require TOML-aware edits or exact existing-array patches that preserve syntax.

4. Patch governance hygiene in the same pass.
   - Header status/revision should match current reality (`draft v4`, `plan-review`, etc.).
   - Evidence should state the current live issue label, not historical `status:plan-approved` drift after rollback.
   - Acceptance criteria should require fresh current-draft review artifacts, not stale `-r3.md` or old self-review artifacts.
   - Risks should explain any earlier approval drift as resolved if the issue is now correctly back in `status:plan-review`.

5. Re-review narrowly before broader rerun.
   - Use a delegated or independent reviewer for a fast governance-hygiene review after patches.
   - Ask specifically about stale status, stale review-artifact references, command-policy drift, and scope contradictions.
   - Keep the issue not approval-ready unless a fresh current-draft substantive review has no MAJOR findings.

6. Avoid git contention.
   - If `git add`/`status` fails with `.git/index.lock`, check `ps -ef | grep '[g]it'` before removing locks.
   - If an active `git remote-https`, pre-push hook, or quality gate is running, do not kill it just to land planning edits unless explicitly authorized.
   - Post a progress comment with exact local artifacts prepared for commit and leave the worktree for the active writer to clear.
   - Only remove `.git/index.lock` when no real git process is running.

7. Recover when the terminal/fanout path itself is unstable.
   - If the terminal tool fails before running commands (for example `FileNotFoundError: [Errno 2] No such file or directory: '%s'`), switch to `execute_code` with `subprocess.run(..., cwd='<repo>')` for git, `gh`, and review commands rather than abandoning the gate.
   - If a combined fanout command times out, rerun providers one at a time (for example `--providers=codex` then `--providers=claude`) and read the regenerated provider artifacts directly.
   - If ad-hoc provider CLI reruns stall with empty stdout/logs, do not wait indefinitely: poll once or twice, kill the stuck process, preserve any successful provider output, and record the stalled provider as infrastructure/tooling state rather than substantive review signal.
   - For non-interactive reruns, prefer an explicit prompt file plus the provider's documented stdin mode. Avoid shell patterns that confuse the wrapper into waiting for stdin (for example a positional prompt while stdin is still open, or giant command substitutions that bypass expected file input). If a wrapper prints "Reading additional input from stdin..." or "no stdin data received" and then hangs, relaunch with corrected stdin handling or mark unavailable.
   - Treat review artifacts as stale unless they were generated after the latest plan commit or patch. A MAJOR artifact that predates the final patch is diagnostic input, not current gate evidence.
   - When a provider rerun downgrades to MINOR with an empty Blockers list, patch only governance/clarity minors that materially affect implementability before the final gate; do not churn the plan for cosmetic findings.
   - Before citing review artifacts in a committed plan, verify the artifact path is trackable in the target repo. If `scripts/review/results/` is ignored, either use an already-tracked review-artifact location such as `docs/reports/` or explicitly force-add only when repo policy allows it; do not cite ignored local-only files as durable approval evidence.

## GitHub progress comment template

```text
#<issue> plan-redraft/re-review progress update.

Review results:
- Codex: UNAVAILABLE because <tool failure>. No substantive signal.
- Gemini/other: <VERDICT> with blockers: ...

Plan patches applied locally:
- ...

Follow-up review:
- <reviewer> returned <VERDICT> for governance hygiene.

Current landing status:
- Local files are patched, but not committed/pushed because <active git/pre-push process>. Avoiding git contention.

Local artifacts prepared for commit once git clears:
- <paths>
```

## Pitfalls

- Do not downgrade a plan to approved just because a prior self-review returned APPROVE; stale self-review artifacts do not satisfy a fresh current-draft review requirement.
- Do not let `UNAVAILABLE` Codex/Gemini artifacts hide the need for real cross-provider review.
- Do not run direct `pip install <missing-dep>` as the green proof for a dependency-declaration fix; it can bypass the project metadata and mask the core bug.
- Do not force-remove `.git/index.lock` while another agent's pre-push hook or git process is still active.
