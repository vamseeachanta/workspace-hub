Reading prompt from stdin...
OpenAI Codex v0.112.0 (research preview)
--------
workdir: /mnt/local-analysis/workspace-hub
model: gpt-5.4
provider: openai
approval: never
sandbox: workspace-write [workdir, /tmp, $TMPDIR, /home/vamsee/.codex/memories]
reasoning effort: medium
reasoning summaries: none
session id: 019cd928-4a3b-7e93-9b99-08edee109936
--------
user
Review this WRK-1071 plan draft for a performance benchmark harness. The plan adds pytest-benchmark to assetutilities (riser/fatigue calcs), digitalmodel (CP + wall thickness), and worldenergydata (EIA aggregations). Focus on: 1) Implementation edge cases (missing baseline, pytest path issues, worldenergydata optional-dev group activation), 2) AC gaps in the 5 TDD tests, 3) cron environment variables issue (REPO_ROOT expansion in crontab), 4) Integration risks. Output a refined plan plus a 'Review Notes' section with verdict APPROVE, MINOR, or MAJOR.

PLAN:
---
wrk_id: WRK-1071
title: "feat(harness): performance benchmark harness — regression detection for engineering calculations"
domain: harness/performance-profiling
complexity: medium
route: B
created_at: 2026-03-10
target_repos: [assetutilities, digitalmodel, worldenergydata]
status: draft
version: "1.0"
---

## Mission

Establish performance baselines for compute-heavy engineering calculations so
regressions are caught before they reach production reports.

## Phase 1 — pytest-benchmark integration (TDD first)

**Tests first** (`scripts/testing/test_run_benchmarks.py`, 5 tests):
- `test_run_benchmarks_all_repos_exit_zero` — script returns 0 on clean run
- `test_run_benchmarks_single_repo` — `--repo assetutilities` runs only that suite
- `test_save_baseline_writes_json` — `--save-baseline` writes `config/testing/benchmark-baseline.json`
- `test_regression_detection_flags_slowdown` — injected 25% slowdown → exit 1
- `test_no_regression_passes` — baseline-equal result → exit 0

**assetutilities**:
- Add `pytest-benchmark>=4.0.0,<5.0.0` to `[dependency-groups].test`
- Create `assetutilities/tests/benchmarks/__init__.py`
- Create `assetutilities/tests/benchmarks/test_scr_fatigue_benchmarks.py`
  - `bench_keulegan_carpenter_number(benchmark)` — synthetic (D, U, T) inputs
  - `bench_soil_interaction_fatigue_factor(benchmark)` — synthetic soil profile

Note: assetutilities CP calcs live in digitalmodel. assetutilities targets
riser/fatigue calcs (`scr_fatigue.py`) — `keulegan_carpenter_number`, `soil_interaction_fatigue_factor`.

**digitalmodel** (pytest-benchmark already installed; `tests/benchmarks/` exists):
- Create `digitalmodel/tests/benchmarks/test_cp_benchmarks.py`
  - `bench_cp_router_abs_gn_ships(benchmark)` — DNV_RP_F103_2010 cfg dict
  - `bench_cp_router_all_routes(benchmark)` — parametrize over all 4 methods
- Create `digitalmodel/tests/benchmarks/test_wall_thickness_benchmarks.py`
  - `bench_wall_thickness_dnv(benchmark)` — synthetic DNV-ST-F101 input

Import path: `from digitalmodel.infrastructure.base_solvers.hydrodynamics.cathodic_protection import CathodicProtection`
(not the deprecated `infrastructure.common` shim)

**worldenergydata** (pytest-benchmark in optional-dev; `tests/performance/` has conftest):
- Create `worldenergydata/tests/benchmarks/__init__.py`
- Create `worldenergydata/tests/benchmarks/test_eia_benchmarks.py`
  - Reuse `tests/performance/conftest.py` BenchmarkFixture setup
  - `bench_state_production_loader(benchmark)` — 1000 synthetic EIA records
  - `bench_basin_production_loader(benchmark)` — 500 synthetic basin records

## Phase 2 — run-benchmarks.sh + baseline tooling

**`scripts/testing/run-benchmarks.sh`** (modelled on `run-all-tests.sh` from WRK-1054):
```
REPOS = [
  {name: assetutilities, dir: assetutilities, pythonpath: src, benchmark_dir: tests/benchmarks},
  {name: digitalmodel, dir: digitalmodel, pythonpath: src, benchmark_dir: tests/benchmarks},
  {name: worldenergydata, dir: worldenergydata, pythonpath: "src:../assetutilities/src", benchmark_dir: tests/benchmarks},
]
```
- Per-repo: `uv run python -m pytest <benchmark_dir> --benchmark-only --benchmark-json=<tmp> -q`
- Collect results → `scripts/testing/benchmark-results/benchmark-YYYY-MM-DD.json`
- `--repo <name>` — single-repo run
- `--save-baseline` — writes `config/testing/benchmark-baseline.json` from latest run
- `--no-compare` — skips comparison (bootstrap / first run)
- Default compare mode: reads baseline, flags any mean >20% slower as REGRESSION (exit 1)

**`scripts/testing/parse_benchmark_output.py`**:
- Reads pytest-benchmark JSON; compares means against baseline
- Prints regression table; exits 1 if any regression found

`.gitignore`: add `scripts/testing/benchmark-results/` (runtime artifacts)

## Phase 3 — cron + integration

- Add weekly cron entry to `scripts/cron/crontab-template.sh`:
  `0 4 * * 0 <REPO_ROOT>/scripts/testing/run-benchmarks.sh >> logs/quality/benchmark-cron.log 2>&1`
- Bootstrap baseline: `./scripts/testing/run-benchmarks.sh --save-baseline --no-compare`
- `config/testing/benchmark-baseline.json` committed from initial run

## Test Strategy

| Layer | What | When |
|-------|------|------|
| TDD harness | 5 tests in `test_run_benchmarks.py` | Before implementation |
| Unit (benchmark) | Each `bench_*` function runs without error | Each commit |
| Integration | `run-benchmarks.sh` exits 0 | Before merge |
| Regression gate | >20% slowdown = exit 1 | Weekly cron + pre-merge |

## Risks

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| worldenergydata pytest-benchmark only in optional-dev deps | Medium | Medium | Verify `uv run` activates group; add to `[dependency-groups].benchmark` if needed |
| Benchmark variance causing false positives | Medium | Low | Use `--benchmark-min-rounds=5`; flag only >20% (not >5%) |
| assetutilities test path is `src/assetutilities/tests/` not root `tests/` | Low | Medium | Create `tests/benchmarks/` at repo root; update pytest config if needed |
| CP calcs location mismatch in WRK body | Confirmed | Fixed | Plan explicitly targets digitalmodel for CP; assetutilities targets scr_fatigue.py |

## Out of Scope

- Benchmark results dashboard (WRK-1057 repo-health integration — follow-on)
- assethold / ogmanufacturing benchmarks (no heavy calc modules identified)
- Historical regression tracking beyond baseline comparison

mcp startup: no servers
codex
Using `work-queue-workflow` and `workflow-gatepass` for the WRK review context, plus a code-review pass against the draft. I’m checking the current repo layout and harness patterns first so the review is tied to the actual workspace rather than the plan text alone.
exec
/bin/bash -lc "rg --files | rg 'run-all-tests\\.sh|run-benchmarks\\.sh|parse_benchmark_output\\.py|crontab-template\\.sh|test_run_benchmarks\\.py|pytest\\.ini|pyproject\\.toml"'$'"'" in /mnt/local-analysis/workspace-hubexec
/bin/bash -lc "rg --files .claude/work-queue | rg 'WRK-1071|INDEX.md'" in /mnt/local-analysis/workspace-hubexec
/bin/bash -lc "rg -n \"pytest-benchmark|tests/benchmarks|tests/performance|dependency-groups|optional-dev|benchmark\" assetutilities digitalmodel worldenergydata scripts -g 'pyproject.toml' -g 'pytest.ini' -g 'conftest.py' -g '*.sh' -g '*.py'" in /mnt/local-analysis/workspace-hubcodex
I’ve got the first grep back; the benchmark harness pieces mostly don’t exist yet, so I’m validating the target repos’ current layouts and dependency definitions next. That matters for the path and optional-dependency risks in the draft.
 succeeded in 22.96s:
