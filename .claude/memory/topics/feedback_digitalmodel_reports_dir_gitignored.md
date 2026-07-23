> Git-tracked snapshot from Claude auto-memory. Captured: 2026-07-23
> Source: /home/vamsee/.claude/projects/-mnt-local-analysis-workspace-hub/memory/feedback_digitalmodel_reports_dir_gitignored.md

---
name: feedback_digitalmodel_reports_dir_gitignored
description: "digitalmodel .gitignore ignores any reports/ dir — completeness HTML must go to a tracked path, not docs/reports/"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 57ba7232-71af-4ee6-92f1-0f808c39212f
---

In `digitalmodel`, `.gitignore:228` is the bare pattern `reports/`, which ignores **any** directory named `reports/` at any depth (`docs/reports/`, `docs/domains/orcawave/reports/`, etc.). So the [[feedback_completeness_score_before_closure]] convention ("document HTML under docs/reports/") produces a LOCAL-ONLY file in digitalmodel — it will never be version-controlled.

**Why:** the scorecard convention was written for workspace-hub; digitalmodel ignores `reports/` globally.

**How to apply:** in digitalmodel, write tracked completeness/assessment HTML directly into the relevant domain dir (e.g. `docs/domains/orcawave/2026-05-27-issue-completeness-scorecard.html`) — NOT a `reports/` subdir. Verify with `git check-ignore -v <path>` before writing, and confirm `git status --short` shows it as `??` (untracked) rather than nothing. Same class as [[feedback_superpowers_specs_gitignored]] (gitignored output dir → relocate to tracked path).
