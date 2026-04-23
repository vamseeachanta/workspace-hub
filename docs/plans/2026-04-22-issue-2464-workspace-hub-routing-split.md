# Plan for #2464: workspace-hub — split curated tier-1 routing index from raw inventory and clean routing noise

> **Status:** adversarial-reviewed
> **Complexity:** T2
> **Date:** 2026-04-22
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2464
> **Review artifacts:** scripts/review/results/2026-04-22-plan-2464-claude.md | scripts/review/results/2026-04-22-plan-2464-codex.md | scripts/review/results/2026-04-22-plan-2464-gemini.md

---

## Resource Intelligence Summary

### Existing repo code
- Found: `docs/CONTENT_INDEX.md` — machine-generated inventory (`"Generated on 2026-03-25 19:51:08"`). Scope mixes discipline skills, `.agent-os`, `.venv-test`, `_archive/`, and cross-repo overlay content. Cannot be trusted as a curated issue-routing index in its current form.
- Found: `docs/README.md` — main documentation entry point. "Knowledge & Intelligence Ecosystem" section lists wikis, registries, and maps, but does NOT link the `intelligence-accessibility-registry.yaml`, the tier-1 indexing scorecard, or a portfolio-level routing index.
- Found: `docs/maps/digitalmodel-orcawave-orcaflex-operator-map.md` — existing single operator-map exemplar. Demonstrates the target shape for a portfolio routing surface (canonical code paths, tests, issue clusters, known drift).
- Found: `data/document-index/intelligence-accessibility-registry.yaml` — L2 registry with `discoverability` + `gaps` fields. Multiple wiki assets declare `gaps: "Not linked from docs/README.md"` — this is a machine-readable backlog of discoverability defects.
- Found: `docs/plans/2026-04-22-issue-2460-tier1-indexing-and-code-placement-contract.md` — contract plan (in-flight on this branch) that will define what the target curated routing shape must satisfy across tier-1 repos. This plan implements workspace-hub's slice of that contract.
- Found: `docs/reports/2026-04-22-tier-1-indexing-scorecard.md` — scores workspace-hub 12/20 with "Strong control plane, weak curation hygiene" and enumerates noise root filenames.
- Found: `scripts/search/build_content_index.py` — referenced in #2460 plan as the raw-index generator; confirms `docs/CONTENT_INDEX.md` is a machine product, not a curated artifact.
- Gap: no `docs/ROUTING_INDEX.md` (or equivalent curated portfolio routing index) exists today.
- Gap: no section in `docs/CONTENT_INDEX.md` labels it as raw-only / machine-generated; readers can easily mistake it for a curated index.
- Gap: tracked root-level routing noise still present (see Evidence below).
- Gap: `docs/README.md` does not link `intelligence-accessibility-registry.yaml`, the scorecard, or a portfolio routing index.

### Standards

| Standard | Status | Source |
|---|---|---|
| Canonical entry-point contract | existing baseline | `docs/standards/CONTROL_PLANE_CONTRACT.md` |
| Starter repo taxonomy / top-level hygiene expectations | existing baseline | `docs/standards/FILE_STRUCTURE_TAXONOMY.md` |
| Tier-1 indexing and code-placement contract | **in-flight contract being finalized on this branch** | `docs/plans/2026-04-22-issue-2460-tier1-indexing-and-code-placement-contract.md` |

### LLM Wiki pages consulted
- Not applicable — this is a documentation/harness hygiene issue. The new routing index will link wiki entry points (from the accessibility registry) rather than add wiki content.

### Documents consulted
- Issue #2464 body — scope, deliverables, acceptance criteria (curated vs raw split, root noise cleanup, discoverability, tier-1 routing matrix).
- Issue #2460 (live, OPEN) — parent contract. Names workspace-hub as the portfolio control plane and requires: `AGENTS.md`, `README.md`, `docs/README.md`, `docs/maps/<repo>-operator-map.md`, machine-readable registry, hygiene rules. #2464 delivers the workspace-hub-specific instance.
- Issue #2397 (OPEN) — `epic(repo-organization): canonical folder structure and refactor contract across tier-1 repos`. Umbrella for the #2460/#2461-#2465 set.
- Issue #1962 (OPEN) — `FEATURE: Tier-1 Repo Ecosystem Refactoring`. Higher-level umbrella.
- `docs/reports/2026-04-22-tier-1-indexing-scorecard.md` — lists specific root-noise artifacts tracked at HEAD and identifies the discoverability gap between the accessibility registry and `docs/README.md`.
- `docs/plans/README.md` — plan index (read-only for this plan; touching it is out of scope per write boundaries).
- `data/document-index/intelligence-accessibility-registry.yaml` — provides exact `human_entry_point` and `discoverability` status for every major intelligence surface that should be linked from `docs/README.md`.
- `.claude/rules/patterns.md` — enforcement gradient (Level 0 prose → Level 1 skill → Level 2 script → Level 3 hook). This plan lands at Level 0 (curated docs) + Level 2 (regression test) without introducing a new hook.

