# Plan for #3220: resolve 5 pre-existing dangling edges in the curated skill graph

> **Status:** adversarial-reviewed (r1 Claude MINOR → folded in)
> **Complexity:** T2
> **Date:** 2026-06-19
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/3220
> **Client:** N/A
> **Lane:** lane:claude
> **Depends on:** #3221 (Part A) merged — it adds `KNOWN_DANGLING_EDGE_REFS` + the (d) edge-integrity check this plan drives to empty.
> **Review artifacts:** scripts/review/results/2026-06-19-plan-3220-claude.md

---

## Resource Intelligence Summary

### What the dangling edges actually are (verified 2026-06-19)
`check-skill-index-coherence.py` (d) flagged 5 edge endpoints not defined as nodes. Existence in `.claude/skills`:
- **REAL skills, missing a node def → ADD node (4):** `engineering/marine-offshore/diffraction-analysis`, `engineering/marine-offshore/cathodic-protection`, `engineering/marine-offshore/risk-assessment`, `engineering/asset-integrity/fitness-for-service` — all have SKILL.md.
- **ABSENT → DELETE edge (1):** `eng/diffraction-spec-converter` (a WRK-240 skill that no longer exists; edge at graph lines ~998-1002, `to: diffraction-analysis`).

So this is predominantly **curate-the-missing-nodes**, not edge-deletion. The 5 edges among these endpoints (graph lines ~998-1025): 1 from the absent converter (delete); 4 among the real skills (cathodic-protection→fitness-for-service, cathodic-protection→risk-assessment, risk-assessment→fitness-for-service, risk-assessment→cathodic-protection) — all become valid once the 4 nodes exist.

### Id-form (verified)
The edges reference the **family-path** id form (`engineering/marine-offshore/diffraction-analysis`), which is also the `skill-index-full.yaml` id form. The new node ids MUST match the edges to resolve → use the family-path form. (The graph mixes this with a `<repo>/<skill>` form on other nodes — a pre-existing convention inconsistency, out of scope; possible follow-up.)

### Node schema (template: `digitalmodel/mooring-design`)
`id, repo, category, domain, sub_domains[], input_types[], output_types[], capabilities[], python_packages[]`. The 4 SKILL.md files carry `name` + `description`; the other fields are authored from each SKILL.md's content (domain = marine_offshore / asset_integrity; capabilities from the skill's stated scope).

### Gotcha
**#3214 carries `gate:completeness`** → when #3221 merges it will be reopened by the unconfigured gate (same as the swept batch). Opt #3214 out (remove `gate:completeness`) at close. (Standing: `COMPLETENESS_OWNERS` still unset.)

