### Verdict: REQUEST_CHANGES

### Summary
WRK-5140 partially implements the migration from next-id.sh to gh-next-id.sh, but critically omits archive collision detection (acceptance criteria #3 and #4). GitHub issues in the ~1300 range will collide with existing archived WRK IDs (WRK-1200, WRK-1202, WRK-1254, etc.), silently creating duplicate WRK/GH ID pairs — the exact problem this ticket was opened to solve.

### Issues Found
- [P1] Critical: scripts/work-queue/gh-next-id.sh — No archive collision check. AC #3 requires gh-next-id.sh to check for existing WRK IDs before returning. AC #4 requires a hook/guard that blocks WRK creation if the GH issue number collides with an archived WRK. Neither is implemented. The script blindly returns the GitHub issue number without scanning pending/, working/, or archived/ directories. Since GH issues are in the ~1300 range and archived WRK items exist at WRK-1200..WRK-1263, collisions are imminent — not theoretical.
- [P1] Critical: scripts/work-queue/gh-next-id.sh:100 — _try_github() suppresses gh stderr (2>/dev/null) during issue creation. If `gh issue create` fails mid-flight (e.g., rate limit, network timeout after issue is created but before URL is captured), the script falls through to _offline_fallback and creates a LOCAL ID — but the GitHub issue has already been created, leaving an orphaned issue with no corresponding WRK item. This is a data integrity issue with no recovery path.
- [P1] Critical: scripts/work-queue/gh-next-id.sh — file mode 100644 in git index (not executable). The next-id.sh delegation checks `[[ -x "$GH_NEXT_ID" ]]` which will fail when gh-next-id.sh is checked out without execute permission, silently falling through to legacy behavior and defeating the entire migration.

### Suggestions
- Add a collision check in gh-next-id.sh after extracting issue_number: scan archived/, pending/, working/ directories for WRK-{issue_number}.md. If found, close the just-created GH issue as 'duplicate/collision' and retry by creating another issue (or error out with a clear message).
- Set file mode to 755 on gh-next-id.sh: `git update-index --chmod=+x scripts/work-queue/gh-next-id.sh`
- Do not suppress stderr on `gh issue create` — at minimum, capture it to a variable for diagnostic logging on failure. Consider checking for partial creation (issue exists but URL wasn't captured) before falling back to offline.

### Questions for Author
- What is the plan for AC #3 and #4 (archive collision resolution)? Is this intentionally deferred to a follow-up, or was it missed? The ticket description specifically calls this out as a core problem.
- How many GitHub issues currently exist in the workspace-hub repo? If the next issue number is in the 1300s, collisions with archived WRK-1200..1263 items are immediate.
