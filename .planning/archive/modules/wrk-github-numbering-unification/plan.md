confirmed_by: user
confirmed_at: 2026-03-23T19:10:00Z
decision: passed

# WRK-5097: Unify WRK Numbering with GitHub Issue Numbering

## Recommended Option: Option A — GitHub-Issue-First Numbering

### Justification

Research findings rule out Options C and D, and favor A over B:

- **Option C (Reserve ranges) is infeasible.** GitHub does not support reserving or specifying issue numbers. The only mechanism would be creating placeholder issues to consume numbers, which is fragile, wasteful, and breaks when PRs consume numbers from the same counter.

- **Option D (Abandon WRK prefix) is too disruptive.** Hundreds of commits use `fix(WRK-NNN):` format. All filenames, asset directories, frontmatter, and skill references use `WRK-NNN`. Migration cost outweighs benefit; the prefix itself is not the problem, the divergent *numbers* are.

- **Option B (Sync on commit) preserves dual-numbering.** Two numbers would still exist during Stages 0-3, which is exactly when confusion is most likely (capture, triage, planning). The `github_issue_ref` field already provides this pattern today, and 22% of items still lack it.

- **Option A (GitHub-issue-first) eliminates divergence at the source.** Every new WRK item gets its ID from GitHub at capture time. The WRK prefix is retained (`WRK-NNN`), but NNN equals the GitHub issue number. Single source of truth. GitHub cross-references work natively. 78% of items already have GitHub issues — the pipeline exists.

**Offline fallback:** When `gh` is unavailable, capture uses a temporary local ID (`WRK-LOCAL-YYYYMMDD-HHMMSS-{hostname_short}`) which is promoted to the real GitHub-derived ID when connectivity returns. The hostname suffix prevents collisions when multiple machines capture offline simultaneously. This addresses the main concern with Option A.

**Single canonical repo:** All WRK issues are created in `vamseeachanta/workspace-hub` regardless of `target_repos`. Multi-repo items store their targets in frontmatter only — the GitHub issue counter is global to workspace-hub.

---

## Acceptance Criteria

1. **AC-1:** `next-id.sh` calls `gh issue create` to obtain the WRK ID number. The returned GitHub issue number IS the WRK ID.
2. **AC-2:** Capture pipeline produces files named `WRK-{gh_issue_number}.md` where the number matches the GitHub issue.
3. **AC-3:** Offline capture creates `WRK-LOCAL-YYYYMMDD-HHMMSS-{hostname}.md` with `provisional_id: true` in frontmatter. A promotion script renames these when online.
4. **AC-4:** Machine-partitioned ranges in `config/work-queue/machine-ranges.yaml` are retired (no longer needed since GitHub is the single counter).
5. **AC-5:** All existing WRK items retain their current filenames and IDs. No renaming of historical items.
6. **AC-6:** `github_issue_ref` is populated at creation time (not post-hoc) for all new items.
7. **AC-7:** Commit message format `fix(WRK-NNN):` continues to work, and `NNN` now resolves to a real GitHub issue.
8. **AC-8:** `validate-wrk-frontmatter.sh` accepts both legacy WRK IDs and new GitHub-derived IDs.
9. **AC-9:** Cross-machine capture (licensed-win-1, dev-secondary) works without range conflicts since GitHub is the single ID source.
10. **AC-10:** A `promote-local-ids.sh` script exists to batch-promote offline-captured items with `--dry-run` support.
11. **AC-11:** `workspace-hub` is the single canonical repo for all WRK GitHub issues, regardless of `target_repos`.
12. **AC-12:** `promote-local-ids.sh` rewrites all references to the old LOCAL ID across the entire workspace (blocked_by, specs, docs, session handoff notes).
13. **AC-13:** Backfill script detects existing GitHub issues (by title search) before creating, preventing duplicates.
14. **AC-14:** A regex audit script identifies all `WRK-[0-9]+` consumers in the codebase and confirms they handle `WRK-LOCAL-*` format.

