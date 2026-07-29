# Claude Code Auto-Memory Snapshot

> Git-tracked snapshot of Claude Code's auto-generated MEMORY.md index.
> Last captured: 2026-07-29
> Source: /home/vamsee/.claude/projects/-mnt-local-analysis-workspace-hub/memory/MEMORY.md

# Memory Index

## User
- [user_workstation_topology.md](user_workstation_topology.md) — 3-machine setup: ace-linux-1=dev-primary, ace-linux-2=dev-secondary, dispatch pattern
- [user_privacy_conscious.md](user_privacy_conscious.md) — Private repo data stays private in cross-repo tooling

## Feedback
- [feedback_no_fluff.md](feedback_no_fluff.md) — Direct execution, not excessive process overhead
- [feedback_cross_review_valuable.md](feedback_cross_review_valuable.md) — Cross-review valuable for platform limitation discovery
- [feedback_gh_always_refresh.md](feedback_gh_always_refresh.md) — Always fetch fresh from GH, never use cached issue data
- [feedback_research_before_stories.md](feedback_research_before_stories.md) — Every story/phase must include online research task before implementation
- [feedback_agent_prompts_with_stories.md](feedback_agent_prompts_with_stories.md) — GH stories should include ready-to-dispatch agent prompts
- [feedback_prefer_inprocess_agents.md](feedback_prefer_inprocess_agents.md) — Run background agents directly, don't just show prompts; prefer zero-token-cost hooks

## Project
- [project_data_placement_1540.md](project_data_placement_1540.md) — Generated data → ace drive, not git; #1540 closed, #1541-1543 follow-ups open
- [project_gsd_v1_1_milestone.md](project_gsd_v1_1_milestone.md) — v1.1 milestone: phase 7 (solver verification) + phase 1000 (cross-AI planning)
- [project_oss_triage_2026_03.md](project_oss_triage_2026_03.md) — 10 libs evaluated: Capytaine+fluids adopt, Playwright shipped, marker/docling evaluated, others deferred
- [project_wrk6670_gh_migration.md](project_wrk6670_gh_migration.md) — GH-first work queue migration, multi-repo Option 2, Stage 9 done 2026-03-24
- [project_digitalmodel_hydro_pipeline.md](project_digitalmodel_hydro_pipeline.md) — GH #464-467 dependency chain: all 4 issues COMPLETE
- [project_llm_wiki_orcina.md](project_llm_wiki_orcina.md) — 741 files, 667K words on ace drive; search-wiki.py; 5 follow-up issues open
- [project_gtm_demos_complete.md](project_gtm_demos_complete.md) — 5/5 GTM demos built (1292 cases), outreach docs ready, next: validate + GIFs + execute
- [project_orcaflex_spec_overhaul.md](project_orcaflex_spec_overhaul.md) — 100% spec audit, 189 tests, yaml_validator + post_validator + spec_upgrader; #495-#511

## Reference
- [reference_resource_intelligence_locations.md](reference_resource_intelligence_locations.md) — NFS mount paths, doc-index scripts, summaries on ace drive, path resolution convention
- [reference_codex_plugin.md](reference_codex_plugin.md) — Codex CLI v0.116.0 plugin, authenticated, direct runtime
- [reference_capytaine_env.md](reference_capytaine_env.md) — Capytaine 2.3.1 at /mnt/local-analysis/capytaine-env, Python 3.12
- [reference_marker_env.md](reference_marker_env.md) — marker 1.10.2 at /mnt/local-analysis/marker-env, needs >=8GB VRAM for GPU mode
- [reference_precommit_hooks.md](reference_precommit_hooks.md) — Pre-commit hook runs 3 check scripts (skill security, encoding, CLAUDE.md limits)
