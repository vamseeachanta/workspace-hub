# Disagreement report — plan #3555 (2026-07-16)

## Verdicts

| Provider | Verdict |
|---|---|
| claude | UNAVAILABLE (claude CLI failed, rc=1: no stderr captured) |
| codex | MAJOR |
| gemini | UNAVAILABLE (gemini CLI failed, rc=1: no non-interactive gemini auth configured (GEMINI_API_KEY/GOOGLE_API_KEY/~/.gemini/oauth_creds.json) ) |

## Findings unique to each provider

A finding is 'unique to X' if its text appears in X's artifact but not
verbatim in any other provider's artifact.

### claude

(no findings unique to this provider)

### codex

- Plan Phase 1 conflicts with the existing `/goal` invocation gate. `docs/plans/2026-07-16-issue-3555-goal-statusline-machine-pilot.md:168` says `SHARED_SOUL.md` will gain a must-fire rule requiring provider-native goal attachment after a substantive task is known, and acceptance line 265 requires substantive Claude/Codex tasks to attach native goals. But `config/agents/SHARED_SOUL.md:59` already requires consulting #2695 before invoking `/goal`, and `.claude/rules/goal-invocation.md:13-24` requires catalog validation, weekly picklist checks, `status:plan-approved`, runner allocation checks, and a post-invocation catalog comment. The plan only says it will “preserve user approval gates” at line 168; it does not specify how the new automatic/substantive-session rule composes with the catalog gate. Implementing the plan as written can force `/goal` on unapproved or catalog-skipped tasks, violating the current rule.
- The Claude Windows statusline path is under-specified for hosts without Git Bash. `docs/plans/2026-07-16-issue-3555-goal-statusline-machine-pilot.md:188` says Claude user settings will point to one installed, home-relative statusline command, and the only planned portability test at line 245 covers “Linux and Git Bash home-relative invocation.” Official Claude statusline docs state that on Windows Claude runs statusline commands through Git Bash when installed, otherwise PowerShell, and that Windows paths need specific handling; the docs show PowerShell invocation via `powershell -NoProfile -File C:/...` and Bash invocation via `~/.claude/statusline.sh`. The plan’s test matrix omits the PowerShell fallback route, so the machine-global statusline can silently fail on Windows machines that lack Git Bash while still satisfying the written tests.
- Phase-0 evidence has no declared durable artifact path. `docs/plans/2026-07-16-issue-3555-goal-statusline-machine-pilot.md:151-161` says implementation will record versions, verify goal/statusline selectors, record accepted identifiers, and store de-identified capability evidence. Acceptance line 273 requires the `ace-win-2` pilot to “publish fresh local evidence.” The Artifact Map at lines 123-136 lists the plan, report, configs, sync scripts, collectors, tests, and review files, but no Phase-0 attestation/evidence output path. Without a named file or schema, reviewers cannot tell whether the empirical attestation was preserved, overwritten, or skipped.

### gemini

(no findings unique to this provider)

