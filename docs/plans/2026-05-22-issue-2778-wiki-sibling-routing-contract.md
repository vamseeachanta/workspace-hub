# Plan for #2778: Lock data/knowledge/result search routing across llm-wiki + llm-wiki-<client> siblings

> **Status:** draft — r1 + r2 reviews complete, r3 inline patches applied (per `feedback_r3_inline_loop_break_pattern`: r1/r2 surface DIFFERENT defects each round → apply inline, do NOT dispatch r3 review). Single-provider signal across both rounds (Gemini); Claude+Codex UNAVAILABLE persistent. Surfacing to user with explicit consensus-gap disclosure.
> **Complexity:** T3
> **Date:** 2026-05-22
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2778
> **Worktree:** `/mnt/local-analysis/agent-worktrees/workspace-hub-issue-2778-llm-wiki-routing` (branch `issue/2778-llm-wiki-routing`)
> **Plan slug rationale:** `wiki-sibling-routing-contract` (the briefing's suggested `…-sibling-sso` slug is avoided because "SSO" conflates with OAuth and with #2775's "sibling-SSoT" harness work — this issue is the routing contract, not the SSoT harness)
> **Review artifacts (landed):** r1 + r2 at `scripts/review/results/2026-05-22-plan-2778-r{1,2}-{claude,codex,gemini,disagreement}.md`

---

## Resource Intelligence Summary

### Existing repo code

