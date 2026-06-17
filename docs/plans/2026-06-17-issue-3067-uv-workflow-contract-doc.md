# Plan for #3067: UV workflow contract standard doc

> **Status:** draft
> **Complexity:** T1
> **Date:** 2026-06-17
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/3067
> **Client:** N/A
> **Project:**
> **Lane:** lane:claude
> **Review artifacts:** scripts/review/results/2026-06-17-plan-3067-claude.md | ...-codex.md | ...-gemini.md

---

## Resource Intelligence Summary

### Existing repo code

- Found: `docs/standards/CONTROL_PLANE_CONTRACT.md` — naming/structure convention for canonical contracts in workspace-hub; confirms target path is `docs/standards/UV_WORKFLOW_CONTRACT.md` (ALLCAPS contract pattern).
- Found: `docs/standards/MODEL_RELEASE_READINESS_CONTRACT.md` — confirms 2-section structure: contract body + tier-specific addenda.
- Found: `docs/modules/workflow/DEVELOPMENT_WORKFLOW.md` — covers git/PR/review workflow, NOT the UV invocation contract; no overlap with this doc.
- Gap: `docs/standards/UV_WORKFLOW_CONTRACT.md` — does NOT exist; must create.
- Gap: `docs/registry/workflows.yaml` — directory does NOT exist in workspace-hub; the contract doc will define the schema but workspace-hub itself does not carry a registry (it is the host of the standard, not a workflow repo).

### Standards

| Standard | Status | Source |
|---|---|---|
| durable-workflow-registries pattern | codified in dm#710 + wed#471 + deckhand#282 | epic #3050 body references |
| UV workflow invocation contract | defined in epic #3050 body | issue #3050 — ratified 2026-06-13 |

Not a traditional engineering standard. This issue IS the act of codifying the agreed-upon contract into a durable doc.

### LLM Wiki pages consulted

- `[[durable-workflow-registries]]` — referenced in issue #3067 body and #3050 as the pattern source; not directly accessible from workspace-hub (wiki path), but the pattern is fully reproduced in the #3050 epic body which serves as the canonical source for this plan.

### Documents consulted

- Issue #3067 body — 7-item must-cover checklist (the doc's required sections); treated as the specification.
- Issue #3050 body — full contract specification including: engine pattern, registry schema (`schema_version 1`: id/basename/input/outputs/test/runtime), the anti-patterns (assethold `in`-substring bug, assetutilities#88 wheel omission), deckhand consumption contract, tier-1 repo audit table ratified 2026-06-13.
- `docs/standards/CONTROL_PLANE_CONTRACT.md` — structural template for contract docs in this repo (heading hierarchy, audience framing).
- `docs/standards/HARD-STOP-POLICY.md` — another precedent contract doc; confirms tone (operator-direct, no hedging).

### Gaps identified

- No UV workflow contract doc exists anywhere in the repo.
- `docs/registry/` directory does not exist (workspace-hub is not a workflow repo, so this is expected — the contract doc defines the schema for tier-1 repos to implement, not for workspace-hub itself).

### Evidence (embedded verification)

