---
name: yaml-configuration
version: 1.0.0
description: YAML for configuration-driven engineering workflows, model setup, and
  analysis parameters
author: workspace-hub
category: data
tags:
- yaml
- configuration
- engineering
- orcaflex
- automation
- data-structures
platforms:
- yaml
- python
capabilities: []
requires: []
see_also:
- yaml-configuration-example-1-orcaflex-mooring-configuration
- yaml-configuration-loading-yaml-in-python
- yaml-configuration-pattern-1-configuration-hierarchy
- yaml-configuration-installation
---

# Yaml Configuration

## When to Use This Skill

Use YAML configuration when you need:
- **Configuration-driven workflows** - Separate data from code
- **Reproducible analyses** - Version-controlled parameters
- **Model templates** - Reusable configurations
- **Complex nested structures** - Hierarchical data organization
- **Human-readable configs** - Easy to review and modify
- **Automated model generation** - OrcaFlex, FEA, CAD models

**Avoid when:**
- Binary data needed (use pickle, HDF5)
- Extremely large datasets (use CSV, databases)
- Real-time performance critical (use JSON)

## Resources

- **YAML Official Spec**: https://yaml.org/spec/
- **PyYAML Documentation**: https://pyyaml.org/wiki/PyYAMLDocumentation
- **YAML Lint**: http://www.yamllint.com/
- **JSON Schema**: https://json-schema.org/

---

**Use this skill to create maintainable, version-controlled configurations for all DigitalModel analyses!**

## Sub-Skills

- [1. Basic YAML Syntax (+1)](1-basic-yaml-syntax/SKILL.md)
- [1. Use Consistent Indentation (+4)](1-use-consistent-indentation/SKILL.md)

## Sub-Skills

- [Example 1: OrcaFlex Mooring Configuration (+5)](example-1-orcaflex-mooring-configuration/SKILL.md)
- [Loading YAML in Python (+3)](loading-yaml-in-python/SKILL.md)
- [Pattern 1: Configuration Hierarchy (+2)](pattern-1-configuration-hierarchy/SKILL.md)
- [Installation](installation/SKILL.md)
