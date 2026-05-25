# Readiness Issues — 2026-05-25T02:37:16

Nightly readiness: 8 failed, 17 passed

## Warnings
- R-CODEX: MAX_TEAMMATES mismatch — CODEX.md=5 settings.json=
- R-MODEL: stale model IDs found in scripts/: /mnt/local-analysis/workspace-hub/scripts/readiness/nightly-readiness.sh 
- R-REGISTRY: model-registry.yaml 54d old — run update-model-ids.sh
- R-AI-CLI: 16 agent warning(s) — claude codex gemini see ai-readiness.jsonl
- R-PLUGINS: claude CLI not found
- R-HOOK-STATIC: hook violations: plan-approval-gate.sh:blocking-pattern:'git push' capture-corrections.sh:201L>max200 check-encoding.sh:blocking-pattern:'\bcurl\b' check-encoding.sh:blocking-pattern:'https://' check-skill-content.sh:553L>max200 check-skill-content.sh:blocking-pattern:'git commit' check-skill-content.sh:blocking-pattern:'\bcurl\b' check-skill-content.sh:blocking-pattern:'\bwget\b' session-review.sh:361L>max200
- R-PRECOMMIT: assetutilities:legal-sanity-scan.sh entry missing worldenergydata:legal-sanity-scan.sh entry missing assethold:legal-sanity-scan.sh entry missing
- R-TELEGRAM-HERMES: readiness failed — run scripts/readiness/telegram-hermes-readiness.sh