### Evidence
- `find .claude/skills -type d -name <s>`: 4 exist, `diffraction-spec-converter` absent.
- Edges at `.planning/skills/skills-knowledge-graph.yaml:998-1025` (5 edges; `source_file`/`note` present).
- Integrity check `KNOWN_DANGLING_EDGE_REFS` = exactly these 5 (#3221).

<!-- sources: issue + graph edges + 4 SKILL.md + node template + check-skill-index-coherence + tree existence = 6 -->

---

## Deliverable

The 4 real skills are curated as graph nodes (family-path ids matching their edges), the 1 dead edge from the absent converter is removed, `KNOWN_DANGLING_EDGE_REFS` is emptied, and the (d) edge-integrity check passes with an **empty allowlist** — the curated graph has zero dangling edges.

---

## Design

**PREFLIGHT (r1-F4):** confirm the graph reads `total_nodes: 43` before editing. If it reads 51, **#3221 is not merged — STOP** (wrong base; the allowlist/integrity check this plan empties don't exist pre-#3221).

**Line-based edits** (preserve formatting; ruamel reformats — proven in #3214 Part A).
1. **Add 4 node blocks** to the `nodes:` list, each authored from its SKILL.md:
   - id = family-path (`engineering/marine-offshore/diffraction-analysis`, `…/cathodic-protection`, `…/risk-assessment`, `engineering/asset-integrity/fitness-for-service`) — verified to match all 5 edges exactly (r1 PASS).
   - **List-form constraint (r1-F1, load-bearing):** `skill_graph.sh` only parses INLINE flow-lists for `sub_domains`/`input_types`/`output_types` (`input_types: [a, b]`) — block-lists are silently dropped. Author those **inline**; `capabilities` as a block-list (match the `mooring-design` template exactly).
   - **Faithful fields only (r1-F5):** `risk-assessment` + `diffraction-analysis` have empty `capabilities:` in their SKILL.md. Do NOT fabricate input/output taxonomies — keep those nodes minimal (id/repo/category/domain + a short capabilities list paraphrased from the SKILL.md Overview). `repo`: `digitalmodel` for diffraction-analysis (body cites digitalmodel modules); for risk-assessment ownership is unstated → pick conservatively or use the family's repo, don't invent.
   - **Domain pin (r1-F3):** `fitness-for-service` introduces a NEW `by_domain` bucket — pin `domain: asset_integrity` (underscore convention); expected new bucket in the regenerated index.
2. **Delete the 1 edge** block from `eng/diffraction-spec-converter` (lines ~998-1002).
3. **Empty `KNOWN_DANGLING_EDGE_REFS`** in `check-skill-index-coherence.py`.
4. **Regenerate** `skill-graph-index.yaml` (`skill_graph.sh --rebuild-index`).
5. **Update `stats:`** (total_nodes 43→47; total_edges 38→37; edge_type_counts for the deleted edge's type).
6. Verify: (a) coherence green; (d) integrity green with EMPTY allowlist; (c) determinism green; **(new, r1-F2)** re-run `skill_graph.sh --rebuild-index` → no diff vs the committed `skill-graph-index.yaml` (the (c) check only covers `skill-index-full.yaml`, NOT the graph-index — add a graph-index determinism test).

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Modify | `.planning/skills/skills-knowledge-graph.yaml` | +4 node defs, −1 dead edge, stats |
| Regenerate | `config/agents/skill-graph-index.yaml` | derived index |
| Modify | `scripts/enforcement/check-skill-index-coherence.py` | empty `KNOWN_DANGLING_EDGE_REFS` |
| Modify | `tests/enforcement/test_skill_graph_integrity.py` | assert empty allowlist + 4 nodes present + integrity green |
| Update | docs/plans/README.md | index |

---

## TDD Test List

| Test | Verifies | Expected |
|---|---|---|
| test_dangling_allowlist_emptied | `KNOWN_DANGLING_EDGE_REFS == set()` | empty |
| test_four_skills_now_nodes | the 4 ids defined as nodes | present |
| test_integrity_green_empty_allowlist | check_d passes with no allowlist | no failures |
| test_absent_converter_edge_removed | no edge references `eng/diffraction-spec-converter` | absent |
| test_new_nodes_basename_in_tree | (a) coherence still green | exit 0 |
| test_stats_total_nodes_47 | stats updated | total_nodes == len(nodes) == 47 |
| test_graph_index_regen_no_diff (r1-F2) | `skill_graph.sh --rebuild-index` == committed skill-graph-index.yaml (date line excluded) | no diff |
| test_ffs_node_domain_bucket (r1-F3) | fitness-for-service in by_domain[asset_integrity] | present |

---

## Acceptance Criteria

- [ ] 4 real skills added as graph nodes (family-path ids); 1 dead edge removed; `KNOWN_DANGLING_EDGE_REFS` emptied
- [ ] (d) integrity green with empty allowlist; (a)/(c) green; `skill-graph-index.yaml` regenerated; stats correct
- [ ] `uv run pytest tests/enforcement/ -q` green
- [ ] Review artifact posted

---

## Adversarial Review Summary

**r1 — Claude (adversarial subagent), 2026-06-19:** verdict **MINOR** (core mechanic verified sound). Folded in:

| # | Sev | Finding | Resolution |
|---|---|---|---|
| F1 | MAJOR-lean | `skill_graph.sh` only parses INLINE flow-lists for sub_domains/input/output_types → block-lists silently dropped | inline-list authoring constraint pinned |
| F2 | MAJOR-lean | (c) validates skill-index-full.yaml only — skill-graph-index.yaml regen is UNGATED | added a graph-index determinism test |
| F3 | MINOR | fitness-for-service introduces a NEW by_domain bucket | pin `domain: asset_integrity`; expected |
| F4 | MINOR | stats base: must be the post-#3221 43-node graph (main shows 51) | preflight `total_nodes==43` STOP-gate |
| F5 | MINOR | risk-assessment/diffraction-analysis have empty SKILL.md capabilities → don't fabricate fields | minimal faithful nodes; conservative repo |
| PASS | — | id-forms match all 5 edges; allowlist captures ALL dangling; no node-id collision; orphan node harmless; generator handles slashes | verified |

**r2 — Codex:** UNAVAILABLE (env timeout, repeated this session).

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | MINOR→addressed | inline-list + graph-index gate + domain pin + base preflight + no-fabrication |

---

## Risks and Open Questions

- **OPEN DECISION 1 — node id form:** family-path (`engineering/marine-offshore/…`, matches the edges + full index) — recommended — vs `<repo>/<skill>` (matches the other node convention but then the existing edges must also be repointed). Family-path is minimal + resolves the edges as-is.
- **OPEN DECISION 2 — the absent `diffraction-spec-converter`:** delete its edge (recommended; the skill is gone) vs investigate restoring the skill (out of scope).
- **Dependency:** must land AFTER #3221 (the allowlist + integrity check it empties live in #3221). Sequence: #3221 merge → #3220.
- **Risk — authored node fields:** sub_domains/types/capabilities are hand-authored from each SKILL.md; keep them faithful to the skill's stated scope (a node is metadata, not behavior — low blast radius).
- **Risk — ruamel reformat:** use line-based edits (Part A precedent).
- **Adjacent cleanup:** opt #3214 out of `gate:completeness` at close (else reopened).

## Complexity: T2

**T2** — graph node authoring (4) + edge deletion + allowlist empty + regen + tests; built on #3221's integrity check. Review = Claude inline (+ Codex if env permits).
