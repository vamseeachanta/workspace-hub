---
name: artifact-commit-verification
version: 1.0.0
category: development
description: Class-level artifact and commit verification for claimed agent work, exact file diffs, and closeout evidence.
tags: [artifacts, commits, verification, agents]
---

# Artifact Commit Verification

## When to Use
Use when an agent claims work is complete and you need to verify exact files, commits, generated artifacts, issue closeout evidence, or working-tree state before trusting the claim.

## Class-Level Workflow
1. Identify the claimed artifact/file/commit set.
2. Compare the exact claimed paths against git status, git diff, and generated output files.
3. Confirm no unrelated dirt is being mistaken for task output.
4. For public/distributable generated artifacts, inspect machine-readable sidecars/manifests as well as the visible output: they must not serialize absolute local paths, staging roots, client repo names, temp directories, or other environment/client identifiers.
5. For visual artifacts (PNG/SVG/PDF/HTML charts, brochures, dashboards), run both structural smoke checks and a human/visual readability check before claiming success.
6. If the repo-wide/legal scanner fails because of unrelated dirty files outside the claimed artifact set, do not either ignore it or falsely report a clean official scan. Run a staged/claimed-file-only deny-list check, report it explicitly as scoped evidence, and document the unrelated blocker separately.
7. Record evidence before closing or reporting success.

## Public Artifact Hygiene

When a task generates client-facing or public GTM/report assets, treat metadata files as part of the artifact surface. Search generated manifests/sidecars and representative rendered files for `/mnt/`, `/tmp/`, workspace names, confidential repo buckets, and client/project identifiers that are not intended for publication. If an adversarial review flags local path leakage, fix the generator so future outputs emit repo-relative or artifact-relative paths rather than post-processing one file by hand. See `references/public-chart-artifact-hygiene.md` for the #2555 chart-pack example.

When the official scanner reports failures from unrelated uncommitted state (for example `.claude/state/**` session logs), preserve truthfulness by separating:
- **official scan result:** failed/blocked and why
- **scoped staged-file evidence:** exact files scanned and pass/fail result
- **decision:** whether the scoped pass is sufficient for a docs-only/handoff commit, or whether the unrelated blocker must be cleaned before publication/release

Never summarize a scoped staged-only scan as a full repo legal PASS.

## Consolidated Session Learnings

Narrow skills absorbed during the 2026-04-29 umbrella consolidation are preserved under `references/`.
## Absorbed Narrow Skills (2026-04-29)

### `targeted-artifact-commit-verification`

- Former skill demoted to `references/targeted-artifact-commit-verification.md`.
- Preserved insight: Verify whether the exact files from a just-completed task are still uncommitted before creating another commit, especially in dirty repos with unrelated churn.