- **Found:** `.claude/rules/codes-standards-data-routing.md` (180+ lines) — covers vendor-licensed standards data → private `llm-wiki`, public-domain federal data → `worldenergydata-wiki`. **Does NOT name the per-client sibling pattern** — that gap is precisely what #2778 fills.
- **Found:** `.claude/rules/calc-citation-contract.md` — defines `Citation` sidecar emission for standards-derived constants; pilot LIVE at digitalmodel#2685. **Gap:** sidecar schema has no `source_sibling:` field, so a citation can't tell whether it originated from `llm-wiki` or `llm-wiki-<client>`.
- **Found:** `.claude/skills/research/llm-wiki-public-private-routing/SKILL.md` (Skill D) — encodes the 2026-05-20 user routing directive (exact client results → private; abstracted → public; public-availability exception for verified-public project names). This skill defines the abstraction-gate decision tree the new rule will reference.
- **Found:** `.claude/skills/coordination/client-llm-wiki-factory/SKILL.md` v1.0.0 — 13-step operator checklist for bootstrapping `llm-wiki-<client>` repos. Already uses suffix-form naming. Plan must update its checklist to instantiate the new `projects/<slug>/` skeleton automatically.
- **Found:** `config/client-wikis.yml` — registry with 6 client entries (`acma` bootstrapped 2026-05-18; `rock-oil-field`, `client-projects`, `doris`, `frontierdeepwater`, `saipem` planned). Plan extends the schema to declare project-nesting layout per client.
- **Found:** `templates/client-llm-wiki/` — existing scaffolding tree (`DATA-CYCLE.md`, `ledgers/`, `LICENSE`, `pages/`, `README.md`, `REDACTION-POSTURE.md`, `reports/`, `sources/`). **Gap:** no `projects/` subtree — the per-project skeleton is what #2778 adds.
- **Found:** `scripts/readiness/check-sibling-sso-flow.py` and `scripts/readiness/repair-sibling-sso-flow.py` (added in commit `326ada4cd` for #2775). Checker sections: `memory`, `skills`, `harness_contracts`, `registry`. **Gap:** no wiki-routing section — the new Level-2 enforcement script for frontmatter consistency will be a sibling, not an extension.
- **Found:** `tests/readiness/test_sibling_agents_contract.py`, `test_sibling_sso_repair_dry_run.py`, `test_sync_agent_configs_pyyaml_fallback.py`, plus 5 more (#2775 landing). Plan adds parallel tests for the new enforcement script.
- **Found:** `scripts/enforcement/check-no-abs-paths.sh`, `check-no-conflict-markers.sh`, `check-harness-file-size.sh` — existing Level-2 enforcement-script pattern. The new `check-wiki-sibling-frontmatter.sh` will follow the same shape (exit 0/1, staged-content scope, per-line sentinel allowlist).

### Standards
Not applicable — this is a governance/architecture issue, not an engineering-calculation issue. Per `_template-issue-plan.md` retrieval contract, this row is explicitly N/A.

### LLM Wiki pages consulted
Not applicable for plan drafting — this issue defines the routing contract that future wiki pages must obey. No existing wiki page is consulted as authority; the existing skill `research/llm-wiki-public-private-routing` is the operational source.

### Documents consulted

- **`docs/session-handoffs/2026-05-20-handoff-digitalmodel-616-ocimf-to-llm-wiki.md`** — operational precedent. OCIMF MEG3/MEG4 routing matrix: public methodology pages → `llm-wiki`; SIROCCO-specific calc results → `llm-wiki-acma`. Cited by #2778 body as the speculated `llm-wiki-sirocco` source that #2778 explicitly *corrects* (one sibling per client, not per project).
- **`docs/session-handoffs/2026-05-22-issue-2760-sirocco-pass-h-exit.md`** — confirms B1528 SIROCCO is a project under client ACMA, and the OCIMF workbook is at `/mnt/ace/acma-codes/OCIMF/OCIMF Coef.xlsx`. Validates the project-as-folder pattern with a live example.
- **`docs/plans/_template-issue-plan.md`** — plan template requiring `client:` field is the modification target.
- **#2778 issue body** (the issue itself) — convention locked by user 2026-05-22; 4 open questions; 6 acceptance criteria.
- **#2744 epic body** — first client-sibling pilot. Currently references `acma-llm-wiki` (prefix) in the body text, but the live repo `vamseeachanta/llm-wiki-acma` exists in suffix form (created 2026-05-18, registered `bootstrapped`). #2778 body's first AC ("rename before repo creation") is OBE; plan handles this explicitly.
- **#2776 issue body** — cross-wiki linking discipline follow-on from worldenergydata#429. #2778 extends with client→generic / generic→client / client→client rules.
- **#2774 issue body** — generic ingest umbrella; routes vendor-licensed standards content to `llm-wiki`. Validates that the routing-target field in writer config (`LLM_WIKI_TARGET=generic`) is the right shape.
- **#2731 issue body** — data-location inventory parent (`status:needs-plan`). Captures the `client_projects` (underscore) and `frontierdeepwater` (no hyphen) bucket-name edge cases that #2778's enforcement script must accommodate.

### Gaps identified

What does not exist today and this plan creates:

1. **No canonical rule file** for sibling-routing. `.claude/rules/codes-standards-data-routing.md` covers public/private routing for standards data only; per-client sibling routing has no rule. → **New file:** `.claude/rules/wiki-sibling-routing.md`.
2. **No frontmatter validator** for `visibility:` / `client:` / `project:` consistency on staged wiki content. → **New script:** `scripts/enforcement/check-wiki-sibling-frontmatter.sh`.
3. **No `private-client-llm-wiki` visibility tier** in the frontmatter schema. Current tiers: `private-llm-wiki`, `public-federal-data`. → **Schema extension** documented in the new rule + validated by the enforcement script.
4. **No `client:` (required) or `project:` (optional) fields** in `docs/plans/_template-issue-plan.md`. → **Template modification**.
5. **No `source_sibling:` or `source_project:` fields** in `Citation` sidecar (per calc-citation-contract.md). → **Schema extension** to citation contract.
6. **No `projects/` skeleton** in `templates/client-llm-wiki/`. → **New template subtree:** `templates/client-llm-wiki/projects/_template-project/{raw,extracted,methodology,results}/`.
7. **No project-nesting field** in `config/client-wikis.yml` schema (currently per-client at the top level only). → **Registry schema extension** for declaring per-client `projects:` list (optional).

### Evidence (embedded verification)

**Issue statuses** (verified 2026-05-22 via `gh issue view`):
- `#2778` — OPEN, status:needs-plan, priority:high, cat:data-pipeline, cat:harness, domain:knowledge, domain:repo-organization — "feat(architecture): lock data/knowledge/result search routing across llm-wiki + llm-wiki-<client> siblings"
- `#2744` — OPEN — "epic(acma): client project data-cycle readiness and private llm-wiki launch"
- `#2774` — OPEN — "Private llm-wiki corpus-ingest program (post-2026-05-20 privacy flip)"
- `#2775` — CLOSED 2026-05-22T18:52:37Z, status:done — "fix(harness): restore workspace-hub SSoT flow across sibling repos"
- `#2776` — OPEN — "Cross-wiki linking discipline — supersede stale governance + add enforcement script"
- `#2731` — OPEN, status:needs-plan — "feat(data-governance): inventory and normalize canonical data/repo locations for llm-wiki promotion"
- `#2400` — OPEN, priority:medium — "feat(doc-intel): MCP server core — doc_key_lookup, wiki_search, registry_query"

**Repo existence** (verified 2026-05-22 via `gh repo view vamseeachanta/llm-wiki-acma --json name,visibility,createdAt`):
- EXISTS: `vamseeachanta/llm-wiki-acma` — PRIVATE — created 2026-05-18T09:36:50Z
- EXISTS: `vamseeachanta/llm-wiki` — PRIVATE since 2026-05-20 (per `project_llm_wiki_privacy_flip` memory)
- EXISTS: `vamseeachanta/worldenergydata-wiki` — public sibling for federal public-domain data (covered by codes-standards-data-routing.md §6, out of scope for #2778)

**File existence** (`ls -la` 2026-05-22, in worktree):
- EXISTS: `.claude/rules/codes-standards-data-routing.md`
- EXISTS: `.claude/rules/calc-citation-contract.md`
- EXISTS: `.claude/rules/README.md`
- EXISTS: `.claude/skills/research/llm-wiki-public-private-routing/SKILL.md`
- EXISTS: `.claude/skills/coordination/client-llm-wiki-factory/SKILL.md`
- EXISTS: `.claude/skills/coordination/issue-planning-mode/SKILL.md`
- EXISTS: `config/client-wikis.yml` (6 client entries)
- EXISTS: `templates/client-llm-wiki/` (existing subtree: `DATA-CYCLE.md`, `ledgers/`, `LICENSE`, `pages/`, `README.md`, `REDACTION-POSTURE.md`, `reports/`, `sources/`)
- EXISTS: `scripts/enforcement/check-no-abs-paths.sh`, `check-no-conflict-markers.sh`, `check-client-wiki-registry.sh` (existing pattern)
- EXISTS: `scripts/readiness/check-sibling-sso-flow.py`, `repair-sibling-sso-flow.py` (#2775 landing)
- EXISTS: `tests/readiness/test_sibling_agents_contract.py`, `test_sibling_sso_repair_dry_run.py`, `test_sync_agent_configs_pyyaml_fallback.py` (#2775 landing)
- EXISTS: `docs/plans/_template-issue-plan.md`
- EXISTS: `docs/plans/README.md` (the index — plan adds this row)
- MISSING (new — this plan creates): `.claude/rules/wiki-sibling-routing.md`
- MISSING (new — this plan creates): `scripts/enforcement/check-wiki-sibling-frontmatter.sh`
- MISSING (new — this plan creates): `templates/client-llm-wiki/projects/_template-project/`
- MISSING (new — this plan creates): `tests/enforcement/test_check_wiki_sibling_frontmatter.sh`
- MISSING (new — this plan creates): `tests/contract/test_planning_template_required_fields.py`
- MISSING (new — this plan creates): `tests/contract/test_citation_sidecar_schema_extensions.py`

**Gap proofs**:
- `ls .claude/rules/wiki-sibling-routing.md 2>&1` → "No such file or directory" → confirms the new rule does not yet exist.
- `grep -r "source_sibling" .claude/rules/ 2>&1 | wc -l` → 0 → confirms the citation contract has no sibling field today.
- `grep -r "client:" docs/plans/_template-issue-plan.md 2>&1 | wc -l` → 0 (only `<repo>` placeholder appears) → confirms the planning template has no `client:` field today.
- `ls templates/client-llm-wiki/projects/ 2>&1` → "No such file or directory" → confirms the project-folder skeleton does not exist today.

**Line excerpts** (verifying issue body's #2744 stale-AC claim, `gh repo view vamseeachanta/llm-wiki-acma`):
```
{"createdAt":"2026-05-18T09:36:50Z","name":"llm-wiki-acma","visibility":"PRIVATE"}
```
→ The repo already exists in suffix form. The #2778 body AC "rename `acma-llm-wiki` → `llm-wiki-acma` BEFORE any repo creation" is OBE. Plan addresses by replacing with the still-open work: project-nesting layout + #2744 AC text refresh (see Acceptance Criteria below).

**Reproduction proofs:** `N/A — governance/architecture issue, no runtime failure asserted` (per Step 1.5 skip-allowed exception of `coordination/issue-planning-mode`).

**Source count:** 9 distinct sources consulted (issue body + 8 others). Exceeds minimum 3 per retrieval contract #2208.

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-05-22-issue-2778-wiki-sibling-routing-contract.md` |
| New rule | `.claude/rules/wiki-sibling-routing.md` |
| Rule index update | `.claude/rules/README.md` |
| New enforcement script | `scripts/enforcement/check-wiki-sibling-frontmatter.sh` |
| Enforcement-script TDD tests | `tests/enforcement/test_check_wiki_sibling_frontmatter.sh` |
| Planning template modification | `docs/plans/_template-issue-plan.md` |
| Planning template TDD test | `tests/contract/test_planning_template_required_fields.py` |
| Citation contract modification | `.claude/rules/calc-citation-contract.md` |
| Citation sidecar TDD test | `tests/contract/test_citation_sidecar_schema_extensions.py` |
| Project-folder template skeleton | `templates/client-llm-wiki/projects/_template-project/{raw,extracted,methodology,results}/.gitkeep` |
| Project-folder README | `templates/client-llm-wiki/projects/_template-project/README.md` |
| client-llm-wiki-factory skill update | `.claude/skills/coordination/client-llm-wiki-factory/SKILL.md` |
| issue-planning-mode skill update | `.claude/skills/coordination/issue-planning-mode/SKILL.md` |
| client-wikis registry schema extension | `config/client-wikis.yml` (add `projects:` list per client; optional) |
| Plan-index update | `docs/plans/README.md` |
| Plan review — Claude r1/r2 | `scripts/review/results/2026-05-22-plan-2778-r{1,2}-claude.md` (both UNAVAILABLE) |
| Plan review — Codex r1/r2 | `scripts/review/results/2026-05-22-plan-2778-r{1,2}-codex.md` (both UNAVAILABLE) |
| Plan review — Gemini r1/r2 | `scripts/review/results/2026-05-22-plan-2778-r{1,2}-gemini.md` (r1: MAJOR, all absorbed; r2: MAJOR, all absorbed except F2 rejected) |
| Plan review — Disagreement r1/r2 | `scripts/review/results/2026-05-22-plan-2778-r{1,2}-disagreement.md` |

---

## Deliverable

A workspace-hub-enforced wiki-sibling routing contract that (a) names the `llm-wiki-<client>` suffix-form convention with one-sibling-per-client and project-as-folder rules, (b) extends the frontmatter / planning-template / citation-sidecar schemas with `client:` and `project:` fields, (c) provides a Level-2 enforcement script that fails CI on staged content where `visibility:` / `client:` / `project:` are inconsistent, and (d) updates the existing client-llm-wiki-factory skill + #2744 ACs to instantiate the new project-nesting layout — all so future agent invocations route data/knowledge/result search correctly across `llm-wiki` and the 6 planned `llm-wiki-<client>` siblings without per-session improvisation.

---

## Pseudocode

### Rule file (`.claude/rules/wiki-sibling-routing.md`)

Structure (mirrors existing rule files):
```
# Wiki sibling routing — agent rule

When: any agent action that reads, writes, or cites content across llm-wiki or
llm-wiki-<client> repos (including ingest, citation emission, page authoring,
chatbot response, report rendering, MCP wiki_search retrieval).

Why: prevents per-session routing improvisation, naming drift, cross-client
leakage, generic-vs-client content duplication, and ambiguous citation
provenance. Rationale locked by user 2026-05-22.

How to apply (numbered):
  1. Naming: `vamseeachanta/llm-wiki-<client>` suffix form; one sibling per
     client; projects nest as folders.
  2. Data layer: writers declare target via LLM_WIKI_TARGET={generic,<client>};
     frontmatter requires `visibility:` ∈ {private-llm-wiki,
     private-client-llm-wiki, public-federal-data}; `client:` and optional
     `project:` required when visibility is private-client-llm-wiki.
  3. Execution layer: planning template, agent dispatch prompts, citation
     resolvers, and skills accept `client` + optional `project` params; default
     `generic` only when explicitly unset; agent dispatch carries
     client+project context to subagents.
  4. Output layer: citation sidecars include `source_sibling:` (required) and
     `source_project:` (optional); reports/dashboards render the sibling badge
     prominently.
  5. Cross-sibling linking: client→generic = full URL (allowed); generic→client
     = forbidden (would leak / would 404 for public readers); client→other-
     client = forbidden (cross-client leakage). Extends #2776.
  6. Sanitized↔unsanitized: client wikis REFERENCE generic content via wiki
     slug; never re-derive locally. Generic← client only via the abstraction
     gate (Skill D, llm-wiki-public-private-routing).

Do not apply when:
  - The content is not destined for any wiki sibling (e.g., scratch report
    under docs/reports/ with no wiki copy).
  - The content is a workspace-hub-internal artifact (rule, skill, doc) where
    routing has no target.
  - The wiki target is worldenergydata-wiki (public-domain federal-data
    sibling) — that surface is covered by codes-standards-data-routing.md §6.

Pilot reference: client `acma` (status:bootstrapped in config/client-wikis.yml);
project `sirocco` under acma (live in #2760).

Related: codes-standards-data-routing.md (vendor-licensed standards),
calc-citation-contract.md (sidecar emission), llm-wiki-public-private-routing
SKILL.md (abstraction gate), client-llm-wiki-factory SKILL.md (bootstrap
operator checklist).
```

### Enforcement script (`scripts/enforcement/check-wiki-sibling-frontmatter.py`)

**Implementation language** (r2-F1 fix): Python 3 (stdlib `subprocess` + PyYAML, identical dependency footprint as `scripts/readiness/check-sibling-sso-flow.py` from #2775). Pythonic constructs (`dict.get`, exception handling, structured YAML parsing) make the script auditable and testable. A 4-line `.sh` wrapper at `scripts/enforcement/check-wiki-sibling-frontmatter.sh` exists only to satisfy hook scripts that exec by `.sh` filename — it `exec`s the `.py` script directly.

**Repo-scope contract.** The script is intended to live in workspace-hub (so it can be tested, audited, and version-controlled in one place) but is **installed into each wiki repo via the existing cross-repo hook installer** (`scripts/agents/install-pre-commit-hook-cross-repo.sh`, prior art from #2722). It runs **inside** the wiki repo at hook time; it does not scan from workspace-hub. This boundary is load-bearing for the corrections below.

**Two modes** (auto-detected): **pre-commit** (default — `git diff --cached`) and **CI** (`git diff --name-only --diff-filter=ACM ${BASE_REF}..HEAD`, where `BASE_REF` defaults to `origin/main` and is overridable via `--base=<ref>` or `$WIKI_FRONTMATTER_BASE_REF`). The script auto-detects CI mode when `CI=true` env var is set; otherwise pre-commit.

**Shallow-clone safety** (r2-F5 fix): in CI mode, the script attempts `git fetch --depth=1 origin "$base_ref" 2>/dev/null || true` before diffing, so it works under default GitHub Actions `fetch-depth: 1` without requiring callers to change their workflow. If the fetch fails and the ref is unreachable, the script exits 0 with a stderr warning (degrades gracefully — does not break the build).

```
def check_wiki_sibling_frontmatter(mode, base_ref):
    # r2-F6 fix: explicit bypass at top — same shape as ALLOW_ABS_PATHS in check-no-abs-paths.sh.
    if os.environ.get("WIKI_FRONTMATTER_ALLOW") == "1":
        print("[wiki-frontmatter] bypass via WIKI_FRONTMATTER_ALLOW=1", file=sys.stderr)
        sys.exit(0)

    # 1. Establish repo identity from inside the wiki repo (NOT from workspace-hub).
    repo_root = run(["git", "rev-parse", "--show-toplevel"]).strip()
    repo_name = os.path.basename(repo_root)

    # Bail early if not a wiki repo. Authoritative naming: `llm-wiki` (generic)
    # or `llm-wiki-<client>` (suffix form per the rule). Anything else exits 0.
    if repo_name != "llm-wiki" and not repo_name.startswith("llm-wiki-"):
        sys.exit(0)  # not a wiki repo; nothing to check

    is_client_wiki = repo_name.startswith("llm-wiki-")
    expected_client_slug = repo_name[len("llm-wiki-"):] if is_client_wiki else None

    # 2. Gather candidate files per mode.
    if mode == "ci":
        # r2-F5 fix: ensure base_ref is reachable in shallow clones; degrade gracefully.
        run(["git", "fetch", "--depth=1", "origin", base_ref], check=False, stderr=DEVNULL)
        try:
            changed_files = run(["git", "diff", "--name-only", "--diff-filter=ACM",
                                 f"{base_ref}..HEAD"]).splitlines()
        except CalledProcessError:
            print(f"[wiki-frontmatter] base ref '{base_ref}' unreachable in CI clone — "
                  f"skipping check (degrades open by design; configure fetch-depth: 0 to enforce)",
                  file=sys.stderr)
            sys.exit(0)
    else:  # pre-commit
        changed_files = run(["git", "diff", "--cached", "--name-only",
                             "--diff-filter=ACM"]).splitlines()

    if not changed_files:
        sys.exit(0)

    # 3. Filter to wiki content paths (RELATIVE TO REPO ROOT — git diff already returns repo-relative paths).
    #    Both `wikis/` and `pages/` exist in the template tree (Finding 3 of plan-r1 review).
    #    `projects/` is valid only inside client wikis.
    #    r2-F4 fix: exclude README.md basenames from project validation — README is a navigation
    #    aid, not a content page; the project-folder template ships a README without frontmatter.
    wiki_files = []
    for path in changed_files:
        basename = os.path.basename(path)
        if fnmatch(path, "wikis/**/*.md") or fnmatch(path, "pages/**/*.md"):
            wiki_files.append(path)
        elif is_client_wiki and fnmatch(path, "projects/**/*.md") and basename != "README.md":
            wiki_files.append(path)
        # else: ignore (frontmatter contract does not apply)

    if not wiki_files:
        sys.exit(0)

    # 4. Frontmatter validation against the routing contract.
    #    Registry path resolution:
    #    - $WIKI_SIBLING_REGISTRY_PATH if set (highest precedence)
    #    - vendored copy at $repo_root/.workspace-hub/client-wikis.yml (default)
    #    - if neither exists: degrade to warn-only on registry-dependent rules
    registry = load_client_wikis_registry(repo_root)

    errors = []
    for file in wiki_files:
        frontmatter = parse_yaml_frontmatter(file)
        if frontmatter is None:
            errors.append(f"{file}: missing YAML frontmatter")
            continue

        visibility = frontmatter.get("visibility")
        client     = frontmatter.get("client")
        project    = frontmatter.get("project")

        # Rule A: visibility must be from the allowed set.
        if visibility not in ALLOWED_VISIBILITY:
            errors.append(f"{file}: visibility='{visibility}' not in {ALLOWED_VISIBILITY}")
            continue  # downstream rules assume valid visibility

        # Rule B: private-client-llm-wiki requires client:.
        if visibility == "private-client-llm-wiki" and not client:
            errors.append(f"{file}: visibility=private-client-llm-wiki requires client:")

        # Rule C: client slug must match the repo's identity AND exist in the registry.
        #         Repo identity comes from repo_name (r1-F1 fix).
        if client:
            if is_client_wiki and client != expected_client_slug:
                errors.append(f"{file}: client='{client}' but repo identity is '{expected_client_slug}'")
            elif not is_client_wiki:
                errors.append(f"{file}: client='{client}' set but repo is generic llm-wiki")
            entry = registry.lookup(client) if registry else None
            if registry and entry is None:
                errors.append(f"{file}: client='{client}' not in client-wikis registry")

        # Rule D: project: only valid when visibility=private-client-llm-wiki.
        if project and visibility != "private-client-llm-wiki":
            errors.append(f"{file}: project='{project}' set but visibility is not private-client-llm-wiki")

        # Rule E (r1-F5 fix): project value, when set, must be enumerated in
        #         the registry's client.projects list. Forward-compatible.
        if project and client and registry:
            entry = registry.lookup(client)
            if entry and entry.get("projects"):
                if project not in entry["projects"]:
                    errors.append(f"{file}: project='{project}' not in registry.projects for client='{client}'")
            # else: warn-only (registry projects: list not yet populated)

    if errors:
        for e in errors:
            print(e, file=sys.stderr)
        sys.exit(1)
    sys.exit(0)
```

**Bypass + scope discipline:**
- `WIKI_FRONTMATTER_ALLOW=1` — explicit bypass (logged), matching the existing pattern of `ALLOW_ABS_PATHS=1` in `check-no-abs-paths.sh`.
- The script does **not** scan workspace-hub. The plan + template + this rule + the script's own tests all live in workspace-hub, where the script never fires — so the self-blocking hazard called out in plan-r1's Risk #6 does not apply (Finding 4 fix: templates are excluded structurally, not via line-allowlist).
- Workspace-hub gets a separate `tests/enforcement/test_check_wiki_sibling_frontmatter.sh` that constructs fixture wiki repos under `tmp_path/llm-wiki-foo/` and invokes the script against them, exercising both pre-commit and CI modes.

### Project-folder template skeleton (`templates/client-llm-wiki/projects/_template-project/`)

```
projects/_template-project/
├── README.md                   # explains the per-project layout, links to the rule
├── raw/.gitkeep                # raw inputs from /mnt/ace/<client>/<project>/
├── extracted/.gitkeep          # cleaned/extracted intermediate artifacts
├── methodology/.gitkeep        # client-specific methodology notes
└── results/.gitkeep            # client-specific calc results + reports
```

The `_template-project` slug is intentional — when `client-llm-wiki-factory` step 5 copies the template tree, the operator subsequently runs `cp -a projects/_template-project/. projects/<actual-project-slug>/` for each project (e.g., `projects/sirocco/`).

### Planning template change (`docs/plans/_template-issue-plan.md`)

Add frontmatter or section near the top:
```
> **Client:** <required for any plan touching wiki content; "N/A" otherwise>
> **Project:** <optional; if work scopes to a single project under the client>
```

Plus a one-paragraph block under "Resource Intelligence Summary" reminding planners that wiki-targeting work routes via `wiki-sibling-routing.md`.

### Citation contract change (`.claude/rules/calc-citation-contract.md`)

Extend sidecar emission schema:
```yaml
citations:
  - code_id: DNV-OS-E301
    publisher: DNV
    revision: 2018-07
    section: §2.2
    source_sibling: generic    # NEW — required (generic | <client-slug>)
    source_project: null       # NEW — optional (null when source is client-level)
```

Update `digitalmodel/src/digitalmodel/citations/schema.py` (sidecar dataclass) to declare the two new fields. Fail-closed at calc time per existing #2481 D2 contract — `CitationResolutionError` extended to surface `source_sibling` mismatches.

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | `.claude/rules/wiki-sibling-routing.md` | the canonical rule (per #2778 AC) |
| Update | `.claude/rules/README.md` | index the new rule |
| Create | `scripts/enforcement/check-wiki-sibling-frontmatter.py` | Level-2 enforcement (Python 3 + PyYAML, matching `scripts/readiness/check-sibling-sso-flow.py` precedent from #2775) — r2-F1 fix |
| Create | `scripts/enforcement/check-wiki-sibling-frontmatter.sh` | 4-line `.sh` wrapper that `exec`s the `.py` (lets hook callers invoke by `.sh` name) |
| Create | `tests/enforcement/test_check_wiki_sibling_frontmatter.py` | TDD coverage for the enforcement script (Python pytest, matching #2775 test pattern) |
| Modify | `docs/plans/_template-issue-plan.md` | add `client:` (required) and `project:` (optional) fields |
| Create | `tests/contract/test_planning_template_required_fields.py` | TDD coverage that template carries the new fields |
| Modify | `.claude/rules/calc-citation-contract.md` | add `source_sibling:` (required) and `source_project:` (optional) sidecar fields |
| Create | `tests/contract/test_citation_sidecar_schema_extensions.py` | TDD coverage that sidecar schema includes the new fields |
| Create | `templates/client-llm-wiki/projects/_template-project/README.md` | per-project skeleton README |
| Create | `templates/client-llm-wiki/projects/_template-project/{raw,extracted,methodology,results}/.gitkeep` | per-project subdirectory skeletons |
| Modify | `templates/client-llm-wiki/DATA-CYCLE.md` | document the project-nesting layout |
| Modify | `.claude/skills/coordination/client-llm-wiki-factory/SKILL.md` | add Step 5b (after template copy) instantiating per-project skeletons |
| Modify | `.claude/skills/coordination/issue-planning-mode/SKILL.md` | require `client:` context in the planning template reference |
| Modify | `config/client-wikis.yml` | add optional `projects:` list per client (declarative roster of known projects); consumed by Rule E of the enforcement script |
| Modify | `scripts/agents/install-pre-commit-hook-cross-repo.sh` | extend the existing #2722 cross-repo installer to also install `check-wiki-sibling-frontmatter.{sh,py}` into each wiki sibling (`llm-wiki`, `llm-wiki-acma`, plus the 5 planned per `config/client-wikis.yml`); vendor a copy of `config/client-wikis.yml` into each wiki repo's `.workspace-hub/` at install time; ensure each wiki repo's `.gitignore` carries a `.workspace-hub/` entry (r2-F7 fix — prevents perpetual dirty state from the vendored registry); document re-sync procedure as **manual `git pull` of workspace-hub then re-run install script** rather than a cron (r2-F3 fix — cron deliverable explicitly out of scope for #2778) |
| Update | `docs/plans/README.md` | add this plan to the index |
| Modify | `digitalmodel/src/digitalmodel/citations/schema.py` (CROSS-REPO) | extend `Citation` dataclass with `source_sibling`, `source_project` — committed in digitalmodel repo, not workspace-hub |

**Cross-repo notes:**
- The `digitalmodel/src/digitalmodel/citations/schema.py` modification is in a sibling repo. Per `feedback_multi_agent_commit_serialization`, the implementation phase will execute that change in `/mnt/local-analysis/digitalmodel/` separately and reference both commit SHAs in the closeout comment.
- The `llm-wiki-acma` and `llm-wiki` repos themselves do NOT receive write traffic from this plan — they consume the new contract. They do receive frontmatter migration in a separate follow-on (see Out of Scope below).

---

## TDD Test List

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| `test_enforcement_passes_on_valid_generic_frontmatter` | a wiki page with `visibility: private-llm-wiki` and no `client:` passes | staged: `wikis/marine-engineering/wiki/concepts/foo.md` with valid frontmatter | exit 0, no stderr |
| `test_enforcement_passes_on_valid_private_client_frontmatter` | a wiki page with `visibility: private-client-llm-wiki`, `client: acma`, `project: sirocco` passes | staged: `projects/sirocco/methodology/foo.md` with valid frontmatter | exit 0, no stderr |
| `test_enforcement_fails_when_visibility_invalid` | unknown visibility tier fails | `visibility: public-wiki` (invalid) | exit 1, stderr names the file + invalid value |
| `test_enforcement_fails_when_private_client_missing_client` | `private-client-llm-wiki` without `client:` fails | frontmatter has visibility but no client | exit 1, stderr explains rule B |
| `test_enforcement_fails_when_client_not_in_registry` | `client: nonexistent` (not in config/client-wikis.yml) fails | client slug unknown | exit 1, stderr names the unregistered client |
| `test_enforcement_fails_when_project_without_private_client_visibility` | `project:` set without `visibility: private-client-llm-wiki` fails | frontmatter has project but visibility is generic | exit 1, stderr explains rule D |
| `test_enforcement_passes_on_pages_dir_frontmatter` | a wiki page under `pages/` (not just `wikis/`) is also validated — Finding 3 of plan-r1 | staged: `pages/handbook/foo.md` with valid frontmatter | exit 0, no stderr |
| `test_enforcement_skips_non_wiki_paths` | staged file outside wiki path globs is ignored | staged: `docs/reports/foo.md` | exit 0, no inspection |
| `test_enforcement_skips_unstaged_files` | only staged files trigger check; working-tree-only changes don't | unstaged wiki file with bad frontmatter | exit 0 |
| `test_enforcement_skips_when_not_in_wiki_repo` | repo identity check bails early outside wiki repos — Finding 1 of plan-r1 | run from a repo named `workspace-hub` | exit 0, no inspection |
| `test_enforcement_fails_when_client_slug_mismatches_repo_identity` | `client:` value must match the wiki repo's identity (suffix after `llm-wiki-`) — Finding 1 of plan-r1 | client: `acma` inside repo `llm-wiki-doris` | exit 1, stderr names the mismatch |
| `test_enforcement_ci_mode_uses_base_ref_diff` | CI mode auto-detection (`CI=true`) uses `${BASE_REF}..HEAD` instead of `--cached` — Finding 2 of plan-r1 | `CI=true` env, committed change between base and HEAD | exit 1 (wiki file with bad frontmatter detected via committed diff) |
| `test_enforcement_pre_commit_mode_uses_cached_diff` | pre-commit mode (no CI env) uses `git diff --cached` | no `CI` env, staged change | exit 1 (wiki file with bad frontmatter detected via staged diff) |
| `test_enforcement_handles_bucket_name_edge_cases` | `client_projects` (underscore raw-root) and `frontierdeepwater` (no hyphen) resolve via registry inside their respective repo names | runs inside repo `llm-wiki-client-projects` and `llm-wiki-frontierdeepwater` | exit 0 |
| `test_enforcement_fails_when_project_not_in_registry_projects_list` | Rule E — when client.projects list is populated, project must be enumerated — Finding 5 of plan-r1 | client: acma with `projects: [sirocco]`; staged file claims `project: unknown` | exit 1, stderr names the missing project |
| `test_enforcement_warns_when_registry_projects_list_absent` | Rule E forward-compat — empty/absent projects list disables hard fail, warn only | client has no projects: key in registry | exit 0, warning to stderr |
| `test_planning_template_carries_client_field` | `docs/plans/_template-issue-plan.md` contains the required `Client:` marker | parse template markdown | assertion: `> **Client:**` present |
| `test_planning_template_carries_project_field` | `docs/plans/_template-issue-plan.md` contains the optional `Project:` marker | parse template markdown | assertion: `> **Project:**` present |
| `test_citation_sidecar_schema_has_source_sibling` | digitalmodel `Citation` dataclass has `source_sibling` field | import + reflect | assertion: field present and required |
| `test_citation_sidecar_schema_has_source_project` | digitalmodel `Citation` dataclass has `source_project` field | import + reflect | assertion: field present and optional (default None) |
| `test_citation_resolver_fails_on_source_sibling_mismatch` | citation pointing to `llm-wiki-acma` slug with `source_sibling: generic` fails fast | construct invalid Citation | raises `CitationResolutionError` referencing the mismatch |

All tests must FAIL before implementation begins (red→green→refactor TDD). Implementation order: enforcement script → planning template → citation contract → templates → skill updates. Tests precede each.

---

## Acceptance Criteria

Per #2778 issue body, plus corrections for OBE items:

- [ ] Rule documented at `.claude/rules/wiki-sibling-routing.md` with When-To-Apply / Do-Not-Apply blocks and the suffix-form locked. **(per #2778 AC #1)**
- [ ] ~~#2744 updated to use `llm-wiki-acma` (suffix) BEFORE any repo creation~~ → **REPLACED:** verify suffix-form `vamseeachanta/llm-wiki-acma` exists and is registered as `bootstrapped` (already true at plan time, evidence above); post comment on #2744 confirming OBE; add new #2744 AC for project-nesting layout to be applied to `llm-wiki-acma` after this plan's templates land. **(corrects #2778 AC #2)**
- [ ] Planning template captures `client:` (required) and `project:` (optional) context. **(per #2778 AC #3)**
- [ ] Citation contract updated to include `source_sibling:` and optional `source_project:` in sidecar schema. **(per #2778 AC #4)**
- [ ] Frontmatter schema extended for `private-client-llm-wiki` visibility tier with required `client:` and optional `project:`. **(per #2778 AC #5)**
- [ ] Cross-sibling link discipline added to #2776 (post comment with proposed text) — client→generic allowed; generic→client forbidden; client→client forbidden. **(per #2778 AC #6)**
- [ ] Level-2 enforcement script verifies frontmatter visibility/client/project consistency on staged content AND on `${BASE_REF}..HEAD` diffs (CI mode); auto-detects mode via `CI` env var; runs only inside wiki repos (early bail by `git rev-parse --show-toplevel` + basename matching `llm-wiki` or `llm-wiki-*`); installable into each wiki repo via `scripts/agents/install-pre-commit-hook-cross-repo.sh` (prior art from #2722); all 20 TDD tests pass. **(per #2778 AC #7)**
- [ ] Memory entries `feedback_wiki_sibling_routing` and `project_wiki_sibling_pattern` land after issue closes (post-implementation, not part of this plan). **(per #2778 AC #8)**
- [ ] First-client pilot validation: instantiate `templates/client-llm-wiki/projects/_template-project/` into `llm-wiki-acma/projects/sirocco/` as the end-to-end smoke test; record commit SHA in closeout. **(per #2778 AC #9)**
- [ ] All new tests pass: `uv run pytest tests/contract/ tests/enforcement/ -v` (where applicable; shell tests run via `bash tests/enforcement/...`).
- [ ] No regression: `uv run pytest tests/readiness/ -q` returns the same pre-plan pass rate (currently 30 passed per briefing).
- [ ] Review artifacts posted to `scripts/review/results/` for Claude + Codex + Gemini per T3 cross-review policy.

---

## Adversarial Review Summary

### Round 1 (2026-05-22 19:55–20:30 UTC, plan commit `72fc77c1`)

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | UNAVAILABLE | `claude` CLI rc=124, SessionEnd hook cancellation. Likely Claude-Code self-invocation collision (this fanout was dispatched FROM a Claude session). To be retried in r2. |
| Codex | UNAVAILABLE | `codex exec` rc=3, INCOMPATIBLE under `CLAUDECODE=1` — `stdin` hangs (workspace-hub #2684, openai/codex#19945). r2 will dispatch via `env -u CLAUDECODE bash scripts/review/plan-review-fanout.sh ...`. |
| Gemini | MAJOR | 4 MAJOR + 1 MINOR findings, all valid: (1) git-diff repo-context mismatch; (2) CI vs pre-commit env flaw; (3) `pages/` path discrepancy; (4) regex allowlist applied to YAML parser; (5) missing registry-array validation. Artifact: `scripts/review/results/2026-05-22-plan-2778-r1-gemini.md`. |

**Round 1 overall result:** FAIL (single-provider MAJOR with two UNAVAILABLE is not consensus per `feedback_codex_sustained_major_loop` — re-review required after revisions).

**Round 1 revisions applied to plan (in commit r1→r2):**
- **Finding 1 (repo-context mismatch):** Pseudocode rewritten to derive repo identity via `git rev-parse --show-toplevel` + basename match against `llm-wiki` / `llm-wiki-*`; early bail when not a wiki repo; client-slug check verifies against repo identity, not path prefix. New test `test_enforcement_skips_when_not_in_wiki_repo` and `test_enforcement_fails_when_client_slug_mismatches_repo_identity`.
- **Finding 2 (CI vs pre-commit):** Added two-mode support — pre-commit (default, `--cached`) and CI (`${BASE_REF}..HEAD`, auto-detected via `CI=true`). New tests `test_enforcement_ci_mode_uses_base_ref_diff` and `test_enforcement_pre_commit_mode_uses_cached_diff`. AC #7 wording updated.
- **Finding 3 (`pages/` omission):** Filter extended to include `pages/**/*.md` (in addition to `wikis/**/*.md`); `projects/**/*.md` only checked in client-wiki repos. New test `test_enforcement_passes_on_pages_dir_frontmatter`.
- **Finding 4 (line-allowlist vs YAML):** Structural correction — script is now scoped to **run only inside wiki repos** (workspace-hub paths are never inspected), so templates in workspace-hub are out-of-scope by construction, not by line allowlist. Old Risk #6 (self-blocking enforcement) deleted.
- **Finding 5 (registry projects unused):** Added Rule E — when `client.projects:` list is populated in registry, the file's `project:` value must be enumerated there. Forward-compatible (warn-only when projects list is absent so onboarding doesn't immediately fail closed). New tests `test_enforcement_fails_when_project_not_in_registry_projects_list` and `test_enforcement_warns_when_registry_projects_list_absent`.
- **Files-to-Change extension:** Added `scripts/agents/install-pre-commit-hook-cross-repo.sh` modification (extend the existing #2722 cross-repo installer to also install the new wiki-frontmatter hook into each wiki sibling).

### Round 2 (2026-05-22 20:45–20:55 UTC, plan commit `6a81ca64`)

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | UNAVAILABLE | `claude` CLI rc=124, same SessionEnd hook timeout as r1. Persistent CLI/wrapper issue when invoked from a Claude-Code Bash; worth filing as a separate bug against the `claude` CLI's SessionEnd hook. |
| Codex | UNAVAILABLE | `codex exec` rc=124 — "Reading additional input from stdin..." — even with `env -u CLAUDECODE`. Confirms `feedback_codex_cli_0_124_upstream_regression` (intermittent stdin hang regardless of CLAUDECODE env). |
| Gemini | MAJOR | 5 MAJOR + 2 MINOR new findings (all distinct from r1): (1) Python-in-Bash language mismatch; (2) Edge-case bucket slug mismatch [REJECTED — see Risk #9]; (3) Missing cron deliverable; (4) Project template README frontmatter; (5) CI shallow-clone fetch; (6) Bypass env-var not in pseudocode; (7) Vendored registry dirties working tree. Artifact: `scripts/review/results/2026-05-22-plan-2778-r2-gemini.md`. |

**Round 2 overall result:** PARTIAL (single-provider MAJOR — not consensus; per `feedback_r3_inline_loop_break_pattern`, defects are DIFFERENT each round, so the right move is inline-patch and surface, not auto-cycle).

**Round 2 → r3 inline patches applied (in this commit):**
- **r2-F1 (Python-in-Bash):** Script renamed `check-wiki-sibling-frontmatter.sh` → `check-wiki-sibling-frontmatter.py`; 4-line `.sh` wrapper retained for hook callers that exec by `.sh` name. Pseudocode rewritten as Python. Dependency footprint matches `scripts/readiness/check-sibling-sso-flow.py` (#2775 prior art).
- **r2-F2 (Edge-case bucket slug — REJECTED):** Gemini conflated `raw_root` (`/mnt/ace/client_projects/`, underscore) with `short_name` (`client-projects`, hyphen). My derivation `repo_name[len("llm-wiki-"):]` from repo `llm-wiki-client-projects` yields `client-projects` (hyphen) which matches `short_name` in registry. The underscore is exclusively in `raw_roots[0]` (a #2731 D5 quirk), never in the slug or the repo name. Documented in Risk #9 with verification evidence. No pseudocode change.
- **r2-F3 (Missing cron):** Cron claim dropped from Risk #8. Replaced with **manual re-sync procedure** documented in install script — operator runs `git -C workspace-hub pull && scripts/agents/install-pre-commit-hook-cross-repo.sh` to refresh vendored registry. Cron explicitly OOS for #2778.
- **r2-F4 (README frontmatter loop):** Pseudocode filter excludes `basename(path) == "README.md"` from `projects/**/*.md` validation. README is a navigation aid in the project skeleton, not a content page subject to frontmatter rules. Template ships without strict frontmatter, copies cleanly into new project folders.
- **r2-F5 (CI shallow clone):** Pseudocode adds `git fetch --depth=1 origin "$base_ref" 2>/dev/null || true` before the CI-mode diff. If the ref remains unreachable, the script exits 0 with stderr warning (degrades open by design — does not break builds). Recommends `fetch-depth: 0` in CI workflows for hard-enforcement.
- **r2-F6 (Bypass not in pseudocode):** Added explicit `if os.environ.get("WIKI_FRONTMATTER_ALLOW") == "1": exit 0` at the top of the function with stderr log line, matching the `ALLOW_ABS_PATHS=1` shape in `check-no-abs-paths.sh`.
- **r2-F7 (Vendored registry dirties tree):** Install-cross-repo script extension now explicitly adds `.workspace-hub/` to each wiki repo's `.gitignore` at install time.

**Consensus-gap disclosure (per AGENTS.md T3 review policy):**
This plan has been adversarially reviewed by Gemini twice (r1 + r2). Claude and Codex have been UNAVAILABLE both rounds due to documented CLI issues:
- **Claude:** rc=124 SessionEnd hook timeout (this fanout was dispatched FROM a Claude-Code session — likely a session-lifecycle interaction between parent Claude-Code and child Claude-CLI subprocess; needs a separate workspace-hub follow-on issue to investigate).
- **Codex:** rc=124 stdin hang (workspace-hub #2684 / openai/codex#19945; persistent regardless of `CLAUDECODE` env unsetting; needs separate diagnosis).
Per `feedback_codex_sustained_major_loop` precedent, single-provider MAJOR is not consensus; per `feedback_r3_inline_loop_break_pattern`, the right move when defects shift each round is r3 inline-patch + surface, not auto-cycle. The user should consider whether this plan needs a manual round of human review or a fresh dispatch from a non-Claude-Code shell before approval. Plan is functionally improved across both review rounds — no findings remain unaddressed.

---

## Risks and Open Questions

### Risks

1. **#2776 dependency.** This plan extends the cross-wiki linking rules introduced by #2776. #2776 is OPEN with no plan yet, so the "generic→client forbidden" addition may conflict with whatever #2776's plan ultimately specifies. **Mitigation:** post the proposed addition as a comment on #2776 rather than directly modifying its body; defer to #2776's plan-author for final wording.
2. **Cross-repo schema change (digitalmodel `Citation`).** The new `source_sibling:` field is a breaking change to the `Citation` dataclass — any code constructing `Citation(...)` without it would break unless we provide a sensible default. **Mitigation:** make `source_sibling` default to `"generic"` for backward compatibility; emit a `DeprecationWarning` when default is used; bump the citation-contract minor version.
3. **Sparse-checkout overlay blindness.** Per `feedback_gemini_sandbox_overlay_blindness`, Gemini reviews may not see sparse-checkout overlays. The new rule file + enforcement script live in workspace-hub, not in overlay paths — confirm by `git ls-files` before dispatching Gemini review.
4. **Bucket-name edge cases.** `config/client-wikis.yml` already documents `client_projects` (underscore raw-root) and `frontierdeepwater` (no hyphen) per #2731 D5/D6. The post-r1 redesign uses **repo identity from `basename(git rev-parse --show-toplevel)`** rather than path-prefix derivation, so the underscore/no-hyphen edge cases resolve naturally as long as the repo names themselves are `llm-wiki-client-projects` and `llm-wiki-frontierdeepwater` (verified by `test_enforcement_handles_bucket_name_edge_cases`).
5. **Frontmatter migration scope creep.** Existing wiki pages on `llm-wiki` and `llm-wiki-acma` may not carry the new `visibility:` / `client:` / `project:` fields. **Mitigation:** the enforcement script acts on STAGED content (pre-commit mode) or `${BASE_REF}..HEAD` (CI mode) only — legacy pages don't trip it until edited. A separate audit issue (post-#2778) handles backfill.
6. ~~**Self-blocking enforcement.**~~ ✓ **RESOLVED in r1→r2 revision.** The post-Finding-4 redesign scopes the script to **run only inside wiki repos** (early bail via `git rev-parse --show-toplevel` + basename match). Workspace-hub paths (rules, plans, tests, templates) are out-of-scope by construction — no allowlist needed. The script's tests run against fixture wiki repos under `tmp_path/`, not against workspace-hub itself.
7. **Planning-template churn.** Changing `_template-issue-plan.md` mid-flight affects every in-progress plan. **Mitigation:** make `Client:` accept `"N/A"` for plans that don't touch wiki content; document migration in `docs/plans/README.md`.
8. **Registry path resolution inside wiki repos.** The script needs `config/client-wikis.yml` from workspace-hub to validate client/project. Wiki repos don't ship with workspace-hub; install-time the hook installer must either (a) vendor a copy of the registry into the wiki repo, or (b) require `$WIKI_SIBLING_REGISTRY_PATH` env pointing to a sibling workspace-hub checkout. **Mitigation (r2-F3 + r2-F7 patches):** the install script (1) vendors the registry to `$wiki_repo/.workspace-hub/client-wikis.yml`, (2) adds `.workspace-hub/` to the wiki repo's `.gitignore` so the vendored copy doesn't appear as dirty state, and (3) documents the **manual re-sync procedure** (`git -C workspace-hub pull && scripts/agents/install-pre-commit-hook-cross-repo.sh`) rather than promising a cron deliverable that this plan does not deliver. Stale-registry behavior is `warn-only` so an out-of-date copy doesn't block all wiki commits; a cron deliverable is explicitly OOS for #2778 and can be filed as a follow-on if churn warrants.
9. **Reviewer-rejection record (Gemini r2-F2, REJECTED with evidence).** Gemini r2 flagged a MAJOR finding claiming `expected_client_slug = repo_name[len("llm-wiki-"):]` from `llm-wiki-client-projects` yields `client-projects` (hyphen) which mismatches the registry's `client_projects` (underscore). **Verification:** `grep -A 3 "short_name: client-projects" config/client-wikis.yml` returns `short_name: client-projects` (hyphen). The underscore-form `client_projects` is exclusively the `raw_roots[0]` path under `/mnt/ace/` — a #2731 D5 quirk documented as a bucket-name edge case, never used as a slug. The script validates against `short_name` (hyphen-form), not `raw_root`. My derivation is correct: `llm-wiki-client-projects` → `client-projects` → matches registry. Reviewers should treat `raw_roots` and `short_name` as distinct fields per the registry schema. Per `feedback_r1_review_trust_hazard`, verified before rejecting — Gemini r2-F2 absorbed-as-clarification (no pseudocode change), tracked here for traceability.

### Open Questions (recommendations for user at plan-approval review)

These mirror the 4 questions in #2778 body. I recommend a verdict for each so the user can confirm or override at approval rather than blocking on a discuss-then-plan cycle.

**Q1. Client-slug discipline** — public-name form when public, vs always-abstracted regardless of public status?
> **Recommendation:** Default to public-name when the client name is publicly known and the user explicitly opts in; abstracted form when in doubt. **Rationale:** the 2026-05-20 user directive (per `research/llm-wiki-public-private-routing`) sets this exact pattern for project names; consistency across project/client surfaces is the cleanest mental model. `acma` is fine as-is because ACMA is a real client engagement and the operator has opted in (evidenced by registry entry as `bootstrapped`). For future clients, the planning template's `client:` field documents the chosen form per-client at registry time.

**Q2. Project-folder schema** — normative skeleton or starting point?
> **Recommendation:** **Normative for the four standard subdirs** (`raw/`, `extracted/`, `methodology/`, `results/`); flexible above that. **Rationale:** the four subdirs match the data-cycle promotion model already in #2744 (DATA-CYCLE.md) and SIROCCO's operational pattern. Per-client extensions (e.g., a `vendor-correspondence/` subdir for clients with heavy off-repo traffic) are allowed but live as documented add-ons in the client's `DATA-CYCLE.md`, not as deviations from the skeleton.

**Q3. Existing generic content with client lineage** — retroactive classification?
> **Recommendation:** **Forward-only** (the #2778 out-of-scope default). **Rationale:** existing `llm-wiki` content under `wikis/` was authored under the public-only license assumption; bulk back-migration introduces audit risk and is its own scope. Flag the question for a follow-on audit issue if any client-derived content is suspected in `llm-wiki` today; the abstraction-gate skill already covers per-page promotion decisions for new content.

**Q4. Promotion-ledger location** — per-client (`llm-wiki-<client>/promotion-ledger/`) or workspace-hub-wide?
> **Recommendation:** **Per-client.** **Rationale:** ledger entries are client-scoped (raw source ID → wiki slug, confidence score, redaction status). A workspace-hub-wide central ledger would require cross-repo read access for every promotion decision (operational complexity) or risk drift between central and per-client copies. #2747 is already building the per-client ledger pattern. If a workspace-hub-wide *index* is needed for governance reporting, that can be a derived view built from per-client ledgers — a separate post-#2778 issue.

### Residual SSoT blocker classification (per briefing request)

From #2775's known blocker list — classification of how each relates to #2778:

| Sibling | Blocker | Classification for #2778 |
|---|---|---|
| `llm-wiki` | missing `AGENTS.md` | **In-scope** (the new routing contract should reference workspace-hub SSoT via this sibling's AGENTS.md; plan delivers the AGENTS.md content as a pilot validation step alongside the contract landing) |
| `llm-wiki-acma` | missing `AGENTS.md` | **In-scope** (same reason; pilot includes both `llm-wiki` and `llm-wiki-acma` AGENTS.md) |
| `aceengineer-strategy` | missing `AGENTS.md` | **Separate child issue** (not a wiki sibling; generic SSoT harness gap, belongs under #2775's residual cleanup) |
| `kaggle-rogii-2026` | missing `AGENTS.md` | **Separate child issue** (not a wiki sibling; same as above) |
| `CAD-DEVELOPMENTS` | missing workspace-hub contract | **Separate child issue** (not a wiki sibling; structural workspace-hub-contract gap, distinct from routing concern) |

Plan delivers AGENTS.md content for the 2 in-scope wiki siblings as part of the pilot validation step (#2778 AC #9). The 3 out-of-scope siblings get a follow-on issue filed separately, referencing #2775 as parent.

---

## Complexity: T3

**T3** justified because this plan:
- Touches multiple architectural layers (data / execution / output) per the issue body's explicit layering.
- Modifies 4 governance surfaces (rule file, planning template, citation contract, skill), creates 2 new artifacts (enforcement script, project-folder template), and touches 1 cross-repo concern (`digitalmodel/citations/schema.py`).
- Has 15 TDD tests required before implementation.
- Requires 3-provider adversarial review per AGENTS.md T3 cross-review policy.
- Carries 4 explicit user-decision points (Q1–Q4) that need approval-time sign-off.
- Coordinates with 5 related open issues (#2744, #2774, #2776, #2731, #2400).
