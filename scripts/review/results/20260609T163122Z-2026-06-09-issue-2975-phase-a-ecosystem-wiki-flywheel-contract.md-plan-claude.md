### Verdict: MAJOR

### Summary
A well-structured, properly narrowed Phase A contract-surfaces plan with clear scope boundaries, explicit Phase B (#3013) deferral, and a solid TDD list. Two correctness gaps block approval: "freshness threshold defaults" appear in acceptance criteria and Files-to-Change but have no contract-value definition or test, and the safety-relevant decision to treat public_federal_wiki as a public residency in existing fail-closed guard logic is only asserted, not test-pinned.

### Issues Found
- [P2] Coverage gap — freshness thresholds: Acceptance Criterion 2 (line 208) and Files-to-Change (config, line 163) require 'freshness threshold defaults', but the Phase A Contract Values table (lines 80-95) defines no freshness values and the TDD list (lines 187-201) has no test asserting their presence or shape. test_config_defines_exact_enum_values only covers enum groups. Either add a contract-value definition + a test, or drop freshness from Phase A scope.
- [P2] Safety-relevant guard behavior under-tested: Pseudocode (line 145-146) states public_federal_wiki must be 'treated as a public residency anywhere existing schema logic guards public_llm_wiki'. This is a behavioral wiring change, not a purely additive enum. The two schema tests (lines 196-197) only assert the schema 'accepts' the new value 'without weakening public gates' — neither pins that public_federal_wiki actually triggers the same fail-closed public-output constraints as public_llm_wiki. A bare enum addition that consumers misread as private would be a silent public-egress hazard. Add a positive test asserting public_federal_wiki is classified/guarded as public.
- [P3] Unverifiable claims (no Attested Evidence block supplied): the plan asserts #2975 OPEN, #3013 OPEN (lines 60-61) and a set of EXISTS/MISSING file states (lines 65-74) 'verified via gh issue view / local reads', but no attestation payload accompanies this dispatch. The entire phase-split premise is load-bearing on #3013 existing as the Phase B child — if that issue does not exist, the deferral boundary is hollow.
- [P3] Minor internal inconsistency on standards index: Resource Intelligence lists docs/standards/README.md as MISSING (line 73), while Files-to-Change (line 178) and acceptance criterion (line 213) treat it as 'create if missing, or add a row if it exists'. The defensive create/modify is fine, but the flat MISSING claim and the conditional handling should be reconciled so the implementer knows which to expect.
- [P3] test_config_defines_exact_enum_values (line 188) pins config values to 'the exact Phase A contract values listed in this plan', but public_identity dataset slugs (line 89) and publication_sequence stages (lines 91-95) are described in prose rather than placed in the contract-values table, making 'exact' ambiguous for those groups.

### Suggestions
- Add a TDD row asserting public_federal_wiki is enumerated AND classified as a public residency by whatever helper/guard the architecture tests already exercise for public_llm_wiki, so the egress semantics are pinned in Phase A even though enforcement lands in Phase B.
- Add or remove freshness-threshold coverage: if it stays in Phase A, give it a contract-value entry and a test_config_defines_freshness_defaults; if it is really Phase B's concern, strike it from AC 2 and the config Reason column.
- Fold public_identity slugs and publication_sequence stages into the Phase A Contract Values table so 'exact enum values' is unambiguous and the sync-check has a single normative source.
- State explicitly whether anything in Phase A (or already-merged code) consumes public_federal_wiki output_residency before Phase B's egress gate lands — if a consumer could route to worldenergydata-wiki on this enum without the #3013 enforcement, note the interim exposure window and why it is safe.
- Reconcile the docs/standards/README.md MISSING vs create-or-modify language so the implementer is not surprised by a pre-existing index.

### Questions for Author
- Does workspace-hub#3013 currently exist as an OPEN Phase B child issue? The phase-split safety argument depends on it; can you attach the gh issue view evidence or an attestation block?
- Are freshness threshold defaults in or out of Phase A scope? They appear in acceptance criteria and config but have no contract definition or test.
- Will any consumer (existing or Phase A) be able to set output_residency: public_federal_wiki before the #3013 public-egress enforcement lands, and if so what prevents premature public routing in that window?
- Should the additive schema change include a positive test that public_federal_wiki inherits public_llm_wiki's fail-closed guard behavior, rather than only the 'accepts without weakening' assertions currently listed?
