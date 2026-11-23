# WRK-1119 Plan: Defined Permission Model

## Context

Claude Code sessions run with `skipDangerousModePermissionPrompt: true` in `~/.claude/settings.json`,
which silently bypasses all tool-call permission checks. The project-level `.claude/settings.json`
already has `permissions.allow` (40 entries) and `permissions.deny` (6 entries), but the allow list
is incomplete — it misses many commands used in practice (e.g., `uv`, `bash`, `cat`, `ssh`, `mkdir`).
The goal is to make the allow list comprehensive enough that the bypass flag can be removed, giving
least-privilege security that travels with the repo to every workstation.

**Data available:** 2,231 session JSONL files (2.2 GB) at `~/.claude/projects/` on dev-primary,
each recording every Bash tool call in `message.content[].input.command`.

---

## Approach

### Phase 1 — TDD: Audit Script

Write `tests/permissions/test_audit_bash_commands.py` first (≥3 tests), then implement
`scripts/permissions/audit-bash-commands.py`.

**Script behavior:**
- Accepts `--sessions-dir PATH` (default: `~/.claude/projects/`) and `--output PATH`
- Parses all `*.jsonl` files: extracts `message.content[]` entries where `type=tool_use`, `name=Bash`, reads `input.command`
- Normalises each command to a "prefix token" (first word, or first two words for `git <subcommand>`, `uv run`, etc.)
- Counts frequency per prefix
- Outputs ranked YAML: `prefix`, `count`, `example_command`, `suggested_allow_pattern`

**Tests to write (TDD order):**
1. `test_extract_bash_commands_from_session` — given a synthetic JSONL with 2 Bash tool-uses and 1 non-Bash, returns 2 commands
2. `test_normalize_command_to_prefix` — `git diff HEAD~1` → `git diff`, `uv run --no-project python foo.py` → `uv run`, `ls -la /tmp` → `ls`
3. `test_suggest_allow_pattern` — `git diff` → `Bash(git diff:*)`, `ls` → `Bash(ls:*)`, `pwd` → `Bash(pwd)`
4. `test_end_to_end_audit` — run on a temp dir with two synthetic sessions, assert output YAML has correct top entries

### Phase 2 — Run Audit on dev-primary

```bash
uv run --no-project python scripts/permissions/audit-bash-commands.py \
  --sessions-dir ~/.claude/projects/-mnt-local-analysis-workspace-hub \
  --output .claude/work-queue/assets/WRK-1119/audit-dev-primary.yaml
```

### Phase 3 — SSH Audit on dev-secondary

```bash
ssh dev-secondary "uv run --no-project python /mnt/local-analysis/workspace-hub/scripts/permissions/audit-bash-commands.py \
  --sessions-dir ~/.claude/projects/ \
  --output /tmp/audit-dev-secondary.yaml"
scp dev-secondary:/tmp/audit-dev-secondary.yaml .claude/work-queue/assets/WRK-1119/
```

### Phase 4 — Merge + Derive Final Allow List

Script `scripts/permissions/merge-audit-results.py`:
- Merges two audit YAMLs by summing counts
- Applies threshold: include prefix if count ≥ 5 across combined sessions
- Excludes patterns already denied (curl, wget, eval, sudo, chmod 777, rm -rf /)
- Outputs merged ranked list + suggested additions to `.claude/settings.json`

### Phase 5 — Update `.claude/settings.json`

Add missing allow patterns derived from audit to the `permissions.allow` array.
Keep existing deny list intact; review against `security.md` to add any missing deny patterns.

**Key expected additions** (confirmed from spot-check of session files):
- `Bash(uv:*)` — uv package manager (heavily used)
- `Bash(bash:*)` — bash script invocation
- `Bash(cat:*)` — file inspection
- `Bash(head:*)`, `Bash(tail:*)` — file inspection
- `Bash(mkdir:*)` — directory creation
- `Bash(cp:*)`, `Bash(mv:*)` — file operations
- `Bash(ssh:*)` — remote machine access
- `Bash(scp:*)` — file transfer
- `Bash(find:*)` — file search
- `Bash(sort:*)`, `Bash(uniq:*)`, `Bash(grep:*)` — text processing
- `Bash(echo:*)` — shell output
- `Bash(export:*)` — env vars
- `Bash(rm:*)` — file removal (scoped; rm -rf / already denied)
- `Bash(chmod:*)` — file permissions (chmod 777 already denied)
- `Bash(scripts/*:*)` — all project scripts (extend beyond `./scripts/*`)

### Phase 6 — Validate on dev-primary

1. Remove `skipDangerousModePermissionPrompt` from `~/.claude/settings.json`
2. Start a new Claude Code session and run representative commands
3. Confirm no unexpected permission prompts for normal workflow commands

### Phase 7 — Documentation

Create `.claude/docs/permission-model.md`:
- How the allow/deny model works in Claude Code
- Where to find the allow list (`.claude/settings.json`)
- How to add a new allowed command
- How to add a new deny pattern
- Cross-machine propagation (repo-committed settings.json)
- licensed-win-1 Windows path for user settings

### Phase 8 — licensed-win-1 (deferred, keeps WRK open)

Run audit script on Windows, validate session works without bypass flag.
WRK closes only after this step.

---

## Files to Create / Modify

| Action | Path |
|--------|------|
| **Create** | `scripts/permissions/audit-bash-commands.py` |
| **Create** | `scripts/permissions/merge-audit-results.py` |
| **Create** | `tests/permissions/test_audit_bash_commands.py` |
| **Modify** | `.claude/settings.json` — extend `permissions.allow` |
| **Create** | `.claude/docs/permission-model.md` |
| **Modify** (later) | `~/.claude/settings.json` — remove `skipDangerousModePermissionPrompt` |

---

## Verification

```bash
# Run TDD tests
uv run --no-project python -m pytest tests/permissions/ -v

# Run audit on dev-primary
uv run --no-project python scripts/permissions/audit-bash-commands.py \
  --sessions-dir ~/.claude/projects/-mnt-local-analysis-workspace-hub \
  --output /tmp/audit-result.yaml

# Verify gate evidence
uv run --no-project python scripts/work-queue/verify-gate-evidence.py WRK-1119
```

---

## AC Mapping

| AC | Covered by |
|----|-----------|
| 1. Audit script + candidate allow list | Phase 1+2 |
| 2. `.claude/settings.json` with allow/deny committed | Phase 5 |
| 3. `--dangerously-skip-permissions` / bypass flag removed on dev-primary | Phase 6 |
| 4. Deny list covers rm -rf /, chmod 777, git push --force, security.md patterns | Phase 5 review |
| 5. Docs in `.claude/docs/` | Phase 7 |
| 6. Fresh session works on dev-primary AND licensed-win-1 | Phase 6 + 8 |
| 7. TDD ≥3 tests | Phase 1 |
