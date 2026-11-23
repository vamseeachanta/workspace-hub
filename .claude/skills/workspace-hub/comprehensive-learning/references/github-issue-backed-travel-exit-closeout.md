# GitHub-issue-backed travel exit closeout

Use this when a travel-planning session is primarily captured as GitHub issues/comments rather than repo files, and the user asks to document/prepare to exit.

## Pattern

1. Treat GitHub issues as the durable task record, but verify them live before writing the handoff:
   - list the relevant issue range or search result with `gh issue list`;
   - verify any important newly added comment with `gh issue view <n> --json comments`;
   - capture clickable issue and comment URLs in the handoff.
2. Write a concise exit handoff under `docs/session-handoffs/` in the control repo when the target issue repository has no local checkout on the host.
3. Explicitly separate action classes:
   - GitHub issue/comment actions performed;
   - no booking/payment/email/calendar/message-send or other external action unless explicitly approved.
4. If the control repo has unrelated dirty state, stage only the handoff. Do not absorb unrelated plan/review/skill/provider dirt just to make exit look clean.
5. Commit/push the handoff, fetch, and prove `HEAD == origin/<branch>` plus ahead/behind `0/0`.
6. If the handoff proof section is updated after the first commit, commit/push/fetch again and make the final user response carry the latest live proof rather than the stale proof embedded in the file.

## Handoff content checklist

- Scope: what travel-planning work was captured.
- External-action status: GitHub-only vs booking/payment/send actions.
- Verified issue links grouped by planning hub and child issues.
- Verified comment links for newly posted planning material.
- Restart guidance: the next issue(s) to open first and booking blockers to verify.
- Control repo proof: host, repo path, branch, local HEAD, origin HEAD, ahead/behind, dirty-count and named unrelated exceptions.

## Pitfall

Do not say “clean exit” when the control repo is synced but still dirty. Use precise wording: “synced to remote; not clean; N unrelated dirty/untracked paths remain; handoff file is clean.”
