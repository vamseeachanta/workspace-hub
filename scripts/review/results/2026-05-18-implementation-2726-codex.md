OpenAI Codex v0.130.0
--------
workdir: /mnt/local-analysis/workspace-hub
model: gpt-5.5
provider: openai
approval: never
sandbox: workspace-write [workdir, /tmp, /home/vamsee/.codex/memories]
reasoning effort: medium
reasoning summaries: none
session id: 019e3b10-3e71-7e63-a68e-b0205127d197
--------
user
# Implementation Adversarial Final Re-Review: workspace-hub #2726

Independent adversarial review. Do not rubber-stamp.

## Context
Issue #2726 is approved. This is the parent architecture/crosswalk TDD slice only: tests + fixture + parent contract + markdown matrix for data, execution, report, and curated output learning layers. Child-layer details remain in #2727/#2728/#2729; mount/source registry normalization remains in #2731/#2732.

## Verification
- `uv run pytest tests/architecture/test_layer_boundary_architecture_contract.py -q` => `5 passed`.
- `scripts/legal/legal-sanity-scan.sh --diff-only` => PASS.

## Prior findings addressed
- Private/client/staging fail-closed tests strengthened.
- Markdown row consistency is now row-keyed, not global string matching.
- `input_residency` added to required fixture columns and markdown matrix.
- Markdown matrix explicitly declares reduced rendering and fixture authority for enforcement fields.

## Review questions
1. Are there remaining blocking gaps in the parent layer architecture contract?
2. Do tests now sufficiently guard data/execution/report boundaries for this first slice?
3. Is scope appropriately bounded to #2726 and not absorbing child issue details?

Required output:
Verdict: APPROVE | MINOR | MAJOR
Findings:
- [severity: critical/high/medium/low] [path] finding + fix

