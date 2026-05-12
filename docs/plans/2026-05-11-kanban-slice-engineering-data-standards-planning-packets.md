# Planning packets — 2026-05-11 Kanban slice (engineering / data-pipeline / standards)

> Scope: planning-only packets for independent `workspace-hub` issues from `cat:engineering`, `cat:engineering-calculations`, `cat:data-pipeline`, and `domain:standards-tooling`.
> Source boards: `docs/reports/kanban/2026-05-11-repo-workspace-hub-domain-cat-engineering-kanban.md`, `...cat-engineering-calculations-kanban.md`, `...cat-data-pipeline-kanban.md`, `...domain-standards-tooling-kanban.md`.
> Constraint: no implementation, no GitHub mutation.

---

## Selected candidates

| Issue | Domain slice | Why selected now | Independence |
|---|---|---|---|
| #2558 — primary-source GoM equipment/cost source pack for #2112/#2055 | engineering + data-pipeline | Clear blocker-unblocker issue with existing downstream consumers and explicit `status:needs-data` gate | Independent data pack; downstream implementation remains separate |
| #2361 — rename `discovered` → `merged_at` in `provenance.py` and propagate | data-pipeline | Small-to-medium schema/contract cleanup with clear operating-model backing | Independent code/data-contract migration |
| #1826 — rebuild stale `specs/module-registry.yaml` as canonical calculation index | engineering-calculations | Dark-intel cataloging problem with clear repo-contract drift evidence | Independent catalog/routing remediation |
| #2658 — O&G-Standards consolidator: 8 catalog-classification defects | standards-tooling | High-leverage quality issue touching the standards ingest/corpus surfaces | Independent defect-batch planning packet |

---

## Packet: #2558 — primary-source GoM equipment/cost source pack for #2112/#2055

**Board status:** Planning Needed (`cat:engineering`, `cat:data-pipeline`, `priority:high`, `status:needs-data`)

### Why this is worth planning now
- `#2055` remains blocked on equipment-count evidence; prior planning artifacts explicitly say the implementation must stay `status:needs-data` until at least 10 GoM records are source-backed and definition-normalized.
- Existing plan artifacts already established that `data/field-development/subseaiq-scan-latest.json` has project rows but **no equipment counts**.
- A completed source-pack pattern exists in-repo (`docs/projects/acma/B1528/sirocco-rudder-source-pack.md`) and is a good template for “authoritative values / derived values / gaps” separation.

### Resource intelligence already confirmed
- Existing downstream references:
  - `docs/plans/overnight-prompts/2026-04-09-10claude/results/terminal-8-subsea-cost-benchmarking.md`
  - `docs/plans/claude-followup-2026-04-09/results/issue-2055-2062-refinement-drafts.md`
  - `docs/reports/kanban/2026-05-11-repo-workspace-hub-domain-cat-engineering-kanban.md`
- Existing state facts from prior planning docs:
  - `subseaiq-scan-latest.json` currently carries `name/operator/water_depth_m/host/year/capacity_bopd` only.
  - `worldenergydata/subseaiq/analytics/normalize.py` and the `SubseaProject` shape were previously documented as capable of consuming equipment-count fields once evidence exists.
- Reusable source-pack style reference:
  - `docs/projects/acma/B1528/sirocco-rudder-source-pack.md`

### Reproduction / resource-intel needs before implementation
1. Confirm the live location and schema of `data/field-development/subseaiq-scan-latest.json` in the current checkout.
2. Inventory which 10 GoM reference fields are the minimum viable set for the unblock.
3. Build a source matrix for each candidate field:
   - equipment counts source,
   - sanctioned/benchmark cost source,
   - year / currency / inflation basis,
   - field naming alias resolution.
4. Decide whether the source pack is:
   - a durable markdown artifact under `docs/projects/field-development/`,
   - a YAML/CSV evidence pack under `data/field-development/`,
   - or both.
5. Explicitly document unsupported data so implementers do not silently infer trees/manifolds/tieback lengths.

### Provider / machine route
- **Primary planner:** Claude
- **Research support:** Gemini for parallel source-hunting and alias reconciliation
- **Machine:** `ace-linux-1`
- **Overflow / external machine:** none needed for planning; any future browser-heavy research can be split but should still route through `ace-linux-1` control

