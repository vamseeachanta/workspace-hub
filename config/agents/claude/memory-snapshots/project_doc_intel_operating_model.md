---
name: Document-intelligence operating model (#2205)
description: Parent operating-model + four child contracts governing the llm-wiki + resource/document intelligence ecosystem
type: project
originSessionId: ac348218-fd8d-49f9-b0d4-daa28cc4ba54
---
The workspace-hub document-intelligence ecosystem is governed by a parent operating model at `docs/document-intelligence/llm-wiki-resource-doc-intelligence-operating-model.md` and three active child contracts:

- `standards-codes-provenance-reuse-contract.md` (#2207 — provenance + reuse)
- `durable-vs-transient-knowledge-boundary.md` (#2209 — durability policy)
- `pyramid-conformance-checks.md` (#2206 — conformance-check design)

**Why:** Before the 2026-04-11 operating model, intelligence artifacts (wikis, registries, summaries, promoted content) had no single-source-of-truth structure; knowledge, provenance, and execution state were intermingled. The six-layer pyramid (L1 source → L2 registry → L3 durable → L4 entry-point → L5 execution → L6 transient) plus the canonical `doc_key`-based identity model established the contract.

**Amendment history:**
- 2026-04-11: Initial parent + four child contracts shipped
- 2026-04-17: Cross-provider (Claude + Codex) adversarial review of children surfaced 38 findings + 3 systemic patterns
- 2026-04-19: Parent amended (§2 worked examples + forbidden inventions, §3 `<algorithm>:<hex>` namespace + 7-state status vocab + `discovered` → `merged_at` rename, §8.1 L3 frontmatter schema authority with baseline floor). All three children revised against amended parent and merged to main.

**How to apply:**
- Any new document-intelligence work must cite the parent operating model as authority; children may not redefine parent-level contracts.
- Child issues discovering conflicts with the parent must escalate via §10 conflict resolution (comment on #2205, propose amendment, wait for user approval) rather than unilaterally deviating.
- Conformance checks under #2206 (FRONT-1, GUARD-1, ID-3, FLOW-6, ID-7, ACC-7) enforce parent invariants; three are blocked on follow-ons #2360 (wiki CLAUDE.md `doc_key`), #2361 (`provenance.py` rename), #2362 (`standards-transfer-ledger.yaml` back-population).
- Session report with full arc and artifact list: `docs/reports/2026-04-19-2205-amendment-campaign.md`.
