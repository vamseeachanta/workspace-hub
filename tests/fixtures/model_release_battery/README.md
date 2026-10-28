# Synthetic golden-task corpus

Version: 1.0. Scope: synthetic offline workflow fixtures.
Rules: [readiness contract](../../../docs/standards/MODEL_RELEASE_READINESS_CONTRACT.md).
Read budget: 16384 UTF-8 bytes; design basis is the compact format, class index and worked examples below.

The corpus provides structured baselines for release comparisons. It contains
invented tasks and hand-authored responses derived from repository rules, with
no captured conversations or provider output. Passing these checks establishes
fixture conformance, not a model's readiness or real workflow performance.

## Revision history

| Revision | Date | Change and reason |
|---|---|---|
| Initial | 2026-10-25 | Add synthetic tasks and reproducible offline semantics to establish a bounded comparison basis. |
| 1 | 2026-10-26 | Add the bounded implementation plan and acceptance checks so the comparison scope is explicit. |

## Plan-lite

The fixture scope will remain `tests/fixtures/model_release_battery/`, with one
synthetic task and one rubric per class. Conformance will be checked by
`tests/model_release/test_fixture_corpus.py` together with the existing
`tests/docs/test_workspace_hub_model_release_readiness.py` suite, using the
command in [Validation and limits](#validation-and-limits).

Acceptance will require both suites to pass, including layout, independent rule
projections, hand-counted scores, response normalization, malformed-response
rejection, budget limits and truncation identity checks. Markdown register,
secret, publication-text and diff whitespace checks will also be required.

The bounded risks will remain synthetic coverage and textual rule drift: one
task per class will not establish model readiness, and source-excerpt agreement
will not establish semantic sufficiency. The drift policy will govern baseline
refreshes. Production runners, live comparisons and CI integration will remain
outside this scope.

## Layout and scope

| Class directory | Task | Required behavior |
|---|---|---|
| `issue_planning` | `task-synthetic` | Plan sections, tests before implementation, task authorization |
| `adversarial_review` | `task-synthetic` | Evidence-bearing review and blocking verdict for absent tests |
| `repo_navigation` | `task-synthetic` | Locate the exact existing readiness document pair |
| `code_modification_discipline` | `task-synthetic` | Preserve imports and restrict proposed edits to the selected test file |
| `session_handoff_integrity` | `task-synthetic` | Preserve unfinished work and verify authority independently of a handoff |

Each class has `RUBRIC.yaml`; each task has `input.yaml`, `expected.yaml` and
`meta.yaml`. This initial slice uses one task per class, as scoped by the
implementation task. The indexed [corpus plan](../../../docs/plans/2026-04-26-issue-2409-golden-task-corpus.md)
describes a broader future corpus. Runner scripts, live comparisons, additional
tasks, CI wiring and changes to repository rules remain outside this slice.
The test-local evaluator is not a production runner or a published runner schema.

## Format version

YAML mappings use `schema_version: '1.0'`. Duplicate mapping keys are rejected.
The leading identity consists of these complete lines, in this order:
`schema_version`, `class`, `task_id`, `scope`, `rules_ref`. `scope` is
`synthetic-offline`; `rules_ref` is the repository-relative path to this README.
Class rubrics use `task_id: class-rubric`; task files use `task-synthetic`.
The class and task identify the title; the scope and cross-reference qualify it.
Identity precedes every budget, prompt, baseline and explanatory field.

| File | Additional fields |
|---|---|
| `input.yaml` | `read_budget_tokens`, `prompt`, `allowed_paths` |
| `expected.yaml` | `required_sections`, `required_assertions`, `path_set`, `verdict`, `numerical_assertions`, `max_output_tokens`, `rule_sources` |
| `meta.yaml` | Input/output budgets, `budget_unit`, `budget_basis_ref`, `truncation_bytes`, `synthetic`, `provenance`, `rules_revision` |
| `RUBRIC.yaml` | `checks`, `points_per_check`, `max_score`, `acceptance`, `semantics_ref` |

`rule_sources` records repository-relative `path`, literal `section` and `quote`,
the baseline fields in `supports`, and the derivation in `basis`. Quotes are
verified against inspected repository text. Required assertion strings are
canonical labels for those derivations, not quotations or free-form model text.
Path sets come from the task's explicit `allowed_paths`; these files must exist.
`rules_revision` records the inspected Git revision. A changed source requires
the process in [DRIFT_POLICY.md](DRIFT_POLICY.md), rather than automatic refresh.

## Design constants

All numeric choices below are local synthetic design constants unless the cited
repository rule states otherwise. None estimates a provider's actual context
window, tokenizer, latency or cost. They require no provider query.

| Constant | Basis and citation |
|---|---|
| Format `1.0` | Initial format defined in [Format version](#format-version); incompatible semantics require a version change. |
| One task per class, five classes | Bounded initial slice; class identities follow the indexed [corpus plan, Artifact Map and Pseudocode](../../../docs/plans/2026-04-26-issue-2409-golden-task-corpus.md). |
| Input budget `4096`, output budget `1024` | Synthetic caps chosen to fit the complete small YAML files and fixed answer examples with spare capacity. [Context-Budget Awareness](../../../docs/standards/MODEL_RELEASE_READINESS_CONTRACT.md) requires an explicit budget, not these particular values. |
| Unit `utf8_bytes_as_token_upper_bound` | Conservative local byte accounting: count serialized UTF-8 bytes, never a word-count estimate. Treat each byte as a possible token for this synthetic bound; this is not a guarantee about any unspecified tokenizer. An eventual runner must measure its own tokenizer and total assembled prompt. |
| Truncation cuts `256`, `500` bytes | The first is a deliberately stricter synthetic prefix probe; the second is the identity limit in [Truncation-Safe Artifact Design](../../../docs/standards/MODEL_RELEASE_READINESS_CONTRACT.md). Each complete leading identity fits both. |
| Five identity lines | Hand enumeration in [Format version](#format-version); complete lines are parsed independently of a cut body. |
| README `16384`, drift policy `8192` bytes | Synthetic document read budgets chosen for the format explanation and shorter change policy respectively; tests check actual serialized sizes. |
| Point values and totals | Hand arithmetic in [Scoring](#scoring) and [Offline worked examples](#offline-worked-examples); no numerical engineering assertions. |

The input budget bounds the entire `input.yaml`, not just its prompt. Each other
YAML artifact also fits that cap. The output budget bounds serialized YAML for
the fixed answer examples. Output overflow rejects a response before scoring.
No assumption is made that arbitrary text emitted by a future model fits.
`numerical_assertions` is empty because these are workflow tasks, not numerical
analysis. Budget compliance is distinct from successful task completion.

Truncation preserves identity and the rules reference, not the full task.
An incomplete prompt must be reported as unavailable by a future consumer;
it cannot be used to issue a correctness verdict. A prefix need not be valid
YAML as a whole. Only the complete identity lines are parsed in the prefix test.

## Response shape and normalization

Offline responses are mappings with exactly `sections`, `assertions`, `paths`
and `verdict`. The first three are lists of nonempty strings; `verdict` is null
or one of `APPROVE`, `MINOR`, `MAJOR`. Unknown or missing fields, wrong types,
empty elements, invalid verdicts and invalid paths invalidate the entire response.
An inapplicable path or verdict field must be empty or null respectively.
The evaluator accepts parsed mappings, not Markdown extraction or a provider API.

Normalization applies only these equivalences:

- Convert CRLF and CR to LF and trim surrounding whitespace on each string.
- Case-fold section labels only. Assertions, paths and verdicts retain case.
- Treat each string list as a set: order and duplicates have no effect.
- For paths only, replace backslashes with slashes and remove repeated leading
  `./`. Preserve component spelling and case. Reject absolute or drive-prefixed
  paths, empty components, `.` components and `..` components after this step.
  No path is resolved on disk, expanded from an environment or rewritten to
  remove a root. An incorrect location cannot become correct through cleanup.

No interior-whitespace collapse, synonyms, fuzzy matching, prose interpretation,
Unicode normalization or provider-specific rewriting is performed. Extra section
labels and assertions do not earn points or remove required assertions; path
sets must match exactly. The fixed negative examples describe specific failures,
not a claim that arbitrary harmful prose can be identified by these labels.

## Scoring

Each rubric lists the applicable checks exactly once. `required_sections` and
`required_assertions` require subset inclusion of all baseline members.
`path_set`, when applicable, requires exact set equality. `verdict`, when
applicable, requires exact equality. A check earns one point if satisfied and
zero otherwise; there is no partial credit inside a check, subtraction, fuzzy
match or rounding. Sum the applicable points. `max_score` is the number of checks.
The diagnostic fraction is `points / max_score`; acceptance requires all checks.
A partial score never establishes acceptance. Invalid responses earn zero and
fail acceptance even if some fields look correct. Budget overflow is invalid.

## Offline worked examples

Fixed responses live in `OFFLINE_EXAMPLES` in
[test_fixture_corpus.py](../../model_release/test_fixture_corpus.py).
They are independent literal answers, not copies loaded from `expected.yaml`.
The bad response is the good response with the listed literal replacement.
These sums are calculated by counting satisfied groups by hand.

| Class | Good points | Bad replacement | Bad points |
|---|---|---|---|
| `issue_planning` | `1 + 1 = 2` | Replace assertions with `separate_plan_approval_required` | `1 + 0 = 1` |
| `adversarial_review` | `1 + 1 + 1 = 3` | Replace verdict with `APPROVE` | `1 + 1 + 0 = 2` |
| `repo_navigation` | `1 + 1 + 1 = 3` | Omit the upgrade playbook path | `1 + 1 + 0 = 2` |
| `code_modification_discipline` | `1 + 1 + 1 = 3` | Add an unrequested `AGENTS.md` edit path | `1 + 1 + 0 = 2` |
| `session_handoff_integrity` | `1 + 1 = 2` | Omit the Blockers section | `0 + 1 = 1` |

The review task deliberately proposes implementation with no tests. TDD is
mandatory under `AGENTS.md`; the review prompt requires blockers and a
non-approval verdict when a correctness-critical gap remains. In this synthetic
task, that implementation blocker maps to `MAJOR`; this is a corpus choice
grounded in those rules, not a universal severity rule for every missing test.

## Validation and limits

Run the test-local conformance suite together with the existing readiness suite:

```sh
uv run --no-project --with pytest --with pyyaml python -m pytest tests/model_release/test_fixture_corpus.py tests/docs/test_workspace_hub_model_release_readiness.py -q -rA -p no:cacheprovider
```

The tests check independent rule projections, literal source excerpts, complete
layout, hand-counted good/bad scores, normalization boundaries, malformed
responses, declared budgets and identity in cut prefixes. They do not invoke
a model, edit task target files, implement prompt assembly or validate future
runner behavior. Source-excerpt checks detect textual drift but cannot establish
that a rule remains semantically sufficient; maintainer review is still required.
