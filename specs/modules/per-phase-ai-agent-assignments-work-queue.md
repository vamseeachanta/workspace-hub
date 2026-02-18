# Plan: Per-Phase AI Agent Assignments for Approved WRK Items

## Context

21 WRK items have `plan_approved: true` with detailed phase breakdowns (4-7 phases each). Currently, each item has a single `provider` field that assigns the **entire** item to one agent. But phases within a single item often require different skills — e.g., a research phase suits `gemini`, a coding phase suits `codex`, and a multi-module architecture phase suits `claude`.

Adding a `task_agents` map to frontmatter lets the orchestrator (Claude) know which agent to dispatch for each phase **before execution begins**.

### Agent Strength Profiles
| Agent | Best For |
|-------|----------|
| **codex** | Focused code, single-file, algorithms, testing, refactoring, config |
| **gemini** | Research, data analysis, summarization, content writing, documents |
| **claude** | Multi-file architecture, orchestration, complex integration, sensitive data |

## Convention

### Frontmatter Format
```yaml
provider: claude
provider_alt:
task_agents:
  phase_1: codex    # Source catalog & nearest-source finder
  phase_2: codex    # Spatial assessment implementation
  phase_3: codex    # Extrapolation models
  phase_4: codex    # Validation & visualization
  phase_5: codex    # Tests
```

### Rules
- **Key**: `task_agents` — placed after `provider_alt:` in frontmatter
- **Phase naming**: `phase_N` (0-indexed if Phase 0 exists, else 1-indexed) matching the plan headings
- **Sub-phases**: `phase_2a`, `phase_2b`, `phase_3b` for lettered sub-phases
- **Comment**: Brief phase description after `#`
- **Completed phases**: Omit from `task_agents` (e.g., WRK-157 phases 1-2 already done)
- **100% complete items**: Skip entirely (WRK-155)

## Per-Phase Assignments (20 items)

### WRK-015 — Metocean extrapolation (provider: claude)
```yaml
task_agents:
  phase_1: gemini   # Source catalog & nearest-source research
  phase_2: codex    # Spatial assessment — bathymetry, fetch code
  phase_3: codex    # Extrapolation models — wave transform, tidal
  phase_4: codex    # Validation & visualization
  phase_5: codex    # Tests
```

### WRK-019 — Cost data layer (provider: claude:gemini)
```yaml
task_agents:
  phase_1: gemini   # Cost data source identification — research
  phase_2: codex    # Cost estimation engine
  phase_3: gemini   # Regional cost profiles — data compilation
  phase_4: claude   # Integration with field pipeline — multi-module
  phase_5: codex    # Reports & visualization
  phase_6: codex    # Tests
```

### WRK-020 — GIS skill (provider: claude)
```yaml
task_agents:
  phase_1: codex    # CRS & coordinate engine
  phase_2a: codex   # Core formats (GeoJSON, KML)
  phase_2b: codex   # Heavy formats (Shapefile, GeoTIFF)
  phase_3: codex    # Spatial queries
  phase_4: claude   # Application integrations — Blender, QGIS, multi-app
  phase_5: codex    # Tests
```

### WRK-021 — Stock analysis (provider: gemini)
```yaml
task_agents:
  phase_1: gemini   # Data acquisition — Yahoo Finance, SEC EDGAR
  phase_2: codex    # Technical indicators — SMA, RSI, MACD
  phase_3: codex    # Trend change detection algorithms
  phase_4: gemini   # Insider trading monitor — EDGAR parsing
  phase_5: codex    # Alerting & reporting
  phase_6: codex    # Tests
```

### WRK-022 — Property valuation GIS (provider: gemini)
```yaml
task_agents:
  phase_1: gemini   # Geocoding & property lookup — research
  phase_2: codex    # Spatial factor extraction
  phase_3: gemini   # Market data integration — data compilation
  phase_4: codex    # Valuation model
  phase_5: codex    # Visualization & report
  phase_6: codex    # Tests
```

