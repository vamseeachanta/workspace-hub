---
name: repo-cleanup-pre-cleanup
description: 'Sub-skill of repo-cleanup: Pre-Cleanup (+7).'
version: 2.2.0
category: _internal
type: reference
scripts_exempt: true
---

# Pre-Cleanup (+7)

## Pre-Cleanup


- [ ] Git working directory status documented
- [ ] Important untracked files identified
- [ ] Backup created if needed

## Build Artifacts


- [ ] `__pycache__/` directories removed
- [ ] `*.egg-info/` directories removed
- [ ] `.pytest_cache/` removed
- [ ] `build/` and `dist/` removed if present

## Log Files


- [ ] `*.log` files removed or archived
- [ ] `*LogFile.txt` files removed
- [ ] Rotated logs cleaned

## Temp Files


- [ ] `*.tmp` files removed
- [ ] Editor backup files removed
- [ ] Cache directories cleaned

## Coverage Reports


- [ ] `htmlcov/` removed
- [ ] `.coverage` files removed

## Consolidation


- [ ] Agent directories consolidated to `.claude/agents/`
- [ ] Prototypes moved to `examples/prototypes/`
- [ ] Test outputs moved to `tests/outputs/`
- [ ] Benchmark test fixtures moved to `tests/fixtures/`
- [ ] Benchmark generated outputs untracked and gitignored
- [ ] Completed plan files archived to `specs/archive/`

## Hidden Folder Review


- [ ] `.agent-os/` reviewed and consolidated
- [ ] `.ai/` reviewed and consolidated
- [ ] `.agent-runtime/` deleted if dead symlinks
- [ ] `.common/` relocated or deleted
- [ ] `.specify/` deleted if stale

## Post-Cleanup


- [ ] `.gitignore` updated with new patterns
- [ ] `git status` shows clean or expected state
- [ ] Tests still pass after cleanup
