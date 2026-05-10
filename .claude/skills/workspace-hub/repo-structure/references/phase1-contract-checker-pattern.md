# Phase 1 Repo-Structure Contract Checker Pattern

Use this reference when executing approved Phase 1 repo-structure normalization issues across workspace-hub tier-1 repos.

## Scope boundary

Phase 1 is a bounded contract/checker/enforcement slice. It may add or update:
- `docs/standards/repo-structure.md` or the repo-equivalent standard
- `config/repo_structure.yml`
- `scripts/maintenance/verify_repo_structure.py` or repo-equivalent checker
- focused tests under `tests/repo_structure/`
- pre-commit / CI wiring when the repo already has those enforcement surfaces
- `.planning/plan-approved/<issue>.md` when required by the local plan gate

Phase 1 must not perform broad source/docs/generated-output moves or delete/relocate tracked generated-looking artifacts unless the approved plan explicitly expands scope.

## TDD checker slices

Write failing tests before checker implementation. Minimum useful slices:
1. Reject an unapproved root/path.
2. Reject a generated-output root without exception metadata.
3. Reject placeholder exception metadata such as `TBD`, `TODO`, empty owners, or missing follow-up URL.
4. Reject a generated artifact path that is under a generated root but not explicitly listed in the exception's `allowed_paths`.
5. Accept current tracked repo paths only after every current root and generated artifact exception is intentionally classified.
6. Preserve leading-dot roots (`.github`, `.claude`, `.planning`) rather than collapsing them or stripping the dot.
7. Include non-ignored working-tree paths in the default checker, not just `git ls-files`, so new root clutter is caught before commit.
8. Preserve git status codes and reject deletion/relocation of generated-output paths (`D`, `R`, rename arrows) even if those paths are otherwise classified as durable exceptions.
9. Parse git paths robustly using NUL-delimited commands where possible (`git ls-files -z`, `git status --porcelain -z`) so quoted, spaced, arrow-containing, and non-ASCII filenames are not misread.
10. Reject exception metadata declared for a non-generated root; exceptions are for generated-output roots, not a way to bypass normal allowed-root policy.

## Config pattern

`config/repo_structure.yml` should separate:
- `allowed_roots`: approved source/docs/config/tooling roots and approved root files
- `ignored_roots`: `.git`, virtualenvs, caches, build directories, test reports, and other ignored/transient roots
- `generated_artifact_roots`: outputs/report/build/log roots and root-level generated files
- `temporary_exceptions`: generated roots that are intentionally tracked today

Each generated exception should include:
- `category`: e.g. `durable-evidence`, `temporary-durable-exception`, or `authorized-generated-artifact`
- `owner`
- `review_date`
- `follow_up`: GitHub issue URL or durable governance link
- `justification`: concrete reason the artifact is tracked now
- `allowed_paths`: exact tracked paths currently permitted under the generated root

Do not use broad glob exceptions for generated roots in Phase 1 unless the plan explicitly authorizes a broader classification model.

## Static-site repo gotchas

Static-site repos may legitimately track many root HTML files and deploy metadata today. Treat those as approved root files in Phase 1 if they are already tracked and used by the site. Do not normalize them into `src/` or `docs/` without later explicit approval.

Generated-looking static-site artifacts often include `reports/**`, `blog_output/**`, `stats.json`, `dist/**`, `site/**`, `coverage.xml`, and `.coverage`. Existing tracked artifacts must be classified before any move/delete. If live source/docs intentionally reference a generated path, do not add broad stale-reference gates that would reject legitimate current links; scope the checker to unauthorized tracked generated roots and unclassified generated paths.

## Markdown/strategy repo gotchas

Strategy or documentation-only repos may not have `AGENTS.md`, `pyproject.toml`, `package.json`, a pre-existing `tests/` tree, pre-commit config, or CI workflows. Do not force Python-package rules onto them. Use the repo README and approved plan as the local contract source, and label the baseline honestly as bounded/targeted (for example, a UTF-8 markdown-readability scan) when no full test suite exists.

For these repos, Phase 1 may still add a tiny pytest-based checker test suite under `tests/repo_structure/` plus `scripts/maintenance/verify_repo_structure.py`, provided the transaction documents that this is new repo-structure validation rather than a pre-existing full suite. Only wire pre-commit/CI if those enforcement surfaces already exist or the approved plan explicitly authorizes creating them.

Approval markers can be committed before implementation to satisfy plan-gate requirements, but then the repo is intentionally ahead of `origin/main`. After that point, report `HEAD` and `origin/main` with separate `git rev-parse --short HEAD` / `git rev-parse --short origin/main` commands; `git rev-parse --short HEAD origin/main` is invalid and can obscure the baseline evidence.

## Import/package gotcha for checker tests

If tests import `scripts.maintenance.verify_repo_structure`, first create the package path or write tests to invoke the script as a CLI. A RED failure caused by `ModuleNotFoundError: No module named 'scripts.maintenance'` is acceptable as the first missing-implementation proof only if the next GREEN step creates the package/script and keeps behavior tests focused on the contract.

## Validation ladder

Before closeout, capture:
- RED evidence for the initial focused checker test
- GREEN evidence for focused checker tests
- direct checker run against the current repo
- baseline test-suite command and result, clearly labeled full-suite or bounded/targeted
- deterministic generated-artifact classification evidence
- proof that no unapproved moves/deletions occurred

Closeout remains transactional: commit, push, GitHub comment, label cleanup/closure, branch/worktree disposition, and clean-state proof belong in the same window.