### User decisions required
1. **Evidence threshold:** is “>=10 GoM records” still the approval bar, or should the pack target a larger set now?
2. **Allowed sources:** are trade-press / operator presentations acceptable, or must every row include operator/FID/regulator-grade sources?
3. **Normalization basis:** should equipment classes be constrained to `num_trees`, `num_manifolds`, and `tieback_distance_km` only for v1?
4. **Cost basis:** nominal sanction-year cost vs normalized real-dollar cost.
5. **Artifact authority:** should the source pack become the authoritative blocker-clearing surface for both `#2112` and `#2055`?

### Tests / CI / hygiene gates for the eventual implementation issue
- Schema validation for any source-pack YAML/CSV/JSON artifact.
- Regression test proving the chosen source-pack artifact can populate at least 10 records with the required evidence fields.
- No silent backfill: tests must fail on missing citation, ambiguous alias, or mixed unit basis.
- Repo-hygiene gate: keep any raw downloaded/source notes out of git unless explicitly curated; durable outputs only.
- Cross-check that future `#2112/#2055` tests consume the curated pack, not ad hoc local notes.

### Adversarial review route
- **Gemini:** challenge source quality, alias collisions, and cost/equipment comparability.
- **Codex:** review schema/testability and confirm the source pack is implementation-ready rather than prose-only.
- Review artifact should explicitly call out any records still requiring manual analyst judgment.

### Planning outcome target
Produce a source-pack plan that can clear `status:needs-data` only after a verifier can show 10+ source-backed, definition-normalized GoM rows with explicit evidence lineage.

---

## Packet: #2361 — rename `discovered` → `merged_at` in `provenance.py` and propagate

**Board status:** Planning Needed (`cat:data-pipeline`, `priority:medium`)

### Why this is worth planning now
- The 2026-04-19 document-intelligence amendment campaign explicitly called out `provenance.py` stamping `discovered` at merge time as contract drift.
- The amended operating model and follow-on issue set identify this rename as the blocker for conformance check `ID-7`.
- Current code evidence is cleanly bounded: `scripts/data/document-index/provenance.py` still contains `discovered`; search showed **3 occurrences** and **0 occurrences** of `merged_at` under `scripts/data/document-index/*`.

### Resource intelligence already confirmed
- Contract / rationale:
  - `docs/reports/2026-04-19-2205-amendment-campaign.md`
  - `config/agents/claude/memory-snapshots/project_doc_intel_operating_model.md`
- Primary code/test surfaces:
  - `scripts/data/document-index/provenance.py`
  - `scripts/data/document-index/tests/test_provenance.py`
- Current implementation detail:
  - `_make_provenance_entry()` writes `"discovered": discovered or _now_iso()`.

### Reproduction / resource-intel needs before implementation
1. Enumerate every consumer of provenance-entry fields beyond the local test file.
2. Confirm whether any historical JSONL/YAML outputs are treated as long-lived artifacts that need migration, compatibility shims, or one-time rewrite scripts.
3. Decide whether the function parameter name `discovered` also changes, or whether only the emitted schema changes.
4. Build a compatibility matrix:
   - code readers expecting `discovered`,
   - contract docs expecting `merged_at`,
   - any mixed-state readers that must tolerate both during transition.

### Provider / machine route
- **Primary planner:** Claude
- **Research / grep support:** Gemini
- **Machine:** `ace-linux-1`

### User decisions required
1. **Compatibility policy:** strict cutover vs temporary dual-read / single-write support.
2. **Historical artifact scope:** should already-generated provenance outputs be migrated in the same wave, or is forward-fix enough?
3. **Naming semantics:** if `merged_at` means merge-time specifically, should any true source-discovery timestamp remain separately representable later?

### Tests / CI / hygiene gates for the eventual implementation issue
- Unit tests updated for the new key name.
- Add explicit backward-compat tests if dual-read is approved.
- Conformance gate for `ID-7` should be runnable and green after the rename.
- Hygiene gate: docs/contracts/tests must land in the same wave so code and policy do not drift again.

### Adversarial review route
- **Gemini:** challenge semantic correctness (`merged_at` vs actual discovery timestamp meaning).
- **Codex:** review migration/test completeness and catch any hidden reader surfaces.
- Review output must confirm whether a one-time data migration is still outstanding.

