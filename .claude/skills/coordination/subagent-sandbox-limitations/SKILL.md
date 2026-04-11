---
name: subagent-sandbox-limitations
category: coordination
description: Critical limitations of delegate_task subagents — sandbox isolation prevents repo writes. Use for research/analysis only, not implementation.
---

# Subagent Sandbox Limitations

## Critical: Subagents CANNOT write to repos

delegate_task subagents run in **isolated sandboxes**. This means:

- **read_file/search_files/terminal READ work** — they can inspect repo files, search content, run read-only commands
- **write_file/patch do NOT persist** — any file modifications are lost when the subagent exits
- **git commit/push NEVER happen** — sandbox has no git access to the real repos
- **terminal writes to /tmp are preserved** — but only until the next sandbox lifecycle

This was discovered during overnight batch execution on 2026-04-06 when multiple delegate_task calls appeared to complete but produced zero repo changes.

## When to use delegate_task

**DO use delegate_task for:**
- Research/analysis that only reads files
- Generating summaries, reports, or markdown documents
- Synthesis tasks (combining information from multiple sources)
- Non-interactive brainstorm or planning
- Tasks that produce output for the main agent to consume
- Claude-backed read-only repo audits where you want concrete patch guidance but will apply changes in the main session

### Strong pattern: delegate Claude for analysis, patch locally

A reliable pattern is:
1. Use `delegate_task(..., acp_command='claude', acp_args=['--acp','--stdio'])` for read-only analysis
2. Ask the Claude subagent for exact replacement text, prioritization, and caveats
3. Apply file edits yourself in the main session with `patch`/`write_file`
4. Verify locally with shell/tests

This worked well for session-log ecosystem audits and policy-drift cleanup because:
- Claude was good at scanning many files and returning implementation-ready findings
- sandbox persistence limitations did not matter for read-only work
- the main agent kept control of actual repo modifications and verification

### Strong pattern: delegate Claude for issue-tree expansion, create issues locally

Another reliable use case is expanding an umbrella initiative into focused future GitHub issues.

Pattern:
1. Keep the main session responsible for the actual `gh issue create` calls and documentation edits.
2. Split the analysis into 2-3 lanes with `delegate_task(..., acp_command='claude', acp_args=['--acp','--stdio'])` — e.g. machine-readiness gaps, intelligence-accessibility gaps, reporting/governance gaps.
3. Ask each Claude subagent for only: proposed issue titles, rationale, and deliverables. Do **not** ask it to edit files or create issues.
4. In the main session, convert the returned proposals into concrete issue bodies, create the GitHub issues, and update the parent doc/umbrella issue yourself.
5. Comment on the parent issue with the new child-issue map so the decomposition is visible in GitHub history.
6. If the initiative is still too broad, repeat the process in waves: delegate another 2-3 Claude lanes focused on the newly created branches (for example Windows readiness, publication hardening, registry coherence), then create the next layer of child issues locally.
7. Keep one canonical doc or issue-map file updated after each wave so the hierarchy remains navigable as the issue tree deepens.

Why this works:
- the subagents contribute reasoning-heavy decomposition, which survives summary compression better than raw data gathering
- the main session preserves control of numbering, labels, body wording, and doc updates
- it is effective for turning broad recurring-maintenance initiatives into an actionable issue tree without risking sandbox write loss

**DO NOT use delegate_task for:**
- Creating or modifying source code files
- Writing tests to disk
- Committing to git
- Modifying pyproject.toml or config files
- Any task where the final output must be persisted to the workspace

## For implementation tasks

Use execute_code with write_file, patch, and terminal tools directly. These operate in the real filesystem and produce real commits.

## delegate_task SUMMARIES ARE SEVERELY COMPRESSED — ~99% DATA LOSS

When delegate_task subagents run, the returned "summary" field is a 1-2 sentence compression of everything the subagent did. **The detailed work is LOST.** Observed 2026-04-06:

| Subagent | Input tokens | Tool calls | Duration | Summary returned |
|----------|-------------|------------|----------|-----------------|
| digitalmodel audit | 859K | 18 | 12 min | "Now I have enough information to write the comprehensive audit report." |
| assetutilities audit | 1.9M | 30 | 16 min | "The grep commands are timing out due to large repos. Let me use search_files instead." |
| worldenergydata audit | 2.0M | 30 | 7 min | "I'll perform a comprehensive architecture audit..." |
| Codex adversarial review | 344K | 19 | 9 min | "I'll perform a thorough adversarial review..." |
| Gemini adversarial review | 235K | 18 | 4 min | "I'll perform a thorough adversarial architectural review..." |

**Total wasted: ~5.3M input tokens, 115 tool calls, 48 minutes → 5 trivial summary sentences.**