.claude/work-queue/INDEX.md
.claude/work-queue/pending/WRK-1071.md
.claude/work-queue/assets/WRK-1071/WRK-1071-plan-draft.html
.claude/work-queue/assets/WRK-1071/WRK-1071-lifecycle.html
.claude/work-queue/assets/WRK-1071/stage-4-prompt.md
.claude/work-queue/assets/WRK-1071/stage-3-prompt.md
.claude/work-queue/assets/WRK-1071/stage-2-prompt.md
.claude/work-queue/assets/WRK-1071/plan_gemini.md
.claude/work-queue/assets/WRK-1071/plan_codex.md
.claude/work-queue/assets/WRK-1071/plan_claude.md
.claude/work-queue/assets/WRK-1071/evidence/user-review-plan-draft.yaml
.claude/work-queue/assets/WRK-1071/evidence/user-review-common-draft.yaml
.claude/work-queue/assets/WRK-1071/evidence/user-review-capture.yaml
.claude/work-queue/assets/WRK-1071/evidence/session-lock.yaml
.claude/work-queue/assets/WRK-1071/evidence/resource-intelligence.yaml
.claude/work-queue/assets/WRK-1071/checkpoint.yaml
codex
The initial file scans were too broad to be useful. I’m narrowing to the specific repos and files the draft depends on so the review can call out concrete breakpoints instead of generic concerns.
exec
/bin/bash -lc "find assetutilities digitalmodel worldenergydata -maxdepth 3 \\( -name pyproject.toml -o -name pytest.ini -o -path '*/tests' -o -path '*/tests/benchmarks' -o -path '*/tests/performance' \\) | sort" in /mnt/local-analysis/workspace-hubexec
/bin/bash -lc "find .claude/work-queue -maxdepth 2 -type f | rg 'WRK-1071|INDEX.md'" in /mnt/local-analysis/workspace-hubexec
/bin/bash -lc "rg -n \"pytest-benchmark|optional-dev|dependency-groups|tool\\.uv|\\[project\\.optional-dependencies\\]|benchmark\" assetutilities/pyproject.toml digitalmodel/pyproject.toml worldenergydata/pyproject.toml assetutilities/pytest.ini digitalmodel/pytest.ini worldenergydata/pytest.ini worldenergydata/tests/performance/conftest.py digitalmodel/tests/conftest.py assetutilities/tests/conftest.py" in /mnt/local-analysis/workspace-hub succeeded in 280ms:
digitalmodel/pytest.ini:19:    benchmark: Performance benchmark tests
worldenergydata/pytest.ini:20:    performance: Performance and benchmark tests
worldenergydata/pytest.ini:21:    benchmark: Benchmark performance tests
worldenergydata/pyproject.toml:62:[project.optional-dependencies]
worldenergydata/pyproject.toml:67:    "pytest-benchmark>=4.0",
worldenergydata/pyproject.toml:172:[tool.uv]
worldenergydata/pyproject.toml:179:[tool.uv.pip]
worldenergydata/pyproject.toml:208:[dependency-groups]
digitalmodel/pyproject.toml:114:    "pytest-benchmark>=4.0.0,<5.0.0", # Performance benchmarking
digitalmodel/pyproject.toml:172:[project.optional-dependencies]
digitalmodel/pyproject.toml:260:    "benchmark: marks tests as performance benchmarks",
digitalmodel/pyproject.toml:332:[tool.pytest-benchmark]
digitalmodel/pyproject.toml:351:[tool.uv]
digitalmodel/pyproject.toml:358:[tool.uv.pip]
digitalmodel/pyproject.toml:364:[tool.uv.sources]
digitalmodel/pyproject.toml:367:[tool.uv.workspace]
digitalmodel/pyproject.toml:393:[dependency-groups]
assetutilities/pyproject.toml:69:[project.optional-dependencies]
assetutilities/pyproject.toml:162:[tool.uv]
assetutilities/pyproject.toml:166:[dependency-groups]
 succeeded in 5.34s:
.claude/work-queue/INDEX.md
.claude/work-queue/logs/WRK-1071-1.log
.claude/work-queue/logs/WRK-1071-2.log
.claude/work-queue/logs/WRK-1071-3.log
.claude/work-queue/logs/WRK-1071-4.log
.claude/work-queue/pending/WRK-1071.md
exec
/bin/bash -lc "find .claude/work-queue -maxdepth 2 -type f | sort | rg 'WRK-1071|INDEX.md'" in /mnt/local-analysis/workspace-hubexec
/bin/bash -lc "find assetutilities digitalmodel worldenergydata -maxdepth 3 \\( -name pyproject.toml -o -name pytest.ini -o -type d -path '*/tests' -o -type d -path '*/tests/benchmarks' -o -type d -path '*/tests/performance' \\) | sort" in /mnt/local-analysis/workspace-hub succeeded in 4.02s:
.claude/work-queue/INDEX.md
.claude/work-queue/logs/WRK-1071-1.log
.claude/work-queue/logs/WRK-1071-2.log
.claude/work-queue/logs/WRK-1071-3.log
.claude/work-queue/logs/WRK-1071-4.log
.claude/work-queue/pending/WRK-1071.md
 succeeded in 17.55s:
assetutilities/pyproject.toml
assetutilities/pytest.ini
assetutilities/src/assetutilities/tests
assetutilities/tests
digitalmodel/pyproject.toml
digitalmodel/pytest.ini
digitalmodel/tests
digitalmodel/tests/benchmarks
digitalmodel/tests/performance
worldenergydata/pyproject.toml
worldenergydata/pytest.ini
worldenergydata/tests
worldenergydata/tests/performance
worldenergydata/tests/pytest.ini
 succeeded in 54.02s:
