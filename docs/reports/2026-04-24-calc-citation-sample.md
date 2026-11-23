# Calc-output citation — worked example (#2481 pilot)

> **Context:** sample output demonstrating the citation contract defined in `docs/standards/calc-output-citation.md` against the pilot module at `digitalmodel/src/digitalmodel/citations/`.
> **Date:** 2026-04-24
> **Pilot:** mooring safety factors from DNV-OS-E301

## Scenario

An engineer running a mooring design calculation needs the DNV-OS-E301 design safety factor for the intact quasi-static condition. Historically this constant has appeared as a hardcoded `1.67` in `digitalmodel/src/digitalmodel/orcaflex/mooring_design.py` with a prose comment referencing API RP 2SK. The pilot formalizes that provenance.

## Code invocation

```python
from pathlib import Path
from digitalmodel.citations.registry import MooringCondition, get_mooring_safety_factor

repo_root = Path("/mnt/local-analysis/workspace-hub")
cv = get_mooring_safety_factor(MooringCondition.INTACT_QUASI_STATIC, repo_root=repo_root)

print(cv.value)         # 1.67
print(cv.units)         # "dimensionless"
print(cv.citation.code_id)    # "DNV-OS-E301"
print(cv.citation.publisher)  # "DNV"
print(cv.citation.revision)   # "2021-07"
print(cv.citation.section)    # "Section 2.2.3 (intact, quasi-static)"
print(cv.citation.wiki_path)  # "knowledge/wikis/engineering/wiki/standards/dnv-os-e301.md"
```

## JSON sidecar (per §6 of the contract)

When a calc report emits JSON, citations live in a sidecar alongside the numeric result — not mixed into it:

```json
{
  "result": {
    "mooring_safety_factor_intact": 1.67,
    "mooring_safety_factor_damaged": 1.25
  },
  "citations": [
    {
      "value_key": "mooring_safety_factor_intact",
      "code_id": "DNV-OS-E301",
      "publisher": "DNV",
      "revision": "2021-07",
      "section": "Section 2.2.3 (intact, quasi-static)",
      "wiki_path": "knowledge/wikis/engineering/wiki/standards/dnv-os-e301.md",
      "note": "Design factor for intact-quasi-static condition"
    },
    {
      "value_key": "mooring_safety_factor_damaged",
      "code_id": "DNV-OS-E301",
      "publisher": "DNV",
      "revision": "2021-07",
      "section": "Section 2.2.3 (damaged, quasi-static)",
      "wiki_path": "knowledge/wikis/engineering/wiki/standards/dnv-os-e301.md",
      "note": "Design factor for damaged-quasi-static condition"
    }
  ]
}
```

Downstream consumers that expect bare numeric output ignore `citations` and read `result` as before. Audit consumers read `citations` to reconstruct provenance.

## Fail-closed behavior (D2)

If the cited wiki page is moved, deleted, or its frontmatter stops matching, the registry call raises at calc time:

```python
# If knowledge/wikis/engineering/wiki/standards/dnv-os-e301.md is moved/renamed:
get_mooring_safety_factor(MooringCondition.INTACT_QUASI_STATIC, repo_root=repo_root)
# CitationResolutionError: code_id='DNV-OS-E301' wiki_path='knowledge/wikis/engineering/wiki/standards/dnv-os-e301.md' reason=page_missing

# If the page exists but frontmatter revision changes upstream:
# CitationResolutionError: code_id='DNV-OS-E301' wiki_path='knowledge/wikis/engineering/wiki/standards/dnv-os-e301.md' reason=frontmatter_mismatch:revision:'2021-07'!='2099-99'
```

The `code_id` in the error message tells operators which standard the registry expects — they can then retarget the citation to the correct wiki page (or update the citation's expected revision) rather than disabling the check.

## What this pilot proves

1. **Schema works**: `Citation` and `CitedValue` compose cleanly; invalid citations are rejected at construction time.
2. **Resolution works**: the cited wiki page is verified against live frontmatter on every getter call.
3. **Fail-closed works**: missing pages and frontmatter mismatches both raise `CitationResolutionError` with the `code_id` surfaced in the message.
4. **Sidecar placement works**: citations can be emitted alongside numeric results without changing the primary calc output shape.
5. **Forward-compatibility with #2471**: the pilot forward-adopted `code_id`/`publisher`/`revision` frontmatter on the two wiki pages it cites (`dnv-os-e301.md`, `ocimf-meg4.md`). When #2471 rolls out broadly, the schema doesn't change.

## What this pilot does NOT claim

- Broad rollout across digitalmodel modules — that is future work per #2481 scope.
- Runtime PDF/HTML report generation with footnoted citations — separate concern.
- Regulator-facing audit-trail format — separate concern.

## Smoke-check output (captured 2026-04-24)

```
PASS: happy-path resolution
PASS: intact factor = 1.67 with citation DNV-OS-E301
PASS: damaged factor = 1.25
PASS: missing-page raises with code_id
PASS: frontmatter-mismatch raises
PASS: path-traversal rejected
PASS: empty code_id rejected
PASS: wrong-root raises
ALL SMOKE CHECKS PASS
```

## Next steps

- #2400 MCP wiki_search lands → swap resolver backend (no schema change)
- #2471 broad rollout → remove forward-adopt exception on dnv-os-e301.md / ocimf-meg4.md
- Future follow-up: migrate `mooring_design.py` `safety_factor_intact`/`safety_factor_damaged` Pydantic Field defaults to call the registry (currently the registry duplicates the constants with citations attached)