---

## Pseudocode

### Step 1: Create `gh-next-id.sh` (replacement for next-id.sh)

```
function gh_next_id(title, labels, body):
    if gh_cli_available():
        # Create issue in final state — no placeholder, single API call
        issue_url = gh issue create \
            --repo vamseeachanta/workspace-hub \
            --title "WRK-{pending}: {title}" \
            --body "{body}"
        issue_number = extract_number(issue_url)
        # Fix title with actual number
        gh issue edit {issue_number} --title "WRK-{issue_number}: {title}"
        return issue_number, issue_url
    else:
        # Offline fallback with hostname to prevent cross-machine collisions
        timestamp = now().format("YYYYMMDD-HHMMSS")
        hostname = short_hostname()
        return "LOCAL-{timestamp}-{hostname}", null
```

### Step 2: Update capture pipeline to use gh-next-id.sh

```
function capture(description):
    metadata = parse_input(description)
    (id, issue_url) = gh_next_id(metadata.title, metadata.labels)

    filename = "WRK-{id}.md"
    write_wrk_file(filename, metadata, github_issue_ref=issue_url)

    if issue_url:
        # Update issue title from "WRK-PENDING" to final title
        gh issue edit {id} --title "WRK-{id}: {metadata.title}"
        # Update issue body with full rendered content
        update_github_issue(wrk_id, --update)
```

### Step 3: Create promote-local-ids.sh for offline-captured items

```
function promote_local_ids(dry_run=false):
    for file in pending/WRK-LOCAL-*.md:
        metadata = parse_frontmatter(file)
        old_id = metadata.id  # e.g. "WRK-LOCAL-20260323-120000-devpri"

        (new_id, issue_url) = gh_next_id(metadata.title, metadata.labels, metadata.body)
        new_filename = "WRK-{new_id}.md"

        if dry_run:
            log("Would promote {old_id} -> WRK-{new_id}")
            continue

        # Update frontmatter
        metadata.id = "WRK-{new_id}"
        metadata.github_issue_ref = issue_url
        metadata.provisional_id = false

        rename(file, new_filename)
        rename(assets/{old_id}/,  assets/WRK-{new_id}/)

        # Rewrite ALL references to old_id across workspace (P1 resolution)
        for ref_file in grep_recursive(workspace_root, old_id):
            sed_replace(ref_file, old_id, "WRK-{new_id}")

        # Update GitHub issue with full content
        update_github_issue(new_id, --update)
        log("Promoted {old_id} -> WRK-{new_id}, rewrote {count} references")
```

### Step 4: Retire machine-ranges.yaml and simplify state.yaml

```
function migrate_config():
    # machine-ranges.yaml: add deprecation header, keep for reference
    # state.yaml: remove last_id (GitHub is now the counter)
    # next-id.sh: keep as legacy wrapper that calls gh-next-id.sh
    # validate-wrk-frontmatter.sh: accept both WRK-NNN and WRK-LOCAL-* patterns
```

### Step 5: Backfill github_issue_ref for existing items missing it

```
function backfill_missing_refs(dry_run=false):
    for file in pending/*.md, working/*.md, blocked/*.md:
        if not has_github_issue_ref(file):
            wrk_id = extract_id(file)
            title = extract_title(file)

            # Duplicate detection (P1 resolution) — search before creating
            existing = gh issue list --repo vamseeachanta/workspace-hub \
                --search "WRK-{wrk_id}" --json number,title --limit 5
            if any(e.title.startswith("WRK-{wrk_id}") for e in existing):
                log("Found existing issue #{e.number} for {wrk_id}, linking")
                set_github_issue_ref(file, existing[0].url)
                continue

            if dry_run:
                log("Would create issue for {wrk_id}")
                continue

            update_github_issue(wrk_id, --create)
            sleep(1)  # Rate limit protection
```

