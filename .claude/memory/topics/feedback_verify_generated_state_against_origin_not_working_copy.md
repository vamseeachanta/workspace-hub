> Git-tracked snapshot from Claude auto-memory. Captured: 2026-07-30
> Source: /home/vamsee/.claude/projects/-mnt-local-analysis-workspace-hub/memory/feedback_verify_generated_state_against_origin_not_working_copy.md

---
name: feedback_verify_generated_state_against_origin_not_working_copy
description: "Generated/state files (skill-scores.yaml, telemetry, caches) must be judged against origin/main, not the current working copy — a feature-branch checkout misleads"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 165a53db-8632-41e6-a2c3-11074ec7d107
---

When assessing the freshness/correctness of a **generated or state file** (e.g. `.claude/state/skill-scores.yaml`, telemetry, caches, baselines), read it from **`origin/main`** (`git show origin/main:<path>`), not the working copy — and check what branch the checkout is on first (`git rev-parse --abbrev-ref HEAD`).

**Why:** 2026-06-15, strengthening the repo ecosystem, I read `skill-scores.yaml` = 402 skills / generated 2026-04-03 and concluded the eval cadence had lapsed ("2 months stale"). An adversarial-review subagent read the same file and agreed. Both wrong: the primary clone was parked on an unrelated feature branch (`fix/cron-render…`) branched from an old base. **`origin/main` was current: 830 skills, generated 2026-06-14** — cadence healthy. My "telemetry refresh" was a no-op. I'd already posted a wrong "stale/cadence root-cause" claim on the issue + a committed report and had to correct both.

**How to apply:** before claiming any generated artifact is stale/broken, (1) `git rev-parse --abbrev-ref HEAD` — am I on main or a foreign branch?; (2) `git show origin/main:<path>` for the canonical version; (3) only then judge. This session also caught a separate over-trusted-grep error (de-prescription "110 over-prescriptive skills" was ~98% legitimate ordered procedures + sub-skill TOC links; keystone marker `show your reasoning` had 0 hits) — same root discipline: validate a metric's hits/canonical source before acting. Pairs with [[feedback_subagent_acceptance_metric_drives_signal_deletion]] and [[feedback_reflog_as_ground_truth]].
