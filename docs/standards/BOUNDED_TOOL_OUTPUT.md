# Bounded tool output and measured context budgets

## Summary

Select the evidence needed for the next decision before running a command.
Bound inventory output, read focused file ranges, and retain complete validation
logs outside the conversation. Preserve exit status and inspect every result.
The observation in issue #3717, “Measured, not estimated” (2026), identifies tool
output as the larger opportunity; it does not justify deleting repository rules.

## Revision history

| Revision | Date | Change and reason |
|---|---|---|
| Initial | 2026-10-22 | Add bounded-output guidance and reproducible context accounting to distinguish observations from estimates. |

## Command guidance

Choose each range and result count for the question being answered. The counts
in these examples are illustrative display choices, not acceptance limits.

| Operation | Bounded starting point | Follow-up |
|---|---|---|
| Inventory | `rg --files scripts/ai tests/ai \| head -40` | Narrow the directory or filename pattern before expanding. |
| Search | `rg -n --glob '*.py' --max-columns 200 'pattern' scripts/ai \| head -40` | Avoid generated bundles and raw transcripts; select individual matching files. |
| History | `git log -8 --oneline -- path/to/file` | Use `git show <revision>:<file>` for the relevant evidence. |
| GitHub inventory | `gh pr list --limit 10 --json number,title,state` | Fetch one item's required fields rather than every body and comment. |
| File inspection | Read with an offset and limit; shell fallback: `sed -n '40,100p' file` | Do not print a whole large file with `cat`. Expand the range as needed. |
| Validation | Save the complete log in an approved scratch directory; return the exit status and relevant summary. | Read failure sections and retain the log for inspection. |

For a validation command, preserve its status separately from the display step:

```bash
# CHECK_LOG names a task-approved scratch file; no repository output is created.
if validation-command > "$CHECK_LOG" 2>&1; then result=0; else result=$?; fi
tail -40 "$CHECK_LOG"
exit "$result"
```

Do not pipe a test, scanner, or generator directly through `head`: that can stop
the producer early or conceal failure. Inventory previews are deliberately
partial, so an omitted match is not evidence of absence. When completeness
matters, save and inspect the full result. Bound line width as well as line
count for generated JSON or other files with very long lines. Check complete
logs for restricted data before including excerpts in public artifacts.

## What the measurement supports

Issue #3717 reports a context window of 1,000,000 tokens, with harness components
of 5,500, 14,000, 8,800, 7,500 and 314 tokens, messages of 776,200 tokens, and
Bash results of 165,500 tokens **within messages**. These are reported rounded
counts from one observation, not a new measurement or tokenizer guarantee.
The example's `source` field records that basis.

The harness components sum to 36,114 tokens: 3.6% of the window. Bash results
occupy 16.6% of the window, approximately 4.6 times the harness subtotal. The
issue's headline rounds tool output to 17%; this guide uses one decimal place.

The issue describes repo-level context optimisation as a roughly 1% lever.
Treat that as its scoped assessment, not a universal ceiling or measured saving:
the table does not separately measure removable auto-loaded prose. All harness
content together provides a 3.6% theoretical bound in this observation; removing
it is neither a recommendation nor evidence of a productivity improvement.

Do not delete `.claude/rules/` content, split shared instructions, or archive
skills based on file counts or bytes. Registered, loaded tokens and loader
behavior require direct evidence. Issue #3717 reports rules were not auto-loaded
in its observation; issue #2725 documents earlier loader work and differing
observations. Neither establishes current behavior across providers. Re-measure
before making a loading claim. Memory-index and build-banner tidying are optional
follow-up work, with no productivity saving claimed here.

## Offline accounting method

The standard-library CLI consumes an explicit JSON observation and never opens
transcripts, invokes a provider or estimates tokens from bytes. Required fields:

- `source`: nonempty evidence reference; use public wording for public output.
- `window_tokens`: positive integer window capacity from the observation.
- `harness_tokens`: nonempty object of disjoint component names and nonnegative
  integer counts; include only loaded components outside messages.
- `message_tokens`: nonnegative integer total including tool results.
- `tool_output_tokens`: nonnegative integer subset of messages.
- Optional `auto_loaded_prose_tokens`: measured prose subset of the harness.
  Omit it when unavailable; explicit zero means measured absence.

Reject booleans, fractions, negative counts, missing fields, unknown fields and
duplicate JSON keys. Require tool output ≤ messages, harness + messages ≤ window,
and measured prose ≤ harness. These are accounting identities from the nesting
in issue #3717, not empirical acceptance thresholds. Supply a consistent,
nonoverlapping observation; the CLI cannot verify measurement provenance.

With W = window capacity, H = sum of harness components, M = messages,
B = tool output and P = measured removable prose:

- Window share = 100 × count / W (definition of percent).
- Tool-to-harness ratio = B / H; undefined when H is zero (`null` in JSON).
- Accounted tokens = H + M, since B is already within M.
- Unaccounted window capacity = W − H − M; this is not necessarily free space,
  since reserves and unreported categories are not identified by the input.
- Hypothetical prose-deletion bound = 100 × P / W. Without P, report
  `NOT_EVALUATED`; no default 1% saving is inserted.

The category nesting comes from issue #3717 (2026); sums, subtraction and
ratios are arithmetic definitions. No engineering coefficient or licensed
standard is involved. Validate unrounded integer counts before displaying
percentages and ratios to one decimal place. A bound is not a safe deletion
recommendation or an observed performance gain.

## Worked example

Input: [the reported observation](../examples/context-budget.json).

```bash
uv run --no-project python scripts/ai/context_budget.py docs/examples/context-budget.json
```

Independent calculation from the cited issue inputs:

```text
H = 5500 + 14000 + 8800 + 7500 + 314 = 36114
100 × H / 1000000 = 3.6% (displayed)
100 × 165500 / 1000000 = 16.6% (displayed)
165500 / 36114 = 4.6 (displayed)
accounted = 36114 + 776200 = 812314
unaccounted = 1000000 − 812314 = 187686
prose saving = NOT_EVALUATED (no separate prose measurement)
```

The independent synthetic example in `tests/ai/test_context_budget.py` supplies
a measured prose count to demonstrate that optional calculation. Tests also
exercise inconsistent totals, zero denominators and malformed CLI input.
