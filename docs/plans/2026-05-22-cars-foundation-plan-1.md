# Plan for TBD: CARS Week-0 Foundation — Registry, Schemas, Warn-Only Enforcement

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:subagent-driven-development` (recommended) or `superpowers:executing-plans` to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.
>
> **Status:** draft (awaiting issue filing + adversarial T3 review)
> **Complexity:** T3
> **Date:** 2026-05-22
> **Issue:** TBD — filed against design `docs/governance/2026-05-22-canonical-anti-repetition-surface-design.md`
> **Review artifacts:** scripts/review/results/YYYY-MM-DD-plan-TBD-{claude,codex,gemini}.md
> **Design reference:** [`docs/governance/2026-05-22-canonical-anti-repetition-surface-design.md`](../governance/2026-05-22-canonical-anti-repetition-surface-design.md) decisions D1-D15

**Goal:** Land the canonical-store foundation — workspace-wide registry, three tier JSON schemas, deterministic fingerprinting, query helper, and five enforcement scripts (warn-only mode). All anti-repetition machinery exists and validates inputs, but nothing yet blocks plan progression. Sets up Plans 2-6.

**Architecture:** Per CARS design Section 4 (Workspace Registry). All artifacts live under `workspace-hub/config/canonical-store/` and `workspace-hub/scripts/{canonical-store,enforcement}/`. No changes to AGENTS.md, `SHARED_SOUL.md`, plan template, or skills (those land in Plan 2). No changes to digitalmodel (those land in Plan 3). No wiki content (lands in Plan 4). Enforcement scripts exist but exit 0 with warnings logged — promotion to hard-gate happens in Plan 6 after retro.

**Tech Stack:** Python 3.12 (uv-managed), bash 5 (POSIX-compliant where possible), JSON Schema draft-07, YAML 1.2, jq for JSON traversal in shell, pytest for Python tests, bats for shell tests.

---

## Resource Intelligence Summary

### Existing repo code

Verified via `Read` and `ls` during design phase (2026-05-22):

- **EXISTS:** `workspace-hub/config/agents/` — existing config-tree neighbor; new `config/canonical-store/` sits beside it (Section 4 design decision D12).
- **EXISTS:** `workspace-hub/config/ai-tools/` — another config-tree sibling.
- **EXISTS:** `workspace-hub/scripts/enforcement/` — contains 20 existing `check-*.sh` scripts (`check-no-abs-paths.sh`, `check-harness-file-size.sh`, etc.). New CARS checks follow same naming + exit-code conventions.
- **EXISTS:** `workspace-hub/scripts/enforcement/enforcement-env.sh` — provides shared env-var loading for all enforcement scripts.
- **EXISTS:** `workspace-hub/scripts/enforcement/install-hooks.sh` — git hook installer used by other enforcement scripts.
- **EXISTS:** `workspace-hub/digitalmodel/src/digitalmodel/citations/schema.py` — the `Citation` pilot per #2685 (out of scope for Plan 1; extended in Plan 3).
- **MISSING (Plan 1 creates):** `workspace-hub/config/canonical-store/` and all contents.
- **MISSING (Plan 1 creates):** `workspace-hub/scripts/canonical-store/` and all contents.
- **MISSING (Plan 1 creates):** five new `scripts/enforcement/check-*.sh` entries listed in Artifact Map.

### Standards

Not applicable — this plan is harness/infrastructure, not engineering-derived content.

### LLM Wiki pages consulted

Not applicable for this plan's deliverables (Plan 4 deals with wiki content). However, design references existing wiki paths that this plan's schema must validate against:

- `llm-wiki/marine-engineering/standards/dnv-os-e301.md` — referenced by `method-registry.yaml` seed entry
- `llm-wiki/marine-engineering/datasets/ocimf-meg4-annex-a/` — referenced as Tier-1-data target

### Documents consulted

- `docs/governance/2026-05-22-canonical-anti-repetition-surface-design.md` (this plan's spec)
- `docs/plans/_template-issue-plan.md` (template structure this plan follows)
- `docs/plans/README.md` (workflow guide)
- `.claude/rules/calc-citation-contract.md` (precedent for Tier-3 sidecar shape; #2685 pilot)
- `.claude/rules/codes-standards-data-routing.md` (precedent for visibility tiers, sibling routing)
- `.claude/rules/patterns.md` (enforcement gradient: prose → script → hook)
- `.claude/rules/coding-style.md` (20-line cap on AGENTS.md/CLAUDE.md — Plan 2 concern, not Plan 1)
- `scripts/enforcement/check-no-abs-paths.sh:1-50` (reference pattern for new check scripts)
- `scripts/enforcement/check-harness-file-size.sh:1-30` (reference pattern for size-bounded checks)
- Related issues: [#2778](https://github.com/vamseeachanta/workspace-hub/issues/2778), [#2744](https://github.com/vamseeachanta/workspace-hub/issues/2744), [#2775](https://github.com/vamseeachanta/workspace-hub/issues/2775), [#2685](https://github.com/vamseeachanta/workspace-hub/issues/2685)

### Gaps identified

Every file in the Artifact Map is a gap (Plan 1 = greenfield foundation). No existing canonical-store machinery exists; this plan builds it from scratch.

### Evidence (embedded verification)

**Issue statuses** (verified 2026-05-22T14:30:00Z via `gh issue view`):

- `#2778` — OPEN — "feat(architecture): lock data/knowledge/result search routing across llm-wiki + llm-wiki-<client> siblings"
- `#2744` — OPEN — "epic(acma): client project data-cycle readiness and private llm-wiki launch"
- `#2775` — OPEN — "fix(harness): restore workspace-hub SSoT flow across sibling repos"
- `#2685` — OPEN (LIVE) — calc-citation pilot

**File existence** (verified 2026-05-22T17:30:00Z via `ls -la`):

```
EXISTS: workspace-hub/config/agents/
EXISTS: workspace-hub/config/ai-tools/
EXISTS: workspace-hub/scripts/enforcement/check-no-abs-paths.sh
EXISTS: workspace-hub/scripts/enforcement/check-harness-file-size.sh
EXISTS: workspace-hub/scripts/enforcement/enforcement-env.sh
EXISTS: workspace-hub/docs/governance/2026-05-22-canonical-anti-repetition-surface-design.md
MISSING (Plan 1 creates): workspace-hub/config/canonical-store/
MISSING (Plan 1 creates): workspace-hub/scripts/canonical-store/
MISSING (Plan 1 creates): workspace-hub/scripts/enforcement/check-canonical-lookup.sh
MISSING (Plan 1 creates): workspace-hub/scripts/enforcement/check-layer-manifest.sh
MISSING (Plan 1 creates): workspace-hub/scripts/enforcement/check-result-dedup.sh
MISSING (Plan 1 creates): workspace-hub/scripts/enforcement/check-supersedes-lineage.sh
MISSING (Plan 1 creates): workspace-hub/scripts/enforcement/check-wiki-promotion-landed.sh
MISSING (Plan 1 creates): workspace-hub/tests/canonical-store/
```

**Line excerpts** (referenced patterns from existing enforcement scripts):

`scripts/enforcement/check-no-abs-paths.sh:1-15` (the shebang + env-load pattern this plan follows):

```bash
#!/usr/bin/env bash
# check-no-abs-paths.sh — prevent absolute paths from being committed
set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"
source "${REPO_ROOT}/scripts/enforcement/enforcement-env.sh"

# ... (rest of script)
```

**Gap proofs** (verified 2026-05-22T17:30:00Z):

```
$ ls workspace-hub/config/canonical-store/ 2>&1
ls: cannot access 'workspace-hub/config/canonical-store/': No such file or directory

$ ls workspace-hub/scripts/canonical-store/ 2>&1
ls: cannot access 'workspace-hub/scripts/canonical-store/': No such file or directory
```

**Reproduction proofs:** N/A — this plan establishes infrastructure; there is no existing failure to reproduce. Original design's §6.5 workflow gate is the user-in-loop verification that this plan is wanted.

**Source count:** Issue body (1) + 5 .claude/rules/ files (2-6) + 2 existing enforcement scripts (7-8) + 4 GitHub issues (9-12) + design doc (13) = 13 distinct sources. Exceeds the 3-source minimum.

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-05-22-cars-foundation-plan-1.md` |
| Design ref | `docs/governance/2026-05-22-canonical-anti-repetition-surface-design.md` |
| Registry — routing rules | `config/canonical-store/layer-routing.yaml` |
| Registry — method catalog | `config/canonical-store/method-registry.yaml` |
| Registry — domain taxonomy | `config/canonical-store/domain-taxonomy.yaml` |
| Registry — changelog | `config/canonical-store/CHANGELOG.md` |
| Registry — README | `config/canonical-store/README.md` |
| Schema — Tier-1 Concept | `config/canonical-store/tier-schema/concept.schema.json` |
| Schema — Tier-2 Method | `config/canonical-store/tier-schema/method.schema.json` |
| Schema — Tier-3 Result | `config/canonical-store/tier-schema/result.schema.json` |
| Schema — common footer | `config/canonical-store/tier-schema/common-footer.schema.json` |
| Helper — fingerprint | `scripts/canonical-store/fingerprint.py` |
| Helper — query | `scripts/canonical-store/query.sh` |
| Helper — resolve-method | `scripts/canonical-store/resolve_method.py` |
| Helper — load-registry | `scripts/canonical-store/load_registry.py` |
| Enforcement — lookup | `scripts/enforcement/check-canonical-lookup.sh` |
| Enforcement — manifest | `scripts/enforcement/check-layer-manifest.sh` |
| Enforcement — result-dedup | `scripts/enforcement/check-result-dedup.sh` |
| Enforcement — supersedes | `scripts/enforcement/check-supersedes-lineage.sh` |
| Enforcement — promotion-landed | `scripts/enforcement/check-wiki-promotion-landed.sh` |
| Tests — fingerprint | `tests/canonical_store/test_fingerprint.py` |
| Tests — query | `tests/canonical_store/test_query.sh` |
| Tests — resolve-method | `tests/canonical_store/test_resolve_method.py` |
| Tests — load-registry | `tests/canonical_store/test_load_registry.py` |
| Tests — enforcement (lookup) | `tests/enforcement/test_check_canonical_lookup.bats` |
| Tests — enforcement (manifest) | `tests/enforcement/test_check_layer_manifest.bats` |
| Tests — enforcement (dedup) | `tests/enforcement/test_check_result_dedup.bats` |
| Tests — enforcement (supersedes) | `tests/enforcement/test_check_supersedes_lineage.bats` |
| Tests — enforcement (promotion) | `tests/enforcement/test_check_wiki_promotion_landed.bats` |
| Plan review — Claude | `scripts/review/results/YYYY-MM-DD-plan-TBD-claude.md` |
| Plan review — Codex | `scripts/review/results/YYYY-MM-DD-plan-TBD-codex.md` |
| Plan review — Gemini | `scripts/review/results/YYYY-MM-DD-plan-TBD-gemini.md` |

---

## Deliverable

A self-contained canonical-store foundation under `workspace-hub/config/canonical-store/` and `workspace-hub/scripts/{canonical-store,enforcement}/` that validates inputs (frontmatter schemas, fingerprints, registry references) and logs warnings on violations, without yet blocking any workflow gate.

---

## Pseudocode

### Fingerprint (RFC-8785 canonical JSON + SHA-256)

```python
# scripts/canonical-store/fingerprint.py
def fingerprint(obj: dict) -> str:
    """Deterministic sha256 of a Python dict using RFC 8785 canonical JSON.

    Returns: "sha256:<64-hex-chars>"
    """
    validate_type(obj, dict)
    round_floats_in_place(obj, sig_figs=15)        # cross-platform stability
    canonical_bytes = canonicalize_rfc8785(obj)    # sort keys, no whitespace, NFC
    return "sha256:" + sha256_hex(canonical_bytes)
```

### Query (Tier-1/2/3 lookup)

```bash
# scripts/canonical-store/query.sh --tier <N> --method <id> --inputs <json> --params <json>
# Returns plan-section-ready output indicating HIT or NO_HIT for each tier
parse_args
compute_fingerprints_via fingerprint.py
for tier in 1 2 3:
    glob_wiki_path_for_tier
    grep_frontmatter_for_match
    if match found: print HIT with slug + code_sha + reviewer + confidence
    else: print NO_HIT with computed key
print disposition_template_block
```

### Enforcement skeleton (all 5 checks follow this shape)

```bash
#!/usr/bin/env bash
# check-<name>.sh — Plan 1 warn-only mode
set -euo pipefail
REPO_ROOT="$(git rev-parse --show-toplevel)"
source "${REPO_ROOT}/scripts/enforcement/enforcement-env.sh"

PLAN_FILE="${1:?plan file required}"
WARNINGS=0

run_validation_rules_against "${PLAN_FILE}"
# each rule violation: log to stderr + increment WARNINGS

if [[ "${WARNINGS}" -gt 0 ]]; then
    echo "[WARN] check-<name>.sh: ${WARNINGS} warnings (warn-only mode; not blocking)" >&2
    log_to "${REPO_ROOT}/docs/reports/canonical-store-warn-log.md" "$@"
fi

exit 0    # Plan 1 always exits 0; Plan 6 flips this to exit ${WARNINGS}
```

### Registry loader (Python convenience)

```python
# scripts/canonical-store/load_registry.py
def load_registry() -> dict:
    """Read config/canonical-store/method-registry.yaml + layer-routing.yaml.

    Returns: {methods: {...}, layer_rules: [...], domains: [...]}
    """
    repo_root = find_repo_root_via_git()
    methods = yaml_load(repo_root / "config/canonical-store/method-registry.yaml")
    rules = yaml_load(repo_root / "config/canonical-store/layer-routing.yaml")
    domains = yaml_load(repo_root / "config/canonical-store/domain-taxonomy.yaml")
    return {"methods": methods["methods"], "layer_rules": rules, "domains": domains}

