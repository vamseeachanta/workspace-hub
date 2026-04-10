# Plan 1: assetutilities Foundation Refactor

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Stabilize assetutilities as the foundation library — clean packaging, decompose monoliths, add type hints, remove stale files.

**Architecture:** Targeted edits to pyproject.toml, decomposition of 6 monolithic files into focused modules with backward-compatible re-exports, type annotation of new modules, and cleanup of stale root-level files.

**Tech Stack:** Python 3.9+, setuptools, pytest, mypy, ruff

**Repo:** `/mnt/local-analysis/workspace-hub/assetutilities`

---

### Task 1: Fix Packaging — Remove pytest from Core Dependencies

**Files:**
- Modify: `pyproject.toml` (lines 27-67 core deps, lines 70-81 dev deps)

- [ ] **Step 1: Remove pytest from core dependencies**

In `pyproject.toml`, remove `"pytest>=7.4.0"` from the `[project.dependencies]` list (approx line 50). pytest is already in both `[project.optional-dependencies.dev]` and `[project.optional-dependencies.test]`.

- [ ] **Step 2: Remove setup.py pass-through**

Delete `setup.py` (3-line pass-through file: `from setuptools import setup; setup()`). pyproject.toml with setuptools>=61.0 handles everything.

- [ ] **Step 3: Verify installation still works**

Run: `cd /mnt/local-analysis/workspace-hub/assetutilities && uv run python -c "import assetutilities; print('OK')"`
Expected: `OK`

- [ ] **Step 4: Commit**

```bash
git add pyproject.toml && git rm setup.py
git commit -m "fix(packaging): remove pytest from core deps and stale setup.py"
```

---

### Task 2: Pin Dependencies with Upper Bounds

**Files:**
- Modify: `pyproject.toml` (lines 27-67)

- [ ] **Step 1: Add upper bounds to all core dependencies**

Replace each `>=X.Y.Z` with `>=X.Y.Z,<NEXT_MAJOR`. For example:
- `"beautifulsoup4>=4.12.0"` → `"beautifulsoup4>=4.12.0,<5.0.0"`
- `"flask>=3.0.0"` → `"flask>=3.0.0,<4.0.0"`
- `"numpy>=1.24.0"` → `"numpy>=1.24.0,<3.0.0"`
- `"pandas>=2.1.0"` → `"pandas>=2.1.0,<3.0.0"`
- Keep `"pint>=0.23,<1.0"` as-is (already has upper bound)

Apply this pattern to all 36 dependencies that lack upper bounds. Use `<NEXT_MAJOR` for each (e.g., `>=3.1.40` → `>=3.1.40,<4.0.0`).

- [ ] **Step 2: Fix black target-version**

In `[tool.black]` (line 117-120), change:
```toml
target-version = ['py39', 'py310', 'py311', 'py312']
```
(Remove py38 since requires-python is >=3.9, add py312)

- [ ] **Step 3: Verify dependency resolution**

Run: `cd /mnt/local-analysis/workspace-hub/assetutilities && uv lock --check 2>&1 | tail -5`
If lock file is stale, run: `uv lock`

- [ ] **Step 4: Run tests to verify nothing broke**

Run: `cd /mnt/local-analysis/workspace-hub/assetutilities && uv run pytest tests/ -x -q --tb=short 2>&1 | tail -20`
Expected: 1235 passed

- [ ] **Step 5: Commit**

```bash
git add pyproject.toml uv.lock
git commit -m "fix(packaging): pin all dependencies with upper bounds, fix black target"
```

---

### Task 3: Decompose common/data.py into Focused Modules

