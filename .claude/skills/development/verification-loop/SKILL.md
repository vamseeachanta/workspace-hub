---
name: verification-loop
description: Six-phase quality gate for code changes. Runs build, typecheck, lint, test, security, and diff-review in sequence. Supports JavaScript/TypeScript, Python, and Rust with auto-detection and skip conditions.
version: 1.0.0
category: development
last_updated: 2026-01-24
phases:
  - build
  - typecheck
  - lint
  - test
  - security
  - diff-review
supported_languages:
  - javascript
  - typescript
  - python
  - rust
related_skills:
  - testing-production
  - code-reviewer
  - systematic-debugging
capabilities: []
requires: []
see_also: []
---

# Verification Loop Skill

## Overview

Six-phase quality gate validating code changes sequentially. Each phase must pass before proceeding. Auto-detects project type and adapts commands.

## When to Use

- Before committing changes
- Pre-merge validation
- CI/CD pipeline integration
- Code review preparation

## Phase Definitions

### Phase 1: Build

| Project | Command | Skip If |
|---------|---------|---------|
| Node.js | `npm run build` | No build script in package.json |
| Python | `uv build` / `python -m build` | No pyproject.toml or setup.py |
| Rust | `cargo build --release` | No Cargo.toml |

### Phase 2: Typecheck

| Project | Command | Skip If |
|---------|---------|---------|
| TypeScript | `tsc --noEmit` | No tsconfig.json |
| Python | `pyright` / `mypy .` | No type checker installed |
| Rust | (included in build) | Always (cargo handles types) |

### Phase 3: Lint

| Project | Command | Skip If |
|---------|---------|---------|
| JS/TS | `eslint . --ext .js,.jsx,.ts,.tsx` | No eslint config |
| Python | `ruff check .` / `flake8 .` | No linter config |
| Rust | `cargo clippy -- -D warnings` | No Cargo.toml |

### Phase 4: Test

| Project | Command | Skip If |
|---------|---------|---------|
| JS/TS | `npm test` / `npm run test:coverage` | No test script |
| Python | `pytest --cov` | No tests directory |
| Rust | `cargo test` | No tests |

### Phase 5: Security

| Project | Command | Skip If |
|---------|---------|---------|
| JS/TS | `npm audit` | No package-lock.json |
| Python | `safety check` / `pip-audit` / `bandit -r .` | No scanner installed |
| Rust | `cargo audit` | cargo-audit not installed |

### Phase 6: Diff Review

**Command:** `git diff HEAD~1 --stat`

Provides summary of changes for review context. Always informational, never fails.

## Detection Logic

```bash
# Project type detection
detect_project() {
  [ -f "package.json" ] && echo "node"
  [ -f "pyproject.toml" ] || [ -f "setup.py" ] && echo "python"
  [ -f "Cargo.toml" ] && echo "rust"
}

# Skip conditions per phase
should_skip_typecheck() {
  [ ! -f "tsconfig.json" ] && [ ! -f "pyproject.toml" ]
}

should_skip_lint() {
  [ ! -f ".eslintrc.js" ] && [ ! -f ".eslintrc.json" ] && \
  [ ! -f "ruff.toml" ] && [ ! -f "Cargo.toml" ]
}

should_skip_test() {
  [ ! -d "tests" ] && [ ! -d "test" ] && \
  ! find . -name "*_test.py" -o -name "test_*.py" | grep -q .
}
```

## Execution Flow

```
START -> BUILD -> TYPECHECK -> LINT -> TEST -> SECURITY -> DIFF-REVIEW -> SUCCESS
              \         \         \       \          \
               -> SKIP   -> SKIP   -> SKIP -> SKIP   -> SKIP (if conditions met)

Any phase FAIL -> STOP with error report
```

## Configuration

### Environment Variables

```bash
VERIFICATION_SKIP_PHASES="security,diff-review"  # Skip specific phases
VERIFICATION_COVERAGE_MIN=80                      # Coverage threshold
VERIFICATION_STRICT=true                          # Fail on warnings
```

### Config File (.verification-loop.yml)

```yaml
phases:
  build:
    enabled: true
    timeout: 300
  typecheck:
    enabled: true
    timeout: 120
  lint:
    enabled: true
    allow_warnings: false
  test:
    enabled: true
    coverage_threshold: 80
  security:
    enabled: true
    severity_threshold: moderate
  diff-review:
    enabled: true
    compare_ref: HEAD~1

skip_conditions:
  - pattern: "*.md"
    skip_phases: [build, typecheck, lint, test]
```

## Error Handling

| Phase | On Failure |
|-------|------------|
| Build | Stop, report compilation errors |
| Typecheck | Stop, report type errors |
| Lint | Stop, report lint violations |
| Test | Stop, report failed tests |
| Security | Report vulns, continue if below threshold |
| Diff-Review | Always succeeds (informational) |

## Integration

**CI (GitHub Actions):** Use `fetch-depth: 2` for diff-review, run each phase in sequence.

**Pre-Commit Hook:**
```bash
#!/bin/bash
./verification-loop.sh --skip=security,diff-review
[ $? -ne 0 ] && exit 1
```

## Metrics

| Metric | Target |
|--------|--------|
| Pass Rate | >95% |
| Duration | <60s |
| Test Coverage | >80% |

---

**Version 1.0.0** (2026-01-24): Initial release