## Diff under review
```diff
diff --git a/docs/architecture/data-execution-report-layer-contract.md b/docs/architecture/data-execution-report-layer-contract.md
new file mode 100644
index 000000000..755eab60f
--- /dev/null
+++ b/docs/architecture/data-execution-report-layer-contract.md
@@ -0,0 +1,57 @@
+# Data, Execution, Report, and Curated-Learning Layer Contract
+
+This contract defines the workspace-hub ecosystem lifecycle requested in [#2726](https://github.com/vamseeachanta/workspace-hub/issues/2726):
+
+```text
+inputs -> execution -> reports/chatbots -> curated output learnings -> corpus tier
+```
+
+It is a parent architecture contract. Child plans #2727, #2728, and #2729 may refine their own layer details only when they consume this cross-layer contract instead of redefining upstream/downstream interfaces.
+
+## Architecture-surface codes
+
+These architecture-surface codes are not replacements for document-intelligence L-levels. Existing document-intelligence L-levels remain governed by `docs/document-intelligence/README.md` and related maps.
+
+| Code | Boundary | Owns | Does not own |
+|---|---|---|---|
+| A-DATA | Source truth and residency | raw/public/private source IDs, curated reference data, provenance, source residence | execution routing, report publication, chatbot exposure |
+| A-EXEC | Execution manifests and compute evidence | `source_id` references, `input_residency`, tools, code execution, machines/compute, checksums, validation logs | raw source truth, public promotion decisions |
+| A-REPORT | Audience-facing and internal output surfaces | raw internal output, client HTML, limited PDFs, chatbot/index configs, evidence bundles, `output_residency` | automatic promotion into public/private llm-wiki |
+| A-CURATED-LEARNING | Reviewed learnings extracted from report/chatbot outputs | public llm-wiki pages, private/domain corpus entries, client-private corpus entries after promotion gate | raw report dumps, private data laundering |
+
+## Lifecycle rules
+
+1. Data starts in A-DATA with a source owner, source posture, and canonical `source_id` or redacted source ID.
+2. A-EXEC consumes data by reference through `source_id`, `input_residency`, and gate evidence. Execution must not duplicate raw data ownership.
+3. A-REPORT consumes execution evidence and data classification to produce raw internal outputs, client-facing HTML, limited PDFs, and chatbot surfaces.
+4. A-CURATED-LEARNING receives only reviewed report-derived learnings after a promotion gate. Report output is not automatically knowledge.
+5. Each transition must name a promotion gate when the destination is more public, more durable, or broader-audience than the source.
+
+## Required gates by transition
+
+| Transition | Required gate |
+|---|---|
+| A-DATA -> A-EXEC | source registry lookup, provenance, `source_id`, `input_residency`, license/legal constraints, validation readiness |
+| A-EXEC -> A-REPORT | tool/run evidence, checksums where applicable, `output_residency`, redaction, audience classification |
+| A-REPORT -> A-CURATED-LEARNING | promotion gate with provenance, license, legal, sanitization, citation/source separation, owner review |
+| Any private/restricted source -> public llm-wiki/public chatbot/public report | explicit legal and sanitization gate; fail closed by default |
+
+## Residency and publication rules
+
+- Raw/private/client data cannot route directly into public llm-wiki or public chatbot indexes.
+- Private or raw-like llm-wiki staging remains local/private until a registry identifies its owner and allowed destination.
+- Public llm-wiki content must be sanitized, source-cited, and public-safe.
+- Client-facing HTML and limited PDFs are A-REPORT outputs and require audience-specific evidence gates.
+- Chatbots inherit the most restrictive posture of their source corpus and report evidence.
+
+## Canonical source matrix
+
+The structured source matrix is `tests/fixtures/architecture/layer_boundary_matrix.yaml`. The reviewable markdown rendering is `docs/architecture/source-layer-classification-matrix.md`.
+
+## Sequencing boundaries
+
+- #2726 owns this parent cross-layer contract and classification crosswalk.
+- #2727 owns data-layer refinements and promotion rules after consuming this contract.
+- #2728 owns execution-layer manifests, tools, compute, and routing after consuming this contract.
+- #2729 owns report-layer outputs and evidence boundaries after consuming this contract.
+- #2731/#2732 own mount/source-registry normalization and must not be silently absorbed into this parent issue.
diff --git a/docs/architecture/source-layer-classification-matrix.md b/docs/architecture/source-layer-classification-matrix.md
new file mode 100644
index 000000000..4cef3907b
--- /dev/null
+++ b/docs/architecture/source-layer-classification-matrix.md
@@ -0,0 +1,25 @@
+# Source Layer Classification Matrix
+
+This matrix is a reduced rendering of the structured fixture at `tests/fixtures/architecture/layer_boundary_matrix.yaml` for review. The fixture is authoritative for tests and enforcement-only fields (`allowed_artifacts`, `forbidden_artifacts`, `retention_expectations`, and `publication_rules`); this markdown file is the human-readable crosswalk for #2726.
+
+| Source class | Owner | Canonical path / source ID | Layer | Level | Public posture | Promotion gate | Input residency | Output residency | Report/chatbot eligibility |
+|---|---|---|---|---|---|---|---|---|---|
+| workspace_control_plane_data | workspace-hub | /mnt/local-analysis/workspace-hub | A-DATA | D-CONTROL | public-controlled | repo review gate plus legal diff scan | /mnt/local-analysis/workspace-hub control-plane docs/config metadata only | workspace-hub docs or reports | internal and public control-plane summaries after review gate |
+| tier1_repo_ecosystem_data | documented tier-1 repos | documented repo registry entries; no inference from checkout name | A-DATA | D-REPO-CURATED | mixed | owner repo review gate and source/license check | owner repo checkout or registry-declared source path | owner repo or workspace-hub cross-reference | eligible only through cited owner-repo artifacts |
+| tier2_publication_strategy_repos | llm-wiki, aceengineer-website, aceengineer-strategy where registry evidence supports role | tracked repository map or unavailable until inventoried | A-CURATED-LEARNING | D-PUBLICATION | mixed | provenance, license, legal, sanitization, and owner review gate | publication repo selected by registry; no private/raw source ingress | publication repo selected by source class | public or strategic chatbot only after promotion gate |
+| public_collection_data | worldenergydata or upstream public API owner | api://worldenergydata or documented public-source cache | A-DATA | D-RAW-PUBLIC | public | provenance/license check and transform validation | api://worldenergydata or documented public-source cache | data repo cache or report evidence bundle | public report/chatbot eligible after provenance gate |
+| engineering_reference_data | digitalmodel or standards-derived reference owner | owner repo reference tables or citation sidecar paths | A-DATA | D-REFERENCE | restricted | standards citation contract, provenance, license, review gate | owner repo reference tables or citation sidecar paths | owner repo reference data or calculation report sidecar | eligible only with citations and license-safe summaries |
+| mounted_standards_literature | mounted source custodian | /mnt/ace/docs/_standards and other mounted-source registry IDs | A-DATA | D-MOUNTED-REFERENCE | restricted | source registry, license, legal, sanitization, citation review gate | mounted-source registry ID; reference-in-place only | mounted source reference plus repo-safe metadata | summaries only after explicit gate; no default public eligibility |
+| client_project_data | client/project repo or private mounted project archive | client_projects or redacted project source ID | A-DATA | D-CLIENT-PRIVATE | client-private | explicit client authorization, legal, sanitization, and provenance gate | client-private repo or redacted mounted project source ID | client-private repo, private corpus, or approved deliverable store | client report only after explicit gate; never public by default |
+| llm_wiki_raw_private_staging | private/local corpus owner pending registry | unavailable until private corpus registry exists; use redacted source IDs | A-DATA | D-PRIVATE-STAGING | local-private | private corpus registry, legal, sanitization, provenance, owner review gate | private/local staging source ID; no public repo path assumed | private/local staging or approved private corpus | private chatbot only after gate; no public eligibility by default |
+| llm_wiki_public_content | public llm-wiki repo | tracked public llm-wiki repository path after live inventory | A-CURATED-LEARNING | D-PUBLIC-KNOWLEDGE | public | public knowledge promotion gate and legal scan | tracked public llm-wiki repository path after promotion gate | public llm-wiki | public chatbot eligible after citation and freshness checks |
+| execution_artifacts | workspace-hub execution/control-plane | issue plans, manifests, prompt bundles, run logs, checksums | A-EXEC | E-MANIFEST-EVIDENCE | mixed | validation, secret scan, and output-residency review gate | source_id plus input_residency references from A-DATA rows; no raw data ownership | workspace-hub logs/reports or target repo evidence path | evidence summaries eligible after redaction; raw logs private by default |
+| report_artifacts | report-producing repo or client deliverable owner | docs/reports, client deliverable store, limited PDFs, chatbot/index configs | A-REPORT | R-OUTPUT | mixed | report evidence, provenance, legal, sanitization, and audience review gate | classified evidence bundles and source_id references from A-EXEC/A-DATA | internal report path, client deliverable store, or public-safe publication repo | depends on audience and output_residency gate |
+
+## Boundary notes
+
+- Data-layer source truth and residency remain separate from execution manifests and report publication surfaces.
+- Private/client/restricted sources fail closed for public llm-wiki, public chatbot, and public report destinations unless the matrix row names an explicit promotion gate.
+- `llm_wiki_raw_private_staging` intentionally has no assumed public-repo canonical path until a private corpus registry exists.
+- Execution artifacts reference data by `source_id`, `input_residency`, and `output_residency`; they do not own raw source truth.
+- Report artifacts are publication surfaces. Curated output learnings require a separate A-CURATED-LEARNING promotion gate.
diff --git a/tests/architecture/test_layer_boundary_architecture_contract.py b/tests/architecture/test_layer_boundary_architecture_contract.py
new file mode 100644
index 000000000..300739892
--- /dev/null
+++ b/tests/architecture/test_layer_boundary_architecture_contract.py
@@ -0,0 +1,145 @@
+from pathlib import Path
+
+import yaml
+
+ROOT = Path(__file__).resolve().parents[2]
+MATRIX_PATH = ROOT / "tests/fixtures/architecture/layer_boundary_matrix.yaml"
+CONTRACT_PATH = ROOT / "docs/architecture/data-execution-report-layer-contract.md"
+MARKDOWN_MATRIX_PATH = ROOT / "docs/architecture/source-layer-classification-matrix.md"
+
+REQUIRED_COLUMNS = {
+    "source_class",
+    "owner",
+    "canonical_path",
+    "layer",
+    "level",
+    "allowed_artifacts",
+    "forbidden_artifacts",
+    "retention_expectations",
+    "publication_rules",
+    "public_posture",
+    "promotion_gate",
+    "input_residency",
+    "output_residency",
+    "report_chatbot_eligibility",
+}
+
+SEED_SOURCE_CLASSES = {
+    "workspace_control_plane_data",
+    "tier1_repo_ecosystem_data",
+    "tier2_publication_strategy_repos",
+    "public_collection_data",
+    "engineering_reference_data",
+    "mounted_standards_literature",
+    "client_project_data",
+    "llm_wiki_raw_private_staging",
+    "llm_wiki_public_content",
+    "execution_artifacts",
+    "report_artifacts",
+}
+
+PRIVATE_POSTURES = {"private", "restricted", "client-private", "local-private"}
+PUBLIC_DESTINATIONS = {"public llm-wiki", "public chatbot", "public report", "client report"}
+PUBLIC_DEFAULT_FORBIDDEN_DESTINATIONS = {"public llm-wiki", "public chatbot", "public report"}
+RENDERED_MARKDOWN_COLUMNS = [
+    "source_class",
+    "owner",
+    "canonical_path",
+    "layer",
+    "level",
+    "public_posture",
+    "promotion_gate",
+    "input_residency",
+    "output_residency",
+    "report_chatbot_eligibility",
+]
+
+
+def load_matrix() -> list[dict]:
+    assert MATRIX_PATH.exists(), f"Missing layer boundary fixture: {MATRIX_PATH}"
+    data = yaml.safe_load(MATRIX_PATH.read_text(encoding="utf-8"))
+    assert isinstance(data, dict), "Matrix fixture must be a mapping with a sources list"
+    sources = data.get("sources")
+    assert isinstance(sources, list) and sources, "Matrix fixture must define non-empty sources"
+    return sources
+
+
+def test_source_matrix_has_required_columns():
+    for row in load_matrix():
+        missing = REQUIRED_COLUMNS - set(row)
+        assert not missing, f"{row.get('source_class', '<unknown>')} missing columns: {sorted(missing)}"
+
+
+def test_known_sources_are_classified():
+    actual = {row["source_class"] for row in load_matrix()}
+    assert SEED_SOURCE_CLASSES <= actual
+
+
+def test_private_sources_not_public_eligible_by_default():
+    for row in load_matrix():
+        posture = str(row["public_posture"]).lower()
+        eligibility = str(row["report_chatbot_eligibility"]).lower()
+        promotion_gate = str(row["promotion_gate"]).lower()
+        publication_rules = str(row["publication_rules"]).lower()
+        forbidden_artifacts = str(row["forbidden_artifacts"]).lower()
+        if posture in PRIVATE_POSTURES:
+            for destination in PUBLIC_DEFAULT_FORBIDDEN_DESTINATIONS:
+                assert destination not in eligibility, (
+                    f"{row['source_class']} must fail closed and avoid default {destination} eligibility"
+                )
+                assert destination in publication_rules or destination in forbidden_artifacts or "public" in publication_rules, (
+                    f"{row['source_class']} must explicitly govern public publication in rules/artifacts"
+                )
+            for destination in PUBLIC_DESTINATIONS:
+                assert not (
+                    destination in eligibility and "gate" not in promotion_gate
+                ), f"{row['source_class']} exposes {destination} without an explicit gate"
+
+
+def test_layer_transitions_are_explicit():
+    assert CONTRACT_PATH.exists(), f"Missing architecture contract: {CONTRACT_PATH}"
+    text = CONTRACT_PATH.read_text(encoding="utf-8")
+    required_phrases = [
+        "inputs -> execution -> reports/chatbots -> curated output learnings -> corpus tier",
+        "A-DATA",
+        "A-EXEC",
+        "A-REPORT",
+        "A-CURATED-LEARNING",
+        "document-intelligence L-levels",
+        "source_id",
+        "input_residency",
+        "output_residency",
+        "promotion gate",
+        "legal",
+        "sanitization",
+    ]
+    for phrase in required_phrases:
+        assert phrase in text, f"Contract missing required phrase: {phrase}"
+
+
+def parse_markdown_matrix_rows(text: str) -> dict[str, list[str]]:
+    rows: dict[str, list[str]] = {}
+    for line in text.splitlines():
+        if not line.startswith("| ") or line.startswith("|---") or "Source class" in line:
+            continue
+        cells = [cell.strip().replace("\\|", "|") for cell in line.strip("|").split("|")]
+        if cells:
+            rows[cells[0]] = cells
+    return rows
+
+
+def test_markdown_matrix_is_generated_from_fixture_classes():
+    assert MARKDOWN_MATRIX_PATH.exists(), f"Missing markdown matrix: {MARKDOWN_MATRIX_PATH}"
+    text = MARKDOWN_MATRIX_PATH.read_text(encoding="utf-8")
+    assert "reduced rendering" in text
+    markdown_rows = parse_markdown_matrix_rows(text)
+    for row in load_matrix():
+        source_class = row["source_class"]
+        assert source_class in markdown_rows, f"Markdown matrix missing row for {source_class}"
+        rendered = markdown_rows[source_class]
+        assert len(rendered) == len(RENDERED_MARKDOWN_COLUMNS), (
+            f"Markdown row for {source_class} has {len(rendered)} columns; "
+            f"expected {len(RENDERED_MARKDOWN_COLUMNS)}"
+        )
+        expected = [str(row[column]) for column in RENDERED_MARKDOWN_COLUMNS]
+        assert rendered == expected, f"Markdown row drift for {source_class}"
diff --git a/tests/fixtures/architecture/layer_boundary_matrix.yaml b/tests/fixtures/architecture/layer_boundary_matrix.yaml
new file mode 100644
index 000000000..a9fa75686
--- /dev/null
+++ b/tests/fixtures/architecture/layer_boundary_matrix.yaml
@@ -0,0 +1,155 @@
+sources:
+  - source_class: workspace_control_plane_data
+    owner: workspace-hub
+    canonical_path: /mnt/local-analysis/workspace-hub
+    input_residency: /mnt/local-analysis/workspace-hub control-plane docs/config metadata only
+    layer: A-DATA
+    level: D-CONTROL
+    allowed_artifacts: repo docs, plans, governance evidence, configuration metadata
+    forbidden_artifacts: client raw data, mounted standards copies, secrets
+    retention_expectations: git-tracked control-plane records only
+    publication_rules: public only when docs are already repo-public and legal scan passes
+    public_posture: public-controlled
+    promotion_gate: repo review gate plus legal diff scan
+    output_residency: workspace-hub docs or reports
+    report_chatbot_eligibility: internal and public control-plane summaries after review gate
+  - source_class: tier1_repo_ecosystem_data
+    owner: documented tier-1 repos
+    canonical_path: documented repo registry entries; no inference from checkout name
+    input_residency: owner repo checkout or registry-declared source path
+    layer: A-DATA
+    level: D-REPO-CURATED
+    allowed_artifacts: source code, tests, reference configs, curated repo docs
+    forbidden_artifacts: private client payloads, raw mounted data dumps
+    retention_expectations: git-tracked per owner repo policy
+    publication_rules: inherit owner repo visibility and citation/provenance rules
+    public_posture: mixed
+    promotion_gate: owner repo review gate and source/license check
+    output_residency: owner repo or workspace-hub cross-reference
+    report_chatbot_eligibility: eligible only through cited owner-repo artifacts
+  - source_class: tier2_publication_strategy_repos
+    owner: llm-wiki, aceengineer-website, aceengineer-strategy where registry evidence supports role
+    canonical_path: tracked repository map or unavailable until inventoried
+    input_residency: publication repo selected by registry; no private/raw source ingress
+    layer: A-CURATED-LEARNING
+    level: D-PUBLICATION
+    allowed_artifacts: sanitized pages, GTM strategy records, public website content
+    forbidden_artifacts: raw client data, private source excerpts, unredacted mounted-source names
+    retention_expectations: git-tracked curated publication records
+    publication_rules: only sanitized derivatives after promotion gate
+    public_posture: mixed
+    promotion_gate: provenance, license, legal, sanitization, and owner review gate
+    output_residency: publication repo selected by source class
+    report_chatbot_eligibility: public or strategic chatbot only after promotion gate
+  - source_class: public_collection_data
+    owner: worldenergydata or upstream public API owner
+    canonical_path: api://worldenergydata or documented public-source cache
+    input_residency: api://worldenergydata or documented public-source cache
+    layer: A-DATA
+    level: D-RAW-PUBLIC
+    allowed_artifacts: source identifiers, normalized public records, provenance metadata
+    forbidden_artifacts: unchecked bulk raw dumps in control-plane docs
+    retention_expectations: cache or owner repo per data residence policy
+    publication_rules: cite upstream source and license before public report reuse
+    public_posture: public
+    promotion_gate: provenance/license check and transform validation
+    output_residency: data repo cache or report evidence bundle
+    report_chatbot_eligibility: public report/chatbot eligible after provenance gate
+  - source_class: engineering_reference_data
+    owner: digitalmodel or standards-derived reference owner
+    canonical_path: owner repo reference tables or citation sidecar paths
+    input_residency: owner repo reference tables or citation sidecar paths
+    layer: A-DATA
+    level: D-REFERENCE
+    allowed_artifacts: curated constants, S-N curves, hydrodynamic coefficient references, citation sidecars
+    forbidden_artifacts: copyrighted standards text, unproven constants without Citation where required
+    retention_expectations: owner repo reference-data policy
+    publication_rules: public summaries may publish derived facts only with citation/provenance sidecars and license-safe wording
+    public_posture: restricted
+    promotion_gate: standards citation contract, provenance, license, review gate
+    output_residency: owner repo reference data or calculation report sidecar
+    report_chatbot_eligibility: eligible only with citations and license-safe summaries
+  - source_class: mounted_standards_literature
+    owner: mounted source custodian
+    canonical_path: /mnt/ace/docs/_standards and other mounted-source registry IDs
+    input_residency: mounted-source registry ID; reference-in-place only
+    layer: A-DATA
+    level: D-MOUNTED-REFERENCE
+    allowed_artifacts: redacted source IDs, metadata, citations, derived parameters when allowed
+    forbidden_artifacts: copied standards PDFs, bulk text, unredacted private path inventories
+    retention_expectations: reference in place; do not copy to public repos
+    publication_rules: no public promotion without license/legal/sanitization gate
+    public_posture: restricted
+    promotion_gate: source registry, license, legal, sanitization, citation review gate
+    output_residency: mounted source reference plus repo-safe metadata
+    report_chatbot_eligibility: summaries only after explicit gate; no default public eligibility
+  - source_class: client_project_data
+    owner: client/project repo or private mounted project archive
+    canonical_path: client_projects or redacted project source ID
+    input_residency: client-private repo or redacted mounted project source ID
+    layer: A-DATA
+    level: D-CLIENT-PRIVATE
+    allowed_artifacts: redacted IDs, approved sanitized derivatives, private evidence bundles
+    forbidden_artifacts: public llm-wiki raw data, public chatbot indexes, client-identifiable report snippets
+    retention_expectations: private project retention policy
+    publication_rules: private by default; no public report/public corpus promotion unless sanitized derivative has explicit client/legal gate
+    public_posture: client-private
+    promotion_gate: explicit client authorization, legal, sanitization, and provenance gate
+    output_residency: client-private repo, private corpus, or approved deliverable store
+    report_chatbot_eligibility: client report only after explicit gate; never public by default
+  - source_class: llm_wiki_raw_private_staging
+    owner: private/local corpus owner pending registry
+    canonical_path: unavailable until private corpus registry exists; use redacted source IDs
+    input_residency: private/local staging source ID; no public repo path assumed
+    layer: A-DATA
+    level: D-PRIVATE-STAGING
+    allowed_artifacts: source cards, extraction notes, provenance metadata, private RAG indexes
+    forbidden_artifacts: public llm-wiki pages, public chatbot corpus, unreviewed source excerpts
+    retention_expectations: local/private staging only until promoted
+    publication_rules: fail closed for public report/public corpus until reviewed and routed to approved corpus tier
+    public_posture: local-private
+    promotion_gate: private corpus registry, legal, sanitization, provenance, owner review gate
+    output_residency: private/local staging or approved private corpus
+    report_chatbot_eligibility: private chatbot only after gate; no public eligibility by default
+  - source_class: llm_wiki_public_content
+    owner: public llm-wiki repo
+    canonical_path: tracked public llm-wiki repository path after live inventory
+    input_residency: tracked public llm-wiki repository path after promotion gate
+    layer: A-CURATED-LEARNING
+    level: D-PUBLIC-KNOWLEDGE
+    allowed_artifacts: sanitized public markdown, citations, public-safe source summaries
+    forbidden_artifacts: private raw data, client identifiers, restricted standards text
+    retention_expectations: git-tracked public knowledge pages
+    publication_rules: source/provenance/license/legal gates complete before merge
+    public_posture: public
+    promotion_gate: public knowledge promotion gate and legal scan
+    output_residency: public llm-wiki
+    report_chatbot_eligibility: public chatbot eligible after citation and freshness checks
+  - source_class: execution_artifacts
+    owner: workspace-hub execution/control-plane
+    canonical_path: issue plans, manifests, prompt bundles, run logs, checksums
+    input_residency: source_id plus input_residency references from A-DATA rows; no raw data ownership
+    layer: A-EXEC
+    level: E-MANIFEST-EVIDENCE
+    allowed_artifacts: source_id references, input_residency, output_residency, tool manifests, checksums
+    forbidden_artifacts: duplicated raw data ownership, secrets, bulky generated data by default
+    retention_expectations: commit manifests/evidence; keep bulky runtime output transient unless approved
+    publication_rules: execution evidence may support reports but does not publish source data
+    public_posture: mixed
+    promotion_gate: validation, secret scan, and output-residency review gate
+    output_residency: workspace-hub logs/reports or target repo evidence path
+    report_chatbot_eligibility: evidence summaries eligible after redaction; raw logs private by default
+  - source_class: report_artifacts
+    owner: report-producing repo or client deliverable owner
+    canonical_path: docs/reports, client deliverable store, limited PDFs, chatbot/index configs
+    input_residency: classified evidence bundles and source_id references from A-EXEC/A-DATA
+    layer: A-REPORT
+    level: R-OUTPUT
+    allowed_artifacts: raw internal outputs, client-facing HTML, limited PDFs, chatbot configs, evidence indexes
+    forbidden_artifacts: unreviewed source data, implicit knowledge promotion, private raw indexes in public repos
+    retention_expectations: audience-specific report retention; preserve evidence provenance
+    publication_rules: classify by audience and run legal/sanitization gates before public/client release
+    public_posture: mixed
+    promotion_gate: report evidence, provenance, legal, sanitization, and audience review gate
+    output_residency: internal report path, client deliverable store, or public-safe publication repo
+    report_chatbot_eligibility: depends on audience and output_residency gate

```