scripts/_archive/phase1-setup.sh:78:uv pip install --quiet pytest pytest-cov pytest-mock pytest-asyncio pytest-benchmark
scripts/_archive/phase1-setup.sh:190:- [ ] Wednesday: Performance benchmarking
scripts/_archive/phase1-setup.sh:270:  - Performance benchmarks acceptable
scripts/_archive/phase1-setup.sh:340:- [ ] Set performance benchmarking tools
scripts/notify.sh:5:#   source:  cron | ci | benchmark
scripts/notify.sh:15:#   - WRK-1071 (benchmark runner): call on regression/clean
scripts/hooks/tests/test-session-start-notify.sh:63:echo "{\"source\":\"benchmark\",\"job\":\"digitalmodel\",\"status\":\"fail\",\"ts\":\"${NOW}\",\"details\":\"+35% regression\"}" \
scripts/work-queue/assign-providers.sh:34:    "WRK-031:claude"        # OrcaWave vs AQWA benchmark — complex analysis
scripts/work-queue/assign-providers.sh:36:    "WRK-039:claude"        # SPM benchmarking — complex analysis
scripts/work-queue/assign-providers.sh:44:    "WRK-099:claude"        # 3-way benchmark — analysis + debugging
scripts/work-queue/assign-providers.sh:62:    "WRK-132:codex:claude"  # OrcaWave benchmarks — code + domain
scripts/utilities/doc-to-context/src/unified_cli.py:41:  %(prog)s /docs -o /output --mode benchmark --recursive
scripts/utilities/doc-to-context/src/unified_cli.py:57:    parser.add_argument('--mode', choices=['sequential', 'parallel', 'swarm', 'benchmark'],
scripts/utilities/doc-to-context/src/unified_cli.py:112:    if args.mode == 'benchmark':
scripts/utilities/doc-to-context/src/unified_cli.py:113:        run_benchmark(args)
scripts/utilities/doc-to-context/src/unified_cli.py:196:def run_benchmark(args):
scripts/utilities/doc-to-context/src/unified_cli.py:265:    print_benchmark_results(results)
scripts/utilities/doc-to-context/src/unified_cli.py:268:def print_benchmark_results(results):
scripts/utilities/doc-to-context/src/unified_cli.py:269:    """Print benchmark comparison."""
scripts/utilities/doc-to-context/examples/quick_start.sh:48:echo "  $DOC_CONVERTER /docs -o /output --mode benchmark --recursive"
 succeeded in 10.19s:
assetutilities/pyproject.toml
assetutilities/pytest.ini
assetutilities/src/assetutilities/tests
assetutilities/tests
digitalmodel/pyproject.toml
digitalmodel/pytest.ini
digitalmodel/tests
digitalmodel/tests/benchmarks
digitalmodel/tests/performance
worldenergydata/pyproject.toml
worldenergydata/pytest.ini
worldenergydata/tests
worldenergydata/tests/performance
worldenergydata/tests/pytest.ini
 succeeded in 57.47s:
coordination/pyproject.toml
frontierdeepwater/pytest.ini
frontierdeepwater/pyproject.toml
sabithaandkrishnaestates/pyproject.toml
aceengineer-website/pyproject.toml
aceengineer-admin/pyproject.toml
teamresumes/pytest.ini
teamresumes/pyproject.toml
digitalmodel/tests/workflows/integration/pytest.ini
seanation/pytest.ini
seanation/pyproject.toml
hobbies/pyproject.toml
doris/pytest.ini
doris/pyproject.toml
sd-work/pyproject.toml
scripts/testing/run-all-tests.sh
docs/templates/pytest.ini
docs/modules/testing/testing-templates/pytest.ini.template
CAD-DEVELOPMENTS/docs/templates/pytest.ini
docs/modules/environment/uv-templates/pyproject.toml
codex
The structure check confirms one key edge case already: `assetutilities` has both `tests/` and `src/assetutilities/tests/`, while `digitalmodel` already has a benchmark lane and `worldenergydata` keeps benchmark support under optional dependencies. I’m pulling the exact config now so the refined plan can be specific about import paths, uv flags, and baseline semantics.
exec
/bin/bash -lc "sed -n '1,260p' worldenergydata/pyproject.toml" in /mnt/local-analysis/workspace-hubexec
/bin/bash -lc "sed -n '1,260p' assetutilities/pyproject.toml" in /mnt/local-analysis/workspace-hubexec
/bin/bash -lc "sed -n '1,220p' .claude/work-queue/pending/WRK-1071.md" in /mnt/local-analysis/workspace-hubexec
/bin/bash -lc "sed -n '1,260p' digitalmodel/pyproject.toml" in /mnt/local-analysis/workspace-hub succeeded in 51ms:
[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "worldenergydata"
version = "0.1.0"
description = "Standardized project configuration for worldenergydata"
readme = "README.md"
requires-python = ">=3.9"
license = {text = "MIT"}
authors = [
    {name = "Development Team", email = "dev@example.com"}
]
classifiers = [
    "Development Status :: 3 - Alpha",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.9",
 succeeded in 50ms:
---
id: WRK-1071
title: "feat(harness): performance benchmark harness — regression detection for engineering calculations"
status: pending
priority: medium
complexity: medium
route: B
created_at: 2026-03-09
computer: ace-linux-1
orchestrator: claude
plan_workstations: [ace-linux-1]
execution_workstations: [ace-linux-1]
category: harness
subcategory: performance-profiling
related: [WRK-1054]
target_repos: [assetutilities, digitalmodel, worldenergydata]
html_output_ref: ".claude/work-queue/assets/WRK-1071/WRK-1071-lifecycle.html"
plan_html_review_draft_ref: ".claude/work-queue/assets/WRK-1071/WRK-1071-plan-draft.html"
plan_html_review_final_ref: ".claude/work-queue/assets/WRK-1071/WRK-1071-plan-final.html"
plan_approved: false
 succeeded in 51ms:
[build-system]
requires = ["setuptools>=68.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "assetutilities"
version = "0.1.0"
description = "Standardized project configuration for assetutilities"
readme = "README.md"
requires-python = ">=3.9"
license = {text = "MIT"}
authors = [
    {name = "Development Team", email = "dev@example.com"}
]
classifiers = [
    "Development Status :: 3 - Alpha",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.9",
 succeeded in 51ms:
[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "digitalmodel"
version = "0.1.0"
description = "Standardized project configuration for digitalmodel"
readme = "README.md"
requires-python = ">=3.10"
license = {text = "MIT"}
authors = [
    {name = "Development Team", email = "dev@example.com"}
]
classifiers = [
    "Development Status :: 3 - Alpha",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.9",
exec
/bin/bash -lc "sed -n '260,430p' digitalmodel/pyproject.toml" in /mnt/local-analysis/workspace-hubexec
/bin/bash -lc "sed -n '1,220p' worldenergydata/tests/performance/conftest.py" in /mnt/local-analysis/workspace-hubexec
/bin/bash -lc "sed -n '1,220p' scripts/cron/crontab-template.sh" in /mnt/local-analysis/workspace-hubexec
/bin/bash -lc "sed -n '1,260p' scripts/testing/run-all-tests.sh" in /mnt/local-analysis/workspace-hub succeeded in 50ms:
"""
Performance Testing Configuration

This module configures pytest-benchmark for performance testing of worldenergydata.
"""

import random
import string
from datetime import datetime, timedelta

import numpy as np
import pandas as pd
import pytest

try:
    from pytest_benchmark.fixture import BenchmarkFixture

    _HAS_BENCHMARK = True
except ImportError:
    _HAS_BENCHMARK = False
 succeeded in 51ms:
    "benchmark: marks tests as performance benchmarks",
    "performance: marks tests as performance tests",
    "property: marks tests as property-based tests",
    "security: marks tests as security tests",
    "flaky: marks tests as potentially flaky",
    "external: marks tests that require external services",
    "load_test: marks tests as load tests",
    "stress_test: marks tests as stress tests",
    "chaos_test: marks tests as chaos/fault injection tests",
]
filterwarnings = [
    "error",
    "ignore::UserWarning",
    "ignore::DeprecationWarning",
    "ignore::PendingDeprecationWarning",
]
minversion = "7.0"

[tool.coverage.run]
source = ["src"]
 succeeded in 50ms:
#!/usr/bin/env bash
# crontab-template.sh — Reference crontab entries per machine role.
#
# PURPOSE: This file is the canonical record of all standard cron jobs.
#          Do NOT run it directly.  To install, use:
#
#   bash scripts/cron/setup-cron.sh               # auto-detects machine role
#   bash scripts/cron/setup-cron.sh --dry-run     # preview without changes
#
# MACHINE ROLES:
#   full              ace-linux-1  — nightly pipeline + all maintenance
#   contribute        ace-linux-2  — repo sync only
#   contribute-minimal ACMA-ANSYS05 / acma-ws014  — Windows Task Scheduler
#
# FORMAT:  # ROLE: <role>
#          <cron-schedule>  <command>
# ─────────────────────────────────────────────────────────────────────────────

# ── ROLE: full (ace-linux-1) ──────────────────────────────────────────────────

 succeeded in 50ms:
#!/usr/bin/env bash
# run-all-tests.sh — Unified test runner for tier-1 Python repos
#
# Iterates tier-1 repos, runs the canonical uv-run pytest command per
# .claude/rules/python-runtime.md, and produces a structured JSONL + markdown summary.
#
# Usage:
#   run-all-tests.sh [--repo <name>] [--json-out <file>]
#
# Exit code:
#   0 = no unexpected failures across all repos
#   1 = one or more unexpected failures (or infrastructure error)
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(git -C "$SCRIPT_DIR" rev-parse --show-toplevel)"
PARSER="${SCRIPT_DIR}/parse_pytest_output.py"
EF_FILE="${SCRIPT_DIR}/expected-failures.txt"

# ── Repo config table ─────────────────────────────────────────────────────────
exec
/bin/bash -lc 'rg -n "CathodicProtection|cathodic_protection|wall thickness|wall_thickness|DNV-ST-F101|router" digitalmodel/src digitalmodel/tests' in /mnt/local-analysis/workspace-hubexec
/bin/bash -lc 'rg -n "keulegan_carpenter_number|soil_interaction_fatigue_factor|scr_fatigue" assetutilities/src assetutilities/tests' in /mnt/local-analysis/workspace-hubexec
/bin/bash -lc 'rg -n "EIA|state.*production|basin.*production|aggregation|tests/performance" worldenergydata/src worldenergydata/tests' in /mnt/local-analysis/workspace-hub succeeded in 1.59s:
assetutilities/src/assetutilities/tests/calculations/test_scr_fatigue.py:7:from assetutilities.calculations.scr_fatigue import (
assetutilities/src/assetutilities/tests/calculations/test_scr_fatigue.py:8:    keulegan_carpenter_number,
assetutilities/src/assetutilities/tests/calculations/test_scr_fatigue.py:9:    soil_interaction_fatigue_factor,
assetutilities/src/assetutilities/tests/calculations/test_scr_fatigue.py:31:# keulegan_carpenter_number
assetutilities/src/assetutilities/tests/calculations/test_scr_fatigue.py:38:        kc = keulegan_carpenter_number(u_m=1.5, period=10.0, diameter=0.5)
assetutilities/src/assetutilities/tests/calculations/test_scr_fatigue.py:42:        kc = keulegan_carpenter_number(u_m=0.8, period=12.0, diameter=0.4)
assetutilities/src/assetutilities/tests/calculations/test_scr_fatigue.py:46:        kc1 = keulegan_carpenter_number(u_m=1.0, period=10.0, diameter=0.5)
assetutilities/src/assetutilities/tests/calculations/test_scr_fatigue.py:47:        kc2 = keulegan_carpenter_number(u_m=2.0, period=10.0, diameter=0.5)
assetutilities/src/assetutilities/tests/calculations/test_scr_fatigue.py:51:        kc1 = keulegan_carpenter_number(u_m=1.0, period=5.0, diameter=0.5)
assetutilities/src/assetutilities/tests/calculations/test_scr_fatigue.py:52:        kc2 = keulegan_carpenter_number(u_m=1.0, period=10.0, diameter=0.5)
assetutilities/src/assetutilities/tests/calculations/test_scr_fatigue.py:56:        kc1 = keulegan_carpenter_number(u_m=1.0, period=10.0, diameter=0.5)
assetutilities/src/assetutilities/tests/calculations/test_scr_fatigue.py:57:        kc2 = keulegan_carpenter_number(u_m=1.0, period=10.0, diameter=1.0)
assetutilities/src/assetutilities/tests/calculations/test_scr_fatigue.py:62:            keulegan_carpenter_number(u_m=1.0, period=10.0, diameter=0.0)
assetutilities/src/assetutilities/tests/calculations/test_scr_fatigue.py:66:            keulegan_carpenter_number(u_m=1.0, period=0.0, diameter=0.5)
assetutilities/src/assetutilities/tests/calculations/test_scr_fatigue.py:70:            keulegan_carpenter_number(u_m=-1.0, period=10.0, diameter=0.5)
assetutilities/src/assetutilities/tests/calculations/test_scr_fatigue.py:73:        kc = keulegan_carpenter_number(u_m=0.0, period=10.0, diameter=0.5)
assetutilities/src/assetutilities/tests/calculations/test_scr_fatigue.py:78:# soil_interaction_fatigue_factor
assetutilities/src/assetutilities/tests/calculations/test_scr_fatigue.py:85:        factor = soil_interaction_fatigue_factor(kc=15.0)
assetutilities/src/assetutilities/tests/calculations/test_scr_fatigue.py:89:        factor = soil_interaction_fatigue_factor(kc=2.0)
assetutilities/src/assetutilities/tests/calculations/test_scr_fatigue.py:93:        factor = soil_interaction_fatigue_factor(kc=10.0)
 succeeded in 3.02s:
worldenergydata/tests/README.md:42:- Located in `tests/performance/`
worldenergydata/tests/README.md:61:pytest tests/performance/
worldenergydata/tests/README.md:77:pytest tests/performance/ --benchmark-only
worldenergydata/tests/README.md:80:pytest tests/performance/ --benchmark-compare
worldenergydata/src/worldenergydata/__init__.py:4:"""World Energy Data - Global energy market data aggregation and analysis.
worldenergydata/tests/unit/test_achievable_coverage.py:151:        # Test aggregations
worldenergydata/tests/performance/test_critical_operations.py:134:    def test_large_dataset_aggregation_performance(self, benchmark, large_dataset):
worldenergydata/tests/performance/test_critical_operations.py:140:            # Multiple aggregations
worldenergydata/tests/integration/workflows/test_end_to_end.py:207:        # Stage 3: Data aggregation
worldenergydata/tests/integration/test_production_api12_full.py:166:        # Field aggregation
worldenergydata/tests/integration/test_production_api12_full.py:256:    def test_aggregation_methods(self, analyzer, production_df):
worldenergydata/tests/integration/test_production_api12_full.py:257:        """Test various aggregation methods"""
worldenergydata/tests/integration/test_production_api12_full.py:258:        # Monthly aggregation
worldenergydata/tests/integration/test_production_api12_full.py:264:        # Yearly aggregation
worldenergydata/tests/performance/regression_detector.py:18:    def __init__(self, baseline_path: str = "tests/performance/baselines", 
worldenergydata/tests/performance/regression_detector.py:262:        report_path = Path("tests/performance/regression_report.txt")
worldenergydata/tests/unit/decommissioning/test_cost_model.py:2:# ABOUTME: Covers parametric estimates, region multipliers, campaign totals, and cost aggregation.
worldenergydata/tests/unit/decommissioning/test_cost_model.py:137:# Campaign and aggregation
worldenergydata/tests/performance/performance_dashboard.py:17:    def __init__(self, output_dir: str = "tests/performance/reports"):
worldenergydata/tests/performance/performance_dashboard.py:31:    def load_regression_report(self, report_file: str = "tests/performance/regression_report.txt") -> str:
 succeeded in 3.43s:
digitalmodel/tests/engineering_validation/pipe_sizing/README.md:108:   - No positive wall thickness checks
digitalmodel/tests/engineering_validation/pipe_sizing/README.md:150:assert wall_thickness < outer_diameter / 2
digitalmodel/tests/engineering_validation/pipe_sizing/README.md:157:- ❌ No wall thickness schedule compliance
digitalmodel/tests/well/tubulars/test_design_envelope.py:75:    def test_wall_thickness_computed_correctly(self):
digitalmodel/tests/well/tubulars/test_design_envelope.py:78:        assert geom.wall_thickness_in == pytest.approx(expected_t, rel=1e-6)
digitalmodel/tests/cathodic_protection/test_api_rp_1632.py:11:from digitalmodel.cathodic_protection.api_rp_1632 import (
digitalmodel/tests/subsea/viv_analysis/test_viv_analysis_unit.py:47:        wall_thickness=0.025,
digitalmodel/tests/subsea/viv_analysis/test_viv_analysis_unit.py:60:        wall_thickness=0.015,
digitalmodel/tests/subsea/viv_analysis/test_viv_analysis_unit.py:149:        assert basic_riser.wall_thickness == 0.025
digitalmodel/tests/subsea/viv_analysis/test_viv_analysis_unit.py:185:            wall_thickness=0.01,
digitalmodel/tests/subsea/viv_analysis/test_viv_analysis_unit.py:230:            wall_thickness=0.02,
digitalmodel/tests/subsea/viv_analysis/test_viv_analysis_unit.py:255:            wall_thickness=0.025, material=STEEL_CARBON,
digitalmodel/tests/subsea/viv_analysis/test_viv_analysis_unit.py:261:            wall_thickness=0.025, material=STEEL_CARBON,
digitalmodel/tests/engineering_validation/pipe_sizing/test_production_validation.py:255:            {"OD": 1, "ID": 0.5, "WT": 0},         # Zero wall thickness
digitalmodel/tests/engineering_validation/pipe_sizing/test_production_validation.py:256:            {"OD": 1, "ID": 0.5, "WT": -0.1},      # Negative wall thickness
digitalmodel/tests/engineering_validation/pipe_sizing/engineering_analysis_report.md:56:- No wall thickness reasonableness checks
digitalmodel/tests/engineering_validation/pipe_sizing/test_industry_standards.py:86:    def test_wall_thickness_schedules(self):
digitalmodel/tests/engineering_validation/pipe_sizing/test_industry_standards.py:87:        """Test wall thickness compliance with API 5L schedules"""
digitalmodel/tests/engineering_validation/pipe_sizing/test_industry_standards.py:95:            # Check minimum wall thickness for pressure containment
digitalmodel/tests/engineering_validation/pipe_sizing/test_industry_standards.py:150:        """Get wall thickness tolerance per API 5L"""
exec
/bin/bash -lc "sed -n '1,220p' assetutilities/pytest.ini" in /mnt/local-analysis/workspace-hubexec
/bin/bash -lc "sed -n '1,140p' worldenergydata/tests/README.md" in /mnt/local-analysis/workspace-hubexec
/bin/bash -lc "sed -n '1,220p' worldenergydata/pytest.ini" in /mnt/local-analysis/workspace-hubexec
/bin/bash -lc "sed -n '1,220p' worldenergydata/tests/pytest.ini" in /mnt/local-analysis/workspace-hub succeeded in 50ms:
[pytest]
minversion = 7.0
testpaths = tests
pythonpath = src tests
python_files = test_*.py *_test.py
python_classes = Test*
python_functions = test_*

markers =
    unit: Unit tests (no external dependencies)
    integration: Integration tests (multiple components)
    slow: Slow tests (>1 second execution)
    llm: LLM/AI tests (external API calls)
    scrapy: Web scraping tests
    selenium: Browser automation tests
    database: Database integration tests
    api: API endpoint tests
    etl: ETL pipeline tests
    live_data: tests that require live network/external APIs (excluded by default)

 succeeded in 51ms:
[pytest]
# Test discovery patterns
python_files = test_*.py *_test.py
python_classes = Test*
python_functions = test_*

# Test directories
testpaths = tests

# Ignore patterns
norecursedirs = .git .venv __pycache__ *.egg-info .pytest_cache reports/coverage/htmlcov build dist legacy_* _archived_tests

# Minimum Python version
minversion = 3.9

# Command line options defaults
addopts = 
    --strict-markers
    --tb=short
    --maxfail=5
 succeeded in 51ms:
[pytest]
minversion = 7.0
testpaths = tests
python_files = test_*.py *_test.py
norecursedirs = _archived_tests _archive .git .venv venv 2025-* legacy_* custom_scripts output legacy comprehensive-report-system financial-analysis-sme-code well-data-verification 2025-08-02-drilling-completion-output-validation 2025-08-06-data-refresh-architecture data htmlcov .coverage* reports
python_classes = Test*
python_functions = test_*

markers =
    unit: Unit tests (no external dependencies)
    integration: Integration tests (multiple components)
    slow: Slow tests (>1 second execution)
    llm: LLM/AI tests (external API calls)
    scrapy: Web scraping tests
    selenium: Browser automation tests
    database: Database integration tests
    api: API endpoint tests
    etl: ETL pipeline tests
    data_validation: Data validation and verification tests
    performance: Performance and benchmark tests
 succeeded in 51ms:
# WorldEnergyData Test Suite

## Overview

This test suite provides comprehensive testing for the WorldEnergyData library, including unit tests, integration tests, performance benchmarks, and validation tests.

## Test Organization

### Directory Structure

```
tests/
├── unit/                    # Unit tests for individual components
│   └── modules/            # Module-specific unit tests
│       ├── bsee/          # BSEE module tests
│       └── financial/     # Financial analysis tests
├── integration/            # Integration tests for workflows
├── performance/            # Performance benchmarks
├── validation/             # Data validation tests
├── consolidated/           # Consolidated parameterized tests
codex
A few concrete risks are showing up now: `worldenergydata/tests/performance/conftest.py` will not automatically apply to a new `tests/benchmarks/` tree, `assetutilities` already has mixed test roots, and the cron template uses `$WORKSPACE_HUB` rather than an ad hoc `<REPO_ROOT>` placeholder. I’m checking the exact benchmark targets and any existing regression tooling so the refined plan can reuse what’s already there.
exec
/bin/bash -lc "sed -n '1,240p' worldenergydata/tests/performance/regression_detector.py" in /mnt/local-analysis/workspace-hubexec
/bin/bash -lc "sed -n '1,260p' worldenergydata/tests/performance/test_critical_operations.py" in /mnt/local-analysis/workspace-hubexec
/bin/bash -lc "sed -n '1,220p' assetutilities/src/assetutilities/calculations/scr_fatigue.py" in /mnt/local-analysis/workspace-hubexec
/bin/bash -lc "sed -n '1,260p' digitalmodel/src/digitalmodel/structural/analysis/wall_thickness.py" in /mnt/local-analysis/workspace-hub succeeded in 51ms:
"""
Performance Regression Detection System
Detects performance regressions in test execution and module operations
"""

import json
import os
import statistics
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import warnings


class PerformanceRegressionDetector:
    """Detects performance regressions by comparing current metrics with historical baselines"""
    
    def __init__(self, baseline_path: str = "tests/performance/baselines", 
                 threshold_percent: float = 20.0):
        """
 succeeded in 50ms:
"""
Performance Tests for Critical Operations

This module tests the performance of critical operations in worldenergydata
to establish baselines and detect performance regressions.
"""

import pytest
import pandas as pd
import numpy as np
from typing import Any
import time
import tracemalloc
from pathlib import Path
import sys
import os

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

 succeeded in 51ms:
# ABOUTME: Steel Catenary Riser (SCR) fatigue calculations for deepwater applications.
# ABOUTME: Implements Allen 1995 VIV, Brooks 1987 screening, KC number, and TDZ fatigue.

"""Steel Catenary Riser (SCR) fatigue calculation module.

References:
- Allen, D.W. (1995) — Vortex-Induced Vibration Analysis of the Auger TLP, OTC.
- Brooks, I.H. (1987) — A Pragmatic Approach to Vortex-Induced Vibrations, OTC.
- OTC1997-8494 — Code Conflicts: pipeline codes for SCR design.
- OTC2001-13109 — SCR Fatigue at Low Keulegan-Carpenter Number.
"""

import math
from typing import List, Tuple

# Threshold reduced velocity for VIV onset (Brooks 1987)
_VR_ONSET = 4.0

# Brooks (1987) lock-in amplitude ratio A/D
_BROOKS_LOCK_IN_A_OVER_D = 0.9
 succeeded in 50ms:
# ABOUTME: Pipeline wall thickness design checks per DNV-ST-F101 and API RP 1111
# ABOUTME: Dataclass + analyzer pattern for burst, collapse, propagation, combined loading

"""
Pipeline Wall Thickness Design Checks

Design code checks per DNV-ST-F101 (submarine pipeline systems) and
API RP 1111 (offshore hydrocarbon pipelines).

Implements:
- Pressure containment (burst) - DNV Sec 5 D401, API 4.3.1.1
- Local buckling / collapse     - DNV Sec 5 D500, API 4.3.2
- Propagation buckling          - DNV Sec 5 D600, API 4.3.3
- Combined loading (P+M+T)      - DNV Sec 5 D700

Standards: DNV-ST-F101 (2021), API RP 1111 (2015)
Units: SI throughout (metres, Pascals, Newtons)
"""

from dataclasses import dataclass, field
exec
/bin/bash -lc "rg -n \"class CathodicProtection|def router\\(|ABS_GN_SHIPS|DNV_RP_F103_2010|ISO_15589_2|API_RP_1632\" digitalmodel/src/digitalmodel/infrastructure/base_solvers/hydrodynamics/cathodic_protection.py" in /mnt/local-analysis/workspace-hubexec
/bin/bash -lc "find worldenergydata/tests/performance -maxdepth 2 -type f | sort | sed -n '1,80p'" in /mnt/local-analysis/workspace-hubexec
/bin/bash -lc 'find digitalmodel/tests/benchmarks -maxdepth 2 -type f | sort' in /mnt/local-analysis/workspace-hub succeeded in 50ms:
14:class CathodicProtection:
18:    def router(self, cfg):
21:        elif cfg["inputs"]["calculation_type"] == "DNV_RP_F103_2010":
22:            self.DNV_RP_F103_2010(cfg)
67:    def DNV_RP_F103_2010(self, cfg):
 succeeded in 51ms:
worldenergydata/tests/performance/__pycache__/regression_detector.cpython-311.pyc
worldenergydata/tests/performance/__pycache__/regression_detector.cpython-312.pyc
worldenergydata/tests/performance/__pycache__/test_critical_operations.cpython-311-pytest-8.4.2.pyc
worldenergydata/tests/performance/__pycache__/test_critical_operations.cpython-312-pytest-9.0.2.pyc
worldenergydata/tests/performance/__pycache__/test_regression_detector.cpython-311-pytest-8.4.2.pyc
worldenergydata/tests/performance/__pycache__/test_regression_detector.cpython-312-pytest-9.0.2.pyc
worldenergydata/tests/performance/conftest.py
worldenergydata/tests/performance/performance_dashboard.py
worldenergydata/tests/performance/regression_detector.py
worldenergydata/tests/performance/reports/performance_dashboard.html
worldenergydata/tests/performance/test_critical_operations.py
worldenergydata/tests/performance/test_regression_detector.py
 succeeded in 50ms:
digitalmodel/tests/benchmarks/__pycache__/conftest.cpython-311-pytest-8.4.2.pyc
digitalmodel/tests/benchmarks/__pycache__/conftest.cpython-312-pytest-9.0.2.pyc
digitalmodel/tests/benchmarks/__pycache__/test_benchmark_classification.cpython-311-pytest-8.4.2.pyc
digitalmodel/tests/benchmarks/__pycache__/test_benchmark_classification.cpython-312-pytest-9.0.2.pyc
digitalmodel/tests/benchmarks/__pycache__/test_example_model_benchmark.cpython-311-pytest-8.4.2.pyc
digitalmodel/tests/benchmarks/__pycache__/test_example_model_benchmark.cpython-312-pytest-9.0.2.pyc
digitalmodel/tests/benchmarks/__pycache__/test_performance_benchmarks.cpython-311-pytest-8.4.2.pyc
digitalmodel/tests/benchmarks/__pycache__/test_performance_benchmarks.cpython-312-pytest-9.0.2.pyc
digitalmodel/tests/benchmarks/__pycache__/test_seed_equivalence_metrics.cpython-311-pytest-8.4.2.pyc
digitalmodel/tests/benchmarks/__pycache__/test_seed_equivalence_metrics.cpython-312-pytest-9.0.2.pyc
digitalmodel/tests/benchmarks/conftest.py
digitalmodel/tests/benchmarks/test_benchmark_classification.py
digitalmodel/tests/benchmarks/test_example_model_benchmark.py
digitalmodel/tests/benchmarks/test_performance_benchmarks.py
digitalmodel/tests/benchmarks/test_seed_equivalence_metrics.py
exec
/bin/bash -lc "sed -n '1,220p' digitalmodel/tests/benchmarks/conftest.py" in /mnt/local-analysis/workspace-hub succeeded in 51ms:
# ABOUTME: Pytest fixtures for benchmark tests.
# ABOUTME: Provides datasets of varying sizes for performance testing.

import pytest


@pytest.fixture
def benchmark_datasets():
    """
    Provide datasets of different sizes for performance benchmarking.

    Returns a dictionary with 'small', 'medium', and 'large' datasets
    containing numeric data suitable for performance testing operations
    such as filtering, statistics computation, and list processing.
    """
    return {
        "small": list(range(100)),
        "medium": list(range(1000)),
        "large": list(range(10000)),
    }
exec
/bin/bash -lc "sed -n '1,220p' digitalmodel/tests/benchmarks/test_performance_benchmarks.py" in /mnt/local-analysis/workspace-hub succeeded in 51ms:
"""
Performance benchmark tests for digitalmodel.

These tests establish performance baselines and detect regressions.
"""

import pytest
from hypothesis import given, strategies as st
import time
from typing import List


@pytest.mark.benchmark
class TestAlgorithmPerformance:
    """Performance benchmarks for core algorithms."""

    def test_list_processing_benchmark(self, benchmark, benchmark_datasets):
        """Benchmark list processing performance."""
        data = benchmark_datasets["medium"]

codex
## Refined Plan

```yaml
---
wrk_id: WRK-1071
title: "feat(harness): performance benchmark harness — regression detection for engineering calculations"
domain: harness/performance-profiling
complexity: medium
route: B
created_at: 2026-03-10
target_repos: [assetutilities, digitalmodel, worldenergydata]
status: draft
version: "1.1"
---
```

### Mission
Establish stable, runnable performance baselines for compute-heavy engineering calculations and fail fast on meaningful regressions without introducing repo-specific env drift.

### Phase 1 — Harness contract and TDD first

**Primary harness tests** in `scripts/testing/test_run_benchmarks.py`:

1. `test_run_benchmarks_all_repos_exit_zero`
   Verifies clean run across all configured repos.

2. `test_run_benchmarks_single_repo`
   Verifies `--repo <name>` runs only the selected repo and compares only that repo’s baseline entries.

3. `test_save_baseline_writes_json`
   Verifies `--save-baseline` writes `config/testing/benchmark-baseline.json` with repo-qualified benchmark keys.

4. `test_regression_detection_flags_slowdown`
   Verifies injected 25% slowdown returns exit 1 and prints offending benchmark IDs.

5. `test_no_regression_passes`
   Verifies baseline-equal or faster results return exit 0.

**Add 4 missing edge-case tests** because the current 5 do not cover the main failure modes:

6. `test_compare_without_baseline_fails_with_actionable_message`
   If baseline file is absent and `--no-compare`/`--save-baseline` is not used, exit non-zero with bootstrap instructions.

7. `test_missing_repo_baseline_entries_warn_and_skip_new_benchmarks`
   New benchmark names should not hard-fail compare mode on first introduction; warn as “unbaselined”.

8. `test_worldenergydata_benchmark_dependency_missing_fails_cleanly`
   Verifies missing `pytest-benchmark` in `worldenergydata` produces a deterministic setup error, not a misleading regression result.

9. `test_invalid_repo_name_exits_nonzero`
   Prevent silent no-op when `--repo` is misspelled.

### Phase 2 — Repo benchmark integration

**assetutilities**
- Add `pytest-benchmark>=4.0.0,<5.0.0` to `[dependency-groups].test`.
- Keep benchmark files under root `tests/benchmarks/`, not `src/assetutilities/tests/`, because repo discovery already points at root `tests` and the repo has split test trees.
- Create `tests/benchmarks/test_scr_fatigue_benchmarks.py`:
  - `test_bench_keulegan_carpenter_number(benchmark)`
  - `test_bench_soil_interaction_fatigue_factor(benchmark)`
- Use pure synthetic scalar inputs only; no fixtures that imply nonexistent soil-profile APIs.

**digitalmodel**
- Do not change dependency setup unless needed; `pytest-benchmark` is already present.
- Reuse existing `digitalmodel/tests/benchmarks/` and its `conftest.py`.
- Create:
  - `digitalmodel/tests/benchmarks/test_cp_benchmarks.py`
  - `digitalmodel/tests/benchmarks/test_wall_thickness_benchmarks.py`
- Import CP from the non-shim path:
  `digitalmodel.infrastructure.base_solvers.hydrodynamics.cathodic_protection.CathodicProtection`
- Benchmark concrete, deterministic calls:
  - CP router for `DNV_RP_F103_2010`
  - CP router for each supported calculation route actually implemented
  - Wall thickness via `WallThicknessAnalyzer` with DNV-ST-F101 inputs
- Explicitly mark new tests `@pytest.mark.benchmark`.

**worldenergydata**
- Do not assume optional extras are active.
- Move `pytest-benchmark` into a real uv-executable dependency path:
  - Preferred: add a dedicated `[dependency-groups].benchmark` with `pytest-benchmark`, or add it to `[dependency-groups].dev`.
  - Avoid relying only on `[project.optional-dependencies].dev`.
- Keep benchmark tests under `tests/performance/` unless there is a deliberate move of `conftest.py` to `tests/conftest.py`.
  Reason: [conftest.py](/mnt/local-analysis/workspace-hub/worldenergydata/tests/performance/conftest.py) will not apply automatically to a sibling `tests/benchmarks/` tree.
- Create `worldenergydata/tests/performance/test_eia_benchmarks.py`:
  - `test_bench_state_production_loader(benchmark, ...)`
  - `test_bench_basin_production_loader(benchmark, ...)`
- Use synthetic in-memory records only; no API-key or network dependence.

### Phase 3 — Runner and baseline tooling

**`scripts/testing/run-benchmarks.sh`**
- Model on [run-all-tests.sh](/mnt/local-analysis/workspace-hub/scripts/testing/run-all-tests.sh), but use `uv run --project <repo>` consistently.
- Repo config should include:
  - repo name
  - repo dir
  - optional `PYTHONPATH`
  - benchmark target path
  - uv groups/extras needed

Example logical config:
- `assetutilities | assetutilities | "" | tests/benchmarks | group=test`
- `digitalmodel | digitalmodel | "" | tests/benchmarks | default`
- `worldenergydata | worldenergydata | "src:../assetutilities/src" or local uv source | tests/performance/test_eia_benchmarks.py | group=benchmark`

Runner behavior:
- Per repo:
  `uv run --project "$repo_dir" [group flags] python -m pytest <target> --benchmark-only --benchmark-json=<tmp> -q`
- Aggregate raw outputs to `scripts/testing/benchmark-results/benchmark-YYYY-MM-DD.json`
- `--repo <name>` for single repo
- `--save-baseline` writes `config/testing/benchmark-baseline.json`
- `--no-compare` skips regression check
- Default compare mode:
  - missing baseline file => actionable failure
  - missing individual benchmark entry => warn/unbaselined, not regression
  - regression threshold => mean > 20% slower
- Exit codes:
  - `0` clean
  - `1` regression detected
  - `2` setup/config/env error

**`scripts/testing/parse_benchmark_output.py`**
- Normalize IDs as `repo::benchmark_name`
- Compare only like-for-like benchmarks
- Print table with:
  - repo
  - benchmark
  - baseline mean
  - current mean
  - percent delta
  - status (`OK`, `REGRESSION`, `NEW`, `MISSING_BASELINE`)
- Support partial compare for `--repo`

### Phase 4 — Cron and workspace integration

- Add weekly cron line using the existing template convention in [crontab-template.sh](/mnt/local-analysis/workspace-hub/scripts/cron/crontab-template.sh):
  `# CRON: 0 4 * * 0  cd $WORKSPACE_HUB && bash scripts/testing/run-benchmarks.sh >> $WORKSPACE_HUB/logs/quality/benchmark-cron.log 2>&1`
- Do not use literal `<REPO_ROOT>` in cron.
- If the runner needs env activation beyond repo-local `uv run`, make it self-contained inside the script rather than depending on cron shell state.
- Bootstrap flow:
  `bash scripts/testing/run-benchmarks.sh --save-baseline --no-compare`
- Commit `config/testing/benchmark-baseline.json`
- Add `scripts/testing/benchmark-results/` to `.gitignore`

### Updated Acceptance Criteria

- [ ] Benchmark runner handles missing baseline file with a clear bootstrap error path
- [ ] Benchmark runner distinguishes regression vs setup/config failure via exit codes
- [ ] `assetutilities` benchmarks run from root `tests/benchmarks/`
- [ ] `digitalmodel` benchmarks integrate into existing `tests/benchmarks/` without breaking current benchmark collection
- [ ] `worldenergydata` benchmark dependency is executable via uv without manual extra activation
- [ ] Benchmark IDs are repo-qualified in baseline/results files
- [ ] Single-repo mode compares only the selected repo’s entries
- [ ] Weekly cron entry uses `$WORKSPACE_HUB` template pattern, not `<REPO_ROOT>`
- [ ] Initial baseline is generated and committed
- [ ] Cross-review passes

## Review Notes

**Verdict: MAJOR**

Major issues in the current draft:

- `worldenergydata` dependency activation is underspecified. `pytest-benchmark` exists only under optional `dev`, not the active dependency groups in [worldenergydata/pyproject.toml](/mnt/local-analysis/workspace-hub/worldenergydata/pyproject.toml), so `uv run` may not have the plugin at all.
- The plan puts new `worldenergydata` benchmarks under `tests/benchmarks/`, but the reusable benchmark fixtures live in [worldenergydata/tests/performance/conftest.py](/mnt/local-analysis/workspace-hub/worldenergydata/tests/performance/conftest.py). That `conftest.py` will not automatically cover a sibling tree.
- The cron command uses `<REPO_ROOT>`, but the actual template convention in [scripts/cron/crontab-template.sh](/mnt/local-analysis/workspace-hub/scripts/cron/crontab-template.sh) uses `cd $WORKSPACE_HUB && ...`. Literal placeholder expansion in crontab is a real failure mode.
- The 5 TDD tests miss the highest-risk behaviors: no-baseline bootstrap, partial/new benchmark entries, invalid repo selection, and dependency/setup failure classification.
- `digitalmodel/tests/benchmarks/` already exists and is non-empty. Running the whole directory can pull in unrelated benchmark tests and variance; the plan needs explicit scoping or an audit of the existing suite. See [digitalmodel/tests/benchmarks/conftest.py](/mnt/local-analysis/workspace-hub/digitalmodel/tests/benchmarks/conftest.py).

Minor notes:

- `assetutilities` has both root `tests/` and `src/assetutilities/tests/`; the draft should explicitly standardize on root `tests/benchmarks/` to avoid collection ambiguity. See [assetutilities/pytest.ini](/mnt/local-analysis/workspace-hub/assetutilities/pytest.ini).
- The baseline schema should use repo-qualified keys to avoid collisions across repos with similarly named benchmarks.
- `run-benchmarks.sh` should prefer `uv run --project ...` over hand-managed path assumptions, with `PYTHONPATH` used only where unavoidable.

Residual integration risk after refinement:
- Benchmark variance across machines and dependency updates can still cause noise; keeping this on one workstation and using a 20% threshold is reasonable, but the runner should label unbaselined/new tests separately from regressions.
tokens used
163,501
## Refined Plan

```yaml
---
wrk_id: WRK-1071
title: "feat(harness): performance benchmark harness — regression detection for engineering calculations"
domain: harness/performance-profiling
complexity: medium
route: B
created_at: 2026-03-10
target_repos: [assetutilities, digitalmodel, worldenergydata]
status: draft
version: "1.1"
---
```

### Mission
Establish stable, runnable performance baselines for compute-heavy engineering calculations and fail fast on meaningful regressions without introducing repo-specific env drift.

### Phase 1 — Harness contract and TDD first

**Primary harness tests** in `scripts/testing/test_run_benchmarks.py`:

1. `test_run_benchmarks_all_repos_exit_zero`
   Verifies clean run across all configured repos.

2. `test_run_benchmarks_single_repo`
   Verifies `--repo <name>` runs only the selected repo and compares only that repo’s baseline entries.

3. `test_save_baseline_writes_json`
   Verifies `--save-baseline` writes `config/testing/benchmark-baseline.json` with repo-qualified benchmark keys.

4. `test_regression_detection_flags_slowdown`
   Verifies injected 25% slowdown returns exit 1 and prints offending benchmark IDs.

5. `test_no_regression_passes`
   Verifies baseline-equal or faster results return exit 0.

**Add 4 missing edge-case tests** because the current 5 do not cover the main failure modes:

6. `test_compare_without_baseline_fails_with_actionable_message`
   If baseline file is absent and `--no-compare`/`--save-baseline` is not used, exit non-zero with bootstrap instructions.

7. `test_missing_repo_baseline_entries_warn_and_skip_new_benchmarks`
   New benchmark names should not hard-fail compare mode on first introduction; warn as “unbaselined”.

8. `test_worldenergydata_benchmark_dependency_missing_fails_cleanly`
   Verifies missing `pytest-benchmark` in `worldenergydata` produces a deterministic setup error, not a misleading regression result.

9. `test_invalid_repo_name_exits_nonzero`
   Prevent silent no-op when `--repo` is misspelled.

### Phase 2 — Repo benchmark integration

**assetutilities**
- Add `pytest-benchmark>=4.0.0,<5.0.0` to `[dependency-groups].test`.
- Keep benchmark files under root `tests/benchmarks/`, not `src/assetutilities/tests/`, because repo discovery already points at root `tests` and the repo has split test trees.
- Create `tests/benchmarks/test_scr_fatigue_benchmarks.py`:
  - `test_bench_keulegan_carpenter_number(benchmark)`
  - `test_bench_soil_interaction_fatigue_factor(benchmark)`
- Use pure synthetic scalar inputs only; no fixtures that imply nonexistent soil-profile APIs.

**digitalmodel**
- Do not change dependency setup unless needed; `pytest-benchmark` is already present.
- Reuse existing `digitalmodel/tests/benchmarks/` and its `conftest.py`.
- Create:
  - `digitalmodel/tests/benchmarks/test_cp_benchmarks.py`
  - `digitalmodel/tests/benchmarks/test_wall_thickness_benchmarks.py`
- Import CP from the non-shim path:
  `digitalmodel.infrastructure.base_solvers.hydrodynamics.cathodic_protection.CathodicProtection`
- Benchmark concrete, deterministic calls:
  - CP router for `DNV_RP_F103_2010`
  - CP router for each supported calculation route actually implemented
  - Wall thickness via `WallThicknessAnalyzer` with DNV-ST-F101 inputs
- Explicitly mark new tests `@pytest.mark.benchmark`.

**worldenergydata**
- Do not assume optional extras are active.
- Move `pytest-benchmark` into a real uv-executable dependency path:
  - Preferred: add a dedicated `[dependency-groups].benchmark` with `pytest-benchmark`, or add it to `[dependency-groups].dev`.
  - Avoid relying only on `[project.optional-dependencies].dev`.
- Keep benchmark tests under `tests/performance/` unless there is a deliberate move of `conftest.py` to `tests/conftest.py`.
  Reason: [conftest.py](/mnt/local-analysis/workspace-hub/worldenergydata/tests/performance/conftest.py) will not apply automatically to a sibling `tests/benchmarks/` tree.
- Create `worldenergydata/tests/performance/test_eia_benchmarks.py`:
  - `test_bench_state_production_loader(benchmark, ...)`
  - `test_bench_basin_production_loader(benchmark, ...)`
- Use synthetic in-memory records only; no API-key or network dependence.

### Phase 3 — Runner and baseline tooling

**`scripts/testing/run-benchmarks.sh`**
- Model on [run-all-tests.sh](/mnt/local-analysis/workspace-hub/scripts/testing/run-all-tests.sh), but use `uv run --project <repo>` consistently.
- Repo config should include:
  - repo name
  - repo dir
  - optional `PYTHONPATH`
  - benchmark target path
  - uv groups/extras needed

Example logical config:
- `assetutilities | assetutilities | "" | tests/benchmarks | group=test`
- `digitalmodel | digitalmodel | "" | tests/benchmarks | default`
- `worldenergydata | worldenergydata | "src:../assetutilities/src" or local uv source | tests/performance/test_eia_benchmarks.py | group=benchmark`

Runner behavior:
- Per repo:
  `uv run --project "$repo_dir" [group flags] python -m pytest <target> --benchmark-only --benchmark-json=<tmp> -q`
- Aggregate raw outputs to `scripts/testing/benchmark-results/benchmark-YYYY-MM-DD.json`
- `--repo <name>` for single repo
- `--save-baseline` writes `config/testing/benchmark-baseline.json`
- `--no-compare` skips regression check
- Default compare mode:
  - missing baseline file => actionable failure
  - missing individual benchmark entry => warn/unbaselined, not regression
  - regression threshold => mean > 20% slower
- Exit codes:
  - `0` clean
  - `1` regression detected
  - `2` setup/config/env error

**`scripts/testing/parse_benchmark_output.py`**
- Normalize IDs as `repo::benchmark_name`
- Compare only like-for-like benchmarks
- Print table with:
  - repo
  - benchmark
  - baseline mean
  - current mean
  - percent delta
  - status (`OK`, `REGRESSION`, `NEW`, `MISSING_BASELINE`)
- Support partial compare for `--repo`

### Phase 4 — Cron and workspace integration

- Add weekly cron line using the existing template convention in [crontab-template.sh](/mnt/local-analysis/workspace-hub/scripts/cron/crontab-template.sh):
  `# CRON: 0 4 * * 0  cd $WORKSPACE_HUB && bash scripts/testing/run-benchmarks.sh >> $WORKSPACE_HUB/logs/quality/benchmark-cron.log 2>&1`
- Do not use literal `<REPO_ROOT>` in cron.
- If the runner needs env activation beyond repo-local `uv run`, make it self-contained inside the script rather than depending on cron shell state.
- Bootstrap flow:
  `bash scripts/testing/run-benchmarks.sh --save-baseline --no-compare`
- Commit `config/testing/benchmark-baseline.json`
- Add `scripts/testing/benchmark-results/` to `.gitignore`

### Updated Acceptance Criteria

- [ ] Benchmark runner handles missing baseline file with a clear bootstrap error path
- [ ] Benchmark runner distinguishes regression vs setup/config failure via exit codes
- [ ] `assetutilities` benchmarks run from root `tests/benchmarks/`
- [ ] `digitalmodel` benchmarks integrate into existing `tests/benchmarks/` without breaking current benchmark collection
- [ ] `worldenergydata` benchmark dependency is executable via uv without manual extra activation
- [ ] Benchmark IDs are repo-qualified in baseline/results files
- [ ] Single-repo mode compares only the selected repo’s entries
- [ ] Weekly cron entry uses `$WORKSPACE_HUB` template pattern, not `<REPO_ROOT>`
- [ ] Initial baseline is generated and committed
- [ ] Cross-review passes

## Review Notes

**Verdict: MAJOR**

Major issues in the current draft:

- `worldenergydata` dependency activation is underspecified. `pytest-benchmark` exists only under optional `dev`, not the active dependency groups in [worldenergydata/pyproject.toml](/mnt/local-analysis/workspace-hub/worldenergydata/pyproject.toml), so `uv run` may not have the plugin at all.
- The plan puts new `worldenergydata` benchmarks under `tests/benchmarks/`, but the reusable benchmark fixtures live in [worldenergydata/tests/performance/conftest.py](/mnt/local-analysis/workspace-hub/worldenergydata/tests/performance/conftest.py). That `conftest.py` will not automatically cover a sibling tree.
- The cron command uses `<REPO_ROOT>`, but the actual template convention in [scripts/cron/crontab-template.sh](/mnt/local-analysis/workspace-hub/scripts/cron/crontab-template.sh) uses `cd $WORKSPACE_HUB && ...`. Literal placeholder expansion in crontab is a real failure mode.
- The 5 TDD tests miss the highest-risk behaviors: no-baseline bootstrap, partial/new benchmark entries, invalid repo selection, and dependency/setup failure classification.
- `digitalmodel/tests/benchmarks/` already exists and is non-empty. Running the whole directory can pull in unrelated benchmark tests and variance; the plan needs explicit scoping or an audit of the existing suite. See [digitalmodel/tests/benchmarks/conftest.py](/mnt/local-analysis/workspace-hub/digitalmodel/tests/benchmarks/conftest.py).

Minor notes:

- `assetutilities` has both root `tests/` and `src/assetutilities/tests/`; the draft should explicitly standardize on root `tests/benchmarks/` to avoid collection ambiguity. See [assetutilities/pytest.ini](/mnt/local-analysis/workspace-hub/assetutilities/pytest.ini).
- The baseline schema should use repo-qualified keys to avoid collisions across repos with similarly named benchmarks.
- `run-benchmarks.sh` should prefer `uv run --project ...` over hand-managed path assumptions, with `PYTHONPATH` used only where unavoidable.

Residual integration risk after refinement:
- Benchmark variance across machines and dependency updates can still cause noise; keeping this on one workstation and using a 20% threshold is reasonable, but the runner should label unbaselined/new tests separately from regressions.