### Step 6: Audit WRK-[0-9]+ regex consumers (P1 resolution)

```
function audit_wrk_regex():
    # Find all files containing WRK-[0-9]+ or WRK-\d+ patterns
    consumers = grep_recursive(workspace_root, r"WRK-\[0-9\]|WRK-\\d|WRK-[0-9]")
    for file in consumers:
        if file needs update to also handle WRK-LOCAL-*:
            log("UPDATE NEEDED: {file}")
        else:
            log("OK: {file}")
    # Output: list of files needing regex updates before Phase 2
```

---

## Test Plan

| # | Test | Type | Acceptance Criteria |
|---|------|------|---------------------|
| 1 | `gh-next-id.sh` with `gh` available returns a numeric ID that matches a real GitHub issue | integration | AC-1, AC-6 |
| 2 | `gh-next-id.sh` without `gh` (mocked unavailable) returns `LOCAL-YYYYMMDD-HHMMSS` format | unit | AC-3 |
| 3 | Full capture pipeline creates `WRK-{N}.md` where N equals the GitHub issue number | integration | AC-2, AC-7 |
| 4 | `promote-local-ids.sh` renames `WRK-LOCAL-*.md` to `WRK-{N}.md` and updates frontmatter | integration | AC-3, AC-10 |
| 5 | `validate-wrk-frontmatter.sh` accepts legacy `WRK-1128` and new `WRK-LOCAL-20260323-120000` | unit | AC-8 |
| 6 | Existing WRK files (WRK-008, WRK-5109, etc.) are untouched after migration | regression | AC-5 |
| 7 | Capture from licensed-win-1 produces a valid GitHub-derived ID (no range conflict) | integration | AC-9 |
| 8 | `state.yaml` no longer tracks `last_id` after migration; `machine-ranges.yaml` has deprecation header | migration | AC-4 |
| 9 | Commit with `fix(WRK-{N}):` where N is a GitHub issue number resolves correctly in GitHub UI | manual | AC-7 |
| 10 | Backfill script creates GitHub issues for the ~87 pending items currently missing `github_issue_ref` | integration | AC-6 |
| 11 | Backfill detects existing GitHub issue by title search and links instead of creating duplicate | integration | AC-13 |
| 12 | `promote-local-ids.sh --dry-run` previews changes without modifying files | unit | AC-10 |
| 13 | Promotion rewrites `blocked_by: WRK-LOCAL-*` references in other WRK files | integration | AC-12 |
| 14 | Regex audit script finds all `WRK-[0-9]+` consumers and reports update-needed files | unit | AC-14 |
| 15 | All issues created in `workspace-hub` repo even when `target_repos` includes other repos | integration | AC-11 |
| 16 | Offline ID with hostname: two machines capturing simultaneously produce unique LOCAL IDs | unit | AC-3 |
| 17 | `validate-wrk-frontmatter.sh` rejects malformed IDs (`WRK-abc`, `WRK-LOCAL-invalid`) | unit | AC-8 |

---

## Migration Strategy

### Phase 0: Audit (prerequisite)
1. Run regex audit script to find all `WRK-[0-9]+` consumers in the codebase (AC-14).
2. Catalog each file and determine if it needs updating for `WRK-LOCAL-*` format.
3. Gate: Phase 1 cannot start until audit is complete and all update-needed files are identified.

### Phase 1: Prepare (non-breaking)
1. Create `gh-next-id.sh` alongside existing `next-id.sh` (no existing behavior changes).
2. Create `promote-local-ids.sh` script with `--dry-run` and workspace-wide reference rewriting.
3. Update `validate-wrk-frontmatter.sh` to accept `WRK-LOCAL-*` pattern and reject malformed IDs.
4. Update all files identified in Phase 0 audit to handle `WRK-LOCAL-*` format.
5. Run all existing tests to confirm no regressions.

