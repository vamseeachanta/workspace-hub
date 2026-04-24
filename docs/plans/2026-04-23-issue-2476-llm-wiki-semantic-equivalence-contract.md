# Plan for #2476: llm-wiki canonical semantic-equivalence contract and fixture cookbook

> **Status:** plan-approved (v3 — user explicitly waived broken Codex/Gemini review-runner issue for #2475/#2476 on 2026-04-24)
> **Complexity:** T2
> **Date:** 2026-04-23
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2476
> **Review artifacts:** scripts/review/results/2026-04-23-plan-2476-claude.md | scripts/review/results/2026-04-23-plan-2476-codex.md | scripts/review/results/2026-04-23-plan-2476-gemini.md

---

## Resource Intelligence Summary

### Existing repo code
- Found: `digitalmodel/src/digitalmodel/hydrodynamics/diffraction/input_schemas.py` — canonical `DiffractionSpec` schema surface for OrcaWave inputs.
- Found: `digitalmodel/src/digitalmodel/hydrodynamics/diffraction/orcawave_backend.py` — canonical spec to native OrcaWave YAML backend; PR #528 added `_effective_solve_type(spec)` so `analysis_type: full_qtf` maps to native `Full QTF calculation`.
- Found: `digitalmodel/src/digitalmodel/hydrodynamics/diffraction/reverse_parsers.py` — native OrcaWave input back to canonical semantics.
- Found: `digitalmodel/src/digitalmodel/solvers/orcaflex/modular_generator/` — canonical `ProjectInputSpec` / modular OrcaFlex generation surface used by #2455/#2456.
- Found: `digitalmodel/src/digitalmodel/hydrodynamics/diffraction/orcawave_to_orcaflex.py` — bridge from OrcaWave sidecar data to OrcaFlex export, including RAOData to DiffractionResults conversion.
- Gap: no durable llm-wiki page currently defines the cross-solver semantic-equivalence contract for `spec.yml -> native solver input`.

### Standards
| Standard / contract | Status | Source |
|---|---|---|
| Workspace issue-planning retrieval contract | active | `docs/plans/README.md` lines 37-66 |
| llm-wiki frontmatter/index/log contract | active | `knowledge/wikis/engineering/CLAUDE.md` lines 10-42 |
| OrcaWave/OrcaFlex machine-boundary contract | active | `docs/maps/digitalmodel-orcawave-orcaflex-operator-map.md` lines 175-193 |

### LLM Wiki pages consulted
- `knowledge/wikis/engineering/wiki/index.md` — engineering wiki already has relevant entities and workflow pages: `OrcaWave Solver`, `OrcaFlex Solver`, `Diffraction Analysis System`, `Solver Queue`, and `OrcaWave-to-OrcaFlex Pipeline`.
- `knowledge/wikis/engineering/wiki/workflows/orcawave-to-orcaflex-pipeline.md` — documents handoff flow and convention conversions, but is too narrow for a general semantic-equivalence contract/cookbook.
- `knowledge/wikis/engineering/wiki/entities/orcaflex-solver.md` and `knowledge/wikis/engineering/wiki/entities/orcawave-solver.md` exist and should be cross-linked from any new contract page.
- `knowledge/wikis/marine-engineering/wiki/sources/15-optimization-of-calm-buoy-export-terminal-availability.md` exists and can support future CALM/SPM fixture examples, but this issue should not add new CALM implementation.

### Documents consulted
- Issue #2476 — asks for durable llm-wiki/knowledge-base pages defining semantic equivalence and fixture cookbook before expanding coverage.
- `docs/handoffs/2026-04-23-orcawave-orcaflex-semantic-proof-exit-handoff.md` — lists six llm-wiki gaps: semantic-equivalence contract, DiffractionSpec examples, ProjectInputSpec examples, OrcaWave-to-OrcaFlex handoff case study, licensed solver proof protocol, fixture expansion cookbook.
- `docs/handoffs/2026-04-24-orcawave-orcaflex-next-wave-closeout.md` — names #2476 as the recommended first next-wave plan.
- `docs/maps/digitalmodel-orcawave-orcaflex-operator-map.md` — canonical code/test/machine-boundary map.
- Closed issues #2455/#2456/#2457 and merged digitalmodel PR #528 — first-wave proof evidence for PLET-to-PLEM, lazy/steep-wave riser, and L03 OrcaWave roundtrip.
- Related issues #2472/#2473/#2474/#2475 — downstream proof issues that should consume this contract, not be silently implemented here.
- Related llm-wiki issues #2088/#2102/#2123 — generic Orcina help ingestion/search wiring is separate from the semantic-proof contract.

### Gaps identified
- No page defines mandatory equivalence dimensions: object identity, units, coordinate/body frames, sign conventions, solver option mapping, frequency/heading domains, native-default tolerances, file/path provenance, and acceptable formatting/default differences.
- No fixture expansion cookbook exists for adding structure-family semantic proofs without overfitting to one generated YAML formatting style.
- Existing `orcawave-to-orcaflex-pipeline.md` needs an update to reference the broader contract and distinguish handoff semantics from native solver load/run proof.
- Existing `engineering/wiki/index.md` and `engineering/wiki/log.md` must be updated for any new/changed wiki pages.

### Evidence (embedded verification)

**Issue statuses** (verified 2026-04-23 via `gh issue view`):
- `#2476` — OPEN — docs(llm-wiki): add canonical spec semantic-equivalence contract and fixture cookbook
- `#2475` — OPEN — chore(licensed-proof): define OrcaWave/OrcaFlex native load-run proof protocol
- `#2455/#2456/#2457` — CLOSED — first-wave semantic proof issues closed by PR #528
- `#2088/#2102` — CLOSED — prior generic llm-wiki ingestion/wiring
- `#2123` — OPEN — llm-wiki search invocation wiring, separate from this issue

**File existence** (verified 2026-04-23 from `/mnt/local-analysis/workspace-hub`):
- EXISTS: `knowledge/wikis/engineering/CLAUDE.md`
- EXISTS: `knowledge/wikis/engineering/wiki/index.md`
- EXISTS: `knowledge/wikis/engineering/wiki/log.md`
- EXISTS: `knowledge/wikis/engineering/wiki/workflows/orcawave-to-orcaflex-pipeline.md`
- EXISTS: `knowledge/wikis/engineering/wiki/entities/orcaflex-solver.md`
- EXISTS: `knowledge/wikis/engineering/wiki/entities/orcawave-solver.md`
- MISSING (new): `knowledge/wikis/engineering/wiki/concepts/canonical-spec-semantic-equivalence.md`
- MISSING (new): `knowledge/wikis/engineering/wiki/workflows/orcawave-orcaflex-fixture-expansion-cookbook.md`

**Line excerpts**:
- `knowledge/wikis/engineering/CLAUDE.md` requires frontmatter fields `title`, `tags`, `added`, `last_updated`; pages live under `wiki/{concepts,entities,sources,standards,workflows}/`.
- `knowledge/wikis/engineering/wiki/index.md` already lists `OrcaWave-to-OrcaFlex Pipeline` under Workflows and solver entities under Entities.
- `knowledge/wikis/engineering/wiki/workflows/orcawave-to-orcaflex-pipeline.md` lines 32-39 document specific convention conversions, but not the full cross-solver equivalence contract.

Source count: 8+ distinct sources consulted (issue #2476, handoff files, operator map, engineering wiki schema/index/workflow, related issue set, PR #528 context).

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-04-23-issue-2476-llm-wiki-semantic-equivalence-contract.md` |
| New concept page | `knowledge/wikis/engineering/wiki/concepts/canonical-spec-semantic-equivalence.md` |
| New workflow/cookbook page | `knowledge/wikis/engineering/wiki/workflows/orcawave-orcaflex-fixture-expansion-cookbook.md` |
| Update existing workflow | `knowledge/wikis/engineering/wiki/workflows/orcawave-to-orcaflex-pipeline.md` |
| Update wiki index | `knowledge/wikis/engineering/wiki/index.md` |
| Update wiki log | `knowledge/wikis/engineering/wiki/log.md` |
| Plan review — Claude | `scripts/review/results/2026-04-23-plan-2476-claude.md` |
| Plan review — Codex | `scripts/review/results/2026-04-23-plan-2476-codex.md` |
| Plan review — Gemini | `scripts/review/results/2026-04-23-plan-2476-gemini.md` |
| Plan index | `docs/plans/README.md` |

---

## Deliverable

Under repo root `/mnt/local-analysis/workspace-hub`, a durable engineering llm-wiki semantic-equivalence contract plus fixture expansion cookbook for OrcaWave/OrcaFlex canonical `spec.yml -> native solver input` proofs, indexed/logged in the wiki and cross-linked from the existing handoff workflow page.

---

## Pseudocode

```text
create canonical-spec-semantic-equivalence page:
    define scope: deterministic semantic proof, not licensed solver execution
    enumerate equivalence dimensions: object identity, units, frames, signs, solver options, frequency/heading domains, defaults, provenance
    include examples from L03 OrcaWave, PLET-to-PLEM, lazy/steep-wave, steep-wave
    link downstream issues #2472-#2475 and existing workflow/entity pages

create fixture-expansion-cookbook page:
    define minimal fixture selection criteria
    define canonical spec fields required per solver family
    define native assertion checklist that avoids formatting overfit
    define review/evidence checklist and when licensed-machine proof is required
    include candidate next families: CALM/SPM, FPSO, multi-body, hydrodynamic handoff

update orcawave-to-orcaflex-pipeline page:
    add semantic-contract link
    clarify RAO/hydrodynamic handoff proof vs native load/run proof

update index/log:
    add new pages to correct sections
    increment page_count and update last_updated
    append 2026-04-23 log entry listing changed files
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | `knowledge/wikis/engineering/wiki/concepts/canonical-spec-semantic-equivalence.md` | Main semantic-equivalence contract |
| Create | `knowledge/wikis/engineering/wiki/workflows/orcawave-orcaflex-fixture-expansion-cookbook.md` | Procedure for adding future fixture proofs |
| Modify | `knowledge/wikis/engineering/wiki/workflows/orcawave-to-orcaflex-pipeline.md` | Cross-link and distinguish handoff/load-run proof boundaries |
| Modify | `knowledge/wikis/engineering/wiki/index.md` | Add new pages and update metadata |
| Modify | `knowledge/wikis/engineering/wiki/log.md` | Append change log entry |
| Modify | `docs/plans/README.md` | Add plan index row |

---

## TDD / Validation List

| Check | What it verifies | Command / input | Expected output |
|---|---|---|---|
| wiki_pages_exist | new concept and cookbook pages exist | `test -f knowledge/wikis/engineering/wiki/concepts/canonical-spec-semantic-equivalence.md && test -f knowledge/wikis/engineering/wiki/workflows/orcawave-orcaflex-fixture-expansion-cookbook.md` | both exist |
| frontmatter_contract | required frontmatter fields present | `uv run --no-project python - <<'PY'
from pathlib import Path
import re, sys
for p in [Path('knowledge/wikis/engineering/wiki/concepts/canonical-spec-semantic-equivalence.md'), Path('knowledge/wikis/engineering/wiki/workflows/orcawave-orcaflex-fixture-expansion-cookbook.md')]:
    text=p.read_text(); fm=re.search(r'^---\n(.*?)\n---', text, re.S|re.M); assert fm, p
    for key in ['title:', 'tags:', 'added:', 'last_updated:']: assert key in fm.group(1), (p,key)
PY` | no missing `title/tags/added/last_updated` |
| wikilink_contract | each new page has ≥2 links to related pages/issues | `uv run --no-project python - <<'PY'
from pathlib import Path
import re
for p in [Path('knowledge/wikis/engineering/wiki/concepts/canonical-spec-semantic-equivalence.md'), Path('knowledge/wikis/engineering/wiki/workflows/orcawave-orcaflex-fixture-expansion-cookbook.md')]:
    text=p.read_text(); links=re.findall(r'\[[^\]]+\]\([^\)]+\)|\[\[[^\]]+\]\]|#[0-9]+', text); assert len(links) >= 2, (p, len(links))
PY` | count ≥2 per page |
| index_updated | `index.md` references both new pages | `grep -E 'canonical-spec-semantic-equivalence|orcawave-orcaflex-fixture-expansion-cookbook' knowledge/wikis/engineering/wiki/index.md` | both found |
| log_updated | `log.md` has 2026-04-23 entry listing changed pages | `grep -E '2026-04-23.*canonical-spec-semantic-equivalence|2026-04-23.*orcawave-orcaflex-fixture-expansion-cookbook' knowledge/wikis/engineering/wiki/log.md` | found |
| no_implementation_scope_creep | no digitalmodel source/test files changed | `git diff --name-only origin/main...HEAD -- knowledge/wikis docs/plans digitalmodel/src digitalmodel/tests` | only wiki + plan/index files for this issue |
| llm_wiki_lint_baseline | wiki health check does not introduce new link/frontmatter warnings beyond pre-existing baseline | `mkdir -p .planning/tmp && uv run scripts/knowledge/llm_wiki.py lint --wiki engineering > .planning/tmp/2476-wiki-lint-before.txt` before edits and repeat to `.planning/tmp/2476-wiki-lint-after.txt`, then compare changed-page warnings | no new errors/warnings attributable to changed pages |

---

## Acceptance Criteria

- [ ] `canonical-spec-semantic-equivalence.md` defines all required equivalence dimensions and explicitly says deterministic semantic proof is not licensed solver execution proof.
- [ ] `orcawave-orcaflex-fixture-expansion-cookbook.md` provides a repeatable checklist for new structure-family fixtures without overfitting to native YAML formatting.
- [ ] Existing `orcawave-to-orcaflex-pipeline.md` links to the new contract/cookbook and clarifies handoff vs licensed proof boundaries.
- [ ] `knowledge/wikis/engineering/wiki/index.md` and `log.md` are updated.
- [ ] Validation checks above pass.
- [ ] No digitalmodel implementation files are touched under this docs-only issue.
- [ ] Plan review artifacts exist and contain no MAJOR blocker before approval.

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | MAJOR (r2) | Artifact-map date drift, missing README in Artifact Map, non-executable validation commands, review-runner unblock path missing, provider packaging failures unresolved. Addressed in v3 where plan-local. |
| Codex | UNAVAILABLE (r1/r2) | `codex exec --no-interactive` wrapper incompatibility; substantive Codex review blocked by review-runner issue outside this plan. |
| Gemini | MAJOR (r2) | Date mismatch, non-executable validation commands, and repository-access packaging problem. Plan-local command issues addressed in v3; provider access still requires runner/package fix. |

**Overall result:** not approval-ready — fresh re-review required after provider-runner/package issues are fixed or explicitly waived by policy. Provider-runner hardening is tracked by #2477.

---

## Risks and Open Questions

- **Risk:** The contract becomes too broad and duplicates future implementation issues. Mitigation: docs-only scope; examples cite existing proofs and candidate future families but do not implement them.
- **Risk:** Wiki link style may prefer markdown links over wikilinks in this repo. Mitigation: follow existing engineering wiki style and lint for broken links.
- **Risk:** Page count/index metadata can drift. Mitigation: update index and log in same commit and run targeted checks.
- **Open:** Whether to add matching pages in `marine-engineering` wiki later. Default: engineering wiki owns workflow/contract; marine-engineering can receive domain-specific CALM/SPM/FPSO case studies in follow-up issues.

---

## Complexity: T2

Docs/wiki-only but touches multiple durable wiki surfaces and defines a reusable contract consumed by #2472-#2475.
