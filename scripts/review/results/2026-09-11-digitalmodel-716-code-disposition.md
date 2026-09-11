# Digitalmodel 716 code-review disposition

User authorization: the user said “continue with the work” after the concrete revision-3 plan. No agent applied an approval label. Scope remains the offline validator, regression tests and corpus evidence.

- [Claude actual review](../../../docs/reports/2026-09-11-digitalmodel-716-claude-code-review.md): MAJOR, Haiku low, 62.77 seconds, exit 0. Packet-only review; not native execution.
- [Codex actual review](../../../docs/reports/2026-09-11-digitalmodel-716-codex-code-review.md): REQUEST_CHANGES, one MAJOR. Reproduced sequence-context false pass.

Main applied and verified the following bounded corrections inline. These are main-session dispositions, not rewritten provider verdicts or a claim of provider consensus on the final patch.

| Finding | Disposition and verification |
| --- | --- |
| Codex C1: sequence edges erased, list item mistaken for direct General mapping | Accepted. Exact reproduction failed the new assertion before the fix. Sequence edges now retain a sentinel in their path. Direct and nested sequence fixtures emit diagnostics; ordinary General mapping remains recognized. |
| Claude C1: same-message findings lose distinct source lines | Accepted. New duplicate-maximum test failed with only line 2; final result retains lines 2 and 3. Approved ambiguous context produces warnings, not the errors proposed in Claude's example test. |
| Claude C2: source findings disappear on YAML construction failure | Accepted with corrected reproduction. Claude's unclosed YAML fails composition before findings exist; a valid node graph containing an unknown YAML tag reaches construction failure. The new test reproduced the lost warning; final code retains it alongside the construction error. |
| Claude secondary: RecursionError handler allegedly redundant | Not accepted. Composition runs before bounded graph inspection and can exhaust recursion. A 2,000-level sequence regression returns a diagnostic within the test deadline; the handler is retained and its purpose documented. |

The first complete corpus audit then exposed eight legitimate large-table files exceeding the initial fixed traversal budget. A 100,010-element table reproduced the rejection before the correction. The final guard bounds expanded visits proportionally to source length, retains the depth guard, and still rejects compact alias expansion in a separate regression. This change is recorded in code commit `72dd0f53`; it is an inline corpus-driven correction, not a new provider approval.

Final focused verification: 206 passed in 6.43 seconds using existing Python 3.11.15, no environment installation, across both validator modules, full generic builder/schema modules and semantic-roundtrip module. Original TDD baseline: 59 failed / 37 passed. Review-driven RED checkpoints: one sequence-context failure, then two diagnostic-retention failures, followed by the corpus-derived large-table failure. No native solver was invoked by these tests.

Final corpus replay: 94 paths, 93 generated cases, all 534 output files byte-identical with the same pinned hash seed, and 441 strict model-file checks with zero errors/warnings/exceptions. Native Model attempts were zero. Eleven generator current-profile warnings and one passing-ship schema-only integration gap remain. [Structured evidence](https://github.com/vamseeachanta/digitalmodel/blob/bugfix/orcaflex-validator-716/docs/reports/orcaflex-validator-716-corpus.json) is pushed at `cb309cbc`.

The generalizable provenance defect classes were promoted to [digitalmodel 2090](https://github.com/vamseeachanta/digitalmodel/issues/2090), an inventory/plan-first follow-on. Cross-process generation-order differences are tracked separately in [digitalmodel 2092](https://github.com/vamseeachanta/digitalmodel/issues/2092); no YAML normalization or generator change is included. No cross-repository refactor is included here. Hosted CI remains a separate integration gate; this review disposition alone does not qualify engineering models or close the broader issue.