### Phase 2: Switch capture pipeline
1. Update `capture.md` action skill to call `gh-next-id.sh` instead of `next-id.sh`.
2. Wrap `next-id.sh` as a legacy alias that logs a deprecation warning and calls `gh-next-id.sh`.
3. Update `update-github-issue.py` to handle the case where the issue already exists at creation time (since `gh-next-id.sh` creates it).

### Phase 3: Backfill and retire
1. Run backfill script for ~87 pending items missing `github_issue_ref`.
2. Add deprecation header to `config/work-queue/machine-ranges.yaml`.
3. Remove `last_id` from `state.yaml` (or keep as legacy, not authoritative).
4. Update `machine-wrk-id-ranges` skill doc to note the deprecation.

### Phase 4: Cleanup (deferred, low priority)
1. Remove machine-range logic from `next-id.sh` wrapper.
2. Remove `machine-ranges.yaml` after 30-day deprecation period.
3. Consider renaming `next-id.sh` to `gh-next-id.sh` once all callers are updated.

### Existing items policy
- All existing WRK items (WRK-001 through WRK-5126) keep their current IDs and filenames.
- Items with `github_issue_ref` already set are not modified.
- Items without `github_issue_ref` get one via the backfill script (Phase 3).
- No attempt to align old WRK numbers with their GitHub issue numbers — the mapping is stored in frontmatter.

---

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| GitHub API unavailable during capture | Medium | Low | Offline fallback to `WRK-LOCAL-*`; promote-local-ids.sh for recovery |
| GitHub rate limiting during backfill | Low | Low | Backfill script adds 1s delay between creations; can be run incrementally |
| PRs consume GitHub issue numbers (creating gaps in WRK sequence) | Certain | Low | Accept gaps — sequential numbering is not a requirement, uniqueness is |
| Existing tools/scripts grep for `WRK-[0-9]+` pattern | Medium | Medium | `WRK-LOCAL-*` breaks this pattern; update regex in validate-wrk-frontmatter.sh and any grep-based tooling |
| Multi-repo WRK items (e.g., WRK-510 targets digitalmodel) create issues in wrong repo | Eliminated | — | All issues created in workspace-hub; `target_repos` is frontmatter-only (AC-11) |
| Partial failure: `gh issue create` succeeds but file write fails, orphaning an issue | Low | Medium | Capture wraps create+write in a transaction-like pattern; orphan reconciliation script checks for unmatched issues |
| Backfill creates duplicate GitHub issues for items that already have one | Low | Medium | Title-based duplicate detection before creation (AC-13) |
| Confusion during transition (some items have old-style IDs, some new) | Certain | Low | Old items keep their IDs; document the cutover date in machine-wrk-id-ranges skill |
| `state.yaml` consumers break when `last_id` is removed | Low | Medium | Keep `last_id` as read-only legacy field for 30 days before removal |

---

## Cross-Review Resolutions (Stage 6)

Reviewed by Claude (APPROVE), Codex (REQUEST_CHANGES), Gemini (REQUEST_CHANGES).

| P1 Finding | Resolution | New AC |
|------------|-----------|--------|
| Source-of-truth repo ambiguous (Codex) | All WRK issues created in `workspace-hub` repo only. `target_repos` is frontmatter metadata. | AC-11 |
| Promote-local-ids misses cross-references (Codex+Claude+Gemini) | Added workspace-wide grep+replace step to promotion script | AC-12 |
| Backfill duplicate detection missing (Codex) | Added title-search before issue creation in backfill | AC-13 |
| WRK-LOCAL-* breaks WRK-[0-9]+ regex (Gemini) | Added Phase 0 audit + AC-14 requiring all consumers identified and updated | AC-14 |

Additional improvements from P2/P3 findings:
- Offline ID includes hostname suffix to prevent cross-machine timestamp collisions
- `--dry-run` flag added to promotion and backfill scripts
- Negative test cases added (malformed ID rejection)
- Issue created with full content in single call where possible (reduces WRK-PENDING noise)
