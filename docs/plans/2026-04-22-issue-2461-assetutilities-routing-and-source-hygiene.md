# Plan for #2461: Canonical routing surfaces and source-hygiene cleanup for assetutilities

> **Status:** draft (adversarial-reviewed r1 — Claude MINOR; Codex/Gemini PENDING per permission-gate fallback `feedback_permission_gate_blocks_cross_review.md`; r2 tightening applied 2026-04-23 to address Claude F1/F2/F3/F4/F7 and parallel the #2462 r2 hardening)
> **Complexity:** T2
> **Date:** 2026-04-22 (r2 tightening 2026-04-23)
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2461
> **Review artifacts:** scripts/review/results/2026-04-22-plan-2461-claude.md | scripts/review/results/2026-04-22-plan-2461-codex.md | scripts/review/results/2026-04-22-plan-2461-gemini.md
> **Contract dependency (HARD GATE):** implementation of this plan MUST NOT begin until (a) #2460 (tier-1 indexing and code-placement contract) has reached `status:plan-approved` AND (b) #2460's contract doc has been drafted to the point where the canonical machine-readable registry filename, the operator-map host location (workspace-hub `docs/maps/` vs per-repo `docs/maps/`), the required routing-surface set, and the source-hygiene rules are textually locked (either in the #2460 plan or in `docs/standards/TIER1_INDEXING_AND_CODE_PLACEMENT_CONTRACT.md` on main). If any of those items moves in #2460, this plan is re-patched and re-reviewed before implementation.
> **Sibling scope boundary:** #2462 owns `digitalmodel` repo-wide routing; #2463 owns `aceengineer-website`; #2464 owns `workspace-hub` curation / `docs/CONTENT_INDEX.md` hygiene; #2465 owns daily freshness automation; #2460 owns the contract itself. This plan edits ONLY `assetutilities/**` files plus, if #2460 ratifies workspace-hub host, the single workspace-hub file `docs/maps/assetutilities-operator-map.md` and the workspace-hub regression guard `tests/docs/test_banned_stale_references.py`. It does not rewrite sibling repos' routing surfaces and does not touch `docs/CONTENT_INDEX.md` or the repo-root cleanup surface.

---

## Resource Intelligence Summary

### Existing repo code
- Found: `assetutilities/AGENTS.md` — already close to the contract shape (lists real entry points, real key modules, real test command). Light rewrite only.
- Found: `assetutilities/README.md` (1592 bytes, 2025-03-25) — stale, not trustworthy as a current architecture guide (per scorecard).
- Found: `assetutilities/MODULE_STRUCTURE.md` (2025-08-11) — actively misdirects: it claims `core/` and `utils/` directories that do not exist in `src/assetutilities/`, and it omits real directories (`common/`, `constants/`, `base_configs/`, `tools/`, `units/`, `calculations/`, `math_helpers.py`, `engine.py`, `calculation.py`).
- Found: `assetutilities/src/assetutilities/` actually contains: `agent_os/, base_configs/, calculations/, cli/, common/, constants/, devtools/, modules/, tools/, units/`, plus `engine.py, calculation.py, math_helpers.py, __init__.py, __main__.py`.
- Found: tracked backup artifacts under package paths:
  - `src/assetutilities/common/ApplicationManager.py.bak`
  - `src/assetutilities/common/ApplicationManager.py.orig`
  - `src/assetutilities/common/file_management.py.bak`
  - `src/assetutilities/common/file_management.py.orig`
- Found: Windows test-harness noise tracked in `tests/`: `visualizations_tests.bat`, `visualizations_tests_temp.bat` — both look like Windows-only scratch helpers in a shared source tree.
- Gap: no `assetutilities/docs/README.md` exists — `ls` returns "No such file or directory".
- Gap: no repo-wide operator map under `docs/maps/` tied to assetutilities (workspace-hub `docs/maps/` has only `digitalmodel-orcawave-orcaflex-operator-map.md`).
- Gap: no canonical machine-readable module/domain registry exists inside the assetutilities repo.
- Gap: no pre-commit or CI check currently guards against `*.bak`/`*.orig` re-entering tracked source paths.

### Standards
| Standard | Status | Source |
|---|---|---|
| Tier-1 indexing and code-placement contract (draft, being landed in #2460) | draft upstream | `docs/plans/2026-04-22-issue-2460-tier1-indexing-and-code-placement-contract.md` |
| Control-plane repo discovery contract | existing baseline | `docs/standards/CONTROL_PLANE_CONTRACT.md` |
| Starter repo taxonomy expectations | existing baseline | `docs/standards/FILE_STRUCTURE_TAXONOMY.md` |
| Data placement decision rule (bulk vs repo) | existing baseline | `docs/standards/DATA_PLACEMENT.md` |

### LLM Wiki pages consulted
- Not applicable — this is a repo-organization/hygiene issue, not a domain-knowledge issue.

### Documents consulted
- GitHub issue #2461 — body defines the specific deliverables: current README, canonical `docs/README.md`, operator map, registry, alignment with observed layout, backup-artifact removal, curated-vs-raw inventory boundary.
- `docs/reports/2026-04-22-tier-1-indexing-scorecard.md` — ranks assetutilities at 8/20 (weakest tier-1 repo) and calls out: stale README, no `docs/README.md`, misaligned `MODULE_STRUCTURE.md`, weak source/test parity, tracked backup artifacts.
- `docs/plans/2026-04-22-issue-2460-tier1-indexing-and-code-placement-contract.md` — T1 contract draft that defines required routing surfaces per tier-1 repo; this plan conforms to that contract.
- `docs/plans/2026-04-22-overnight-tier1-knowledge-beef-up-pack.md` — overnight coordination frame; confines this plan's writes to `docs/plans/2026-04-22-issue-2461-*.md`, `docs/plans/README.md` (only the 2461 row), `scripts/review/results/*2461*`, and the T2 summary report.
- Related parent/umbrella issues #2397 and #1962 — broader repo-organization and tier-1 refactor umbrellas; #2461 is intentionally narrow to the assetutilities repo.

### Gaps identified
- `docs/README.md` entry point missing — nothing routes an incoming issue into code/tests/docs locations.
- `docs/maps/assetutilities-operator-map.md` missing — no curated mapping from "issue topic" to source/tests/docs paths.
- No canonical machine-readable module/domain registry file exists under the assetutilities repo.
- `MODULE_STRUCTURE.md` misaligned with observed layout (see stale claims above).
- `README.md` not trustworthy as current architecture guide.
- Tracked `.bak`/`.orig` artifacts in `src/assetutilities/common/`.
- `.bat` Windows scratch test scripts in `tests/`.
- No curated-vs-raw inventory boundary in the repo (no stated rule about what `docs/` subtrees are routing surfaces versus supporting material).
- No regression guard preventing re-entry of backup artifacts or re-introduction of stale directory claims.

### Evidence (embedded verification)

**Issue statuses** (verified 2026-04-22 via `gh issue view` in this session):
- `#2461` — OPEN — `chore(assetutilities): canonical routing surfaces and source-hygiene cleanup for tier-1 issue work`
- `#2460` — OPEN — `feat(repo-organization): tier-1 indexing and code-placement contract` (upstream contract dependency)
- `#2397` — OPEN — `epic(repo-organization): canonical folder structure and refactor contract across tier-1 repos` (cited by #2461 body)
- `#1962` — OPEN — `FEATURE: Tier-1 Repo Ecosystem Refactoring` (cited by #2461 body)

**File existence** (verified 2026-04-22 via `ls`):
- EXISTS: `assetutilities/AGENTS.md`
- EXISTS: `assetutilities/README.md`
- EXISTS: `assetutilities/MODULE_STRUCTURE.md`
- EXISTS: `assetutilities/docs/` (directory only, no README.md child)
- EXISTS: `assetutilities/src/assetutilities/common/ApplicationManager.py.bak`
- EXISTS: `assetutilities/src/assetutilities/common/ApplicationManager.py.orig`
- EXISTS: `assetutilities/src/assetutilities/common/file_management.py.bak`
- EXISTS: `assetutilities/src/assetutilities/common/file_management.py.orig`
- EXISTS: `assetutilities/tests/visualizations_tests.bat`
- EXISTS: `assetutilities/tests/visualizations_tests_temp.bat`
- MISSING (this plan creates): `assetutilities/docs/README.md`
- MISSING (this plan creates): the canonical assetutilities operator map at the host/path ratified by #2460 — default conditional on #2460 ratification is `docs/maps/assetutilities-operator-map.md` (workspace-hub), following the pattern already set by `docs/maps/digitalmodel-orcawave-orcaflex-operator-map.md`; if #2460 picks per-repo `docs/maps/`, the artifact relocates and this plan is re-patched before implementation
- MISSING (this plan creates): a canonical machine-readable module/domain registry inside the assetutilities repo (exact filename deferred to #2460 unless #2460 explicitly delegates to child issues)

**Line excerpts — stale `MODULE_STRUCTURE.md` claims vs observed layout**:
```
# MODULE_STRUCTURE.md (claimed)
├── core/                 # Core functionality
├── utils/                # Utilities
├── devtools/             # Development tools
└── modules/              # Feature modules
```
```
# ls src/assetutilities/ (observed 2026-04-22)
agent_os/  base_configs/  calculation.py  calculations/  cli/  common/
constants/ devtools/      engine.py       __init__.py    __main__.py
math_helpers.py           modules/        __pycache__    py.typed
tests/     tools/         units/          UV_SETUP.md
```

**Gap proofs**:
- `ls assetutilities/docs/README.md` → `No such file or directory` → confirms canonical docs entry missing.
- `ls docs/maps/assetutilities-operator-map.md` → `No such file or directory` → confirms operator map missing.
- `git ls-files ':(glob)**/*.bak' ':(glob)**/*.orig'` inside `assetutilities/` → returns exactly the four backup files listed above → confirms source-path pollution.

<!-- Source count: 6 distinct (issue body + scorecard + #2460 plan + overnight pack + standards + observed tree). -->

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-04-22-issue-2461-assetutilities-routing-and-source-hygiene.md` |
| Canonical docs entry point (new, nested repo) | `assetutilities/docs/README.md` |
| Current-state package map (rewrite/replace) | `assetutilities/MODULE_STRUCTURE.md` |
| Repo README rewrite | `assetutilities/README.md` |
| Operator map (host/path per #2460 — default `docs/maps/assetutilities-operator-map.md` in workspace-hub if #2460 ratifies that host) | `docs/maps/assetutilities-operator-map.md` (conditional on #2460) |
| Machine-readable module registry (path shape defined by #2460) | `assetutilities/<registry path per #2460 contract>` |
| Tests | `assetutilities/tests/docs/test_assetutilities_routing_contract.py`, `assetutilities/tests/hygiene/test_no_backup_artifacts_tracked.py` |
| Workspace-hub regression guard (curated stale-reference) | `tests/docs/test_banned_stale_references.py` (extend coverage) |
| Plan index update | `docs/plans/README.md` (only the #2461 row) |
| Plan review — Claude | `scripts/review/results/2026-04-22-plan-2461-claude.md` |
| Plan review — Codex | `scripts/review/results/2026-04-22-plan-2461-codex.md` |
| Plan review — Gemini | `scripts/review/results/2026-04-22-plan-2461-gemini.md` |

---

## Deliverable

A trustworthy set of canonical routing surfaces for `assetutilities` — current README, canonical `docs/README.md`, workspace-level operator map at `docs/maps/assetutilities-operator-map.md`, machine-readable registry at the path shape defined by #2460, an aligned `MODULE_STRUCTURE.md`, a curated-vs-raw inventory boundary statement — plus source-hygiene cleanup that removes the four tracked `.bak`/`.orig` artifacts and the two `.bat` scratch test helpers, with regression guards preventing re-entry. After this issue, an incoming assetutilities-scoped GitHub issue can be routed to a source/tests/docs location without rediscovery.

---

## Pseudocode

```text
function update_routing_surfaces():
    rewrite assetutilities/README.md with current architecture only (no legacy claims, no stale directory names)
    create assetutilities/docs/README.md as canonical entry point:
        link to AGENTS.md, README.md, operator map, module registry
        include code/tests/docs routing table keyed on common issue types
        state curated-vs-raw inventory boundary explicitly
    rewrite assetutilities/MODULE_STRUCTURE.md to match the observed src/assetutilities/ tree:
        list: agent_os/, base_configs/, calculations/, cli/, common/, constants/,
              devtools/, modules/, tools/, units/, plus top-level files engine.py, calculation.py, math_helpers.py
        drop non-existent core/ and utils/ claims
        correct the file-placement rules table to reference real directories only
    create docs/maps/assetutilities-operator-map.md (workspace-hub hosted, following the digitalmodel-orcawave-orcaflex pattern):
        columns: module | source path | tests path | related docs path | typical issue labels | key dependencies
        include a row for each of the 10 observed top-level source directories
        link depends_on relationship to upstream consumers such as digitalmodel

function create_machine_readable_registry():
    once #2460 lands the required registry filename convention, create the assetutilities registry at that path
    cover module/domain ownership, entry point, stability tier
    source of truth must match the operator map

function hygiene_cleanup():
    # F4 + F7: discovery before deletion — if any hit, reclassify the deletion as a move/rename or stop and surface for review
    assert grep -rn 'ApplicationManager\.py\.bak' src/ tests/ scripts/ docs/ .github/ returns no hits
    assert grep -rn 'ApplicationManager\.py\.orig' src/ tests/ scripts/ docs/ .github/ returns no hits
    assert grep -rn 'file_management\.py\.bak' src/ tests/ scripts/ docs/ .github/ returns no hits
    assert grep -rn 'file_management\.py\.orig' src/ tests/ scripts/ docs/ .github/ returns no hits
    assert grep -rn 'visualizations_tests' . (across both workspace-hub and the assetutilities nested repo, excluding the tracked files themselves) returns no hits
    # only after all five grep checks return empty may the deletions proceed:
    git rm src/assetutilities/common/ApplicationManager.py.bak
    git rm src/assetutilities/common/ApplicationManager.py.orig
    git rm src/assetutilities/common/file_management.py.bak
    git rm src/assetutilities/common/file_management.py.orig
    git rm tests/visualizations_tests.bat
    git rm tests/visualizations_tests_temp.bat
    add repo .gitignore entries: *.bak, *.orig
    add pre-commit / CI hygiene test that fails if any tracked file matches *.bak / *.orig under src/**
    document hygiene rules in assetutilities/docs/README.md and link from AGENTS.md

function implement_with_tdd():
    write tests first (see TDD Test List)
    confirm tests fail against current tree
    apply doc rewrites (README, docs/README.md, MODULE_STRUCTURE.md)
    apply operator map creation under docs/maps/
    apply registry creation per #2460 shape
    apply hygiene cleanup (git rm + gitignore + guard test)
    rerun targeted tests until green
    extend workspace-hub tests/docs/test_banned_stale_references.py to cover the new curated assetutilities docs
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Modify | `assetutilities/README.md` | Replace stale architecture claims with a current-state, trust-worthy README. |
| Create | `assetutilities/docs/README.md` | Canonical docs entry point, required by #2460 contract. |
| Modify | `assetutilities/MODULE_STRUCTURE.md` | Align with the observed `src/assetutilities/` layout; drop `core/` and `utils/` claims. |
| Create | operator map at host/path per #2460 — default `docs/maps/assetutilities-operator-map.md` in workspace-hub | Canonical operator map for assetutilities; host location is authoritative per #2460 contract. If #2460 picks per-repo hosting, the artifact moves to `assetutilities/docs/maps/assetutilities-operator-map.md` and this plan is re-patched first. |
| Create | `assetutilities/<registry path per #2460>` | Canonical machine-readable module/domain registry. |
| Delete | `assetutilities/src/assetutilities/common/ApplicationManager.py.bak` | Remove tracked backup artifact from source path. |
| Delete | `assetutilities/src/assetutilities/common/ApplicationManager.py.orig` | Remove tracked backup artifact from source path. |
| Delete | `assetutilities/src/assetutilities/common/file_management.py.bak` | Remove tracked backup artifact from source path. |
| Delete | `assetutilities/src/assetutilities/common/file_management.py.orig` | Remove tracked backup artifact from source path. |
| Delete | `assetutilities/tests/visualizations_tests.bat` | Remove Windows scratch helper from shared tests tree. |
| Delete | `assetutilities/tests/visualizations_tests_temp.bat` | Remove Windows scratch helper from shared tests tree. |
| Modify | `assetutilities/.gitignore` | Add `*.bak`, `*.orig` patterns. |
| Create | `assetutilities/tests/docs/test_assetutilities_routing_contract.py` | Asserts canonical surfaces exist, operator map has all observed domains, MODULE_STRUCTURE matches observed tree. |
| Create | `assetutilities/tests/hygiene/test_no_backup_artifacts_tracked.py` | Fails if any tracked file under `src/**` matches `*.bak` or `*.orig`. |
| Modify | `tests/docs/test_banned_stale_references.py` | Bring new curated assetutilities docs into the workspace-hub stale-reference guard. |
| Update | `docs/plans/README.md` | Add the #2461 plan row (only the 2461 row, per overnight pack write fence). |

---

## TDD Test List

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| `test_docs_readme_exists` | `assetutilities/docs/README.md` is present | `assetutilities/docs/README.md` | file exists |
| `test_docs_readme_routes_common_issue_types` | `docs/README.md` contains a routing table with at least {issue type → source path → tests path → docs path} columns | docs/README.md text | required columns present |
| `test_docs_readme_states_curated_vs_raw_boundary` | `docs/README.md` names at least three curated routing surfaces (for example `docs/README.md`, the operator-map link, the registry link) AND at least one raw/supporting subtree (for example `docs/sub_automation/` or `docs/sub_data/`). Test asserts both halves of the partition are present — hand-waving single-sentence rules fail. | docs/README.md text | curated set ≥3 items AND raw set ≥1 item, both bound to named paths |
| `test_operator_map_exists` | `docs/maps/assetutilities-operator-map.md` is present in workspace-hub | path | file exists |
| `test_operator_map_covers_all_top_level_source_dirs` | Operator map has one row per top-level directory under `src/assetutilities/` that is a Python package (has `__init__.py`); expected set is derived from `git ls-tree src/assetutilities` at test time — not hard-coded in the test body | observed live tree vs operator map text | exact set match |
| `test_module_structure_matches_observed_tree` | `MODULE_STRUCTURE.md` lists exactly the top-level Python-package directories observed under `src/assetutilities/` at test time (derived from `git ls-tree`, not hard-coded), and does not reference any directory absent from the live tree (including specifically `core/` or `utils/`) | MODULE_STRUCTURE.md text vs live tree | forbidden names absent; observed names present; set match |
| `test_readme_no_stale_directory_claims` | `README.md` does not reference `core/` or `utils/` as if they exist | README.md text | forbidden strings absent |
| `test_registry_exists` | Canonical machine-readable registry file exists at the path shape defined by #2460 | registry path | file exists |
| `test_registry_covers_all_top_level_source_dirs` | Registry entries cover every top-level Python-package directory observed under `src/assetutilities/` at test time (expected set derived from `git ls-tree src/assetutilities`, not hard-coded) | registry vs live tree | exact set match |
| `test_no_tracked_backup_artifacts_under_src` | Fails if any tracked file matches `*.bak` or `*.orig` anywhere under `src/**` | `git ls-files` output | empty match set |
| `test_no_bat_scratch_files_in_tests` | Fails if `tests/*.bat` scratch helpers re-enter the tracked tree | `git ls-files tests/*.bat` | empty |
| `test_gitignore_blocks_backup_patterns` | `.gitignore` contains both `*.bak` and `*.orig` entries | `.gitignore` text | both present |
| `test_workspace_stale_ref_guard_covers_new_docs` | Workspace-hub stale-reference guard includes the new assetutilities canonical docs | workspace test text | paths present |
| `test_plans_readme_indexes_2461_plan` | `docs/plans/README.md` includes the #2461 plan row | README text | row present |
| `test_agents_md_links_canonical_surfaces` | `assetutilities/AGENTS.md` links to operator map and registry (light edit) | AGENTS.md text | both links present |

---

## Acceptance Criteria

- [ ] `assetutilities/README.md` is a current-state, no-broken-links architecture doc — no references to non-existent `core/` or `utils/`.
- [ ] `assetutilities/docs/README.md` exists and routes common issue types to source/tests/docs paths.
- [ ] `assetutilities/docs/README.md` explicitly states the curated-vs-raw inventory boundary.
- [ ] `assetutilities/MODULE_STRUCTURE.md` matches the observed `src/assetutilities/` layout — no false directory claims, real directories enumerated.
- [ ] The canonical assetutilities operator map exists at the host/path ratified by #2460 (default `docs/maps/assetutilities-operator-map.md` in workspace-hub if #2460 ratifies that host; otherwise `assetutilities/docs/maps/assetutilities-operator-map.md` per-repo) and covers every top-level Python-package directory observed under `src/assetutilities/` at implementation time (derived from the live tree, not hard-coded).
- [ ] Canonical machine-readable module/domain registry exists at the path defined by #2460 and covers every top-level Python-package directory observed under `src/assetutilities/` at implementation time (derived from the live tree, not hard-coded).
- [ ] Pre-delete discovery gates (per Claude F4 and F7) all returned empty: `grep -rn 'ApplicationManager\.py\.(bak|orig)'`, `grep -rn 'file_management\.py\.(bak|orig)'`, and `grep -rn 'visualizations_tests'` across `src/`, `tests/`, `scripts/`, `docs/`, and `.github/` in both workspace-hub and the assetutilities nested repo (excluding the tracked files themselves). Implementation commit includes the captured grep output as evidence (inline or as `.planning/quick/2461-pre-delete-grep.out`). A non-empty hit reclassifies the action as move/investigate — not delete — and patches this plan first.
- [ ] The four tracked `.bak`/`.orig` backup artifacts under `src/assetutilities/common/` are removed AFTER the discovery gates above returned empty.
- [ ] Both `tests/visualizations_tests.bat` and `tests/visualizations_tests_temp.bat` are removed AFTER the discovery gate above returned empty.
- [ ] `assetutilities/.gitignore` contains both `*.bak` and `*.orig` entries.
- [ ] `assetutilities/tests/hygiene/test_no_backup_artifacts_tracked.py` is green and guards against re-entry.
- [ ] `assetutilities/tests/docs/test_assetutilities_routing_contract.py` is green.
- [ ] `tests/docs/test_banned_stale_references.py` is extended to cover the new assetutilities canonical docs and still passes.
- [ ] `assetutilities/AGENTS.md` links to the operator map and registry.
- [ ] `docs/plans/README.md` includes the #2461 row.
- [ ] All three plan-review artifacts under `scripts/review/results/2026-04-22-plan-2461-{claude,codex,gemini}.md` exist AND every provider's final verdict is APPROVE or MINOR. If any provider returns MAJOR, the plan is re-tightened and re-reviewed (up to the repo-standard `MAX_REVIEW_ITERATIONS=3`) — there is NO "at most one non-APPROVE/MINOR" loophole; all three must clear. (Parallels #2462's r2 anti-loophole clause per `feedback_codex_sustained_major_loop.md`.)
- [ ] No encroachment on sibling scope: the implementation touches only `assetutilities/**` plus — only if #2460 ratifies workspace-hub host — the single workspace-hub file `docs/maps/assetutilities-operator-map.md` and the workspace-hub regression guard `tests/docs/test_banned_stale_references.py`. No file owned by #2460 (contract doc), #2462 (`digitalmodel/**`), #2463 (`aceengineer-website/**`), #2464 (`docs/CONTENT_INDEX.md` / repo-root cleanup), or #2465 (daily-freshness automation) is modified.
- [ ] Hard gate on #2460: before implementation begins, #2460 has reached `status:plan-approved` AND its contract doc has locked the registry filename, operator-map host location, required routing-surface set, and source-hygiene rules. If #2460 changes any of those, this plan is patched and re-reviewed first.
- [ ] TDD red-phase evidence captured in the implementation commit(s): the new tests in `test_assetutilities_routing_contract.py` and `test_no_backup_artifacts_tracked.py` demonstrably failed on the red-phase commit BEFORE the new docs/edits/deletions landed; the evidence is either inline in the commit body or attached as `.planning/quick/2461-red-phase.out`.

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | PENDING | to be filled after adversarial wave runs tonight |
| Codex | PENDING | no artifact yet |
| Gemini | PENDING | no artifact yet |

**Current draft state:** initial canonical draft — first Claude adversarial review artifact produced alongside this plan tonight; Codex and Gemini artifacts are pending and required before any transition to `status:plan-review`.

---

## Risks and Open Questions

- **Blocker (promoted from risk per Claude F2):** The canonical registry filename is decided in #2460, not here. Implementation of this plan MUST NOT begin until #2460 has (a) reached `status:plan-approved` AND (b) textually locked the registry filename and the operator-map host location (either in the #2460 plan or in the contract doc `docs/standards/TIER1_INDEXING_AND_CODE_PLACEMENT_CONTRACT.md` on main). If those items change between now and implementation, this plan is patched and re-reviewed before the implementation-start gate re-opens.
- **Risk:** Rewriting `MODULE_STRUCTURE.md` to match the observed tree could still drift if the tree evolves during implementation. Mitigation: the routing-contract test re-derives the required directory list from `git ls-tree src/assetutilities` at test time rather than hard-coding it.
- **Risk:** Deleting `.bat` scratch test files could surprise a Windows contributor OR silently break a CI workflow, nightly batch, or documented Windows quickstart that references them. **Mitigation (per Claude F4):** before any `git rm` runs, the implementation MUST execute `grep -rn 'visualizations_tests'` across both workspace-hub and the assetutilities nested repo (excluding the tracked files themselves); if any hit is found, the deletion is reclassified as a move/rename to `tests/platform/windows/` and this plan is patched first. Discovery step is codified in Pseudocode and binding via the acceptance criterion below.
- **Risk (resolved by HARD GATE per Claude F1):** The operator map's host location is deferred to #2460. If #2460 picks per-repo `docs/maps/` over workspace-hub `docs/maps/`, the artifact relocates. This plan's acceptance criteria no longer assert a specific workspace-hub path — they assert "at the host/path ratified by #2460". Implementation-start blocked until #2460 locks the host; see HARD GATE front-matter.
- **Risk:** Assetutilities has downstream consumers (digitalmodel `depends_on: [assetutilities]`). Any public import surface change during hygiene cleanup could break digitalmodel tests. **Mitigation (per Claude F7):** before any deletion, implementation MUST run `grep -rn 'ApplicationManager\.py\.(bak|orig)'` and `grep -rn 'file_management\.py\.(bak|orig)'` across `src/` and `tests/` (workspace-hub and assetutilities); no hits must be found before `git rm` runs. A positive hit reclassifies the action as investigate-first, not delete. Assertion is codified in Pseudocode and binding via the acceptance criterion below.
- **Open:** Should the hygiene guard run as a pytest only, or also as a pre-commit hook? This plan defers the pre-commit decision to the implementation PR.
- **Open:** Should `assetutilities/docs/README.md` embed a snapshot of the operator map or only link to it? This plan specifies a link; reviewers may push for an inline snapshot.

---

## Complexity: T2

**T2** — documentation rewrite across three repo-local files, one new canonical docs entry point, one new workspace-hub operator map, one new machine-readable registry, six file deletions, two new test files, and one extension to the workspace-hub stale-reference guard. Non-trivial but scoped: no source-code changes to `src/**`, no runtime behavior changes, no multi-module integration.