warning: Codex's Linux sandbox uses bubblewrap and needs access to create user namespaces.
hook: SessionStart
hook: SessionStart
hook: SessionStart
hook: SessionStart
hook: SessionStart Completed
hook: SessionStart Completed
hook: SessionStart Completed
hook: SessionStart Completed
codex
I’ll re-check the actual files behind the supplied diff, focusing on whether the tests enforce the stated contract rather than only mirroring text. Then I’ll return a verdict with only blocking or material findings.
hook: PreToolUse
hook: PreToolUse
hook: PreToolUse
hook: PreToolUse
hook: PreToolUse
hook: PreToolUse
hook: PreToolUse
hook: PreToolUse
hook: PreToolUse
hook: PreToolUse
hook: PreToolUse
hook: PreToolUse
hook: PreToolUse
hook: PreToolUse
hook: PreToolUse
hook: PreToolUse Completed
hook: PreToolUse Completed
hook: PreToolUse Completed
hook: PreToolUse Completed
hook: PreToolUse Completed
hook: PreToolUse Completed
hook: PreToolUse Completed
hook: PreToolUse Completed
hook: PreToolUse Completed
hook: PreToolUse Completed
hook: PreToolUse Completed
hook: PreToolUse Completed
hook: PreToolUse Completed
hook: PreToolUse Completed
hook: PreToolUse Completed
hook: PostToolUse
hook: PostToolUse
hook: PostToolUse
hook: PostToolUse
hook: PostToolUse
hook: PostToolUse
hook: PostToolUse
hook: PostToolUse
hook: PostToolUse
hook: PostToolUse Completed
hook: PostToolUse Completed
hook: PostToolUse Completed
hook: PostToolUse Completed
hook: PostToolUse Completed
hook: PostToolUse Completed
hook: PostToolUse Completed
hook: PostToolUse Completed
hook: PostToolUse Completed
codex
Verdict: APPROVE

