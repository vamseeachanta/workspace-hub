# Plan for #2685: Wire DNV-OS-E301 citation pilot in orcaflex/mooring_design.py (Option A)

> **Status:** approved (r3 — 4 r2 defects patched inline; sustained-MAJOR loop break per `feedback_codex_sustained_major_loop`)
> **r1 review artifacts:** scripts/review/results/2026-05-13-plan-2685-claude-r1.md, ...-disagreement.md
> **r2 review artifacts:** scripts/review/results/2026-05-13-plan-2685-{claude,codex,gemini}.md (2026-05-13T21:11-21:12)
> **r3 patches (main-session inline, 2026-05-13):**
>  - Replace `self.repo_root` → kwarg `repo_root_override` in `_resolve_sf_for_condition` (codex+claude+gemini r2 F1)
>  - Fix `CitationResolutionError(...)` to use keyword-only args `code_id=, wiki_path=, reason=` (codex r2 F2 / gemini r2 F3)
>  - Wire `get_intact_safety_factor` / `get_damaged_safety_factor` through `_resolve_sf_for_condition` to honor user overrides (gemini r2 F2)
>  - Add explicit "Theatre tradeoff" risk row (gemini r2 F1 — new method has 0 callers in src/)
> **No r3 cross-review dispatched** (loop-break decision per memory rule)
> **Complexity:** T2
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2685
> **Review artifacts:** scripts/review/results/2026-05-13-plan-2685-claude.md | ...-codex.md | ...-gemini.md

---

## Resource Intelligence Summary

### Existing repo code

- Found: `digitalmodel/src/digitalmodel/citations/__init__.py` (21 lines) — re-exports `Citation`, `CitedValue`, `CitationResolutionError`, `validate_citation`.
- Found: `digitalmodel/src/digitalmodel/citations/schema.py` (133 lines) — `@dataclass(frozen=True) Citation(code_id, publisher, revision, section, wiki_path, note="")`, `CitedValue(value, citation, units="")`, `validate_citation(citation, *, repo_root: Path)` (fail-closed against wiki page frontmatter — lines 102–132).
- Found: `digitalmodel/src/digitalmodel/citations/registry.py` (58 lines) — **`class MooringCondition(str, Enum)`** at lines 21–23 with **string** members `INTACT_QUASI_STATIC = "intact-quasi-static"` and `DAMAGED_QUASI_STATIC = "damaged-quasi-static"` (NOT numeric). The numeric SF values (1.67 / 1.25) live in a **separate dict `_MOORING_SAFETY_FACTORS`** at lines 35–38 (`MooringCondition.INTACT_QUASI_STATIC: (1.67, "Section 2.2.3 (intact, quasi-static)")`, etc.). `_DNV_OS_E301_CITATION_TEMPLATE` at lines 26–31 (publishes `wiki_path = "knowledge/wikis/engineering/wiki/standards/dnv-os-e301.md"`), `get_mooring_safety_factor(condition, *, repo_root)` at lines 41–58 — currently **zero callers in `src/`**. **Implementer note:** the enum is a routing key, not a number; the float comes out of `get_mooring_safety_factor(...).value`, never from `MooringCondition.<MEMBER>` directly.
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

