# /objective <issue#>

Run an objective brief through the coordinator intake path.

## Dry run

```bash
uv run --no-project python -m scripts.coordination.objective --issue <issue#> --dry-run
```

The dry run reads the GitHub issue, extracts the Objective fields, classifies the execution mode per `docs/standards/PARALLEL_FIRST_EXECUTION.md`, and prints lane contracts. It does not write labels, comments, branches, commits, or issues.

## Coordinator duties

- Verify the issue scope, authority, labels, and current state.
- Choose `single-lane`, `parallel-readonly`, or `parallel-worktree`.
- Launch lanes in one batch only after lane contracts exist.
- Own integration, push, PR, issue comments, and closeout.
- Keep TDD, hard-stop policy, data handling, and cross-review gates intact.
