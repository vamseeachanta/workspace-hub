# Plan for #3408: Add harness-checkup (/doctor) hygiene dimension to machine-equality matrix

> **Status:** draft
> **Complexity:** T3
> **Date:** 2026-07-09
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/3408
> **Client:** N/A
> **Lane:** lane:claude
> **Review artifacts:** scripts/review/results/2026-07-09-plan-3408-claude.md | ...-codex.md | ...-gemini.md

---

## Resource Intelligence Summary

### Existing repo code
- **Found — collector extension pattern:** `scripts/readiness/collect-equality.sh` §6c/6d/6e (`skill_currency`, `memory_freshness`, `skill_link_health`) each READ a `.claude/state/<name>-<machine>.json` written by a separate audit, fail-closed to null → MISSING-EVIDENCE, keep `audited_at` in the canonical payload to force a rewrite. New dimension mirrors this exactly.
- **Found — matrix grading pattern:** `scripts/readiness/build-equality-matrix.py` — per-dimension `*_verdict(report)` fns (lines ~260–351), dispatch (lines ~459–464), and a ROWS registration (lines ~514–516). New dimension adds `harness_checkup_verdict()` + dispatch + one ROW.
- **Found — version/install ALREADY collected:** `scripts/monitoring/equivalence-fingerprint.sh:40–110` emits `harness_version` (`claude --version`) + `harness_install` (npm-global/native/other) into `.claude/state/equivalence/local-fingerprint.json`. The audit READS these; it does not re-collect. **Avoids duplication.**
- **Found — distinct existing "doctor":** `scripts/maintenance/harness-install-doctor.sh` (#3184) REPAIRS per-provider runtime symlinks (SOUL/AGENTS, codex skills). Different surface (provider runtime, not Claude Code CLI hygiene); emits no state file. No overlap with the six gap facts.
- **Found — audit exemplars:** `scripts/curation/audit_memory_freshness.py`, `audit_skill_currency.py` write `.claude/state/*-<machine>.json`; `.ps1` companions exist for Windows parity (`curate-session-memory.ps1`). New audit + `.ps1` follow suit.
- **Gap:** none of the above computes version-currency-vs-latest, settings parse validity, agent-def health, duplicate/leftover installs, unused skill/plugin counts, or default permission mode as a comparable matrix cell.

### Standards
Not applicable (harness/infrastructure issue).

### LLM Wiki pages consulted
No relevant wiki pages (harness-internal).

### Documents consulted
- Issue #3408 (this issue) — scope + explicit out-of-scope.
- `config/scheduled-tasks/schedule-tasks.yaml` — cadence SSoT: `equality-report` weekly (Mon 04:30), `equality-matrix-refresh` 6-hourly, `equivalence-sentinel` 6-hourly, `session-curation` 6-hourly. New audit adds a **daily** entry (network latest-lookup must not run 6-hourly).
- `.claude/rules/coding-style.md` — no hardcoded abs paths (enforced), harness files ≤20 lines. Applies to any doc/config touched.
- Parent epic #3058 (harden-ecosystem: drift #3059, model-sourcing #3060, parity #3061, skill-sprawl #3062).

### Gaps identified (each is a testable claim)
- No module computes Claude Code version currency vs the published latest.
- No per-machine record of settings-cascade parse validity, agent-def collisions, duplicate installs, unused-extension counts, or default permission mode.
- The equality matrix has no row reflecting Claude Code harness hygiene.

### Evidence (embedded verification)

**Issue statuses** (verified 2026-07-09 via `gh`):
- `#3408` — OPEN — Add harness-checkup (/doctor) hygiene dimension to machine-equality matrix (this issue)
- `#3184` — CLOSED (merged 525a30c32) — install-doctor repair arm
- `#3059` — equivalence-sentinel (fingerprint source)

**File existence** (verified 2026-07-09 on origin/main `371d3114b`):
- EXISTS: scripts/readiness/collect-equality.sh, scripts/readiness/build-equality-matrix.py
- EXISTS: scripts/monitoring/equivalence-fingerprint.sh, scripts/maintenance/harness-install-doctor.sh
- EXISTS: scripts/curation/audit_memory_freshness.py, audit_skill_currency.py
- MISSING (this plan creates): scripts/curation/audit_harness_checkup.py, scripts/curation/audit-harness-checkup.ps1, .claude/state/harness-checkup-<machine>.json

**Line excerpts** (`collect-equality.sh` §6d, the pattern to mirror):
```
200  mf_file="${STATE_DIR}/memory-freshness-${MACHINE}.json"
201  mf_audited="null"; mf_worst="null"; mf_fresh="null"
202  if [[ -f "$mf_file" ]] && have jq; then
203    _mfa=$(jq -r '.audited_at // empty' "$mf_file" 2>/dev/null)
204    [[ -n "$_mfa" ]] && mf_audited="\"$(yesc "$_mfa")\""
```

**Line excerpts** (`equivalence-fingerprint.sh` — version/install already collected):
```
40  # Harness version + install method.
41  hv="$(claude --version 2>/dev/null | awk '{print $1}')"; [ -z "$hv" ] && hv=null
110 "harness_version": s(hv), "harness_install": s(hinstall),
```

**Reproduction proofs:** N/A — feature addition, not an alleged runtime failure. Gap confirmed by `git grep -lniE 'harness_checkup' origin/main -- scripts/ config/` → no matches.

Distinct sources consulted: 7 (issue + 6 files/registries). Minimum 3 met.

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | docs/plans/2026-07-09-issue-3408-harness-checkup-equality-dimension.md |
| Audit (new) | scripts/curation/audit_harness_checkup.py |
| Audit Windows companion (new) | scripts/curation/audit-harness-checkup.ps1 |
| Audit tests (new) | tests/curation/test_audit_harness_checkup.py |
| Collector edit | scripts/readiness/collect-equality.sh (+ collect-equality.ps1 parity) |
| Matrix edit | scripts/readiness/build-equality-matrix.py |
| Matrix verdict tests | tests/readiness/test_build_equality_matrix.py |
| Collector schema test | tests/readiness/test_collect_equality.py |
| Schedule entry | config/scheduled-tasks/schedule-tasks.yaml |
| Plan reviews | scripts/review/results/2026-07-09-plan-3408-{claude,codex,gemini}.md |

---

## Deliverable

A `harness_checkup` machine-equality dimension: `audit_harness_checkup.py` emits allowlist-safe `/doctor` hygiene facts per box daily, `collect-equality.sh` folds them into `equality-<machine>.yaml` fail-closed, and `build-equality-matrix.py` renders a graded row — so version-staleness, broken settings/agents, duplicate installs, extension clutter, and non-auto default mode become visible and comparable across all machines.

---

## Pseudocode

```
# audit_harness_checkup.py  (run daily; facts-only, allowlist-safe)
def main():
    fp = read_json(".claude/state/equivalence/local-fingerprint.json")   # REUSE #3059
    version   = fp.get("harness_version")        # do NOT re-shell claude --version
    install   = fp.get("harness_install")
    latest    = lookup_latest(install)           # npm view @latest --registry pinned, cwd=$HOME,
                                                 # SKIP if CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC set
    facts = {
      "audited_at": utc_now_iso(),               # kept in canonical payload -> forces rewrite
      "cc_version": version, "cc_latest": latest,
      "version_current": semver_ge(version, latest) if latest else None,
      "install_method": install,
      "duplicate_installs": count_extra_installs(),        # which -a claude vs installMethod
      "settings_parse_ok": all(jq_empty(f) for f in settings_cascade),
      "broken_agents": count_bad_or_colliding_agent_defs(),
      "unused_skills": count_zero_use_user_skills(),       # skillUsage==0 & no window hits
      "unused_plugins": count_zero_use_plugins(),
      "default_mode": read(".permissions.defaultMode"),    # enum
      "auto_mode_default": (default_mode == "auto"),
    }
    assert_allowlist_safe(facts)   # no names/tokens/paths/cron/env/transcript strings
    write_json(f".claude/state/harness-checkup-{machine}.json", facts)

# build-equality-matrix.py
def harness_checkup_verdict(report):
    hc = report["dimensions"].get("harness_checkup")
    if not hc or hc.get("audited_at") is None:  return "missing-evidence"
    if hc["settings_parse_ok"] is False or hc["duplicate_installs"] > 0 \
       or hc["broken_agents"] > 0:              return "red"
    if hc["version_current"] is False or not hc["auto_mode_default"] \
       or hc["unused_skills"] > CLUTTER or hc["unused_plugins"] > 0:  return "amber"
    return "green"
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | scripts/curation/audit_harness_checkup.py | doctor-hygiene fact audit (facts-only) |
| Create | scripts/curation/audit-harness-checkup.ps1 | Windows schema-parity companion |
| Create | tests/curation/test_audit_harness_checkup.py | TDD for the audit |
| Modify | scripts/readiness/collect-equality.sh | add §6f `harness_checkup:` block (read fail-closed) |
| Modify | scripts/readiness/collect-equality.ps1 | keep YAML schema parity with the .sh |
| Modify | scripts/readiness/build-equality-matrix.py | verdict fn + dispatch + ROW |
| Modify | tests/readiness/test_build_equality_matrix.py | verdict cases (green/amber/red/missing) |
| Modify | tests/readiness/test_collect_equality.py | new-dimension schema case |
| Modify | config/scheduled-tasks/schedule-tasks.yaml | daily `harness-checkup-audit` entry |
| Update | docs/plans/README.md | index this plan |

---

## TDD Test List

| Test name | What it verifies | Input | Output |
|---|---|---|---|
| test_audit_reads_fingerprint_version | reuses fingerprint, no re-shell | fp json w/ harness_version=2.1.205 | facts.cc_version==2.1.205 |
| test_audit_version_current_true | currency compare | version==latest | version_current True |
| test_audit_version_behind | behind latest | version<latest | version_current False, verdict amber |
| test_audit_no_network_path | essential-traffic mode | env flag set | cc_latest None, version_current None (no crash) |
| test_audit_settings_parse_fail | broken settings.json | malformed json fixture | settings_parse_ok False → red |
| test_audit_broken_agent_collision | colliding agent names | 2 same-name defs | broken_agents>=1 |
| test_audit_allowlist_safe | no names/tokens/paths leak | rich fixture | assert no disallowed keys/strings emitted |
| test_audit_malformed_fingerprint | fail-closed on garbled fp | truncated json | facts written w/ nulls, exit 0 |
| test_collect_reads_checkup_failclosed | collector null when file absent | no state file | dimension present, audited_at null |
| test_verdict_missing_evidence | absent/garbled → missing | no dimension | "missing-evidence" |
| test_verdict_green_clean | all-good | current+clean+auto | "green" |
| test_verdict_red_duplicate_install | duplicate installs | duplicate_installs=1 | "red" |

---

## Acceptance Criteria

- [ ] `uv run pytest tests/curation/test_audit_harness_checkup.py tests/readiness/test_build_equality_matrix.py tests/readiness/test_collect_equality.py -v` passes
- [ ] `collect-equality.sh --stdout` on this box emits a `harness_checkup:` block with the 12 facts, no disallowed content (grep the output for abs paths / tokens / names → empty)
- [ ] `build-equality-matrix.py` renders the new row across all boxes; a box with no state file grades MISSING-EVIDENCE (fail-closed), not green
- [ ] `.ps1` companions keep YAML schema parity (existing `test_collect_equality_ps1_schema.py` still green)
- [ ] Daily schedule entry validates: `uv run python scripts/cron/validate-schedule.py`
- [ ] Legal/security scan clean: `scripts/legal/legal-sanity-scan.sh`
- [ ] Review artifacts posted (T3 → 3 providers)

---

## Adversarial Review Summary

<!-- Filled after Step 4 (T3 = Claude + Codex + Gemini). Not posted to GitHub until populated. -->

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | pending | |
| Codex | pending | |
| Gemini | pending | |

**Overall result:** pending

---

## Risks and Open Questions

- **Risk — allowlist leakage:** the audit touches secret-adjacent files (`~/.claude.json`, settings). It must emit ONLY counts/booleans/enums/version strings. Mitigation: `assert_allowlist_safe()` + a dedicated test + the collector's own §-block re-validates on read.
- **Risk — network in a cron:** the latest-version lookup runs from `$HOME` with a pinned registry and honors `CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC`; failure degrades to `cc_latest=null` → version_current null (not red). Daily cadence bounds egress.
- **Risk — Windows parity:** `.ps1` companions must stay schema-identical or `test_collect_equality_ps1_schema.py` fails. Keep field set minimal.
- **Open (for approval):** clutter thresholds — `unused_skills > N` amber (propose N=15) and `unused_plugins > 0` amber. Confirm N.
- **Open (for approval):** dimension name `harness_checkup` vs `harness_hygiene`. Propose `harness_checkup` (matches issue + /doctor mental model).

---

## Complexity: T3

Multi-file across two subsystems (curation audit + readiness collector/matrix), cross-OS Windows parity, systemic harness surface, network-in-cron with fail-closed semantics, and a secret-adjacent allowlist boundary. Warrants 3-provider adversarial review at both plan and code stages.
