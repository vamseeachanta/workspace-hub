# Python Code Refactor Skill Specification

> Created: 2026-01-26
> Type: Skill Design
> Status: Planning
> Location: workspace-hub/.claude/skills/_internal/meta/python-code-refactor/
> Inspired by: mcpmarket.com/tools/skills/python-refactor

---

## Context: Existing Skills in Workspace-Hub

| Skill | Version | Scope |
|-------|---------|-------|
| module-based-refactor | v3.2.0 | Repository structure (5-layer architecture) |
| discipline-refactor | v2.0.0 | Domain-based organization |
| repo-cleanup | v2.2.0 | Artifacts and consolidation |

**Gap:** No Python code-level refactoring (complexity, OOP, type hints, documentation)

---

## Proposed: python-code-refactor Skill (v1.0.0)

### Purpose
Systematic Python code quality improvements with safety-first design, multi-dimensional metrics, and comprehensive validation.

### Key Principles (from mcpmarket skill)

1. **Safety-First** - Regression prevention is mandatory, not optional
2. **Static Analysis BEFORE Tests** - Catches NameErrors immediately
3. **Migration Checklists** - Makes incomplete refactoring structurally impossible
4. **Multi-Dimensional Metrics** - Not just one complexity measure
5. **Class-Based Architecture** - OOP transformation is non-negotiable for spaghetti code

---

## File Structure

```
.claude/skills/_internal/meta/python-code-refactor/
├── SKILL.md                    # Core skill definition
├── README.md                   # High-level overview
├── assets/
│   ├── pyproject.toml          # Ruff, Complexipy, pytest, coverage config
│   └── templates/
│       ├── analysis_template.md
│       ├── summary_template.md
│       └── flake8_report_template.md
├── scripts/
│   ├── measure_complexity.py   # AST-based cyclomatic/nesting analysis
│   ├── analyze_with_flake8.py  # Multi-plugin code quality
│   ├── compare_flake8_reports.py
│   ├── check_documentation.py  # Docstring + type hint coverage
│   ├── compare_metrics.py      # Before/after comparison
│   └── benchmark_changes.py    # Performance regression detection
└── references/
    ├── REGRESSION_PREVENTION.md
    ├── patterns.md             # Refactoring patterns catalog
    ├── anti-patterns.md        # 16 anti-pattern detection guide
    ├── cognitive_complexity_guide.md
    ├── oop_principles.md       # SOLID + OOP best practices
    └── examples/
        ├── script_to_oop.md
        └── complexity_reduction.md
```

---

## 4-Phase Workflow

### Phase 1: ANALYSIS (Read-Only)

```
1. Read entire codebase
2. Identify anti-patterns (reference: anti-patterns.md)
   - Script-like/procedural code (CRITICAL)
   - God Objects/Classes
   - Complex nesting (>3 levels)
   - Long functions (>30 lines)
   - Magic numbers, cryptic names
3. Assess OOP architecture
   - Global state organization?
   - SOLID principles compliance?
   - Dependency injection?
4. Measure metrics (measure_complexity.py)
   - Cyclomatic complexity
   - Cognitive complexity
   - Function length, nesting depth
5. Run flake8 analysis (16 plugins)
6. Check test coverage
7. Generate analysis report (analysis_template.md)
```

### Phase 2: PLANNING

```
1. Categorize changes by risk:
   ├─ LOW: Renames, docs, type hints (non-destructive)
   ├─ MEDIUM: Extract functions, guard clauses
   └─ HIGH: Remove globals, delete code (destructive)

2. For DESTRUCTIVE changes (MANDATORY):
   ├─ grep for ALL usages
   ├─ Create migration checklist
   ├─ Document every usage location
   └─ Calculate migration effort

3. Sequence: safest → riskiest
4. Define rollback plan
```

### Phase 3: EXECUTION

**For NON-DESTRUCTIVE changes:**
- Rename variables/functions
- Extract magic numbers to constants
- Add/improve docs + type hints
- Add guard clauses

**For DESTRUCTIVE changes (STRICT PROTOCOL):**

```
Step 1: CREATE new structure (no removal yet)
  └─ Write new classes/functions, add tests

Step 2: SEARCH for ALL usages
  └─ grep exact name + access patterns

Step 3: CREATE migration checklist
  └─ List all usages, track progress

Step 4: MIGRATE one at a time
  ├─ Update ONE usage
  ├─ Run: flake8 --select=F821,E0602
  ├─ Run: pytest
  ├─ Check off in list
  ├─ Commit: "refactor: migrate X to Y (N/total)"
  └─ REPEAT

Step 5: VERIFY 100% migration
  └─ Re-grep = ZERO matches

Step 6: REMOVE old code (only after verified)
  └─ Commit: "refactor: remove obsolete X"

⛔ NEVER skip migration checklist
```

### Phase 4: VALIDATION