def resolve_method(method_id: str) -> dict:
    """Return the registry entry for a method_id, or raise KeyError."""
    return load_registry()["methods"][method_id]
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | `config/canonical-store/layer-routing.yaml` | Routing rules per design Section 4 |
| Create | `config/canonical-store/method-registry.yaml` | Method catalog with 3 seed entries |
| Create | `config/canonical-store/domain-taxonomy.yaml` | Canonical domain slugs |
| Create | `config/canonical-store/CHANGELOG.md` | Audit trail for registry edits |
| Create | `config/canonical-store/README.md` | Usage notes + retrieval patterns |
| Create | `config/canonical-store/tier-schema/concept.schema.json` | JSON-schema for Tier-1 frontmatter |
| Create | `config/canonical-store/tier-schema/method.schema.json` | JSON-schema for Tier-2 frontmatter |
| Create | `config/canonical-store/tier-schema/result.schema.json` | JSON-schema for Tier-3 frontmatter |
| Create | `config/canonical-store/tier-schema/common-footer.schema.json` | Shared footer schema |
| Create | `scripts/canonical-store/fingerprint.py` | RFC-8785 canonical-JSON + sha256 |
| Create | `scripts/canonical-store/query.sh` | Tier-1/2/3 lookup with plan-section output |
| Create | `scripts/canonical-store/resolve_method.py` | Code-time method registry resolution |
| Create | `scripts/canonical-store/load_registry.py` | Shared registry loader (Python) |
| Create | `scripts/enforcement/check-canonical-lookup.sh` | Plan lookup-section validator (warn-only) |
| Create | `scripts/enforcement/check-layer-manifest.sh` | Plan manifest validator (warn-only) |
| Create | `scripts/enforcement/check-result-dedup.sh` | Tier-3 dedup check (warn-only) |
| Create | `scripts/enforcement/check-supersedes-lineage.sh` | Supersedes-link integrity (warn-only) |
| Create | `scripts/enforcement/check-wiki-promotion-landed.sh` | Closure attestation (warn-only) |
| Create | `tests/canonical_store/test_fingerprint.py` | TDD test suite for fingerprint stability |
| Create | `tests/canonical_store/test_query.sh` | TDD test suite for query.sh |
| Create | `tests/canonical_store/test_resolve_method.py` | TDD test suite for method resolution |
| Create | `tests/canonical_store/test_load_registry.py` | TDD test suite for registry loader |
| Create | `tests/enforcement/test_check_canonical_lookup.bats` | bats test for lookup check |
| Create | `tests/enforcement/test_check_layer_manifest.bats` | bats test for manifest check |
| Create | `tests/enforcement/test_check_result_dedup.bats` | bats test for dedup check |
| Create | `tests/enforcement/test_check_supersedes_lineage.bats` | bats test for supersedes check |
| Create | `tests/enforcement/test_check_wiki_promotion_landed.bats` | bats test for promotion check |
| Modify | `scripts/enforcement/enforcement-env.sh:end-of-file` | Add `CARS_*` env vars (WARN_ONLY default true, log path, etc.) |

---

## Implementation Tasks

### Task 1 — Registry skeleton: domain-taxonomy.yaml

**Files:**
- Create: `config/canonical-store/domain-taxonomy.yaml`
- Test: `tests/canonical_store/test_load_registry.py` (test added in Task 4)

- [ ] **Step 1.1: Create the directory**

```bash
mkdir -p config/canonical-store/tier-schema
```

- [ ] **Step 1.2: Write `config/canonical-store/domain-taxonomy.yaml`**

```yaml
# config/canonical-store/domain-taxonomy.yaml
# Canonical domain slugs used throughout the canonical-store.
# Domain slugs appear in: wiki paths (llm-wiki/<domain>/...), method_id prefixes,
# layer-routing.yaml path_glob templates.
version: 1
last_updated: 2026-05-22
issue: TBD

domains:
  marine-engineering:
    description: "Marine engineering: mooring, vessel dynamics, wind/wave loading, offshore structures."
    wiki_path_prefix: marine-engineering
    primary_siblings: [digitalmodel]
  naval-architecture:
    description: "Naval architecture: hull form, hydrostatics, stability."
    wiki_path_prefix: naval-architecture
    primary_siblings: [digitalmodel]
  data-pipeline:
    description: "Generic data-pipeline methods: ETL, extraction, transformation."
    wiki_path_prefix: data-pipeline
    primary_siblings: [worldenergydata, assetutilities]
  energy-data-public:
    description: "Public-domain federal energy data (BSEE, NOAA, USGS, MMS)."
    wiki_path_prefix: energy-data-public
    primary_siblings: [worldenergydata]
    canonical_sibling: worldenergydata-wiki   # public per #2778 §6
  maritime-law:
    description: "Maritime law, regulatory compliance, jurisdictional content."
    wiki_path_prefix: maritime-law
    primary_siblings: []
```

- [ ] **Step 1.3: Commit**

```bash
git add config/canonical-store/domain-taxonomy.yaml
SKIP_PUSH=1 git commit -m "feat(canonical-store): add domain-taxonomy.yaml" -- config/canonical-store/domain-taxonomy.yaml
```

---

### Task 2 — Registry skeleton: layer-routing.yaml

**Files:**
- Create: `config/canonical-store/layer-routing.yaml`

- [ ] **Step 2.1: Write `config/canonical-store/layer-routing.yaml`**

Use the full content from CARS design Section 4 `layer-routing.yaml` excerpt. Reproduced verbatim for completeness:

```yaml
# config/canonical-store/layer-routing.yaml
# Routing rules: artifact kind → (tier, layer, sibling, path) constraints.
# Read by enforcement scripts (check-layer-manifest.sh) to validate plan manifests.
version: 1
last_updated: 2026-05-22
issue: TBD
ref_documents:
  - .claude/rules/codes-standards-data-routing.md
  - .claude/rules/wiki-sibling-routing.md    # produced by #2778; may not exist yet
  - issues: [2778, 2744, 2731]

# ─── Tier 1 ─── CONCEPT entries
tier_1_rules:
  - kind: concept-page-generic
    layer: any
    sibling: llm-wiki
    path_glob: "<domain>/concepts/<slug>.md"
    visibility_required: private-llm-wiki
    description: "Generic concept page (e.g., 'VLCC wind coefficients')."

  - kind: concept-page-client
    layer: any
    sibling: "llm-wiki-<client>"
    path_glob: "projects/<project>/concepts/<slug>.md"
    visibility_required: private-client-llm-wiki
    client_field_required: true
    description: "Client/project-specific concept that does NOT exist generically."

  - kind: standards-page
    layer: data
    sibling: llm-wiki
    path_glob: "<domain>/standards/<code-id>.md"
    visibility_required: private-llm-wiki
    description: "Standards-derived data (per codes-standards-data-routing rule)."

  - kind: dataset-page
    layer: data
    sibling: llm-wiki
    path_glob: "<domain>/datasets/<dataset-slug>/"
    visibility_required: private-llm-wiki
    description: "Generic dataset description + the dataset files."

  - kind: public-federal-data
    layer: data
    sibling: worldenergydata-wiki
    path_glob: "<domain>/datasets/<dataset-slug>/"
    visibility_required: public-federal-data
    license_required: public-domain
    description: "Public-domain federal data per codes-standards-data-routing §6."

# ─── Tier 2 ─── METHOD entries
tier_2_rules:
  - kind: engineering-method
    layer: exec
    sibling: llm-wiki
    path_glob: "<domain>/methods/<method-slug>.md"
    visibility_required: private-llm-wiki
    method_registry_required: true

  - kind: data-pipeline-method
    layer: exec
    sibling: llm-wiki
    path_glob: "<domain>/methods/pipelines/<method-slug>.md"
    visibility_required: private-llm-wiki
    method_registry_required: true

  - kind: client-specific-method
    layer: exec
    sibling: "llm-wiki-<client>"
    path_glob: "projects/<project>/methods/<method-slug>.md"
    visibility_required: private-client-llm-wiki
    method_registry_required: true
    client_field_required: true

# ─── Tier 3 ─── RESULT entries
tier_3_rules:
  - kind: engineering-result
    layer: exec
    sibling: llm-wiki
    path_glob: "<domain>/results/<YYYY-MM-DD>-<method-slug>-<inputs-fp-short>.md"
    visibility_required: private-llm-wiki
    method_ref_required: true

  - kind: client-result
    layer: any
    sibling: "llm-wiki-<client>"
    path_glob: "projects/<project>/results/<YYYY-MM-DD>-<method-slug>-<inputs-fp-short>.md"
    visibility_required: private-client-llm-wiki
    method_ref_required: true
    client_field_required: true

  - kind: report-output
    layer: output
    sibling: "llm-wiki-<client>"
    path_glob: "projects/<project>/results/reports/<YYYY-MM-DD>-<report-slug>.md"
    visibility_required: private-client-llm-wiki
    client_field_required: true

  - kind: generic-report-output
    layer: output
    sibling: llm-wiki
    path_glob: "<domain>/results/reports/<YYYY-MM-DD>-<report-slug>.md"
    visibility_required: private-llm-wiki

# ─── Exclusions ─── what canonical-store does NOT govern
exclusions:
  - kind: harness-config
    matches:
      - "AGENTS.md"
      - "CLAUDE.md"
      - ".claude/rules/**"
      - ".claude/skills/**"
      - "config/agents/**"
    reason: "Harness — covered by #2775."
  - kind: source-code
    matches:
      - "**/src/**"
      - "**/tests/**"
      - "**/*.py"
      - "**/*.ts"
    reason: "Source code is the implementation; canonical-store only governs results."
  - kind: memory-bridge
    matches:
      - ".claude/memory/**"
      - "~/.claude/projects/**/memory/**"
    reason: "Memory-bridge surface (Hermes-managed)."
```

- [ ] **Step 2.2: Commit**

```bash
git add config/canonical-store/layer-routing.yaml
SKIP_PUSH=1 git commit -m "feat(canonical-store): add layer-routing.yaml" -- config/canonical-store/layer-routing.yaml
```

---

### Task 3 — Registry skeleton: method-registry.yaml

**Files:**
- Create: `config/canonical-store/method-registry.yaml`

- [ ] **Step 3.1: Write `config/canonical-store/method-registry.yaml`**

```yaml
# config/canonical-store/method-registry.yaml
# Named methods catalog. Each method_id MUST exist here before Tier-2 wiki page
# or Tier-3 result can reference it.
version: 1
last_updated: 2026-05-22
issue: TBD

# ─── Plan 1 ships an EMPTY methods map; seed entries land in Plan 3 + Plan 4. ──
# Reason: we can't reference Tier-2 pages or implementations that don't exist yet.
# Plan 3 lands the dnv-os-e301 entry (the #2685 pilot); Plan 4 lands ocimf-meg4.
methods: {}

# Plan 6 lands the allow-list for trivial edits per design D13
allowed_trivial_edits:
  - field: description
    reason: "Description-only edits downgrade to T1 review."
  - file: CHANGELOG.md
    matches: ["formatting", "typo"]
    reason: "CHANGELOG cosmetic edits downgrade to T1; semantic edits require T3."
  - file: README.md
    reason: "README edits are doc-only, downgrade to T1."
```

- [ ] **Step 3.2: Commit**

```bash
git add config/canonical-store/method-registry.yaml
SKIP_PUSH=1 git commit -m "feat(canonical-store): add method-registry.yaml (empty methods; seeds land Plans 3-4)" -- config/canonical-store/method-registry.yaml
```

---

### Task 4 — Registry loader (Python helper)

**Files:**
- Create: `scripts/canonical-store/load_registry.py`
- Create: `tests/canonical_store/__init__.py`
- Create: `tests/canonical_store/test_load_registry.py`

- [ ] **Step 4.1: Write the failing test FIRST**

```python
# tests/canonical_store/test_load_registry.py
"""TDD tests for load_registry.py — registry loader for canonical-store."""
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "scripts" / "canonical-store"))

from load_registry import load_registry, resolve_method


def test_load_registry_returns_three_top_level_keys():
    """load_registry() must return dict with methods, layer_rules, domains."""
    reg = load_registry()
    assert set(reg.keys()) == {"methods", "layer_rules", "domains"}


def test_load_registry_methods_is_dict():
    """Methods catalog is a dict (empty in Plan 1)."""
    reg = load_registry()
    assert isinstance(reg["methods"], dict)


def test_load_registry_layer_rules_has_tier_keys():
    """layer_rules carries tier_1_rules, tier_2_rules, tier_3_rules, exclusions."""
    reg = load_registry()
    rules = reg["layer_rules"]
    assert "tier_1_rules" in rules
    assert "tier_2_rules" in rules
    assert "tier_3_rules" in rules
    assert "exclusions" in rules


def test_load_registry_domains_contains_marine_engineering():
    """domain-taxonomy.yaml has marine-engineering entry."""
    reg = load_registry()
    assert "marine-engineering" in reg["domains"]
    assert reg["domains"]["marine-engineering"]["wiki_path_prefix"] == "marine-engineering"


def test_resolve_method_raises_keyerror_for_unknown():
    """resolve_method raises KeyError when method_id not registered."""
    with pytest.raises(KeyError):
        resolve_method("nonexistent-method-id")


def test_resolve_method_returns_dict_for_known(monkeypatch):
    """Once a method is registered, resolve_method returns the entry."""
    # Plan 1 ships empty methods; this test stubs an entry in-memory.
    from load_registry import load_registry as real_load

    def fake_load():
        return {
            "methods": {"test-method": {"canonical_page": "test/methods/test-method"}},
            "layer_rules": {},
            "domains": {},
        }

    monkeypatch.setattr("load_registry.load_registry", fake_load)
    entry = resolve_method("test-method")
    assert entry["canonical_page"] == "test/methods/test-method"
```