**Issue statuses** (verified 2026-06-17T via GitHub MCP):
- `#3067` — OPEN — uv-workflow(workspace-hub): write the canonical UV workflow contract standard doc
- `#3050` — OPEN — EPIC: confirm tier-1 repos + drive workflows through the UV package
- `#3063` — OPEN — assetutilities (prereq, blocked on #88)
- `#3065` — OPEN — digitalmodel (additive quick win)
- `#3066` — OPEN — assethold (heaviest, last)

**File existence** (verified 2026-06-17T via Bash):
- EXISTS: `docs/standards/CONTROL_PLANE_CONTRACT.md`
- EXISTS: `docs/standards/MODEL_RELEASE_READINESS_CONTRACT.md`
- EXISTS: `docs/modules/workflow/DEVELOPMENT_WORKFLOW.md`
- MISSING (new — this plan creates): `docs/standards/UV_WORKFLOW_CONTRACT.md`
- MISSING (by design — workspace-hub is not a workflow repo): `docs/registry/`

**Gap proofs**:
- `ls docs/standards/ | grep -i uv` → no output → no UV contract doc exists
- `ls docs/registry/` → "No such file or directory" → confirmed absent (by design)

**Reproduction proofs**:
N/A — documentation issue. Skip allowed per template. Reason: no runtime failure to reproduce; the issue is absence of a document, not a broken behavior.

<!-- Source count: issue body (#3067), epic body (#3050), docs/standards/CONTROL_PLANE_CONTRACT.md, docs/standards/HARD-STOP-POLICY.md, docs/modules/workflow/DEVELOPMENT_WORKFLOW.md = 5 distinct sources ✓ -->

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-06-17-issue-3067-uv-workflow-contract-doc.md` |
| Contract doc (new) | `docs/standards/UV_WORKFLOW_CONTRACT.md` |
| Plan review — Claude | `scripts/review/results/2026-06-17-plan-3067-claude.md` |
| Plan review — Codex | `scripts/review/results/2026-06-17-plan-3067-codex.md` |
| Plan review — Gemini | `scripts/review/results/2026-06-17-plan-3067-gemini.md` |

---

## Deliverable

A single `docs/standards/UV_WORKFLOW_CONTRACT.md` file that is the definitive reference for the `uv run python -m <pkg> <input.yml>` invocation contract — covering engine pattern, registry schema, package-data rule, fail-closed routing, deckhand consumption, and CI gate template — so any repo adopting the contract has a single document to check against.

---

## Pseudocode

T1 — trivial; see Files to Change. The doc structure is defined by #3067's must-cover checklist. No implementation logic to pseudocode.

**Planned document outline** (maps directly to issue #3067 checklist):

```
# UV Workflow Contract

## 1. The Contract (1 sentence)
   uv run python -m <pkg> <input.yml>  ← the single canonical invocation

## 2. Engine Pattern
   __main__.py → engine(inputfile) → cfg["basename"] switch → router()
   - YAML-file arg MUST route to engine(), not bypass via CLI subcommands
   - engine() is a basename equality switch (==), never substring (in "x")

## 3. Registry Schema (docs/registry/workflows.yaml)
   schema_version: 1
   workflows:
     - id: <str>
       basename: <str>       # matches engine() switch value
       input: examples/workflows/<basename>/input.yml
       outputs: [...]        # declared output files/dirs
       test: tests/workflows/test_<basename>.py
       runtime: uv run python -m <pkg> <input.yml>
   invariant: registry rows == example dirs == green-CI jobs

## 4. Package-Data Rule
   - base_configs/**, templates/, pkgutil-loaded configs MUST be in wheel MANIFEST
   - Use package_data or include-package-data = true in pyproject.toml
   - Anti-pattern: assetutilities#88 — worked from source, broke from wheel

## 5. Fail-Closed Routing
   - Unknown basename → raise ValueError (never silently dispatch)
   - Anti-pattern: assethold if basename in "stocks" → substring match;
     use if basename == "stocks" or basename in {"stocks", ...}

## 6. Deckhand / Bot Consumption
   - Bot reads docs/registry/workflows.yaml to discover runnable workflows
   - Unregistered workflow → 24h ESCALATE SLA (bot cannot route it)
   - Registry is the source of truth; ad-hoc scripts invisible to bot

## 7. CI Gate Template
   test-workflows job:
     - clean uv sync (no --no-dev cache reuse)
     - for each registry row: uv run python -m <pkg> <row.input>
     - assert declared outputs exist + are non-empty
     - data-backed workflows: offline fixture OR documented live-dep annotation
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | `docs/standards/UV_WORKFLOW_CONTRACT.md` | canonical contract doc (the sole deliverable) |

No other files require modification. The doc is self-contained and references the existing `docs/standards/` neighbors by proximity.

---

## TDD Test List

Documentation issue — no executable tests. Acceptance is content-based: every required section from the #3067 checklist must appear in the doc.

| Required section | Verifiable by | Pass condition |
|---|---|---|
| Invocation contract line | `grep "uv run python -m" docs/standards/UV_WORKFLOW_CONTRACT.md` | present |
| Engine pattern (`__main__` → `engine`) | section heading + code block | present |
| Registry schema (`schema_version 1` with all 6 fields) | YAML block with id/basename/input/outputs/test/runtime | all 6 fields named |
| Package-data rule + assetutilities#88 callout | section present | present |
| Fail-closed routing + assethold anti-pattern | section present | present |
| Deckhand consumption + 24h SLA | section present | present |
| CI gate template | code/YAML block showing the 3-step gate | present |

---

## Acceptance Criteria

- [ ] `docs/standards/UV_WORKFLOW_CONTRACT.md` exists and passes the completeness checklist (`gate:completeness` label present on issue)
- [ ] All 7 sections from the #3067 must-cover list appear in the doc
- [ ] Registry schema block names all 6 fields: `id`, `basename`, `input`, `outputs`, `test`, `runtime`
- [ ] Fail-closed routing section explicitly names the assethold `in`-substring anti-pattern
- [ ] Package-data section explicitly references assetutilities#88 as the cautionary tale
- [ ] Deckhand/bot section states the 24h ESCALATE SLA for unregistered workflows
- [ ] CI gate section includes: `uv sync`, per-row invocation, output assertion, and data-dependency annotation rule
- [ ] Doc length: 200–600 lines (sufficient for a reference, not a tutorial)
- [ ] Review artifacts posted to `scripts/review/results/`

---

## Adversarial Review Summary

<!-- Filled in after adversarial review step. -->

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | — | pending |
| Codex | — | pending |
| Gemini | — | pending |

**Overall result:** pending

---

## Risks and Open Questions

- **Sequencing soft dependency:** The issue says "after first repo lands (so the doc reflects reality)." None of the sibling repos (#3063–#3066) are merged yet. However, the pattern is real (dm#710/wed#471/deckhand#282 are landed), and the epic body already specifies the contract in detail. **Decision:** draft the doc now against the epic spec; if sibling PRs reveal deviations, update the doc before closing.
- **worldenergydata PR #477:** The drafter routine discovered that #3064's implementation may already exist as PR #477 on worldenergydata. If merged, #3064 scope is done and worldenergydata is a verified reference implementation for the contract doc. The implementer should confirm PR #477 state before writing §7 CI gate template.
- **Doc audience:** Is this a human-readable guide or a machine-parseable contract? The existing `CONTROL_PLANE_CONTRACT.md` is human-readable. Recommend following that pattern (Markdown with code blocks, no YAML frontmatter schema enforcement). Add a "Machine consumption" note pointing to the registry YAML for tooling.
- **Open:** Should the contract doc link to all three reference implementations (dm#710/wed#471/deckhand#282 PR numbers)? Yes — they are the ground truth the doc codifies; cite them explicitly in a §References section.

---

## Complexity: T1

**T1** — single new file (`docs/standards/UV_WORKFLOW_CONTRACT.md`), no code changes, no executable tests, no cross-repo impact. All content is fully specified in issue #3067 body + epic #3050 body. Can ship in one focused writing session.
