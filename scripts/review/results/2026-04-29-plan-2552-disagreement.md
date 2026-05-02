# Disagreement report — plan #2552 (2026-04-29)

## Verdicts

| Provider | Verdict |
|---|---|
| claude | UNKNOWN |
| codex | UNKNOWN |
| gemini | MAJOR |

## Findings unique to each provider

A finding is 'unique to X' if its text appears in X's artifact but not
verbatim in any other provider's artifact.

### claude

(no findings unique to this provider)

### codex

(no findings unique to this provider)

### gemini

- Plan section §Documents consulted claims `docs/handoffs/github-collaborator-only-lockdown-2026-04-29.md` exists and was consulted. A glob search confirms no such file exists at HEAD in `docs/handoffs/`.
- Plan section §Evidence (embedded verification) explicitly states `EXISTS: docs/handoffs/github-collaborator-only-lockdown-2026-04-29.md`. This is a false assertion; the file is missing from the repository.
- Plan section §Artifact Map asserts the Claude single-author review artifact exists at `docs/plans/overnight-prompts/2026-04-29-next-wave-autofeed/results/nextwave-followup-plan-review-2552-20260429-1246.md` `(EXISTS)`. A recursive search confirms this directory and file do not exist at HEAD, invalidating the claim that a single-author review is complete and recorded on disk.
- Plan section §Files to Change specifies creating the file `tests/security/test_runbook_external_contributor.py`. However, the directory `tests/security/` does not currently exist at HEAD. The plan lacks instructions to create this directory or any necessary `__init__.py` file prior to test creation.