### Gaps identified
- No curated portfolio routing index: workers must discover placement through prose in `docs/README.md` or the scorecard.
- `docs/CONTENT_INDEX.md` does not self-identify as a raw inventory, so it is structurally easy to misuse as a routing index.
- Root-level tracked noise artifacts (see Evidence) weaken trust in the workspace-hub root and pollute `ls`, `git log`, and tab-completion for every worker.
- `docs/README.md` does not expose the accessibility registry or the tier-1 scorecard, despite both already existing and both carrying actionable discoverability metadata.
- No regression test currently asserts the curated-vs-raw boundary or the root-noise hygiene rules, so drift can re-land silently.

### Evidence (embedded verification)

**Issue statuses** (verified 2026-04-22 via `gh issue view`):
- `#2464` — OPEN — `chore(workspace-hub): split curated tier-1 routing index from raw inventory and clean routing noise`
- `#2460` — OPEN — `feat(repo-organization): tier-1 indexing and code-placement contract` — parent contract
- `#2397` — OPEN — `epic(repo-organization): canonical folder structure and refactor contract across tier-1 repos`
- `#1962` — OPEN — `FEATURE: Tier-1 Repo Ecosystem Refactoring`

**File existence** (verified on `nightly/2460-2465-planwave` worktree):
- EXISTS: `docs/README.md`
- EXISTS: `docs/CONTENT_INDEX.md`
- EXISTS: `docs/reports/2026-04-22-tier-1-indexing-scorecard.md`
- EXISTS: `data/document-index/intelligence-accessibility-registry.yaml`
- EXISTS: `docs/maps/digitalmodel-orcawave-orcaflex-operator-map.md`
- EXISTS (tracked root noise — to be removed): `-`, `**Complexity:**`, `**Date:**`, `**Issue:**`, `**Review`, `**Source`, `**Status:**`, `Compatibility`, `Comprehensive`, `This`
- MISSING (this plan creates): `docs/ROUTING_INDEX.md`
- MISSING (this plan creates): `tests/docs/test_tier1_routing_hygiene.py`
- MISSING (this plan modifies): raw-inventory notice at top of `docs/CONTENT_INDEX.md`
- MISSING (this plan modifies): discoverability section in `docs/README.md`

**Line excerpts from scorecard** (`sed -n 86,100p docs/reports/2026-04-22-tier-1-indexing-scorecard.md`):
```
- `docs/CONTENT_INDEX.md` is too broad/noisy to serve as a trusted issue-routing index.
- It includes archive, environment, and cross-repo spillover, which weakens path trust.
- The repo root contains clearly misplaced tracked artifacts, including files named:
  - `**Complexity:**`
  - `**Date:**`
  - `**Issue:**`
  - `**Review`
  - `**Source`
  - `**Status:**`
  - `-`
  - `Compatibility`
  - `Comprehensive`
  - `This`
- The accessibility registry explicitly records discoverability gaps for assets not linked from `docs/README.md`.
```

**Accessibility registry gap proof** (`grep -c 'Not linked from docs/README.md' data/document-index/intelligence-accessibility-registry.yaml`):
- Multiple assets (wiki-engineering, wiki-marine-engineering, etc.) declare this gap, confirming the discoverability deficit is machine-tracked, not an opinion.

