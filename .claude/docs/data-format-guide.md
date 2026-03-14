# Data Format Guide

> Canonical rule: `.claude/rules/coding-style.md` §Data Format Selection

## Why This Matters

AI agents follow instructions better when:
1. **More instructions fit** — YAML uses 30-40% fewer tokens than JSON
2. **Rules are co-located** — YAML comments (`# HARD RULE`) next to fields improve compliance
3. **Corruption is caught** — schema validation rejects structural changes to protected fields

Markdown tables have no parser. Corruption (deleted rows, misaligned columns) is silent.

## Format Decision Matrix

| Writer | Format | Examples |
|--------|--------|---------|
| Agent writes structured data | **YAML** + schema | `ac-test-matrix.yaml`, `test-results.yaml`, `claim-evidence.yaml` |
| Agent writes prose | **Markdown** | Plans, review narratives, WRK bodies |
| Script generates output | **JSON** | `gate-evidence-summary.json`, `accumulator.json` |
| Human curates config | **YAML** | `stage-*.yaml`, `pricing.yaml`, `machine-ranges.yaml` |
| Append-only machine logs | **JSONL** | `wrk-completions.jsonl`, `knowledge-base/*.jsonl` |

## YAML vs JSON — Agent-Level Comparison

| Dimension | YAML | JSON | Winner |
|-----------|------|------|--------|
| Token cost | ~30-40% fewer | Verbose | **YAML** |
| Agent comprehension | Equal | Equal | Tie |
| Inline instructions | `# comments` supported | No comments | **YAML** |
| Multiline strings | `\|` blocks, native | `\n` escaping | **YAML** |
| Corruption detection | Silent (wrong indent = valid YAML) | Loud (parse error) | **JSON** |
| With schema validation | Loud (schema rejects) | Loud (parse rejects) | **Tie** |

**Conclusion**: With schema validation, YAML wins on every dimension except external API interchange.

## Schema Validation

New agent-writable YAML files should have a companion schema:

```
config/work-queue/schemas/
  ac-test-matrix-schema.yaml
  test-results-schema.yaml
  feature-checklist-schema.yaml
```

Validator scripts reject:
- Missing required fields
- Wrong field types
- Structural changes to protected fields (e.g., agent edited `description` instead of `passes`)

## AC Test Matrix — Target Format

Current (Markdown — **deprecated**):
```markdown
| AC | Description | Result | Evidence |
|----|-------------|--------|----------|
| AC-1 | Feature works | PASS | test_feature::test_basic |
```

Target (YAML):
```yaml
# Schema: config/work-queue/schemas/ac-test-matrix-schema.yaml
wrk_id: WRK-1173
generated_at: "2026-03-13T00:00:00Z"
results:
  - id: AC-1
    description: Feature works  # HARD RULE: never edit description
    passes: true                # Agent: only change this field
    evidence: test_feature::test_basic
    verified_at: "2026-03-13T10:00:00Z"
  - id: AC-2
    description: Edge case handled
    passes: false
    evidence: null
    verified_at: null
```

## Test Results — Target Format

Current (Markdown — **deprecated**):
```markdown
| Test | Result | Notes |
|------|--------|-------|
| test_basic | PASS | |
```

Target (YAML):
```yaml
wrk_id: WRK-1173
test_suite: unit
results:
  - name: test_basic
    result: PASS  # PASS or FAIL only
    duration_ms: 42
    notes: ""
  - name: test_edge_case
    result: FAIL
    duration_ms: 108
    notes: "AssertionError: expected 3, got 4"
summary:
  total: 2
  passed: 1
  failed: 1
```

## Migration Path

Legacy `.md` files in archived WRK assets are not migrated (read-only history).
New files from this point forward must use the correct format.

Migration script: `scripts/work-queue/audit-data-formats.sh`
Migration WRK: WRK-1177 (updates stage configs + gate scripts to accept `.yaml`)

## Files That Must Change (Source of Agent Behavior)

These stage configs tell agents which files to create:

| Stage config | Current artifact | Target artifact |
|-------------|-----------------|-----------------|
| `stage-12-tdd-eval.yaml` | `ac-test-matrix.md` | `ac-test-matrix.yaml` |
| `stage-13-agent-cross-review.yaml` | `ac-test-matrix.md` | `ac-test-matrix.yaml` |

These scripts parse the files:

| Script | Reads | Must update |
|--------|-------|-------------|
| `exit_stage.py` | `ac-test-matrix.md` | Accept `.yaml` (fallback to `.md` for legacy) |
| `verify-gate-evidence.py` | `ac-test-matrix.md` | Accept `.yaml` (fallback to `.md`) |
| `generate-html-review.py` | `ac-test-matrix.md`, `test-results.md` | Accept `.yaml` |
