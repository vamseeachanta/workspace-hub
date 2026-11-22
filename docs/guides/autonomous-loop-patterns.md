# Autonomous loop patterns

The six architectures requested in issue #1806 differ in how they select the
next action and record progress. This guide compares their stopping and failure
conditions and supplies a bounded, local checkpoint teaching example. It does
not establish a production orchestrator or change operational policy.

## Revision history

| Revision | Date | Change and reason |
|---|---|---|
| Initial | 2026-10-25 | Compare the issue-listed patterns and add a reproducible checkpoint example. |
| 1 | 2026-10-26 | Clarify that the coordinator counter limits successful starts, because failed starts do not increment it. |

## Selection guide

| Architecture | When to use | Main risk |
|---|---|---|
| Sequential pipeline | Known ordered steps with dependent outputs | A failed early step invalidates later work. |
| Checkpoint loop | A verifiable action can be retried within a budget | Retrying an external action can duplicate effects. |
| Recursive decomposition | A large task can be split into smaller bounded tasks | Unbounded expansion or incompatible child outputs. |
| Event-driven loop | Work becomes eligible after a change or test result | Duplicate, stale or out-of-order events. |
| Multi-agent round-robin | Participants take turns refining shared work | Cycling without measurable progress; stale shared state. |
| RFC-driven dependency DAG | Independent work can proceed after dependencies and review decisions | Cycles, failed prerequisites or treating a proposal as authorization. |

The repository paths below were read for this comparison. A related contract or
partial implementation is identified as such; a gap means no complete example
was established in the inspected paths. Historical examples are references,
not instructions to launch their commands or adopt their older policy wording.
Current [authorization policy](../standards/HARD-STOP-POLICY.md) and
[execution rules](../standards/PARALLEL_FIRST_EXECUTION.md) govern actual work.

## Sequential pipeline

- **Input:** an ordered plan, required inputs and acceptance criteria per step.
- **Progress state:** the current step and verified outputs from earlier steps.
- **Stopping condition:** every required output passes its criteria, or a failed
  prerequisite prevents the next step.
- **Failure handling:** stop dependent steps; retain evidence and retry only the
  affected step under its existing authority. Revalidate downstream outputs if
  an earlier input changes.
- **Use case:** a GSD plan with ordered implementation and verification tasks.
  The checked [execute-plan workflow](../../.claude/get-shit-done/workflows/execute-plan.md)
  describes task execution, deviations and verification. It is workflow guidance,
  not evidence that an engine is installed or running.

## Checkpoint loop

- **Input:** an action, an independent verification criterion and a finite attempt
  budget; production work also needs an effect and retry contract.
- **Progress state:** attempted actions, verification results and the last
  accepted checkpoint. A failed attempt is recorded but does not establish success.
- **Stopping condition:** verified success, exhausted attempts, unavailable input
  or a failure that requires escalation.
- **Failure handling:** retry only retryable failures; preserve the failed result.
  Check external effects before replaying a real action. Exhaustion is a reported
  failure, never permission to increase the budget automatically.
- **Use case:** demonstrating execute, verify and retry using the
  [local example](../../examples/workflow/checkpoint_loop.py) below. Its checkpoint
  is an in-memory attempted prefix; durable restart and recovery are gaps.
  The operational [coordinator `run_once`](../../scripts/dispatch/coordinator_loop.py)
  is a related bounded iteration entry point, not this retry algorithm. It limits
  successful starts per invocation and records failed starts. Failed-start
  attempts are not bounded by that counter. It can perform external actions and
  is not invoked by the teaching example.

## Recursive decomposition

- **Input:** a parent objective, a split rule and criteria that define a leaf task.
- **Progress state:** a task tree, child status and evidence used to combine outputs.
- **Stopping condition:** verified leaves satisfy the parent, or depth, task count,
  attempt or resource budgets prevent further expansion.
- **Failure handling:** stop dependent combinations, report the failed child and
  revise the decomposition only within the authorized scope. Bound expansion and
  check interfaces before accepting child results.
- **Use case:** decomposing an implementation into bounded plans with separate
  verification. The [subagent isolation convention](../standards/SUBAGENT_CONTEXT_ISOLATION.md)
  documents centralized delegation and explicitly rejects chains of child agents.
  It is a related decomposition contract, not a recursive runtime. **Gap:** no
  recursive scheduler is established by that convention or the checked dispatch
  code; this guide does not authorize recursive spawning.

## Event-driven loop

- **Input:** typed change or test-result events with source identity and scope.
- **Progress state:** event identity, deduplication record, acknowledged position
  and pending work associated with the affected revision.
- **Stopping condition:** the bounded event batch is acknowledged, shutdown is
  requested, or retry and resource limits require intervention.
- **Failure handling:** reject malformed events; isolate persistent failures;
  deduplicate retries and recheck revision freshness before accepting results.
- **Use case:** reassessing affected files after an edit or test result. The
  checked [event normalizer](../../scripts/governance/consumer_event.py) maps
  synthetic edit events and rejects unsupported or incomplete contexts. It
  performs no scheduling. **Gap:** that module supplies neither a listener nor
  an event queue, acknowledgement store or test-result execution loop.

## Multi-agent round-robin

- **Input:** an ordered participant list, shared artifact and per-turn contract.
- **Progress state:** the current participant, artifact revision, turn history and
  unresolved findings; updates need serialized ownership.
- **Stopping condition:** acceptance criteria pass, a turn budget expires, no
  measurable progress occurs, or an unresolved conflict needs a maintainer.
