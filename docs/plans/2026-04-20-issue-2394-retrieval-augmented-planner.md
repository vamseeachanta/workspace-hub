# Plan for #2394: Retrieval-augmented planner — v3 (post-iter-2 fixes + embedded evidence)

> **Status:** plan-review (iteration 3 of 3 — final)
> **Complexity:** T2
> **Date:** 2026-04-20 (v3)
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2394
> **Prior reviews:** v1 at `5b4c347cd` (Claude MINOR + Codex/Gemini MAJOR); v2 at `27821dafa` (Codex/Gemini MAJOR).

---

## Revision History

- **v1:** initial draft; convergent P1s: sha256, skip-log undefined, hook mischar, gh auth, AC gaps.
- **v2:** added §Identity Contract / §Tier Assignment / §Threat Model / §Dep Matrix / §AC↔Test Map. Still MAJOR on (a) identity rule self-contradiction, (b) dep-vs-risks contradiction, (c) bypass→PASS unsafe, (d) `candidates - filtered` TypeError, (e) AC-test gaps, (f) unverified claims.
- **v3 (this revision):**
  - **M1 fix:** Identity Contract rewritten — CLI accepts `sha256:` and `md5:` (both); rejects only bare-hex and path-only. `md5:` entries appear in emitted table with `identity_status: legacy-read-only` annotation. This resolves the CLI-vs-conformance contradiction.
  - **M1 fix:** Dependency contradiction resolved — `#2402` is **hard**; no grep-stub fallback. Implementation waits for `#2402` approval.
  - **M1 fix:** Bypass semantics — hook records distinct `BYPASSED` outcome in audit log + distinct git-commit trailer `Planner-Retrieval-Bypass: <reason>`; never `PASS`.
  - **M1 fix:** `candidates - filtered` replaced with list comprehension `[c for c in candidates if c not in filtered]`.
  - **M1 fix:** AC coverage — new test `test_skill_file_contains_cli_reference` for SKILL.md update.
  - **M2 fix:** Evidence block embeds actual `gh`/`ls` output per updated template.

---

## Resource Intelligence Summary

### Existing repo code
- `.claude/skills/coordination/issue-planning-mode/SKILL.md` — planning workflow mandate.
- `docs/plans/_template-issue-plan.md` — plan template (v3 relies on 2026-04-20 Evidence-section addition).
- `scripts/enforcement/install-hooks.sh` — hook installer.
- `scripts/conformance/` — **does not exist**; this plan creates it.

### Standards
Not applicable.

### LLM Wiki pages consulted
Not applicable (tooling).

### Documents consulted
- `docs/plans/2026-04-11-issue-2208-intelligence-retrieval-contract-for-github-issue-workflows.md` — retrieval contract extended.
- Operating model §3/§4/§7.

### Dependency Matrix

| Issue | State | Relationship | Behavior if unshipped |
|---|---|---|---|
| #2402 | OPEN | **HARD** | implementation WAITS; no stub fallback |
| #2403 | OPEN | transitive (via #2402) | same |
| #2208 | CLOSED | extends | — |
| #2206 | OPEN status:plan-approved | adds check class | — |

### Gaps identified
- No planner-side retrieval tool.
- No conformance check for retrieval-block presence.
- No audit-log standard.

### Evidence (embedded verification)

**Issue statuses** (via `gh issue view`):
- `#2402` — **OPEN** — feat(doc-intel): build embeddings index L2+L3 + query CLI (single authoritative tier)
- `#2403` — **OPEN** — feat(doc-intel): embeddings model-selection spike — BGE-M3 / Voyage / text-embedding-3-large
- `#2208` — **CLOSED** — feat(workflow): require intelligence retrieval contract in GitHub issue planning/execution/review
- `#2206` — **OPEN** (status:plan-approved) — feat(knowledge): validate single-source-of-truth pyramid conformance

**File existence:**
```
EXISTS: .claude/skills/coordination/issue-planning-mode/SKILL.md
EXISTS: docs/plans/_template-issue-plan.md
EXISTS: scripts/enforcement/install-hooks.sh
MISSING (new — this plan creates): scripts/conformance/
```

