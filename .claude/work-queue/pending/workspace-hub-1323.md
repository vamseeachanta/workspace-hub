---
id: workspace-hub#1323
title: "Target problem-set textbooks for deep extraction to reach 150+ worked examples"
type: standard
status: pending
priority: medium
complexity: moderate
route: B
created_at: 2026-03-24
target_repos: [workspace-hub]
computer: dev-primary
plan_workstations: [dev-primary]
execution_workstations: [dev-primary]
category: document-intelligence
subcategory: knowledge-extraction
parent: WRK-1339
blocked_by: []
github_issue_ref: https://github.com/vamseeachanta/workspace-hub/issues/1323
---

## Mission

Identify textbooks with explicit worked examples/problem sets and run targeted deep extraction
to increase the worked example count from 82 to 150+.

## Context (from WRK-1369)

26 of 44 naval architecture manifests yielded 0 worked examples because they are
standards/references (SOLAS, ABS, DNV RPs) without step-by-step problems.

Top 3 current sources: EN400 (31), Biran (22), Attwood (16).

## What

1. Audit remaining textbook manifests for problem-set content
2. Identify candidates: Basic Ship Theory Vol 2, PNA stability chapters, others
3. Tune deep-extract.py parsers for identified textbook formats
4. Run targeted extraction on high-yield candidates
5. Verify total indexed examples >= 150
