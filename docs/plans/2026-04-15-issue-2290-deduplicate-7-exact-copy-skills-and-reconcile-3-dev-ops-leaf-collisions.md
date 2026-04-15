# Plan for #2290: deduplicate 7 exact-copy skills and reconcile 3 dev/ops leaf collisions

> **Status:** plan-review
> **Complexity:** T2
> **Date:** 2026-04-15
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2290
> **Review artifacts:** scripts/review/results/2026-04-15-plan-2290-claude.md | ...-codex.md | ...-gemini.md

**Implementation is blocked pending adversarial review + user approval.**

---

## Resource Intelligence Summary

### Existing repo code

- Found: `.claude/skills/` — all 20 paths (10 pairs) confirmed present on disk. Live sha256 comparison shows **only 1 of 7 "exact-duplicate" pairs is byte-identical** (`corporate-tax-strategic-planning`). The remaining 6 pairs share canonical frontmatter names but have divergent file content, requiring diff/compare/merge before any deletion.
- Found: affected skill directories are not uniformly `SKILL.md`-only. Live directory inventory already shows auxiliary files in at least two planned-delete locations:
  - `.claude/skills/github/github-code-review/references/review-output-template.md`
  - `.claude/skills/mlops/research/dspy/references/examples.md`
  - `.claude/skills/mlops/research/dspy/references/modules.md`
  - `.claude/skills/mlops/research/dspy/references/optimizers.md`
  This means directory-level inventory/preservation is a hard requirement before any delete step.
- Found: `scripts/skills/detect_duplicate_skills.py` — deterministic detector for duplicate frontmatter names and leaf-directory collisions; the 2026-04-15 weekly audit run surfaced the 10 findings addressed by this issue.
- Found: `scripts/cron/skills-curation.sh` — cron wrapper for the weekly skills audit; this is the entrypoint that produces the audit JSON/Markdown artifacts used to identify these findings.
- Found: `.claude/agent-skills-map.yaml` contains skill-name references for `devtools/uv-package-manager` and `devtools/pyproject-toml`, proving that `.claude`-level wiring lies outside the original narrow grep scope and must be included in cleanup verification.
- Found: `operations/devtools/` — contains 9 skill subdirectories (ai-tool-assessment, background-service-manager, cli-productivity, docker, git-advanced, pyproject-toml, raycast-alfred, uv-package-manager, vscode-extensions) plus INDEX.md. Removing pyproject-toml and uv-package-manager will **not** empty this directory; the issue's conditional `operations/devtools/` removal step is inapplicable.

### Standards

| Standard | Status | Source |
|---|---|---|
| Weekly skills audit classification/ranking policy | done (landed) | `#2282` — locked classification and ranking policy |
| Deterministic weekly audit implementation | done (landed) | `#2281` — v1 weekly audit script |
| Skills governance umbrella | done (landed) | `#2280` — parent governance plan |

### LLM Wiki pages consulted

- No relevant wiki pages; this is a mechanical skill-tree hygiene issue grounded in audit output and repo structure.

### Documents consulted

- `docs/plans/2026-04-14-issue-2280-weekly-skill-ecosystem-audit-and-consolidation-maintenance-loop.md` — parent governance plan defining the audit contract, classification ladder, and canonical identity rule (frontmatter `name` wins over leaf name). The classification `exact-duplicate` and `generic-leaf-collision` used by #2290 originate from this policy.
- `docs/plans/2026-04-14-issue-2282-lock-classification-and-ranking-policy-for-weekly-skills-audit.md` — locked the severity/confidence rubric and finding-key schema that the weekly audit uses to surface the 10 findings addressed here.
- `docs/plans/2026-04-14-issue-2281-implement-v1-weekly-audit-for-existing-skills-curation-workflow.md` — child implementation plan for the deterministic audit script; the JSON output from this script is the primary evidence source for #2290.
- GitHub issue #2290 — scope, keep/delete table, acceptance criteria, and out-of-scope boundaries.
- GitHub issue #2019 — email skill consolidation (open); explicitly out of scope for #2290.
- GitHub issue #2083 — session-corpus-audit dedup (open); explicitly out of scope for #2290.
- GitHub issue #2214 — architecture doc split / legacy wrapper redirects (open); explicitly out of scope for #2290.

