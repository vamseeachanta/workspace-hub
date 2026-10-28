# Generate a local-ref commit table

Manual transcription can put a commit ID from one row into another row.
`scripts/workflow/handoff_ref_table.py` resolves every supplied ref independently
and renders full commit IDs in a deterministic Markdown table.

The table records current local refs and conveys no approval. Remote-tracking
refs can be stale. The generator does not fetch, contact a hosting service,
interpret labels, authenticate approval, write Git state or edit handoffs.

## Input and usage

Supply a UTF-8 JSON file containing an explicit list of objects with exactly
`issue` and `ref` keys. Issue numbers are positive integers. The synthetic
example uses issue ordinals in ascending order, starting at one:

```json
[
  {"issue": 1, "ref": "origin/plan/issue-1-example"},
  {"issue": 2, "ref": "origin/plan/issue-2-example"}
]
```

Run from the intended local checkout, or identify it with `--repo`:

```sh
uv run --no-project python scripts/workflow/handoff_ref_table.py refs.json --repo .
```

The Markdown table is written to standard output, sorted by numeric issue number.
Each row shows the supplied ref and its resolved immutable commit ID. Ref text is
escaped so that Markdown or HTML characters cannot add table cells or markup.
Empty input produces the table header. Failure produces a nonzero exit status
and a generic diagnostic on standard error, with no partial table.

## Resolution rules and limits

Named branches, tags and remote-tracking refs already available locally are
accepted, either fully qualified or as unambiguous Git shorthand. Annotated tags
are peeled to commits. Missing refs, ambiguous names, non-commit targets,
revision expressions and pseudorefs such as `HEAD` are refused. Use a named ref
rather than a raw object ID. Invalid input, duplicate JSON keys, repeated issues
and repeated refs are refused, including aliases of the same canonical ref.
Distinct refs may legitimately resolve to the same commit.

Every row receives independent read-only `git rev-parse` calls: one identifies
the canonical ref, and another resolves that ref with `^{commit}`. Arguments are
passed without a shell, after `--end-of-options`. Ambiguity warnings are enabled
explicitly and treated as failures. Full object names support both Git hash
formats. Inherited Git bindings are cleared; replacements, lazy fetching,
optional locks and interactive prompts are disabled for these reads.

Refs are observed sequentially, rather than in an atomic repository snapshot.
A ref may move during or after generation. Each displayed commit is the result
of that row's commit-resolution read; no prior table, adjacent row or approval
marker supplies the ID. The caller remains responsible for the intended
repository, ref freshness and any separate review or approval evidence.

## Verification

```sh
uv run --no-project --with pytest python -m pytest tests/workflow/test_handoff_ref_table.py -q -rA -p no:cacheprovider
```

Fixtures are synthetic, offline and temporary. Injected command responses capture
argv and environment settings without invoking Git or accessing real refs.
Expected row IDs come from independent synthetic ref/ID pairs; expected ordering
comes from the example's issue ordinals.

Git command semantics and object-name lengths follow `git help rev-parse`,
`git help check-ref-format`, `git help git` (environment variables), and
`git help hash-function-transition` (Object names).

Implementation lesson: bind each displayed commit to its own ref read and test
with different IDs so cross-row copying cannot pass unnoticed.
