# Readiness Issues — 2026-05-31T18:02:51

Nightly readiness: 7 failed, 15 passed

## Warnings
- R-MODEL: stale model IDs found in scripts/: /c/workspace-hub/scripts/readiness/nightly-readiness.sh 
- R-AI-CLI: 16 agent warning(s) — claude codex gemini see ai-readiness.jsonl
- R-UX: 1 UX gap(s) — FAIL  ~/.claude/keybindings.json absent — submit key inconsistent across machines;
- R-JQ: jq not found — install with: sudo apt-get install jq
- R-PLUGINS: missing required plugins: frontend-design skill-creator code-review pr-review-toolkit feature-dev playground pyright-lsp claude-md-management hookify superpowers
- R-HOOK-STATIC: hook violations: capture-corrections.sh:201L>max200 check-encoding.sh:blocking-pattern:'\bcurl\b' check-encoding.sh:blocking-pattern:'https://' check-skill-content.sh:553L>max200 check-skill-content.sh:blocking-pattern:'git commit' check-skill-content.sh:blocking-pattern:'\bcurl\b' check-skill-content.sh:blocking-pattern:'\bwget\b' plan-approval-gate.sh:blocking-pattern:'git push' session-review.sh:361L>max200
- R-PRECOMMIT: assetutilities:legal-sanity-scan.sh entry missing worldenergydata:legal-sanity-scan.sh entry missing
- R-TELEGRAM-HERMES: readiness failed — run scripts/readiness/telegram-hermes-readiness.sh

