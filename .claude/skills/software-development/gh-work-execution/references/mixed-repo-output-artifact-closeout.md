# Mixed-repo output artifact closeout

Use when an approved issue changes implementation in one sibling repo but must also publish generated deliverables into another repo or an embedded output tree.

## Trigger

- Implementation files live in a tier-1 sibling repo such as `/mnt/local-analysis/digitalmodel`.
- Final deliverables must land in a different checkout or embedded output path, for example `/mnt/local-analysis/workspace-hub/acma-projects/B1528/output`.
- The orchestration repo is dirty, ahead/behind, or contains unrelated generated state.

## Pattern

1. Verify the issue gate first: GitHub `status:plan-approved`, local plan marker if hooks require it, and the approved plan/output contract.
2. Classify each output path by actual Git boundary before staging:
   - Run git status in the implementation repo.
   - Run git status in the output location.
   - If the output location is not a Git repo, walk upward to identify the owning checkout.
3. Keep implementation and packaged-output commits separate unless they are in the same repository and validation requires one atomic commit.
4. Stage by explicit paths only. Never use `git add .` from a dirty orchestration repo.
5. Verify generated artifacts by content, not existence alone:
   - Markdown/HTML: required headings, default assumptions, forbidden-resultant/heatmap terms absent.
   - DOCX: open with `python-docx` and assert required sections.
   - PDF: extract text and assert required/forbidden terms.
   - Manifest: list every artifact, source/citation sidecars, supersession note, and repo/output path.
6. After committing the implementation repo, re-check output artifacts before committing the packaging repo. Regeneration can change timestamps/manifest paths.
7. Closeout comment must separate:
   - implementation repo commit/push evidence,
   - packaging/output repo commit/push evidence,
   - artifacts generated but intentionally untracked,
   - unrelated dirty files preserved.

## Pitfalls

- A directory named like a repo (`/mnt/local-analysis/acma-projects`) may not be a Git checkout. Do not assume; verify the owning repository.
- `workspace-hub` can be dirty from agent state, memory snapshots, provider dashboards, review artifacts, or unrelated planning work. Path-scope every stage/commit.
- A generated PDF/DOCX existing on disk is not sufficient. Parse/extract text before reporting it as client-ready.
- Do not close the GitHub issue until every promised repo/output surface is landed or explicitly documented as local-only/untracked by design.
