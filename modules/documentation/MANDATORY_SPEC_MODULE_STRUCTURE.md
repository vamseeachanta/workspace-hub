# 🚨 MANDATORY: Spec Module Structure Requirement

## Overview

**CRITICAL DIRECTIVE**: All specifications MUST be created in the `specs/modules/[module-name]/` directory structure. This is a MANDATORY requirement enforced across ALL repositories with no exceptions.

## Directory Structure

### ✅ CORRECT Structure
```
repo/
└── specs/
    └── modules/
        ├── auth/
        │   ├── 2025-01-15-user-login/
        │   ├── 2025-01-16-password-reset/
        │   └── 2025-01-17-oauth-integration/
        ├── core/
        │   ├── 2025-01-14-api-gateway/
        │   └── 2025-01-15-database-schema/
        └── utils/
            ├── 2025-01-13-logging-system/
            └── 2025-01-14-error-handling/
```

### ❌ INCORRECT Structures (WILL BE REJECTED)
```
# Wrong - Missing modules level
specs/2025-01-15-feature/           # NO!
.agent-os/specs/2025-01-15-feature/ # NO!

# Wrong - Not under specs/modules
modules/auth/2025-01-15-feature/     # NO!
src/specs/2025-01-15-feature/        # NO!

# Wrong - Module name in wrong position
specs/2025-01-15-auth-feature/       # NO!
specs/auth-modules/feature/          # NO!
```

## Command Usage

### /create-spec Command

**OLD (No longer supported):**
```bash
/create-spec user-authentication
```

**NEW (MANDATORY):**
```bash
/create-spec user-authentication auth
#            ^spec-name          ^module-name (REQUIRED)
```

### /create-spec-enhanced Command

**OLD (No longer supported):**
```bash
/create-spec-enhanced user-authentication
```

**NEW (MANDATORY):**
```bash
/create-spec-enhanced user-authentication auth enhanced
#                     ^spec-name          ^module-name ^variant
```

## Module Naming Guidelines

### Standard Module Names

Use these standard module names when applicable:

| Module Name | Purpose | Examples |
|------------|---------|----------|
| `auth` | Authentication & authorization | Login, OAuth, permissions |
| `core` | Core business logic | Main features, workflows |
| `api` | API endpoints & integrations | REST, GraphQL, webhooks |
| `data` | Data processing & storage | ETL, migrations, schemas |
| `ui` | User interface components | Forms, dashboards, widgets |
| `utils` | Utility functions | Helpers, formatters, validators |
| `infra` | Infrastructure & DevOps | CI/CD, deployment, monitoring |
| `docs` | Documentation specs | Guides, tutorials, references |
| `test` | Testing specifications | E2E, integration, performance |
| `security` | Security features | Encryption, auditing, compliance |

### Custom Module Names

For domain-specific features, use descriptive module names:

```bash
# Good module names
/create-spec vessel-tracking marine-engineering
/create-spec hydrodynamic-analysis simulation
/create-spec mooring-design offshore-structures

# Poor module names (too generic)
/create-spec feature misc        # Too vague
/create-spec update stuff        # Meaningless
/create-spec fix other          # Non-descriptive
```

## Migration Guide

### For Existing Specs

If you have specs in the old structure, migrate them:

```bash
# Old structure
.agent-os/specs/2025-01-15-user-auth/

# Migration steps
mkdir -p specs/modules/auth
mv .agent-os/specs/2025-01-15-user-auth specs/modules/auth/

# Update references in files
# Change: @.agent-os/specs/2025-01-15-user-auth/
# To: @specs/modules/auth/2025-01-15-user-auth/
```

### Bulk Migration Script

```bash
#!/bin/bash
# Migrate all old specs to new structure

# Create modules directory
mkdir -p specs/modules

# Move specs from .agent-os/specs/
if [ -d ".agent-os/specs" ]; then
    for spec in .agent-os/specs/*/; do
        basename=$(basename "$spec")
        # Determine module based on spec name
        if [[ $basename == *"auth"* ]]; then
            module="auth"
        elif [[ $basename == *"api"* ]]; then
            module="api"
        else
            module="core"
        fi
        
        mkdir -p "specs/modules/$module"
        mv "$spec" "specs/modules/$module/"
        echo "Moved $basename to specs/modules/$module/"
    done
fi
```