**Files:**
- Modify: `src/assetutilities/common/data.py` (1217 lines → slim re-export file)
- Create: `src/assetutilities/common/readers/__init__.py`
- Create: `src/assetutilities/common/readers/excel_reader.py`
- Create: `src/assetutilities/common/readers/csv_reader.py`
- Create: `src/assetutilities/common/readers/data_reader.py`
- Create: `src/assetutilities/common/readers/data_getter.py`
- Create: `src/assetutilities/common/writers.py`
- Create: `src/assetutilities/common/transform.py`
- Create: `src/assetutilities/common/attribute_dict.py`
- Create: `src/assetutilities/common/datetime_utils.py`
- Create: `src/assetutilities/common/string_utils.py`
- Create: `src/assetutilities/common/number_format.py`
- Create: `src/assetutilities/common/file_ops.py`

**Current classes in data.py:**
- Line 23: `ReadFromExcel` → `readers/excel_reader.py`
- Line 53: `ReadFromCSV` → `readers/csv_reader.py`
- Line 64: `ReadData` → `readers/data_reader.py`
- Line 402: `GetData` → `readers/data_getter.py`
- Line 432: `FromString` → `string_utils.py`
- Line 483: `SaveData` → `writers.py`
- Line 739: `DefineData` → `readers/data_reader.py` (alongside ReadData)
- Line 757: `AttributeDict` → `attribute_dict.py`
- Line 763: `objdict` → `attribute_dict.py`
- Line 781: `DateTimeUtility` → `datetime_utils.py`
- Line 792: `Transform` → `transform.py`
- Line 1071: `TransformData` → `transform.py`
- Line 1091: `TransferDataFromExcelToWord` → `file_ops.py`
- Line 1141: `PandasChainedAssignent` → `transform.py`
- Line 1177: `CopyAndPasteFiles` → `file_ops.py`
- Line 1207: `NumberFormat` → `number_format.py`

Also move standalone function `transform_df_datetime_to_str` → `datetime_utils.py`

- [ ] **Step 1: Create readers/ subpackage**

Create `src/assetutilities/common/readers/__init__.py`:
```python
"""Data reader classes — extracted from common/data.py."""

from assetutilities.common.readers.csv_reader import ReadFromCSV
from assetutilities.common.readers.data_getter import GetData
from assetutilities.common.readers.data_reader import DefineData, ReadData
from assetutilities.common.readers.excel_reader import ReadFromExcel

__all__ = [
    "ReadFromExcel",
    "ReadFromCSV",
    "ReadData",
    "DefineData",
    "GetData",
]
```

- [ ] **Step 2: Extract each class into its target module**

For each target file, copy the class definition and its required imports from data.py. Each file should have only the imports it needs. Add type hints to function signatures as you extract.

Key extraction pattern — for each new file:
1. Copy the class and its methods
2. Copy only the imports that class uses
3. Add return type annotations and parameter types
4. Add a module docstring

- [ ] **Step 3: Create backward-compatible data.py with re-exports**

Replace data.py content with:
```python
"""Backward-compatible re-exports from decomposed modules.

All classes have been moved to focused modules under common/.
Import from the new locations for new code.
"""

from assetutilities.common.attribute_dict import AttributeDict, objdict
from assetutilities.common.datetime_utils import DateTimeUtility, transform_df_datetime_to_str
from assetutilities.common.file_ops import CopyAndPasteFiles, TransferDataFromExcelToWord
from assetutilities.common.number_format import NumberFormat
from assetutilities.common.readers import DefineData, GetData, ReadData, ReadFromCSV, ReadFromExcel
from assetutilities.common.string_utils import FromString
from assetutilities.common.transform import PandasChainedAssignent, Transform, TransformData
from assetutilities.common.writers import SaveData

__all__ = [
    "AttributeDict",
    "CopyAndPasteFiles",
    "DateTimeUtility",
    "DefineData",
    "FromString",
    "GetData",
    "NumberFormat",
    "PandasChainedAssignent",
    "ReadData",
    "ReadFromCSV",
    "ReadFromExcel",
    "SaveData",
    "Transform",
    "TransformData",
    "TransferDataFromExcelToWord",
    "objdict",
    "transform_df_datetime_to_str",
]
```

- [ ] **Step 4: Remove mypy override for data.py**

In pyproject.toml, remove the `[[tool.mypy.overrides]]` section for `assetutilities.common.data` (lines 132-140). The new modules will be properly typed.

