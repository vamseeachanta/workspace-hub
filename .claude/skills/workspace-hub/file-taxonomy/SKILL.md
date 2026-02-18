---
skill: workspace-hub:file-taxonomy
version: 1.1.0
invocation: /file-taxonomy
applies-to: [claude, codex, gemini]
---

# File Taxonomy — Where Does This File Go?

Consult this skill before writing any output file. Do not create new output dirs
without checking the canonical map below.

## Decision Tree

1. Is it human-readable output (HTML, PDF, Markdown report)? → `reports/<domain>/`
2. Is it raw computation (arrays, matrices, intermediate data)? → `results/<domain>/`
3. Is it a benchmark comparison vs reference? → `reports/benchmarks/<domain>/`
4. Is it validated ground truth / reference data? → `data/<domain>/`
5. Is it only used by tests? → `tests/<domain>/fixtures/`
6. Is it ephemeral / reproducible from source? → `cache/` (gitignored, never committed)
7. Is it a design spec (pre-build)? → `specs/wrk/WRK-NNN/` or `specs/repos/<repo>/`
8. Is it documentation of how something works? → `docs/modules/<domain>/`
9. Is it a how-to guide? → `docs/guides/`
10. Is it config? → `config/`
11. Is it a provider prompt template (Codex/Gemini)? → `.codex/prompts/` or `.gemini/prompts/`
12. Is it a shell test harness for agent/orchestration scripts? → `scripts/agents/tests/`

## Format Guide

| Use case | Format | Reason |
|----------|--------|--------|
| Structured config / schema | **YAML** | Human-readable, comment-friendly |
| API responses / machine data | **JSON** | Strict types, universal tooling |
| Tabular data (large) | **CSV** | Pandas-native, Excel-compatible |
| Tabular data (small, typed) | **YAML** | Inline, readable with units |
| Reports (human) | **HTML** or **Markdown** | Browsable / diffable |
| Binary data / matrices | **NumPy .npy** | Efficient, lossless |
| Geospatial | **GeoJSON** or **NetCDF** | Standard for domain |
| Model parameters | **YAML** | Editable, diffable |
| Hydrodynamic output | **.owd** (internal) | OrcaWave native; never convert to CSV |

## Canonical Directory Map

| File Type | Canonical Dir | Rule |
|-----------|--------------|------|
| Structured reports (HTML, PDF, Markdown) | `reports/<domain>/` | Timestamped filenames for archives |
| Raw computation output (arrays, matrices) | `results/<domain>/` | Machine-readable; intermediate data |
| Benchmark comparisons | `reports/benchmarks/<domain>/` | method_vs_reference naming pattern |
| Validated reference data | `data/<domain>/` | Ground truth; version-controlled |
| Test fixtures | `tests/<domain>/fixtures/` | Input data for tests only |
| Cache / temp | `cache/` (gitignored) | Ephemeral; never committed |
| Coverage | `reports/coverage/` | HTML in htmlcov/; XML at reports/coverage/coverage.xml |
| Specs / design docs | `specs/wrk/WRK-NNN/` or `specs/repos/<repo>/` | Pre-build; Route C only |
| Reference docs | `docs/modules/<domain>/` | Post-build; explains how it works |
| Guides | `docs/guides/` | How-to for humans; stable prose |
| Config | `config/` | Never output |
| Provider prompt templates | `.codex/prompts/` or `.gemini/prompts/` | Provider-specific; supplement skills |
| Agent/orchestration test scripts | `scripts/agents/tests/` | Shell test harnesses; `test-*.sh` naming |
| Agent capability profiles | `config/agents/` | model-registry, provider-capabilities, ai-agents-registry |

## Naming Conventions

| Pattern | Example | Rule |
|---------|---------|------|
| Timestamped reports | `spar_fatigue_2026-02-18.html` | ISO date suffix for archives |
| Domain-scoped results | `results/fatigue/spar_sn_curves.npy` | Domain subdir always present |
| Benchmark files | `reports/benchmarks/wamit/ellipsoid_vs_wamit.html` | method_vs_reference |
| Coverage | `reports/coverage/coverage.xml` | Singular fixed name, gitignored |
| Fixtures | `tests/bsee/fixtures/cost_sample.yaml` | Domain-matched to src/ |

## Gitignore Policy

| Category | Always gitignore | Always track |
|----------|-----------------|-------------|
| `results/` | Yes (computation output) | Never |
| `cache/` | Yes | Never |
| `data/` | Never (ground truth) | Yes (large files → LFS) |
| `tests/fixtures/` | Never | Yes |
| `htmlcov/` | Yes | Never |
| `coverage*.xml` | Yes | Never |
| `*.backup*` | Yes | Never |
| `node_modules/` | Yes | Never |
| `dist/`, `build/` | Yes | Never |
| `.venv/`, `venv/` | Yes | Never |
| `reports/` | If fully generated | If curated/reference |

## Architectural Decisions (Resolved 2026-02-18)

### specs/ vs docs/ vs plans/

- `specs/wrk/WRK-NNN/` — Execution spec for a specific work item (Route C only)
- `specs/repos/<repo>/` — Formal design decisions / ADRs for a repo
- `specs/modules/` — System-level module specs (pre-build design)
- `docs/modules/<domain>/` — Reference docs written *after* build
- `docs/guides/` — How-to guides for humans
- `.claude/work-queue/` — WRK item tracking only (no specs or docs)

**`plans/` does not exist.** Planning lives in WRK item body (Route A/B) or `specs/wrk/` (Route C).

### Where WRK items reside

Single location: `workspace-hub/.claude/work-queue/` only.
Submodule repos must NOT have their own WRK items.

### Module-based folder structure (canonical)

```
src/<package>/<domain>/<component>/   ← source code
tests/<domain>/unit/                  ← fast unit tests
tests/<domain>/integration/           ← component tests
tests/<domain>/fixtures/              ← test data
docs/modules/<domain>/                ← reference docs
data/modules/<domain>/                ← input data
```

NOT `tests/modules/<domain>/` — the `modules/` wrapper in tests is redundant.

### Provider adapter directories (canonical 2026-02-18)

```
.codex/
  skills → ../.claude/skills  (symlink)
  prompts/                     ← provider-specific prompt templates
  settings.json
.gemini/
  skills → ../.claude/skills  (symlink)
  prompts/                     ← provider-specific prompt templates
  settings.json
```

- Skills live in `.claude/skills/` only — `.codex/skills` and `.gemini/skills` are symlinks
- Provider prompts compensate for lack of skill marketplace in Codex/Gemini
- `config/agents/` holds: `model-registry.yaml`, `provider-capabilities.yaml`, `ai-agents-registry.json`, `behavior-contract.yaml`

### Shell agent test scripts

- `scripts/agents/tests/test-*.sh` — harness tests for workflow-guards.sh, execute.sh routing
- Run with `bash scripts/agents/tests/test-name.sh`; exit 0 = pass, 1 = fail
- NOT placed in `tests/` (which is for Python packages); shell scripts stay under their `scripts/` home
