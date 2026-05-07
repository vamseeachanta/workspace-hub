---
name: VA job applications log location
description: Where VA's job-application records live and the per-entry shape — pointer for "add this to applications" / "what did I apply to" requests
type: reference
originSessionId: 3cf69cd0-fda5-4753-8971-3bfb6b129ef4
---
VA's job-application records live in the **`teamresumes`** git repo (separate from `workspace-hub` — a sibling at `/mnt/local-analysis/workspace-hub/teamresumes/`, remote `https://github.com/vamseeachanta/teamresumes`).

Path pattern: `cv/va/applications-YYYY.md` (year-scoped). First file: `cv/va/applications-2026.md`, started 2026-05-06 with the Candid entry (commit `1f1aa02` on `main`).

**Per-entry shape:**
1. One-line row appended to the at-a-glance table at the top: `| YYYY-MM-DD | Company | Role (as posted) | Stage / Source | Status |`
2. Long-form section below with: company snapshot, why-the-role-exists, scope, requirements, nice-to-haves, comp/perks, fit notes (VA's own match/gap analysis), source, status. JD captured verbatim against posting-disappearance.

**Operational notes:**
- `teamresumes/` is its own git repo. Always use `git -C /mnt/local-analysis/workspace-hub/teamresumes ...` for staging/commit/push (do not run from workspace-hub root).
- `cv/va/` is git-tracked and not gitignored (verified 2026-05-06).
- Stage with explicit file paths, not `-A`, since `teamresumes/` accumulates cruft (`.coverage.*`, `.backup-*` files) that should not enter commits.
- Hooks run normally (no `--no-verify`); pre-commit secret-scan will catch credential-string leaks if a future JD or fit-note quotes one.

**Sibling pattern** (do not confuse): `achantas-data/` (also a sibling repo) holds personal data + travel **as GitHub issues**, per `reference_achantas_data.md`. Job applications are intentionally markdown-in-teamresumes, not issues — career artifacts live alongside the resume they target.