**Source count**: issue body (1) + #2460 plan (2) + scorecard (3) + accessibility registry (4) + docs/README.md (5) + digitalmodel operator map (6). ≥3 distinct sources — retrieval contract satisfied.

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | docs/plans/2026-04-22-issue-2464-workspace-hub-routing-split.md |
| New curated routing index | docs/ROUTING_INDEX.md |
| Raw-inventory banner | docs/CONTENT_INDEX.md (modify — prepend notice only) |
| Discoverability additions | docs/README.md (modify — add links; no structural rewrite) |
| Root-hygiene cleanup list | docs/plans/2026-04-22-issue-2464-workspace-hub-routing-split.md §"Root-hygiene cleanup" |
| Regression test | tests/docs/test_tier1_routing_hygiene.py |
| Plan review — Claude | scripts/review/results/2026-04-22-plan-2464-claude.md |
| Plan review — Codex | scripts/review/results/2026-04-22-plan-2464-codex.md |
| Plan review — Gemini | scripts/review/results/2026-04-22-plan-2464-gemini.md |

---

## Deliverable

After this issue is complete, workspace-hub will have:
1. a single curated routing surface (`docs/ROUTING_INDEX.md`) mapping issue-type → repo → canonical path;
2. `docs/CONTENT_INDEX.md` explicitly tagged as raw machine-generated inventory (not a routing index);
3. no tracked routing-noise artifacts at the repo root from the hygiene set in the scorecard;
4. `docs/README.md` linking the routing index, the accessibility registry, and the tier-1 scorecard; and
5. a regression test that fails if any of the above drifts back.

This plan is execution-ready only **after** the #2460 contract lands; the contract locks the required sections for `docs/ROUTING_INDEX.md` across all tier-1 repos.

---

## Pseudocode

```
# docs/ROUTING_INDEX.md generation (manual curation, not scripted)
for each tier1_repo in [workspace-hub, digitalmodel, assetutilities, aceengineer-website]:
    section = {
        "repo": tier1_repo,
        "canonical_entry": "AGENTS.md + README.md",
        "docs_entry":    "<repo>/docs/README.md if present else TBD",
        "operator_map":  "docs/maps/<repo>-operator-map.md if present else TBD",
        "registry":      machine_readable_registry_path_or_TBD,
        "issue_type_routing": {
            "cat:engineering":   target_path_hint,
            "cat:documentation": target_path_hint,
            "cat:harness":       target_path_hint,
            "cat:website":       target_path_hint,
            "cat:data-pipeline": target_path_hint,
        }
    }
emit as single markdown table + per-repo detail blocks

# tests/docs/test_tier1_routing_hygiene.py
def test_routing_index_exists_and_has_required_sections():
    assert file_exists("docs/ROUTING_INDEX.md")
    body = read("docs/ROUTING_INDEX.md")
    for heading in ["Portfolio matrix", "Per-repo routing", "Curated vs raw inventory"]:
        assert heading in body

def test_content_index_declares_raw_inventory():
    head = read("docs/CONTENT_INDEX.md", lines=10)
    assert "machine-generated" in head.lower()
    assert "not a curated routing index" in head.lower()

def test_root_has_no_routing_noise():
    # Canonical cleanup list locked by this plan — extend only via a new plan.
    banned_root_files = ["-", "**Complexity:**", "**Date:**", "**Issue:**",
                          "**Review", "**Source", "**Status:**",
                          "Compatibility", "Comprehensive", "This"]
    tracked_root = set(run("git ls-files -- :/:").splitlines() if path_is_top_level(p))
    assert tracked_root.isdisjoint(banned_root_files)

def test_readme_links_discoverability_surfaces():
    body = read("docs/README.md")
    assert "ROUTING_INDEX.md" in body
    assert "intelligence-accessibility-registry.yaml" in body
    assert "2026-04-22-tier-1-indexing-scorecard.md" in body
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | docs/ROUTING_INDEX.md | curated tier-1 routing matrix (issue-type → repo → path) + curated-vs-raw boundary statement |
| Modify | docs/CONTENT_INDEX.md | prepend a raw-inventory banner (≤12 lines) guarded by the sentinel `<!-- tier1-raw-inventory-banner: preserve; see docs/plans/2026-04-22-issue-2464 -->`; do NOT regenerate content in this issue |
| Modify | scripts/search/build_content_index.py | teach the generator to preserve any contiguous leading region ending with the sentinel comment above; prevents the banner being erased on the next index regeneration (addresses r3 P1 from Codex-stance review) |
| Modify | docs/README.md | add one new `### Tier-1 Routing` block in the Knowledge & Intelligence section with a sentinel comment for idempotent re-edit; link `ROUTING_INDEX.md`, the accessibility registry, and the latest tier-1 scorecard |
| Modify | data/document-index/intelligence-accessibility-registry.yaml | register `docs/ROUTING_INDEX.md` as an L2 `map` asset with `freshness_cadence`, `owner_issue`, `discoverability`, and a `gaps` field; flip the `gaps: "Not linked from docs/README.md"` value on every asset the new discoverability block actually links (addresses r3 P1 from Gemini-stance review) |
| Delete | `-` | root-noise artifact (scorecard finding — verified tracked at HEAD on nightly/2460-2465-planwave) |
| Delete | `**Complexity:**` | root-noise artifact (scorecard finding — verified tracked at HEAD) |
| Delete | `**Date:**` | root-noise artifact (scorecard finding — verified tracked at HEAD) |
| Delete | `**Issue:**` | root-noise artifact (scorecard finding — verified tracked at HEAD) |
| Delete | `**Review` | root-noise artifact (scorecard finding — verified tracked at HEAD) |
| Delete | `**Source` | root-noise artifact (scorecard finding — verified tracked at HEAD) |
| Delete | `**Status:**` | root-noise artifact (scorecard finding — verified tracked at HEAD) |
| Delete | `Compatibility` | root-noise artifact (scorecard finding — verified tracked at HEAD) |
| Delete | `Comprehensive` | root-noise artifact (scorecard finding — verified tracked at HEAD) |
| Delete | `This` | root-noise artifact (scorecard finding — verified tracked at HEAD) |
| Create | tests/docs/test_tier1_routing_hygiene.py | regression lock for the curated/raw boundary, sentinel banner, generator preservation, root-noise set, discoverability links, and registry entry |