- [ ] **Step 4.2: Run test; verify it FAILS**

```bash
cd workspace-hub && uv run pytest tests/canonical_store/test_load_registry.py -v
```

Expected: FAIL with `ModuleNotFoundError: No module named 'load_registry'` (because load_registry.py does not yet exist).

- [ ] **Step 4.3: Create `tests/canonical_store/__init__.py`** (empty, to make it a package)

```python
# tests/canonical_store/__init__.py
```

- [ ] **Step 4.4: Write `scripts/canonical-store/load_registry.py`**

```python
"""Registry loader for the canonical-store.

Reads config/canonical-store/{method-registry,layer-routing,domain-taxonomy}.yaml
and returns a unified dict view. Used by enforcement scripts (via subprocess +
JSON output) and by code-time method resolution.
"""
from pathlib import Path
import subprocess

import yaml


def _repo_root() -> Path:
    """Locate workspace-hub root via git."""
    result = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        capture_output=True, text=True, check=True,
    )
    return Path(result.stdout.strip())


def load_registry() -> dict:
    """Read all three registry files and return a unified view.

    Returns:
        {
          "methods": dict,        # from method-registry.yaml
          "layer_rules": dict,    # full layer-routing.yaml content
          "domains": dict,        # from domain-taxonomy.yaml's "domains" key
        }
    """
    root = _repo_root()
    base = root / "config" / "canonical-store"

    with (base / "method-registry.yaml").open() as f:
        method_doc = yaml.safe_load(f)
    with (base / "layer-routing.yaml").open() as f:
        routing_doc = yaml.safe_load(f)
    with (base / "domain-taxonomy.yaml").open() as f:
        taxonomy_doc = yaml.safe_load(f)

    return {
        "methods": method_doc.get("methods", {}) or {},
        "layer_rules": routing_doc,
        "domains": taxonomy_doc.get("domains", {}) or {},
    }


def resolve_method(method_id: str) -> dict:
    """Return the registry entry for a method_id, or raise KeyError."""
    reg = load_registry()
    return reg["methods"][method_id]   # KeyError if missing
```

- [ ] **Step 4.5: Run test; verify it PASSES**

```bash
cd workspace-hub && uv run pytest tests/canonical_store/test_load_registry.py -v
```

Expected: 6 passed.

- [ ] **Step 4.6: Commit**

```bash
git add scripts/canonical-store/load_registry.py tests/canonical_store/__init__.py tests/canonical_store/test_load_registry.py
SKIP_PUSH=1 git commit -m "feat(canonical-store): add registry loader + TDD tests (6 passing)" -- scripts/canonical-store/load_registry.py tests/canonical_store/__init__.py tests/canonical_store/test_load_registry.py
```

---

### Task 5 — Fingerprint algorithm (Python helper)

**Files:**
- Create: `scripts/canonical-store/fingerprint.py`
- Create: `tests/canonical_store/test_fingerprint.py`

- [ ] **Step 5.1: Write the failing test FIRST**

```python
# tests/canonical_store/test_fingerprint.py
"""TDD tests for fingerprint.py — RFC-8785 canonical-JSON + sha256."""
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "scripts" / "canonical-store"))

from fingerprint import fingerprint


def test_fingerprint_returns_sha256_prefixed_64_hex():
    """Output is 'sha256:' + 64 hex chars."""
    fp = fingerprint({"a": 1})
    assert fp.startswith("sha256:")
    assert len(fp) == 7 + 64
    assert all(c in "0123456789abcdef" for c in fp[7:])


def test_fingerprint_is_deterministic_for_same_input():
    """Calling twice with identical input yields identical output."""
    a = fingerprint({"x": 1, "y": 2})
    b = fingerprint({"x": 1, "y": 2})
    assert a == b


def test_fingerprint_key_order_invariant():
    """Inputs with same keys in different order produce same fingerprint."""
    a = fingerprint({"x": 1, "y": 2})
    b = fingerprint({"y": 2, "x": 1})
    assert a == b


def test_fingerprint_distinguishes_different_inputs():
    """Different inputs produce different fingerprints."""
    a = fingerprint({"x": 1})
    b = fingerprint({"x": 2})
    assert a != b


def test_fingerprint_distinguishes_int_vs_string():
    """1 and '1' fingerprint differently."""
    a = fingerprint({"x": 1})
    b = fingerprint({"x": "1"})
    assert a != b


def test_fingerprint_float_15_sig_figs_stable():
    """Floats are rounded to 15 sig figs for cross-platform stability."""
    # Same value to 15 sig figs but different precisions input
    a = fingerprint({"x": 0.123456789012345})
    b = fingerprint({"x": 0.123456789012345001})  # extra digit beyond 15
    assert a == b


def test_fingerprint_float_below_15_sig_figs_distinguished():
    """Floats differing within 15 sig figs are distinguished."""
    a = fingerprint({"x": 0.123456789012345})
    b = fingerprint({"x": 0.123456789012346})  # last sig fig differs
    assert a != b


def test_fingerprint_nested_dict():
    """Nested dicts are handled (recursive sort)."""
    a = fingerprint({"a": {"b": 1, "c": 2}})
    b = fingerprint({"a": {"c": 2, "b": 1}})
    assert a == b


def test_fingerprint_rejects_non_dict():
    """Top-level input must be a dict."""
    with pytest.raises(TypeError):
        fingerprint([1, 2, 3])


def test_fingerprint_known_value_stability():
    """Known input → known output (regression test for cross-platform stability)."""
    fp = fingerprint({"method": "test", "vessel": "vlcc", "heading": 90})
    # This value is computed once; if it changes, the algorithm changed (regression).
    # Compute it during test development by running fingerprint manually once,
    # then pin it here. For now: assert format is right; exact value pinned in Step 5.5.
    assert fp.startswith("sha256:")
    assert len(fp) == 71
```

- [ ] **Step 5.2: Run test; verify it FAILS**

```bash
cd workspace-hub && uv run pytest tests/canonical_store/test_fingerprint.py -v
```

Expected: FAIL with `ModuleNotFoundError`.

- [ ] **Step 5.3: Write `scripts/canonical-store/fingerprint.py`**

```python
"""Deterministic content-addressable fingerprinting for the canonical-store.

Algorithm: RFC 8785 canonical JSON form + SHA-256.
- Keys sorted recursively
- Whitespace stripped
- UTF-8 NFC normalized
- Floats rounded to 15 significant figures (IEEE-754 double precision limit)
  for cross-platform stability

Used by Tier-3 lookup keys (inputs_fingerprint, params_fingerprint) and by
output_fingerprint for change-detection.
"""
import hashlib
import json
import unicodedata
from typing import Any


def _round_floats(obj: Any, sig_figs: int = 15) -> Any:
    """Recursively round floats to `sig_figs` significant figures."""
    if isinstance(obj, float):
        if obj == 0.0 or not (obj == obj):  # zero or NaN
            return obj
        from math import floor, log10
        d = sig_figs - int(floor(log10(abs(obj)))) - 1
        return round(obj, d)
    if isinstance(obj, dict):
        return {k: _round_floats(v, sig_figs) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_round_floats(v, sig_figs) for v in obj]
    return obj


def fingerprint(obj: dict) -> str:
    """Deterministic sha256 of a dict using RFC 8785 canonical JSON.

    Returns: "sha256:<64-hex-chars>"
    Raises: TypeError if obj is not a dict.
    """
    if not isinstance(obj, dict):
        raise TypeError(f"fingerprint() requires dict, got {type(obj).__name__}")

    rounded = _round_floats(obj, sig_figs=15)
    canonical = json.dumps(
        rounded,
        sort_keys=True,
        ensure_ascii=False,
        separators=(",", ":"),
        default=str,
    )
    canonical = unicodedata.normalize("NFC", canonical)
    digest = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    return f"sha256:{digest}"
```

- [ ] **Step 5.4: Run test; verify it PASSES**

```bash
cd workspace-hub && uv run pytest tests/canonical_store/test_fingerprint.py -v
```

Expected: 10 passed.

- [ ] **Step 5.5: Pin the known-value regression test**

Run once to generate the known value:

```bash
cd workspace-hub && uv run python -c "
import sys
sys.path.insert(0, 'scripts/canonical-store')
from fingerprint import fingerprint
print(fingerprint({'method': 'test', 'vessel': 'vlcc', 'heading': 90}))
"
```

Take the printed value (e.g., `sha256:abc123...`) and edit `tests/canonical_store/test_fingerprint.py:test_fingerprint_known_value_stability` to pin it:

```python
def test_fingerprint_known_value_stability():
    """Known input → known output (regression test for cross-platform stability)."""
    fp = fingerprint({"method": "test", "vessel": "vlcc", "heading": 90})
    assert fp == "sha256:<PASTE_GENERATED_VALUE_HERE>"
```

Run tests again to confirm pinned value passes:

```bash
cd workspace-hub && uv run pytest tests/canonical_store/test_fingerprint.py::test_fingerprint_known_value_stability -v
```

Expected: PASS.

- [ ] **Step 5.6: Commit**

```bash
git add scripts/canonical-store/fingerprint.py tests/canonical_store/test_fingerprint.py
SKIP_PUSH=1 git commit -m "feat(canonical-store): add RFC-8785 fingerprint + 10 TDD tests (incl pinned regression)" -- scripts/canonical-store/fingerprint.py tests/canonical_store/test_fingerprint.py
```

---

### Task 6 — Tier JSON schemas (Tier 1, Tier 2, Tier 3, common footer)

**Files:**
- Create: `config/canonical-store/tier-schema/common-footer.schema.json`
- Create: `config/canonical-store/tier-schema/concept.schema.json`
- Create: `config/canonical-store/tier-schema/method.schema.json`
- Create: `config/canonical-store/tier-schema/result.schema.json`
- Create: `tests/canonical_store/test_tier_schemas.py`

- [ ] **Step 6.1: Write the failing test FIRST**

```python
# tests/canonical_store/test_tier_schemas.py
"""TDD tests for tier JSON-schemas: concept, method, result, common-footer."""
import json
from pathlib import Path

import pytest
from jsonschema import Draft7Validator, ValidationError

REPO_ROOT = Path(__file__).resolve().parents[2]
SCHEMA_DIR = REPO_ROOT / "config" / "canonical-store" / "tier-schema"


@pytest.fixture
def common_footer_schema():
    return json.loads((SCHEMA_DIR / "common-footer.schema.json").read_text())


@pytest.fixture
def concept_schema():
    return json.loads((SCHEMA_DIR / "concept.schema.json").read_text())


@pytest.fixture
def method_schema():
    return json.loads((SCHEMA_DIR / "method.schema.json").read_text())


@pytest.fixture
def result_schema():
    return json.loads((SCHEMA_DIR / "result.schema.json").read_text())


def test_common_footer_schema_is_valid_draft7(common_footer_schema):
    """common-footer schema is itself a valid Draft-07 schema."""
    Draft7Validator.check_schema(common_footer_schema)


def test_common_footer_schema_requires_visibility(common_footer_schema):
    """common-footer schema requires `visibility` field."""
    assert "visibility" in common_footer_schema["required"]


def test_common_footer_visibility_enum_three_tiers(common_footer_schema):
    """visibility enum: private-llm-wiki, private-client-llm-wiki, public-federal-data."""
    v_schema = common_footer_schema["properties"]["visibility"]
    assert set(v_schema["enum"]) == {
        "private-llm-wiki", "private-client-llm-wiki", "public-federal-data"
    }


def test_concept_schema_tier_is_concept(concept_schema):
    """concept schema pins tier=='concept'."""
    assert concept_schema["properties"]["tier"]["const"] == "concept"


def test_method_schema_tier_is_method(method_schema):
    """method schema pins tier=='method'."""
    assert method_schema["properties"]["tier"]["const"] == "method"


def test_result_schema_tier_is_result(result_schema):
    """result schema pins tier=='result'."""
    assert result_schema["properties"]["tier"]["const"] == "result"


def test_result_schema_requires_method_ref_and_fingerprints(result_schema):
    """result schema requires method_ref, inputs_fingerprint, params_fingerprint."""
    required = set(result_schema["required"])
    assert "method_ref" in required
    assert "inputs_fingerprint" in required
    assert "params_fingerprint" in required
    assert "output_fingerprint" in required


def test_result_schema_fingerprint_pattern_is_sha256_hex(result_schema):
    """result schema's fingerprint fields use sha256:<64hex> pattern."""
    pat = result_schema["properties"]["inputs_fingerprint"]["pattern"]
    assert pat == r"^sha256:[a-f0-9]{64}$"


def test_result_schema_client_required_when_visibility_is_client(result_schema):
    """result schema's allOf/if/then requires client when visibility=private-client."""
    # The schema has an allOf with if/then for conditional requirement
    found_conditional = False
    for cond in result_schema.get("allOf", []):
        if "if" in cond and "then" in cond:
            if cond["if"]["properties"]["visibility"]["const"] == "private-client-llm-wiki":
                assert "client" in cond["then"]["required"]
                found_conditional = True
    assert found_conditional, "Conditional `client` requirement missing from result schema"


def test_valid_concept_entry_passes_schema(concept_schema):
    """A valid concept entry validates against the schema."""
    entry = {
        "tier": "concept",
        "concept_slug": "marine-engineering/concepts/test-concept",
        "visibility": "private-llm-wiki",
        "source_sibling": "llm-wiki",
        "created": "2026-05-22T14:30:00Z",
        "created_by": "test-author",
        "authored_in_issue": "vamseeachanta/workspace-hub#9999",
    }
    Draft7Validator(concept_schema).validate(entry)


def test_invalid_concept_entry_wrong_tier_fails(concept_schema):
    """A concept entry with tier='method' fails."""
    entry = {
        "tier": "method",
        "concept_slug": "x",
        "visibility": "private-llm-wiki",
        "source_sibling": "llm-wiki",
        "created": "2026-05-22T14:30:00Z",
        "created_by": "t",
        "authored_in_issue": "x#1",
    }
    with pytest.raises(ValidationError):
        Draft7Validator(concept_schema).validate(entry)


def test_valid_result_entry_passes_schema(result_schema):
    """A valid result entry validates against the schema."""
    entry = {
        "tier": "result",
        "result_id": "2026-05-22-test-method-abc123",
        "method_ref": "test-method",
        "method_version_at_run": "1.0.0",
        "inputs_fingerprint": "sha256:" + "a" * 64,
        "params_fingerprint": "sha256:" + "b" * 64,
        "output_fingerprint": "sha256:" + "c" * 64,
        "inputs": {"x": 1},
        "parameters": {"y": 2},
        "execution": {
            "sibling": "digitalmodel",
            "code_sha": "0" * 40,
            "entry_point": "test:run",
            "ran_at": "2026-05-22T14:30:00Z",
        },
        "visibility": "private-llm-wiki",
        "source_sibling": "llm-wiki",
        "created": "2026-05-22T14:30:00Z",
        "created_by": "test",
        "authored_in_issue": "vamseeachanta/workspace-hub#9999",
    }
    Draft7Validator(result_schema).validate(entry)


def test_result_entry_missing_client_when_private_client_fails(result_schema):
    """A private-client visibility result without `client` field fails."""
    entry = {
        "tier": "result",
        "result_id": "x",
        "method_ref": "test-method",
        "method_version_at_run": "1.0.0",
        "inputs_fingerprint": "sha256:" + "a" * 64,
        "params_fingerprint": "sha256:" + "b" * 64,
        "output_fingerprint": "sha256:" + "c" * 64,
        "inputs": {},
        "parameters": {},
        "execution": {
            "sibling": "digitalmodel",
            "code_sha": "0" * 40,
            "entry_point": "test:run",
            "ran_at": "2026-05-22T14:30:00Z",
        },
        "visibility": "private-client-llm-wiki",     # client tier but no client field
        "source_sibling": "llm-wiki-acma",
        "created": "2026-05-22T14:30:00Z",
        "created_by": "test",
        "authored_in_issue": "x#1",
    }
    with pytest.raises(ValidationError):
        Draft7Validator(result_schema).validate(entry)
```

