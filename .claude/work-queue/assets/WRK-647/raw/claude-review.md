### Verdict: REQUEST_CHANGES

### Summary
WRK-624 Canonical Workflow Hardening presents a well-structured phased rollout with a solid testing taxonomy and a clear review matrix. However, the compact bundle is explicitly truncated in two critical sections (Phase 2 details and the review matrix body), the dependency contract table required by the acceptance criteria is absent from the reviewed content, and several key elements—Resource Intelligence stage definition, hard-fail cutoff dates for all phases, Route A escalation trigger criteria, and rollback paths beyond Phase 1—are either missing or underspecified for a plan rated critical complexity. These gaps prevent a full approval.

### Issues Found
- Plan is explicitly truncated in two locations ('[truncated for Claude compact bundle]'), making it impossible to fully evaluate Phase 2 scope and the lower half of the review matrix against the acceptance criteria.
- Dependency contract table (required by acceptance criteria: 'names the source of truth and blocking behavior for each gate input') is not present in the reviewed content and may be in a truncated section.
- Hard-fail cutoff date is listed as a required migration matrix field in the acceptance criteria but is absent from the Phase 1 block; Phase 2's migration matrix details are fully truncated.
- Rollback path is only documented for Phase 1. Phase 2 rollback strategy is not visible; for a critical-complexity plan this is a material gap.
- Route A escalation rule ('auto-escalate to 3-model review on risk signals') is not machine-enforceable as written—'risk signals' are never defined.
- The 'Resource Intelligence' stage mentioned in the Executive Summary has no definition, input/output spec, or acceptance criteria anywhere in the reviewed content.
- Acceptance criteria require a Mermaid diagram rendering planning HTML review gates, claim routing gate, and archive gate, but no diagram is present in the bundle.
- Acceptance criteria require an HTML review artifact for this WRK, but no path, reference, or evidence of its existence appears in the reviewed content.
- Plan metadata lists Status as 'implemented' while it is actively being reviewed under Route C; this is either a metadata error or indicates the review is happening post-implementation, which inverts the intended gate order.
- Phase 2 legal scan requirement ('require legal scan on generated artifacts') names no tooling, threshold, or failure criteria, making it unenforceable.

### Suggestions
- Provide the full, untruncated plan for Route C review; a compact proxy is insufficient for a critical-complexity plan requiring three reviewers and phase-level artifacts.
- Add the dependency contract table directly to the plan body (not only in a referenced artifact) so all reviewers can evaluate gate inputs and blocking behavior without external lookups.
- Specify hard-fail cutoff dates and rollback paths for every phase, not just Phase 1, and surface them in a single consolidated migration matrix.
- Define 'risk signals' for Route A escalation as a concrete, machine-checkable list (e.g., presence of MAJOR findings, specific keyword patterns, reviewer disagreement threshold) so the rule can be implemented deterministically.
- Write a self-contained definition of the Resource Intelligence stage: its inputs, outputs, validation criteria, and how failures block downstream stages.
- Resolve the Status metadata: if the plan is implemented, explain why a Route C review is occurring post-implementation and document what remediation actions are available if the review results in REJECT.
- Embed or reference the required Mermaid diagrams and HTML review artifact path within the plan document so validators can confirm their existence without human lookup.
- Add tooling name, version, pass/fail thresholds, and exception-handling procedure for the Phase 2 legal scan requirement.

### Questions for Author
- What content is in the two truncated sections, and why was it omitted from the compact bundle submitted for Route C review?
- What specific conditions constitute 'risk signals' that trigger automatic escalation from Route A to a 3-model review?
- How is the Resource Intelligence stage defined—what are its mandatory inputs, outputs, and gate conditions?
- Why does the plan metadata show Status 'implemented' if this is a pre-execution Route C review gate? Was execution begun before review was completed?
- Where does the dependency contract table live, and can it be included or linked directly in the plan body?
- Which legal scan tool and version will be used in Phase 2, and what is the acceptance threshold for generated artifacts?
