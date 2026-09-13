---
name: session-corpus-audit
description: Audit session quality, provider log coverage, workflow drift and skill gaps. Reuse existing conversation ratings for product catch-up; distinguish tool events, file reads and review artifacts.
metadata:
  version: 1.1.0
  category: coordination
  author: Hermes Agent (cross-provider methods); Workspace Hub coordination workflow
  tags: [session, audit, quality, signals, cross-agent, skill-gaps]
  related_skills:
    - session-start-routine
    - comprehensive-learning
  hermes:
    tags: [analysis, session-logs, skill-gaps, cross-agent, frequency, orchestrator]
    related_skills: [claude-reflect, skill-eval, repo-architecture-analysis]
---

# Session Corpus Audit

## When to use

- Weekly session quality review or investigation of repeated restarts and tool-call ceiling hits.
- Cross-provider activity baselines, workflow or prompt drift, and skill-gap investigations.
- Conversation-rating provider catch-up using existing rated examples and the established rubric.

## Select a bounded audit

Resolve the owning checkout and authorized log roots from task context. State the
period, providers, source formats and question before reading a corpus. Start with
existing audit receipts and indexes; expand only to evidence needed for the question.
Follow `docs/architecture/agent-data-handling-contract.md`; session text may contain
private messages, credentials or project data. Public reports should use redacted
findings and authorized evidence references, not transcript mirrors.

- **Session quality:** inspect `.claude/state/session-signals/` for repeated stops,
  errors, permission failures and incomplete delivery; verify their meaning.
- **Provider/workflow comparison:** use
  [corpus methods](references/corpus-analysis-methods.md) for format adapters,
  deduplication, file/tool frequencies, prompt drift and skill-gap candidates.
- **Conversation-rating catch-up:** load the rated baseline first, then use
  [the retained rating procedure](references/conversation-rating-provider-catchup.md).
  Provider logs are meta-evidence explaining quality defects, not replacement ratings.

## Evidence and interpretation

Inventory actual sources and schema coverage per provider. Filter post-hook records
only where the schema defines paired pre/post events; use call IDs for other streams
when available. Do not infer format, capability or role from provider name.
Review-only logs cannot supply tool-frequency denominators. Missing observations
remain unknown; zero usage, high tool counts or no commits do not prove wasted work.

Separate explicit skill invocation, file-body reads, discovery exposure and inferred
use. Historical hot/warm/cold/dead scores are prioritization metadata, not deletion
permission. Verify replacements, unique content and current callers before proposing
consolidation. Existing historical observations will not change when code is fixed;
measure later sessions separately to assess improvement.

## Output and continuation

Report scope, scanned/skipped sources, deduplication rules, time basis, measured
counts and limitations. Bind each finding to evidence and its current replacement
or unresolved gap. Rank bounded remedies by demonstrated impact; keep assumptions
and rubric candidates distinct from verified failures.

For technical audit output, prefer an HTML summary and machine-readable evidence;
existing scripts may emit Markdown, which can remain a supporting artifact. Store
private evidence only in its authorized owner. Read back generated outputs and name
what remains unverified. The audit grants no permission to delete skills, publish
logs, mutate Git history or install hooks. Apply shared lifecycle/cleanup controls;
never automatically stash another session's work or rebase to finish an audit.
