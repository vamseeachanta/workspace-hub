# feat(execution): enforce report handoff gates at runtime

Parent: #2728

Connect execution manifests to report handoff checks so `report_eligible` cannot be asserted unless the manifest includes:

- source IDs and a source registry reference
- command, replay, regeneration, and environment metadata
- checksums for generated outputs
- targeted test evidence
- canonical legal scan evidence
- adversarial review artifact paths
- output-residency compatibility and required promotion gates

Acceptance criteria:

- runtime/check script fails closed on missing evidence
- runtime/check script rejects inline raw/private payload fields
- CI or pre-publication workflow invokes the check before report publication
- tests cover valid, missing-evidence, and invalid-publication cases
