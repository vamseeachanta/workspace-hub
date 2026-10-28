# Report CLI argument privacy

## Plan-lite

- Scope: `scripts/workflow/build_session_review.py` will use the shared
  `SafeArgumentParser` with a static program name.
- Privacy criterion: rejected arguments will not appear in either output stream.
  Parser-detected errors will retain usage, a generic diagnostic and exit status 2 before
  policy loading, Git queries, payload writes or rendering.
- Compatibility checks: the existing renderer tests and subprocess regressions
  will verify help, manual payloads, Git-derived payloads and payload emission.
  Help and successful invocations will retain exit status 0.
- Exclusions: the shared parser, sanitization policy, enforcement, workflows and
  other CLIs will remain outside this change.

## Evidence and limits

`tests/workflow/test_build_session_review.py` covers rendering and public-output
sanitization. `tests/workflow/test_build_session_review_cli_privacy.py` covers
parse-error privacy, post-parse side-effect traps and CLI compatibility. Successful
CLI smoke cases replace downstream work; the existing renderer tests exercise
that work separately. Argument exit-status expectations cite Python documentation
in the tests.

The supplied review found no blocking code defect and requested the Plan-lite
section. This document records that bounded contract. The accompanying pull
request comment supplies the section for inclusion in its description; changing
the description remains a maintainer action.
