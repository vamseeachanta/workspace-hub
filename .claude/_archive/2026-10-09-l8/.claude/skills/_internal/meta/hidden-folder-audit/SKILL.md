---
name: hidden-folder-audit
description: Audit and consolidate hidden folders in a repository. Identifies duplicates,
  dead directories, and consolidation opportunities for .agent-os/, .ai/, .claude/,
  and other hidden folders.
version: 1.2.0
updated: 2026-01-20
category: _internal
triggers:
- hidden folder audit
- consolidate hidden folders
- .agent-os cleanup
- .ai cleanup
- dot folder review
tags: []
see_also:
- hidden-folder-audit-version-metadata
- hidden-folder-audit-step-1-inventory-all-hidden-folders
- hidden-folder-audit-common-hidden-folders-reference
- hidden-folder-audit-specsarchive
- hidden-folder-audit-migrate-agent-os-to-claude
- hidden-folder-audit-pre-audit
- hidden-folder-audit-verify-hidden-folder-state
---

# Hidden Folder Audit

## When to Use

- Repository has accumulated multiple hidden folders over time
- Multiple AI/agent configuration directories exist (`.agent-os/`, `.ai/`, `.claude/`)
- Symlinks point to non-existent targets
- Unclear which configuration is authoritative
- Preparing for repository restructure or cleanup
- After inheriting or forking a repository
- Before establishing new folder standards

## Related Skills

- [repo-cleanup](../repo-cleanup/SKILL.md) - General repository cleanup
- [module-based-refactor](../module-based-refactor/SKILL.md) - For source code restructuring
- `coordination/session-start-routine/SKILL.md` - Session initialization

## References

- Git ls-files documentation: https://git-scm.com/docs/git-ls-files
- Git check-ignore documentation: https://git-scm.com/docs/git-check-ignore
- Symbolic links in Git: https://git-scm.com/book/en/v2/Git-Internals-Git-References

---

## Version History

- **1.2.0** (2026-01-20): Added Related Directory Patterns section
  - Added benchmarks/ entry to reference table (SPLIT action)
  - Added Related Directory Patterns section for non-hidden directories
  - Added specs/archive/ as standard location for completed plans
  - Added benchmarks/ separation pattern (fixtures vs generated outputs)
  - Updated verification commands for new patterns
- **1.1.0** (2026-01-20): Updated reference table and added verification commands
  - Updated Common Hidden Folders Reference table with verified recommendations
  - Added .drcode/ as DELETE (confirmed legacy AI config)
  - Added .slash-commands/ as CONSOLIDATE to .claude/docs/commands/
  - Added .git-commands/ as CONSOLIDATE to scripts/git/
  - Added .benchmarks/ as DELETE (usually empty)
  - Added .githooks/ as KEEP (standard location)
  - Added Verification Commands section with:
    - Verify Hidden Folder State commands
    - Verify Consolidation Targets commands
    - Verify Git Status commands
    - Final State Checklist script
  - Added Notes column to reference table for additional context
- **1.0.0** (2025-01-20): Initial release based on digitalmodel repository hidden folder audit session

## Sub-Skills

- [Best Practices](best-practices/SKILL.md)

## Sub-Skills

- [Version Metadata](version-metadata/SKILL.md)
- [Step 1: Inventory All Hidden Folders (+4)](step-1-inventory-all-hidden-folders/SKILL.md)
- [Common Hidden Folders Reference](common-hidden-folders-reference/SKILL.md)
- [specs/archive/ (+1)](specsarchive/SKILL.md)
- [Migrate .agent-os to .claude (+4)](migrate-agent-os-to-claude/SKILL.md)
- [Pre-Audit (+6)](pre-audit/SKILL.md)
- [Verify Hidden Folder State (+3)](verify-hidden-folder-state/SKILL.md)
