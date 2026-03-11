---
name: file-taxonomy
version: "1.6.0"
category: workspace
description: "Canonical decision tree for where to place output files, repo manifests, and all generated artifacts across the workspace-hub ecosystem."
invocation: /file-taxonomy
applies-to: [claude, codex, gemini]
capabilities: []
requires: []
see_also: [repo-structure, clean-code]
tags: []
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
8. Is it documentation of how something works? → `docs/modules/<domain>/` or `docs/domains/<domain>/`
9. Is it a how-to guide? → `docs/guides/`
10. Is it runtime config (YAML/JSON consumed by the app)? → `config/<domain>/`
11. Is it an exploratory analysis script? → `scripts/analysis/<domain>/`
12. Is it a Jupyter notebook? → `notebooks/<domain>/` (NEVER in `src/`)
13. Is it benchmark data / input files for runtime? → `data/inputs/<domain>/`
14. Is it a provider prompt template (Codex/Gemini)? → `.codex/prompts/` or `.gemini/prompts/`
15. Is it a shell test harness for agent/orchestration scripts? → `scripts/agents/tests/`
16. Is it a SQL query or HTML template loaded at runtime by a Python package? → keep in `src/<pkg>/<domain>/` as a **package resource**; declare in `pyproject.toml` `[tool.setuptools.package-data]`; do NOT put at `config/`
17. Is it a markdown doc found inside `src/`? → move to `docs/domains/<domain>/` — markdown is NEVER a package resource

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
| Runtime config (user-facing YAML/JSON) | `config/<domain>/` | Never output; env-specific overrides only |
| Package-internal config (not user-facing) | `src/<pkg>/<module>/config/` | Exception: only when config is truly internal to the package |
| Root-level build/test config | `.` (repo root) | pyproject.toml, pytest.ini, Makefile, .gitignore only |
| Analysis scripts (exploratory) | `scripts/analysis/<domain>/` | Not `src/`; exploratory scripts only |
| Jupyter notebooks | `notebooks/<domain>/` | Never committed to `src/` or `tests/` |
| Runtime input files | `data/inputs/<domain>/` | YAML/CSV/JSON inputs consumed at runtime |
| Test benchmarks | `tests/benchmarks/<domain>/` | Benchmark comparisons; single canonical location |
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
| Config | `config/analysis/bsee_config.yaml` | Domain-scoped; never at root except pyproject/pytest.ini |
| Analysis scripts | `scripts/analysis/production/decline_study.py` | Not in src/ |
| Notebooks | `notebooks/bsee/well_production_eda.ipynb` | Domain subdir required |
| Input data | `data/inputs/metocean/jonswap_params.yaml` | Runtime inputs; separate from test fixtures |
| Internal config dir | `src/<pkg>/<domain>/config/` | **Singular** `config/` — NEVER `configs/` (plural) |

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

## Repo Manifest Files

Some files describe the structure and capabilities of the repo itself — these are "repo manifests." They have a canonical home:

| Manifest Type | Canonical Location | Notes |
|--------------|-------------------|-------|
| Module/capability index | `specs/index.yaml` | Machine-readable index of all modules |
| Human-readable index | `README.md` (repo root) or `docs/README.md` | One-page orientation |
| Module manifest YAML | `specs/modules/<domain>.yaml` | Per-module architecture spec |
| Data source descriptions | `specs/data-sources/<name>.yaml` | Structured, version-controlled |
| Provider capability map | `config/agents/` | `model-registry.yaml`, `ai-agents-registry.json` |

**Do NOT** place manifest files at repo root (e.g., `MODULE_INDEX.md`, `module-manifest.yaml`). They become stale, undiscoverable, and inconsistently named. Use `specs/` instead.

### Migration Path

```bash
# If MODULE_INDEX.md or module-manifest.yaml exist at root:
git mv MODULE_INDEX.md specs/modules/INDEX.md        # or specs/index.md
git mv module-manifest.yaml specs/modules/manifest.yaml
# Update any references in README.md
```

