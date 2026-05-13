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
2. Resolve whether the artifact path is inside the canonical git repository. If the generated file lives in a staging/non-repo mount (for example `/mnt/ace/...`) but the deliverable belongs in a tier-1 repo, copy it into the repo-tracked canonical path first, then verify and commit the repo path. Do not treat a non-repo staging directory as the source of truth for push/closeout.
3. Compare the exact claimed paths against git status, git diff, and generated output files.
4. Confirm no unrelated dirt is being mistaken for task output.
5. For public/distributable generated artifacts, inspect machine-readable sidecars/manifests as well as the visible output: they must not serialize absolute local paths, staging roots, client repo names, temp directories, or other environment/client identifiers.
6. For visual artifacts (PNG/SVG/PDF/HTML charts, brochures, dashboards), run both structural smoke checks and a human/visual readability check before claiming success.
7. For interactive chart artifacts (dropdowns, sliders, tabs, filters), verify at least one representative control path in a browser or DOM-capable test: confirm the default selection is present, changing the control updates the expected chart/data region, and the displayed labels/units remain correct. Static HTML grep alone is not sufficient for interactive controls.
8. For generated artifact families (HTML + PDF + ZIP/manifests), verify the complete family together: inspect `file` output, sizes/page counts where available, secret/deny-list scan text renderables, and re-run status after staging/commit because PDF/ZIP generators can rewrite already-tracked binaries after an apparently clean check.
9. If the repo-wide/legal scanner fails because of unrelated dirty files outside the claimed artifact set, do not either ignore it or falsely report a clean official scan. Run a staged/claimed-file-only deny-list check, report it explicitly as scoped evidence, and document the unrelated blocker separately.
10. Record evidence before closing or reporting success.

## Dirty or Hanging Git Status During Handoff

If repo-wide `git status` or combined status/log commands hang, time out, or produce unusable/truncated output, switch to bounded path-scoped verification instead of retrying broad commands. Use `GIT_OPTIONAL_LOCKS=0 timeout 10 ...` around conflict checks, individual path status checks, branch divergence checks, and file-existence checks. If the workspace is behind remote, dirty, or conflict-adjacent (`AA`/`UU`/ambiguous planning files), do not create a mixed handoff commit; leave the handoff untracked if necessary, document why, and give the next session explicit salvage/reconciliation steps. If normal `git commit` also hangs but the staged file set and diff are narrow, fully verified, and ready for immediate push, follow the `worktree-branch-sync-hygiene` `references/commit-tree-fallback-when-commit-hangs.md` fallback rather than repeatedly invoking hanging porcelain. See `references/dirty-hanging-status-handoff.md`.

## Post-Compaction Verification Resume

When a context-compaction handoff leaves only a preserved active task list, treat the summary as reference-only and re-ground before claiming closeout. Reload the governing verification skill, identify the exact committed artifact paths, verify those paths are clean, validate representative machine-readable outputs (for example JSON with `uv run python -m json.tool`), and compare `git rev-parse HEAD` with `git ls-remote origin refs/heads/main`. If the broader worktree still has unrelated/session-generated dirt, report it separately as a caveat instead of blocking or polluting the transactional artifact commit.

## Public Artifact Hygiene

When a task generates client-facing or public GTM/report assets, treat metadata files as part of the artifact surface. Search generated manifests/sidecars and representative rendered files for `/mnt/`, `/tmp/`, workspace names, confidential repo buckets, and client/project identifiers that are not intended for publication. If an adversarial review flags local path leakage, fix the generator so future outputs emit repo-relative or artifact-relative paths rather than post-processing one file by hand. See `references/public-chart-artifact-hygiene.md` for the #2555 chart-pack example.

When the official scanner reports failures from unrelated uncommitted state (for example `.claude/state/**` session logs), preserve truthfulness by separating:
- **official scan result:** failed/blocked and why
- **scoped staged-file evidence:** exact files scanned and pass/fail result
- **decision:** whether the scoped pass is sufficient for a docs-only/handoff commit, or whether the unrelated blocker must be cleaned before publication/release

Never summarize a scoped staged-only scan as a full repo legal PASS.

## Remote Ref-Lock Push Anomaly

If `git push` fails with a remote ref-lock message like `cannot lock ref 'refs/heads/main': is at <new> but expected <old>`, do not assume the push failed. Immediately verify remote state with `git fetch origin main` or `git ls-remote origin refs/heads/main`, then compare to local `git rev-parse HEAD`. If remote already equals local `HEAD`, treat the commit as landed, record the verified state, and avoid unnecessary retry/rebase churn.

## Client-Facing GitHub Links for Generated Artifacts

When the user asks for a GitHub link to client-facing generated artifacts, especially PNG/PDF/HTML reports:
1. Commit and push the exact artifact paths first; do not give cache paths or untracked local file paths as if they are GitHub deliverables.
2. Provide both the GitHub `blob/<branch>/...` URL for browser review and the `raw.githubusercontent.com/<owner>/<repo>/<branch>/...` URL for direct download/embedding.
3. For binary/image artifacts, verify the raw URL returns HTTP `200` after push before reporting it.
4. If the artifact is on a feature/issue branch rather than `main`, say that plainly in the response so the user does not assume the link is from the default branch.

## Consolidated Session Learnings

Narrow skills absorbed during the 2026-04-29 umbrella consolidation are preserved under `references/`.
## Absorbed Narrow Skills (2026-04-29)

### `targeted-artifact-commit-verification`

- Former skill demoted to `references/targeted-artifact-commit-verification.md`.
- Preserved insight: Verify whether the exact files from a just-completed task are still uncommitted before creating another commit, especially in dirty repos with unrelated churn.
