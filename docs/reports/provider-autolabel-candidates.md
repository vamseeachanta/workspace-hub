# Provider autolabel candidates

Generated: 2026-10-09T13:21:20.890414Z
Apply mode: False
Threshold: 0.9

| Issue | Target label | Confidence | Eligible | Reasons |
|---|---|---:|---|---|
| #3740 867 issues cannot leave dispatch:ready — nothing advances dispatch state | agent:codex | 0.95 | yes | execution-ready, priority-labeled, strong-codex-language-match, provider-highest-priority |
| #3839 fix(digitalmodel/fatigue): two of four rainflow paths understate stress range, understating damage | agent:codex | 0.95 | yes | execution-ready, priority-labeled, strong-codex-language-match, provider-highest-priority |
| #3816 feat(repo): generate authoritative work-surface inventory and adapter coverage report | agent:claude | 0.90 | yes | execution-ready, priority-labeled, strong-claude-language-match, provider-high-priority |
| #3838 fix(digitalmodel/orcaflex): three verified model-building integrity defects with silent failure modes | agent:claude | 0.90 | yes | execution-ready, priority-labeled, strong-claude-language-match, provider-high-priority |
| #3843 refactor(orcaflex): consolidate four model generators onto modular_generator | agent:claude | 0.90 | yes | execution-ready, priority-labeled, strong-claude-language-match, provider-high-priority |
| #3787 pytest pays a large fixed startup tax before any test runs — 38s git call, 59MB DB query on collect-only, 487 hidden test files | agent:codex | 0.80 | no | execution-ready, strong-codex-language-match, provider-highest-priority |
| #3592 equality matrix: reclassify harness/scheduler/memory rows — uniform vote mis-grades per-role differences + Windows placeholder data poisons majority | agent:claude | 0.75 | no | execution-ready, strong-claude-language-match, provider-high-priority |
| #3702 bug(equality): equality-matrix-cron writes generated artifacts into the tracked tree, creating a self-sustaining STALE-CHECKOUT deadlock | agent:claude | 0.75 | no | execution-ready, strong-claude-language-match, provider-high-priority |
| #3788 bug(dispatch): reconcile.py reads an open-only label snapshot, so every CLOSED issue reports false LABEL-MISSING | agent:codex | 0.60 | no | priority-labeled, strong-codex-language-match, provider-highest-priority |
| #3821 bug(equality): restore collector idempotency and macOS atomic-publish test portability | agent:codex | 0.60 | no | priority-labeled, strong-codex-language-match, provider-highest-priority |
| #3696 chore(machines): 6 unpushed commits stranded in secondary working copies on ace-linux-2 (incl. one clone with no remote) | agent:codex | 0.60 | no | priority-labeled, strong-codex-language-match, provider-highest-priority |
| #3792 feat(scheduler): no transaction attestation exists for systemd-user surfaces, so they can only ever declare missing_transaction | agent:codex | 0.60 | no | priority-labeled, strong-codex-language-match, provider-highest-priority |
| #3819 feat(harness): unified ecosystem doctor with stable probe schema | agent:agy | 0.60 | no | priority-labeled, strong-agy-language-match, provider-highest-priority |
| #3842 refactor(fatigue): consolidate seven rainflow counting paths onto one | agent:codex | 0.60 | no | priority-labeled, strong-codex-language-match, provider-highest-priority |
| #3596 Compliance alert: W30 — 18% (critical) | agent:claude | 0.55 | no | priority-labeled, strong-claude-language-match, provider-high-priority |
| #3693 Compliance alert: W31 — 0% (critical) | agent:claude | 0.55 | no | priority-labeled, strong-claude-language-match, provider-high-priority |
| #3794 Compliance alert: W32 — 66% (medium) | agent:claude | 0.55 | no | priority-labeled, strong-claude-language-match, provider-high-priority |
| #3717 Context budget: harness config is 3.6% of the window — the cost is tool output (17%), not CLAUDE.md | agent:agy | 0.45 | no | strong-agy-language-match, provider-highest-priority |