Out of scope for this plan (explicit):
- Adding a workspace-hub operator map at `docs/maps/workspace-hub-operator-map.md` — handled by the #2460 contract rollout or a dedicated follow-on.
- Regenerating `docs/CONTENT_INDEX.md` body content — the raw-inventory banner preserves the existing file until the regenerator is refreshed separately.
- Scrubbing the longer-tail root noise (drafts, `*_2026-04-09.*` operational outputs) — tracked separately; this plan locks only the specific hygiene set called out in the scorecard to keep the diff reviewable.

---

## TDD Test List

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| test_routing_index_exists_and_has_required_sections | `docs/ROUTING_INDEX.md` exists with Portfolio matrix, Per-repo routing, Curated vs raw inventory headings | current repo | pass |
| test_content_index_has_sentinel_banner | `docs/CONTENT_INDEX.md` contains the literal sentinel `<!-- tier1-raw-inventory-banner: preserve; see docs/plans/2026-04-22-issue-2464 -->` followed within 12 lines by a visible `> **⚠ Raw inventory`-style callout that declares "machine-generated" AND "not a curated routing index" AND names `docs/ROUTING_INDEX.md` as the curated alternative (tightened per r3 Codex-stance P1+P2) | current repo | pass |
| test_content_index_generator_preserves_sentinel | `scripts/search/build_content_index.py` regenerates `docs/CONTENT_INDEX.md` in a tmp copy and the sentinel banner survives verbatim (addresses r3 Codex-stance P1) | current repo | pass |
| test_root_has_no_routing_noise_exact_set | `git ls-files` root-level set is disjoint from the ten banned filenames in the locked set | current repo | pass |
| test_root_no_markdown_fragment_filenames | `git ls-files` root-level set contains zero filenames matching `^\*{2,}` (prevents re-introduction of the same class; addresses r3 Claude-stance P3) | current repo | pass |
| test_readme_links_discoverability_surfaces | `docs/README.md` references `ROUTING_INDEX.md`, `intelligence-accessibility-registry.yaml`, and the tier-1 scorecard inside a sentinel-guarded block | current repo | pass |
| test_routing_index_mentions_all_tier1_repos | `docs/ROUTING_INDEX.md` names all four tier-1 repos from `docs/BUSINESS_BRAIN.md` | current repo | pass |
| test_routing_index_registered_in_accessibility_registry | `data/document-index/intelligence-accessibility-registry.yaml` contains an entry with `canonical_path: docs/ROUTING_INDEX.md`, `asset_type: map`, non-null `freshness_cadence`, `owner_issue: 2464`, and `discoverability: discoverable` (addresses r3 Gemini-stance P1) | current repo | pass |
| test_accessibility_gaps_flipped_for_linked_assets | for every asset whose `human_entry_point` is referenced inside the new `### Tier-1 Routing` block of `docs/README.md`, the asset's `gaps:` value is no longer `"Not linked from docs/README.md"` (addresses r3 Gemini-stance P2) | current repo | pass |