- **Failure handling:** retain the last verified revision, reject stale updates
  and report unavailable participants. A replacement participant does not inherit
  authority merely by taking the next turn.
- **Use case:** alternating implementation and defect review on a bounded artifact.
  **Gap:** the checked [dispatch directory](../../scripts/dispatch/) establishes
  routing and iteration, not an ordered round-robin shared-state protocol. The
  [review routing policy](../standards/AI_REVIEW_ROUTING_POLICY.md) specifies review
  participants; it is not a round-robin implementation.

## RFC-driven dependency DAG

- **Input:** an acyclic graph of work items, prerequisite evidence and required
  RFC decisions. RFC means request for comments; a reviewed proposal is not action
  authorization.
- **Progress state:** node status, dependency revisions, review decisions and the
  set of nodes whose prerequisites currently pass.
- **Stopping condition:** every required node is verified, or failed dependencies,
  missing decisions, cycles or resource limits leave no eligible work.
- **Failure handling:** detect cycles before scheduling; block dependent nodes on
  failure; invalidate downstream evidence when prerequisites change. Preserve
  independent completed work and escalate missing decisions to maintainers.
- **Use case:** GSD phase plans grouped into dependency waves. The checked
  [execute-phase workflow](../../.claude/get-shit-done/workflows/execute-phase.md)
  describes dependency analysis, wave ordering and result checks. The historical
  [overnight batch guide](../../scripts/dispatch/overnight-2026-05-13/README.md)
  records ordering dependencies, but manual timing does not enforce them.
  **Gap:** neither reference establishes a complete RFC-gated DAG engine. Existing
  authorization and review controls remain the authority for actual execution.

## Worked checkpoint cases

The inputs below are synthetic design fixtures, not measured reliability data.
Their budgets and expected attempts are hand counts of the literal sequences:
success stops after its first occurrence, and each visited literal consumes an
attempt. No expected value is calculated by calling the example.

Run from the repository root with Python. Set `CHECKPOINT_INPUT` to a writable
JSON file in an external temporary directory, and put the indicated array in it
before each command. The tests create these inputs under their temporary root.
Only the input file is read; summaries are written to standard output.

| Case | Input array | Budget | Expected attempts | Result |
|---|---|---|---|---|
| Success | `["success","retry"]` | 3 | 1: the first literal succeeds | `success` |
| Retry then success | `["retry","success","retry"]` | 3 | 2: retry plus success | `success` |
| Exhausted budget | `["retry","retry","success"]` | 2 | 2: both permitted attempts retry | `budget_exhausted` |
| Invalid budget | `["success"]` | 0 | No action; rejected before execution | argument error |

Success command:

```sh
python examples/workflow/checkpoint_loop.py --input "$CHECKPOINT_INPUT" --budget 3
```

Retry then success command:

```sh
python examples/workflow/checkpoint_loop.py --input "$CHECKPOINT_INPUT" --budget 3
```

Exhausted budget command:

```sh
python examples/workflow/checkpoint_loop.py --input "$CHECKPOINT_INPUT" --budget 2
```

Invalid budget command:

```sh
python examples/workflow/checkpoint_loop.py --input "$CHECKPOINT_INPUT" --budget 0
```

The retry case prints exactly this stable JSON line, with sorted keys, compact
separators and a trailing newline:

```json
{"attempts":2,"budget":3,"history":["retry","success"],"status":"success"}
```

### Local CLI contract

The budget is an explicitly supplied positive integer. The complete input must
be a nonempty JSON array containing only `retry` and `success`; even unused
trailing entries are validated before execution. A shorter all-retry sequence
ends with `input_exhausted` rather than inventing more actions. Success on the
last permitted attempt still succeeds. History contains only attempted outcomes.

Exit values are local interface choices: `0` for success, `1` for an unverified
result (`budget_exhausted` or `input_exhausted`), and `2` for invalid arguments or
unreadable or invalid input, reported through argument parsing without a summary.
These values and the zero budget boundary are the numeric contract cited by the
example and tests; they are not engineering coefficients or production defaults.

Run the isolated tests:

```sh
uv run --no-project --with pytest python -m pytest tests/workflow/test_checkpoint_loop_example.py -q -rA -p no:cacheprovider
```

The [tests](../../tests/workflow/test_checkpoint_loop_example.py) independently
enumerate attempts and execute the documented command tokens with temporary
inputs. The example contains no shell execution, network connection, assistant
dispatch or solver invocation and writes no operational state. It loads the
input into memory; its attempt budget does not bound input size. Persistent
checkpoints, external-effect idempotency, concurrency, timeouts and crash recovery
require a separately designed production orchestrator.

## Post-implementation cleanup and review

- [ ] **De-Sloppify:** perform a named cleanup pass after implementation. Remove
  redundant changes, unused code, unsupported claims and accidental outputs;
  retain required behavior, failure evidence and meaningful tests.
- [ ] Compare outputs with independent expectations and rerun affected tests
  after cleanup. Verify that every claimed implementation link resolves.
- [ ] Check budgets, progress signals, termination and non-retryable failures;
  report gaps instead of silently restarting or increasing limits.
- [ ] Inspect the diff for unrelated edits, credentials and restricted data.
  Preserve existing data and explain any retained artifacts.
- [ ] Obtain the required adversarial review and resolve blocking findings under
  the existing [review policy](../standards/AI_REVIEW_ROUTING_POLICY.md).
- [ ] Verify current task authority before consequential actions. Successful
  tests and cleanup do not approve publication or deployment. Run existing hooks
  and gates as required; this checklist supplies no bypass or new approval rule.
