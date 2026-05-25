# Wiki sibling routing — agent rule

**When to apply:** any agent action that reads, writes, or cites content across `llm-wiki` (generic sibling) or `llm-wiki-<client>` (per-client siblings). This includes ingest writers, frontmatter authors, citation emitters, page authoring, chatbot responses, report rendering, MCP `wiki_search` retrieval (per [#2400](https://github.com/vamseeachanta/workspace-hub/issues/2400)), and any dispatch that targets a wiki repo for read or write.

**Why:** prevents per-session routing improvisation, naming drift, cross-client leakage, generic-vs-client duplication, and ambiguous citation provenance. Routing convention locked by user 2026-05-22 (issue [#2778](https://github.com/vamseeachanta/workspace-hub/issues/2778)). The contract is enforced by the Level-2 script [`scripts/enforcement/check-wiki-sibling-frontmatter.py`](../../scripts/enforcement/check-wiki-sibling-frontmatter.py) running as a pre-commit / CI hook inside each wiki repo.

**How to apply:**

1. **Naming.** Generic sibling is `vamseeachanta/llm-wiki` (private since 2026-05-20 — see [[project_llm_wiki_privacy_flip]]). Client siblings use the **suffix form** `vamseeachanta/llm-wiki-<client>` — one sibling per client, not per project. Projects nest as folders under `projects/<project-slug>/` inside the client sibling. Registry: [`config/client-wikis.yml`](../../config/client-wikis.yml). Confirmed bootstrap: `llm-wiki-acma` (created 2026-05-18, PRIVATE).

2. **Data layer.** Writers (ingest pipelines, AI-assisted extraction, manual digitization) declare their target sibling via `LLM_WIKI_TARGET={generic,<client>}` env or config. Frontmatter must carry a `visibility:` field from the allowed set:

   | `visibility:` value | Where it applies | Required adjacent fields | Optional adjacent fields |
   |---|---|---|---|
   | `private-llm-wiki` | generic `llm-wiki` content | (none) | (none) |
   | `private-client-llm-wiki` | content inside `llm-wiki-<client>` | `client: <slug>` | `project: <slug>` |
   | `public-federal-data` | content in public `worldenergydata-wiki` (per [`codes-standards-data-routing.md`](codes-standards-data-routing.md) §6) | `license: public-domain`, `source_authority:` | `contribution_status:`, `last_license_check:` |

   The enforcement script rejects any other `visibility:` value at hook time.

3. **Execution layer.** Planning template ([`docs/plans/_template-issue-plan.md`](../../docs/plans/_template-issue-plan.md)) carries `Client:` (required for plans touching wiki content; `N/A` otherwise) and `Project:` (optional) header fields. Agent dispatch prompts (Claude `Agent`, Codex `codex exec`, Hermes routing) propagate `client` + `project` context to subagents so they don't re-improvise. Citation resolvers and skills that retrieve knowledge accept `client` + `project` parameters; default to `generic` only when explicitly unset.

4. **Output layer.** Citation sidecars (per [`calc-citation-contract.md`](calc-citation-contract.md)) include `source_sibling:` (required — `generic` or the client slug) and `source_project:` (optional — `null` when source is client-level, populated when source is project-level). Reports, dashboards, and chatbots render the source-sibling identity prominently (e.g., a `Sourced from llm-wiki-acma/projects/sirocco` badge) so client-specific findings are never confused with generic ones.

5. **Cross-sibling linking discipline.** Extends [#2776](https://github.com/vamseeachanta/workspace-hub/issues/2776) (cross-wiki linking discipline epic).
   - `client → generic`: **full URL allowed and encouraged** (reference-not-duplicate posture).
   - `generic → client`: **forbidden** (generic must not depend on per-client content; would 404 for public readers of any future re-publication).
   - `client → other-client`: **forbidden** (prevents cross-client leakage).
   - `generic → worldenergydata-wiki`: full URL allowed (both public/private boundaries permit it).
   - `client → worldenergydata-wiki`: full URL allowed.

6. **Sanitized ↔ unsanitized referencing.** Client wikis hold full-fidelity unsanitized content. Generic wiki holds sanitized derivatives safe for cross-client reuse. **Client → generic:** when a client project relies on a sanitized concept/standard/methodology (e.g., OCIMF MEG3/MEG4 Annex A), the client wiki **references** the generic wiki slug — does NOT re-derive locally. **Generic ← client:** only via the abstraction gate (Skill D: [`research/llm-wiki-public-private-routing`](../skills/research/llm-wiki-public-private-routing/SKILL.md)). Once promoted to generic, the client wiki references it instead of holding a local copy.

## Do not apply when

- The content is not destined for any wiki sibling (e.g., a scratch report under `docs/reports/` with no wiki copy planned).
- The content is a workspace-hub-internal artifact (rule, skill, doc, hook script). Workspace-hub paths are out of scope of the enforcement script by construction — the script bails early via `git rev-parse --show-toplevel` + basename match against `llm-wiki` / `llm-wiki-*`.
- The wiki target is `worldenergydata-wiki` (public-domain federal-data sibling). That surface is governed by [`codes-standards-data-routing.md`](codes-standards-data-routing.md) §6 with its own frontmatter schema (`visibility: public-federal-data`, `license: public-domain`, etc.).

## Frontmatter validation (Rule A–E)

The enforcement script validates against five rules. Each rule has a corresponding test in `tests/enforcement/test_check_wiki_sibling_frontmatter.py`.

- **Rule A.** `visibility:` must be one of `{private-llm-wiki, private-client-llm-wiki, public-federal-data}`.
- **Rule B.** `visibility: private-client-llm-wiki` requires `client:` (and optionally `project:`).
- **Rule C.** When `client:` is set, the slug must match the repo's identity (derived from `basename(git rev-parse --show-toplevel)` after stripping the `llm-wiki-` prefix) AND must exist in the `client-wikis.yml` registry.
- **Rule D.** When `project:` is set, `visibility:` must be `private-client-llm-wiki` (projects don't exist outside client wikis).
- **Rule E.** When `project:` is set AND the registry entry for the client has a populated `projects:` list, the project value must be enumerated there. If the projects list is absent or empty, warn-only (forward-compat for newly onboarded projects).

## Operational modes and bypass

- **Pre-commit mode** (default): `git diff --cached --name-only --diff-filter=ACM`.
- **CI mode** (auto-detected when `CI=true`): `git diff --name-only --diff-filter=ACM ${BASE_REF}..HEAD`, where `BASE_REF` defaults to `origin/main` and is overridable via `--base=<ref>` or `$WIKI_FRONTMATTER_BASE_REF`. The script attempts a `git fetch --depth=1 origin "$base_ref"` before diffing so it works under default shallow CI clones; if the ref remains unreachable, it exits 0 with a stderr warning (degrades open by design — does not break the build; configure `fetch-depth: 0` in CI for hard-enforcement).
- **Bypass:** `WIKI_FRONTMATTER_ALLOW=1` (logged to stderr; use sparingly). Same shape as `ALLOW_ABS_PATHS=1` in [`check-no-abs-paths.sh`](../../scripts/enforcement/check-no-abs-paths.sh).

## Registry path resolution

The enforcement script reads `client-wikis.yml` in this precedence order:
1. `$WIKI_SIBLING_REGISTRY_PATH` if set (highest precedence — useful for ad-hoc validation).
2. Vendored copy at `${repo_root}/.workspace-hub/client-wikis.yml` (default; installed by [`scripts/agents/install-pre-commit-hook-cross-repo.sh`](../../scripts/agents/install-pre-commit-hook-cross-repo.sh) at hook-install time; the install script also adds `.workspace-hub/` to the wiki repo's `.gitignore` so the vendored copy doesn't appear as dirty state).
3. If neither exists, registry-dependent rules (C/E) degrade to warn-only so an out-of-date or missing copy doesn't block all wiki commits.

Re-sync procedure (manual): `git -C workspace-hub pull && scripts/agents/install-pre-commit-hook-cross-repo.sh` from the install host. A cron-based re-sync is **not** in scope for the initial landing ([#2778](https://github.com/vamseeachanta/workspace-hub/issues/2778) Risk #8); it can be added as a follow-on if registry churn warrants.

## Pilot reference

- **Bootstrap pilot:** client `acma` (`status: bootstrapped` in `config/client-wikis.yml` since 2026-05-18; repo `vamseeachanta/llm-wiki-acma` PRIVATE).
- **First nested project:** `sirocco` under `acma`, lives at `llm-wiki-acma/projects/sirocco/` (live engagement tracked in [#2760](https://github.com/vamseeachanta/workspace-hub/issues/2760)).
- **First operational routing decision:** OCIMF MEG3/MEG4 methodology → generic `llm-wiki/wikis/naval-architecture/standards/ocimf-meg.md`; SIROCCO project-specific calc results → `llm-wiki-acma/projects/sirocco/results/`. Documented in [`docs/session-handoffs/2026-05-20-handoff-digitalmodel-616-ocimf-to-llm-wiki.md`](../../docs/session-handoffs/2026-05-20-handoff-digitalmodel-616-ocimf-to-llm-wiki.md).

## Related rules and skills

- [`codes-standards-data-routing.md`](codes-standards-data-routing.md) — vendor-licensed standards data routing (private llm-wiki) + public-domain federal-data routing (worldenergydata-wiki §6).
- [`calc-citation-contract.md`](calc-citation-contract.md) — sidecar emission schema (extended for `source_sibling:` + `source_project:` per this rule's Output Layer).
- [`research/llm-wiki-public-private-routing`](../skills/research/llm-wiki-public-private-routing/SKILL.md) (Skill D) — abstraction-gate decision tree for content promotion from client wikis to generic.
- [`coordination/client-llm-wiki-factory`](../skills/coordination/client-llm-wiki-factory/SKILL.md) — operator checklist for bootstrapping new `llm-wiki-<client>` repos; updated to instantiate `projects/_template-project/` skeleton at Step 5b.
- [`coordination/issue-planning-mode`](../skills/coordination/issue-planning-mode/SKILL.md) — references the `Client:`/`Project:` planning-template fields added per this rule.

## Related issues

- [#2778](https://github.com/vamseeachanta/workspace-hub/issues/2778) — this rule's source issue (architecture: lock data/knowledge/result search routing).
- [#2744](https://github.com/vamseeachanta/workspace-hub/issues/2744) — first client-sibling pilot (acma); receives a follow-on AC for project-nesting layout per this rule.
- [#2774](https://github.com/vamseeachanta/workspace-hub/issues/2774) — generic ingest umbrella; consumes this rule's data-layer convention.
- [#2776](https://github.com/vamseeachanta/workspace-hub/issues/2776) — cross-wiki linking discipline (this rule's §5 extends it).
- [#2775](https://github.com/vamseeachanta/workspace-hub/issues/2775) — workspace-hub SSoT harness flow (sibling SSoT scaffolding from this rule's enforcement-script installer extends).
- [#2731](https://github.com/vamseeachanta/workspace-hub/issues/2731) — canonical data/repo locations; `client_projects` (underscore raw-root) and `frontierdeepwater` (no hyphen) edge cases noted in §1.
- [#2400](https://github.com/vamseeachanta/workspace-hub/issues/2400) — MCP `wiki_search` dependency (will consume this routing contract once landed).
