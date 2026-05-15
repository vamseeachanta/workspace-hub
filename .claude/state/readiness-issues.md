# Readiness Issues — 2026-05-15T02:03:07

Nightly readiness: 6 failed, 18 passed

## Warnings
- R-CODEX: MAX_TEAMMATES mismatch — CODEX.md=5 settings.json=
- R-MODEL: stale model IDs found in scripts/: /mnt/local-analysis/workspace-hub/scripts/readiness/nightly-readiness.sh 
- R-REGISTRY: model-registry.yaml 44d old — run update-model-ids.sh
- R-AI-CLI: 14 agent warning(s) — codex gemini see ai-readiness.jsonl
- R-PLUGINS: missing required plugins: frontend-design skill-creator code-review pr-review-toolkit feature-dev playground pyright-lsp claude-md-management hookify superpowers
- R-HOOK-STATIC: hook violations: plan-approval-gate.sh:blocking-pattern:'git push' capture-corrections.sh:201L>max200 check-encoding.sh:blocking-pattern:'\bcurl\b' check-encoding.sh:blocking-pattern:'https://' check-skill-content.sh:553L>max200 check-skill-content.sh:blocking-pattern:'git commit' check-skill-content.sh:blocking-pattern:'\bcurl\b' check-skill-content.sh:blocking-pattern:'\bwget\b' session-review.sh:361L>max200