### Planning outcome target
A bounded migration packet covering code, tests, docs, and compatibility semantics for `discovered` → `merged_at`, with explicit go/no-go criteria for enabling `ID-7`.

---

## Packet: #1826 — rebuild stale `specs/module-registry.yaml` as canonical calculation index

**Board status:** Planning Needed (`cat:engineering-calculations`, `priority:medium`, `dark-intelligence`)

### Why this is worth planning now
- Current repo guidance repeatedly says older `specs/module-registry.yaml` surfaces are stale or non-canonical while modern routing should use `docs/registry/module-routing.yaml`-style contracts.
- The issue is still open, but adjacent governance material shows confusion about what is canonical versus historical.
- Provider-session audit evidence shows `digitalmodel/specs/module-registry.yaml` is still heavily read, so drift here affects both humans and tooling.

### Resource intelligence already confirmed
- Drift evidence / planning context:
  - `docs/handoffs/2026-04-23-llm-wiki-tier1-focus-wave-exit.md` says `specs/module-registry.yaml` references should be replaced with `digitalmodel/docs/registry/module-routing.yaml` for the digitalmodel lane.
  - `docs/reports/provider-session-ecosystem-audit.md` lists repeated sibling-repo reads of `digitalmodel/specs/module-registry.yaml`.
  - `tests/analysis/test_provider_session_ecosystem_audit.py` includes fixtures/assertions referencing `digitalmodel/specs/module-registry.yaml`.
- Kanban location:
  - `docs/reports/kanban/2026-05-11-repo-workspace-hub-domain-cat-engineering-calculations-kanban.md`

### Reproduction / resource-intel needs before implementation
1. Confirm the real current state of the sibling `digitalmodel` repo:
   - whether `digitalmodel/specs/module-registry.yaml` still exists,
   - whether `digitalmodel/docs/registry/module-routing.yaml` exists and is authoritative,
   - whether any calculation-index data still lives only in the legacy file.
2. Separate three concerns that are currently conflated:
   - routing authority,
   - calculation inventory/catalog,
   - dark-intel prioritization / coverage metadata.
3. Inventory all consumers in `workspace-hub` that still parse or mention the legacy module registry.
4. Decide if the issue should produce:
   - a new canonical calculation index,
   - a migration/bridge layer from legacy registry,
   - or a documentation-only clarification plus follow-on implementation children.

### Provider / machine route
- **Primary planner:** Claude
- **Research support:** Gemini for sibling-repo/read-surface audit
- **Machine:** `ace-linux-1`
- **Potential overflow:** only if a fresh sibling-repo worktree/readiness check is needed on `ace-linux-2`; not required for planning by default

### User decisions required
1. Should the end-state be **one canonical calculation index** distinct from routing, or should routing metadata remain the canonical index?
2. Is sibling-repo mutation in `digitalmodel` in scope for the eventual implementation, or must `workspace-hub` only update its own references/plans/tests?
3. Should historical `specs/module-registry.yaml` remain as a compatibility artifact, or be clearly demoted/retired?

### Tests / CI / hygiene gates for the eventual implementation issue
- Any audit/analysis tests referencing `digitalmodel/specs/module-registry.yaml` must be reviewed and updated intentionally.
- Add fixture coverage for “canonical path present / legacy path absent or deprecated”.
- Documentation gate: all plan/handoff/report references should stop calling the stale registry canonical.
- Hygiene gate: no hidden dependency on sibling-repo local state; all required paths must be explicit.

### Adversarial review route
- **Gemini:** challenge whether the proposed canonical index actually solves retrieval/planning use cases or merely renames the file.
- **Codex:** inspect test and consumer completeness, especially audit fixtures and route-check logic.
- Review should explicitly flag any remaining mixed-authority surfaces.

### Planning outcome target
A clarification-first implementation plan that separates routing authority from calculation indexing and removes ambiguity about whether the legacy `module-registry.yaml` is historical, compatibility-only, or still semantically required.

---

## Packet: #2658 — O&G-Standards consolidator: 8 catalog-classification defects surfaced by parallel-agent ingest

**Board status:** Planning Needed (`domain:standards-tooling`, `domain:quality`, `cat:tooling`, `cat:data`)