```
1. Static analysis FIRST (before tests!)
   └─ flake8 --select=F821,E0602 = ZERO errors

2. Run full test suite
   └─ 100% pass rate required

3. Compare before/after metrics
   └─ compare_metrics.py

4. Run flake8 comparison
   └─ compare_flake8_reports.py

5. Performance regression check
   └─ benchmark_changes.py (no >10% degradation)

6. Generate summary report
   └─ summary_template.md

7. Flag for human review if:
   ├─ Performance degraded >10%
   ├─ Public API changed
   ├─ Test coverage decreased
   └─ Flake8 issues increased
```

---

## Anti-Pattern Catalog (Priority Order)

### CRITICAL (Fix First)
1. **Script-like/Procedural Code** - Global state, no OOP
2. **God Object/Class** - Too many responsibilities

### HIGH
3. Complex nested conditionals (>3 levels)
4. Long functions (>30 lines)
5. Magic numbers and strings
6. Cryptic variable names
7. Missing type hints on public APIs
8. Missing/inadequate docstrings

### MEDIUM
9. Duplicate code (DRY violation)
10. Primitive obsession
11. Long parameter lists (>5 params)
12. Mixed abstraction levels

### LOW
13. Inconsistent naming
14. Redundant comments
15. Unused imports

---

## Refactoring Patterns

### Complexity Reduction
- **Guard clauses** - Eliminate nested if/else
- **Extract method** - Split large functions (resets nesting counter)
- **Dictionary dispatch** - Replace if/elif chains (CC 8→1)
- **Match statement** - Python 3.10+ (CC +1 total, not per branch)

### OOP Transformation
- Encapsulate global state in classes
- Group related functions into classes
- Create domain models (dataclasses)
- Apply dependency injection
- Organize into layered architecture

### Naming Improvements
- Booleans: `is_`, `has_`, `can_`, `should_` prefixes
- Functions: verb + object (`calculate_total`)
- Constants: `UPPERCASE_WITH_UNDERSCORES`

---

## Tool Integration

### Ruff (Primary - 10-100x faster)
```toml
[tool.ruff]
target-version = "py311"
line-length = 88

[tool.ruff.lint]
select = ["E", "W", "F", "C90", "B", "SIM", "C4", "UP", "I", "N", "D", "RUF"]
```

### Flake8 Plugins (16 total)

**Essential (5):**
- flake8-bugbear
- flake8-simplify
- flake8-cognitive-complexity
- pep8-naming
- flake8-docstrings

**Recommended (5):**
- flake8-comprehensions
- flake8-expression-complexity
- flake8-functions
- flake8-variables-names
- tryceratops

### Validation Tools
- **Complexipy** - Cognitive complexity (max 15)
- **mypy/pyright** - Type checking
- **pytest + coverage** - Test validation (≥80%)

---

## Metric Targets

| Metric | Target | Warning |
|--------|--------|---------|
| Cyclomatic complexity | <10 | >15 |
| Cognitive complexity | <15 | >20 |
| Function length | <30 lines | >50 |
| Nesting depth | ≤3 levels | >4 |
| Docstring coverage | >80% | <60% |
| Type hint coverage | >90% | <70% |
| Test coverage | ≥80% | <70% |

---

## Safety Rules (Non-Negotiable)

1. **Pre-refactoring checklist** - Test coverage ≥80%, golden outputs captured
2. **Static analysis BEFORE tests** - Catches NameErrors immediately
3. **Validate after EVERY micro-change** - Not just at the end
4. **Migration checklists** - For all destructive changes
5. **Atomic commits** - Document progress, enable rollback
6. **Stop on ANY error** - No continuing past failures

---

## Usage

```bash
# Full refactor (all capabilities)
/python-code-refactor --all

# Analysis only (dry-run)
/python-code-refactor --analyze

# Specific operations
/python-code-refactor --complexity    # Reduce complexity
/python-code-refactor --oop           # OOP transformation
/python-code-refactor --imports       # Organize imports
/python-code-refactor --type-hints    # Add type hints
/python-code-refactor --docstrings    # Standardize docs
/python-code-refactor --modernize     # Upgrade syntax
```

---

## Implementation Plan

### Step 1: Create skill structure
Create folder at `.claude/skills/_internal/meta/python-code-refactor/`

### Step 2: Write SKILL.md
Core skill definition with 4-phase workflow

### Step 3: Create scripts/
Port validation scripts (measure_complexity.py, etc.)

### Step 4: Create references/
Anti-patterns, patterns, cognitive complexity guide

### Step 5: Create assets/
pyproject.toml template, output templates

### Step 6: Test on worldenergydata repo
Validate skill works end-to-end

---

## Sources

- [mcpmarket.com Python Refactor Skill](https://mcpmarket.com/tools/skills/python-refactor)
- [Real Python - Refactoring Guide](https://realpython.com/python-refactoring/)
- [Ruff Documentation](https://docs.astral.sh/ruff/)
- [Rope - Python Refactoring Library](https://github.com/python-rope/rope)
- [8 Python Refactoring Techniques](https://www.qodo.ai/blog/8-python-code-refactoring-techniques-tools-practices/)
