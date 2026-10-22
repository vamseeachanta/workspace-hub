# Scanner exemption contract

Scanner exemptions shall remain bound to their original exact rule category,
restricted paths and line structure. An exemption for a retired category shall
not transfer to a retained category. This design rule addresses issue #3938
(2026) and the category-migration defect recorded during issue #3936.

## Revision history

| Revision | Date | Change and reason |
| --- | --- | --- |
| Initial | 2026-10-22 | Define category-bound exemptions and reusable regression probes to prevent accidental migration. |

## Binding rule

For a finding, suppression shall require the conjunction:

```text
suppress = known_context AND exact_category AND exact_path
           AND same_line_marker AND eligible_line_structure
```

This is a Boolean specification derived from issue #3938, not an empirical
equation. There are no numerical coefficients or engineering acceptance limits.
Each term shall be established independently. A marker, file name, successful
scan or empty finding set alone shall not establish eligibility.

- Context and category names shall match exactly. Unknown or retired contexts
  and categories shall deny suppression. Category aliases and inherited defaults
  shall not enlarge a binding.
- Reviewed policies shall list exact repository-relative paths. If an existing
  scanner requires restricted patterns, its adapter shall test near-miss paths,
  nested paths and traversal spellings explicitly. The shared helper uses exact
  byte membership and performs no path normalization or glob expansion.
- A marker shall occur on the finding's physical line in the required trailing
  comment form. Neighboring markers and longer marker names shall not qualify.
- A language-aware check shall establish the permitted line structure from the
  same content snapshot used for finding detection. Parse failure shall deny
  suppression. Executable statements shall not borrow an adjacent literal's
  exemption.
- Suppression shall apply to the individual rule finding. A matching exemption
  shall not skip another category on the same line or another line in the file.

The shared implementation is
[`scanner_exemptions.py`](../../scripts/enforcement/scanner_exemptions.py).
Its `structure_matches` argument is a trusted adapter result; the helper cannot
establish language semantics, content provenance or review authorization itself.
Only the Boolean value `True` qualifies. Policies belong in reviewed source,
outside scanner-input configuration. An empty policy collection denies all
suppression.

## Migration review

Before changing scanner categories, list the old and proposed bindings and the
findings each suppresses. Removing a rule shall remove its exemptions or leave
them inert. Adding a rule shall not derive exemptions from the new rule set,
reuse an old context as a catch-all, or change an identifier exemption into a
secret-assignment exemption.

A category, path or structural expansion shall fail the existing contract tests
until an explicit review accepts the changed policy and its independent expected
cases. A review shall examine both the policy change and the changed oracle;
updating both without review does not establish authorization. No runtime flag,
review string, local receipt or caller-supplied approval enables migration.
Repository access controls and review provide that boundary.

Review mixed migrations for threat-model inversion: a change intended to remove
an identifier restriction shall not suppress a retained security rule. Preserve
independent secret handling, source rights and access controls. This contract
does not restore retired identifier scanners or register new callers for them.

## Reusable contract tests

[`assert_exemption_contract`](../../scripts/testing/scanner_exemption_contract.py)
accepts an adapter and independently authored synthetic probes. The adapter shall
return whether a particular finding was suppressed. It shall not infer exemption
from an exit code, an unscanned path, or a category that has no matching rule.

The required inputs are a positive case, another active category matching the
same line, disallowed but scanned paths, and invalid bodies that still trigger
the original rule. Include missing and adjacent markers, executable lookalikes,
and a second unmarked finding. The harness also probes unknown contexts and
invalid physical line numbers. Assertion messages identify only the boundary;
they do not include scanned content.

The expected outcomes shall remain independent of the production policy.
Copying the current allowlist into test expectations at runtime would accept
the very migration that these tests must reject. Tests of the harness itself
shall demonstrate failure for deliberately broken adapters, including
always-allow, always-deny, category-ignoring and path-ignoring behavior.

## Worked example

Input: the scheduler scanner reads an exact reviewed checker path and this
synthetic line:

```python
PATTERN = "crontab -"  # scheduler-mutation-forensic
```

The method evaluates each binding term separately. For `crontab-replace`, the
context is known, the original category and path match, the marker is on the
same line, and the AST identifies a standalone literal assignment. All terms
are true, so that scheduler finding is suppressed.

For an additional matching category named `other-category`, the category term
is false. Its finding remains visible even though the other terms are true.
The following hand-derived cases are executable tests in
[`test_scheduler_exemption_categories.py`](../../tests/enforcement/test_scheduler_exemption_categories.py).

| Changed input | Failed term | Answer |
| --- | --- | --- |
| None, original category | None | Suppress the original finding |
| Additional matching category | Exact category | Report the new-category finding |
| Literal moved to a production script | Exact path | Report the scheduler finding |
| Marker moved to the preceding line | Same-line marker | Report the scheduler finding |
| A function call follows the literal on the same line | Eligible line structure | Report the scheduler finding |
| Unmarked executable finding added on the next line | Same-line marker and eligible structure | Report the additional finding |

The scheduler's bindings enumerate its original categories explicitly rather than
deriving them from its detection table. Its AST check permits literal assignments
to simple names; calls, computed values, attribute assignments, evaluated complex
annotations and same-line executable neighbors do not qualify. This is a source
shape check, not a general proof that arbitrary Python code is inert.

## Verification and limits

Run the focused suites with `pytest` and `PyYAML` available:

```sh
uv run --no-project --with pytest --with pyyaml python -m pytest \
  tests/enforcement/test_scanner_exemptions.py \
  tests/enforcement/test_scheduler_exemption_categories.py \
  tests/enforcement/test_scheduler_mutation_surfaces.py \
  tests/enforcement/test_scheduler_mutation_hardening.py \
  tests/enforcement/test_scheduler_mutation_delivery.py \
  tests/enforcement/test_scheduler_mutation_task3.py \
  -q -rA -p no:cacheprovider
```

The scheduler integration proves this consumer's boundary. Other scanners require
their own adapters, positive controls and negative probes before adoption. This
change does not claim a repository-wide scanner migration or authenticate an
external review.

## Sources

- Issue #3938 (2026), “Guard scanner exemptions against rule-category migration”:
  exact-category, restricted-path and line-structure requirements.
- Issue #3936 (2026), identifier-scanner retirement: retained security and
  publication controls remain independent of identifier retirement.
- Existing scheduler scanner and its source attestations: the restricted forensic
  paths, original scheduler categories and AST-based literal context extended here.
  Test expectations are the Boolean calculation above, not scanner output.