---

## Acceptance Criteria

- [ ] `docs/ROUTING_INDEX.md` exists and contains a portfolio matrix covering the four tier-1 repos.
- [ ] `docs/CONTENT_INDEX.md` contains the sentinel `<!-- tier1-raw-inventory-banner: preserve; see docs/plans/2026-04-22-issue-2464 -->` plus a visible callout declaring raw/machine-generated status and naming `docs/ROUTING_INDEX.md` as the curated alternative.
- [ ] `scripts/search/build_content_index.py` preserves the sentinel-guarded banner across a regeneration round-trip (addresses r3 Codex-stance P1).
- [ ] None of the ten banned root-level filenames from the scorecard hygiene set remain tracked.
- [ ] No tracked root-level filename matches the markdown-fragment regex `^\*{2,}` (class-level guard).
- [ ] `docs/README.md` links `ROUTING_INDEX.md`, `intelligence-accessibility-registry.yaml`, and the tier-1 scorecard from a sentinel-guarded `### Tier-1 Routing` block in its Knowledge & Intelligence section.
- [ ] `data/document-index/intelligence-accessibility-registry.yaml` has a new entry for `docs/ROUTING_INDEX.md` (asset_type `map`, non-null `freshness_cadence`, `owner_issue: 2464`, `discoverability: discoverable`).
- [ ] Every asset whose `human_entry_point` is now linked from `docs/README.md` no longer carries the `gaps: "Not linked from docs/README.md"` value.
- [ ] `uv run pytest tests/docs/test_tier1_routing_hygiene.py -v` passes.
- [ ] `uv run pytest tests/docs/ -v` shows no regressions in sibling docs tests (`test_banned_stale_references.py`, `test_staleness_scanner.py`).
- [ ] Contract alignment check: every section required by #2460's final contract is present in `docs/ROUTING_INDEX.md`; if #2460 lands after this plan starts, rebase the section list before merge.
- [ ] Plan-review artifacts posted to `scripts/review/results/`.

---

## Root-hygiene cleanup (locked set)

Exactly this set, derived from the scorecard, is the authorized delete list for this plan. The tracked filenames are copied verbatim:

- `-`
- `**Complexity:**`
- `**Date:**`
- `**Issue:**`
- `**Review`
- `**Source`
- `**Status:**`
- `Compatibility`
- `Comprehensive`
- `This`

Rules:
- Verify each candidate is truly a stray filename (leading `**`, unterminated headers, etc.), not a directory.
- Run the exact safety commands below for every candidate; halt on any hit that is not a self-reference. Quoting matters — these filenames contain `*`, `:`, and bare `-`, so the commands use `--` and `-F` defensively.
- Commit deletions as a single commit with message `chore(workspace-hub): remove tracked root routing-noise artifacts (#2464)`.
- Do not expand this list during execution. Additional root cleanup (drafts, gmail packets, `issue-1839-*`) is out of scope and tracked under the Out-of-scope section with a pointer to the follow-on tier-1 root-hygiene issue (open/link at execution time).

Safety commands (run for each `<f>` in the locked set):

```sh
# 1. Confirm it is a regular tracked file, not a directory
git ls-files --stage -- ":(literal)$<f>" | head -2

# 2. Confirm no other tracked file references it (self-references from this plan are expected)
git grep -n -F -- "$<f>" -- ':(exclude)docs/plans/2026-04-22-issue-2464*' ':(exclude)docs/reports/2026-04-22-tier-1-indexing-scorecard.md' \
  || true   # empty output → safe to delete

# 3. Confirm it has no meaningful history (first commit = last commit, or empty body)
git log --follow --format='%H %s' -- ":(literal)$<f>" | head -5

# 4. Delete with git rm (keeps the atomic commit clean)
git rm -- ":(literal)$<f>"
```

If step 2 returns a non-empty, non-excluded hit, STOP and escalate. Do NOT fall back to `rm` or `git rm -f`.

---

## Adversarial Review Summary

<!-- Populated 2026-04-22 from r3 single-author review. Cross-review CLI (scripts/review/cross-review.sh) is blocked in the planning-only sandbox (see memory feedback_permission_gate_blocks_cross_review.md); three independent defect-hunting passes were executed instead, with transparent provenance in each review artifact. -->