**§3 read-only carve-out evidence** (operating-model §3 status-vocab table requires `md5:<hex>` permitted for reads from `og_standards` legacy entries; see `phase-a-index.py:135-137` in #2392 v3 evidence block). This plan's conformance check accepts `md5:` with `identity_status: legacy-read-only` annotation, matching the live-data contract.

---

## Identity Contract (v3 — resolved self-contradiction)

**Single unified rule (no more CLI/conformance disagreement):**

All `doc_key` values, at BOTH CLI and conformance stages, handled identically:
- `sha256:<64-hex>` → `identity_status: ok` → included in table, check PASS.
- `md5:<32-hex>` → `identity_status: legacy-read-only` → included in table with annotation, check PASS (per §3 read-only carve-out).
- Bare-hex (no prefix) → `identity_status: invalid` → excluded from table, conformance FAIL if present.
- Path-only (no prefix AND no hex) → `identity_status: invalid` → same as bare-hex.

CLI and conformance check share a `classify_identity(key)` helper to guarantee consistency.

Tests:
- `test_sha256_included_in_table_ok_status`
- `test_md5_included_with_legacy_annotation` (now actually reachable, unlike v2)
- `test_bare_hex_excluded_from_table_and_conformance_fails_if_present`
- `test_path_only_identity_rejected`
- `test_cli_and_conformance_use_same_classify_helper` (invariant test)

---

## Cross-Machine Tier Assignment

| Artifact | Path | Tier | Notes |
|---|---|---|---|
| Skill file | `.claude/skills/coordination/issue-planning-mode/SKILL.md` | 1 | git-tracked authoritative |
| Template | `docs/plans/_template-issue-plan.md` | 1 | git-tracked |
| Plan files | `docs/plans/*.md` | 1 | git-tracked |
| Conformance check | `scripts/conformance/planner_retrieval_check.py` | 1 | git-tracked (new) |
| CLI | `scripts/knowledge/retrieve_plan_candidates.py` | 1 | git-tracked |
| **Audit log** | `logs/planner-retrieval/bypass-YYYY-MM-DD.jsonl` | **3 local-cache** | never authoritative; gitignored |
| **Git commit trailer** | `Planner-Retrieval-Bypass: <reason>` in commit message | 1 git-tracked (implicit via git log) | durable proof-of-bypass |
| Install side-effect | `.git/hooks/pre-push` | **not an artifact** | generated by install-hooks.sh |

Dual-logging rationale: local JSONL gives per-machine rapid audit; git-commit trailer survives across machines and is part of permanent history. Reviewer concern about tier-3 log "getting lost" addressed by trailer.

---

## Threat Model

**Input surfaces:** GitHub issue body (untrusted, fetched via `gh`), CLI args (trusted local), plan files (trusted git-tracked).
**Trust boundaries:** issue body is string-only; no shell interpolation, no eval. Plan files trusted.
**`gh` auth:** uses existing `gh auth login` token (ecosystem-required; no new secret surface). Plan does not store or log the token.

**Tests:**
- `test_issue_body_with_shell_metacharacters_treated_as_opaque`
- `test_conformance_is_read_only_on_plan_files`
- `test_audit_log_path_cannot_be_overridden`
- `test_no_gh_auth_token_leaked_in_logs`

---

## Bypass Semantics (v3 — resolves iter-2 P1 safety concern)

`--skip-retrieval <reason>`:
1. Requires non-empty `<reason>` string (test: `test_skip_requires_reason`).
2. Writes to `logs/planner-retrieval/bypass-YYYY-MM-DD.jsonl`:
   ```json
   {"ts": "...", "issue": NNNN, "reason": "...", "user": "...", "hostname": "...", "commit_preparing": "..."}
   ```
3. Instructs the author to add a trailer to the eventual commit message: `Planner-Retrieval-Bypass: <reason>`.
4. Conformance check records outcome as **`BYPASSED`**, not `PASS` (distinct state).
5. Pre-push hook accepts `BYPASSED` for passage, but flags it distinctly in hook output: `[WARNING] bypassed planner retrieval: <reason>`.

**Tests:** `test_bypass_outcome_distinct_from_pass`, `test_bypass_requires_reason`, `test_bypass_logs_and_prints_warning`, `test_commit_trailer_recommended`.

---

## AC ↔ Test Map

| AC | Test(s) |
|---|---|
| CLI emits markdown block | `test_retrieve_returns_markdown_block` |
| Empty corpus handled | `test_retrieve_empty_corpus` |
| Invalid issue num | `test_retrieve_issue_not_found` |
| Conformance passes on filled block | `test_check_passes_on_filled_block` |
| Missing block | `test_check_fails_missing_block` |
| Blank status | `test_check_fails_blank_status` |
| REJECTED without reason | `test_check_fails_rejected_no_reason` |
| `--skip-retrieval` requires reason + logs + commit trailer | 4 bypass tests above |
| Hook installation wires check | `test_install_hooks_registers_planner_check` |
| Template updated | `test_template_contains_retrieval_candidates_section` (static grep) |
| **SKILL.md updated** | **`test_skill_file_contains_cli_reference`** (NEW — addresses v2 Codex finding) |
| Identity unified | all 5 `test_*_identity_*` above |
| Threat tests | listed |
| 3 real-issue smoke | reviewer-task |

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-04-20-issue-2394-retrieval-augmented-planner.md` |
| CLI | `scripts/knowledge/retrieve_plan_candidates.py` |
| Conformance package | `scripts/conformance/__init__.py` |
| Check | `scripts/conformance/planner_retrieval_check.py` |
| Tests | `tests/knowledge/test_retrieve_plan_candidates.py`, `tests/conformance/test_planner_retrieval_check.py` |
| Audit log dir | `logs/planner-retrieval/` (tier-3, gitignored) |

---

## Deliverable

CLI + conformance check + dual-log bypass semantics that auto-surface top-K retrieval candidates at Resource-Intel time; `sha256:` and `md5:` identities handled uniformly; failed mandatory check recorded as `BYPASSED`, never `PASS`.

---

## Pseudocode (v3 — fixes TypeError + bypass contradiction)

```python
def classify_identity(key):  # single helper — used by both CLI + conformance
    if key is None: return "invalid"
    if re.match(r"^sha256:[0-9a-f]{64}$", key): return "ok"
    if re.match(r"^md5:[0-9a-f]{32}$", key): return "legacy-read-only"
    return "invalid"

def retrieve(issue_number, top_k=10):
    issue = gh_view(issue_number)  # opaque text
    candidates = query_embeddings(issue.title + " " + issue.body[:500], top_k, layer="both")
    annotated = [(c, classify_identity(c.doc_key)) for c in candidates]
    valid = [c for c, status in annotated if status != "invalid"]
    invalid = [c for c, status in annotated if status == "invalid"]
    if invalid: log_skips(invalid)
    emit markdown block with valid rows (identity_status column pre-filled ok/legacy-read-only)

def conformance_check(plan_file):
    parse plan → find "## Retrieval Candidates" section; if absent → FAIL
    for row in rows:
        if classify_identity(row.doc_key) == "invalid" → FAIL
        if row.status blank → FAIL
        if row.status startswith "REJECTED" and no colon-reason → FAIL
    return PASS

def bypass(skip_reason):
    if not skip_reason: return error "bypass requires --skip-retrieval <reason>"
    append JSONL entry to logs/planner-retrieval/bypass-YYYY-MM-DD.jsonl
    print "[WARNING] bypassed planner retrieval: {reason}"
    print "Add this line to your commit: Planner-Retrieval-Bypass: {reason}"
    return BYPASSED  # distinct outcome from PASS
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | `scripts/knowledge/retrieve_plan_candidates.py` | CLI |
| Create | `scripts/conformance/__init__.py` | new package |
| Create | `scripts/conformance/planner_retrieval_check.py` | check |
| Create | `tests/knowledge/test_retrieve_plan_candidates.py` | CLI tests |
| Create | `tests/conformance/test_planner_retrieval_check.py` | check tests |
| Modify | `.claude/skills/coordination/issue-planning-mode/SKILL.md` | reference new tool |
| Modify | `docs/plans/_template-issue-plan.md` | add Retrieval Candidates section |
| Modify | `scripts/enforcement/install-hooks.sh` | wire check + handle `BYPASSED` |
| Modify | `.gitignore` | ensure `logs/planner-retrieval/` ignored |

---

## Acceptance Criteria

All v2 ACs plus:
- [ ] Identity rule unified — one `classify_identity` helper in both CLI + conformance (invariant test)
- [ ] Bypass records distinct `BYPASSED` outcome (not `PASS`) — tested + hook-verified
- [ ] Commit trailer recommendation printed on bypass — tested
- [ ] SKILL.md update tested (not just implied)
- [ ] No TypeError from list arithmetic (comprehension not set-sub)

---

## Adversarial Review Summary

| Provider | Verdict | Artifact |
|---|---|---|
| Claude v1 | MINOR | `2026-04-20-plan-2394-claude.md` |
| Codex v1 / Gemini v1 | MAJOR / MAJOR | `...-codex.md`, `...-gemini.md` |
| Codex v2 / Gemini v2 | MAJOR / MAJOR | `2026-04-20-v2-plan-2394-{codex,gemini}.md` |
| Codex v3 / Gemini v3 | PENDING | — |

---

## Risks and Open Questions

- **Risk:** Hard-dep on #2402 blocks implementation. **Accepted** — no stub fallback (v3 eliminates v2 contradiction).
- **Risk:** Bypass mechanism could be abused. Mitigation: dual-log (JSONL local + git trailer durable) + audit-cadence reviews.

---

## Complexity: T2
