# Plan for #2685: Wire DNV-OS-E301 citation pilot in orcaflex/mooring_design.py (Option A)

> **Status:** draft
> **Complexity:** T2
> **Date:** 2026-05-13
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2685
> **Review artifacts:** scripts/review/results/2026-05-13-plan-2685-claude.md | ...-codex.md | ...-gemini.md

---

## Resource Intelligence Summary

### Existing repo code

- Found: `digitalmodel/src/digitalmodel/citations/__init__.py` (21 lines) — re-exports `Citation`, `CitedValue`, `CitationResolutionError`, `validate_citation`.
- Found: `digitalmodel/src/digitalmodel/citations/schema.py` (133 lines) — `@dataclass(frozen=True) Citation(code_id, publisher, revision, section, wiki_path, note="")`, `CitedValue(value, citation, units="")`, `validate_citation(citation, *, repo_root: Path)` (fail-closed against wiki page frontmatter — lines 102–132).
- Found: `digitalmodel/src/digitalmodel/citations/registry.py` (59 lines) — `MooringCondition` enum (INTACT_QUASI_STATIC=1.67, DAMAGED_QUASI_STATIC=1.25) at lines 21–24, `_DNV_OS_E301_CITATION_TEMPLATE` at lines 26–31 (publishes `wiki_path = "knowledge/wikis/engineering/wiki/standards/dnv-os-e301.md"`), `get_mooring_safety_factor(condition, *, repo_root)` at lines 41–58 — currently **zero callers in `src/`**.
- Found: `digitalmodel/src/digitalmodel/orcaflex/mooring_design.py` (455 lines) — target file. Relevant lines:
  - L11 (docstring): `- DNV-OS-E301: Position Mooring`
  - L267: `safety_factor_intact: float = Field(1.67, gt=1.0, description="FoS for intact condition (API RP 2SK)")`
  - L268: `safety_factor_damaged: float = Field(1.25, gt=1.0, description="FoS for damaged condition")`
  - L283–301: `MooringLineDesign.estimate_catenary()` — does NOT consume the SF fields.
  - L303–317: `MooringLineDesign.check_mbl(max_tension_kn)` — utilisation = `max_tension / mbl`. **Does NOT divide by safety_factor.** This is the natural consumption site.
  - L327 (docstring): `Reference: API RP 2SK Section 5, DNV-OS-E301.`
