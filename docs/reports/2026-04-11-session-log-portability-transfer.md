# Session-Log Portability Transfer — 2026-04-11

Transfer of durable session-log learnings from ace-linux-1 into the repo ecosystem.

## Scope and Sources Reviewed

| Source | Type | Status |
|--------|------|--------|
| `analysis/provider-session-ecosystem-audit.json` | Structured audit (2026-04-11) | Read — 4 providers, 112 sessions, 172K records |
| `docs/reports/provider-session-ecosystem-audit.md` | Narrative audit report | Read — migration debt, tool mix, remediation hints |
| `logs/orchestrator/README.md` | Operator documentation | Read — structure, write methods, export commands |
| `docs/ops/legacy-claude-reference-map.md` | Legacy redirect guide | Read — 6 legacy path clusters with canonical targets |
| `.claude/memory/agents.md` | Agent workflow facts | Read — bridge-synced Hermes + Claude memory |
| `.claude/memory/KNOWLEDGE.md` | Institutional knowledge | Read — 96 lines, no session-log section |
| `.claude/memory/topics/` | 19 topic files | Scanned — `feedback_cross_machine_execution.md` most relevant |
| `scripts/memory/bridge-hermes-claude.sh` | Memory bridge script | Read — Hermes→repo sync model |
| `logs/orchestrator/claude/` | 319 raw files | Confirmed — session_YYYYMMDD.jsonl + WRK-NNN cross-review logs |
| `logs/orchestrator/codex/` | 452 raw files | Confirmed — exported session_*.jsonl + WRK-NNN cross-review logs |
| `logs/orchestrator/hermes/` | 12 raw files | Confirmed — session_*.jsonl + corrections/ + skill-patches.jsonl |
| `logs/orchestrator/gemini/` | 255 raw files | Confirmed — exported session_*.jsonl + WRK-NNN cross-review logs |

Native provider stores (`~/.codex/sessions/`, `~/.gemini/tmp/`, `~/.hermes/`) exist on ace-linux-1 but are outside the sandbox for this session. Their structure is documented in the orchestrator README and audit report.

## Durable Learnings Selected for Promotion

### L1 — Session log locality principle

**Observation:** Raw session logs (`logs/orchestrator/<provider>/session_*.jsonl`) are machine-local and gitignored. Only derived artifacts (audit JSON/Markdown, memory surfaces, session-signals) cross machines via git.

**Why durable:** This is a design invariant, not an accident. Raw logs contain machine-specific paths, tool call payloads, and ephemeral state. Promoting raw logs to git would bloat the repo and leak local context. The audit script and export scripts exist precisely to extract portable signal from local noise.

**Promoted to:** KNOWLEDGE.md (concise rule), topic file (full context).

### L2 — Migration debt signals mean "redirect, don't recreate"

**Observation:** The audit surfaces "missing repo reads" — files that sessions tried to read but no longer exist. Claude has 7,559 missing reads, heavily concentrated in 4 legacy clusters (work-queue transitions, HTML review, lifecycle scripts, old skills). The `legacy-claude-reference-map.md` provides redirect targets for each cluster.

**Why durable:** Every workflow migration creates this pattern. Agents that encounter stale-path signals in audit output must interpret them as migration artifacts, not as proof that deleted features should be restored. This is a recurring anti-pattern across all providers.

**Promoted to:** KNOWLEDGE.md (behavioral rule), topic file (detailed cluster breakdown).

### L3 — Provider export chain: native → orchestrator → audit

**Observation:** Each provider has a three-stage pipeline:
1. **Native store** (machine-local, provider-managed): `~/.codex/sessions/`, `~/.gemini/tmp/`, `~/.hermes/`
2. **Exported JSONL** (machine-local, repo-gitignored): `logs/orchestrator/<provider>/session_*.jsonl`
3. **Audit artifacts** (repo-tracked, portable): `analysis/provider-session-ecosystem-audit.json` + `docs/reports/provider-session-ecosystem-audit.md`

Export scripts bridge stage 1→2; the audit script bridges stage 2→3. Skipping stage 2 (exports) means the audit runs on stale data.

**Why durable:** This pipeline is infrastructure, not ephemeral. Any new machine or provider must fit this model.

**Promoted to:** Topic file (full pipeline map with script paths and state files).

### L4 — Hermes produces unique correction and skill-patch artifacts

**Observation:** Hermes logs include `corrections/` (10 correction sessions mirroring standard sessions) and `skill-patches.jsonl` (11 entries). No other provider produces these artifact types. The audit counts correction sessions separately.

**Why durable:** These artifacts represent Hermes's self-correction capability and are relevant to any machine running Hermes. Understanding their existence prevents confusion when comparing provider log directories.

**Promoted to:** Topic file (artifact description), orchestrator README update.

### L5 — Claude raw logs lack session_id

**Observation:** The audit reports 0 unique runtime sessions for Claude because "Claude raw orchestrator logs do not persist session_id." Other providers (Codex: 402, Hermes: 941, Gemini: 282) do track this.

**Why durable:** This is a structural limitation that affects any deduplication or per-session analysis of Claude data. Workaround is to use date-based files as session proxies.

**Promoted to:** Topic file (limitation note with workaround).

## Portability Gaps Found

1. **Orchestrator README lacked export ordering guidance.** The README listed export commands and audit commands but didn't explain the dependency: exports must run before audits to produce fresh data. Fixed in this transfer.

2. **No mention of Hermes-specific artifacts in README.** The `corrections/` directory and `skill-patches.jsonl` were undocumented. Fixed in this transfer.

3. **KNOWLEDGE.md had no session-log section.** 96 lines with zero coverage of the session log ecosystem — a gap for any agent needing to understand observability. Fixed in this transfer.

4. **No topic file for session-log portability.** Detailed operational guidance had no home. Created in this transfer.

## Exact Files Changed

| File | Action | What changed |
|------|--------|-------------|
| `docs/reports/2026-04-11-session-log-portability-transfer.md` | Created | This report |
| `logs/orchestrator/README.md` | Updated | Added export ordering note, Hermes artifact types, freshness guidance |
| `.claude/memory/KNOWLEDGE.md` | Updated | Added "Session Log Ecosystem" section (L1 + L2) |
| `.claude/memory/topics/session-log-portability.md` | Created | Detailed operational guidance (L1–L5) |

## Residual Local-Only Observations (Not Promoted)

These observations are grounded but intentionally not promoted because they are ephemeral, machine-specific, or already captured elsewhere:

- **Exact file counts** (319/452/12/255) — change daily with new sessions
- **Tool usage statistics** (40K Bash, 13K Read for Claude) — interesting but volatile; already in the audit report
- **Specific WRK-NNN log filenames** — task-specific, not reusable
- **Bare python3 vs uv run ratios** — already tracked in audit; the `uv run` migration rule is in KNOWLEDGE.md
- **Top Bash command families per provider** — audit artifact, not institutional knowledge
- **Native session store paths** — already documented in orchestrator README
- **Current dirty/untracked files in worktree** — ephemeral session state
