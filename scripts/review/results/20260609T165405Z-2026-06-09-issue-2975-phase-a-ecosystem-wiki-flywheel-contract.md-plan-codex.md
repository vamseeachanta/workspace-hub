### Verdict: MAJOR

### Summary
The plan is close, but it is not implementation-ready because the schema guard contract is still internally inconsistent around `input_residency`, and the pre-edit occurrence drift gate is not made test-enforceable before edits begin.

### Issues Found
- [P1] Critical: The plan broadens `input_residency` to include `public_federal_wiki` while framing `public_federal_wiki` as an output/publication route. In the occurrence table, `execution-manifest.schema.yaml` line 55 and `report-evidence-bundle.schema.yaml` line 117 are marked for enum broadening, but the acceptance criteria and mitigations focus on output/public guard behavior. This risks admitting wiki-publication residency as an input/source residency without a stated semantic rule or negative tests proving it cannot be used to launder generated wiki output back into source evidence.
- [P2] Important: The “stop if current occurrence count differs from 16” safeguard is procedural, not test-enforced in the TDD list. The regression test listed checks post-edit occurrence disposition, but the plan requires a pre-edit live count gate before implementation. Without a dedicated pre-change test or scripted check that captures the precondition, an implementer can accidentally edit against drifted schemas and only discover ambiguity after partial edits.
- [P2] Important: The plan says Phase A will not implement validator/helper modules, but the sync script is itself a validator-like policy checker for config internal consistency, standard drift, public-safe flags, and write/check roundtrip behavior. That scope is probably acceptable, but the boundary needs sharper wording: otherwise Phase A can expand into general validation behavior that belongs to #3013.
- [P3] Minor: The plan’s evidence section claims `.gitattributes` was verified locally, but the attested evidence block does not include `.gitattributes`. Since `.gitattributes` is part of the implementation scope and closeout evidence requirement, final label-time evidence should include it as the plan already notes.

### Suggestions
- Either remove `public_federal_wiki` from `input_residency` enums or add explicit semantics and negative tests for when wiki residency may appear as an input.
- Add a first TDD check or small script assertion for the exact pre-edit `public_llm_wiki` occurrence count/disposition before schema modification proceeds.
- Rename/scope the sync script language as a config-to-standard synchronization check only, and explicitly defer broader bundle/public-egress validation to #3013.
- Include `.gitattributes` in the final attestation/evidence payload, including the existing LF rules and the new `*.jsonl` line.

### Questions for Author
- Is `public_federal_wiki` intentionally valid as an `input_residency`, or should Phase A restrict it to output/publication fields only?
- Should the pre-edit schema occurrence gate be a reusable script/check, or is a one-off governance test acceptable for Phase A?
