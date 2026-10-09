---
name: hidden-folder-audit-pre-audit
description: 'Sub-skill of hidden-folder-audit: Pre-Audit (+6).'
version: 1.2.0
category: _internal
type: reference
scripts_exempt: true
---

# Pre-Audit (+6)

## Pre-Audit


- [ ] Working directory is clean (`git status`)
- [ ] Create backup branch: `git checkout -b backup/pre-hidden-audit`
- [ ] Document current state: `ls -la .*/ > hidden-folders-before.txt`

## Discovery Phase


- [ ] List all hidden folders at root level
- [ ] Record size of each hidden folder
- [ ] Identify symlinks and their targets
- [ ] Check git tracking status for each

## Analysis Phase


- [ ] Identify duplicate configurations
- [ ] Find broken symlinks
- [ ] Determine authoritative source for each config type
- [ ] Check for active usage in scripts/CI

## Planning Phase


- [ ] Create target folder structure diagram
- [ ] List files to migrate with source/destination
- [ ] List files/folders to delete
- [ ] Identify scripts/references to update

## Execution Phase


- [ ] Backup folders before migration
- [ ] Migrate content to authoritative locations
- [ ] Update git tracking (`git rm --cached`, `git add`)
- [ ] Remove legacy folders
- [ ] Update .gitignore

## Verification Phase


- [ ] Run tests to ensure nothing broke
- [ ] Verify symlinks work (if any remain)
- [ ] Confirm scripts still function
- [ ] Check CI/CD pipelines
- [ ] Commit with descriptive message

## Documentation Phase


- [ ] Update README if folder structure changed
- [ ] Document new standard in CLAUDE.md or equivalent
- [ ] Remove references to legacy folders in docs
