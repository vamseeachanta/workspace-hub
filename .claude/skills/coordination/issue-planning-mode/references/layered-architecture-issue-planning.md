# Layered Architecture Issue Planning

Use this reference when a user asks to create or harden GitHub feature/issues for architecture that spans data, execution, and report/publication layers.

## Recommended issue shape

Create or maintain a parent issue/plan plus child layer issues/plans:

- Parent architecture issue: owns the lifecycle contract, cross-layer crosswalk, shared terminology, promotion gates, and dependency rules.
- Data-layer child: raw sources, readable raw/private staging, llm-wiki-private/raw, public llm-wiki promotion eligibility, source registry, path classes, sensitivity, citation/source-class separation.
- Execution-layer child: input manifests, tool/code execution, compute/provider routing, command manifests, run evidence, provider-agent prompts, environment manifests. It references data-layer source truth rather than owning data-at-rest classification.
- Report-layer child: raw outputs, client-facing HTML, limited PDFs, chatbot surfaces, evidence bundles, claim binding, output residency, publication/promotion decisions.

The key contract is: interrelated but separable. Children may run in parallel only if they consume the parent crosswalk and do not redefine the upstream/downstream interface.

## Data-routing guardrails

- Model routing levels distinctly: raw-data, readable-raw-data, llm-wiki-private/raw-staging, llm-wiki-public.
- Private/client raw or readable data cannot route directly into a public llm-wiki.
- Sanitized derivatives require explicit promotion gates and source-class/citation separation.
- Use neutral codes such as D-L1/D-L2, E-L1, R-L1 in public-tracked docs when raw paths or client mappings might leak sensitive structure.
- Do not assume a private llm-wiki raw/staging source has a public-repo home.

## Review-hardening checklist

Before posting a plan-review update, verify:

1. The parent plan explicitly says the layer plans are interrelated but separable.
2. Child plans name what they own and what they only reference.
3. Data-layer rows use explicit source-registry semantics, for example `source_registry_kind` plus `registry_ref`, with fail-closed handling when a registry ref is unavailable.
4. No data source or report output is chatbot-eligible by default.
5. Ambiguous report artifacts fail closed to internal evidence until ownership and output residency are recorded.
6. Report-layer claims bind to source manifest, command manifest, validation result, legal scan, checksum, review verdict, output residency, and promotion decision.
7. Review evidence cites revision-stamped, non-empty artifacts rather than mutable paths that can be truncated or overwritten in the same run.
8. README/index status remains conservative (`plan-review` or `plan-review-blocked`) until fresh adversarial review clears MAJOR findings and the user approves.

## GitHub update pattern

When patching plan artifacts after review drift, post a concise parent-issue update with:

- patched plan paths
- local validation commands/results
- unresolved blocker/gate
- next review action

Do not ask the user to approve while the plan remains blocked by fresh or unresolved MAJOR review findings.
