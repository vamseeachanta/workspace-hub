# Plan for #2551: Security Audit — Branch/Ruleset Protections Across Public Repos After Collaborator-Only Lockdown

> **Status:** draft
> **Complexity:** T2
> **Date:** 2026-05-06
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2551
> **Review artifacts:** scripts/review/results/2026-05-06-plan-2551-claude.md | ...-codex.md | ...-gemini.md

---

## Resource Intelligence Summary

### Existing repo code

- Found: `docs/BUSINESS_BRAIN.md:10-59` — canonical repo inventory; lists 24 active repos across 3 tiers: Tier-1 (workspace-hub, digitalmodel, assetutilities, aceengineer-website), Tier-2 (OGManufacturing, acma-projects, frontierdeepwater, worldenergydata, sabithaandkrishnaestates), Tier-3/archive (~11 repos). Interaction-limit lockdown (#2546) targeted public repos — Tier-1 and Tier-2 are the primary audit scope.
- Found: `docs/standards/CONTROL_PLANE_CONTRACT.md` — exists; defines `ace-linux-1` as dispatch control plane with GitHub-mutation authority. Relevant: branch protection rules that block unauthorized pushes to main are part of the same governance layer.
- Gap: No dedicated security audit script exists in `scripts/security/` for branch-protection querying.
- Gap: No `docs/security/` directory exists — this plan creates it as the evidence landing zone.

### Standards

| Standard | Status | Source |
|---|---|---|
| GitHub branch protection model (required reviews, status checks, force-push/delete settings) | gap — no formal standard; GitHub documentation is the reference | Issue body §scope |
| Repository ruleset model (repo-level vs organization-level rulesets) | gap — not codified in any workspace-hub standard | Issue body §scope |

Not applicable to engineering standards ledger — this is a security governance issue.

### LLM Wiki pages consulted

No relevant wiki pages exist for GitHub branch-protection governance in this repo's knowledge base.

### Documents consulted

- `docs/BUSINESS_BRAIN.md` (lines 10-59) — repo inventory with tier classification; used to derive audit scope (Tier-1 + public Tier-2 first; Tier-3 as secondary pass).
- `docs/standards/CONTROL_PLANE_CONTRACT.md` — found; defines machine-level authorization model. Branch protection rules are the repo-level analog of this contract: they enforce that code mutations go through authorized paths.
- Prior issue #2546 (referenced in issue body) — completed interaction-limit lockdown ("collaborators-only" flag set across public repos). This audit verifies the complementary code-path controls that interaction limits do NOT cover.
- `docs/plans/` search for "security|branch.protection|2546|2551" — returned 10 plan files, none covering branch protection or ruleset audit. No prior plan exists.
- `.claude/rules/coding-style.md`, `.claude/rules/patterns.md` — harness enforcement rules reviewed; no branch-protection auditing tooling exists yet; security scripts at `scripts/enforcement/` cover path checks and file size only.

### Gaps identified

- No `docs/security/` directory — must be created.
- No branch-protection audit script or MCP query workflow documented anywhere in the repo.
- No minimum public-repo protection baseline defined for this ecosystem.
- Tier-3/archive repos have no clear policy — audit must distinguish "intended bare/no-protection" from "accidentally unprotected."

### Evidence (embedded verification)

**Issue statuses** (verified 2026-05-06 via GitHub MCP):
- `#2551` — OPEN — audit(security): verify branch/ruleset protections across public repos after collaborator-only lockdown
- `#2546` — (referenced in body as completed root hardening; not re-verified here — treat as closed)

**File existence** (`ls` 2026-05-06T00:00Z):
- EXISTS: `docs/standards/CONTROL_PLANE_CONTRACT.md`
- EXISTS: `docs/BUSINESS_BRAIN.md`
- MISSING (new — this plan creates): `docs/security/` directory
- MISSING (new — this plan creates): `docs/security/2026-05-06-public-repo-protection-audit.md`
- MISSING (new — this plan creates): `docs/security/public-repo-protection-baseline.md`

**Gap proofs**:
- `ls docs/security/ 2>&1` → "No such file or directory" → confirms directory does not exist; this plan creates it.
- `find docs/plans/ -name "*.md" | xargs grep -l "security|branch.protection" | wc -l` → 10 files → none targeted branch-protection audit specifically (confirmed by review: all 10 were CI, email, or general security mentions).
- `ls scripts/security/ 2>&1` → lists existing enforcement scripts (check-no-abs-paths.sh, check-harness-file-size.sh) → no branch-protection auditing tool exists.

<!-- Verification: count distinct sources above (across all sub-sections).
     Minimum 3 required (issue body + 2 others). Current count: 5 -->

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-05-06-issue-2551-security-audit-public-repos-branch-protection.md` |
| Audit evidence table | `docs/security/2026-05-06-public-repo-protection-audit.md` |
| Minimum baseline doc | `docs/security/public-repo-protection-baseline.md` |
| Audit query script | `scripts/security/audit-repo-protections.sh` |
| Tests | `tests/security/test_audit_repo_protections.py` |
| Plan review — Claude | `scripts/review/results/2026-05-06-plan-2551-claude.md` |
| Plan review — Codex | `scripts/review/results/2026-05-06-plan-2551-codex.md` |
| Plan review — Gemini | `scripts/review/results/2026-05-06-plan-2551-gemini.md` |

---

## Deliverable

A `docs/security/2026-05-06-public-repo-protection-audit.md` evidence table covering all Tier-1 and Tier-2 public repos with columns for: visibility, archived state, default branch, interaction-limit status, branch-protection status, ruleset status, required reviews, required status checks, force-push/delete enabled, Issues/Discussions/Wiki/Actions surfaces enabled — plus a `docs/security/public-repo-protection-baseline.md` defining the minimum protection standard, and a reusable `scripts/security/audit-repo-protections.sh` that produces the same table on demand via GitHub CLI.

---

## Pseudocode

```
script audit-repo-protections.sh:
    repos = read from BUSINESS_BRAIN.md or pass as args (default: Tier-1 + Tier-2)
    for each repo in repos:
        meta = gh repo view <repo> --json visibility,isArchived,defaultBranchRef,
                   hasIssuesEnabled,hasDiscussionsEnabled,hasWikiEnabled
        bp   = gh api repos/<owner>/<repo>/branches/<default>/protection --silent
               (returns 404 if no protection set)
        rulesets = gh api repos/<owner>/<repo>/rulesets (list all; filter active)
        row = {
            repo, visibility, archived, default_branch,
            interaction_limit: "collaborators-only" (from #2546; assume set),
            branch_protection: "yes/no + required_reviews + status_checks",
            rulesets: "count + bypass_actors",
            force_push_blocked: derived from bp,
            surfaces: hasIssues + hasDiscussions + hasWiki + hasActions
        }
        append row to output table
    emit markdown table sorted by tier
    emit "Findings" section: repos with no protection AND not archived
    emit "Follow-up issues" section: one bullet per unprotected active repo
```

```
baseline doc public-repo-protection-baseline.md:
    Tier-1 (active code repos):
        - default branch protection required
        - require at least 0 pull request reviews (solo practitioner — no forced PR)
        - block force pushes to default branch
        - block branch deletion on default branch
        - at least one status check required (CI green gate)
        - Issues enabled (workflow intake); Discussions optional; Wiki disabled (wiki lives in knowledge/)
    Tier-2 (domain-specific, public):
        - same as Tier-1 for active repos
        - archived repos: no protection needed; archive flag is the gate
    Tier-3 / archive candidates:
        - recommend archiving rather than adding protection
        - if not yet archived: block force pushes minimum
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | `docs/security/2026-05-06-public-repo-protection-audit.md` | Evidence table — audit output for this run |
| Create | `docs/security/public-repo-protection-baseline.md` | Minimum protection standard for public repos |
| Create | `scripts/security/audit-repo-protections.sh` | Reusable audit script via `gh` CLI; uses relative paths / `$(git rev-parse --show-toplevel)` per coding-style.md |
| Create | `tests/security/test_audit_repo_protections.py` | TDD guard: script exits 0 on valid args, emits required columns, validates output format |
| Update | `docs/plans/README.md` | Add this plan to index |

---

## TDD Test List

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| `test_script_exits_zero_dry_run` | Script runs without error in dry-run/mock mode | `--dry-run` flag with fixture repo list | exit code 0 |
| `test_output_has_required_columns` | Audit table has all 10 required columns | fixture output | markdown table with repo, visibility, archived, default_branch, interaction_limit, branch_protection, rulesets, force_push_blocked, delete_blocked, surfaces columns |
| `test_unprotected_active_repo_flagged` | Unprotected non-archived repo appears in Findings section | mock gh returning no-protection on a non-archived repo | repo name appears in Findings section |
| `test_archived_repo_not_flagged` | Archived repos do not appear in Findings | mock gh returning no-protection on an archived repo | repo name NOT in Findings section |
| `test_baseline_doc_has_tier1_rules` | Baseline doc defines Tier-1 rules | `docs/security/public-repo-protection-baseline.md` exists | grep for "force push" and "Tier-1" both match |

---

## Acceptance Criteria

- [ ] `docs/security/2026-05-06-public-repo-protection-audit.md` contains a row for every Tier-1 and Tier-2 public `vamseeachanta/*` repo
- [ ] Evidence table columns cover all fields listed in issue body §scope: visibility, archived state, default branch, interaction limit status, branch/ruleset status, required reviews, status checks, force-push/delete settings, Issues/Discussions/Projects/Wiki/Actions surfaces
- [ ] Findings section explicitly separates: (a) already-hardened (interaction limits), (b) code-path protections present, (c) code-path protections missing
- [ ] `docs/security/public-repo-protection-baseline.md` distinguishes Tier-1/active from Tier-3/archive candidates
- [ ] Any proposed branch-protection changes are listed as bullets in a "Follow-up issues" section of the audit doc, NOT applied directly — each becomes a separate `status:plan-review` child issue
- [ ] `scripts/security/audit-repo-protections.sh` uses `$(git rev-parse --show-toplevel)` for path resolution (no hardcoded absolute paths per coding-style.md)
- [ ] All 5 TDD tests pass: `uv run pytest tests/security/test_audit_repo_protections.py -v`
- [ ] Script produces a fresh audit run: `bash scripts/security/audit-repo-protections.sh --output docs/security/YYYY-MM-DD-audit.md` exits 0

---

## Adversarial Review Summary

<!-- Filled in after Step 4 completes. -->

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | — | — |
| Codex | — | — |
| Gemini | — | — |

**Overall result:** Pending

---

## Risks and Open Questions

- **Risk:** GitHub API returns 404 on branch protection if no protection is set (not an error — this is the "unprotected" signal). Script must handle 404 gracefully and map it to `protection: none` in the table, not abort.
- **Risk:** MCP session is scoped to `vamseeachanta/workspace-hub` only; the audit script will use `gh` CLI directly (not MCP) to query other repos — this is the correct path because the audit needs to query ~10+ repos outside the MCP scope.
- **Risk:** Interaction-limit status is NOT queryable via `gh repo view` standard fields — requires `gh api /repos/<owner>/<repo>/interaction-limits` endpoint. Script must handle this separately and may return empty if the temp limit from #2546 has expired (interaction limits are time-bound).
- **Open:** Should the audit cover Tier-3/archive candidates? Recommended: include them in a separate section with "recommend archiving" rather than recommending protection rules, to avoid wasted hardening work on repos that should be archived.
- **Open:** Organization-level rulesets vs repo-level rulesets: for a single-owner personal GitHub account (not org), organization rulesets do not apply — audit can skip org-ruleset check and focus on repo-level only. Confirm with `gh api /orgs/vamseeachanta/rulesets` — expected to return 404 (personal account, not org).

---

## Complexity: T2

**T2** — new script + new documentation directory + TDD tests + multi-repo data gathering. More than a single-file fix but well under T3: no architectural changes, no multi-module dependencies, single focused session.