`digitalmodel.orcaflex.mooring_design` consumes `get_mooring_safety_factor(...)` for its intact and damaged DNV-OS-E301 design factors and emits `CitedValue`s through a new public-API sidecar return path (`check_mbl_with_safety_factor()` — renamed from r1's `check_mbl_with_citations()` to make the **semantic shift** explicit; the new method applies the SF to utilisation while the legacy `check_mbl()` does not), with green integration tests, the production wiki page created with frontmatter that matches `_DNV_OS_E301_CITATION_TEMPLATE` exactly, and the rule file flipped from PENDING to live. **Standalone digitalmodel deployments** (pip-installed, no `knowledge/wikis/` tree) gracefully no-op with a one-shot `WARNING` rather than hard-crashing.

---

## Pseudocode

```
# mooring_design.py — additions

import os
import warnings
from pathlib import Path
from typing import Optional
from digitalmodel.citations import Citation, CitedValue, CitationResolutionError
from digitalmodel.citations.registry import (
    MooringCondition,
    get_mooring_safety_factor,
    _MOORING_SAFETY_FACTORS,  # for default-detection (see fix #6)
)

# Sentinel for the field-default check (fix #6).
# These are the literal defaults declared on MooringLineDesign at L267–L268.
_INTACT_FIELD_DEFAULT = 1.67
_DAMAGED_FIELD_DEFAULT = 1.25

_REPO_ROOT_RESOLUTION_CACHE: dict = {}  # one-shot WARNING dedup in standalone mode


def _default_repo_root(explicit: Optional[Path] = None) -> Optional[Path]:
    """Layered fallback for repo_root resolution (per Adversarial Review §2).

    Returns Path on success, or None when running in standalone-package mode
    (caller MUST treat None as "skip citation emission, warn once").
    NEVER walks unbounded — guards against feedback_path_parent_infinite_loop.

    Resolution order:
      1. Explicit kwarg (highest precedence; respects test injection & user override)
      2. Env var DIGITALMODEL_REPO_ROOT (CI / pip-installed deployments)
      3. Bounded parent walk from this file looking for sentinel `knowledge/wikis/`
         with a HARD CAP of 8 levels (cannot escape to `/`)
      4. Standalone-package detection: if this file's path contains `site-packages`
         OR the walk exhausted without finding the sentinel → return None
      5. Workspace-hub context detection: only raise CitationResolutionError when
         BOTH (a) we are not in site-packages AND (b) DIGITALMODEL_REPO_ROOT
         is set but invalid (explicit user misconfiguration)
    """
    # Step 1 — explicit kwarg
    if explicit is not None:
        return Path(explicit)

    # Step 2 — env var
    env = os.environ.get("DIGITALMODEL_REPO_ROOT")
    if env:
        env_path = Path(env)
        if (env_path / "knowledge" / "wikis").is_dir():
            return env_path
        # User explicitly set it but it's wrong — fail-closed loud
        raise CitationResolutionError(
            f"DIGITALMODEL_REPO_ROOT={env_path!s} does not contain knowledge/wikis/; "
            f"set to the workspace-hub root or unset to fall through to standalone mode "
            f"(DNV-OS-E301)"
        )

    # Step 3 — bounded parent walk (sentinel: max 8 levels; never `while True`)
    here = Path(__file__).resolve()
    for parent in [here, *here.parents][:8]:
        if (parent / "knowledge" / "wikis").is_dir():
            return parent

    # Step 4 — standalone detection
    if "site-packages" in str(here) or "dist-packages" in str(here):
        return None  # graceful no-op; caller emits one-shot WARNING

    # Step 5 — checked-out source tree without the knowledge/ overlay
    # (e.g., shallow clone of digitalmodel/) → still standalone-like
    return None


def _resolve_sf_for_condition(
    self,
    condition: str,
    *,
    repo_root_override: Optional[Path] = None,
) -> tuple[float, Optional[Citation]]:
    """Return (safety_factor, citation_or_None).

    r3: repo_root passed via kwarg, not self.repo_root (no Pydantic field — per
    r2 portability finding). All callers MUST pass through their own repo_root
    kwarg or rely on the module-level _default_repo_root() chain.

    Fix #6 (user-override-wins):
      - If self.safety_factor_intact / _damaged != the field default, treat the
        user as having explicitly overridden the registry. Use their value.
        Still emit a citation IF resolvable, with note='user override; registry
        reference value=<registry_value>'.
      - Otherwise, take the registry value AND its citation.

    Fix #7 (standalone graceful no-op):
      - If _default_repo_root() returns None, log one-shot WARNING and proceed
        with the (overridden-or-default) field value, citation=None.
      - Only raise CitationResolutionError when in workspace-hub context AND the
        wiki page is genuinely missing/mismatched (true contract violation).
    """
    field_default, registry_key = (
        (_INTACT_FIELD_DEFAULT, MooringCondition.INTACT_QUASI_STATIC)
        if condition == "intact"
        else (_DAMAGED_FIELD_DEFAULT, MooringCondition.DAMAGED_QUASI_STATIC)
    )
    user_value = (
        self.safety_factor_intact if condition == "intact" else self.safety_factor_damaged
    )
    user_overrode = user_value != field_default

    # r3 fix: repo_root is a method-level kwarg, NOT a Pydantic field on
    # MooringLineDesign (would AttributeError otherwise; codex+claude+gemini r2 F1)
    repo_root = _default_repo_root(repo_root_override)
    if repo_root is None:
        # Standalone mode — one-shot WARNING, no citation
        key = ("standalone_no_citation", condition)
        if key not in _REPO_ROOT_RESOLUTION_CACHE:
            warnings.warn(
                "digitalmodel standalone mode: DNV-OS-E301 citation unavailable "
                "(no knowledge/wikis/ tree found; set DIGITALMODEL_REPO_ROOT to "
                "enable). Calc proceeds with SF=%s." % user_value,
                RuntimeWarning,
                stacklevel=3,
            )
            _REPO_ROOT_RESOLUTION_CACHE[key] = True
        return user_value, None

    # workspace-hub context — fail-closed if wiki page is broken (contract violation)
    cited = get_mooring_safety_factor(registry_key, repo_root=repo_root)
    if user_overrode:
        # Honor the override; cite the registry value as REFERENCE only.
        ref_citation = Citation(
            **{**cited.citation.__dict__,
               "note": f"user override (value={user_value}); registry reference value={cited.value}"}
        )
        return user_value, ref_citation
    return cited.value, cited.citation


class MooringLineDesign(BaseModel):
    ...
    # NOTE: per claude-r1 finding, do NOT persist repo_root as a Pydantic field
    # (YAML serialization would embed absolute paths). Instead, pass via method
    # kwarg or use the module-level _default_repo_root() resolution chain.
    # Tests inject via env var DIGITALMODEL_REPO_ROOT or by calling the helper
    # with explicit=.

    def get_intact_safety_factor(self, *, repo_root: Optional[Path] = None) -> CitedValue:
        """r3 fix (gemini r2 F2): delegate to _resolve_sf_for_condition so user
        overrides on safety_factor_intact are honored. Standalone mode raises
        CitationResolutionError with keyword args (r3 fix codex r2 F2)."""
        value, citation = self._resolve_sf_for_condition(
            "intact", repo_root_override=repo_root
        )
        if citation is None:
            raise CitationResolutionError(
                code_id="DNV-OS-E301",
                wiki_path="knowledge/wikis/engineering/wiki/standards/dnv-os-e301.md",
                reason="standalone_no_citation: set DIGITALMODEL_REPO_ROOT or use "
                       "check_mbl_with_safety_factor() which degrades gracefully.",
            )
        return CitedValue(value=value, citation=citation, units="")

    def get_damaged_safety_factor(self, *, repo_root: Optional[Path] = None) -> CitedValue:
        """r3 fix: symmetric to get_intact_safety_factor; honors override + uses
        keyword-only CitationResolutionError."""
        value, citation = self._resolve_sf_for_condition(
            "damaged", repo_root_override=repo_root
        )
        if citation is None:
            raise CitationResolutionError(
                code_id="DNV-OS-E301",
                wiki_path="knowledge/wikis/engineering/wiki/standards/dnv-os-e301.md",
                reason="standalone_no_citation: set DIGITALMODEL_REPO_ROOT or use "
                       "check_mbl_with_safety_factor() which degrades gracefully.",
            )
        return CitedValue(value=value, citation=citation, units="")

    def check_mbl_with_safety_factor(
        self, max_tension_kn: float, *, condition: str = "intact"
    ) -> dict:
        """Apply DNV-OS-E301 SF to MBL utilisation and emit citation sidecar.

        ⚠️ SEMANTIC DIFFERENCE FROM check_mbl():
          - check_mbl():           utilisation = max_tension / mbl
          - check_mbl_with_safety_factor(): utilisation = (max_tension * SF) / mbl
          A caller migrating from the old to new method WILL see utilisation
          multiplied by 1.67 (intact) or 1.25 (damaged). Loads at 0.60 utilisation
          under the legacy method land at ~1.002 (FAIL) under this one.
          This is intentional — DNV-OS-E301 §2.2.3 mandates the SF be applied —
          but the migration is NOT additive at the numeric-output level.
          Callers MUST recalibrate any utilisation thresholds before adopting.
        """
        if condition not in ("intact", "damaged"):
            raise ValueError(
                f"condition must be 'intact' or 'damaged', got {condition!r} "
                "(prevents typos like 'damagd' silently selecting wrong SF)"
            )
        sf, citation = _resolve_sf_for_condition(self, condition)  # fixes #6 + #7
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
            "safety_factor": sf,
            "condition": condition,
            "citations": [citation] if citation is not None else [],
        }
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Modify | `digitalmodel/src/digitalmodel/orcaflex/mooring_design.py` | Import `Citation`/`CitedValue`/`CitationResolutionError` infra, add `_default_repo_root(explicit)` helper with **5-step layered fallback** (kwarg → env var → bounded parent-walk capped at 8 levels → site-packages detection → standalone-graceful-None), add `_resolve_sf_for_condition()` helper (user-override-aware, fixes #6), add `get_intact_safety_factor()` / `get_damaged_safety_factor()` methods, add `check_mbl_with_safety_factor()` (**renamed from `check_mbl_with_citations` for semantic clarity, fixes #3**) that consumes the SFs and returns sidecar citations. Leave existing `check_mbl()` untouched for backward compat. |
| (Out of scope) | `digitalmodel/src/digitalmodel/citations/registry.py` | r1 hedged with "Only if `MooringCondition` needs a third member (TBD)". r2 fixes the scope: **NO registry change**. The two existing enum members + the dict mapping cover both SFs that `MooringLineDesign` consumes. Removed from rollback surface. |
| Create | `digitalmodel/tests/orcaflex/test_mooring_design_citations.py` | Integration tests: (1) `MooringLineDesign(...).get_intact_safety_factor(repo_root=fixtures)` returns `CitedValue` with value=1.67; (2) `check_mbl_with_safety_factor()` returns `safety_factor` + ≥1 `Citation` whose `code_id == "DNV-OS-E301"`; (3) **parent-walk sentinel test**: from a tmp path far from any `knowledge/wikis/`, helper returns `None` not infinite-loop; (4) **user-override-wins test**: `MooringLineDesign(safety_factor_intact=2.5).check_mbl_with_safety_factor(...)` uses 2.5 not 1.67, citation note records the override; (5) **standalone graceful-no-op test**: monkeypatch `_default_repo_root` to return None, assert `RuntimeWarning` issued and `citations == []`. |
| **REQUIRED (r2)** | `knowledge/wikis/engineering/wiki/standards/dnv-os-e301.md` | Production wiki page with frontmatter `code_id: DNV-OS-E301`, `publisher: DNV`, `revision: 2021-07` matching `_DNV_OS_E301_CITATION_TEMPLATE` byte-for-byte. **Stub body acceptable for pilot**; expand via #2676 (Domain Knowledge Sweep). **AC6 now requires this file unconditionally** — escape clause removed (fix #4). |
| Modify | `.claude/rules/calc-citation-contract.md` | Flip "PENDING" pilot reference to live; cite the actual file + function `mooring_design.py:check_mbl_with_safety_factor` with date `2026-05-13`. |
| **Modify (r2 — was missing in r1)** | `docs/standards/calc-output-citation.md` | Append CHANGELOG-style entry: "2026-05-13: DNV-OS-E301 mooring pilot live via `orcaflex.mooring_design.MooringLineDesign.check_mbl_with_safety_factor`. Sidecar return shape: `{results, safety_factor, condition, citations}`." Required for AC7 (codex finding: AC7 listed the file but Files-to-Change didn't). |
| Update | `docs/plans/README.md` | Add this plan to the index. |

---

## TDD Test List

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| `test_mooring_design_emits_intact_citation` | `MooringLineDesign().get_intact_safety_factor(repo_root=fixtures)` returns `CitedValue` | default config + fixture root | `cv.value == 1.67`, `cv.citation.code_id == "DNV-OS-E301"` |
| `test_mooring_design_emits_damaged_citation` | same for damaged condition | default config + fixture root | `cv.value == 1.25`, `cv.citation.code_id == "DNV-OS-E301"` |
| `test_check_mbl_with_sf_applies_sf` | `util_with_sf == max_tension * 1.67 / mbl` (behavioral, not grep) | `max_tension_kn=3000.0`, `condition="intact"`, fixture root | sidecar `citations` has 1 entry, `safety_factor==1.67`, `util_with_sf` matches arithmetic to 4 decimals |
| `test_check_mbl_with_sf_fail_closed_on_missing_wiki` | empty `repo_root=tmp_path` with `DIGITALMODEL_REPO_ROOT=tmp_path` raises `CitationResolutionError` | tmp_path with no fixture, env var set | raises; `reason == "page_missing"`; code_id in msg |
| **`test_user_override_wins_for_intact_sf`** (fix #6) | `MooringLineDesign(safety_factor_intact=2.5).check_mbl_with_safety_factor(...)` honors 2.5 | intact, override=2.5 | `safety_factor==2.5`, citation present with `note` containing "user override" + registry reference value 1.67 |
| **`test_user_override_wins_for_damaged_sf`** (fix #6) | same for damaged + override 1.5 | damaged, override=1.5 | `safety_factor==1.5`, citation `note` contains "user override"; registry value 1.25 cited as reference |
| **`test_standalone_no_repo_root_graceful_warn`** (fix #7) | `_default_repo_root()` returns None → method proceeds with WARNING, no citation | monkeypatch helper to None | `RuntimeWarning` emitted once; `citations == []`; calc still produces utilisation |
| **`test_repo_root_walk_bounded_sentinel`** (fix #5, defends `feedback_path_parent_infinite_loop`) | from a deep tmp path, `_default_repo_root()` returns None within bounded steps (no hang) | tmp_path 12+ levels deep, no wikis tree | returns None within < 0.1s |
| **`test_repo_root_env_var_overrides_walk`** (fix #5) | `DIGITALMODEL_REPO_ROOT=<fixture>` wins even if parent walk would also succeed elsewhere | env var set + cwd in workspace-hub | resolves to env-var path, not walk-discovered path |
| **`test_repo_root_invalid_env_var_raises`** (fix #5) | `DIGITALMODEL_REPO_ROOT=/nonexistent` raises `CitationResolutionError` | bad env var | raises with actionable message naming the env var |
| **`test_invalid_condition_string_raises`** (codex finding) | `check_mbl_with_safety_factor(..., condition="damagd")` raises `ValueError`, NOT silently picking 1.25 | typo'd condition | `ValueError` mentioning valid values |
| **`test_wiki_page_frontmatter_matches_template`** (smoke, defends production page) | `validate_citation(template_citation, repo_root=workspace_hub_root)` succeeds | the freshly-created prod wiki page | no raise; resolver returns clean |
| `test_no_regression_in_existing_mooring_tests` | existing `test_mooring_design.py` still passes | — | green |

**Removed in r2:** `test_grep_count_meets_target` (was an artifact-grep test, not behavior — per claude-r1 + codex findings; redundant with the behavioral tests above).

---

## Acceptance Criteria

Mirrors #2685 AC list with explicit verification commands. **r2 changes:** AC1 rewritten to count actual call sites; AC6 escape clause removed (wiki page now mandatory); AC5 strengthened to require positive presence assertion.

- [ ] **AC1 (fix #1):** Behavioral emission — `uv run python -c "from digitalmodel.orcaflex.mooring_design import MooringLineDesign; ml = MooringLineDesign(); r = ml.check_mbl_with_safety_factor(3000.0, condition='intact'); assert r['citations'] and r['citations'][0].code_id == 'DNV-OS-E301'; print('OK')"` returns `OK` (replaces the broken `grep -c 'Citation' >= 3` from r1, which counted lines not occurrences and the pseudocode only emitted 2 matching lines anyway). The grep-count check is **removed**; emission is now verified at runtime through AC2/AC3 behavioral tests.
- [ ] **AC2:** `uv run pytest digitalmodel/tests/orcaflex/test_mooring_design_citations.py -v` — all new tests pass (≥ 11 cases including user-override-wins, standalone-graceful, bounded-walk-sentinel)
- [ ] **AC3:** `uv run pytest digitalmodel/tests/orcaflex/test_mooring_design.py -v` — no regression
- [ ] **AC4:** `uv run pytest digitalmodel/tests/citations/ -v` — existing citation infra tests still green
- [ ] **AC5 (strengthened):** Rule claims the pilot is live — `.claude/rules/calc-citation-contract.md` (a) MUST NOT contain the string `PENDING` in relation to this pilot, AND (b) MUST contain a positive reference of the form `mooring_design.py:check_mbl_with_safety_factor` with a date stamp `2026-05-13` (verify by `grep -E 'check_mbl_with_safety_factor.*2026-05-13' .claude/rules/calc-citation-contract.md` returns ≥ 1)
- [ ] **AC6 (fix #4 — escape clause REMOVED):** `knowledge/wikis/engineering/wiki/standards/dnv-os-e301.md` MUST exist with frontmatter `code_id: DNV-OS-E301`, `publisher: DNV`, `revision: 2021-07` (verified by running `validate_citation(template, repo_root=<workspace-hub root>)` and observing **no** `CitationResolutionError`). The r1 "OR Risk row" escape contradicted the Deliverable ("green integration tests") and is removed. Note: the escape clause was load-bearing for AC2/AC3 — removing it makes the wiki page a hard dependency, not optional. If the wiki page cannot be created at PR time (e.g., domain-knowledge review pending), the **plan blocks** until it can.
- [ ] **AC7:** CHANGELOG-style entry exists in `docs/standards/calc-output-citation.md` noting the pilot went live 2026-05-13 — verified by `grep -q '2026-05-13.*pilot' docs/standards/calc-output-citation.md`. **r2 note:** Files-to-Change must also list this file as Modify; r1 omitted it (codex finding). Now added below.
- [ ] **AC8:** Cross-provider plan review artifacts posted to `scripts/review/results/` per `feedback_always_adversarial_review_scale_depth`. T2 scope → Codex + Gemini minimum; Claude review optional unless complexity is upgraded. r1 mis-asserted "three-provider" for T2; r2 reads: Codex + Gemini required (T2 baseline), Claude added for r1→r2 transparency.

---

## Adversarial Review Stance

Per `.claude/memory/feedback_adversarial_review_stance.md` + `feedback_always_adversarial_review_scale_depth.md`. T2 scope → Claude + Codex + Gemini. Things that could go wrong:

1. **Wiki page missing in production → every prod caller fail-closes.** The registry resolver validates `knowledge/wikis/engineering/wiki/standards/dnv-os-e301.md` against the live tree. That page does **not** exist (confirmed by `ls` 2026-05-13). Subagents writing the test fixture in 2026-04 (#2580) did not also write the prod page. Consequence: `check_mbl_with_safety_factor()` will raise `CitationResolutionError(reason="page_missing")` for every real caller in workspace-hub context (standalone callers degrade gracefully per r2 fix #7). **Mitigation:** create `knowledge/wikis/engineering/wiki/standards/dnv-os-e301.md` (frontmatter-valid stub) as part of this PR. Cross-check by running `validate_citation(...)` against workspace-hub root in a smoke test.

2. **`repo_root` discovery from inside `digitalmodel/` is ambiguous.** digitalmodel is both a workspace-hub subdir and a standalone publishable package (per `digitalmodel/CLAUDE.md` adapter and `tests/citations/test_registry.py` line 19–22 comment referencing #2580). A naive "walk up to `knowledge/wikis/`" will work in workspace-hub overlay but fail in a standalone clone. **Mitigation (now in pseudocode, fix #5 + #7):** 5-step layered fallback — (1) explicit `repo_root` kwarg, (2) `DIGITALMODEL_REPO_ROOT` env var (raises actionable error if set-but-invalid), (3) **bounded** parent walk looking for `knowledge/wikis/` with a hard cap of 8 levels (defends `feedback_path_parent_infinite_loop`), (4) **standalone-package detection** via `site-packages`/`dist-packages` in path → return `None`, (5) **graceful no-op with one-shot `RuntimeWarning`** rather than hard-crash for standalone users. Only raise `CitationResolutionError` when the user explicitly set `DIGITALMODEL_REPO_ROOT` to an invalid path, or when in workspace-hub context but the wiki page is missing.

3. **`safety_factor_intact`/`safety_factor_damaged` field defaults shadow the registry.** The Pydantic model defaults (1.67, 1.25) at L267–268 are *frozen literals*. If the registry's values diverge in the future (e.g., DNV revision 2027-XX), callers that read `mooring.safety_factor_intact` get the stale value while `get_intact_safety_factor()` returns the current one. **Mitigation:** deprecate the literal fields in this PR (mark with `Field(..., description="DEPRECATED — use get_intact_safety_factor()")`) and add a `@model_validator` that warns if the field value doesn't match the registry. Removal is a separate follow-up issue.

4. **Pydantic v2 `Optional[Path]` field on `MooringLineDesign` breaks YAML config consumers.** If downstream tools load `MooringLineDesign` from YAML, adding `repo_root: Optional[Path] = None` is fine (defaults preserve compat), but if anything uses `MooringLineDesign(**dict)` with strict mode, an unknown `repo_root` key won't bite. **Mitigation:** verify with `MooringLineDesign.model_config` — default Pydantic v2 ignores unknown keys; document in the field description.

5. **Auto-sync race during merge** (per `feedback_merge_race_silent_revert` + `feedback_hermes_active_preflight_check`). Mooring is a load-bearing module; concurrent Hermes cleanup could revert the citation wiring. **Mitigation:** `pgrep -af 'git (rebase|stash push|commit|merge|reset|checkout)'` preflight before push; if Hermes active, branch + worktree.

6. **Subagent Write phantom** (per `feedback_subagent_write_phantom`). If any subagent claims to have written the test file or wiki page, main session must `ls` independently before believing.

---

## Risks and Open Questions

- **Risk (load-bearing):** Production wiki page `knowledge/wikis/engineering/wiki/standards/dnv-os-e301.md` is missing. Without it, prod callers fail-closed. **Mitigation:** create the page in the same PR with valid frontmatter — see AC6 (now unconditional in r2).
- **Risk (NEW in r2, fix #3 — semantic difference between old and new method):** `check_mbl_with_safety_factor()` returns utilisation values that are **NOT comparable** to `check_mbl()`. The legacy `check_mbl(max_tension_kn)` returns `max_tension / mbl`; the new method returns `(max_tension * SF) / mbl`. For intact SF=1.67, a load that read 0.60 utilisation under the legacy method reads 1.002 (FAIL) under the new method. **This is a deliberate engineering correctness improvement** (DNV-OS-E301 §2.2.3 mandates the SF be applied) but **migrating callers MUST recalibrate any utilisation thresholds, dashboards, or PASS/FAIL boundaries**. **Mitigations:** (a) renamed method (`...with_safety_factor` not `...with_citations`) so the semantic shift is impossible to miss at the call site; (b) docstring contains explicit `⚠️ SEMANTIC DIFFERENCE` block; (c) the new return dict includes `utilisation_no_sf` alongside `utilisation_with_sf` so callers can diff numerically during their migration; (d) leave `check_mbl()` unchanged — no caller is silently upgraded, migration is opt-in by method name.
- **Risk:** `check_mbl()` (the existing, citation-free method) has unknown external callers. Leave it intact; expose new functionality via `check_mbl_with_safety_factor()` only. Removal is a future deprecation cycle.
- **Risk:** This is a load-bearing calc module. **Rollback plan:** the changes are additive (new methods, new test file, new wiki page) plus *no edits* to `check_mbl()`, `solve_catenary()`, `estimate_catenary()`, or the material library. Rollback = revert the single commit; existing callers remain green because nothing they use changed. The wiki page addition is also additive (a new file, not an edit). The rule file edit is a one-line text swap, trivially revertable.
- **Open Q for user approval:** Should we deprecate `safety_factor_intact`/`safety_factor_damaged` Pydantic fields in this PR (warn-on-access), or leave for a follow-up cleanup issue? Recommend follow-up to keep this PR tightly scoped.
- **Open Q for user approval:** Wiki page body — pilot stub (frontmatter + 1-paragraph placeholder) OR delegate to the domain-knowledge-sweep #2676 backlog (which is actively researching DNV-OS-E301)? Recommend pilot stub now, full body via #2676.
- **Risk (NEW in r3, gemini r2 F1 — theatre tradeoff acknowledged):** This pilot adds `check_mbl_with_safety_factor()` as a NEW method alongside the existing `check_mbl()`. The legacy method remains untouched and is the only one currently called from production code paths. **As of plan-approval, the new method has ZERO src/ callers** — it exists for explicit caller opt-in only. This is a deliberate tradeoff between safety (no silent semantic shift in existing calls) and immediate citation coverage (the citation contract only kicks in when a caller migrates). **Mitigation:** (a) follow-up issue tracks migration of high-value internal callers (`solve_mooring_design`, batch reporters) to the new method on a deliberate cadence; (b) the `_resolve_sf_for_condition()` helper is the *single* SF resolution path going forward — any future method that consumes SFs uses it, ensuring no silent regression to non-cited SF lookups; (c) memory entry `feedback_silent_verdict_flip_defect_class` (2026-05-13) warns against the "rename creates silent migration risk" pattern and is referenced in the new method's docstring.

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
