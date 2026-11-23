# 🚨 MANDATORY: /verify-ai-work Spec Folder Requirement

## Overview

**CRITICAL DIRECTIVE**: The `/verify-ai-work` command MUST be executed from within a repository spec folder. This is a MANDATORY requirement with no exceptions.

## What is a Spec Folder?

A spec folder is a directory that contains specification documents for a feature or task. Valid spec folders are identified by:

### Valid Spec Folder Indicators
1. **Contains `spec.md` file** - Main specification document
2. **Contains `tasks.md` file** - Task breakdown document  
3. **Located under `.agent-os/specs/`** - Agent OS spec directory structure
4. **Is a sub-specs folder** - Contains parent spec.md in parent directory

### Typical Spec Folder Structure
```
.agent-os/specs/2025-01-15-feature-name/
├── spec.md                 # Main specification (REQUIRED)
├── tasks.md                # Task breakdown (REQUIRED)
├── prompt.md               # Prompt history
├── verification_report/    # Created by /verify-ai-work
│   ├── 20250115_143022.json
│   ├── 20250115_153045.json
│   └── 20250115_163012.json
└── sub-specs/
    ├── technical-spec.md
    └── api-spec.md
```

## Execution Requirements

### ✅ VALID Execution Locations

```bash
# Navigate to a spec folder first
cd .agent-os/specs/2025-01-15-user-authentication/
/verify-ai-work tasks.json

# Or from a dated spec folder
cd .agent-os/specs/2025-01-16-api-integration/
/verify-ai-work --sample

# Or from sub-specs (parent must have spec.md)
cd .agent-os/specs/2025-01-15-feature/sub-specs/
/verify-ai-work verification-tasks.md
```

### ❌ INVALID Execution Locations

```bash
# From project root - WILL FAIL
/verify-ai-work tasks.json
# ERROR: /verify-ai-work must be run from a spec folder!

# From random directory - WILL FAIL
cd /home/user/documents/
/verify-ai-work --sample
# ERROR: /verify-ai-work must be run from a spec folder!

# From src directory - WILL FAIL
cd src/components/
/verify-ai-work test.json
# ERROR: /verify-ai-work must be run from a spec folder!
```

## Report Storage Location

All verification reports are saved to a `verification_report` subdirectory within the spec folder:

```
spec-folder/
└── verification_report/
    ├── 20250115_143022.json    # Session from 14:30:22
    ├── 20250115_153045.json    # Session from 15:30:45
    └── 20250115_163012.json    # Session from 16:30:12
```

### Report Naming Format
- **Pattern**: `YYYYMMDD_HHMMSS.json`
- **Example**: `20250115_143022.json`
- **Timezone**: Local system time
- **Uniqueness**: Guaranteed by timestamp precision

## Error Messages and Navigation Help

### When Not in Spec Folder

The command provides helpful navigation guidance:

```
❌ ERROR: /verify-ai-work must be run from a spec folder!

📁 A spec folder contains:
   • spec.md file
   • tasks.md file
   • Or is located under .agent-os/specs/

📍 Found these spec folders you can navigate to:
   cd .agent-os/specs/2025-01-15-user-auth/
   cd .agent-os/specs/2025-01-14-api-endpoints/
   cd .agent-os/specs/2025-01-13-database-schema/

💡 To create a spec folder:
   1. Navigate to your project root
   2. Run: /create-spec to create a new spec
   3. Navigate to the created spec folder
   4. Run: /verify-ai-work
```

## Workflow Integration

### Recommended Workflow

1. **Create a Spec**
   ```bash
   /create-spec user-authentication
   ```

2. **Navigate to Spec Folder**
   ```bash
   cd .agent-os/specs/2025-01-15-user-authentication/
   ```

3. **Execute Tasks**
   ```bash
   /execute-tasks tasks.md
   ```

4. **Verify AI Work**
   ```bash
   /verify-ai-work tasks.md
   ```

5. **Review Reports**
   ```bash
   ls verification_report/
   cat verification_report/20250115_143022.json
   ```

## Benefits of Spec Folder Requirement

### 1. **Organization**
- Reports are automatically organized with their specifications
- Easy to find verification history for specific features
- Clear context for what's being verified

### 2. **Traceability**
- Direct link between spec, implementation, and verification
- Complete audit trail in one location
- Version control friendly structure

### 3. **Context Awareness**
- Verification knows which spec it's testing
- Can reference spec.md and tasks.md directly
- Better AI learning from contextual feedback

### 4. **Prevents Confusion**
- No accidental verification in wrong directories
- Clear separation of different feature verifications
- Consistent report locations across all projects

## Examples

### Example 1: Verifying API Implementation

```bash
# Navigate to API spec folder
cd .agent-os/specs/2025-01-15-rest-api/

# Run verification with API test tasks
/verify-ai-work api-verification-tasks.json

# Reports saved to:
# .agent-os/specs/2025-01-15-rest-api/verification_report/20250115_143022.json
```

### Example 2: Verifying UI Components

```bash
# Navigate to UI spec folder  
cd .agent-os/specs/2025-01-14-dashboard-ui/

# Use sample verification tasks
/verify-ai-work --sample

# Reports saved to:
# .agent-os/specs/2025-01-14-dashboard-ui/verification_report/20250115_153045.json
```

### Example 3: Creating Template in Spec Folder

```bash
# Navigate to spec folder
cd .agent-os/specs/2025-01-16-search-feature/

# Create verification template
/verify-ai-work --create-template

# Edit the template
nano sample_verification_tasks.json

# Run verification
/verify-ai-work sample_verification_tasks.json
```

## Report Structure

Each report contains comprehensive verification data:

```json
{
  "session_id": "20250115_143022",
  "spec_folder": ".agent-os/specs/2025-01-15-user-auth",
  "timestamp": "2025-01-15T14:30:22.123456",
  "total_steps": 5,
  "completed": 4,
  "total_time": 245.3,
  "steps": [...],
  "feedback_log": [...],
  "summary": {
    "success_rate": 80.0,
    "common_issues": [...],
    "improvement_areas": [...]
  }
}
```

## Troubleshooting

### Issue: Command Won't Run
**Solution**: Ensure you're in a valid spec folder with spec.md or tasks.md

### Issue: Can't Find Spec Folders
**Solution**: Run `find . -name "spec.md" -type f` to locate all spec folders

### Issue: Reports Not Saving
**Solution**: Check write permissions in the spec folder

### Issue: Wrong Directory Error
**Solution**: Use the suggested `cd` commands in the error message

## Migration Guide

For existing projects without spec folders:

1. **Create Agent OS Structure**
   ```bash
   mkdir -p .agent-os/specs/
   ```

2. **Create First Spec**
   ```bash
   /create-spec initial-feature
   ```

3. **Move Existing Tasks**
   ```bash
   mv old-tasks.json .agent-os/specs/*/
   ```

4. **Run Verification**
   ```bash
   cd .agent-os/specs/2025-01-15-initial-feature/
   /verify-ai-work old-tasks.json
   ```

## Summary

The mandatory spec folder requirement ensures:
- ✅ Organized verification reports
- ✅ Clear feature context
- ✅ Consistent project structure
- ✅ Better traceability
- ✅ Improved AI learning

**Remember**: Always navigate to a spec folder before running `/verify-ai-work`!

---

*This is a MANDATORY requirement effective immediately for all repositories using the /verify-ai-work command.*