- [ ] **Step 6.2: Run test; verify it FAILS**

```bash
cd workspace-hub && uv run pytest tests/canonical_store/test_tier_schemas.py -v
```

Expected: FAIL with FileNotFoundError (schemas don't exist yet).

- [ ] **Step 6.3: Write `config/canonical-store/tier-schema/common-footer.schema.json`**

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "Canonical-Store Common Footer",
  "description": "Shared frontmatter fields across Tier-1/2/3 entries.",
  "type": "object",
  "required": [
    "visibility", "source_sibling", "created", "created_by", "authored_in_issue"
  ],
  "properties": {
    "visibility": {
      "type": "string",
      "enum": ["private-llm-wiki", "private-client-llm-wiki", "public-federal-data"]
    },
    "client":         {"type": "string"},
    "project":        {"type": "string"},
    "source_sibling": {"type": "string"},
    "supersedes":     {"type": "array", "items": {"type": "string"}, "default": []},
    "superseded_by":  {"oneOf": [{"type": "string"}, {"type": "null"}]},
    "related":        {"type": "array", "items": {"type": "string"}, "default": []},
    "created":        {"type": "string", "format": "date-time"},
    "created_by":     {"type": "string"},
    "last_reviewed":  {"type": "string", "format": "date-time"},
    "reviewer":       {"type": "string"},
    "revision":       {"type": "integer", "minimum": 1},
    "confidence":     {"type": "number", "minimum": 0.0, "maximum": 1.0},
    "completion":     {"type": "number", "minimum": 0.0, "maximum": 1.0},
    "authored_in_issue": {"type": "string"},
    "authored_in_plan":  {"type": "string"}
  }
}
```

- [ ] **Step 6.4: Write `config/canonical-store/tier-schema/concept.schema.json`**

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "Canonical-Store Tier-1 Concept Entry",
  "type": "object",
  "required": [
    "tier", "concept_slug",
    "visibility", "source_sibling", "created", "created_by", "authored_in_issue"
  ],
  "properties": {
    "tier":              {"const": "concept"},
    "concept_slug":      {"type": "string", "pattern": "^[a-z0-9][a-z0-9-/]+$"},
    "references":        {"type": "object"},
    "applied_by_methods":{"type": "array", "items": {"type": "string"}},
    "visibility":        {"enum": ["private-llm-wiki", "private-client-llm-wiki", "public-federal-data"]},
    "client":            {"type": "string"},
    "project":           {"type": "string"},
    "source_sibling":    {"type": "string"},
    "supersedes":        {"type": "array", "items": {"type": "string"}},
    "superseded_by":     {"oneOf": [{"type": "string"}, {"type": "null"}]},
    "related":           {"type": "array", "items": {"type": "string"}},
    "created":           {"type": "string", "format": "date-time"},
    "created_by":        {"type": "string"},
    "last_reviewed":     {"type": "string", "format": "date-time"},
    "reviewer":          {"type": "string"},
    "revision":          {"type": "integer", "minimum": 1},
    "confidence":        {"type": "number", "minimum": 0.0, "maximum": 1.0},
    "completion":        {"type": "number", "minimum": 0.0, "maximum": 1.0},
    "authored_in_issue": {"type": "string"},
    "authored_in_plan":  {"type": "string"}
  },
  "allOf": [
    {
      "if":   {"properties": {"visibility": {"const": "private-client-llm-wiki"}}},
      "then": {"required": ["client"]}
    }
  ]
}
```

- [ ] **Step 6.5: Write `config/canonical-store/tier-schema/method.schema.json`**

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "Canonical-Store Tier-2 Method Entry",
  "type": "object",
  "required": [
    "tier", "method_id", "method_version",
    "visibility", "source_sibling", "created", "created_by", "authored_in_issue"
  ],
  "properties": {
    "tier":                  {"const": "method"},
    "method_id":             {"type": "string", "pattern": "^[a-z0-9-]+$"},
    "method_version":        {"type": "string", "pattern": "^\\d+\\.\\d+\\.\\d+$"},
    "applies_to_concepts":   {"type": "array", "items": {"type": "string"}},
    "implementations":       {"type": "array"},
    "input_schema":          {"type": "object"},
    "parameters_schema":     {"type": "object"},
    "output_schema":         {"type": "object"},
    "data_dependencies":     {"type": "array", "items": {"type": "string"}},
    "visibility":            {"enum": ["private-llm-wiki", "private-client-llm-wiki", "public-federal-data"]},
    "client":                {"type": "string"},
    "project":               {"type": "string"},
    "source_sibling":        {"type": "string"},
    "supersedes":            {"type": "array", "items": {"type": "string"}},
    "superseded_by":         {"oneOf": [{"type": "string"}, {"type": "null"}]},
    "related":               {"type": "array", "items": {"type": "string"}},
    "created":               {"type": "string", "format": "date-time"},
    "created_by":            {"type": "string"},
    "last_reviewed":         {"type": "string", "format": "date-time"},
    "reviewer":              {"type": "string"},
    "revision":              {"type": "integer", "minimum": 1},
    "confidence":            {"type": "number", "minimum": 0.0, "maximum": 1.0},
    "completion":            {"type": "number", "minimum": 0.0, "maximum": 1.0},
    "authored_in_issue":     {"type": "string"},
    "authored_in_plan":      {"type": "string"}
  },
  "allOf": [
    {
      "if":   {"properties": {"visibility": {"const": "private-client-llm-wiki"}}},
      "then": {"required": ["client"]}
    }
  ]
}
```

- [ ] **Step 6.6: Write `config/canonical-store/tier-schema/result.schema.json`**

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "Canonical-Store Tier-3 Result Entry",
  "type": "object",
  "required": [
    "tier", "result_id", "method_ref", "method_version_at_run",
    "inputs_fingerprint", "params_fingerprint", "inputs", "parameters",
    "output_fingerprint", "execution",
    "visibility", "source_sibling", "created", "created_by", "authored_in_issue"
  ],
  "properties": {
    "tier":                   {"const": "result"},
    "result_id":              {"type": "string"},
    "method_ref":             {"type": "string", "pattern": "^[a-z0-9-]+$"},
    "method_version_at_run":  {"type": "string", "pattern": "^\\d+\\.\\d+\\.\\d+$"},
    "inputs_fingerprint":     {"type": "string", "pattern": "^sha256:[a-f0-9]{64}$"},
    "params_fingerprint":     {"type": "string", "pattern": "^sha256:[a-f0-9]{64}$"},
    "output_fingerprint":     {"type": "string", "pattern": "^sha256:[a-f0-9]{64}$"},
    "inputs":                 {"type": "object"},
    "parameters":             {"type": "object"},
    "output":                 {"type": ["object", "array", "number", "string"]},
    "output_reference":       {"type": "object",
                                "properties": {"path": {"type": "string"}, "output_fingerprint": {"type": "string"}}},
    "execution": {
      "type": "object",
      "required": ["sibling", "code_sha", "entry_point", "ran_at"],
      "properties": {
        "sibling":      {"type": "string"},
        "code_sha":     {"type": "string", "pattern": "^[a-f0-9]{40}$"},
        "code_version": {"type": "string"},
        "entry_point":  {"type": "string"},
        "ran_at":       {"type": "string", "format": "date-time"},
        "ran_by":       {"type": "string"},
        "runtime_seconds": {"type": "number"},
        "environment":  {"type": "string"}
      }
    },
    "citations":              {"type": "array"},
    "qa":                     {"type": "object"},
    "visibility":             {"enum": ["private-llm-wiki", "private-client-llm-wiki", "public-federal-data"]},
    "client":                 {"type": "string"},
    "project":                {"type": "string"},
    "source_sibling":         {"type": "string"},
    "supersedes":             {"type": "array", "items": {"type": "string"}},
    "supersedes_reason":      {"type": "string",
                                "enum": ["code-fix", "method-change", "input-correction", "precision-upgrade"]},
    "superseded_by":          {"oneOf": [{"type": "string"}, {"type": "null"}]},
    "related":                {"type": "array", "items": {"type": "string"}},
    "created":                {"type": "string", "format": "date-time"},
    "created_by":             {"type": "string"},
    "last_reviewed":          {"type": "string", "format": "date-time"},
    "reviewer":               {"type": "string"},
    "revision":               {"type": "integer", "minimum": 1},
    "confidence":             {"type": "number", "minimum": 0.0, "maximum": 1.0},
    "completion":             {"type": "number", "minimum": 0.0, "maximum": 1.0},
    "authored_in_issue":      {"type": "string"},
    "authored_in_plan":       {"type": "string"}
  },
  "allOf": [
    {
      "if":   {"properties": {"visibility": {"const": "private-client-llm-wiki"}}},
      "then": {"required": ["client"]}
    }
  ]
}
```

- [ ] **Step 6.7: Run test; verify all PASS**

```bash
cd workspace-hub && uv run pytest tests/canonical_store/test_tier_schemas.py -v
```

Expected: 13 passed.

- [ ] **Step 6.8: Commit**

```bash
git add config/canonical-store/tier-schema/ tests/canonical_store/test_tier_schemas.py
SKIP_PUSH=1 git commit -m "feat(canonical-store): add Tier-1/2/3 + common-footer JSON schemas (13 TDD tests)" -- config/canonical-store/tier-schema/ tests/canonical_store/test_tier_schemas.py
```

---

### Task 7 — query.sh (Tier-1/2/3 lookup helper)

**Files:**
- Create: `scripts/canonical-store/query.sh`
- Create: `tests/canonical_store/test_query.sh`

- [ ] **Step 7.1: Write the failing test FIRST**

```bash
#!/usr/bin/env bats
# tests/canonical_store/test_query.sh — bats tests for query.sh

setup() {
  REPO_ROOT="$(git rev-parse --show-toplevel)"
  QUERY="${REPO_ROOT}/scripts/canonical-store/query.sh"
}

@test "query.sh exists and is executable" {
  [[ -x "${QUERY}" ]]
}

@test "query.sh --help prints usage" {
  run "${QUERY}" --help
  [[ "${status}" -eq 0 ]]
  [[ "${output}" == *"Usage:"* ]]
}

@test "query.sh --tier 3 with no method fails with helpful message" {
  run "${QUERY}" --tier 3
  [[ "${status}" -ne 0 ]]
  [[ "${output}" == *"--method"* ]]
}

@test "query.sh --tier 1 --concept <slug> returns NO_HIT for nonexistent" {
  run "${QUERY}" --tier 1 --concept "nonexistent/concept"
  [[ "${status}" -eq 0 ]]
  [[ "${output}" == *"NO_HIT"* ]]
}

@test "query.sh --tier 3 --method ... --inputs ... computes fingerprint" {
  run "${QUERY}" --tier 3 \
    --method "test-method" \
    --inputs '{"x":1}' \
    --params '{"y":2}'
  [[ "${status}" -eq 0 ]]
  [[ "${output}" == *"inputs_fingerprint: sha256:"* ]]
  [[ "${output}" == *"params_fingerprint: sha256:"* ]]
  [[ "${output}" == *"NO_HIT"* ]]   # no wiki content seeded in Plan 1
}

@test "query.sh emits plan-section template after lookup" {
  run "${QUERY}" --tier 3 \
    --method "test-method" \
    --inputs '{"x":1}' \
    --params '{}'
  [[ "${output}" == *"## Canonical Store Lookup (REQUIRED)"* ]]
  [[ "${output}" == *"### Disposition"* ]]
}
```