- Found: `digitalmodel/tests/orcaflex/test_mooring_design.py` — existing test surface (will be extended, not replaced).
- Found: `digitalmodel/tests/citations/fixtures/knowledge/wikis/engineering/wiki/standards/dnv-os-e301.md` + `FIXTURE_PROVENANCE.md` — vendored frontmatter fixture proving the resolver pattern works in CI without the real wiki page.
- Found: `digitalmodel/tests/citations/test_registry.py` — reference test pattern: `_repo_root() = Path(__file__).parent / "fixtures"` (lines 19–22 establish the vendoring approach per workspace-hub #2580).
- Gap: `safety_factor_intact` / `safety_factor_damaged` defaults exist on `MooringLineDesign` but are **never consumed** by `estimate_catenary()`, `check_mbl()`, or `generate_layout()`. Option A must therefore wire SFs into a calc — emission alone with no consumer is theatre.
- Gap: No production-side `repo_root` resolver. `get_mooring_safety_factor()` is `repo_root`-injected. The pilot needs a deterministic way to discover `repo_root` from inside a digitalmodel calc (digitalmodel is checked out at `workspace-hub/digitalmodel/` AND can run standalone — see test_registry comment about the workspace-hub #2580 vendoring decision).

### Standards

| Standard | Status | Source |
|---|---|---|
| DNV-OS-E301 (Position Mooring) | citation infra references this; canonical wiki page does NOT live in `knowledge/wikis/engineering/wiki/standards/dnv-os-e301.md` in main repo (only the test fixture copy exists). | `digitalmodel/tests/citations/fixtures/...` (vendored) + `data/document-index/standards-transfer-ledger.yaml` (not re-verified in this plan — risk row below) |
| API RP 2SK | referenced in docstring (L11, L327) but not the citation pilot target per #2481 D1. | `mooring_design.py` |

### LLM Wiki pages consulted

- Tried `knowledge/wikis/engineering/wiki/standards/dnv-os-e301.md` → MISSING in main tree.
- Tried `find /knowledge/wikis -iname '*e301*'` → only the digitalmodel **test fixture** hit. No marine-engineering or engineering wiki page exists yet.
- Existing standards roots found: `knowledge/wikis/acma-projects/wiki/standards/`, `knowledge/wikis/marine-engineering/raw/standards/`. Neither contains DNV-OS-E301 today.

### Documents consulted

- `.claude/rules/calc-citation-contract.md` — already amended (B1) to mark pilot PENDING; this plan delivers the A side of #2685's Option C.
- Issue #2481 — original D1/D2/D3 decisions: mooring SFs are the pilot calc target, fail-closed at calc time, direct file read for v1.
- Issue #2685 (body) — Acceptance Criteria list copied into the AC section below.
- Issue #2400 (referenced by `calc-citation-contract.md`) — future MCP `wiki_search` migration; the schema is forward-compatible.
- Issue #2580 — established the test-fixture vendoring pattern (`tests/citations/fixtures/knowledge/wikis/...`) so resolver works in standalone CI.

### Gaps identified

- **Wiki page gap (load-bearing):** `knowledge/wikis/engineering/wiki/standards/dnv-os-e301.md` does not exist in the production tree. The registry resolver will fail-closed (`reason="page_missing"`) on any caller that passes the workspace-hub repo root. Either (a) create that wiki page with the matching frontmatter, or (b) repoint the citation template at an existing real page, or (c) accept fail-closed behavior in prod and only emit at test/fixture time (rejected — defeats the rule's purpose).
- **`repo_root` discovery gap:** no helper exists to find workspace-hub root from inside a calc function. The pilot needs a small `_resolve_repo_root()` utility (or accept an optional kwarg).
- **SF consumption gap:** `check_mbl()` doesn't currently apply a safety factor. To emit a Citation meaningfully, the calc must actually *use* the cited SF.

### Evidence (embedded verification)

**Issue statuses** (verified 2026-05-13 via `gh issue view`):
- `#2685` — OPEN — "Citation pilot contradiction: rule names orcaflex/mooring_design.py but file emits no Citation" (labels: bug, cat:engineering, cat:knowledge-domain, priority:high)

**File existence** (`ls` 2026-05-13):
- EXISTS: `digitalmodel/src/digitalmodel/orcaflex/mooring_design.py` (455 lines)
- EXISTS: `digitalmodel/src/digitalmodel/citations/{__init__.py,schema.py,registry.py}`
- EXISTS: `digitalmodel/tests/orcaflex/test_mooring_design.py`
- EXISTS: `digitalmodel/tests/citations/{test_registry.py,test_schema.py,fixtures/knowledge/wikis/engineering/wiki/standards/dnv-os-e301.md}`
- MISSING (must address — see Risk row): `knowledge/wikis/engineering/wiki/standards/dnv-os-e301.md` (production wiki page)
- MISSING (new — this plan creates): `digitalmodel/tests/orcaflex/test_mooring_design_citations.py`

**Line excerpts** (mooring_design.py L264–276):
```
class MooringLineDesign(BaseModel):
    """Mooring line preliminary design input.
    Reference: API RP 2SK Section 5.
    """
    water_depth: float = Field(1500.0, gt=0.0, description="Water depth (m)")
    fairlead_depth: float = Field(10.0, ge=0.0, description="Fairlead depth below surface (m)")
    target_pretension: float = Field(1500.0, gt=0.0, description="Target pretension at fairlead (kN)")
    safety_factor_intact: float = Field(1.67, gt=1.0, description="FoS for intact condition (API RP 2SK)")
    safety_factor_damaged: float = Field(1.25, gt=1.0, description="FoS for damaged condition")
```

**Line excerpts** (mooring_design.py L303–317 — `check_mbl`, the natural consumption site):
```
def check_mbl(self, max_tension_kn: float) -> Dict[str, float]:
    """Check MBL utilisation for each segment.
    Args:
        max_tension_kn: Maximum line tension (kN).
    Returns:
        Dict of segment material -> utilisation (ratio of max tension / MBL).
    """
    results = {}
    for seg in self.segments:
        mat = MOORING_MATERIAL_LIBRARY[seg.material_key]
        utilisation = max_tension_kn / mat.mbl
        results[seg.material_key] = round(utilisation, 4)
    return results
```

**Gap proofs:**
```
$ ls /mnt/local-analysis/workspace-hub/knowledge/wikis/engineering/wiki/standards/dnv-os-e301.md
ls: cannot access ...: No such file or directory
$ find knowledge/wikis -iname '*e301*'
(only test-fixture path — no production page)
```

**Reproduction proofs** (Step 1.5 — confirm the alleged state):
```
$ grep -c 'Citation\|from digitalmodel.citations' digitalmodel/src/digitalmodel/orcaflex/mooring_design.py
0
```
- Reproduced at: 2026-05-13.
- Failure mode observed matches issue claim: YES — file imports zero citation symbols, emits zero `Citation` instances. Issue #2685 is accurately scoped.
- **Target count after implementation:** ≥ 2 occurrences (one import line + at least one `Citation`/`CitedValue` reference per consumed SF site). Concretely: 1 import + 2 callsites (intact + damaged conditions) = `grep -c` ≥ 3.

Distinct sources consulted: issue body (1) + `calc-citation-contract.md` rule (2) + `citations/registry.py` source (3) + existing `tests/citations/test_registry.py` (4) + #2481 + #2580 + #2400 references (5). **Count: 5+, meets ≥3 minimum.**

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | docs/plans/2026-05-13-issue-2685-citation-pilot-option-a-plan.md |
| Implementation (modified) | digitalmodel/src/digitalmodel/orcaflex/mooring_design.py |
| Implementation (possibly extended) | digitalmodel/src/digitalmodel/citations/registry.py |
| New tests | digitalmodel/tests/orcaflex/test_mooring_design_citations.py |
| New wiki page (option A only — see Risks) | knowledge/wikis/engineering/wiki/standards/dnv-os-e301.md |
| Rule update | .claude/rules/calc-citation-contract.md (flip "PENDING" → live pilot reference) |
| Plan review — Claude | scripts/review/results/2026-05-13-plan-2685-claude.md |
| Plan review — Codex | scripts/review/results/2026-05-13-plan-2685-codex.md |
| Plan review — Gemini | scripts/review/results/2026-05-13-plan-2685-gemini.md |

---

## Deliverable

`digitalmodel.orcaflex.mooring_design` consumes `get_mooring_safety_factor(...)` for its intact and damaged DNV-OS-E301 design factors and emits `CitedValue`s through a new public-API sidecar return path (`check_mbl_with_citations()` and an updated `MooringLineDesign` constructor option), with green integration tests and the rule file flipped from PENDING to live.

---

## Pseudocode

```
# mooring_design.py — additions

from pathlib import Path
from typing import Optional
from digitalmodel.citations import Citation, CitedValue
from digitalmodel.citations.registry import (
    MooringCondition, get_mooring_safety_factor,
)

def _default_repo_root() -> Path:
    # Walk up from this file until we find a directory containing `knowledge/wikis/`
    # OR fall back to env var DIGITALMODEL_REPO_ROOT.
    # If neither, raise — fail-closed.
    ...

class MooringLineDesign(BaseModel):
    ...
    repo_root: Optional[Path] = None  # injection seam for tests + standalone CI

    def get_intact_safety_factor(self) -> CitedValue:
        return get_mooring_safety_factor(
            MooringCondition.INTACT_QUASI_STATIC,
            repo_root=self.repo_root or _default_repo_root(),
        )

    def get_damaged_safety_factor(self) -> CitedValue:
        return get_mooring_safety_factor(
            MooringCondition.DAMAGED_QUASI_STATIC,
            repo_root=self.repo_root or _default_repo_root(),
        )

    def check_mbl_with_citations(self, max_tension_kn: float, *, condition="intact") -> dict:
        # Wires the SF into the calc that previously ignored it.
        sf_cv = self.get_intact_safety_factor() if condition == "intact" else self.get_damaged_safety_factor()
        sf = sf_cv.value
        per_segment = {}
        for seg in self.segments:
            mat = MOORING_MATERIAL_LIBRARY[seg.material_key]
            util_no_sf = max_tension_kn / mat.mbl
            util_with_sf = (max_tension_kn * sf) / mat.mbl
            per_segment[seg.material_key] = {
                "utilisation_no_sf": round(util_no_sf, 4),
                "utilisation_with_sf": round(util_with_sf, 4),
                "passes": util_with_sf < 1.0,
            }
        return {
            "results": per_segment,
            "citations": [sf_cv.citation],  # sidecar — preserves downstream-consumer compatibility
        }
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Modify | `digitalmodel/src/digitalmodel/orcaflex/mooring_design.py` | Import `Citation` infra, add `_default_repo_root()` helper, add `get_intact_safety_factor()` / `get_damaged_safety_factor()` methods, add `check_mbl_with_citations()` that consumes the SFs and returns sidecar citations. Leave existing `check_mbl()` untouched for backward compat. |
| Modify (small) | `digitalmodel/src/digitalmodel/citations/registry.py` | Only if `MooringCondition` needs a third member (TBD); currently the existing two enum values (intact + damaged) cover the 1.67 and 1.25 defaults in `MooringLineDesign`. **Default expectation: no change required.** |
| Create | `digitalmodel/tests/orcaflex/test_mooring_design_citations.py` | Integration test: `_repo_root()` fixture (same vendoring pattern as `tests/citations/test_registry.py`), assert `check_mbl_with_citations()` returns ≥1 citation, assert citation `code_id == "DNV-OS-E301"`, assert SF is applied to utilisation. |
| Create (likely required) | `knowledge/wikis/engineering/wiki/standards/dnv-os-e301.md` | Production wiki page with `code_id: DNV-OS-E301`, `publisher: DNV`, `revision: 2021-07` frontmatter so production calls don't fail-closed with `page_missing`. Stub body acceptable for pilot; expand as a follow-up issue. |
| Modify | `.claude/rules/calc-citation-contract.md` | Flip "PENDING" pilot reference to live; cite the actual file + functions. |
| Update | `docs/plans/README.md` | Add this plan to the index. |

---

## TDD Test List

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| `test_mooring_design_emits_intact_citation` | `MooringLineDesign(repo_root=fixtures).get_intact_safety_factor()` returns `CitedValue` | default config | `cv.value == 1.67`, `cv.citation.code_id == "DNV-OS-E301"` |
| `test_mooring_design_emits_damaged_citation` | same for damaged condition | default config | `cv.value == 1.25`, `cv.citation.code_id == "DNV-OS-E301"` |
| `test_check_mbl_with_citations_applies_sf` | utilisation_with_sf == util_no_sf * 1.67 | `max_tension_kn=3000.0`, `condition="intact"` | sidecar contains 1 citation; `util_with_sf` matches arithmetic |
| `test_check_mbl_with_citations_fail_closed_on_missing_wiki` | passing `repo_root=tmp_path` raises `CitationResolutionError` with code_id "DNV-OS-E301" | tmp_path with no fixture | raises; `reason == "page_missing"` |
| `test_grep_count_meets_target` (sanity) | `grep -c 'Citation' mooring_design.py >= 3` | repo file | passes |
| `test_no_regression_in_existing_mooring_tests` | existing `test_mooring_design.py` still passes | — | green |

---

## Acceptance Criteria

Mirrors #2685 AC list with explicit verification commands:

- [ ] **AC1:** `grep -c 'Citation' digitalmodel/src/digitalmodel/orcaflex/mooring_design.py` returns ≥ 3 (was 0)
- [ ] **AC2:** `uv run pytest digitalmodel/tests/orcaflex/test_mooring_design_citations.py -v` — all new tests pass
- [ ] **AC3:** `uv run pytest digitalmodel/tests/orcaflex/test_mooring_design.py -v` — no regression
- [ ] **AC4:** `uv run pytest digitalmodel/tests/citations/ -v` — existing citation infra tests still green
- [ ] **AC5:** Rule no longer claims unrealized pilot — `grep -c 'PENDING' .claude/rules/calc-citation-contract.md` returns 0 (the PENDING block is replaced with a positive reference)
- [ ] **AC6:** `knowledge/wikis/engineering/wiki/standards/dnv-os-e301.md` exists with valid frontmatter (`code_id`, `publisher`, `revision`), OR Risk row below explicitly documents accepted fail-closed behavior with deferred follow-up issue
- [ ] **AC7:** CHANGELOG entry in `docs/standards/calc-output-citation.md` notes the pilot is live as of 2026-05-13
- [ ] **AC8:** Three-provider plan review artifacts posted to `scripts/review/results/` (Claude + Codex + Gemini per `feedback_always_adversarial_review_scale_depth`)

---

## Adversarial Review Stance

Per `.claude/memory/feedback_adversarial_review_stance.md` + `feedback_always_adversarial_review_scale_depth.md`. T2 scope → Claude + Codex + Gemini. Things that could go wrong:

1. **Wiki page missing in production → every prod caller fail-closes.** The registry resolver validates `knowledge/wikis/engineering/wiki/standards/dnv-os-e301.md` against the live tree. That page does **not** exist (confirmed by `ls` 2026-05-13). Subagents writing the test fixture in 2026-04 (#2580) did not also write the prod page. Consequence: `check_mbl_with_citations()` will raise `CitationResolutionError(reason="page_missing")` for every real caller. **Mitigation:** create `knowledge/wikis/engineering/wiki/standards/dnv-os-e301.md` (frontmatter-valid stub) as part of this PR. Cross-check by running `validate_citation(...)` against workspace-hub root in a smoke test.

2. **`repo_root` discovery from inside `digitalmodel/` is ambiguous.** digitalmodel is both a workspace-hub subdir and a standalone publishable package (per `digitalmodel/CLAUDE.md` adapter and `tests/citations/test_registry.py` line 19–22 comment referencing #2580). A naive "walk up to `knowledge/wikis/`" will work in workspace-hub overlay but fail in a standalone clone. **Mitigation:** layered fallback — (a) explicit `repo_root` kwarg, (b) `DIGITALMODEL_REPO_ROOT` env var, (c) parent-walk looking for `knowledge/wikis/`, (d) bounded sentinel (per `feedback_path_parent_infinite_loop` — don't `while True` walk to `/`), (e) raise `CitationResolutionError` with actionable message if none resolve.

3. **`safety_factor_intact`/`safety_factor_damaged` field defaults shadow the registry.** The Pydantic model defaults (1.67, 1.25) at L267–268 are *frozen literals*. If the registry's values diverge in the future (e.g., DNV revision 2027-XX), callers that read `mooring.safety_factor_intact` get the stale value while `get_intact_safety_factor()` returns the current one. **Mitigation:** deprecate the literal fields in this PR (mark with `Field(..., description="DEPRECATED — use get_intact_safety_factor()")`) and add a `@model_validator` that warns if the field value doesn't match the registry. Removal is a separate follow-up issue.

4. **Pydantic v2 `Optional[Path]` field on `MooringLineDesign` breaks YAML config consumers.** If downstream tools load `MooringLineDesign` from YAML, adding `repo_root: Optional[Path] = None` is fine (defaults preserve compat), but if anything uses `MooringLineDesign(**dict)` with strict mode, an unknown `repo_root` key won't bite. **Mitigation:** verify with `MooringLineDesign.model_config` — default Pydantic v2 ignores unknown keys; document in the field description.

5. **Auto-sync race during merge** (per `feedback_merge_race_silent_revert` + `feedback_hermes_active_preflight_check`). Mooring is a load-bearing module; concurrent Hermes cleanup could revert the citation wiring. **Mitigation:** `pgrep -af 'git (rebase|stash push|commit|merge|reset|checkout)'` preflight before push; if Hermes active, branch + worktree.

6. **Subagent Write phantom** (per `feedback_subagent_write_phantom`). If any subagent claims to have written the test file or wiki page, main session must `ls` independently before believing.

---

## Risks and Open Questions

- **Risk (load-bearing):** Production wiki page `knowledge/wikis/engineering/wiki/standards/dnv-os-e301.md` is missing. Without it, prod callers fail-closed. **Mitigation:** create the page in the same PR with valid frontmatter — see AC6.
- **Risk:** `check_mbl()` (the existing, citation-free method) has unknown external callers. Leave it intact; expose new functionality via `check_mbl_with_citations()` only. Removal is a future deprecation cycle.
- **Risk:** This is a load-bearing calc module. **Rollback plan:** the changes are additive (new methods, new test file, new wiki page) plus *no edits* to `check_mbl()`, `solve_catenary()`, `estimate_catenary()`, or the material library. Rollback = revert the single commit; existing callers remain green because nothing they use changed. The wiki page addition is also additive (a new file, not an edit). The rule file edit is a one-line text swap, trivially revertable.
- **Open Q for user approval:** Should we deprecate `safety_factor_intact`/`safety_factor_damaged` Pydantic fields in this PR (warn-on-access), or leave for a follow-up cleanup issue? Recommend follow-up to keep this PR tightly scoped.
- **Open Q for user approval:** Wiki page body — pilot stub (frontmatter + 1-paragraph placeholder) OR delegate to the domain-knowledge-sweep #2676 backlog (which is actively researching DNV-OS-E301)? Recommend pilot stub now, full body via #2676.

---

## Estimated Effort

| Dimension | Estimate |
|---|---|
| Files modified | 2 (mooring_design.py, calc-citation-contract.md) |
| Files created | 3 (test_mooring_design_citations.py, dnv-os-e301.md wiki page, optional CHANGELOG line) |
| LOC touched in `mooring_design.py` | ~60 lines added (imports + 3 methods + helper); 0 lines deleted |
| LOC for new test file | ~80–100 lines |
| Wiki page (stub) | ~20 lines (frontmatter + minimal body) |
| Total LOC | ~160 added, ~3 modified (rule file flip) |
| Time estimate (implementation only) | 1.5–2 hours |
| Time estimate (incl. adversarial review + revisions) | 3–4 hours wall-clock |

---

## Complexity: T2

**T2** — multi-file change touching a load-bearing calc module, requires new tests, requires a small wiki addition, requires the citation-contract rule update. Below T3 because: no new public API surface that downstream repos consume, no schema changes to existing infra, and rollback is trivial (additive changes only). Per `feedback_always_adversarial_review_scale_depth`, T2 → Codex + Gemini + Claude review depth.

---

## Plan-Review Routing Recommendation

Recommend running the adversarial review pass next, then on PASS, label the issue `status:plan-review` for user gate per `feedback_never_offer_to_self_label_plan_approved` (never self-label `status:plan-approved` from a planning session).
