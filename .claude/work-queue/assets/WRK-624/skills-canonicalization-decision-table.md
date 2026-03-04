# Skills Canonicalization Decision Table

Generated: 2026-03-04

Policy: each `_archive` / `_diverged` skill must be either **canonicalized** or **deleted**.

| # | Bucket | Path | Action | Canonical Target | Rationale | Captured | Status | Comment |
|---|---|---|---|---|---|---|---|---|
| 1 | diverged-unmatched | `.claude/skills/_diverged/digitalmodel/automation/windmill/SKILL.md` | canonicalize | operations/automation/windmill | Core automation skill; keep as active canonical. | YES | DONE | Canonical file exists and diverged canonical_ref is aligned. |
| 2 | diverged-unmatched | `.claude/skills/_diverged/digitalmodel/automation/airflow/SKILL.md` | canonicalize | operations/automation/airflow | Core automation skill; keep as active canonical. | YES | DONE | Canonical file exists and diverged canonical_ref is aligned. |
| 3 | diverged-unmatched | `.claude/skills/_diverged/digitalmodel/automation/n8n/SKILL.md` | canonicalize | operations/automation/n8n | Core automation skill; keep as active canonical. | YES | DONE | Canonical file exists and diverged canonical_ref is aligned. |
| 4 | diverged-unmatched | `.claude/skills/_diverged/digitalmodel/automation/activepieces/SKILL.md` | canonicalize | operations/automation/activepieces | Core automation skill; keep as active canonical. | YES | DONE | Canonical file exists and diverged canonical_ref is aligned. |
| 5 | diverged-unmatched | `.claude/skills/_diverged/digitalmodel/documentation/sphinx/SKILL.md` | canonicalize | development/documentation/sphinx | Documentation tool skill should be canonical. | YES | DONE | Canonical file exists and diverged canonical_ref is aligned. |
| 6 | diverged-unmatched | `.claude/skills/_diverged/digitalmodel/documentation/pandoc/SKILL.md` | canonicalize | development/documentation/pandoc | Documentation tool skill should be canonical. | YES | DONE | Canonical file exists and diverged canonical_ref is aligned. |
| 7 | diverged-unmatched | `.claude/skills/_diverged/digitalmodel/documentation/mkdocs/SKILL.md` | canonicalize | _internal/documentation/mkdocs | Map to existing active mkdocs canonical. | YES | DONE | Canonical file exists and diverged canonical_ref is aligned. |
| 8 | diverged-unmatched | `.claude/skills/_diverged/digitalmodel/documentation/marp/SKILL.md` | canonicalize | development/documentation/marp | Documentation tool skill should be canonical. | YES | DONE | Canonical file exists and diverged canonical_ref is aligned. |
| 9 | diverged-unmatched | `.claude/skills/_diverged/digitalmodel/documentation/docusaurus/SKILL.md` | canonicalize | development/documentation/docusaurus | Documentation tool skill should be canonical. | YES | DONE | Canonical file exists and diverged canonical_ref is aligned. |
| 10 | diverged-unmatched | `.claude/skills/_diverged/digitalmodel/documentation/gitbook/SKILL.md` | canonicalize | development/documentation/gitbook | Documentation tool skill should be canonical. | YES | DONE | Canonical file exists and diverged canonical_ref is aligned. |
| 11 | diverged-unmatched | `.claude/skills/_diverged/digitalmodel/ai-prompting/agenta/SKILL.md` | canonicalize | ai/prompting/agenta | Prompt platform skill should be canonical. | YES | DONE | Canonical file exists and diverged canonical_ref is aligned. |
| 12 | diverged-unmatched | `.claude/skills/_diverged/digitalmodel/ai-prompting/dspy/SKILL.md` | canonicalize | ai/prompting/dspy | Prompt platform skill should be canonical. | YES | DONE | Canonical file exists and diverged canonical_ref is aligned. |
| 13 | diverged-unmatched | `.claude/skills/_diverged/digitalmodel/ai-prompting/langchain/SKILL.md` | canonicalize | ai/prompting/langchain | Prompt platform skill should be canonical. | YES | DONE | Canonical file exists and diverged canonical_ref is aligned. |
| 14 | diverged-unmatched | `.claude/skills/_diverged/digitalmodel/ai-prompting/pandasai/SKILL.md` | canonicalize | ai/prompting/pandasai | Prompt platform skill should be canonical. | YES | DONE | Canonical file exists and diverged canonical_ref is aligned. |
| 15 | diverged-unmatched | `.claude/skills/_diverged/worldenergydata/_internal/meta/python-code-refactor/SKILL.md` | delete | - | Repo-specific legacy variant; no shared canonical destination. | YES | DONE | Deleted. |
| 16 | archive-orphan | `.claude/skills/_archive/_core/agents/memory-systems/SKILL.md` | delete | - | Archive-only legacy variant; no active canonical mapping. | YES | DONE | Deleted. |
| 17 | archive-orphan | `.claude/skills/_archive/_core/agents/multi-agent-patterns/SKILL.md` | delete | - | Archive-only legacy variant; no active canonical mapping. | YES | DONE | Deleted. |
| 18 | archive-orphan | `.claude/skills/_archive/_core/agents/parallel-dispatch/SKILL.md` | delete | - | Archive-only legacy variant; no active canonical mapping. | YES | DONE | Deleted. |
| 19 | archive-orphan | `.claude/skills/_archive/_internal/documentation/docusaurus/SKILL.md` | delete | - | Archive-only legacy variant; no active canonical mapping. | YES | DONE | Deleted. |
| 20 | archive-orphan | `.claude/skills/_archive/_internal/documentation/gitbook/SKILL.md` | delete | - | Archive-only legacy variant; no active canonical mapping. | YES | DONE | Deleted. |
| 21 | archive-orphan | `.claude/skills/_archive/_internal/documentation/marp/SKILL.md` | delete | - | Archive-only legacy variant; no active canonical mapping. | YES | DONE | Deleted. |
| 22 | archive-orphan | `.claude/skills/_archive/_internal/documentation/pandoc/SKILL.md` | delete | - | Archive-only legacy variant; no active canonical mapping. | YES | DONE | Deleted. |
| 23 | archive-orphan | `.claude/skills/_archive/_internal/documentation/sphinx/SKILL.md` | delete | - | Archive-only legacy variant; no active canonical mapping. | YES | DONE | Deleted. |
| 24 | archive-orphan | `.claude/skills/_archive/ai/prompting/agenta/SKILL.md` | delete | - | Archive-only legacy variant; no active canonical mapping. | YES | DONE | Deleted. |
| 25 | archive-orphan | `.claude/skills/_archive/ai/prompting/dspy/SKILL.md` | delete | - | Archive-only legacy variant; no active canonical mapping. | YES | DONE | Deleted. |
| 26 | archive-orphan | `.claude/skills/_archive/ai/prompting/langchain/SKILL.md` | delete | - | Archive-only legacy variant; no active canonical mapping. | YES | DONE | Deleted. |
| 27 | archive-orphan | `.claude/skills/_archive/ai/prompting/pandasai/SKILL.md` | delete | - | Archive-only legacy variant; no active canonical mapping. | YES | DONE | Deleted. |
| 28 | archive-orphan | `.claude/skills/_archive/coordination/workspace/ai-questioning-pattern/SKILL.md` | delete | - | Archive-only legacy variant; no active canonical mapping. | YES | DONE | Deleted. |
| 29 | archive-orphan | `.claude/skills/_archive/coordination/workspace/auto-generated/auto-sync-batch-update-2026-01/SKILL.md` | delete | - | Archive-only legacy variant; no active canonical mapping. | YES | DONE | Deleted. |
| 30 | archive-orphan | `.claude/skills/_archive/coordination/workspace/auto-generated/refactor-migrate-claude-md-to-/SKILL.md` | delete | - | Archive-only legacy variant; no active canonical mapping. | YES | DONE | Deleted. |
| 31 | archive-orphan | `.claude/skills/_archive/coordination/workspace/compliance-propagation-automator/SKILL.md` | delete | - | Archive-only legacy variant; no active canonical mapping. | YES | DONE | Deleted. |
| 32 | archive-orphan | `.claude/skills/_archive/coordination/workspace/file-organization-assistant/SKILL.md` | delete | - | Archive-only legacy variant; no active canonical mapping. | YES | DONE | Deleted. |
| 33 | archive-orphan | `.claude/skills/_archive/coordination/workspace/html-reporting-enforcer/SKILL.md` | delete | - | Archive-only legacy variant; no active canonical mapping. | YES | DONE | Deleted. |
| 34 | archive-orphan | `.claude/skills/_archive/coordination/workspace/knowledge-base-system/SKILL.md` | delete | - | Archive-only legacy variant; no active canonical mapping. | YES | DONE | Deleted. |
| 35 | archive-orphan | `.claude/skills/_archive/coordination/workspace/productivity/SKILL.md` | delete | - | Archive-only legacy variant; no active canonical mapping. | YES | DONE | Deleted. |
| 36 | archive-orphan | `.claude/skills/_archive/coordination/workspace/repository-health-analyzer/SKILL.md` | delete | - | Archive-only legacy variant; no active canonical mapping. | YES | DONE | Deleted. |
| 37 | archive-orphan | `.claude/skills/_archive/coordination/workspace/workspace-hub-compliance/SKILL.md` | delete | - | Archive-only legacy variant; no active canonical mapping. | YES | DONE | Deleted. |
| 38 | archive-orphan | `.claude/skills/_archive/operations/automation/activepieces/SKILL.md` | delete | - | Archive-only legacy variant; no active canonical mapping. | YES | DONE | Deleted. |
| 39 | archive-orphan | `.claude/skills/_archive/operations/automation/airflow/SKILL.md` | delete | - | Archive-only legacy variant; no active canonical mapping. | YES | DONE | Deleted. |
| 40 | archive-orphan | `.claude/skills/_archive/operations/automation/n8n/SKILL.md` | delete | - | Archive-only legacy variant; no active canonical mapping. | YES | DONE | Deleted. |
| 41 | archive-orphan | `.claude/skills/_archive/operations/automation/windmill/SKILL.md` | delete | - | Archive-only legacy variant; no active canonical mapping. | YES | DONE | Deleted. |
| 42 | archive-orphan | `.claude/skills/_archive/workspace-hub/auto-generated/auto-sync-batch-update-2026-01/SKILL.md` | delete | - | Archive-only legacy variant; no active canonical mapping. | YES | DONE | Deleted. |
| 43 | archive-orphan | `.claude/skills/_archive/workspace-hub/auto-generated/chore-sync-with-workspace-hub-/SKILL.md` | delete | - | Archive-only legacy variant; no active canonical mapping. | YES | DONE | Deleted. |
| 44 | archive-orphan | `.claude/skills/_archive/workspace-hub/auto-generated/refactor-migrate-claude-md-to-/SKILL.md` | delete | - | Archive-only legacy variant; no active canonical mapping. | YES | DONE | Deleted. |