### Gaps identified

- No existing merge/reconciliation tooling for skill pairs with divergent content — the 6 non-identical "duplicate" pairs require manual or semi-automated diff/merge that does not yet exist as a script.
- No regression test currently validates that the 10 specific findings from the 2026-04-15 audit are resolved after implementation.
- No cross-reference scan is currently wired to verify zero dangling references after skill directory removal.

<!-- Verification: distinct sources >= 3. Current count: 10 (6 repo code/paths, 3 prior plans, 4 GitHub issues) -->

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-04-15-issue-2290-deduplicate-7-exact-copy-skills-and-reconcile-3-dev-ops-leaf-collisions.md` |
| Parent issue | #2290 |
| Prior work — governance | #2280 (landed) |
| Prior work — audit implementation | #2281 (landed) |
| Prior work — policy lock | #2282 (landed) |
| Weekly audit wrapper | `scripts/cron/skills-curation.sh` |
| Duplicate detector | `scripts/skills/detect_duplicate_skills.py` |
| Skill paths (7 exact-duplicate pairs) | see Files to Change table below |
| Skill paths (3 leaf-collision pairs) | see Files to Change table below |
| Plan review — Claude | `scripts/review/results/2026-04-15-plan-2290-claude.md` |
| Plan review — Codex | `scripts/review/results/2026-04-15-plan-2290-codex.md` |
| Plan review — Gemini | `scripts/review/results/2026-04-15-plan-2290-gemini.md` |
| Docs index update | `docs/plans/README.md` |
| Future: regression test | `tests/skills/test_issue_2290_dedup_regression.py` (to be created during implementation) |
| Future: directory inventory fixture/report | `.planning/quick/issue-2290-directory-inventory.md` or equivalent implementation-time artifact |
| Future: affected .claude mappings | `.claude/agent-skills-map.yaml`, `.claude/skill-registry.yaml`, and any impacted skill index files |
| Future: cross-agent adapter surfaces | `.codex/**`, `.gemini/**`, `.hermes/**`, `AGENTS.md`, `.mcp.json` (scan/update only if they contain deleted-path references or symlinks) |

---

## Deliverable

A net reduction of 10 skill directories from `.claude/skills/` — 7 stale duplicate copies removed and 3 leaf-collision pairs merged into their canonical locations — with zero dangling references and zero audit findings for the 10 resolved skill names.

---

## Pseudocode

```text
deduplicate_and_reconcile():
    for each candidate duplicate/collision directory pair:
        inventory the full directory tree, not just SKILL.md
        record explicit disposition for every non-SKILL file (keep, move, merge, or delete)

    for each of the 7 "exact-duplicate" pairs:
        diff canonical_path vs stale_path
        if byte-identical and directory inventory proves no unique auxiliary files:
            delete stale_path directory
        else:
            compare content and auxiliary files
            merge only loss-preventing unique material from stale into canonical
            if diffs suggest meaningful specialization or unclear conflict resolution:
                stop and escalate for human review instead of rewriting broadly
            preserve canonical frontmatter identity and structural validity
            delete stale_path directory only after merge + inventory disposition verified

    for each of the 3 leaf-collision pairs:
        diff canonical_path vs merge_from_path
        merge any unique content or auxiliary references from merge_from into canonical
        if diffs suggest meaningful specialization or unclear conflict resolution:
            stop and escalate for human review instead of rewriting broadly
        validate canonical skill still parses cleanly
        delete merge_from directory

    search for deleted-path references across .claude/, .claude/rules/, .codex/, .gemini/, .hermes/, AGENTS.md, .mcp.json, config/, and scripts/
    update mappings/registries and any skill index files to point to canonical paths

    remove only parent directories made empty directly by this issue

    run scripts/cron/skills-curation.sh (or underlying audit)
    assert zero findings for the 10 resolved skill names and no broken skill parsing
```

---

## Files to Change

### Now (planning phase — this PR)

| Action | Path | Reason |
|---|---|---|
| Create | `docs/plans/2026-04-15-issue-2290-deduplicate-7-exact-copy-skills-and-reconcile-3-dev-ops-leaf-collisions.md` | canonical plan artifact |
| Update | `docs/plans/README.md` | add plan index row for #2290 |

### Future (implementation phase — after plan approval)

**Exact-duplicate pairs — delete stale copy (diff/merge first if not byte-identical)**

| Action | Keep (canonical) | Delete (stale) | Byte-identical? |
|---|---|---|---|
| Delete | `.claude/skills/coordination/cross-agent-skill-audit/` | `.claude/skills/cross-agent-skill-audit/` | No — diff required |
| Delete | `.claude/skills/development/github/code-review/` | `.claude/skills/github/github-code-review/` | No — diff required |
| Delete | `.claude/skills/business/productivity/obsidian/` | `.claude/skills/note-taking/obsidian/` | No — diff required |
| Delete | `.claude/skills/business-finance/corporate-tax-strategic-planning/` | `.claude/skills/corporate-tax-strategic-planning/` | **Yes** — safe direct delete |
| Delete | `.claude/skills/development/planning/writing-plans/` | `.claude/skills/software-development/writing-plans/` | No — diff required |
| Delete | `.claude/skills/ai/prompting/dspy/` | `.claude/skills/mlops/research/dspy/` | No — diff required |
| Delete | `.claude/skills/development/systematic-debugging/` | `.claude/skills/software-development/systematic-debugging/` | No — diff required |

**Leaf-collision pairs — merge unique content into canonical, then delete merge-from**

| Action | Canonical | Merge-from | Notes |
|---|---|---|---|
| Merge+Delete | `.claude/skills/development/github/code-review/` | `.claude/skills/software-development/code-review/` | Different content; merge needed |
| Merge+Delete | `.claude/skills/development/devtools/pyproject-toml/` | `.claude/skills/operations/devtools/pyproject-toml/` | Different content; merge needed |
| Merge+Delete | `.claude/skills/development/devtools/uv-package-manager/` | `.claude/skills/operations/devtools/uv-package-manager/` | Different content; merge needed |

**Reference cleanup**

| Action | Scope | Reason |
|---|---|---|
| Inventory+Fix | `.claude/**`, `.claude/rules/**`, `.codex/**`, `.gemini/**`, `.hermes/**`, `AGENTS.md`, `.mcp.json`, `config/**`, `scripts/**` | Update any mappings, registries, index files, symlinks, or references to deleted paths |

**Note:** `operations/devtools/` contains 7 other skill directories beyond the 2 being removed and will NOT be empty after this work — no directory removal needed.

---

## TDD Test List

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| `test_directory_inventory_captures_auxiliary_files` | Every affected directory pair is inventoried before deletion/merge and all non-`SKILL.md` files receive an explicit disposition | Inventory of 10 affected directory pairs | Inventory artifact lists extra files and keep/move/delete decision for each |
| `test_no_exact_duplicate_findings_for_resolved_skills` | Weekly audit produces zero `exact-duplicate` findings for the 7 resolved canonical names | Run `detect_duplicate_skills.py` or weekly audit | Zero findings matching: cross-agent-skill-audit, github-code-review, obsidian, corporate-tax-strategic-planning, writing-plans, dspy, systematic-debugging |
| `test_no_leaf_collision_findings_for_resolved_skills` | Weekly audit produces zero `generic-leaf-collision` findings for the 3 resolved pairs | Run audit | Zero findings matching: code-review/github-code-review, pyproject-toml, uv-package-manager |
| `test_stale_paths_do_not_exist` | All 10 stale/merge-from directories are absent from disk | `os.path.exists()` on each deleted path | All return `False` |
| `test_canonical_paths_exist_and_have_content` | All 10 canonical paths still exist with non-empty SKILL.md | `os.path.exists()` + file size check | All return `True`, size > 0 |
| `test_canonical_skills_parse_cleanly_after_merge` | Surviving canonical skills remain structurally valid after merge | Parse canonical `SKILL.md` files for frontmatter / required structure | All parse without error |
| `test_no_dangling_references` | No file in `.claude/`, `.claude/rules/`, `.codex/`, `.gemini/`, `.hermes/`, `AGENTS.md`, `.mcp.json`, `config/`, or `scripts/` references a deleted path | Search for each of 10 deleted directory basepaths | Zero matches |
| `test_no_dangling_cross_agent_skill_symlinks_or_paths` | Other agent adapter directories do not retain broken symlinks or dead path references to removed skills | Walk `.codex/`, `.gemini/`, `.hermes/` and inspect path-bearing config/files | Zero broken symlinks and zero deleted-path references |
| `test_merged_content_preservation_matches_inventory` | For the 6 non-identical duplicate pairs and 3 collision pairs, all inventoried unique content/assets are preserved in canonical locations | Pre-merge inventory + post-merge canonical tree | All recorded preserve/move items accounted for |
| `test_audit_finding_keys_cleared_for_target_pairs` | The exact target findings disappear by key/path set, not just by loose skill names | Baseline JSON vs post-change JSON | No matching finding keys/path sets remain for the 10 targets |
| `test_operations_devtools_intact` | `operations/devtools/` still contains its remaining 7 skill subdirectories | `ls operations/devtools/` | ai-tool-assessment, background-service-manager, cli-productivity, docker, git-advanced, raycast-alfred, vscode-extensions all present |
| `test_empty_parent_directories_removed_only_when_created_by_this_issue` | Parent-directory cleanup is limited to directories made empty by this issue | Post-change tree walk | Only directly emptied parents removed |

---

## Acceptance Criteria

- [ ] A directory-level inventory/disposition is captured for every affected pair before deletion or merge, including any auxiliary files under `references/`, `scripts/`, or similar subdirectories
- [ ] All 7 stale exact-duplicate directories removed from `.claude/skills/`
- [ ] All 3 leaf-collision merge-from directories removed from `.claude/skills/`
- [ ] For the 6 non-identical duplicate pairs: diff reviewed and any unique content or auxiliary files merged/preserved in canonical locations before deletion
- [ ] For the 3 collision pairs: content merged into canonical, no information lost
- [ ] Search for every deleted path returns zero hits across `.claude/`, `.claude/rules/`, `.codex/`, `.gemini/`, `.hermes/`, `AGENTS.md`, `.mcp.json`, `config/`, and `scripts/`
- [ ] Running `bash scripts/cron/skills-curation.sh` (or the underlying weekly audit) produces zero findings for the 10 resolved skill names
- [ ] Canonical copies remain structurally valid and content-complete after merge
- [ ] PR diff is net-negative in file count (expect -10 SKILL.md files minimum, plus any removed auxiliary files that are intentionally retired)
- [ ] `operations/devtools/` retains its remaining 7 skill subdirectories
- [ ] Empty parent-directory cleanup, if performed, is limited to directories made empty directly by this issue
- [ ] Regression tests pass: `uv run pytest tests/skills/test_issue_2290_dedup_regression.py -v`
- [ ] Review artifacts posted to `scripts/review/results/`

---

## Adversarial Review Summary

<!-- Filled in after Step 4 completes. Do not post to GitHub until this section is populated. -->

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | UNAVAILABLE | Second-wave interactive Claude re-review attempted via tmux, but again did not return a bounded final artifact in-session |
| Codex | APPROVE | Prior blockers addressed; only bounded implementation caution remains around supporting-file placement |
| Gemini | MINOR | Widen deleted-path search/test scope to cross-agent adapter surfaces and root docs/config; clarify manual loss-preventing merge behavior |

**Overall result:** PASS WITH MINOR NOTES — approval-ready after incorporating Gemini's non-blocking scope expansion notes

Revisions made based on review:
- Added cross-agent adapter surfaces (`.codex/**`, `.gemini/**`, `.hermes/**`) plus `AGENTS.md` and `.mcp.json` to artifact map, cleanup scope, tests, acceptance criteria, and risks
- Clarified that merge behavior must stop/escalate on meaningful specialization or unclear conflicts rather than broad rewriting
- Added explicit cross-agent dangling-symlink / deleted-path validation test
- Preserved the first-wave safety improvements (directory inventory, auxiliary-file preservation, structural validity, exact finding-key regression)

**Re-review status:** complete — plan is ready for `status:plan-review`.

---

## Risks and Open Questions

- **Risk: "exact-duplicate" label is misleading for 6 of 7 pairs.** Live sha256 verification shows only `corporate-tax-strategic-planning` is byte-identical. The other 6 pairs share canonical frontmatter names but have divergent file content. Implementation must diff each pair and merge unique content before deleting — a blind `rm` risks information loss. The issue title uses "exact-copy" but the plan treats these as **canonical-name duplicate reconciliation** requiring compare-before-delete.
- **Risk: content divergence may reveal intentional specialization.** Some "duplicate" pairs may have diverged intentionally (e.g., one copy evolved for a specific agent context). During implementation, if a diff reveals substantial unique content in the stale copy, flag for user review rather than auto-merging.
- **Risk: hidden references.** Deleted paths may be referenced in skill INDEX.md files, agent routing configs, or session logs not covered by the original narrow grep scope. Implementation must search `.claude/`, `.claude/rules/`, `.codex/`, `.gemini/`, `.hermes/`, `AGENTS.md`, `.mcp.json`, config, scripts, and any skill index files before deletion is complete.
- **Risk: auxiliary-file loss outside `SKILL.md`.** Live inventory already found extra files under `.claude/skills/github/github-code-review/references/` and `.claude/skills/mlops/research/dspy/references/`. Deleting directories without explicit file-by-file disposition would silently lose real skill assets even if the weekly audit passes.
- **Risk: structural merge breakage.** Some `SKILL.md` files can have meaningful frontmatter and structured sections; merges must preserve canonical identity and parse cleanly after reconciliation.
- **Risk: `operations/devtools/` NOT emptied.** The issue mentions conditional removal of `operations/devtools/` if empty after pyproject-toml + uv-package-manager removal. Live inspection shows 7 other skill directories remain — this conditional step is **inapplicable** and should be skipped.
- **Open: merge strategy for collision pairs.** The 3 leaf-collision pairs have different content under the same functional name. The plan should limit merge work to loss-preventing reconciliation, not broad editorial harmonization.
- **Open: should stale parent directories be removed?** If parent directories become empty because of this issue, cleanup should be allowed only for those directly emptied parents; broader taxonomy cleanup is out of scope.

---

## Scope Boundaries

### In scope (this issue)

- The 7 canonical-name duplicate pairs listed in the issue
- The 3 leaf-collision pairs listed in the issue
- Reference cleanup for deleted paths
- Regression test creation
- Audit verification

### Explicitly out of scope (covered by other issues)

| Topic | Covered by | Why excluded |
|---|---|---|
| Email skill consolidation (gmail, email-management, etc.) | #2019 | Separate domain; different merge complexity |
| session-corpus-audit dedup | #2083 | Different finding class; separate scoping |
| Architecture doc split / legacy wrapper redirects | #2214 | Broader structural refactor beyond skill dedup |
| Adjacent-specialization findings (openfoam vs orcawave, etc.) | Future issue TBD | Require domain judgment, not mechanical dedup |
| Remaining leaf collisions not in scope (competitive-analysis, naval-architecture, etc.) | Future issue TBD | Cross domain boundaries; separate scoping needed |
| Top-level directory taxonomy refactoring | Future issue TBD | This issue removes orphans and merges within existing trees only |

---

## Complexity: T2

**T2** — mechanical but multi-file dedup across 10 skill pairs, requiring diff/compare for 9 of 10 pairs, content merging for at least 3 collision pairs, reference cleanup, and regression test creation. No architecture-wide changes, but not trivial single-file work either.
