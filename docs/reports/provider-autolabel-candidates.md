# Provider autolabel candidates

Generated: 2026-09-17T09:21:16.578085Z
Apply mode: False
Threshold: 0.9

| Issue | Target label | Confidence | Eligible | Reasons |
|---|---|---:|---|---|
| #3740 867 issues cannot leave dispatch:ready — nothing advances dispatch state | agent:codex | 0.95 | yes | execution-ready, priority-labeled, strong-codex-language-match, provider-highest-priority |
| #3839 fix(digitalmodel/fatigue): two of four rainflow paths understate stress range, understating damage | agent:codex | 0.95 | yes | execution-ready, priority-labeled, strong-codex-language-match, provider-highest-priority |
| #3816 feat(repo): generate authoritative work-surface inventory and adapter coverage report | agent:claude | 0.90 | yes | execution-ready, priority-labeled, strong-claude-language-match, provider-high-priority |
| #3838 fix(digitalmodel/orcaflex): three verified model-building integrity defects with silent failure modes | agent:claude | 0.90 | yes | execution-ready, priority-labeled, strong-claude-language-match, provider-high-priority |
| #3843 refactor(orcaflex): consolidate four model generators onto modular_generator | agent:claude | 0.90 | yes | execution-ready, priority-labeled, strong-claude-language-match, provider-high-priority |
| #3566 fix(agent-ux): make keyboard and context-menu text paste equivalent in Codex CLI | agent:claude | 0.90 | yes | execution-ready, priority-labeled, strong-claude-language-match, provider-high-priority |
| #3568 epic(agent-ux): cross-machine input interaction parity | agent:claude | 0.90 | yes | execution-ready, priority-labeled, strong-claude-language-match, provider-high-priority |
| #3554 bug(equality): Windows publish-equality misclassifies missing flock as contention and reports success | agent:codex | 0.80 | no | execution-ready, strong-codex-language-match, provider-highest-priority |
| #3571 equality/reconcile tooling gaps on ace-win-1: junction-following restore wiped canonical skills; Windows host-identity + flock gaps | agent:codex | 0.80 | no | execution-ready, strong-codex-language-match, provider-highest-priority |
| #3787 pytest pays a large fixed startup tax before any test runs — 38s git call, 59MB DB query on collect-only, 487 hidden test files | agent:codex | 0.80 | no | execution-ready, strong-codex-language-match, provider-highest-priority |
| #3573 feat(ai-orchestration): replace gemini with agy as the third worker/reviewer provider ecosystem-wide | agent:claude | 0.75 | no | execution-ready, strong-claude-language-match, provider-high-priority |
| #3578 fix(review): submit-to-codex.sh hangs — codex exec exit 124 'Reading additional input from stdin' despite #3294 mitigation | agent:claude | 0.75 | no | execution-ready, strong-claude-language-match, provider-high-priority |
| #3592 equality matrix: reclassify harness/scheduler/memory rows — uniform vote mis-grades per-role differences + Windows placeholder data poisons majority | agent:claude | 0.75 | no | execution-ready, strong-claude-language-match, provider-high-priority |
| #3788 bug(dispatch): reconcile.py reads an open-only label snapshot, so every CLOSED issue reports false LABEL-MISSING | agent:codex | 0.60 | no | priority-labeled, strong-codex-language-match, provider-highest-priority |
| #3821 bug(equality): restore collector idempotency and macOS atomic-publish test portability | agent:codex | 0.60 | no | priority-labeled, strong-codex-language-match, provider-highest-priority |
| #3585 phone-media: EXIF-date organizer + cross-phone dedupe | agent:codex | 0.60 | no | priority-labeled, strong-codex-language-match, provider-highest-priority |
| #3819 feat(harness): unified ecosystem doctor with stable probe schema | agent:agy | 0.60 | no | priority-labeled, strong-agy-language-match, provider-highest-priority |
| #3717 Context budget: harness config is 3.6% of the window — the cost is tool output (17%), not CLAUDE.md | agent:agy | 0.45 | no | strong-agy-language-match, provider-highest-priority |
