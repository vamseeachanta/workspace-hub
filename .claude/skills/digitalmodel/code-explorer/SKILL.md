---
name: digitalmodel-code-explorer
description: Fast orientation guide for the digitalmodel codebase, with module lookup, source-to-test mapping, and targeted inspection patterns to avoid repeated bulk-reading of digitalmodel/src and tests.
version: 1.0.0
category: digitalmodel
type: skill
trigger: manual
auto_execute: false
capabilities:
- module_indexing
- source_test_mapping
- package_orientation
- targeted_code_lookup
- architecture_navigation
tools:
- Read
- Grep
- Bash
related_skills:
- repo-capability-map
- module-lookup
requires: []
tags:
- digitalmodel
- code-explorer
- navigation
- architecture
---

# Digitalmodel Code Explorer

## Purpose

Use this skill to navigate `digitalmodel/src/digitalmodel/` and its tests without bulk-reading large numbers of files. It is intended to reduce repeated manual source exploration by giving a fast module map and lookup workflow.

## Core Areas in digitalmodel/src/digitalmodel/

Examples of major areas present on this machine include:
- `fatigue/`
- `cathodic_protection/`
- `structural/`
- `subsea/`
- `reservoir/`
- `signal_processing/`
- `well/`
- `workflows/`
- top-level helpers like `engine.py`, `units.py`, `__main__.py`

## Recommended Exploration Pattern

### 1. Find the relevant package first

```bash
find digitalmodel/src/digitalmodel -maxdepth 2 -type f | head -50
```

### 2. Narrow by topic before reading files

Examples:

```bash
rg -n "rainflow|sn curve|fatigue" digitalmodel/src/digitalmodel/fatigue
rg -n "orcawave|diffraction|rao" digitalmodel/src/digitalmodel
rg -n "cathodic|anode|iccp" digitalmodel/src/digitalmodel/cathodic_protection
```

### 3. Read only the most relevant files

Prefer:
- package `__init__.py`
- API-facing modules
- the exact function/class implementation you matched
- the corresponding tests

## Source -> Test Mapping Pattern

Before editing a source file, look for mirrored or neighboring tests.

Examples:

```bash
find digitalmodel/tests -type f | rg "fatigue|cathodic|orcawave|orcaflex"
```

Heuristic mapping:
- `digitalmodel/src/digitalmodel/fatigue/<module>.py`
  -> search under `digitalmodel/tests/` for `<module>` or the package name
- package-level behavior
  -> check `digitalmodel/tests/<package>/` and `digitalmodel/tests/unit/`

## Useful Fast Questions This Skill Helps Answer

- Which package owns a domain concept?
- Where is the public API versus a helper implementation?
- What tests exist for a module before changing it?
- Which neighboring files should be compared for similar patterns?

## Practical Workflow

1. identify the domain/package
2. grep for the concrete symbol or topic
3. read the smallest relevant set of files
4. map to tests before implementation
5. only then expand outward if architecture context is still missing

## Common Pitfalls

- reading an entire package tree before asking a narrower question
- editing a module without finding its tests first
- assuming domain ownership without checking sibling packages
- mixing package discovery and implementation in the same pass

## Good Companion Commands

```bash
find digitalmodel/src/digitalmodel -maxdepth 2 -type f | sort
find digitalmodel/tests -type f | sort | head -100
rg -n "class |def " digitalmodel/src/digitalmodel/<package>
```

## Notes

This is an orientation skill, not a replacement for reading source. Its goal is to reduce repeated bulk-read behavior by making the first pass targeted and test-aware.
