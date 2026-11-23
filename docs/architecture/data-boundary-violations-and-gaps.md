# Data Boundary Violations and Gaps — Issue #2727

The following YAML is intentionally machine-readable so future issue creation can reuse the evidence without re-discovering the same path drift.

```yaml
generated: '2026-05-18T15:37:13Z'
issue: 2727
searches:
- command: git grep -n -- '/mnt/ace-data' -- . ':!docs/plans/**' ':!scripts/review/results/**'
  machine: ace-linux-1
  timestamp: '2026-05-18T15:37:13Z'
  paths_scanned:
  - workspace-hub tracked files excluding plan/review artifacts
  excluded_patterns:
  - docs/plans/**
  - scripts/review/results/**
  matches: tracked references remain in skills, legacy analysis artifacts, operations
    scripts, and logs; see sanitized runtime probe summary captured in this artifact
  conclusion: Do not canonize /mnt/ace-data; file follow-up cleanup/migration work.
- command: git grep -n -E 'client_confidential|private_client_wiki_target|private mount paths|/mnt/ace/<' -- docs tests ':!docs/plans/**' ':!scripts/review/results/**'
  machine: ace-linux-1
  timestamp: '2026-05-18T15:37:13Z'
  paths_scanned:
  - docs
  - tests
  excluded_patterns:
  - docs/plans/**
  - scripts/review/results/**
  matches: literal private/client path references exist in legacy docs/session handoffs;
    no new public inventory preserves exact client roots
  conclusion: 'Treat as boundary-review candidates; new #2727 artifacts use generalized
    placeholders.'
follow_up_not_filed_reason: Follow-up issues are drafted here but intentionally not filed by this implementation packet; issue creation remains a separate planning/governance action to avoid expanding #2727 execution scope.
follow_up_issue_drafts:
- title: 'chore(data-governance): migrate durable references away from /mnt/ace-data
    alias before symlink deletion'
  body_file: docs/architecture/followups/issue-migrate-ace-data-alias.md
  gh_issue_create_command: 'gh issue create --title "chore(data-governance): migrate
    durable references away from /mnt/ace-data alias before symlink deletion" --body-file
    docs/architecture/followups/issue-migrate-ace-data-alias.md --label cat:data-pipeline
    --label status:planning'
- title: 'feat(data-governance): define canonical llm-wiki private/public repo placement
    under /mnt/local-analysis'
  body_file: docs/architecture/followups/issue-canonical-llm-wiki-repo-placement.md
  gh_issue_create_command: 'gh issue create --title "feat(data-governance): define
    canonical llm-wiki private/public repo placement under /mnt/local-analysis" --body-file
    docs/architecture/followups/issue-canonical-llm-wiki-repo-placement.md --label
    cat:data-pipeline --label status:planning'
```
