# Offline workflow readiness assessment

The preflight resolves references in the existing discovery manifest and reports
metadata prerequisites before a consumer attempts a workflow. It does not run an
engine. A declared workflow, command or result cannot establish live readiness.

## Revision history

| Revision | Date | Change and reason |
| --- | --- | --- |
| Initial | 2026-10-22 | Add reference resolution, declaration checks and a worked example to expose gaps before runtime integration. |

## Scope and method

This implements three local slices of initiative #3603:

1. Resolve pinned identities and unpinned routing references. Reject duplicate
   identities, inconsistent counts, unsupported format versions and an index
   inconsistent with its workflow rows.
2. Assess stable status, explicit license and offline declarations, input and
   invocation declarations, result kind and registry provenance syntax.
3. Produce JSON or self-contained HTML from a read-only command, with a synthetic
   example and tests. No package engine, solver or assistant is imported or run.

The source is the existing manifest, not a second channel or workflow registry.
All versions are assessed by default. Repeated `--ref` options select specific
references; aliases resolving to the same identity are counted once. Output is
sorted by identity and contains fixed diagnostics rather than source commands,
input locators, titles, descriptors or arbitrary warnings. Identities are retained
for traceability; the report is not a publication sanitizer for restricted names.

The consumer validates identity and selection invariants. It does not replace
the complete discovery JSON Schema validator. JSON loading rejects duplicate
keys and non-finite numbers, including exponent overflow. Filesystem errors do
not echo source paths. Input declarations must be repository-relative locators;
they are never opened, and invocation templates are never rendered or executed.
Passing the invocation check says nothing about shell safety.

## Worked example: inputs, method and answer

[The example manifest](examples/workflow-readiness.json) is synthetic. `sample`
is not an installed engine, the input file and output artifact do not exist, and
the repeated-letter digest is a syntax fixture, not an observed content hash.
The format and registry versions follow the existing manifest/schema contract;
all other example values are explicit synthetic inputs, not engineering data.

The inputs contain two versions of `sample:screen`: stable version 1 with
`latest: true`, and experimental version 2. The stored index points to version 1.
Selection proceeds by the existing rule: flagged stable, otherwise highest
stable, otherwise highest available. Thus the unpinned reference selects version
1 despite the higher experimental version.

```bash
uv run --no-project python scripts/workflow/workflow_readiness.py \
  docs/registry/examples/workflow-readiness.json --ref sample:screen

uv run --no-project python scripts/workflow/workflow_readiness.py \
  docs/registry/examples/workflow-readiness.json --ref sample:screen --format html
```

Both commands write to standard output and create no files. Redirect output to
a caller-selected scratch location if an artifact is needed.

The answer for the selected stable version, counted directly from the checks:

| Check | Expected status | Independent basis |
| --- | --- | --- |
| Stable version | PASS | The selected fixture row declares `stable`. |
| License policy | PASS | Runtime is `offline` and `license_gated` is explicitly false. |
| Offline runtime | PASS | The fixture explicitly declares `offline`. |
| Input declared | PASS | The fixture supplies a relative locator without traversal. |
| Invocation declared | PASS | Its only replacement field is `{input}`. |
| Result declared | PASS | A `files` result kind is present. |
| Registry provenance | PASS | Status is `ok` and digest text has the declared SHA-256 syntax. |
| Registry freshness | NOT_EVALUATED | Live source bytes were not compared. |
| Live access | NOT_EVALUATED | No scope, privacy, quota or access check was performed. |
| Runtime execution | NOT_EVALUATED | No workflow ran. |
| Artifact delivery | NOT_EVALUATED | No artifact was created, checked or delivered. |
| Engineering basis | NOT_EVALUATED | No workflow-specific sources, units or criteria were reviewed. |

There are seven passing declarations and five unevaluated checks. The result is
`NOT_EVALUATED`, with one assessed workflow, zero blocked and one unevaluated.
Assessing the entire fixture adds the experimental version: two workflows, one
blocked and one unevaluated, with overall status `BLOCKED`. These are row counts,
not numerical acceptance limits or engineering calculations.

## Status and exit codes

`PASS` applies only to the named declaration check. An explicit invalid
prerequisite yields `FAIL`; any such check makes that workflow `BLOCKED`.
Missing live evidence remains `NOT_EVALUATED`. A missing result descriptor or
provenance record is unevaluated; a present but unsupported result kind fails.
Only result kind is checked, not descriptor completeness or artifact existence.
Licensed execution is blocked, regardless of a contradictory false license flag.
Unknown runtime labels are not inferred to mean offline. A network-required flag
does not independently imply a license requirement.

The CLI returns zero when no declaration is blocked, one when at least one is
blocked, and two for invalid input or an unresolved reference. Zero is not a
deployment or launch approval. An empty manifest also remains unevaluated.
No overall `READY` or live `PASS` outcome is produced by this tool.

## Sources and verification

- [Registry contract](README.md), “How consumers read it” and “Field-set”:
  reference identities, version selection, license semantics, input-only
  substitution and result kinds.
- [Discovery schema](workflow-manifest.schema.json): format and field types.
- [Existing generator](../../scripts/workflow/generate_workflow_manifest.py),
  `MANIFEST_VERSION` and `latest_by_routing_id`: producer compatibility.
- [Data handling contract](../architecture/agent-data-handling-contract.md),
  “Descriptor v1 and qualification”: metadata presence cannot prove access,
  source rights, digest agreement, units or intended-use eligibility.

No engineering equation, coefficient or acceptance threshold is introduced.
Expected values in the tests come from selection by inspection and independently
counted fixture rows. Tests cover malformed identities and JSON, stale index
selection, license declarations, input traversal, absent evidence, escaped HTML,
CLI results, no external access during assessment and schema conformance of the
example. The existing generator tests establish compatibility with its contract.

## Known limits and later slices

The full initiative remains open. Runtime API integration, operational channel
ownership and onboarding, scoped credentials, live privacy and quota validation,
artifact integrity and publication, public-tier hardening, domain-specific
engineering validation and end-to-end channel tests belong to later work in
their authoritative repositories. This preflight supplies discovery diagnostics;
it grants no access and changes no operational configuration.