Findings:
- None blocking.

Residual notes:
- I could not locally re-run commands because this Codex sandbox hit `bwrap: loopback: Failed RTM_NEWADDR: Operation not permitted`, so this review is based on the supplied diff.
- The parent scope is appropriately bounded: it defines the cross-layer contract, seed source classes, fixture authority, and reduced markdown rendering without absorbing #2727/#2728/#2729 or #2731/#2732 details.
- The tests now materially guard the first-slice boundary: required schema, seed coverage, private/restricted fail-closed behavior, explicit transition language, and row-keyed markdown drift against the fixture.

One non-blocking hardening opportunity for a follow-up: add a generalized assertion that any row, including `mixed` posture rows, mentioning public report/chatbot/llm-wiki eligibility must also name a gate. Current rows satisfy that contract, but the strongest fail-closed test path is concentrated on private/restricted postures.
hook: Stop
hook: Stop
hook: Stop
hook: Stop
hook: Stop Completed
hook: Stop Completed
hook: Stop Completed
hook: Stop Completed
tokens used
41,778
Verdict: APPROVE

Findings:
- None blocking.

Residual notes:
- I could not locally re-run commands because this Codex sandbox hit `bwrap: loopback: Failed RTM_NEWADDR: Operation not permitted`, so this review is based on the supplied diff.
- The parent scope is appropriately bounded: it defines the cross-layer contract, seed source classes, fixture authority, and reduced markdown rendering without absorbing #2727/#2728/#2729 or #2731/#2732 details.
- The tests now materially guard the first-slice boundary: required schema, seed coverage, private/restricted fail-closed behavior, explicit transition language, and row-keyed markdown drift against the fixture.

One non-blocking hardening opportunity for a follow-up: add a generalized assertion that any row, including `mixed` posture rows, mentioning public report/chatbot/llm-wiki eligibility must also name a gate. Current rows satisfy that contract, but the strongest fail-closed test path is concentrated on private/restricted postures.