- [ ] **Step 5: Run tests to verify backward compatibility**

Run: `cd /mnt/local-analysis/workspace-hub/assetutilities && uv run pytest tests/unit/test_common_data.py -v --tb=short 2>&1 | tail -30`
Expected: All tests pass — imports are unchanged from test perspective.

Run: `cd /mnt/local-analysis/workspace-hub/assetutilities && uv run pytest tests/ -x -q --tb=short 2>&1 | tail -10`
Expected: 1235 passed

- [ ] **Step 6: Commit**

```bash
git add src/assetutilities/common/readers/ src/assetutilities/common/writers.py \
  src/assetutilities/common/transform.py src/assetutilities/common/attribute_dict.py \
  src/assetutilities/common/datetime_utils.py src/assetutilities/common/string_utils.py \
  src/assetutilities/common/number_format.py src/assetutilities/common/file_ops.py \
  src/assetutilities/common/data.py pyproject.toml
git commit -m "refactor(common): decompose data.py into focused typed modules

Extracted 16 classes from 1217-line monolith into 8 focused modules.
Backward-compatible re-exports preserved in data.py.
Removed mypy override — new modules are properly typed."
```

---

### Task 4: Decompose agent_os/commands/ Monoliths

**Files:**
- Modify: `src/assetutilities/agent_os/commands/context_optimization.py` (1099 lines → re-export hub)
- Create: `src/assetutilities/agent_os/commands/context/` subpackage
- Modify: `src/assetutilities/agent_os/commands/specs_integration.py` (1026 lines → re-export hub)
- Create: `src/assetutilities/agent_os/commands/specs/` subpackage
- Modify: `src/assetutilities/agent_os/commands/template_management.py` (1068 lines → re-export hub)
- Create: `src/assetutilities/agent_os/commands/templates/` subpackage
- Modify: `src/assetutilities/agent_os/commands/documentation_integration.py` (901 lines → re-export hub)
- Create: `src/assetutilities/agent_os/commands/docs/` subpackage
- Modify: `src/assetutilities/agent_os/commands/cli.py` (1071 lines → re-export hub)
- Create: `src/assetutilities/agent_os/commands/cli_components/` subpackage

Each monolith follows the same pattern:
1. Identify logical groupings (already mapped in exploration)
2. Extract each group to its own file in a subpackage
3. Replace original file with re-exports for backward compatibility
4. Verify tests pass

**Decomposition map:**

