# Calculation Output Citation Contract

> **Scope:** defines the schema and operational contract by which engineering code modules (digitalmodel, assetutilities, etc.) emit wiki-backed citations alongside calculation outputs.
> **Status:** v1 — pilot scope is one digitalmodel mooring calculation (#2481). Broad rollout is future work.
> **Governing issue:** [#2481](https://github.com/vamseeachanta/workspace-hub/issues/2481)
> **Frontmatter schema source:** [#2471](https://github.com/vamseeachanta/workspace-hub/issues/2471) decision for wiki standards pages

## 1. Why citations in calc output

Engineering calculation outputs that derive from standards/manuals (DNV, API, ISO, OCIMF, Orcina, etc.) must be defensible to a reviewer. "Where does this coefficient come from?" has historically been answered via convention, engineer memory, or a PDF in a shared drive. This contract formalizes it: every standards-derived constant in a calc output carries a machine-verifiable citation to the wiki page encoding the source.

This turns `llm-wiki` from a retrieval surface into an **audit-trail surface** for engineering deliverables.

## 2. Citation schema

```python
@dataclass(frozen=True)
class Citation:
    code_id: str      # canonical join key matching wiki frontmatter (e.g., "DNV-OS-E301")
    publisher: str    # standards body (e.g., "DNV", "API", "ISO", "OCIMF", "Orcina")
    revision: str     # publisher revision identifier (e.g., "2021-07", "4th-Edition-2018")
    section: str      # clause/section/table/figure identifier (e.g., "Table C-1", "Section 2.2.3")
    wiki_path: str    # repo-relative path to the wiki page (e.g., "knowledge/wikis/engineering/wiki/standards/dnv-os-e301.md")
    note: str = ""    # optional free text (e.g., "used factor from Table 3; quasi-static intact condition")
```

A `Citation` is always paired with the numeric value it justifies:

```python
@dataclass(frozen=True)
class CitedValue:
    value: float           # the calc-domain value (e.g., 1.67 for a safety factor)
    citation: Citation     # provenance
    units: str = ""        # optional SI units annotation (e.g., "dimensionless", "MPa", "kN")
```

## 3. Field requirements

All five required fields (`code_id`, `publisher`, `revision`, `section`, `wiki_path`) must be populated. Missing required field → `ValidationError` at schema construction.

- `code_id` MUST match the `code_id` frontmatter field of the wiki page at `wiki_path`. This is the #2471 canonical join key.
- `publisher` MUST match the `publisher` frontmatter field.
- `revision` MUST match the `revision` frontmatter field.
- `wiki_path` MUST be repo-relative (not absolute, not `..`-escaping). Path outside `knowledge/wikis/` → `ValidationError`.
- `section` is a human-readable locator (Table/Section/Figure/Clause). Not validated against wiki content; trust the author.

## 4. Resolution behavior

Before returning a `CitedValue`, the calling code (or a shared validator) MUST verify the citation resolves:

```python
def validate(citation: Citation) -> None:
    """Raise CitationResolutionError if the cited wiki page does not exist or frontmatter mismatches."""
    path = Path(REPO_ROOT) / citation.wiki_path
    if not path.exists():
        raise CitationResolutionError(code_id=citation.code_id, wiki_path=citation.wiki_path, reason="page_missing")
    fm = read_frontmatter(path)
    for field in ("code_id", "publisher", "revision"):
        if fm.get(field) != getattr(citation, field):
            raise CitationResolutionError(
                code_id=citation.code_id, wiki_path=citation.wiki_path,
                reason=f"frontmatter_mismatch:{field}:{fm.get(field)!r}!={getattr(citation, field)!r}",
            )
```

### 4.1 Fail-closed semantics (D2 decision per #2481)

Resolution failures are **hard errors at calc time**, not warnings. A missing or stale citation aborts the calc with a `CitationResolutionError` that carries the `code_id` in its message so operators can retarget the citation rather than disabling it. Rationale: professional-practice engineering outputs should not silently ship without provenance.

### 4.2 Resolver implementation (D3 decision per #2481)

v1 resolver uses direct file read (`pathlib.Path(wiki_path).exists()` plus YAML frontmatter parse). When [#2400](https://github.com/vamseeachanta/workspace-hub/issues/2400) ships the MCP `wiki_search` tool, the resolver implementation can swap to MCP without changing the citation schema or the calling code.

## 5. Wiki page frontmatter contract (forward-adopted from #2471)

Wiki pages that are citation targets MUST carry the three #2471 fields in their frontmatter:

```yaml
---
title: "DNV-OS-E301 — Position Mooring"
code_id: DNV-OS-E301
publisher: DNV
revision: 2021-07
tags: [standard, dnv, mooring, position-mooring]
...
---
```

Until #2471 lands broadly, the citation-emitting pilot forward-adopts these fields on the specific wiki pages it cites. Pages without these fields cannot be citation targets.

## 6. Output placement

Citations emit to a **sidecar** — they do NOT modify the primary result payload:

- Python function returns `CitedValue` instead of a bare `float` — but `.value` preserves the numeric interface.
- Calc reports may attach a "Citations" section at the end; the body of the report is unchanged.
- JSON output: `{"result": <bare value>, "citations": [<Citation as dict>, ...]}`.

This prevents citation emission from breaking downstream consumers that expect plain numeric output.

## 7. Adoption

This contract is authoritative for any new or migrated calc code that consumes standards-derived constants. The rule for agents to invoke this contract is at `.claude/rules/calc-citation-contract.md`.

Pilot module (per #2481 D1 decision): `digitalmodel/src/digitalmodel/orcaflex/mooring_design.py` — safety factor constants for intact/damaged mooring conditions.

## 8. References

- #2481 — governing issue
- #2471 — `code_id` / `publisher` / `revision` wiki frontmatter decision
- #2482 — llm-wiki → GTM boundary (complementary; citations never route to GTM)
- #2238 — closed-issue citation guardrail (covers durable docs; this contract covers calc outputs)
- #2400 — MCP wiki_search (future resolver backend)
- #2485 — GTM boundary enforcement linter (separate concern)
