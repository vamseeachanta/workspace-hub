# Task classifier

Source `task_classifier.sh` and call `classify_task "task description"` for JSON.
The additive `complexity_tier` field follows the keyword groups in issue #121:

- `complex`: architecture, cross-repo, security, design.
- `routine`: format, config, rename, copy, update-doc, scaffold.
- `standard`: no keyword matches, including an empty description.

Matching uses case-insensitive substrings. Complex keywords take precedence
when both groups match. This field is independent of the existing uppercase
`tier`, weighted score, confidence, dimensions and provider scores. Model
selection and consumer wiring remain deferred.

Focused tests: `tests/coordination/test_task_complexity_tier.py`.
