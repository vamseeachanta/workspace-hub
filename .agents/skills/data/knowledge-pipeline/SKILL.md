---
name: knowledge-pipeline
description: Workflow for maintaining workspace-hub knowledge and learning pipelines
  across scripts/knowledge, scripts/learning, and docs/superpowers, including indexing,
  archive synthesis, issue updates, and pipeline troubleshooting.
version: 1.0.0
category: data
type: skill
trigger: manual
auto_execute: false
capabilities:
- knowledge_indexing
- archive_synthesis
- issue_update_automation
- learning_pipeline_maintenance
- knowledge_troubleshooting
tools:
- Read
- Write
- Bash
- Grep
requires: []
tags:
- knowledge
- learning
- pipeline
- indexing
- archive
---

# Knowledge Pipeline

## When to Use

Use this skill when working on the repository's knowledge and learning flow across:
- `scripts/knowledge/`
- `scripts/learning/`
- `docs/superpowers/`

Typical tasks:
- build or refresh knowledge indexes
- synthesize archived material into reusable knowledge
- review or update open issue summaries
- maintain learning scripts that capture patterns from prior work
- debug the flow between knowledge extraction, learning, and documentation artifacts

## Main Data Flow

```text
source material / session artifacts
  -> scripts/knowledge/*
  -> synthesized knowledge / issue updates / index artifacts
  -> scripts/learning/*
  -> reusable lessons, summaries, and pipeline maintenance
  -> docs/superpowers/*
  -> human-readable designs, plans, and reference docs
```

## Directory Roles

### scripts/knowledge/
Primary operational scripts for knowledge handling.
Common patterns include:
- build/update indexes
- query knowledge stores
- synthesize archive/history
- capture summaries
- update GitHub issues from structured knowledge

Relevant scripts on this machine include:
- `build-knowledge-index.sh`
- `query-knowledge.sh`
- `synthesize_archive.py`
- `review-open-issues.py`
- `update-github-issue.py`
- `check-staleness.sh`

### scripts/learning/
Learning-stage automation and maintenance.
Use this area when a workflow turns repeated observations into reusable process improvements.

Current anchor script:
- `scripts/learning/comprehensive-learning.sh`

### docs/superpowers/
Design and planning documentation that explains the higher-level workflow and intended system behavior.
Use this as the narrative/spec layer when code behavior and intended pipeline behavior drift apart.

## Recommended Workflow

1. Inspect the current pipeline surface
   - list scripts under `scripts/knowledge/` and `scripts/learning/`
   - read the closest matching design doc in `docs/superpowers/`
2. Identify the failing or missing stage
   - ingestion/indexing
   - archive synthesis
   - issue update
   - learning/summary generation
3. Run the narrowest script that reproduces the problem
4. Check generated artifacts and downstream consumers
5. Update tests or add a focused regression test
6. Re-run the stage and validate the next stage still receives the expected inputs

## Validation Guidance

Prefer targeted tests where they exist.
Examples in this repo include:
- `scripts/knowledge/tests/test_review_open_issues.py`
- `scripts/knowledge/tests/test_synthesize_archive.py`
- `scripts/knowledge/tests/test_update_github_issue.py`
- `scripts/knowledge/tests/test-knowledge-scripts.sh`

Run targeted validations such as:

```bash
uv run pytest scripts/knowledge/tests/test_review_open_issues.py -q
uv run pytest scripts/knowledge/tests/test_synthesize_archive.py -q
uv run pytest scripts/knowledge/tests/test_update_github_issue.py -q
bash scripts/knowledge/tests/test-knowledge-scripts.sh
```

## Common Failure Modes

- index/build script succeeds but downstream docs are stale
- archive synthesis runs but outputs are not promoted or linked
- issue-update logic drifts from actual GitHub issue format
- learning scripts assume artifact locations that have moved
- docs/superpowers describes a pipeline no longer matching the code

## Troubleshooting Checklist

- verify the source artifact path first
- inspect one known-good output before changing code
- compare intended flow in `docs/superpowers/` against actual script behavior
- keep code-stage and docs-stage fixes aligned
- add regression coverage when fixing a recurring pipeline break
