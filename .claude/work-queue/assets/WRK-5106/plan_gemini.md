YOLO mode is enabled. All tool calls will be automatically approved.
Loaded cached credentials.
YOLO mode is enabled. All tool calls will be automatically approved.
# WRK-5106 Plan — Refined

## Deliverable
One new script: `scripts/work-queue/backfill-issues.sh` (~150 lines bash)

## Approach

### Phase 1: Fetch & Match
1. `gh issue list --repo vamseeachanta/workspace-hub --state all --limit 5000 --json number,title` → temp file. **Must use `jq` to parse the JSON robustly.**
2. For each issue, extract the `WRK-\d+` identifier from the title using robust regex matching (e.g., `grep -oE`).
3. **Conflict Resolution:** If multiple GitHub issues map to the same `WRK-NNN`, log a warning and skip to prevent data overwrite.
4. Find local WRK file using the canonical `find_wrk_file()` pattern from `scripts/work-queue/backfill-domain-labels.sh`.

### Phase 2: Backfill github_issue_ref (YAML Parsing)
5. **Robust YAML Injection:** Do NOT use raw `sed` for YAML mutation. This is highly fragile. Instead, use a python inline script or `yq` to safely read/write the YAML frontmatter. It must handle edge cases gracefully: missing frontmatter, malformed YAML, or an already existing key.
6. Verify file modification was successful before proceeding.

### Phase 3: Update Issues (Execution & State Management)
7. **State Tracking:** Track progress in a state file (e.g., `.backfill-state.json`) to allow automatic resumption without relying solely on manual `--resume-from` flags.
8. Call `uv run --no-project python scripts/knowledge/update-github-issue.py WRK-NNN --update` for each match.
9. **Rate limit & Retry:** Implement a robust backoff strategy. Sleep 1s (to respect GitHub's secondary abuse rate limits, not just the hourly quota) and retry up to 3 times on 5xx or 429 HTTP errors.
10. On error: append to a dedicated `backfill-errors.log` and continue execution.

### Phase 4: Report
11. Print a comprehensive summary: total / updated / skipped (no WRK ID, no file, already current, duplicate mapping) / errors.
12. Print a helpful final message suggesting `git add` and `git status` commands for the modified WRK files.

## CLI Interface
```
backfill-issues.sh [--dry-run] [--limit N] [--resume-from N] [--auto-resume]
```
- `--dry-run`: log what would happen, no API writes or local file mutations.
- `--limit N`: process only first N issues.
- `--resume-from N`: skip first N issues manually.
- `--auto-resume`: Use the `.backfill-state.json` file to pick up exactly where the last run left off.

## Risks & Mitigation
- **Malformed WRK files:** Addressed by using a proper YAML parser instead of string manipulation.
- **GitHub Secondary Abuse Limits:** 2500+ rapid API mutations can trigger undocumented secondary limits. Addressed by increasing sleep to 1s + exponential backoff on 429s.
- **Workspace Data Corruption:** Modifying hundreds of files locally is risky. Mitigation: Enforce a clean working tree (`git diff --quiet`) before starting the script.

## Test Strategy
1. **Automated Unit Tests:** Create a test script (e.g. `tests/scripts/test_backfill_issues.bats` or a small pytest file) to explicitly test the WRK-NNN regex extraction and the YAML frontmatter injection on dummy files.
2. `--dry-run --limit 5` — verify output format, ensure zero API calls and zero file writes.
3. Manual spot-check of 3 updated issues via browser.
4. Verify `github_issue_ref` backfilled correctly in WRK files using `git diff`.

---

# Gemini Notes

1. **Failure modes in parsing (L3 gemini / JSON / YAML):** The original plan relied on `sed` to mutate YAML frontmatter. This is a critical failure mode if the target file lacks frontmatter, has malformed YAML, or if the key already exists in a different location. The refined plan mandates robust parsing for both the `gh` JSON output (`jq`) and the local file mutations.
2. **Carry-forward logic (State tracking):** Relying on `--resume-from N` is fragile if the script fails silently or if new issues shift the index. The refined plan introduces `.backfill-state.json` to explicitly track successfully processed issue IDs, ensuring idempotent and reliable carry-forward across interrupted runs.
3. **Dual-mode tie-break (Resolving conflicts):** What happens if multiple GitHub issues map to the same `WRK-NNN`, or a `WRK-NNN` already has a conflicting `github_issue_ref`? The script needs a strict tie-breaking rule. The refined plan dictates: warn and skip on duplicate issue mappings, and safely merge or preserve existing local file state rather than blindly overwriting.
4. **Test coverage:** The original draft had zero automated tests (relying purely on manual spot-checks). Given the massive surface area (touching potentially 1,200+ local files and firing 2,500+ API calls), the refined plan mandates automated unit tests for the regex extraction and YAML mutation logic to ensure safety prior to bulk execution.
5. **Nightly cron risks:** If this backfill ever transitions to a headless cron job, it introduces severe reliability risks: git merge conflicts (modifying WRK files while developers are actively editing them locally), `gh` CLI token expiration, file lock races, and exhausting the hourly API quota at 3 AM. The script must either run in a strictly isolated CI branch or enforce `git status --porcelain` safeguards to avoid corrupting active user workspaces.