**context_optimization.py → context/**
- `chunking.py`: DocumentChunk, Pattern, Concept, APISignature, DocumentChunker (lines 33-265)
- `processor.py`: ContextProcessor (lines 266-555)
- `embedding.py`: EmbeddingGenerator, ContextCache, SemanticSearch (lines 556-932)
- `optimizer.py`: OptimizedContext (lines 933+)

**specs_integration.py → specs/**
- `models.py`: OperationResult, WorkflowHook, EnhancedSpecsConfig (lines 18-104)
- `tracker.py`: PromptEvolutionTracker (lines 105-401)
- `referencer.py`: CrossRepositoryReferencer (lines 402-568)
- `refresher.py`: WorkflowRefresher (lines 569-736)
- `manager.py`: SpecsIntegrationManager (lines 737+)

**template_management.py → templates/**
- `models.py`: ValidationResult, OperationResult, Capabilities, ContextSources, Template (lines 17-121)
- `validator.py`: TemplateValidator (lines 122-332)
- `registry.py`: TemplateRegistry (lines 333-514)
- `composer.py`: TemplateComposer (lines 515-684)
- `instantiator.py`: TemplateInstantiator (lines 685-827)
- `manager.py`: TemplateManager (lines 828+)

**documentation_integration.py → docs/**
- `scanner.py`: DocumentReference, RepositoryDocumentationScanner (lines 19-211)
- `linker.py`: ExternalDocumentationLinker (lines 212-393)
- `references.py`: ReferenceManager (lines 394-582)
- `processor.py`: DocumentationProcessor (lines 583-756)
- `parser.py`: MarkdownParser (lines 757+)

**cli.py → cli_components/**
- `models.py`: ValidationResult, ParsedCommand, ErrorResult (lines 19-46)
- `manager.py`: CLIManager (lines 47-270)
- `interactive.py`: InteractiveMode (lines 271-438)
- `progress.py`: ProgressIndicator (lines 439-537)
- `help_system.py`: HelpSystem (lines 538-676)
- `error_handler.py`: ErrorHandler (lines 677-802)
- `interface.py`: CommandLineInterface + main() (lines 803+)

- [ ] **Step 1: Decompose context_optimization.py**

Create `src/assetutilities/agent_os/commands/context/__init__.py` with re-exports. Extract 4 modules. Replace original with re-exports.

- [ ] **Step 2: Run tests for context_optimization**

Run: `cd /mnt/local-analysis/workspace-hub/assetutilities && uv run pytest tests/agent_os/commands/test_context_optimization.py -v --tb=short`
Expected: PASS

- [ ] **Step 3: Commit context_optimization decomposition**

```bash
git add src/assetutilities/agent_os/commands/context/ src/assetutilities/agent_os/commands/context_optimization.py
git commit -m "refactor(agent_os): decompose context_optimization into 4 focused modules"
```

- [ ] **Step 4-6: Repeat for specs_integration → specs/**
- [ ] **Step 7-9: Repeat for template_management → templates/**
- [ ] **Step 10-12: Repeat for documentation_integration → docs/**
- [ ] **Step 13-15: Repeat for cli.py → cli_components/**

Each decomposition follows the same 3-step pattern: extract → test → commit.

- [ ] **Step 16: Run full test suite**

Run: `cd /mnt/local-analysis/workspace-hub/assetutilities && uv run pytest tests/ -x -q --tb=short 2>&1 | tail -10`
Expected: 1235 passed

---

### Task 5: Delete Stale Root Files

**Files:**
- Delete: `GLOBAL_SETUP_COMPLETE.md`
- Delete: `GLOBAL_UV_ENVIRONMENT.md`
- Delete: `UV_SETUP.md`
- Delete: `CLAUDE.md.backup-20251023-081047` (if exists)

Note: Other root files (DEPLOYMENT_SUMMARY.md, TEST_PATH_RESOLUTION_FIX.md, etc.) were not confirmed to exist — only delete what's confirmed present.

- [ ] **Step 1: Remove confirmed stale files**

```bash
cd /mnt/local-analysis/workspace-hub/assetutilities
git rm GLOBAL_SETUP_COMPLETE.md GLOBAL_UV_ENVIRONMENT.md UV_SETUP.md
# Only if backup exists:
git rm "CLAUDE.md.backup-20251023-081047" 2>/dev/null || true
```

- [ ] **Step 2: Commit**

```bash
git commit -m "chore: remove stale root-level documentation files"
```

---

### Task 6: Final Verification

- [ ] **Step 1: Run full test suite**

```bash
cd /mnt/local-analysis/workspace-hub/assetutilities
uv run pytest tests/ -q --tb=short 2>&1 | tail -15
```
Expected: 1235 passed, 0 failed

- [ ] **Step 2: Run mypy**

```bash
cd /mnt/local-analysis/workspace-hub/assetutilities
uv run mypy src/assetutilities/common/ --ignore-missing-imports 2>&1 | tail -20
```
Expected: No errors in decomposed modules

- [ ] **Step 3: Verify imports work from downstream**

```bash
cd /mnt/local-analysis/workspace-hub/assetutilities
uv run python -c "
from assetutilities.common.data import ReadData, SaveData, Transform, AttributeDict
from assetutilities.common.readers import ReadFromExcel, ReadFromCSV
from assetutilities.common.writers import SaveData as SD2
from assetutilities.common.transform import Transform as T2
print('All imports OK')
"
```
Expected: `All imports OK`
