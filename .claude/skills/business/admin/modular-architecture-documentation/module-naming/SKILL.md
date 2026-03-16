---
name: modular-architecture-documentation-module-naming
description: 'Sub-skill of modular-architecture-documentation: Module Naming (+4).'
version: 1.0.0
category: business
type: reference
scripts_exempt: true
---

# Module Naming (+4)

## Module Naming

- **Use domain names, not technical terms:**
  - ✅ `invoice`, `tax_prep`, `tax_file`
  - ❌ `module1`, `processor`, `generator`

- **Keep names short and memorable:**
  - ✅ `invoice-gen` (CLI command)
  - ❌ `invoice_generation_automation_tool`


## Module Boundaries

- **One module = one CLI command = one purpose**
- **Clear inputs/outputs per module**
- **No circular dependencies between modules**
- **Minimize shared components** (only truly shared code)


## CLI Command Design

- **Consistent flag naming across modules:**
  - `--help`, `--verbose`, `--dry-run`, `--config`
- **Intuitive command names reflecting actions:**
  - `invoice-gen`, `tax-prep`, `tax-file`
- **Comprehensive help text with examples**


## Documentation Standards

- **Document in tech-stack.md:** Module structure, CLI commands, adoption path
- **Record in decisions.md:** Why modular, alternatives considered, consequences
- **Update roadmap.md:** Phased implementation per module
- **Maintain README:** Quick start per module


## Testing Independence

- **Each module has test directory:**
  ```
  tests/
  ├── invoice/
  ├── tax_prep/
  ├── tax_file/
  └── shared/
  ```
- **Mock other modules in tests** (don't depend on them)
- **80% coverage per module, 95% for critical**