## Why This Is MANDATORY

### 1. **Organization at Scale**
- Clear categorization of specifications
- Easy navigation in large codebases
- Logical grouping of related features

### 2. **Cross-Repository Consistency**
- Same structure across all 25+ repositories
- Simplified tooling and automation
- Consistent developer experience

### 3. **Module-Based Development**
- Features grouped by functional area
- Clear ownership boundaries
- Simplified dependency tracking

### 4. **Tool Integration**
- `/execute-tasks` knows where to find specs
- `/verify-ai-work` can validate by module
- CI/CD can process by module

## Enforcement

### Command-Level Enforcement

Both `/create-spec` and `/create-spec-enhanced` now:
- **REQUIRE** module name as mandatory parameter
- **REJECT** execution without module name
- **CREATE** specs only in `specs/modules/[module-name]/`

### Error Messages

```bash
# Missing module name
$ /create-spec user-auth
❌ ERROR: Module name is required!
Usage: /create-spec <spec-name> <module-name>
All specs must be created in: specs/modules/[module-name]/

# Correct usage
$ /create-spec user-auth auth
✅ Creating specification: user-auth in module: auth
📁 Created: specs/modules/auth/2025-01-15-user-auth/
```

## Examples

### Example 1: Authentication Feature
```bash
/create-spec oauth-integration auth
# Creates: specs/modules/auth/2025-01-15-oauth-integration/
```

### Example 2: API Endpoint
```bash
/create-spec-enhanced rest-endpoints api enhanced
# Creates: specs/modules/api/2025-01-15-rest-endpoints/
```

### Example 3: Data Processing
```bash
/create-spec etl-pipeline data
# Creates: specs/modules/data/2025-01-15-etl-pipeline/
```

### Example 4: UI Component
```bash
/create-spec-enhanced dashboard-widgets ui minimal
# Creates: specs/modules/ui/2025-01-15-dashboard-widgets/
```

## File References

When referencing specs in documentation or code:

### Old Format (DEPRECATED)
```markdown
See specification: @.agent-os/specs/2025-01-15-feature/spec.md
```

### New Format (REQUIRED)
```markdown
See specification: @specs/modules/auth/2025-01-15-feature/spec.md
```

## Integration with Other Commands

### /execute-tasks
```bash
/execute-tasks @specs/modules/auth/2025-01-15-user-auth/tasks.md
```

### /verify-ai-work
```bash
cd specs/modules/auth/2025-01-15-user-auth/
/verify-ai-work verification-tasks.json
```

## Benefits

### For Developers
- ✅ Clear organization by functional area
- ✅ Easy to find related specifications
- ✅ Consistent across all projects
- ✅ Module-level documentation

### For AI Agents
- ✅ Predictable structure for navigation
- ✅ Module context for better understanding
- ✅ Simplified cross-reference resolution
- ✅ Consistent training data structure

### For Teams
- ✅ Clear ownership by module
- ✅ Simplified code reviews
- ✅ Module-based permissions
- ✅ Easier onboarding

## Troubleshooting

### Issue: Command Still Creating in Old Location
**Solution**: Update to latest version of create-spec commands

### Issue: Can't Find Module Name
**Solution**: Use standard names (auth, core, api, data, ui, utils) or create descriptive domain-specific names

### Issue: References Broken After Migration
**Solution**: Update all @references to use new path structure

## Summary

**Remember:**
- ✅ ALWAYS include module name when creating specs
- ✅ Use `specs/modules/[module-name]/` structure
- ✅ Follow standard module naming when possible
- ❌ NEVER create specs outside module structure
- ❌ NEVER skip the module parameter

**This is MANDATORY and enforced across all repositories!**

---

*Effective immediately for all specification creation across the entire repository ecosystem.*