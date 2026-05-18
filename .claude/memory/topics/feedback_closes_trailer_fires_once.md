> Git-tracked snapshot from Claude auto-memory. Captured: 2026-05-18
> Source: /home/vamsee/.claude/projects/-mnt-local-analysis-workspace-hub/memory/feedback_closes_trailer_fires_once.md

---
name: gh "Closes #X, #Y" comma-trailer in single commit body fires only once on direct push
description: When ONE commit body carries multiple comma-joined Closes refs and is pushed directly to main, only the FIRST issue auto-closes. Distinct from the squash-merge case (memory `feedback_cross_repo_closes_at_squash.md`) where N separate commits each with their own Closes ref all fire correctly.
type: feedback
originSessionId: a41b1fe4-c523-4299-a0b6-07faa1e0f409
---
When a SINGLE commit message contains multiple `Closes #NNNN` references joined into one trailer line (e.g., `Closes #X, #Y` or `Closes #X #Y`) and is pushed directly to the default branch (no PR), GitHub auto-closes only the FIRST issue cited.

**Why:** Verified empirically 2026-05-03 during Tier C llm-wiki batch commits. Three batch commits each ended with `Closes #X, #Y` (Batch A: #2587 + #2589; Batch B: #2592 + #2612; Batch C: #2597 + #2602). After push to main, each batch auto-closed exactly the FIRST cited issue: #2587, #2592, #2597 closed; #2589, #2602, #2612 stayed OPEN and required explicit `gh issue close`.

**Distinction from `feedback_cross_repo_closes_at_squash.md`:** That memory covers PR squash-merge of N separate commits, each with its own dedicated `Closes` ref — those all fire because the squash body concatenates the per-commit messages and the scanner sees N independent refs. THIS memory covers ONE commit body carrying N comma-joined refs in a single trailer — the scanner appears to only consume the first.

**How to apply:**

1. **For multi-issue work bundled into one commit on main**: don't trust auto-close. Run a post-push verification loop:
   ```bash
   for n in <each issue cited>; do
     state=$(gh issue view $n --json state --jq '.state')
     [ "$state" = "OPEN" ] && gh issue close $n
   done
   ```
2. **Better pattern (VERIFIED 2026-05-16)**: split into separate `Closes #X` trailers on their own lines — this fires ALL refs reliably on direct push. Instead of `Closes #X, #Y` write:
   ```
   Closes vamseeachanta/llm-wiki#X
   Closes vamseeachanta/llm-wiki#Y
   ```
   Verified 2026-05-16: llm-wiki commit [`b8cb773b`](https://github.com/vamseeachanta/llm-wiki/commit/b8cb773b) had separate-line `Closes vamseeachanta/llm-wiki#93` + `Closes vamseeachanta/llm-wiki#94` trailers; on direct push to main, GitHub closed BOTH issues with closeAt timestamps 1 second apart (22:45:12Z + 22:45:13Z). Sequential processing per trailer line, all fire.
3. **Best pattern (when applicable)**: use the PR squash-merge flow — open one PR with N commits, each with its own `Closes` ref, squash-merge → all fire reliably (the verified-good case).
4. `gh issue comment <n>` works in BOTH OPEN and CLOSED states; only `gh issue close --comment "..."` drops on already-closed issues (per `feedback_gh_issue_close_silent_comment_drop.md`).

**Do NOT apply when:** filing one commit per issue (no comma trailer), using separate-line `Closes` form (each fires independently), or when using the PR squash-merge flow.

**Variant resolution (RESOLVED 2026-05-16):** the previously-untested variant `Closes #X\nCloses #Y` (line-separated, same commit body) **DOES fire all refs** on direct push to main. The rule now narrows to: **comma-joined form fires once; line-separated form fires all**. Sequential processing per trailer line (observed 1-second gap between closeAt timestamps confirms GitHub's webhook pipeline processes each trailer-line as a separate event after the push lands). Preferred pattern for multi-issue commits is now the line-separated form — no post-push verification loop needed.
