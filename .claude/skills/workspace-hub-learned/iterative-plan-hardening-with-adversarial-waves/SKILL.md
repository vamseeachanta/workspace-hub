---
name: iterative-plan-hardening-with-adversarial-waves
description: Tighten a draft plan through repeated Codex/Gemini adversarial review waves without prematurely advancing it to plan-review.
version: 1.0.0
category: workspace-hub-learned
tags: [planning, adversarial-review, governance, iteration, workspace-hub]
---

# Iterative plan hardening with adversarial waves

Use when a plan survives initial drafting but repeated adversarial review keeps returning MAJOR. Especially useful for detector/contract plans where correctness depends on exact status semantics, source boundaries, scheduler behavior, and output contracts.

## When this fits
- The issue is reopened or preserved for re-file after earlier MAJOR reviews.
- You already have one or more concrete review artifacts from Codex/Gemini.
- The plan is still draft-only and must NOT move to `status:plan-review` yet.
- The productive path is iterative tightening, not implementation.

## Core loop

1. Read the latest review artifacts first.
- Prefer the newest Codex + Gemini files.
- Extract only the current blocker set; do not keep chasing already-fixed historical findings.

2. Patch the plan, not just the summary.
For every blocker, reconcile all affected sections together:
- problem statement
- deliverable
- candidate record shape / contracts
- pseudocode
- scheduled task contract
- TDD test list
- manual verification / approval gate
- acceptance criteria
- adversarial review summary

3. Maintain one authoritative contract per concept.
Reviewers keep finding MAJOR when the same concept is defined differently in multiple sections. Unify these explicitly:
- status enum
- source dedupe policy
- cross-domain coverage policy
- exit code contract
- publication-mode activation
- locking strategy
- field derivation / mapping contract
- output-vs-summary-only behavior

4. Separate surfaces explicitly.
For detector/data plans, distinguish:
- source-side candidate inputs
- coverage-providing artifacts
- reporting/context aids
Do not blur them in one mixed list.

5. Treat MAJOR findings as governance state, not just prose feedback.
- Keep the issue OPEN but draft-only.
- Do not add `status:plan-review` while MAJOR remains.
- Post short GitHub comments summarizing the latest blocker cluster and linking the fresh review artifacts.

6. Rerun review immediately after each patch wave.
Do not leave the plan claiming blockers are fixed without a fresh wave.
Suggested naming pattern:
- `scripts/review/results/YYYY-MM-DD-vN-plan-<issue>-codex.md`
- `scripts/review/results/YYYY-MM-DD-vN-plan-<issue>-gemini.md`

7. Narrow the blocker set deliberately.
A good pass shrinks the blocker cluster. Update the plan’s review summary to reflect the newest live blockers only.

## High-value hardening patterns learned

### A. Status contracts must be single-source-of-truth
If a record/status enum exists, define it once and make every later section conform.
Typical failure mode:
- one section says a record is `gap`
- another says it is `domain-mismatch`
- pseudocode produces both
Fix by stating one canonical enum and whether a condition is:
- a terminal source-record status, or
- a summary-only diagnostic

### B. Summary-only vs YAML-emitted rows must be explicit
For edge cases like:
- wrong-domain wiki match
- duplicate wiki `doc_key`
- unresolved identity
state whether they:
- produce per-domain YAML rows, or
- appear only in `_summary.md`
Do not leave this to inference from pseudocode.

### C. Scheduler contracts need operational safety, not just commands
If the plan includes scheduled publication, explicitly define:
- required-input prechecks
- clean-worktree precondition
- lock model
- publication-mode activation path
- degraded-run publication behavior
- exit codes
- whether logs/write-side artifacts live outside repo cleanliness concerns or are guaranteed gitignored
If multiple machines are listed, say whether they are:
- one publisher + one observer/failover, or
- both publishers
A local `flock` is not a fleet-wide single-publisher guarantee.

Important live finding from #2392:
- shell command structure matters. A command shaped like `... ; rc=$?; git add ...` can still dirty the checkout after a fail-closed run. Gate staging/commit/push behind explicit `rc` checks so failure paths do not mutate repo state.
- if scheduled publication is supposed to be single-publisher, do not describe it that way unless the mechanism is actually cross-machine. A checkout-local lock only prevents same-host concurrency.

### D. Config-driven plans need normative config schema
When the plan references config keys like domain maps or rules, define:
- key names
- precedence order
- collision/tie behavior
- invalid-config behavior
Otherwise reviewers correctly reject the plan as under-specified.

### E. Dedupe policy must specify field fill behavior
If records are deduplicated across multiple sources, define:
- dedupe key
- source precedence order
- whether higher-precedence wins even if empty, or first-non-empty by precedence
- conflict handling for domain/discipline
Without this, the same plan can produce different implementations.

### G. Attested evidence must cover required-input claims
When a plan's approval gate depends on a required file or live repo fact, make sure the fact is either:
- covered by the attested evidence block, or
- moved into an explicit precheck/manual verification step without pretending the plan itself already proves it.

Live finding from #2392:
- reviewers will correctly keep returning MAJOR if a required runtime input like `data/document-index/index.jsonl` is central to the plan but not actually attested in the evidence block.
- remove unneeded live-state claims if they are not attested and not load-bearing. Unverified noise creates avoidable MAJOR findings.

### H. Domain contracts must specify whether one source can map to multiple domains
For detector/coverage plans, decide explicitly whether:
- one canonical source belongs to exactly one output domain, or
- one canonical source may emit multiple domain-scoped candidates.

Do not dedupe by `doc_key` alone unless the plan also states and justifies a single-domain invariant. Otherwise reviewers will correctly flag silent suppression of real per-domain gaps.
- Post a concise issue comment after each meaningful wave.
- Include the new artifact paths and current blocker cluster.
- Say explicitly whether the issue should remain draft-only.
- Keep the issue open, but do not advance labels prematurely.

## Commit hygiene
For docs-only revision waves:
- commit the plan file plus the new review artifacts together
- use a commit message like:
  - `docs(plans): continue #NNNN adversarial revision wave`
  - `docs(plans): add #NNNN v8 review wave`

## Stop condition
The plan is ready to advance only when:
- latest Codex/Gemini reviews are no worse than MINOR, and
- the blocker cluster is empty or explicitly downgraded, and
- the acceptance/verification sections no longer contradict the pseudocode/contracts.

Until then, keep it draft-only.
