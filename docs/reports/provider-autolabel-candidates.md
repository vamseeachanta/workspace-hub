# Provider autolabel candidates

Generated: 2026-09-11T09:21:33.818760Z
Apply mode: False
Threshold: 0.9

| Issue | Target label | Confidence | Eligible | Reasons |
|---|---|---:|---|---|
| #3516 bug(equivalence): ref blobs keyed by role — same-role boxes (ace-win-1/2) will clobber each other; role detection hardcoded to 2 hosts (gpu-claw published as unknown.json) | agent:codex | 0.95 | yes | execution-ready, priority-labeled, strong-codex-language-match, provider-highest-priority |
| #3740 867 issues cannot leave dispatch:ready — nothing advances dispatch state | agent:codex | 0.95 | yes | execution-ready, priority-labeled, strong-codex-language-match, provider-highest-priority |
| #3500 bug(pre-push): equivalence-state publish loops full tier-1 suite forever — remote ref never created, every push gated as new-branch RUN_ALL (sub-case of #3198) | agent:claude | 0.90 | yes | execution-ready, priority-labeled, strong-claude-language-match, provider-high-priority |
| #3549 feat(ops): registry-driven Linux connection helpers with TDD | agent:claude | 0.90 | yes | execution-ready, priority-labeled, strong-claude-language-match, provider-high-priority |
| #3816 feat(repo): generate authoritative work-surface inventory and adapter coverage report | agent:claude | 0.90 | yes | execution-ready, priority-labeled, strong-claude-language-match, provider-high-priority |
| #3524 [WRK] bug(workstations): RDP microphone input not negotiated from ace-win-2 to ace-win-1 | agent:claude | 0.90 | yes | execution-ready, priority-labeled, strong-claude-language-match, provider-high-priority |
| #3525 [WRK] Investigate safe remote Claude job dispatch to ace-win-2 | agent:claude | 0.90 | yes | execution-ready, priority-labeled, strong-claude-language-match, provider-high-priority |
| #3566 fix(agent-ux): make keyboard and context-menu text paste equivalent in Codex CLI | agent:claude | 0.90 | yes | execution-ready, priority-labeled, strong-claude-language-match, provider-high-priority |
| #3568 epic(agent-ux): cross-machine input interaction parity | agent:claude | 0.90 | yes | execution-ready, priority-labeled, strong-claude-language-match, provider-high-priority |
| #3532 fix(memory): reserve cross-provider runtime budget for operational feedback | agent:codex | 0.80 | no | execution-ready, strong-codex-language-match, provider-highest-priority |
| #3554 bug(equality): Windows publish-equality misclassifies missing flock as contention and reports success | agent:codex | 0.80 | no | execution-ready, strong-codex-language-match, provider-highest-priority |
| #3571 equality/reconcile tooling gaps on ace-win-1: junction-following restore wiped canonical skills; Windows host-identity + flock gaps | agent:codex | 0.80 | no | execution-ready, strong-codex-language-match, provider-highest-priority |
| #3787 pytest pays a large fixed startup tax before any test runs — 38s git call, 59MB DB query on collect-only, 487 hidden test files | agent:codex | 0.80 | no | execution-ready, strong-codex-language-match, provider-highest-priority |
| #3511 bug(equivalence): Windows sentinel emits empty unknown fingerprint and corrupts mktree filenames | agent:claude | 0.75 | no | execution-ready, strong-claude-language-match, provider-high-priority |
| #3788 bug(dispatch): reconcile.py reads an open-only label snapshot, so every CLOSED issue reports false LABEL-MISSING | agent:codex | 0.60 | no | priority-labeled, strong-codex-language-match, provider-highest-priority |
| #3821 bug(equality): restore collector idempotency and macOS atomic-publish test portability | agent:codex | 0.60 | no | priority-labeled, strong-codex-language-match, provider-highest-priority |
| #3819 feat(harness): unified ecosystem doctor with stable probe schema | agent:agy | 0.60 | no | priority-labeled, strong-agy-language-match, provider-highest-priority |
| #3717 Context budget: harness config is 3.6% of the window — the cost is tool output (17%), not CLAUDE.md | agent:agy | 0.45 | no | strong-agy-language-match, provider-highest-priority |
