---
name: repo-readiness-execution-checklist
description: 'Sub-skill of repo-readiness: Execution Checklist.'
version: 1.0.0
category: coordination
type: reference
scripts_exempt: true
---

# Execution Checklist

## Execution Checklist


**Pre-Check:**
- [ ] Repository path is valid
- [ ] Git repository initialized
- [ ] Read access to all files

**Analysis Phase:**
- [ ] Read CLAUDE.md (root and .claude/)
- [ ] Analyze directory structure
- [ ] Extract mission from .agent-os/
- [ ] Check git status
- [ ] Verify environment setup
- [ ] Validate standards compliance

**Reporting Phase:**
- [ ] Generate configuration summary
- [ ] Create structure assessment
- [ ] Extract mission & objectives
- [ ] Report repository state
- [ ] Calculate readiness score
- [ ] Provide recommended actions

**Post-Check:**
- [ ] Save readiness report to .claude/readiness-report.md
- [ ] Update repository context cache
- [ ] Provide summary to user or agent
