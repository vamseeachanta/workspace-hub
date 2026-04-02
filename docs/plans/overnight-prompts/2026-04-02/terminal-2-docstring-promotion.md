# Terminal 2 — Docstring Uplift: DEVELOPMENT → PRODUCTION Promotion

Provider: **Codex seat 1** (bounded implementation, systematic file-by-file work)
Issues: #1587, #1602

---

We are in /mnt/local-analysis/workspace-hub. Execute these 3 tasks in order.
Use `uv run` for all Python — never bare python3. Commit to main and push after each task.
Do not branch. TDD: write tests before implementation where applicable.
Do NOT ask the user any questions. Run `git pull origin main` before every push.

IMPORTANT: Do NOT write to scripts/solver/, digitalmodel/tests/orcaflex/,
digitalmodel/tests/solver/, scripts/analysis/, scripts/docs/,
scripts/document-intelligence/, docs/architecture/, docs/roadmaps/,
docs/dashboards/, docs/document-intelligence/, digitalmodel/tests/web/,
digitalmodel/tests/orcawave/ — those are owned by other terminals.
Only write to: digitalmodel/src/digitalmodel/structural/,
digitalmodel/src/digitalmodel/subsea/, digitalmodel/src/digitalmodel/asset_integrity/,
digitalmodel/src/digitalmodel/naval_architecture/,
digitalmodel/src/digitalmodel/production_engineering/,
digitalmodel/src/digitalmodel/well/, digitalmodel/src/digitalmodel/ansys/.

---

## TASK 1: Docstring Uplift — structural package (191 files, 37% → 55%+)

**Context**: The module status matrix shows `structural` at 37% docstring coverage.
PRODUCTION requires >50%. That means adding module-level docstrings to ~25 more files.

**Approach**:
1. Run: `find digitalmodel/src/digitalmodel/structural/ -name '*.py' -not -name '__init__.py' -exec grep -L '"""' {} \;`
   to find files without docstrings
2. For each file missing a module-level docstring, add a concise 1-3 line docstring
   at the top of the file (after any imports preamble, following the shebang/encoding if present)
3. The docstring should describe what the module does based on its class/function names
4. Format: `"""Module description — what it contains and its purpose."""`
5. Do NOT change any logic, imports, or function signatures — only add docstrings

**Acceptance criteria**:
- At least 25 files in structural/ get new module-level docstrings
- Docstring coverage reaches >50%
- All existing tests still pass: `uv run pytest digitalmodel/tests/structural/ -v` (if tests exist)
- No functional code changes

**Commit message**: `docs(structural): add module docstrings — 37% → 55%+ coverage (#1587)`

---

## TASK 2: Docstring Uplift — subsea package (65 files, 28% → 55%+)

**Context**: `subsea` has 28% docstring coverage. Need ~18 more files with docstrings.

**Approach**: Same as Task 1 — find files without docstrings, add module-level docstrings.

**Acceptance criteria**:
- At least 18 files in subsea/ get new module-level docstrings
- Coverage reaches >50%
- Existing tests still pass: `uv run pytest digitalmodel/tests/subsea/ -v`
- No functional code changes

**Commit message**: `docs(subsea): add module docstrings — 28% → 55%+ coverage (#1587)`

---

## TASK 3: Docstring Uplift — asset_integrity + naval_architecture + production_engineering + well + ansys

**Context**: These 5 smaller packages all have 0-21% docstring coverage. Batch them together.

| Package | Files | Current % | Target Files |
|---------|------:|----------:|-------------:|
| asset_integrity | 52 | 21% | ~17 files |
| naval_architecture | 21 | 5% | ~9 files |
| production_engineering | 8 | 0% | ~5 files |
| well | 7 | 0% | ~4 files |
| ansys | 5 | 0% | ~3 files |

**Approach**: Same as Task 1 for each package.

**Acceptance criteria**:
- All 5 packages reach >50% docstring coverage
- All existing tests still pass for each package
- No functional code changes
- Total: ~38 files get new module-level docstrings

**Commit message**: `docs(multi): docstring uplift for 5 packages — all above 50% (#1587, #1602)`

---

Post a brief progress comment on GH issues #1587, #1602 when complete.
