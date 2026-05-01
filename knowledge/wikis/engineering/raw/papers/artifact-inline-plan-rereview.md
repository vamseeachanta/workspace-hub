# Archived Skill: `artifact-inline-plan-rereview`

Original path: `/home/vamsee/.hermes/skills/software-development/artifact-inline-plan-rereview`
Archived into: `/home/vamsee/.hermes/skills/.archive/umbrella-2026-04-29/software-development/artifact-inline-plan-rereview`
Consolidation date: 2026-04-29

---

---
name: artifact-inline-plan-rereview
description: Recover adversarial plan reviews when providers keep reading stale remote/main content instead of the revised local artifact.
version: 1.0.0
author: Hermes Agent
category: software-development
triggers:
  - Local plan was materially revised after an earlier review
  - Provider review references content no longer present in the local artifact
  - Codex/Gemini appear to be reviewing stale remote/main state
---

# Artifact-Inline Plan Re-Review

Use this when a plan has been tightened locally but provider reruns keep reviewing an older remote/main version.

## When to use
- The plan file was revised locally after earlier MAJOR/MINOR findings
- A provider returns findings about content you already removed
- Path-based or repo-discovery prompts are likely to fetch stale branch/default-branch state

## Reliable recovery pattern
1. Read the revised local plan artifact from disk.
2. Extract only the exact sections under review, typically:
   - Deliverable
   - Scope Boundaries
   - Linkage Strategy
   - Downstream Integration Surface
   - Pseudocode
   - Files to Change
   - TDD Test List
   - Acceptance Criteria
3. Build a compact self-contained prompt that explicitly says:
   - review ONLY the inline artifact below
   - do NOT substitute any remote/main/branch version
4. Run the provider against that inline-artifact bundle, not a path-only prompt.
5. Treat this rerun as authoritative if it resolves stale-remote drift and materially changes the verdict.

## Why this works
Provider sandboxes or GitHub connectors may prefer remote/default-branch content over fresh local edits. Inline artifact prompts force review against the intended version.

## Guardrails
- Keep the prompt compact; include only the sections needed for the decision.
- For Codex CLI, do not use the obsolete `--no-interactive` flag; current `codex exec` rejects it. Prefer `codex exec "$(< prompt.md)"` or stdin/file-based invocation supported by the installed CLI.
- Avoid sending a full large plan inline unless necessary. Large inline prompts can hang with empty output; first try a narrowed artifact bundle containing only the sections tied to the prior MAJOR findings.
- Run inline re-reviews with explicit timeout/process monitoring. If a provider produces empty stdout and no useful stderr after the timeout, kill it and record the run as infrastructure/no-signal, not as a review verdict.
- Remove or clearly quarantine empty/partial review artifacts from failed/hung runs so later approval checks do not mistake them for clean review evidence.
- Say explicitly that the local artifact was revised after prior review.
- Summary-only prompts are not enough when the provider can still infer remote/default-branch content; inline the exact local sections under review.
- If the provider still mentions removed content, discard that run as stale-context contamination and rerun.
- Before replacing canonical review artifacts, compare the findings against the current local plan text and confirm the reviewer is no longer talking about already-removed items.

## Child-issue sequencing lesson
When reviewing child plans in parallel, Codex may still return structural MAJOR findings if the child plan assumes parent artifacts that are approved conceptually but not yet present on current `main`.

Add these explicitly in the child plan:
- exact parent issue dependency
- statement that the parent contract/files may not yet exist on current `main`
- wording that the child consumes that future parent surface rather than modifying today's unrelated legacy/sanction-era files

This is especially important for follow-up issue trees where multiple child plans are being adversarially reviewed in the same wave.

## Missing-artifact / branch-drift recovery lesson
If the expected revised plan artifact vanishes, truncates, or is absent because the current checkout is on an unrelated planning branch:
1. Stop editing the dirty/mismatched checkout; do not recreate the plan in-place if it risks trampling another active branch.
2. Inspect `git branch --show-current`, `git worktree list`, `origin/main`, and the GitHub issue state.
3. Create an isolated approval/review worktree from current `origin/main`, for example:
   `git worktree add /mnt/local-analysis/worktrees/<repo>-<issue>-approval origin/main`
4. Reconstruct or compact the current plan there from durable issue comments, repo evidence, and current source files. Prefer a concise approval-ready artifact over restoring stale verbose review-history prose.
5. Apply approval-stage hygiene before review: remove stale process narration, fix duplicate plan-index rows, ensure `READY` means implemented evidence (not merely approved future plans), and pin schema/test failure semantics.
6. If provider CLIs are unstable or hang, use isolated `delegate_task` reviewers against the exact local artifact and persist concise review artifacts manually only after they produce real signal. Empty/hung artifacts must be deleted or quarantined.
7. Commit and push the docs/review-artifact state before labeling the issue `status:plan-review`, rebasing on `origin/main` if push is rejected as non-fast-forward.

## Example use case
On 2026-04-22 for worldenergydata issue #334, Codex initially returned a false MAJOR by reviewing stale remote/main content. An artifact-inline rerun against the exact revised local sections changed the verdict to MINOR and aligned with the actual bounded plan.

In the same wave, child-plan reviews for #335–#338 showed that Codex often blocks plans as mis-grounded to `main` unless parent dependency and future-surface assumptions are made explicit.
