---
name: feedback_codex_bootstrap_untracked_sed_origin
description: "~/.codex/AGENTS.md broken-path bug originated from an UNTRACKED sed-derivative of ~/.claude/CLAUDE.md, not from any committed script; symlink-to-runtime-artifact is the durable fix."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 214b6592-b65b-480f-accf-16e6a9761175
---

When a provider bootstrap file (e.g. `~/.codex/AGENTS.md`, `~/.hermes/SOUL.md`) is found to contain a wrong literal path or stale content, do NOT assume a tracked script regenerated it. Trace forensically:

1. **Diff against the sibling provider's bootstrap.** If `~/.codex/AGENTS.md` looks like `~/.claude/CLAUDE.md` with case-aware substitutions, you're looking at a one-off sed pipeline, not a script output.
2. **`git log --all -S "<broken-literal>"`** on committed scripts. Zero matches = no tracked generator.
3. **`grep -nE "<broken-literal>" scripts/**` — confirms no committed script writes the string.
4. **File mtime vs embedded "generated on" date.** Mismatch (e.g. mtime 2026-05-04, content header "2026-04-05") strongly suggests manual re-derivation.

**Why:** workspace-hub#2719 Phase 1 Discovery (2026-05-15/16) traced the broken `~/.codex/AGENTS.md` containing `Read \`.Codex/memory/\`` (capital C, non-existent path) to a manual sed pipeline that applied `s/Claude/Codex/g` + `s/claude/Codex/g` to `~/.claude/CLAUDE.md`. The second substitution capitalized the path component wrong (should have been `s/claude/codex/g`). The original r1+r2 plan proposed "fix `scripts/memory/bootstrap-machine.sh`" as the remediation. Both reviewers caught that bootstrap-machine.sh has zero matches for `.Codex` or `.codex` in its prose — the broken file came from an untracked source. Targeting the wrong generator would have left the actual bug source unfixed.

**How to apply:** When investigating a broken provider bootstrap or config file:
- Verify the alleged generator BEFORE writing a fix for it (per [`feedback_r1_review_trust_hazard`](feedback_r1_review_trust_hazard.md))
- If no tracked generator exists, the durable fix is NOT "fix the missing generator" — it's "replace the static file with a symlink to a committed canonical artifact" (workspace-hub#2719 Phase 4 pattern: `scripts/agents/install-soul-runtime.sh` retargets `~/.codex/AGENTS.md → config/agents/codex/AGENTS.runtime.md`).
- Back up the broken file before retargeting (preserve forensic evidence): `mv ~/.codex/AGENTS.md{,.pre-install-backup.$(date +%Y%m%dT%H%M%SZ)}` before `ln -s`.
- Integrate the install step into `scripts/memory/bootstrap-machine.sh` so cross-machine bootstrap parity is preserved.

**Related:**
- [[feedback_r1_review_trust_hazard]] — independently verify reviewer-asserted gaps before applying fixes
- [[feedback_cross_provider_review_payoff]] — Codex GH-connector evidence must be locally verified
- [[feedback_codex_sandbox_no_execution]] — Codex sandbox can prevent local verification; main session must verify
- [[reference_codex_desktop_linux_ilysenko]] — Codex CLI install path for runtime inspection

**Verification commands (run on ace-linux-1 post-fix, 2026-05-16):**
```
$ readlink ~/.codex/AGENTS.md
/mnt/local-analysis/workspace-hub/config/agents/codex/AGENTS.runtime.md

$ grep -F "Read \`.Codex/memory/\`" ~/.codex/AGENTS.md
(no match — original bug pattern gone)

$ ls ~/.codex/AGENTS.md.pre-install-backup.20260516T042128Z
-rw-rw-r-- 989 bytes  (broken file preserved for forensics)
```
