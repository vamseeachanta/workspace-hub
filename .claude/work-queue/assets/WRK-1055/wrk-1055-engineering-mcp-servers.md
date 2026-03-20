# WRK-1055 Plan — Engineering MCP Servers

**Route**: B (medium) | **Machine**: dev-primary
**Revision**: v2 — revised per Codex REQUEST_CHANGES findings
**Status**: Approved (Stage 5)

---

## Scope Note

Codex/Gemini MCP wiring is explicitly out of scope for this WRK. Claude-only on dev-primary.
Codex/dev-secondary wiring captured as follow-on (WRK-1012 scope).

---

## Phase 1: Create `config/ai-tools/mcp-servers.yaml` (candidates, not yet active)

Create the catalog file with candidate entries. Status starts as `evaluated` — promoted to
`active` only after trust assessment passes (Phase 2) and installation succeeds (Phase 3).

**Steps:**
1. Read `config/ai-tools/subscriptions.yaml` for header/structure pattern
2. Write `config/ai-tools/mcp-servers.yaml` with fields:
   `name`, `id`, `status` (active|evaluated|pending), `install_command`, `runtime`,
   `use_case`, `auth_required`, `source_repo`, `license`, `maintainer`, `last_reviewed`,
   `commit_sha` (populated in Phase 3), `permissions_review`, `rollback_command`,
   `trust_assessment`, `related_wrk`
3. Add `semantic_scholar_mcp` entry with `status: evaluated`
4. Add ≥1 additional candidate with `status: evaluated`

**Test**: File exists, parses as valid YAML, ≥2 entries, no `status: active` entries yet.

---

## Phase 2: Trust Assessment for Semantic Scholar MCP

Perform trust assessment before any installation. Document in `mcp-servers.yaml`.

**Trust checklist (all required):**
- Canonical upstream repo confirmed (not a fork or aggregator mirror)
- Maintainer identity and last commit activity reviewed
- License confirmed (must be OSI-approved)
- Requested permissions: read-only network calls only? File system access? Env vars?
- Transitive dependencies reviewed (`uv tree` or `pip show`)
- Rollback command documented: `claude mcp remove semantic-scholar-mcp`
- Install path: uvx or uv tool install (no bare pip)

**Steps:**
1. Browse `https://github.com/FujishigeTemma/semantic-scholar-mcp`
2. Identify latest commit SHA on main branch
3. Check dependencies (`pyproject.toml` or `requirements.txt`)
4. Populate trust assessment fields in `mcp-servers.yaml`
5. Record verdict: pass/fail. Only proceed to Phase 3 if PASS.

**Test**: `trust_assessment: pass` in mcp-servers.yaml; all checklist fields populated.

---

## Phase 3: Install Semantic Scholar MCP (after trust gate)

Install with pinned commit SHA and wire into Claude config.

**Steps:**
1. Install: `claude mcp add semantic-scholar-mcp -s project -- uvx --from git+https://github.com/FujishigeTemma/semantic-scholar-mcp@<SHA> semantic-scholar-mcp`
   (use `-s project` scope — lower blast radius than `-s user`)
2. Verify: `claude mcp list` shows `semantic-scholar-mcp`
3. Verify config written to: `.claude/settings.json` (project-scoped) — confirm entry present
4. Run smoke test query: search "offshore pipeline fatigue DNV" — returns ≥1 result
5. Run rollback test: `claude mcp remove semantic-scholar-mcp` → confirm removed from list
6. Re-install: repeat install step — confirm it comes back
7. Update `mcp-servers.yaml`: set `status: active`, populate `commit_sha`

**Test**: `claude mcp list` shows entry; `.claude/settings.json` has mcpServers entry;
smoke query returns results; rollback and re-install both succeed.

---

## Phase 4: Evaluate ≥1 Additional Engineering-Domain Server

Identify and evaluate one more candidate via live registry query.

**Steps:**
1. Query `https://registry.modelcontextprotocol.io` API with keywords:
   geospatial, weather, materials, structural, offshore (fallback: browse mcpmarket.com)
2. Identify top candidate relevant to engineering workflows
3. Run trust assessment (same checklist as Phase 2) — document in `mcp-servers.yaml`
4. Set `status: evaluated` (not `active` unless trust passes and install is in scope)

**Test**: ≥1 entry with `status: evaluated`, trust assessment fields populated, verdict recorded.

---

## Phase 5: Write `.claude/docs/mcp-servers.md`

Document usage patterns, install procedure, and trust assessment template.

**Sections:**
- Why MCP servers (not training knowledge) — cite Semantic Scholar as working example
- Install pattern: `claude mcp add` command with scope flag, commit pinning requirement
- Trust assessment checklist (copy from Phase 2 — formalise as template)
- Removal pattern: `claude mcp remove <name>`
- How to use Semantic Scholar MCP from Claude Code (example prompt)
- How to add new servers: update mcp-servers.yaml → trust assessment → install → promote to active
- Note: installed MCPs enhance Stage 2 (Resource Intelligence) — agents can query live literature

**Test**: File exists, ≤200 lines, contains install + trust checklist + removal sections.

---

## Phase 6: Codex Cross-Review (hard gate)

**Steps:**
1. Write review input: `scripts/review/results/wrk-1055-phase-1-review-input.md`
   covering all deliverables: mcp-servers.yaml, .claude/settings.json change, mcp-servers.md
2. Run: `scripts/review/cross-review.sh scripts/review/results/wrk-1055-phase-1-review-input.md all`
3. Fix any MAJOR findings; document deferred MINORs

**Test**: Codex verdict = APPROVE or MINOR (no MAJOR).

---

## Acceptance Criteria Mapping

| AC | Phase |
|----|-------|
| `config/ai-tools/mcp-servers.yaml` created | Phase 1 |
| Trust assessment completed before install | Phase 2 |
| Semantic Scholar MCP installed, reachable, rollback tested | Phase 3 |
| ≥1 additional MCP identified and evaluated | Phase 4 |
| Usage documented in `.claude/docs/mcp-servers.md` | Phase 5 |
| Cross-review (Codex) passes | Phase 6 |

---

## Out of Scope

- Codex/Gemini MCP config wiring (different config format; deferred)
- dev-secondary MCP setup (WRK-1012 scope)
- arXiv/BSEE custom MCP wrappers (separate WRKs)
- WRK-578 registry audit skill (separate WRK)
