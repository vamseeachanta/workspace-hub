> Git-tracked session-log portability guidance. Captured: 2026-04-11
> Source: provider session ecosystem audit + local orchestrator inventory on ace-linux-1

---
name: Session log portability and provider observability
description: How machine-local provider session stores become portable repo knowledge, and how to interpret provider-audit drift safely
type: memory
---

# Session Log Portability

## Core model

Treat provider session observability as a 3-stage pipeline:

1. Native provider store — machine-local, provider-managed
   - Codex: `~/.codex/sessions/`
   - Gemini: `~/.gemini/tmp/`
   - Hermes: `~/.hermes/`
   - Claude: repo-local hook outputs plus provider-specific local state
2. Exported orchestrator JSONL — machine-local, repo gitignored
   - `logs/orchestrator/<provider>/session_*.jsonl`
3. Portable tracked artifacts — safe to share across machines via git
   - `analysis/provider-session-ecosystem-audit.json`
   - `docs/reports/provider-session-ecosystem-audit.md`
   - repo-tracked memory/docs that summarize durable learnings

Rule: do not try to sync raw session logs across machines. Promote signal, not raw exhaust.

## Canonical operator sequence

When refreshing provider observability on a machine:

1. Run provider exports first
   - `bash scripts/cron/hermes-session-export.sh`
   - `bash scripts/cron/codex-session-export.sh`
   - `bash scripts/cron/gemini-session-export.sh`
2. Then run the audit
   - `bash scripts/cron/provider-session-ecosystem-audit.sh`
3. Then promote only durable findings into repo-tracked docs/memory if needed

If exports are stale, the audit is stale.

## Interpreting missing-path drift

High-volume missing repo reads in the provider audit usually mean migration debt, not a mandate to restore deleted files.

Expected behavior:
- consult `docs/ops/legacy-claude-reference-map.md`
- redirect agents toward current workflow surfaces
- treat stale reads as evidence of old habits or old prompts still circulating
- only recreate a removed file if a current, verified integration truly requires it

The recurring pattern on this machine was concentrated in legacy work-queue and legacy skill paths, especially for Claude. That is a redirect problem, not a resurrection problem.

## Provider-specific notes

### Hermes

Hermes has extra observability artifacts beyond `session_*.jsonl`:
- `logs/orchestrator/hermes/corrections/session_*.jsonl`
- `logs/orchestrator/hermes/skill-patches.jsonl`

These reflect Hermes-specific correction and skill-patching behavior. Do not expect the same artifact types from Codex or Gemini.

### Claude

Current raw Claude orchestrator logs do not provide reliable `session_id` coverage for historical corpus slices. When analyzing old Claude data, prefer file/date-level aggregation unless newer logger outputs explicitly include `session_id`.

## What belongs in portable memory

Good candidates for promotion:
- architectural rules about local-only vs tracked artifacts
- stable export/audit workflow rules
- recurring interpretation rules for stale-path drift
- provider-specific observability quirks that change analysis behavior

Bad candidates for promotion:
- daily file counts
- top-tool rankings from one audit run
- transient dirty-worktree state
- raw issue/task execution summaries

## Recommended placement

Use these targets deliberately:
- `logs/orchestrator/README.md` — operator-facing structure and command sequence
- `.claude/memory/KNOWLEDGE.md` — short institutional rules only
- `.claude/memory/topics/session-log-portability.md` — richer operational guidance
- `docs/reports/*.md` — dated transfer or analysis reports

Short memory should hold the rule. Topic files should hold the nuance.