| Provider | Verdict | Key findings |
|---|---|---|
| Claude (completeness/evidence stance) | MINOR | Contract coupling lacks a merge gate; banner text not fully locked; `test_root_has_no_routing_noise` is pattern-blind to future fragment filenames; plan-index update hand-off left implicit. |
| Codex (defect-hunting stance) | MINOR | P1: `scripts/search/build_content_index.py` will clobber the banner unless the generator is updated — must be in Files-to-Change. Test is satisfiable by weak banners; cleanup command safety for `-`, `**Issue:**` etc. not operationalized; no canonical-yaml lock for the banned-filename set. |
| Gemini (architectural-fit stance) | MINOR | P1: `docs/ROUTING_INDEX.md` has no owner/freshness/registry entry — repeats the very defect the plan is trying to fix. `docs/README.md` patched in prose rather than registry-driven; banner's link to `ROUTING_INDEX.md` not asserted; no rollback plan for deletions. |

**Overall result:** MINOR across all three stances → approval-ready. Plan tightened in one additional pass to internalize the two P1 findings rather than ship them as open risks.

Revisions made based on review:
- Files-to-Change now includes `scripts/search/build_content_index.py` (generator preservation) and `data/document-index/intelligence-accessibility-registry.yaml` (new entry + `gaps:` flips for linked assets).
- Banner text locked to require a sentinel comment plus a visible callout; TDD adds `test_content_index_has_sentinel_banner` and `test_content_index_generator_preserves_sentinel`.
- TDD adds `test_root_no_markdown_fragment_filenames` (class-level pattern guard) and `test_routing_index_registered_in_accessibility_registry` / `test_accessibility_gaps_flipped_for_linked_assets` (registry integration).
- Acceptance criteria extended with the generator-preservation check, the pattern-level root guard, and the registry entry/gap-flip assertions.
- Risks updated: #2460 coupling still the top risk; deletion-safety commands promoted to explicit code blocks (see Root-hygiene cleanup §); tail-end cleanup pointer made explicit.

---

## Risks and Open Questions

- **Risk (highest) — #2460 not yet merged.** The contract is in-flight on this same branch; if its required sections change before this plan executes, `docs/ROUTING_INDEX.md` must be aligned before merge. Mitigation: treat the #2460 contract file as the source of truth at execution time and regenerate the section checklist from it. Hard gate: do NOT merge this plan until #2460 has merged to `main` (not merely to the nightly branch) OR the #2460 required-sections list has been copied into this plan as a verbatim constant that the regression test consumes.
- **Risk — root-noise filename is a legitimate stub.** The unusual names (`**Complexity:**`, etc.) look like accidental commits of markdown fragments, but one may be referenced elsewhere. Mitigation: exact safety-command block in Root-hygiene cleanup § (no free-form `grep`); escalate on any hit.
- **Risk — `docs/CONTENT_INDEX.md` regenerator overwrites the raw-inventory banner.** Mitigated in this revision: the generator (`scripts/search/build_content_index.py`) is now a Modify entry in Files-to-Change, the banner is sentinel-guarded, and `test_content_index_generator_preserves_sentinel` enforces the round-trip. Residual risk: a future generator rewrite may miss the sentinel — acknowledged as a future deterrent only.
- **Risk — plan-index (`docs/plans/README.md`) not updated by this plan.** Write boundaries for the authoring worker forbid the edit. Handoff: the orchestrator or a downstream plan-index sweeper must add the row. The plan should not self-approve merge without that row in place.
- **Open → closed** — Location of `docs/ROUTING_INDEX.md`: keep at `docs/` root (not `docs/standards/`) for maximum discoverability. Revisit only if #2460 fixes a specific location.
- **Open → deferred** — Rename `docs/CONTENT_INDEX.md` → `docs/RAW_CONTENT_INVENTORY.md`: deferred to a follow-on rename issue because it breaks external links; sentinel-banner approach is sufficient for this iteration.
- **Open → deferred** — Tail-end root cleanup (drafts, gmail packets, `issue-1839-*`, `terminal-2-*`, `transcript_raw.json`, etc.): a single follow-on "tier-1 root-hygiene Pass 2" issue must be opened (or linked if it exists) before merge of this plan; this plan intentionally does not touch those files to keep the diff reviewable.

---

## Complexity: T2

**T2** — Multiple files (create + modify), deletions verified per-file, one new test module. No new code in `src/`; no new automation hooks. The coupling to #2460 raises coordination risk slightly above a pure T1 docs edit.
