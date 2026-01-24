# Phase 1 Project Board Setup Guide

> This guide provides step-by-step instructions for setting up the GitHub Project Board for Phase 1 consolidation tasks.

## Overview

**Project Name:** Phase 1: Foundation Tasks
**Description:** Foundation consolidation of aceengineercode into digitalmodel - Configuration (1.1), Mathematical Solvers (1.2), Utilities Deduplication (1.3), Data Models (1.4), Database Layer (1.5)
**Timeline:** 3 weeks (21 days)
**Team:** Infrastructure Lead + Full-Stack Developer

---

## Manual Setup Instructions

### Step 1: Create the Project Board

1. Navigate to: https://github.com/vamseeachanta/workspace-hub/projects
2. Click **"New Project"** button
3. Enter project details:
   - **Project name:** `Phase 1: Foundation Tasks`
   - **Description:** `Foundation consolidation: Configuration (1.1), Solvers (1.2), Utilities (1.3), Models (1.4), Database (1.5)`
   - **Template:** Select "Table" (allows custom fields and better task tracking)
4. Click **"Create project"**

### Step 2: Configure Project Columns

The project should have these columns for workflow tracking:

| Column | Purpose | WIP Limit |
|--------|---------|-----------|
| **Not Started** | Task created, not yet assigned | None |
| **In Progress** | Task assigned and work underway | 2 max |
| **Review** | Code review in progress | 3 max |
| **Testing** | Integration/performance testing | 2 max |
| **Done** | Task completed and merged | None |

**Setup Instructions:**
1. Click **"+ Add column"** for each missing column
2. Configure WIP limits:
   - Click column header → **Settings** → Set WIP limit
3. Add automation:
   - In Progress: Auto-add when PR opened
   - Review: Auto-add when PR review requested
   - Done: Auto-add when PR merged

### Step 3: Link GitHub Issues to Project

Link the 5 Phase 1 GitHub issues:

- **Issue #123:** Task 1.1 Configuration Framework → Assigned to Infrastructure Lead
- **Issue #124:** Task 1.2 Mathematical Solvers → Assigned to Full-Stack Developer
- **Issue #125:** Task 1.3 Utilities Deduplication → Assigned to Both (parallel)
- **Issue #126:** Task 1.4 Data Models → Assigned to Full-Stack Developer
- **Issue #127:** Task 1.5 Database Layer → Assigned to Infrastructure Lead

