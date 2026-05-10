# Exit Handoff Closeout Checklist

Use when the user asks to "document and prepare to exit" or an equivalent closeout request.

## Required sequence

1. Create or update a concise durable handoff, usually under `docs/session-handoffs/` unless a task-specific docs location is more appropriate.
2. Include live repo-state evidence for every touched tier-1 repo:
   - branch name
   - `HEAD` commit
   - `origin/<branch>` commit
   - ahead/behind count
   - dirty/untracked count
   - intentional dirty exceptions, if any
3. Commit and push the handoff in the same closeout window unless an explicit blocker prevents it.
4. After push, re-fetch and prove `HEAD == origin/<branch>` or document the exact push blocker.
5. Inspect hook-generated or concurrently generated dirt before claiming clean state.
6. State external-action status explicitly: e.g. "No external send/action performed" unless the user approved one.
7. Report branch/worktree disposition: removed, preserved with reason, or blocked with evidence.

## If push emits a ref-lock/race warning

Do not assume failure from the warning alone. Immediately run a fetch/status check and compare local `HEAD` to `origin/<branch>`. If they match and ahead/behind is `0/0`, report the warning as a benign ref-lock race with verification evidence.

## If concurrent writers advance `origin/main`

Closeout proof must be based on the final live repository state, not only on the handoff commit you just pushed. After committing/pushing the handoff, run one last fetch/status pass. If a concurrent commit now sits above the handoff commit, report both facts explicitly:

- the handoff commit(s) that contain the closeout artifact; and
- the current local/origin `HEAD` that proves the repository is synced after the concurrent update.

Do not imply the handoff commit is still tip when a later synced commit is present. Keep dirty-state exceptions tied to the latest status probe.

## Dirty-state wording

Use precise language:

- Good: "Repo is not clean: 19 unrelated dirty paths remain; not staged by this handoff."
- Good: "Nested repo `llm-wiki` has ongoing untracked standards-page ingest dirt; preserved intentionally."
- Bad: "Clean enough" or "mostly clean" without counts and paths/classes.

## Interaction with comprehensive learning

Do not run the heavyweight learning pipeline during normal exit closeout. If the user explicitly asks to update the skill library, perform a targeted skill update with `skill_manage`; that is different from running the full nightly comprehensive-learning pipeline.