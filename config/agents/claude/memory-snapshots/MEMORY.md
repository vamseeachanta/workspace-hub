# Workspace Hub Memory

## Feedback
> working-style.md, shell-git-patterns.md, engineering-modules.md
> feedback_*: html_refresh, skill_before_code, no_shortcuts_knowledge, dark_intelligence_excel
> repo_scope, research_skill_sources, specs_plans_location, uv_run_isolation, no_jargon
- [No local task IDs](feedback_no_reserved_wrk_ids.md) — GitHub issues only
- [Check parallel work](feedback_check_parallel_work.md) — scan in-flight sessions first
- [Comment on issues](feedback_gh_issue_comment.md) — post summary on every issue
- [Queue git-tracked](feedback_queue_git_tracked.md) — verify files in git before queue
- [Worktree gitlink pollution](feedback_worktree_gitlink_pollution.md) — add .claude/worktrees/ to .gitignore before parallel-agent runs
- [Adversarial review stance](feedback_adversarial_review_stance.md) — every review prompt must force defect-hunting, not charitable reading
- [Cross-provider review payoff](feedback_cross_provider_review_payoff.md) — Codex finds non-overlapping defects vs. Claude; verify Codex's GitHub-connector evidence locally
- [gh issue close drops comments](feedback_gh_issue_close_silent_comment_drop.md) — if issue already CLOSED, --comment is silently lost; reopen-comment-close to recover
- [Codex needs pushed artifact](feedback_codex_needs_pushed_artifact.md) — push plan to GitHub BEFORE dispatching `codex exec` review; sandbox can't read local files
- [Codex sandbox write blocked](feedback_codex_sandbox_write_blocked.md) — Codex sandbox blocks filesystem writes even for pushed artifacts; capture findings inline and write the review file yourself
- [Merge-race silent revert](feedback_merge_race_silent_revert.md) — auto-sync race during `git merge --no-ff` + `git commit --no-edit` can drop second-parent tree; always verify merged content matches branch tip
- [Data-format guidelines](data_format_guidelines.md) — default YAML for agent-facing structured data; JSON only when tool output is machine-consumed
- [Cross-machine execution](feedback_cross_machine_execution.md) — per-machine tasks via shared git repo, not SSH/rsync
- [Plugin cache ≠ repo tree](feedback_plugin_cache_not_repo_tracked.md) — `gsd:`/`sparc:`/`workflows:` skills live under `~/.claude/plugins/cache/`; `git mv` cannot operate on them
- [Retry-loop reset hazard](feedback_retry_loop_reset_hazard.md) — `git reset HEAD -- .` in a retry loop under auto-sync contention can strip staged edits and land mislabeled commits

## Project
> project_ecosystem_theme.md, project_github_workflow.md, project_2025_taxes.md
> project_cfd_openfoam_storage.md
- [Doc-intel operating model](project_doc_intel_operating_model.md) — #2205 parent + #2206/#2207/#2209 children; 2026-04-19 amendments landed; follow-ons #2360/#2361/#2362
- [GSD](project_gsd_migration.md) — sole workflow, v1.38.1, Node 24+
- [Cross-review](project_cross_review_policy.md) — gate scripts + pre-push hook + audit cron
- [Mooring knowledge](project_mooring_failures_knowledge.md) — 40 entries at knowledge/seeds/
- [Nightly researchers](project_nightly_researchers.md) — LIVE, rotating Mon-Fri
- [Harness evals](project_ai_harness_evaluations.md) — #1466-1470
- [Hermes](project_hermes_installation.md) — v0.4.0, shebang reverts (3x)
- [Hermes Codex quota](project_hermes_codex_quota.md) — #6551, follow-ups #6564-6567
- [/today tips](project_workflow_tips_today.md) — tip-of-the-day, YAML catalog
- [Solver queue](project_solver_queue_architecture.md) — PRODUCTION, batch+retry+dashboard
- [Overnight batch](project_overnight_batch_runs.md) — 5 parallel terminals nightly
- [Tier-1 refactor](project_tier1_refactor.md) — Ph1 DONE; Ph2A/2B ready
- [Field-dev econ](project_field_dev_economics.md) — DONE; follow-ups #2076,#2079,#2081
- [Field-dev arch](project_field_dev_arch_patterns.md) — DONE; follow-ups #2082,#2084,#2086
- [assethold specs](project_assethold_spec_location.md) — design docs go in docs/reports/ (specs/ gitignored)
- [assethold ownership](project_assethold_ownership_transfer.md) — transferred samdansk2 → vamseeachanta; local origin may be stale
- [TX Franchise 2026](project_tx_franchise_2026.md) — DONE; both C-Corps filed, C-Corps ineligible for passive entity
- [Daily readiness cron](project_daily_readiness_cron.md) — trig_019GWtRosbZ9rw1HxrGpsvy9, 6am CT daily, posts to repo-readiness issue
- [CAD tooling review](project_cad_tooling_review.md) — PAUSED; #2327/#2328/#2329 await doc/resource intel (#2205) review

## Tips
- [Voice prompts](user_voice_prompt_tips.md) — Linux shortcuts for voice-dictated editing

## References
> ai-orchestration.md, network_machines.md
- [achantas-data](reference_achantas_data.md) — personal data + travel as GitHub issues
- [Google CLI](reference_google_cli_paid.md) — paid GWS API access
