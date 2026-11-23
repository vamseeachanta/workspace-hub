# Archived Skill: `github-issue-label-audit-and-command-bundles`

Original path: `/home/vamsee/.hermes/skills/github/github-issue-label-audit-and-command-bundles`
Archived into: `/home/vamsee/.hermes/skills/.archive/umbrella-2026-04-29/github/github-issue-label-audit-and-command-bundles`
Consolidation date: 2026-04-29

---

---
name: github-issue-label-audit-and-command-bundles
description: Safely turn drafted issue bodies into reusable gh issue create commands by auditing repo labels, exact duplicates, and auth first.
version: 1.0.0
author: Hermes Agent
---

# GitHub issue label audit and command bundles

Use when you already have draft issue bodies/titles and want to produce reliable `gh issue create` commands or operator scripts without failing on missing labels or duplicate issues.

## Why this exists
A common failure mode is generating polished `gh issue create` commands that reference labels not present in the target repo. Another is using only broad keyword search and missing an exact-title duplicate check. This skill front-loads those checks before side effects.

## Workflow

1. Confirm target repo and auth
   - `git remote -v`
   - `gh auth status`
   - verify the intended `owner/repo` explicitly instead of assuming the current checkout or script default is correct.

2. Audit live labels before generating commands
   - `gh label list --repo <owner/repo>`
   - compare proposed labels against actual repo taxonomy.
   - if a drafted label does not exist, replace it with an existing repo label rather than leaving a broken command in a reusable script.
   - add an inline note in the generated script documenting which labels were verified and which drafted labels were removed/replaced.

3. Search for duplicates twice
   - broad keyword search for nearby issues:
     - `gh issue list --repo <owner/repo> --state all --search '<keyword1> OR <keyword2>'`
   - exact-title or exact-phrase search for each planned issue title:
     - `gh issue list --repo <owner/repo> --state all --search '"<exact title or distinctive phrase>"'`
   - broad search finds nearby work; exact search catches low-noise duplicates.

4. Generate body files and commands only after the audit
   - prefer `--body-file` over inline body strings.
   - emit copy/paste commands or a shell script only after repo/auth/label/duplicate checks are complete.

5. Re-render and verify the final command bundle
   - execute the script in print mode if possible.
   - confirm printed commands reference only existing labels and the correct repo.

6. If label audit forces changes, patch all related artifacts consistently
   - update the standalone `gh issue create` helper script
   - update any broader operator bundle that embeds those commands
   - re-run the rendered output check afterward

## Good fit examples
- turning review findings into 3-10 follow-up GitHub issues
- preparing operator handoff scripts for issue creation
- building repeatable triage or issue-seeding bundles for a repo with a custom taxonomy

## Pitfalls
- Do not assume labels like `area:*`, `parsing`, or `releases` exist just because they look reasonable.
- Do not rely only on broad keyword search when avoiding duplicates.
- Do not update one script and forget a second operator bundle that embeds the same commands.

## Minimal command checklist
```bash
gh auth status
gh label list --repo <owner/repo>
gh issue list --repo <owner/repo> --state all --search '"<exact title>"'
```

Then generate or patch the reusable `gh issue create` commands.