---

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

---

## AI Agent Log & Session File Locations

Consult this section before searching for AI session data or writing log analysis scripts.
See `/file-structure-skills-map` for the full skill cluster context.

### Native Session Stores (gitignored — local to each machine)

| Agent | Path | Format | Notes |
|-------|------|--------|-------|
| Claude | `~/.claude/projects/<encoded-path>/*.jsonl` | JSONL | Full session transcripts; managed by Claude CLI |
| Codex | `~/.codex/sessions/YYYY/MM/DD/rollout-*.jsonl` | JSONL | ~302 sessions on ace-linux-1 (2026-03-03) |
| Gemini | `~/.gemini/tmp/<project>/chats/session-*.json` | JSON | ~772 sessions on ace-linux-1 (2026-03-03) |

`<encoded-path>` = repo path with `/` replaced by `-` (e.g. `-mnt-local-analysis-workspace-hub`).

### Orchestrator Logs (`logs/orchestrator/` — gitignored per-machine)

Written by hooks and cross-review scripts; **not** native session transcripts.

| Path | Written by | Format |
|------|-----------|--------|
| `logs/orchestrator/claude/session_YYYYMMDD.jsonl` | Claude pre-tool/post-tool hooks | JSONL |
| `logs/orchestrator/codex/*.log` | `scripts/review/submit-to-codex.sh` | text |
| `logs/orchestrator/gemini/*.log` | `scripts/review/submit-to-gemini.sh` | text |

Structure: `logs/orchestrator/{claude,codex,gemini}/` — one dir per agent.

### Derived State (git-tracked — crosses machines via commit)

| Path | Written by | Format |
|------|-----------|--------|
| `.claude/state/session-signals/*.jsonl` | session-end hook | JSONL |
| `.claude/state/session-analysis/` | comprehensive-learning Phases 1–9 | Markdown |
| `.claude/state/session-analysis/compilation-YYYYMMDD.md` | Phase 10a (ace-linux-1 only) | Markdown |
| `.claude/state/skill-scores.yaml` | comprehensive-learning Phase 7 | YAML |
| `.claude/state/candidates/` | comprehensive-learning Phase 6 | YAML |
| `scripts/review/results/` | `submit-to-{codex,gemini}.sh` | text |

### Key Distinction

```
native stores   → raw AI session transcripts (local machine only, gitignored)
orchestrator/   → cross-review invocation logs (sparse — only on cross-review runs)
derived state   → processed analysis output (git-tracked, crosses machines)
```

### Verbose Output Setting — Does NOT Affect Logs

**Verified 2026-03-08 (live test):**

- `--verbose` / "Verbose Output" in the Claude Code config dialog is a **terminal display flag only** — it controls what you see in the terminal, not what gets written to logs.
- There is **no `verbose` field in `settings.json`**; the setting is CLI-only and not persisted.
- `logs/orchestrator/claude/session_YYYYMMDD.jsonl` is written by `session-logger.sh` hook (pre/post every tool call) — **completely independent of verbose**.
- `~/.codex/sessions/YYYY/MM/DD/rollout-*.jsonl` (~296K per session) is written by codex CLI itself — also independent of Claude Code verbose.
- **Comprehensive-learning signal quality is unaffected by verbose=false.**

Test method: ran `scripts/review/submit-to-codex.sh` before/after; codex session file count grew 3→4, Claude hook log grew 694→700 lines, both independent of verbose flag.

### acma-ansys05 (Windows)

Paths follow the same convention but under `%USERPROFILE%` / `C:\Users\<user>\`:
- Claude: `%USERPROFILE%\.claude\projects\<encoded-path>\*.jsonl`
- Codex: `%USERPROFILE%\.codex\sessions\YYYY\MM\DD\rollout-*.jsonl`
- Gemini: `%USERPROFILE%\.gemini\tmp\<project>\chats\session-*.json`

Use Git Bash to apply Linux-style path patterns on acma-ansys05.