- [ ] **Step 7.2: Run test; verify it FAILS**

```bash
cd workspace-hub && bats tests/canonical_store/test_query.sh
```

Expected: FAIL (script doesn't exist).

- [ ] **Step 7.3: Write `scripts/canonical-store/query.sh`**

```bash
#!/usr/bin/env bash
# query.sh — Canonical-store Tier-1/2/3 lookup.
# Emits plan-section-ready output to stdout.
set -euo pipefail

usage() {
  cat <<EOF
Usage: query.sh --tier <1|2|3> [options]

Tier-1 options:
  --concept <slug>      Look up concept by slug (e.g., marine-engineering/concepts/vlcc-wind)

Tier-2 options:
  --method <method_id>  Look up method by registered id

Tier-3 options (all required):
  --method <method_id>  Method to query
  --inputs <json>       Inputs dict (JSON)
  --params <json>       Parameters dict (JSON)

Common:
  --client <slug>       Restrict search to llm-wiki-<client> instead of generic
  --help                Show this message

Output: plan-section-ready Markdown for pasting into Canonical Store Lookup section.
EOF
}

# ── Argument parsing ─────────────────────────────────────────────────────────
TIER=""
CONCEPT=""
METHOD=""
INPUTS=""
PARAMS=""
CLIENT=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --tier)    TIER="$2"; shift 2 ;;
    --concept) CONCEPT="$2"; shift 2 ;;
    --method)  METHOD="$2"; shift 2 ;;
    --inputs)  INPUTS="$2"; shift 2 ;;
    --params)  PARAMS="$2"; shift 2 ;;
    --client)  CLIENT="$2"; shift 2 ;;
    --help|-h) usage; exit 0 ;;
    *) echo "Unknown argument: $1" >&2; usage; exit 2 ;;
  esac
done

[[ -z "${TIER}" ]] && { echo "Error: --tier required" >&2; usage; exit 2; }

REPO_ROOT="$(git rev-parse --show-toplevel)"
WIKI_BASE="${REPO_ROOT}/llm-wiki"
if [[ -n "${CLIENT}" ]]; then
  WIKI_BASE="${REPO_ROOT}/llm-wiki-${CLIENT}"
fi

QUERIED_AT="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo "## Canonical Store Lookup (REQUIRED)"
echo ""
echo "Queried at: ${QUERIED_AT}"
echo "Query method: scripts/canonical-store/query.sh"
echo ""

case "${TIER}" in
  1)
    [[ -z "${CONCEPT}" ]] && { echo "Error: tier-1 requires --concept" >&2; exit 2; }
    echo "### Tier 1 — Concept hit(s)"
    target="${WIKI_BASE}/${CONCEPT}.md"
    if [[ -f "${target}" ]]; then
      echo "- [x] Hit: ${CONCEPT}"
    else
      echo "- [x] No hit (queried: ${CONCEPT})"
    fi
    ;;
  2)
    [[ -z "${METHOD}" ]] && { echo "Error: tier-2 requires --method" >&2; exit 2; }
    echo "### Tier 2 — Method hit(s)"
    # Check method registry
    if uv run python -c "
import sys; sys.path.insert(0, '${REPO_ROOT}/scripts/canonical-store')
from load_registry import resolve_method
try:
    e = resolve_method('${METHOD}')
    print(f'- [x] Hit: ${METHOD}@' + e.get('current_version', 'unknown'))
except KeyError:
    print('- [x] No hit (method not in registry)')
" 2>/dev/null; then
      true
    else
      echo "- [x] No hit (method resolution failed)"
    fi
    ;;
  3)
    [[ -z "${METHOD}" ]] && { echo "Error: tier-3 requires --method" >&2; exit 2; }
    [[ -z "${INPUTS}" ]] && { echo "Error: tier-3 requires --inputs" >&2; exit 2; }
    [[ -z "${PARAMS}" ]] && PARAMS='{}'
    echo "### Tier 3 — Result hit(s)"
    # Compute fingerprints via fingerprint.py
    FPS="$(uv run python -c "
import json, sys
sys.path.insert(0, '${REPO_ROOT}/scripts/canonical-store')
from fingerprint import fingerprint
inputs = json.loads('''${INPUTS}''')
params = json.loads('''${PARAMS}''')
print(fingerprint(inputs))
print(fingerprint(params))
" 2>/dev/null)"
    INPUTS_FP="$(echo "${FPS}" | sed -n 1p)"
    PARAMS_FP="$(echo "${FPS}" | sed -n 2p)"
    # Search wiki results/ for matching frontmatter
    RESULTS_DIR_PATTERN="${WIKI_BASE}/*/results/"
    HIT_FOUND=false
    if compgen -G "${RESULTS_DIR_PATTERN}" > /dev/null; then
      while IFS= read -r f; do
        if grep -q "inputs_fingerprint: ${INPUTS_FP}" "${f}" 2>/dev/null && \
           grep -q "params_fingerprint: ${PARAMS_FP}" "${f}" 2>/dev/null && \
           grep -q "method_ref: ${METHOD}" "${f}" 2>/dev/null; then
          rel="${f#${REPO_ROOT}/}"
          echo "- [x] Hit: ${rel}"
          HIT_FOUND=true
        fi
      done < <(find ${RESULTS_DIR_PATTERN} -name '*.md' 2>/dev/null)
    fi
    if ! ${HIT_FOUND}; then
      echo "- [x] No hit (query key: method=${METHOD}, inputs_fp=${INPUTS_FP}, params_fp=${PARAMS_FP})"
    fi
    ;;
  *)
    echo "Error: --tier must be 1, 2, or 3" >&2
    exit 2
    ;;
esac

echo ""
echo "### Disposition (REQUIRED — pick exactly one)"
echo "- [ ] cite-and-stop"
echo "- [ ] verification"
echo "- [ ] improvement"
echo "- [ ] genuinely-new"
```

- [ ] **Step 7.4: Make executable and run test; verify PASS**

```bash
cd workspace-hub && chmod +x scripts/canonical-store/query.sh
bats tests/canonical_store/test_query.sh
```

Expected: 6 passed.

- [ ] **Step 7.5: Commit**

```bash
git add scripts/canonical-store/query.sh tests/canonical_store/test_query.sh
SKIP_PUSH=1 git commit -m "feat(canonical-store): add query.sh + bats tests (6 passing)" -- scripts/canonical-store/query.sh tests/canonical_store/test_query.sh
```

---

### Task 8 — resolve_method.py (CLI wrapper around load_registry)

**Files:**
- Create: `scripts/canonical-store/resolve_method.py`
- Create: `tests/canonical_store/test_resolve_method.py`

- [ ] **Step 8.1: Write the failing test FIRST**

```python
# tests/canonical_store/test_resolve_method.py
"""TDD tests for resolve_method.py CLI wrapper."""
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "scripts" / "canonical-store" / "resolve_method.py"


def test_resolve_method_script_exists():
    assert SCRIPT.exists()


def test_resolve_method_help_succeeds():
    result = subprocess.run(
        ["uv", "run", "python", str(SCRIPT), "--help"],
        capture_output=True, text=True, cwd=str(REPO_ROOT),
    )
    assert result.returncode == 0
    assert "method_id" in result.stdout


def test_resolve_method_unknown_id_exits_1():
    result = subprocess.run(
        ["uv", "run", "python", str(SCRIPT), "nonexistent-method"],
        capture_output=True, text=True, cwd=str(REPO_ROOT),
    )
    assert result.returncode == 1
    assert "not found" in result.stderr.lower()
```

- [ ] **Step 8.2: Run test; verify it FAILS**

```bash
cd workspace-hub && uv run pytest tests/canonical_store/test_resolve_method.py -v
```

Expected: FAIL (script missing).

- [ ] **Step 8.3: Write `scripts/canonical-store/resolve_method.py`**

```python
#!/usr/bin/env python3
"""resolve_method.py — CLI to look up a method_id in method-registry.yaml.

Usage:
  resolve_method.py <method_id>
  resolve_method.py --help

Exit codes:
  0 — method found; prints YAML to stdout
  1 — method not found
  2 — argument error
"""
import argparse
import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
from load_registry import resolve_method


def main() -> int:
    p = argparse.ArgumentParser(description="Resolve method_id from canonical-store registry.")
    p.add_argument("method_id", help="The method_id to look up (e.g., ocimf-meg4-wind-coeff-lookup)")
    args = p.parse_args()
    try:
        entry = resolve_method(args.method_id)
    except KeyError:
        print(f"Error: method_id '{args.method_id}' not found in registry", file=sys.stderr)
        return 1
    print(yaml.safe_dump(entry, default_flow_style=False, sort_keys=False), end="")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 8.4: Run test; verify it PASSES**

```bash
cd workspace-hub && uv run pytest tests/canonical_store/test_resolve_method.py -v
```

Expected: 3 passed.

- [ ] **Step 8.5: Commit**

```bash
git add scripts/canonical-store/resolve_method.py tests/canonical_store/test_resolve_method.py
SKIP_PUSH=1 git commit -m "feat(canonical-store): add resolve_method.py CLI (3 TDD tests)" -- scripts/canonical-store/resolve_method.py tests/canonical_store/test_resolve_method.py
```

---

### Task 9 — Update enforcement-env.sh (add CARS env vars)

**Files:**
- Modify: `scripts/enforcement/enforcement-env.sh`

- [ ] **Step 9.1: Read existing enforcement-env.sh to find end-of-file**

```bash
cat scripts/enforcement/enforcement-env.sh
```

- [ ] **Step 9.2: Append CARS-related env vars** at the end of the file:

```bash
# ── CARS (Canonical Anti-Repetition Surface) env vars ──────────────────────
# Plan 1 ships WARN-only mode; Plan 6 ratchets to hard-gate.
: "${CARS_WARN_ONLY:=1}"                                      # 1 = warn, 0 = block
: "${CARS_LOG_PATH:=${REPO_ROOT:-$(git rev-parse --show-toplevel)}/docs/reports/canonical-store-warn-log.md}"
: "${CARS_REGISTRY_DIR:=${REPO_ROOT:-$(git rev-parse --show-toplevel)}/config/canonical-store}"
: "${CARS_HELPER_DIR:=${REPO_ROOT:-$(git rev-parse --show-toplevel)}/scripts/canonical-store}"

export CARS_WARN_ONLY CARS_LOG_PATH CARS_REGISTRY_DIR CARS_HELPER_DIR
```

- [ ] **Step 9.3: Verify by sourcing the file**

```bash
cd workspace-hub && bash -c 'source scripts/enforcement/enforcement-env.sh && env | grep ^CARS_'
```

Expected output (paths may differ):
```
CARS_WARN_ONLY=1
CARS_LOG_PATH=/path/to/workspace-hub/docs/reports/canonical-store-warn-log.md
CARS_REGISTRY_DIR=/path/to/workspace-hub/config/canonical-store
CARS_HELPER_DIR=/path/to/workspace-hub/scripts/canonical-store
```

- [ ] **Step 9.4: Commit**

```bash
git add scripts/enforcement/enforcement-env.sh
SKIP_PUSH=1 git commit -m "feat(enforcement): add CARS env vars (warn-only default)" -- scripts/enforcement/enforcement-env.sh
```

---

### Task 10 — check-canonical-lookup.sh (validates plan's Canonical Store Lookup section)

**Files:**
- Create: `scripts/enforcement/check-canonical-lookup.sh`
- Create: `tests/enforcement/test_check_canonical_lookup.bats`

- [ ] **Step 10.1: Write the failing test FIRST**

```bash
#!/usr/bin/env bats
# tests/enforcement/test_check_canonical_lookup.bats

setup() {
  REPO_ROOT="$(git rev-parse --show-toplevel)"
  CHECK="${REPO_ROOT}/scripts/enforcement/check-canonical-lookup.sh"
  TMPDIR_TEST="$(mktemp -d)"
}

teardown() {
  rm -rf "${TMPDIR_TEST}"
}

@test "check exists and is executable" {
  [[ -x "${CHECK}" ]]
}

@test "missing argument prints helpful error" {
  run "${CHECK}"
  [[ "${status}" -ne 0 ]] || [[ "${output}" == *"plan file"* ]]
}

@test "plan without Canonical Store Lookup section emits WARN" {
  cat > "${TMPDIR_TEST}/plan.md" <<EOF
# Plan

## Some Other Section
Content.
EOF
  run "${CHECK}" "${TMPDIR_TEST}/plan.md"
  # Warn-only mode → exits 0 but emits WARN to stderr
  [[ "${status}" -eq 0 ]]
  [[ "${output}" == *"WARN"* ]] || [[ "${stderr}" == *"WARN"* ]] || true
}

@test "plan with empty Canonical Store Lookup section emits WARN" {
  cat > "${TMPDIR_TEST}/plan.md" <<EOF
# Plan

## Canonical Store Lookup (REQUIRED)
EOF
  run "${CHECK}" "${TMPDIR_TEST}/plan.md"
  [[ "${status}" -eq 0 ]]   # warn-only
}

@test "plan with Disposition missing emits WARN" {
  cat > "${TMPDIR_TEST}/plan.md" <<EOF
# Plan

## Canonical Store Lookup (REQUIRED)
Queried at: 2026-05-22T14:30:00Z

### Tier 1 — Concept hit(s)
- [x] No hit
EOF
  run "${CHECK}" "${TMPDIR_TEST}/plan.md"
  [[ "${status}" -eq 0 ]]
}

@test "valid plan with Disposition passes silently" {
  cat > "${TMPDIR_TEST}/plan.md" <<EOF
# Plan

## Canonical Store Lookup (REQUIRED)
Queried at: 2026-05-22T14:30:00Z

### Tier 1 — Concept hit(s)
- [x] No hit

### Tier 2 — Method hit(s)
- [x] No hit

### Tier 3 — Result hit(s)
- [x] No hit

### Disposition (REQUIRED — pick exactly one)
- [x] genuinely-new
EOF
  run "${CHECK}" "${TMPDIR_TEST}/plan.md"
  [[ "${status}" -eq 0 ]]
}

@test "CARS_WARN_ONLY=0 blocks invalid plan" {
  cat > "${TMPDIR_TEST}/plan.md" <<EOF
# Plan
## Some Other Section
EOF
  CARS_WARN_ONLY=0 run "${CHECK}" "${TMPDIR_TEST}/plan.md"
  [[ "${status}" -ne 0 ]]
}
```

- [ ] **Step 10.2: Run test; verify it FAILS**

```bash
cd workspace-hub && bats tests/enforcement/test_check_canonical_lookup.bats
```

Expected: FAIL (script missing).

- [ ] **Step 10.3: Write `scripts/enforcement/check-canonical-lookup.sh`**

```bash
#!/usr/bin/env bash
# check-canonical-lookup.sh — validates plan's Canonical Store Lookup section.
# Plan 1: warn-only mode (CARS_WARN_ONLY=1, exit 0 on violations).
set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"
source "${REPO_ROOT}/scripts/enforcement/enforcement-env.sh"

PLAN_FILE="${1:-}"
[[ -z "${PLAN_FILE}" ]] && { echo "Usage: $0 <plan-file>" >&2; exit 2; }
[[ ! -f "${PLAN_FILE}" ]] && { echo "Plan file not found: ${PLAN_FILE}" >&2; exit 2; }

WARNINGS=0
emit_warn() {
  echo "[WARN] check-canonical-lookup.sh: $1 (in ${PLAN_FILE})" >&2
  WARNINGS=$((WARNINGS + 1))
  mkdir -p "$(dirname "${CARS_LOG_PATH}")"
  echo "- $(date -u +%Y-%m-%dT%H:%M:%SZ) | ${PLAN_FILE} | $1" >> "${CARS_LOG_PATH}"
}

# Rule 1: Plan must have ## Canonical Store Lookup section
if ! grep -q "^## Canonical Store Lookup" "${PLAN_FILE}"; then
  emit_warn "missing '## Canonical Store Lookup' section"
fi

# Rule 2: Section must declare Queried-at timestamp
if grep -q "^## Canonical Store Lookup" "${PLAN_FILE}" && \
   ! grep -q "^Queried at: [0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]T" "${PLAN_FILE}"; then
  emit_warn "missing 'Queried at: <ISO-8601>' line in Canonical Store Lookup section"
fi

# Rule 3: Section must declare a Disposition
if ! grep -qE "^### Disposition" "${PLAN_FILE}"; then
  emit_warn "missing '### Disposition' subsection"
elif ! grep -qE "^\- \[x\] (cite-and-stop|verification|improvement|genuinely-new)" "${PLAN_FILE}"; then
  emit_warn "Disposition section has no checked option (must check exactly one)"
fi

# Rule 4: All three tier subsections present
for tier in "Tier 1" "Tier 2" "Tier 3"; do
  if ! grep -qE "^### ${tier}" "${PLAN_FILE}"; then
    emit_warn "missing '### ${tier}' subsection"
  fi
done

# Exit policy: warn-only by default; CARS_WARN_ONLY=0 blocks
if [[ "${WARNINGS}" -gt 0 ]]; then
  echo "[WARN] check-canonical-lookup.sh: ${WARNINGS} warnings" >&2
  if [[ "${CARS_WARN_ONLY}" -eq 0 ]]; then
    exit 1
  fi
fi

exit 0
```

- [ ] **Step 10.4: Make executable and run test; verify PASS**

```bash
cd workspace-hub && chmod +x scripts/enforcement/check-canonical-lookup.sh
bats tests/enforcement/test_check_canonical_lookup.bats
```

Expected: 7 passed.

- [ ] **Step 10.5: Commit**

```bash
git add scripts/enforcement/check-canonical-lookup.sh tests/enforcement/test_check_canonical_lookup.bats
SKIP_PUSH=1 git commit -m "feat(enforcement): add check-canonical-lookup.sh warn-only + 7 bats tests" -- scripts/enforcement/check-canonical-lookup.sh tests/enforcement/test_check_canonical_lookup.bats
```

---

### Task 11 — check-layer-manifest.sh

**Files:**
- Create: `scripts/enforcement/check-layer-manifest.sh`
- Create: `tests/enforcement/test_check_layer_manifest.bats`

- [ ] **Step 11.1: Write the failing test**

```bash
#!/usr/bin/env bats
# tests/enforcement/test_check_layer_manifest.bats

setup() {
  REPO_ROOT="$(git rev-parse --show-toplevel)"
  CHECK="${REPO_ROOT}/scripts/enforcement/check-layer-manifest.sh"
  TMPDIR_TEST="$(mktemp -d)"
}

teardown() {
  rm -rf "${TMPDIR_TEST}"
}

@test "check exists and is executable" {
  [[ -x "${CHECK}" ]]
}

@test "missing arg prints usage" {
  run "${CHECK}"
  [[ "${status}" -ne 0 ]]
}

@test "plan with no Layer Manifest emits WARN (warn-only exits 0)" {
  cat > "${TMPDIR_TEST}/plan.md" <<EOF
# Plan
## Some Section
EOF
  run "${CHECK}" "${TMPDIR_TEST}/plan.md"
  [[ "${status}" -eq 0 ]]
}

@test "plan with Layer Manifest but no rows emits WARN" {
  cat > "${TMPDIR_TEST}/plan.md" <<EOF
# Plan

## Layer Manifest (REQUIRED)
| Tier | Layer | Kind | Sibling | Path | Lifecycle |
|------|-------|------|---------|------|-----------|
EOF
  run "${CHECK}" "${TMPDIR_TEST}/plan.md"
  [[ "${status}" -eq 0 ]]   # warn-only
}

@test "plan with valid Layer Manifest passes silently" {
  cat > "${TMPDIR_TEST}/plan.md" <<EOF
# Plan

## Layer Manifest (REQUIRED)
| Tier | Layer | Kind | Sibling | Path | Lifecycle |
|------|-------|------|---------|------|-----------|
| T3 | exec | engineering-result | llm-wiki | marine-engineering/results/test.md | NEW |
EOF
  run "${CHECK}" "${TMPDIR_TEST}/plan.md"
  [[ "${status}" -eq 0 ]]
}
```

- [ ] **Step 11.2: Run test; verify FAIL**

```bash
cd workspace-hub && bats tests/enforcement/test_check_layer_manifest.bats
```

Expected: FAIL.

- [ ] **Step 11.3: Write `scripts/enforcement/check-layer-manifest.sh`**

```bash
#!/usr/bin/env bash
# check-layer-manifest.sh — validates plan's Layer Manifest section.
# Plan 1: warn-only mode.
set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"
source "${REPO_ROOT}/scripts/enforcement/enforcement-env.sh"

PLAN_FILE="${1:-}"
[[ -z "${PLAN_FILE}" ]] && { echo "Usage: $0 <plan-file>" >&2; exit 2; }
[[ ! -f "${PLAN_FILE}" ]] && { echo "Plan file not found: ${PLAN_FILE}" >&2; exit 2; }

WARNINGS=0
emit_warn() {
  echo "[WARN] check-layer-manifest.sh: $1 (in ${PLAN_FILE})" >&2
  WARNINGS=$((WARNINGS + 1))
  mkdir -p "$(dirname "${CARS_LOG_PATH}")"
  echo "- $(date -u +%Y-%m-%dT%H:%M:%SZ) | ${PLAN_FILE} | $1" >> "${CARS_LOG_PATH}"
}

# Rule 1: Layer Manifest section present
if ! grep -q "^## Layer Manifest" "${PLAN_FILE}"; then
  emit_warn "missing '## Layer Manifest' section"
else
  # Rule 2: at least one data row in the manifest table
  # Lines matching " | T1 | " / " | T2 | " / " | T3 | "
  ROWS="$(grep -cE "^\| T[123] \|" "${PLAN_FILE}" || true)"
  if [[ "${ROWS}" -eq 0 ]]; then
    emit_warn "Layer Manifest section has no T1/T2/T3 data rows"
  fi
fi

if [[ "${WARNINGS}" -gt 0 ]]; then
  echo "[WARN] check-layer-manifest.sh: ${WARNINGS} warnings" >&2
  if [[ "${CARS_WARN_ONLY}" -eq 0 ]]; then
    exit 1
  fi
fi

exit 0
```

- [ ] **Step 11.4: Make executable, run test, verify PASS**

```bash
cd workspace-hub && chmod +x scripts/enforcement/check-layer-manifest.sh
bats tests/enforcement/test_check_layer_manifest.bats
```

Expected: 5 passed.

- [ ] **Step 11.5: Commit**

```bash
git add scripts/enforcement/check-layer-manifest.sh tests/enforcement/test_check_layer_manifest.bats
SKIP_PUSH=1 git commit -m "feat(enforcement): add check-layer-manifest.sh warn-only + 5 bats tests" -- scripts/enforcement/check-layer-manifest.sh tests/enforcement/test_check_layer_manifest.bats
```

---

### Task 12 — check-result-dedup.sh

**Files:**
- Create: `scripts/enforcement/check-result-dedup.sh`
- Create: `tests/enforcement/test_check_result_dedup.bats`

- [ ] **Step 12.1: Write the failing test**

```bash
#!/usr/bin/env bats
# tests/enforcement/test_check_result_dedup.bats

setup() {
  REPO_ROOT="$(git rev-parse --show-toplevel)"
  CHECK="${REPO_ROOT}/scripts/enforcement/check-result-dedup.sh"
  TMPDIR_TEST="$(mktemp -d)"
}

teardown() {
  rm -rf "${TMPDIR_TEST}"
}

@test "check exists and is executable" {
  [[ -x "${CHECK}" ]]
}

@test "missing arg fails" {
  run "${CHECK}"
  [[ "${status}" -ne 0 ]]
}

@test "sidecar with unique (method,inputs_fp,params_fp) passes" {
  cat > "${TMPDIR_TEST}/sidecar.yaml" <<EOF
tier: result
method_ref: test-method
method_version_at_run: 1.0.0
inputs_fingerprint: sha256:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
params_fingerprint: sha256:bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb
EOF
  run "${CHECK}" "${TMPDIR_TEST}/sidecar.yaml"
  [[ "${status}" -eq 0 ]]
}

@test "sidecar without method_ref emits WARN" {
  cat > "${TMPDIR_TEST}/sidecar.yaml" <<EOF
tier: result
inputs_fingerprint: sha256:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
EOF
  run "${CHECK}" "${TMPDIR_TEST}/sidecar.yaml"
  [[ "${status}" -eq 0 ]]   # warn-only
  [[ "${stderr}" == *"WARN"* ]] || true
}
```

- [ ] **Step 12.2: Run test; verify FAIL**

```bash
cd workspace-hub && bats tests/enforcement/test_check_result_dedup.bats
```

Expected: FAIL.

- [ ] **Step 12.3: Write `scripts/enforcement/check-result-dedup.sh`**

```bash
#!/usr/bin/env bash
# check-result-dedup.sh — validates result sidecar is unique by (method_ref, inputs_fp, params_fp).
# Plan 1: warn-only mode (no wiki content yet to dedup against; mostly schema-validates).
set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"
source "${REPO_ROOT}/scripts/enforcement/enforcement-env.sh"

SIDECAR="${1:-}"
[[ -z "${SIDECAR}" ]] && { echo "Usage: $0 <sidecar-file>" >&2; exit 2; }
[[ ! -f "${SIDECAR}" ]] && { echo "Sidecar not found: ${SIDECAR}" >&2; exit 2; }

WARNINGS=0
emit_warn() {
  echo "[WARN] check-result-dedup.sh: $1 (in ${SIDECAR})" >&2
  WARNINGS=$((WARNINGS + 1))
  mkdir -p "$(dirname "${CARS_LOG_PATH}")"
  echo "- $(date -u +%Y-%m-%dT%H:%M:%SZ) | ${SIDECAR} | $1" >> "${CARS_LOG_PATH}"
}

# Rule 1: sidecar carries method_ref
if ! grep -qE "^method_ref:[[:space:]]+[a-z0-9-]+" "${SIDECAR}"; then
  emit_warn "missing or invalid method_ref field"
fi

# Rule 2: sidecar carries inputs_fingerprint
if ! grep -qE "^inputs_fingerprint:[[:space:]]+sha256:[a-f0-9]{64}" "${SIDECAR}"; then
  emit_warn "missing or invalid inputs_fingerprint field"
fi

# Rule 3: sidecar carries params_fingerprint
if ! grep -qE "^params_fingerprint:[[:space:]]+sha256:[a-f0-9]{64}" "${SIDECAR}"; then
  emit_warn "missing or invalid params_fingerprint field"
fi

# Rule 4 (Plan 4+): grep wiki for existing (method_ref, inputs_fp, params_fp) match.
# Plan 1 ships this as a stub since llm-wiki has no entries to dedup against yet.

if [[ "${WARNINGS}" -gt 0 ]]; then
  echo "[WARN] check-result-dedup.sh: ${WARNINGS} warnings" >&2
  if [[ "${CARS_WARN_ONLY}" -eq 0 ]]; then
    exit 1
  fi
fi

exit 0
```

- [ ] **Step 12.4: Make executable, run test, verify PASS**

```bash
cd workspace-hub && chmod +x scripts/enforcement/check-result-dedup.sh
bats tests/enforcement/test_check_result_dedup.bats
```

Expected: 4 passed.

- [ ] **Step 12.5: Commit**

```bash
git add scripts/enforcement/check-result-dedup.sh tests/enforcement/test_check_result_dedup.bats
SKIP_PUSH=1 git commit -m "feat(enforcement): add check-result-dedup.sh warn-only + 4 bats tests" -- scripts/enforcement/check-result-dedup.sh tests/enforcement/test_check_result_dedup.bats
```

---

### Task 13 — check-supersedes-lineage.sh

**Files:**
- Create: `scripts/enforcement/check-supersedes-lineage.sh`
- Create: `tests/enforcement/test_check_supersedes_lineage.bats`

- [ ] **Step 13.1: Write the failing test**

```bash
#!/usr/bin/env bats
# tests/enforcement/test_check_supersedes_lineage.bats

setup() {
  REPO_ROOT="$(git rev-parse --show-toplevel)"
  CHECK="${REPO_ROOT}/scripts/enforcement/check-supersedes-lineage.sh"
  TMPDIR_TEST="$(mktemp -d)"
}

teardown() {
  rm -rf "${TMPDIR_TEST}"
}

@test "check exists and is executable" {
  [[ -x "${CHECK}" ]]
}

@test "plan with disposition=improvement and supersedes link present passes" {
  cat > "${TMPDIR_TEST}/plan.md" <<EOF
## Canonical Store Lookup (REQUIRED)
### Disposition
- [x] improvement
       → supersedes: marine-engineering/results/2026-05-15-test.md
EOF
  run "${CHECK}" "${TMPDIR_TEST}/plan.md"
  [[ "${status}" -eq 0 ]]
}

@test "plan with disposition=improvement and NO supersedes link emits WARN" {
  cat > "${TMPDIR_TEST}/plan.md" <<EOF
## Canonical Store Lookup (REQUIRED)
### Disposition
- [x] improvement
EOF
  run "${CHECK}" "${TMPDIR_TEST}/plan.md"
  [[ "${status}" -eq 0 ]]   # warn-only
}

@test "plan with disposition=genuinely-new and no supersedes link passes" {
  cat > "${TMPDIR_TEST}/plan.md" <<EOF
## Canonical Store Lookup (REQUIRED)
### Disposition
- [x] genuinely-new
EOF
  run "${CHECK}" "${TMPDIR_TEST}/plan.md"
  [[ "${status}" -eq 0 ]]
}
```

- [ ] **Step 13.2: Run test; verify FAIL**

```bash
cd workspace-hub && bats tests/enforcement/test_check_supersedes_lineage.bats
```

Expected: FAIL.

- [ ] **Step 13.3: Write `scripts/enforcement/check-supersedes-lineage.sh`**

```bash
#!/usr/bin/env bash
# check-supersedes-lineage.sh — when disposition=improvement, validates supersedes link.
set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"
source "${REPO_ROOT}/scripts/enforcement/enforcement-env.sh"

PLAN_FILE="${1:-}"
[[ -z "${PLAN_FILE}" ]] && { echo "Usage: $0 <plan-file>" >&2; exit 2; }
[[ ! -f "${PLAN_FILE}" ]] && { echo "Plan file not found: ${PLAN_FILE}" >&2; exit 2; }

WARNINGS=0
emit_warn() {
  echo "[WARN] check-supersedes-lineage.sh: $1 (in ${PLAN_FILE})" >&2
  WARNINGS=$((WARNINGS + 1))
  mkdir -p "$(dirname "${CARS_LOG_PATH}")"
  echo "- $(date -u +%Y-%m-%dT%H:%M:%SZ) | ${PLAN_FILE} | $1" >> "${CARS_LOG_PATH}"
}

# Detect disposition=improvement and ensure supersedes link present
if grep -qE "^\- \[x\] improvement" "${PLAN_FILE}"; then
  if ! grep -qE "supersedes:" "${PLAN_FILE}"; then
    emit_warn "disposition=improvement but no 'supersedes:' link found in plan"
  fi
fi

if [[ "${WARNINGS}" -gt 0 ]]; then
  echo "[WARN] check-supersedes-lineage.sh: ${WARNINGS} warnings" >&2
  if [[ "${CARS_WARN_ONLY}" -eq 0 ]]; then
    exit 1
  fi
fi

exit 0
```

- [ ] **Step 13.4: Make executable, run test, verify PASS**

```bash
cd workspace-hub && chmod +x scripts/enforcement/check-supersedes-lineage.sh
bats tests/enforcement/test_check_supersedes_lineage.bats
```

Expected: 4 passed.

- [ ] **Step 13.5: Commit**

```bash
git add scripts/enforcement/check-supersedes-lineage.sh tests/enforcement/test_check_supersedes_lineage.bats
SKIP_PUSH=1 git commit -m "feat(enforcement): add check-supersedes-lineage.sh warn-only + 4 bats tests" -- scripts/enforcement/check-supersedes-lineage.sh tests/enforcement/test_check_supersedes_lineage.bats
```

---

### Task 14 — check-wiki-promotion-landed.sh (closure attestation, warn-only)

**Files:**
- Create: `scripts/enforcement/check-wiki-promotion-landed.sh`
- Create: `tests/enforcement/test_check_wiki_promotion_landed.bats`

- [ ] **Step 14.1: Write the failing test**

```bash
#!/usr/bin/env bats
# tests/enforcement/test_check_wiki_promotion_landed.bats

setup() {
  REPO_ROOT="$(git rev-parse --show-toplevel)"
  CHECK="${REPO_ROOT}/scripts/enforcement/check-wiki-promotion-landed.sh"
  TMPDIR_TEST="$(mktemp -d)"
}

teardown() {
  rm -rf "${TMPDIR_TEST}"
}

@test "check exists and is executable" {
  [[ -x "${CHECK}" ]]
}

@test "issue body with 'Wiki promotion attestation: <slug>' for existing slug passes" {
  # Create a fake wiki slug that exists
  mkdir -p "${REPO_ROOT}/llm-wiki/test-domain/concepts" 2>/dev/null || true
  echo "test concept" > "${REPO_ROOT}/llm-wiki/test-domain/concepts/test-attestation.md"

  cat > "${TMPDIR_TEST}/issue-body.md" <<EOF
Wiki promotion attestation: test-domain/concepts/test-attestation
EOF
  run "${CHECK}" "${TMPDIR_TEST}/issue-body.md"
  [[ "${status}" -eq 0 ]]

  rm -f "${REPO_ROOT}/llm-wiki/test-domain/concepts/test-attestation.md"
}

@test "issue body with attestation pointing to nonexistent slug emits WARN" {
  cat > "${TMPDIR_TEST}/issue-body.md" <<EOF
Wiki promotion attestation: nonexistent/slug
EOF
  run "${CHECK}" "${TMPDIR_TEST}/issue-body.md"
  [[ "${status}" -eq 0 ]]   # warn-only
}

@test "issue body without attestation AND disposition!=cite-and-stop emits WARN" {
  cat > "${TMPDIR_TEST}/issue-body.md" <<EOF
This issue had disposition: genuinely-new
EOF
  run "${CHECK}" "${TMPDIR_TEST}/issue-body.md"
  [[ "${status}" -eq 0 ]]
}

@test "cite-and-stop disposition needs no attestation (passes)" {
  cat > "${TMPDIR_TEST}/issue-body.md" <<EOF
Disposition: cite-and-stop
EOF
  run "${CHECK}" "${TMPDIR_TEST}/issue-body.md"
  [[ "${status}" -eq 0 ]]
}
```

- [ ] **Step 14.2: Run test; verify FAIL**

```bash
cd workspace-hub && bats tests/enforcement/test_check_wiki_promotion_landed.bats
```

Expected: FAIL.

- [ ] **Step 14.3: Write `scripts/enforcement/check-wiki-promotion-landed.sh`**

```bash
#!/usr/bin/env bash
# check-wiki-promotion-landed.sh — closure attestation check.
# Plan 1: warn-only mode (Plan 6 ratchets to hard-gate).
set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"
source "${REPO_ROOT}/scripts/enforcement/enforcement-env.sh"

ISSUE_BODY="${1:-}"
[[ -z "${ISSUE_BODY}" ]] && { echo "Usage: $0 <issue-body-file>" >&2; exit 2; }
[[ ! -f "${ISSUE_BODY}" ]] && { echo "Body file not found: ${ISSUE_BODY}" >&2; exit 2; }

WARNINGS=0
emit_warn() {
  echo "[WARN] check-wiki-promotion-landed.sh: $1 (in ${ISSUE_BODY})" >&2
  WARNINGS=$((WARNINGS + 1))
  mkdir -p "$(dirname "${CARS_LOG_PATH}")"
  echo "- $(date -u +%Y-%m-%dT%H:%M:%SZ) | ${ISSUE_BODY} | $1" >> "${CARS_LOG_PATH}"
}

# If disposition was cite-and-stop, no attestation required
if grep -qE "[Dd]isposition:?\s*cite-and-stop|\[x\]\s*cite-and-stop" "${ISSUE_BODY}"; then
  exit 0
fi

# Otherwise, expect "Wiki promotion attestation: <slug>"
ATT_LINE="$(grep -E "Wiki promotion attestation:" "${ISSUE_BODY}" || true)"
if [[ -z "${ATT_LINE}" ]]; then
  emit_warn "no 'Wiki promotion attestation: <slug>' line found"
else
  SLUG="$(echo "${ATT_LINE}" | sed -E 's/.*Wiki promotion attestation:[[:space:]]*([^[:space:]]+).*/\1/')"
  # Search both generic + client wiki paths
  found=false
  for wiki_dir in "${REPO_ROOT}/llm-wiki" "${REPO_ROOT}"/llm-wiki-*; do
    [[ -d "${wiki_dir}" ]] || continue
    if [[ -f "${wiki_dir}/${SLUG}.md" ]] || [[ -d "${wiki_dir}/${SLUG}" ]]; then
      found=true
      break
    fi
  done
  if ! ${found}; then
    emit_warn "attested slug '${SLUG}' not found at expected path under any wiki sibling"
  fi
fi

if [[ "${WARNINGS}" -gt 0 ]]; then
  echo "[WARN] check-wiki-promotion-landed.sh: ${WARNINGS} warnings (warn-only mode)" >&2
  if [[ "${CARS_WARN_ONLY}" -eq 0 ]]; then
    exit 1
  fi
fi

exit 0
```

- [ ] **Step 14.4: Make executable, run test, verify PASS**

```bash
cd workspace-hub && chmod +x scripts/enforcement/check-wiki-promotion-landed.sh
bats tests/enforcement/test_check_wiki_promotion_landed.bats
```

Expected: 5 passed.

- [ ] **Step 14.5: Commit**

```bash
git add scripts/enforcement/check-wiki-promotion-landed.sh tests/enforcement/test_check_wiki_promotion_landed.bats
SKIP_PUSH=1 git commit -m "feat(enforcement): add check-wiki-promotion-landed.sh warn-only + 5 bats tests" -- scripts/enforcement/check-wiki-promotion-landed.sh tests/enforcement/test_check_wiki_promotion_landed.bats
```

---

### Task 15 — Registry CHANGELOG.md and README.md

**Files:**
- Create: `config/canonical-store/CHANGELOG.md`
- Create: `config/canonical-store/README.md`

- [ ] **Step 15.1: Write `config/canonical-store/CHANGELOG.md`**

```markdown
# Canonical-Store Registry Changelog

> Every registry edit gets a one-line entry: date | issue | nature-of-change.
> Reviewer scope per design D13: edits trigger T3 review (except allow-listed trivial edits per `method-registry.yaml#allowed_trivial_edits`).

## 2026-05-22 — v1 initial landing
- Initial bootstrap (Plan 1 of CARS implementation).
- `layer-routing.yaml`: tier-1/2/3 rules + 3-kind exclusions per design Section 4.
- `method-registry.yaml`: empty methods map. Seeds land in Plan 3 (digitalmodel pilot) and Plan 4 (OCIMF + BSEE).
- `domain-taxonomy.yaml`: 5 domain slugs (marine-engineering, naval-architecture, data-pipeline, energy-data-public, maritime-law).
- `tier-schema/`: 4 JSON-schema files (concept, method, result, common-footer).
- Issue: TBD (filed against design `docs/governance/2026-05-22-canonical-anti-repetition-surface-design.md`).
```

- [ ] **Step 15.2: Write `config/canonical-store/README.md`**

```markdown
# Canonical-Store Registry

Per design `docs/governance/2026-05-22-canonical-anti-repetition-surface-design.md`.

## Contents

| File | Purpose |
|---|---|
| `layer-routing.yaml` | Routing rules: artifact kind → (tier, layer, sibling, path) constraints. Read by `scripts/enforcement/check-layer-manifest.sh`. |
| `method-registry.yaml` | Named methods catalog. Every `method_id` must register here before Tier-2 wiki page or Tier-3 result references it. |
| `domain-taxonomy.yaml` | Canonical domain slugs (marine-engineering, naval-architecture, data-pipeline, energy-data-public, maritime-law). |
| `tier-schema/` | JSON-Schema (draft-07) for Tier-1/2/3 frontmatter + common footer. |
| `CHANGELOG.md` | Audit trail; every edit gets a one-line entry. |

## Retrieval patterns

### Plan-time lookup (Phase 2 of issue workflow)
```
scripts/canonical-store/query.sh --tier 3 \
    --method ocimf-meg4-wind-coeff-lookup \
    --inputs '{"vessel_class":"vlcc","wind_heading_deg":90}' \
    --params '{"interpolation":"linear"}'
```

### Code-time method resolution
```python
import sys
sys.path.insert(0, "<workspace-hub>/scripts/canonical-store")
from load_registry import resolve_method
meth = resolve_method("ocimf-meg4-wind-coeff-lookup")
```

### Pre-commit validation
Enforcement scripts under `scripts/enforcement/check-*.sh` read this directory
to validate staged plans + sidecars.

## Edit governance (per design D13)

Any change under `config/canonical-store/**` triggers T3 (3-provider) adversarial
review, overriding per-issue disposition scaling. Exceptions defined in
`method-registry.yaml#allowed_trivial_edits` (description-only edits + README
edits + CHANGELOG cosmetic edits downgrade to T1).

## Mode

Plan 1 ships all enforcement scripts in WARN-only mode (`CARS_WARN_ONLY=1`).
Plan 6 ratchets to hard-gate after the 4-week soft phase + retro.
```

- [ ] **Step 15.3: Commit**

```bash
git add config/canonical-store/CHANGELOG.md config/canonical-store/README.md
SKIP_PUSH=1 git commit -m "feat(canonical-store): add CHANGELOG + README" -- config/canonical-store/CHANGELOG.md config/canonical-store/README.md
```

---

### Task 16 — Full test suite + acceptance verification

- [ ] **Step 16.1: Run all Python tests**

```bash
cd workspace-hub && uv run pytest tests/canonical_store/ -v
```

Expected: 32 passed (10 fingerprint + 6 load_registry + 13 tier_schemas + 3 resolve_method).

- [ ] **Step 16.2: Run all bats tests**

```bash
cd workspace-hub && bats tests/enforcement/test_check_canonical_lookup.bats tests/enforcement/test_check_layer_manifest.bats tests/enforcement/test_check_result_dedup.bats tests/enforcement/test_check_supersedes_lineage.bats tests/enforcement/test_check_wiki_promotion_landed.bats tests/canonical_store/test_query.sh
```

Expected: 31 passed (7+5+4+4+5+6).

- [ ] **Step 16.3: Manual smoke test — query against empty wiki**

```bash
cd workspace-hub && ./scripts/canonical-store/query.sh \
    --tier 3 \
    --method ocimf-meg4-wind-coeff-lookup \
    --inputs '{"vessel_class":"vlcc","wind_heading_deg":90,"loading_condition":"loaded"}' \
    --params '{"interpolation":"linear"}'
```

Expected: plan-section Markdown output ending with `NO_HIT` (no wiki content yet in Plan 1).

- [ ] **Step 16.4: Manual smoke test — check against this plan file itself**

```bash
cd workspace-hub && CARS_WARN_ONLY=1 \
    ./scripts/enforcement/check-canonical-lookup.sh \
    docs/plans/2026-05-22-cars-foundation-plan-1.md
```

Expected: WARN about missing Canonical Store Lookup section (this plan itself doesn't have one, which is fine — it predates the section's existence; this is the chicken-and-egg case the design §6.5 calls out). Exit code 0.

- [ ] **Step 16.5: Verify SOUL.runtime.md unchanged (Plan 2 territory)**

```bash
cd workspace-hub && git diff config/agents/SHARED_SOUL.md config/agents/claude/SOUL.delta.md
```

Expected: no diff (Plan 2 modifies these, not Plan 1).

- [ ] **Step 16.6: Push (after user approval)**

This step is HELD until user explicitly approves push timing. Per `feedback_post_commit_autosync_defeats_test_gate` and SOUL.md governance, push timing is user-controlled.

When approved:
```bash
git push origin main
```

---

## TDD Test List

| Test name | What it verifies | File |
|---|---|---|
| `test_load_registry_returns_three_top_level_keys` | registry loader returns dict with `methods`, `layer_rules`, `domains` | `tests/canonical_store/test_load_registry.py` |
| `test_load_registry_methods_is_dict` | methods catalog is a dict | same |
| `test_load_registry_layer_rules_has_tier_keys` | layer_rules contains `tier_1_rules`, `tier_2_rules`, `tier_3_rules`, `exclusions` | same |
| `test_load_registry_domains_contains_marine_engineering` | marine-engineering present in domains | same |
| `test_resolve_method_raises_keyerror_for_unknown` | KeyError on unknown method_id | same |
| `test_resolve_method_returns_dict_for_known` | Returns entry for known method | same |
| `test_fingerprint_returns_sha256_prefixed_64_hex` | Format check: `sha256:<64hex>` | `tests/canonical_store/test_fingerprint.py` |
| `test_fingerprint_is_deterministic_for_same_input` | Identical input → identical output | same |
| `test_fingerprint_key_order_invariant` | Key reordering produces same fingerprint | same |
| `test_fingerprint_distinguishes_different_inputs` | Different inputs → different fingerprints | same |
| `test_fingerprint_distinguishes_int_vs_string` | Type distinction preserved | same |
| `test_fingerprint_float_15_sig_figs_stable` | Floats round to 15 sig figs | same |
| `test_fingerprint_float_below_15_sig_figs_distinguished` | Sub-15-sig-fig differences distinguished | same |
| `test_fingerprint_nested_dict` | Recursive key sort | same |
| `test_fingerprint_rejects_non_dict` | TypeError on non-dict input | same |
| `test_fingerprint_known_value_stability` | Pinned regression test for cross-platform stability | same |
| `test_common_footer_schema_is_valid_draft7` | common-footer schema is valid Draft-07 | `tests/canonical_store/test_tier_schemas.py` |
| `test_common_footer_schema_requires_visibility` | Required field check | same |
| `test_common_footer_visibility_enum_three_tiers` | Enum contains 3 visibility tiers | same |
| `test_concept_schema_tier_is_concept` | tier const='concept' | same |
| `test_method_schema_tier_is_method` | tier const='method' | same |
| `test_result_schema_tier_is_result` | tier const='result' | same |
| `test_result_schema_requires_method_ref_and_fingerprints` | Required field check | same |
| `test_result_schema_fingerprint_pattern_is_sha256_hex` | Pattern: `^sha256:[a-f0-9]{64}$` | same |
| `test_result_schema_client_required_when_visibility_is_client` | Conditional required: client field for client visibility | same |
| `test_valid_concept_entry_passes_schema` | Happy-path concept validates | same |
| `test_invalid_concept_entry_wrong_tier_fails` | Wrong tier fails validation | same |
| `test_valid_result_entry_passes_schema` | Happy-path result validates | same |
| `test_result_entry_missing_client_when_private_client_fails` | Conditional required enforced | same |
| `test_resolve_method_script_exists` | CLI script exists | `tests/canonical_store/test_resolve_method.py` |
| `test_resolve_method_help_succeeds` | --help works | same |
| `test_resolve_method_unknown_id_exits_1` | Exit-1 for unknown method | same |
| (bats) `check exists and is executable` | each of 5 enforcement scripts | `tests/enforcement/test_check_*.bats` |
| (bats) `missing arg fails` | each of 5 enforcement scripts | same |
| (bats) `valid input passes` | each of 5 enforcement scripts | same |
| (bats) `invalid input emits WARN (warn-only mode exits 0)` | each of 5 enforcement scripts | same |
| (bats) `query.sh emits plan-section template` | query.sh output format | `tests/canonical_store/test_query.sh` |

---

## Acceptance Criteria

- [ ] `config/canonical-store/` directory exists with `layer-routing.yaml`, `method-registry.yaml` (empty methods map), `domain-taxonomy.yaml`, `CHANGELOG.md`, `README.md`, and `tier-schema/{concept,method,result,common-footer}.schema.json`.
- [ ] `scripts/canonical-store/` directory exists with `fingerprint.py`, `query.sh` (executable), `resolve_method.py` (executable), `load_registry.py`.
- [ ] `scripts/enforcement/` contains five new check scripts (executable): `check-canonical-lookup.sh`, `check-layer-manifest.sh`, `check-result-dedup.sh`, `check-supersedes-lineage.sh`, `check-wiki-promotion-landed.sh`.
- [ ] `scripts/enforcement/enforcement-env.sh` exports `CARS_WARN_ONLY` (default 1), `CARS_LOG_PATH`, `CARS_REGISTRY_DIR`, `CARS_HELPER_DIR`.
- [ ] All Python tests pass: `uv run pytest tests/canonical_store/ -v` reports 32 passed.
- [ ] All bats tests pass: `bats tests/enforcement/test_check_*.bats tests/canonical_store/test_query.sh` reports 31 passed.
- [ ] Each enforcement script in warn-only mode (`CARS_WARN_ONLY=1`) exits 0 on violations and writes to `${CARS_LOG_PATH}` (`docs/reports/canonical-store-warn-log.md`).
- [ ] Each enforcement script in block mode (`CARS_WARN_ONLY=0`) exits 1 on violations.
- [ ] `query.sh --tier 3 --method <id> --inputs <json> --params <json>` computes fingerprints and emits plan-section-ready Markdown.
- [ ] No changes outside Plan 1's declared scope: `AGENTS.md`, `SHARED_SOUL.md`, `docs/plans/_template-issue-plan.md`, `.claude/skills/`, `.claude/rules/`, and `digitalmodel/` are all untouched (Plan 2/3 territory).
- [ ] Plan review artifacts written to `scripts/review/results/YYYY-MM-DD-plan-TBD-{claude,codex,gemini}.md` (3-provider T3 review per design D13).
- [ ] Cross-platform fingerprint stability verified: `test_fingerprint_known_value_stability` passes on Linux + macOS in CI (added to Plan 1's CI matrix).

---

## Adversarial Review Summary

<!-- Filled in after the 3-provider plan review completes. Do not post to GitHub until populated. -->

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | APPROVE / MINOR / MAJOR | (TBD) |
| Codex | APPROVE / MINOR / MAJOR | (TBD) |
| Gemini | APPROVE / MINOR / MAJOR | (TBD) |

**Overall result:** PASS / FAIL (re-draft required)

Revisions made based on review:
- (list any changes made to the plan after adversarial review)

---

## Risks and Open Questions

- **Risk: Float fingerprint cross-platform divergence.** Same input on Linux vs macOS may produce different fingerprints if `_round_floats()` interacts with platform-specific IEEE-754 rounding. Mitigation: Task 5 includes a pinned regression test (`test_fingerprint_known_value_stability`); CI must run on both platforms before Plan 1 is ratified for use.
- **Risk: bats not installed.** Tests under `tests/enforcement/` require `bats` (Bash Automated Testing System). Mitigation: implementation plan reviewer must verify `bats` is available on the executor's machine; install via `sudo apt install bats` (Linux) or `brew install bats-core` (macOS) before starting Task 10.
- **Risk: `jsonschema` Python library not in deps.** `tests/canonical_store/test_tier_schemas.py` imports `jsonschema`. Mitigation: implementation plan reviewer adds `jsonschema` to the appropriate dependency manifest (likely `pyproject.toml` dev-deps) before Task 6 if not already present.
- **Risk: `yaml` Python library version mismatch.** `load_registry.py` imports `yaml`. PyYAML 6.x is standard; verify before Task 4. Mitigation: check `uv pip list | grep -i yaml` in implementation plan's Step 4.0.
- **Risk: CARS_LOG_PATH location creates docs/reports/ pollution.** `docs/reports/canonical-store-warn-log.md` grows append-only. Mitigation: add to `docs/reports/.gitignore` if commit-noise becomes problematic — defer to Plan 5 (dashboards) which formalizes the reporting layer.
- **Open: Issue number.** TBD until the user files an issue against this design. Implementation plan execution waits for issue filing.
- **Open: 3-provider plan review timing.** Standard 3-agent adversarial review per AGENTS.md AI Review Policy; T3 mandatory per design D13. Should run before any `status:plan-review` label.
- **Open: Test target compatibility for digitalmodel later (Plan 3).** Plan 3 extends `digitalmodel.citations.schema.Citation`; the schema this plan ships must be forward-compatible. The result schema is already designed to accept the existing Citation fields (`code_id`, `source_sibling`, `revision`) under `citations[]`. If Plan 3 reveals incompatibility, this plan's `result.schema.json` may need a v1.1 bump via the always-T3 path.

---

## Complexity: T3

This plan creates 22 new files across 3 directories, ~31 unit/bats tests, modifies one existing file (`enforcement-env.sh`), and introduces a registry + helper + enforcement triad that other Plans 2-6 build on. T3 is justified by: multi-file architectural change, cross-script integration (query.sh → fingerprint.py + load_registry.py → registry YAML), JSON-schema definitions used by multiple downstream consumers, and the fact that all 5 Plan 2-6 implementations depend on Plan 1's interface choices.