### Why this is worth planning now
- This is the only open item on the `domain:standards-tooling` board, so it represents the current highest-leverage standards-tooling quality queue.
- Repo evidence already shows the standards corpus is large and partially pre-indexed (`O&G-Standards` has `_inventory.db`, `_catalog.json`, OCR text per prior audits/recovery artifacts), so classification defects likely have high downstream blast radius.
- Related tooling surfaces (`doc-key-lookup.py`, `query-ledger.py`, `generate-domain-resource-views.py`) all depend on standards metadata being trustworthy.

### Resource intelligence already confirmed
- Current issue lane source:
  - `docs/reports/kanban/2026-05-11-repo-workspace-hub-domain-domain-standards-tooling-kanban.md`
- Standards metadata / contract surfaces:
  - `data/document-index/standards-transfer-ledger.yaml` (436 tracked entries; search shows **0** `doc_key` fields today)
  - `scripts/knowledge/doc-key-lookup.py` (hard-coded wiki domains: `engineering`, `marine-engineering`, `maritime-law`, `naval-architecture`, `personal`)
  - `scripts/data/document-index/query-ledger.py`
  - `scripts/data/generate-domain-resource-views.py`
- Corpus-scale evidence from existing reports/patch history:
  - `data/document-intelligence/standards-ledger-expansion-plan.md` documents >26k standards files on disk vs 425/436 ledger entries.

### Reproduction / resource-intel needs before implementation
1. Surface the actual “8 defects” as a durable defect ledger:
   - wrong domain,
   - wrong org/catalog bucket,
   - duplicate/alias collision,
   - ledger/index/wiki disagreement,
   - missing classification target.
2. Identify which artifact is authoritative for each field under review:
   - source catalog,
   - standards-transfer ledger,
   - wiki frontmatter/page placement,
   - generated domain-resource views.
3. Determine whether the defects are confined to `workspace-hub` metadata or require coordinated changes in the `llm-wiki` spinout tree.
4. Check if the defect set overlaps with open doc-intel prerequisites like `#2362` (`doc_key` back-population).

### Provider / machine route
- **Primary planner:** Claude
- **Research support:** Gemini for corpus/metadata cross-checks
- **Machine:** `ace-linux-1`
- **Future implementation note:** if live corpus inspection against large external mounts is needed, keep `ace-linux-1` as control and only use overflow after a fresh readiness/auth check

### User decisions required
1. **Authority decision:** when catalog, ledger, and wiki classification disagree, which wins by default?
2. **Fix scope:** patch only the 8 known defects, or treat this as a pattern-mining issue that should produce validator rules and follow-on cleanup batches?
3. **Spinout boundary:** should `workspace-hub` remain the source of truth for standards classification, or should llm-wiki own the durable classification after ingest?

### Tests / CI / hygiene gates for the eventual implementation issue
- Add regression fixtures for each of the 8 defect classes (or one fixture per defect if all are unique).
- Validation should fail on mismatched org/domain/category mappings that previously slipped through.
- If generated views or lookup tools are affected, update their tests or add snapshot-style assertions.
- Hygiene gate: no bulk reclassification without a machine-readable change record mapping old → new classifications.

### Adversarial review route
- **Gemini:** challenge defect taxonomy and authority assumptions across catalog/ledger/wiki layers.
- **Codex:** review validator/test design and confirm fixes are reproducible rather than one-off manual edits.
- Review artifact must state whether the issue closes with 8 fixes only or requires a child issue for generalized validation.

### Planning outcome target
A defect-batch plan that turns the vague “8 surfaced defects” into a reproducible correction set with explicit authority rules, regression coverage, and a clear boundary between metadata patching and broader validator work.

---

## Recommended execution ordering after plan approval

1. **#2361** — smallest bounded contract fix; unblocks conformance clarity.
2. **#2558** — highest-value data unblocker for downstream field-development work.
3. **#2658** — standards-quality batch once authority rules are agreed.
4. **#1826** — broader calculation-index/routing clarification once sibling-repo authority is confirmed.

## Cross-cutting review note
All four issues should require a brief adversarial review artifact before implementation starts, because each one changes an authority boundary: data evidence, schema naming, canonical registry/index ownership, or standards classification.