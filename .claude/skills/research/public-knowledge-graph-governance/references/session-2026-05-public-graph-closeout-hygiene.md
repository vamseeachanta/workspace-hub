# Session note — public graph closeout hygiene

## Context

During llm-wiki public graph manifest work, implementation fixes and targeted validation were green, but closeout was still unsafe because the working tree mixed generated artifacts, dated reports, and staged/unstaged states.

The durable lesson is the artifact closeout pattern, not the specific issue or commit.

## Failure shape observed

- Generated artifact files had `AM` status: staged as new/modified while also changed unstaged.
- Two dated report files existed simultaneously.
- The validator had been run against the newer report path, while a different dated report was staged.
- Transient adversarial review output lived under a scratch planning directory and should not be committed by default.

## Closeout pattern

Before committing tracked public graph artifacts:

1. Choose the final report path/date first.
2. Regenerate artifacts and report once against the current corpus.
3. Run the artifact validator against the exact artifact directory and exact report path intended for commit.
4. Normalize staging after validation: reset/re-stage final files or `git add` the exact intended artifact/report/schema/script/test set.
5. Exclude scratch review/log directories unless the repo explicitly tracks them.
6. Re-run the validator after staging normalization if there was any report-path or artifact regeneration drift.
7. Only then run final full tests, legal scan, adversarial review, commit, push, and issue closeout.

## Red flags

- `AM` on generated artifacts after validation.
- Validator command references a report that is still untracked.
- Summary `run_date`, report heading, report filename, and validator command disagree.
- Review artifacts from a stale MAJOR review are present next to final artifacts and may be accidentally committed.