### WRK-023 — Property GIS timeline (provider: claude)
```yaml
task_agents:
  phase_0: gemini   # Tool research spike
  phase_1: gemini   # Research & data source integration
  phase_2: codex    # Historical imagery retrieval — API integration
  phase_3: codex    # Timeline visualization
  phase_4: codex    # Future development projection
  phase_5: codex    # Google Earth animation & KML export
  phase_6: codex    # Report generation
  phase_7: codex    # Tests
```

### WRK-032 — OrcaFlex pipeline modular (provider: codex)
```yaml
task_agents:
  phase_5a: codex   # Stinger roller builder
  phase_5b: codex   # Campaign soil override test
  phase_5c: codex   # CLI campaign smoke test
  phase_5d: gemini  # Documentation & skill registration
```

### WRK-036 — OrcaFlex deployment (provider: claude)
```yaml
task_agents:
  phase_0: gemini   # Reference examples — review existing models
  phase_1: claude   # Deployment schema extension — architecture
  phase_2: codex    # Deployment builders — focused code
  phase_3: claude   # Parametric splash zone campaign — multi-module
  phase_4: codex    # Load extraction & export
  phase_5: codex    # Results summary & reporting
```

### WRK-043 — Parametric hull analysis (provider: claude)
```yaml
task_agents:
  phase_1: claude   # Parametric hull form definition — schema design
  phase_2: claude   # Batch diffraction pipeline — multi-module
  phase_3: codex    # RAO database & storage
  phase_4: codex    # Lookup graph generation — Plotly
  phase_5: codex    # engine.py registration + CLI
  phase_6: codex    # Client reporting package
```

### WRK-045 — Rigid jumper analysis (provider: claude)
```yaml
task_agents:
  phase_1: codex    # Jumper configuration library — data structures
  phase_2: codex    # OrcaFlex model generator
  phase_3: codex    # Stress analysis — DNV-ST-F101
  phase_4: codex    # VIV assessment — DNV-RP-F105
  phase_5: claude   # Parametric runner — multi-module orchestration
  phase_6: codex    # Tests
```

### WRK-046 — Drilling/completion riser (provider: claude)
```yaml
task_agents:
  phase_1: claude   # Drilling riser model — complex multi-component
  phase_2: claude   # Completion riser model — complex multi-component
  phase_3: claude   # Parametric analysis engine — multi-module
  phase_4: codex    # Results & operability
  phase_5: codex    # Tests
```

### WRK-047 — OpenFOAM CFD (provider: claude)
```yaml
task_agents:
  phase_0: codex    # Prerequisites check
  phase_1: codex    # Case data model — Pydantic schemas
  phase_2: codex    # Geometry import & mesh pipeline
  phase_3: claude   # Solver configuration — multi-file marine setups
  phase_4: codex    # Post-processing pipeline
  phase_5: codex    # Parametric case generation
  phase_6: claude   # Integration & CLI — multi-module wiring
```

### WRK-075 — OFFPIPE integration (provider: claude)
```yaml
task_agents:
  phase_0: gemini   # Documentation analysis (USER-BLOCKED)
  phase_1: claude   # Scaffold + router + engine.py — architecture
  phase_2: codex    # OFFPIPE output parser — single module
  phase_3: codex    # OrcaFlex pipelay result extraction
  phase_4: codex    # Comparison engine — algorithm
  phase_5: codex    # Benchmark report — templating
  phase_6: codex    # Input generator (deferred)
```

### WRK-126 — Benchmark all models (provider: claude)
```yaml
task_agents:
  phase_1: gemini   # Model inventory & classification — research
  phase_2: codex    # Statics baseline — run benchmarks
  phase_3: codex    # Time domain benchmark
  phase_4: codex    # Frequency domain benchmark
  phase_5: codex    # Seed equivalence analysis
  phase_6: gemini   # Consolidated report — summarization
```

### WRK-146 — Website overhaul (provider: claude:gemini)
```yaml
task_agents:
  phase_1: gemini   # Homepage rewrite — content
  phase_2: gemini   # About page rewrite — content
  phase_3: gemini   # Case study narratives — content writing
  phase_4: codex    # Blog integration — HTML/template
  phase_5: gemini   # Social proof section — content
  phase_6: claude   # Visual review — cross-page QA
```