**Linking Instructions:**
1. Navigate to each issue (#123-#127)
2. In the right sidebar, click **"Projects"**
3. Select **"Phase 1: Foundation Tasks"** project
4. Set Status field to **"Not Started"**

### Step 4: Configure Custom Fields

Add these custom fields to track additional metadata:

| Field Name | Type | Values |
|-----------|------|--------|
| **Task Phase** | Single select | Phase 1, Phase 2, Phase 3, Phase 4 |
| **Assigned To** | Single select | Infrastructure Lead, Full-Stack Developer, Both |
| **Estimated Hours** | Number | (hours estimated) |
| **Priority** | Single select | Critical, High, Medium, Low |
| **Dependencies** | Text | (list blocking tasks) |

### Step 5: Set Up Automation Rules

Configure GitHub project automation for workflow efficiency:

**When PR is opened:**
- Move card to "In Progress"

**When PR is marked as "needs review":**
- Move card to "Review"

**When PR is merged:**
- Move card to "Done"

**When issue is closed:**
- Move card to "Done"

---

## Project Board Template JSON

If using GitHub Projects API (v4 GraphQL), use this configuration:

```json
{
  "name": "Phase 1: Foundation Tasks",
  "description": "Foundation consolidation: Configuration (1.1), Solvers (1.2), Utilities (1.3), Models (1.4), Database (1.5)",
  "template": "TABLE",
  "columns": [
    {
      "name": "Not Started",
      "purpose": "Task created, not yet assigned"
    },
    {
      "name": "In Progress",
      "purpose": "Task assigned and work underway",
      "wip_limit": 2
    },
    {
      "name": "Review",
      "purpose": "Code review in progress",
      "wip_limit": 3
    },
    {
      "name": "Testing",
      "purpose": "Integration/performance testing",
      "wip_limit": 2
    },
    {
      "name": "Done",
      "purpose": "Task completed and merged"
    }
  ],
  "custom_fields": [
    {
      "name": "Task Phase",
      "type": "single_select",
      "options": ["Phase 1", "Phase 2", "Phase 3", "Phase 4"]
    },
    {
      "name": "Assigned To",
      "type": "single_select",
      "options": ["Infrastructure Lead", "Full-Stack Developer", "Both"]
    },
    {
      "name": "Estimated Hours",
      "type": "number"
    },
    {
      "name": "Priority",
      "type": "single_select",
      "options": ["Critical", "High", "Medium", "Low"]
    }
  ]
}
```

---

## Initial Project Setup

### Task Cards to Create/Link

| Issue # | Task Title | Assigned | Hours | Priority |
|---------|-----------|----------|-------|----------|
| #123 | Configuration Framework | Infrastructure Lead | 25-30 | Critical |
| #124 | Mathematical Solvers | Full-Stack Developer | 35-40 | Critical |
| #125 | Utilities Deduplication | Both | 45-50 | Critical |
| #126 | Data Models | Full-Stack Developer | 30-35 | Critical |
| #127 | Database Layer | Infrastructure Lead | 40-45 | Critical |

**Total Effort:** 175-200 hours over 3 weeks

### Field Values for Each Task

**Task 1.1 - Configuration Framework:**
- Task Phase: Phase 1
- Assigned To: Infrastructure Lead
- Estimated Hours: 25-30
- Priority: Critical
- Dependencies: None (critical path)

**Task 1.2 - Mathematical Solvers:**
- Task Phase: Phase 1
- Assigned To: Full-Stack Developer
- Estimated Hours: 35-40
- Priority: Critical
- Dependencies: Blocked by Task 1.1

**Task 1.3 - Utilities Deduplication:**
- Task Phase: Phase 1
- Assigned To: Both
- Estimated Hours: 45-50
- Priority: Critical
- Dependencies: Blocked by Task 1.1 (partial)

**Task 1.4 - Data Models:**
- Task Phase: Phase 1
- Assigned To: Full-Stack Developer
- Estimated Hours: 30-35
- Priority: Critical
- Dependencies: Blocked by Task 1.1

**Task 1.5 - Database Layer:**
- Task Phase: Phase 1
- Assigned To: Infrastructure Lead
- Estimated Hours: 40-45
- Priority: Critical
- Dependencies: Blocked by Task 1.4

---

## Monitoring & Status

### Weekly Status Check Points

**Every Friday:**
1. Review project board progress
2. Verify WIP limits are respected
3. Check for blocked tasks
4. Update estimated remaining hours
5. Identify risks/blockers for Monday standup

### Success Criteria

- All 5 Phase 1 tasks completed within 3-week window
- Test coverage maintained at 90%+
- No blocked tasks lasting >24 hours
- All PRs reviewed and merged within 24 hours
- Zero production incidents from consolidation work

---

## Related Documentation

- [Phase 1 Preflight Checklist](phase1-preflight-checklist.md)
- [Phase 1 Task Specifications](PHASE_1_TASK_SPECIFICATIONS.md)
- [Phase 1 Execution Log](phase1-execution-log.md)
- [Phase 1 Processes](phase1-processes.md)

---

## Next Steps

1. **Create project board** using instructions above
2. **Link GitHub issues** #123-#127 to project
3. **Configure automation** for PR/issue workflow
4. **Schedule team kickoff** meeting (reference docs/phase1-processes.md)
5. **Begin Phase 1 execution** once team is aligned

---

*Last Updated: 2025-12-26*
*Part of Phase 1 Pre-Execution Setup*
