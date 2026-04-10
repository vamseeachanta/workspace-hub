---
name: repo-cleanup
description: Systematic cleanup of repository clutter including build artifacts, duplicates,
  temp files, and consolidation of scattered directories. Use for repository maintenance,
  artifact removal, directory consolidation, and gitignore updates.
version: 2.2.0
updated: 2026-01-20
category: _internal
triggers:
- repository cleanup
- artifact removal
- temp file cleanup
- duplicate files
- build artifacts
- cache cleanup
- directory consolidation
- gitignore update
- log file cleanup
- untracked files
tags: []
see_also:
- repo-cleanup-version-metadata
- repo-cleanup-1-build-artifacts
- repo-cleanup-agent-directories
- repo-cleanup-common-hidden-folders
- repo-cleanup-conflict-resolution-patterns
- repo-cleanup-progress-tracking-commands
- repo-cleanup-list-untracked-files
- repo-cleanup-for-tracked-files-use-git-rm
- repo-cleanup-gitignore-updates
- repo-cleanup-pre-cleanup
- repo-cleanup-folders-to-delete-confirmed-safe
- repo-cleanup-structure-section-updates
- repo-cleanup-references-to-remove
---

# Repo Cleanup

## When to Use

- Repository has accumulated build artifacts and temp files
- Multiple agent/coordination directories scattered in root
- Log files and coverage reports cluttering the workspace
- Need to consolidate prototype code and test outputs
- Preparing for a clean commit or release
- After major refactoring work

## Related Skills

- [module-based-refactor](../module-based-refactor/SKILL.md) - For restructuring after cleanup
- `coordination/session-start-routine/SKILL.md` - Session initialization

## References

- Git clean documentation: https://git-scm.com/docs/git-clean
- Git rm documentation: https://git-scm.com/docs/git-rm
- Gitignore patterns: https://git-scm.com/docs/gitignore

---

## Version History

- **2.2.0** (2026-01-20): Added Benchmark Cleanup and Plan File Archival patterns
  - Added Benchmark Artifacts section for handling benchmark directories
  - Added Plan Files section for archiving completed specifications
  - Added benchmark patterns to .gitignore recommendations
  - Updated checklist with benchmark and plan archival items
- **2.1.0** (2026-01-20): Added Final Cleanup Checklist and README Update Checklist
  - Added Final Cleanup Checklist with verified DELETE/CONSOLIDATE/KEEP tables
  - Confirmed .drcode/ as safe to delete (legacy AI config)
  - Added .slash-commands/ consolidation to .claude/docs/commands/
  - Added .git-commands/ consolidation to scripts/git/
  - Added .benchmarks/ as safe to delete if empty
  - Added README Update Checklist for structure documentation
  - Added example README structure section template
  - Added references to remove checklist
- **2.0.0** (2026-01-20): Major update with hidden folder cleanup learnings
  - Added Hidden Folder Cleanup section with legacy AI folder patterns
  - Added Consolidation Merge Strategies for conflict resolution
  - Added File Count Verification for tracking consolidation progress
  - Updated Cleanup Checklist with hidden folder review items
  - Documented patterns for .agent-os, .ai, .agent-runtime, .common, .specify, .drcode, .slash-commands
- **1.0.0** (2025-01-20): Initial release based on digitalmodel repository cleanup session

## Sub-Skills

- [Best Practices](best-practices/SKILL.md)

## Sub-Skills

- [Version Metadata](version-metadata/SKILL.md)
- [1. Build Artifacts (+5)](1-build-artifacts/SKILL.md)
- [Agent Directories (+4)](agent-directories/SKILL.md)
- [Common Hidden Folders (+2)](common-hidden-folders/SKILL.md)
- [Conflict Resolution Patterns (+2)](conflict-resolution-patterns/SKILL.md)
- [Progress Tracking Commands (+1)](progress-tracking-commands/SKILL.md)
- [List Untracked Files (+3)](list-untracked-files/SKILL.md)
- [For Tracked Files (Use git rm) (+2)](for-tracked-files-use-git-rm/SKILL.md)
- [Gitignore Updates](gitignore-updates/SKILL.md)
- [Pre-Cleanup (+7)](pre-cleanup/SKILL.md)
- [Folders to DELETE (Confirmed Safe) (+3)](folders-to-delete-confirmed-safe/SKILL.md)
- [Structure Section Updates (+1)](structure-section-updates/SKILL.md)
- [References to Remove](references-to-remove/SKILL.md)
