---
name: json-config-loader
version: 1.0.0
description: Configuration file parsing patterns for bash scripts (INI, key=value,
  JSON)
author: workspace-hub
category: _core
tags:
- bash
- config
- json
- yaml
- parsing
- jq
- configuration
platforms:
- linux
- macos
see_also:
- json-config-loader-1-keyvalue-configuration-parsing
- json-config-loader-3-json-report-generation
- json-config-loader-4-multi-section-ini-parsing
- json-config-loader-5-environment-variable-configuration
- json-config-loader-6-yaml-configuration-via-yq
- json-config-loader-1-always-provide-defaults
---

# Json Config Loader

## When to Use This Skill

✅ **Use when:**
- Loading configuration from files into bash scripts
- Parsing key=value or INI-style configuration files
- Working with JSON data using jq
- Generating JSON reports from bash
- Managing configuration with associative arrays

❌ **Avoid when:**
- Complex nested configuration (consider Python instead)
- Real-time configuration changes (use a daemon)
- Configuration with complex validation rules

## Complete Example: Config Manager

Full configuration management with multiple formats:

```bash
#!/bin/bash
# ABOUTME: Universal configuration manager
# ABOUTME: Supports key=value, JSON, and environment overrides

set -e

# ─────────────────────────────────────────────────────────────────
# Configuration Storage
# ─────────────────────────────────────────────────────────────────

declare -A CONFIG
CONFIG_FILE=""
CONFIG_FORMAT=""

# ─────────────────────────────────────────────────────────────────
# Format Detection
# ─────────────────────────────────────────────────────────────────

detect_format() {
    local file="$1"

    case "${file##*.}" in

*See sub-skills for full details.*

## Resources

- [jq Manual](https://stedolan.github.io/jq/manual/)
- [yq Documentation](https://mikefarah.gitbook.io/yq/)
- [Bash Associative Arrays](https://www.gnu.org/software/bash/manual/html_node/Arrays.html)

---

## Version History

- **1.0.0** (2026-01-14): Initial release - extracted from workspace-hub configuration scripts

## Sub-Skills

- [1. Key=Value Configuration Parsing (+1)](1-keyvalue-configuration-parsing/SKILL.md)
- [3. JSON Report Generation](3-json-report-generation/SKILL.md)
- [4. Multi-Section INI Parsing](4-multi-section-ini-parsing/SKILL.md)
- [5. Environment Variable Configuration](5-environment-variable-configuration/SKILL.md)
- [6. YAML Configuration (via yq)](6-yaml-configuration-via-yq/SKILL.md)
- [1. Always Provide Defaults (+4)](1-always-provide-defaults/SKILL.md)
