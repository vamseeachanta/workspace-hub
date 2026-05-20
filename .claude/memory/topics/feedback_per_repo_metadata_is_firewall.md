> Git-tracked snapshot from Claude auto-memory. Captured: 2026-05-20
> Source: /home/vamsee/.claude/projects/-mnt-local-analysis-workspace-hub/memory/feedback_per_repo_metadata_is_firewall.md

---
name: Per-repo metadata is the firewall, not directory location
description: When evaluating whether to nest or sibling a repo, the firewall mechanisms that prevent license bleed, ToS violations, and agent-context leakage are per-repo metadata (LICENSE, .gitignore, .claude/, .git), not file-system distance. Don't conflate "different directory" with "different boundary."
type: feedback
originSessionId: eb5d9f9b-67bd-4730-86fd-59b396905f3c
---
When a user proposes nesting a repo with different license/lifecycle/ecosystem boundaries inside workspace-hub, do not reflexively cite "structural costs" as a blocker. Verify which mechanisms actually enforce the boundary before arguing the boundary requires sibling layout.

**Why:** On 2026-05-07 I argued three turns against nesting llm-wiki and kaggle-rogii-2026 into workspace-hub on grounds of license contamination, Kaggle ToS exposure, and CLAUDE.md context leak. The user pushed back each time. On the third pushback I actually verified the repos and discovered each had its own LICENSE file (license travels with the repo, not the directory), gitignored its dataset (data redistribution risk is the gitignore + backup-exclude posture, not the file-system path), and could be given a per-repo `.claude/` directory to scope agent memory away from hub private state. The "structural costs" were conditional on layout assumptions that don't hold once the per-repo metadata mechanisms are in place. The user's "fresh and doesn't hurt" framing was correct; my structural arguments were too strong.

**How to apply:**

1. **Before invoking "structural cost" against a nesting proposal**, enumerate the actual firewall mechanisms and check whether they bind to the repo (metadata) or to the location (file-system). Almost always the former.
   - License: enforced by `LICENSE` file in repo, not directory parent.
   - ToS / data redistribution: enforced by `.gitignore` + backup-exclude rules, not directory parent.
   - Agent-context boundary: enforced by per-repo `.claude/` directory presence (Claude Code keys memory namespace by `.claude/` ancestry), not directory parent.
   - Git history independence: enforced by per-repo `.git`, not directory parent.
2. **When the user repeats a question with new framing 2+ times after technical pushback**, treat that as a strong signal to reconsider rather than escalate. They are usually exposing a hidden assumption in your argument.
3. **Migration cost is a separate axis from structural cost.** A 24-hour-old repo with 8 commits and no external contributors is in a "decisions are still cheap" window where revising costs almost nothing. Locking decisions into permanence inside that window is its own anti-pattern.
4. **Verify before holding the line.** A 30-second `ls`/`grep`/`git log` on the actual repo state would have caught this on turn one. "Sounds structurally risky" without verification is overweighted in my reasoning; cheap verification beats abstract argument.
5. **The portable pattern from this incident:** for any nested public/external repo, the safe firewall is `LICENSE` + `.gitignore` + per-repo `CLAUDE.md` + per-repo `.claude/` (gitignored). Nesting is then safe regardless of license/lifecycle differences, *provided* those four mechanisms are in place.