### WRK-147 — Strategy repo (provider: claude)
```yaml
task_agents:
  phase_1: codex    # Create repo & structure — scaffolding
  phase_2: claude   # CLAUDE.md & agent definitions — architecture
  phase_3: gemini   # Strategy documents — content/research
  phase_4: codex    # Pipeline & experiments — templates
  phase_5: gemini   # Metrics & content
```

### WRK-149 — digitalmodel test coverage (provider: codex)
```yaml
task_agents:
  phase_1: codex    # Baseline measurement
  phase_2: codex    # Priority module tests
  phase_3: codex    # Cross-cutting tests
  phase_4: codex    # CI integration
```

### WRK-154 — CI workflow rewrite (provider: codex)
```yaml
task_agents:
  phase_1: codex    # Audit & test
  phase_2: codex    # Fix baseline-check.yml
  phase_3: codex    # Fix multi-ai-review.yml
  phase_4: codex    # Verify & document
```

### WRK-156 — FFS Phase 1 (provider: claude)
```yaml
task_agents:
  phase_0: codex    # Prerequisites — fix imports, legal scan
  phase_1: codex    # Grid parser — focused code
  phase_2: claude   # FFS router & assessment — multi-module architecture
  phase_3: codex    # Decision engine — algorithm
  phase_3b: codex   # Expert HTML report — templating
  phase_4: codex    # Tests
```

### WRK-157 — Fatigue enhancement (provider: claude, 40% done)
```yaml
task_agents:
  phase_3: codex    # Parametric sweep engine — algorithm
  phase_4: claude   # Worked examples — multi-standard, cross-module
  phase_5: codex    # Design-code report templates
```

### WRK-164 — Production test data quality (provider: claude)
```yaml
task_agents:
  phase_1: codex    # Production test quality scorer — algorithm
  phase_2: codex    # VLP correlations + IPR models — algorithm
  phase_3: codex    # GIGO detector + reconciliation
  phase_4: codex    # Tests & examples
```

## Distribution Summary (across all phases)

| Agent | Phase Count | % | Typical Work |
|-------|-------------|---|--------------|
| **codex** | 74 | 66% | Algorithm, testing, single-module code, templating |
| **gemini** | 18 | 16% | Research, data compilation, content writing, docs |
| **claude** | 20 | 18% | Architecture, multi-module integration, orchestration |

## Files Modified

20 WRK files in `.claude/work-queue/pending/`:
```
WRK-015, 019, 020, 021, 022, 023, 032, 036, 043, 045,
046, 047, 075, 126, 146, 147, 149, 154, 156, 157, 164
```

**Skipped**: WRK-155 (100% complete)

## Implementation

For each file, insert `task_agents:` block into frontmatter after the `provider_alt:` line. No script changes needed — the orchestrator (Claude) reads `task_agents` directly from frontmatter when executing phases.

## Verification

```bash
# 1. Confirm all 20 files have task_agents
grep -l "^task_agents:" .claude/work-queue/pending/WRK-*.md | wc -l
# Expected: 20 (or 21 if WRK-155 included)

# 2. Validate YAML frontmatter still parseable
for f in .claude/work-queue/pending/WRK-{015,019,020,021,022,023,032,036,043,045,046,047,075,126,146,147,149,154,156,157,164}.md; do
  python3 -c "
import yaml, sys
with open('$f') as fh:
    content = fh.read()
    fm = content.split('---')[1]
    data = yaml.safe_load(fm)
    ta = data.get('task_agents', {})
    if not ta: sys.exit(1)
    print(f'{data[\"id\"]}: {len(ta)} phases assigned')
  "
done

# 3. Count agent distribution
grep -h "^\s\+phase_" .claude/work-queue/pending/WRK-*.md | awk -F: '{gsub(/\s+#.*/,"",$2); print $2}' | sort | uniq -c | sort -rn
# Expected: ~74 codex, ~20 claude, ~18 gemini
```