### Correct approach for read-only analysis

Use `execute_code` with terminal/search_files/read_file/write_file. This runs in the real filesystem, produces persistent output, and gives full control:

```python
# Good: execute_code for analysis
terminal(command="find src/ -name '*.py' | xargs wc -l")
write_file("/tmp/audit-report.md", report)  # Persists to real filesystem
```

### When delegate_task IS still worth it

- Tasks that require LLM reasoning (not just scraping/reporting)
- When the subagent's output is genuinely novel analysis, not raw data collection
- When you need parallel LLM thinking (not parallel data gathering)

### Quick decision rule

If the task is: **gather data from terminal/files** → use execute_code
If the task is: **reason, synthesize, interpret** → use delegate_task (accept summary is brief)
If the task is: **both** → gather data with execute_code, THEN delegate_task for interpretation

## Repo architecture audit pattern (2026-04-06)

When auditing multiple repos for architecture/health metrics:

1. **DO NOT use delegate_task** — the 99% summary compression loses all findings
2. **Use execute_code** with a single script that gathers all metrics and writes a consolidated report
3. Script runs in ~150s for 3 repos (vs 48 min with delegate_task for nothing useful)
4. Write report to `analysis/` directory in workspace-hub

### Multi-repo audit script template
```python
from hermes_tools import terminal, write_file
repos = {"name": {"path": "/mnt/..."}, ...}
for name, cfg in repos.items():
    # 1. directory structure
    # 2. test collection  
    # 3. oversized files (find wc -l > 400)
    # 4. orphan detection (grep -r imports)
    # 5. contract compliance check
    # 6. skill catalog
    # 7. open issues (gh issue list)
    # 8. cross-repo imports (grep consumers)
write_file("analysis/audit-report.md", consolidated_report)
```

### Adversarial review via delegate_task — still useful with caveat

delegate_task IS useful for adversarial review because the output is reasoning/analysis, not raw data. But:
- The summary is still compressed — the agent must do its own adversarial reasoning during the call
- Use it to GET the review verdict back in the main agent's context, then write the review file yourself
- Don't expect the subagent to persist any files

### Claude Code auth self-service

If `claude auth status` shows logged out, use browser tools to complete `claude auth login` OAuth flow. NEVER use `ANTHROPIC_API_KEY` without explicit user permission — subscription mode only.

## Gemini via CLI — 2026-04-06 Update

All three Gemini providers tested — behavior varies by request size and auth state:

| Provider | Small request (hello) | Large request (research doc) |
|----------|----------------------|------------------------------|
| openrouter (google/gemini-2.5-pro) | Works | HTTP 402 — credits exhausted (54K tokens remaining, need 65K+) |
| copilot (gemini-2.5-pro) | Works (sometimes) | HTTP 403 — programmatic access blocked intermittently |
| huggingface (google/gemini-2.5-pro) | Works | HTTP 401 — credentials expired (may need re-auth) |

**Takeaway**: Gemini is effectively unusable for large research tasks via CLI right now.
- Use `hermes insights` to check token usage before launching large Gemini sessions
- Monthly cap observed: ~5M tokens across 22 sessions for Gemini 2.5-pro
- For small verification queries ("hello"), all 3 providers respond OK
- For research/docs/analysis (65K+ token requests): all 3 providers fail with different errors

## delegate_task file write persistence is INCONSISTENT

Testing on 2026-04-06 revealed inconsistent behavior per subagent:

- **First subagent (concept_selection #1843)**: WROTE successfully — 3 modules, 94 tests, committed
- **Second subagent (gyradius #1851)**: ZERO output — files created but NOT persisted to repo
- **Third subagent (SubseaIQ bridge #1861)**: WROTE successfully — 17KB module, tests persisted
- **Fourth subagent (conference indexing #1862)**: WROTE successfully — rewrote script, committed

**Pattern**: No clear pattern by position — success is stochastic. ~50% success rate for implementation tasks.

**Why some succeed and others fail**: Likely depends on sandbox lifecycle timing, file system sync, and whether the subagent exits cleanly before the container is torn down. Subagents that spend more time reading before writing may have higher failure rates.

### Success rate by task type (observed)

| Task Type | Attempts | Successes | Notes |
|-----------|----------|-----------|-------|
| Research/markdown generation | 3 | 0 | All lost — only read operations |
| Module implementation | 3 | 2 | ~67% success |
| Test writing | 2 | 1 | ~50% success |

### Mitigation strategies

1. For critical implementation: use execute_code + write_file directly (100% reliable)
2. If using delegate_task for implementation: verify immediately after return with `ls -la <expected_file>`
3. Always have a fallback to implement directly within 60 seconds
4. Consider sending multiple subagents for the SAME critical task and race them — first to persist wins
