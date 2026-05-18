# Implementation Adversarial Review: workspace-hub issues #2728 and #2729

You are an independent adversarial reviewer. Be skeptical. Do not rubber-stamp.

## Context
Approved issues:
- #2728: define execution layer contracts, tooling, compute routing.
- #2729: define report layer outputs, publication surfaces, evidence rules.

Implementation is docs + schema + tests only. No raw/private data implementation should occur.

## Validation already run
`uv run pytest tests/architecture/test_execution_layer_contract.py tests/architecture/test_report_layer_contract.py -q` -> `26 passed in 5.53s`.

## Review questions
1. Do the execution-layer artifacts enforce source IDs/registries, input/output residency, command/replay manifests, machine/provider/tool routing, checksums, test/legal evidence, and promotion gates?
2. Do the report-layer artifacts enforce output taxonomy, HTML-first/PDF-limited posture, chatbot corpus boundaries, published claim evidence bindings, legal scan, checksums, review verdicts, output residency, promotion decisions, and promotion gates?
3. Are schema fail-closed rules strong enough, especially public llm-wiki promotion and report-eligible handoff?
4. Are tests meaningful, not only string-presence tests? Identify missing negative cases.
5. Is the work inside approved scope and safe to commit/close #2728/#2729? Name any MAJOR blocker.

Output format:
- Verdict: APPROVE | MINOR | MAJOR
- Findings by severity with exact file/path evidence
- Required fixes before closeout

## Artifacts under review


## FILE: docs/architecture/execution-layer-contract.md
```
# Execution Layer Contract (#2728)

The execution layer transforms classified data-layer inputs into report-eligible artifacts without becoming the canonical owner of raw data or bypassing publication gates.

## Levels

| Level | Working name | Contents | Boundary rule |
|---|---|---|---|
| E-L1 | Input contracts | YAML/JSON specs, issue plans, source manifests, fixture manifests, prompt bundles | References data sources by `source_id`, `source_registry_kind`, and `input_residency`; does not own raw data |
| E-L2 | Tools/code execution | ingestion scripts, parsers, report generators, validation harnesses, legal scanners, skills/prompts | Code is repo-backed; Python commands use `uv run`; outputs manifest evidence |
| E-L3 | Compute/runtime placement | registry machine IDs, local worktrees, background jobs, provider tools | References `config/workstations/registry.yaml` for machine truth; no duplicated machine capability policy |
| E-L4 | Validation/evidence | tests, legal scan outputs, adversarial review artifacts, checksums, run manifests, command logs | Required validation/evidence handoff before any report-layer handoff |

## Required manifest fields

Execution manifests must include: `source_ids`, `source_registry_kind`, `source_registry_ref`, `input_residency`, `output_residency`, `tool`, `machine`, `provider_tool`, `command_manifest`, `regeneration_command`, `replay_command`, `environment_pin`, `outputs`, `checksums`, `test_evidence`, `legal_scan_evidence`, `review_artifact_paths`, `promotion_gates`, and `report_eligible`.

## Boundary rules

1. Execution consumes data-layer source IDs and registry references; it does not copy source truth into execution artifacts.
2. Report eligibility requires validation/evidence, a declared `output_residency`, and a report-layer handoff path.
3. Outputs cannot become more public than inputs unless a promotion gate names provenance, license, legal, sanitization, and owner-review evidence.
4. Runtime orchestrators may enforce this later, but the contract fails closed through schema, fixtures, and TDD tests now.
5. Machine/provider routing is a view over `config/workstations/registry.yaml`; #2119, #1838, and #2089 remain open dependencies, not approved policy.

```

## FILE: docs/architecture/execution-entry-point-inventory.md
```
# Execution Entry-Point Inventory (#2728)

Enumeration command: `python - <<'PY' ... Path('/mnt/local-analysis').glob('*') ... PY` plus targeted repo documentation review. Client/project child paths are intentionally redacted.

| Repo | Evidence status | Entry-point classes | Notes |
|---|---|---|---|
| workspace-hub | available | plans, review fanout, legal scan, pytest architecture fixtures, governance docs | control-plane execution contracts live here |
| digitalmodel | available as tier-1 role by docs/memory | engineering scripts, OrcaFlex/OrcaWave workflows, report generation | implementation details owned by repo |
| assetutilities | available as tier-1 role by docs/memory | shared utilities, Python tooling | owner repo policy applies |
| worldenergydata | available as tier-1 role by docs/memory | public/API ingestion and data processing | public collection source owner |
| llm-wiki | available role; live path requires registry confirmation | public knowledge pages, possible public chatbot corpus | raw/private staging is not assumed public |
| aceengineer-website | available role; live path requires registry confirmation | public website publication and demos | sanitized public outputs only |
| aceengineer-strategy | available role; live path requires registry confirmation | GTM/prospect strategy records | generic collateral belongs elsewhere |
| assethold | available as tier-1 role by memory | asset/repo data as owner policy defines | not expanded in this issue |
| client/project roots | unavailable/redacted | private execution inputs and deliverables | no tracked child paths; registry required |

Unavailable means no authoritative registry-backed local path was committed by this issue. Follow-up registry work remains blocked on #2731/#2732.

```

## FILE: docs/architecture/execution-routing-policy-view.md
```
# Execution Routing Policy View

This is a derived policy view for #2728. The canonical machine identity and capability source is `config/workstations/registry.yaml`.

## Registry keys referenced

- `dev-primary`
- `dev-secondary`
- `licensed-win-1`
- `licensed-win-2`
- `macbook-portable`

This document intentionally references registry keys only. It must not duplicate machine identity, network, operating-system, role, provider, or capability fields. When those facts are needed, read the registry.

## Routing posture

- Control-plane documentation and architecture tests default to `dev-primary`.
- Open-source simulation or heavy engineering stacks route by registry capability to a capable Linux worker when approved.
- Licensed Windows execution remains registry-routed and cannot be assumed reachable by SSH.
- Provider tools are capabilities of a machine, not standalone source-of-truth records.

## Open dependencies

#2119, #1838, and #2089 remain open dependencies. This view does not treat them as approved policy and does not replace their future routing contracts.

```

## FILE: docs/architecture/execution-manifest-schema.md
```
# Execution Manifest Schema

Human-readable companion to `execution-manifest.schema.yaml`.

An execution manifest is the reproducibility and evidence handoff record for E-L1 through E-L4. It links source IDs to commands, machines/providers, outputs, validation evidence, legal scan evidence, checksums, and review artifacts.

Minimum required fields are machine-tested in `tests/architecture/test_execution_layer_contract.py`.

## Fail-closed rules

- No inline raw data fields.
- Unknown source IDs require an explicit blocked registry kind tied to #2731/#2732.
- Report handoff requires tests, legal scan status, checksums, review artifacts, and `output_residency`.
- Public output residency requires promotion gates.

```

## FILE: docs/architecture/execution-manifest.schema.yaml
```
type: object
additionalProperties: false
not:
  required:
    - raw_data
    - data_dump
    - client_payload
    - source_text
required:
  - manifest_id
  - issue
  - source_ids
  - source_registry_kind
  - source_registry_ref
  - input_residency
  - output_residency
  - tool
  - machine
  - provider_tool
  - command_manifest
  - regeneration_command
  - replay_command
  - environment_pin
  - outputs
  - checksums
  - test_evidence
  - legal_scan_evidence
  - review_artifact_paths
  - promotion_gates
  - report_eligible
properties:
  manifest_id: {type: string}
  issue: {type: string}
  source_ids:
    type: array
    minItems: 1
    items: {type: string}
  source_registry_kind:
    enum:
      - mounted_source_registry
      - repo_registry
      - document_index_registry
      - manual_seed
      - unavailable
  source_registry_ref: {type: string}
  input_residency:
    enum:
      - raw_data
      - readable_raw_data
      - owner_repo_checkout
      - target_repo_checkout
      - domain_private_corpus
      - registered_client_private_corpus
      - public_llm_wiki
  output_residency:
    enum:
      - public_llm_wiki
      - domain_private_corpus
      - registered_client_private_corpus
      - ignored_internal_run_artifact
      - no_preserve
  tool: {type: string}
  machine: {type: string}
  provider_tool: {type: string}
  command_manifest:
    type: object
    additionalProperties: false
    required: [working_directory, command]
    properties:
      working_directory: {type: string}
      command: {type: string}
  regeneration_command: {type: string}
  replay_command: {type: string}
  environment_pin: {type: string}
  outputs:
    type: array
    minItems: 1
    items:
      type: object
      additionalProperties: false
      required:
        - path
        - kind
        - report_handoff
        - output_residency
      properties:
        path: {type: string}
        kind: {type: string}
        report_handoff: {type: boolean}
        output_residency:
          enum:
            - public_llm_wiki
            - domain_private_corpus
            - registered_client_private_corpus
            - ignored_internal_run_artifact
            - no_preserve
  checksums:
    type: object
    minProperties: 1
  test_evidence:
    type: array
    minItems: 1
  legal_scan_evidence:
    type: object
    additionalProperties: false
    required: [command, result]
    properties:
      command: {type: string}
      result: {type: string}
  review_artifact_paths:
    type: array
    minItems: 1
    items: {type: string}
  promotion_gates:
    type: array
    items:
      enum:
        - provenance
        - license
        - legal
        - sanitization
        - owner-review
  report_eligible: {type: boolean}
allOf:
  - if:
      properties:
        source_registry_kind:
          const: unavailable
    then:
      properties:
        report_eligible:
          const: false
  - if:
      properties:
        output_residency:
          const: public_llm_wiki
    then:
      properties:
        promotion_gates:
          allOf:
            - contains: {const: provenance}
            - contains: {const: license}
            - contains: {const: legal}
            - contains: {const: sanitization}
            - contains: {const: owner-review}
  - if:
      properties:
        outputs:
          contains:
            type: object
            properties:
              output_residency:
                const: public_llm_wiki
    then:
      properties:
        promotion_gates:
          allOf:
            - contains: {const: provenance}
            - contains: {const: license}
            - contains: {const: legal}
            - contains: {const: sanitization}
            - contains: {const: owner-review}
  - if:
      properties:
        report_eligible:
          const: true
    then:
      properties:
        outputs:
          contains:
            type: object
            properties:
              report_handoff:
                const: true

```

## FILE: docs/architecture/execution-follow-up-issue-backlog.md
```
# Execution Follow-up Issue Backlog (#2728)

These are body/command drafts only. They are not self-approved implementation work.

## Execution manifest validator

```bash
gh issue create --title "feat(execution): implement execution manifest validator for #2728" --label enhancement --label domain:workflow --label cat:harness --body-file docs/architecture/follow-up-bodies/execution-manifest-validator.md
```

Body draft: build a validator for `docs/architecture/execution-manifest.schema.yaml` and fail closed on missing source IDs, missing evidence, inline raw data, or public output without promotion gates. Parent: #2728.

## runtime enforcement

```bash
gh issue create --title "feat(execution): enforce report handoff gates at runtime" --label enhancement --label domain:workflow --label cat:harness --body-file docs/architecture/follow-up-bodies/execution-runtime-enforcement.md
```

Body draft: connect execution manifests to report handoff checks so `report_eligible` cannot be asserted without tests, legal scan, checksums, review artifacts, and output-residency compatibility. Parent: #2728.

## Machine/provider routing registry adapter

```bash
gh issue create --title "feat(execution): add machine/provider routing registry adapter" --label enhancement --label domain:infrastructure --label cat:operations --body-file docs/architecture/follow-up-bodies/execution-routing-registry-adapter.md
```

Body draft: expose a read-only adapter over `config/workstations/registry.yaml` for routing decisions while leaving #2119/#1838/#2089 as open policy dependencies. Parent: #2728.

## Registry/source gap adapter

```bash
gh issue create --title "feat(execution): block unresolved repo/client/wiki source paths until #2731/#2732 registry exists" --label enhancement --label domain:workflow --label cat:documentation --body-file docs/architecture/follow-up-bodies/execution-source-registry-gap.md
```

Body draft: fail closed on unregistered repo/client/wiki paths and require source registry references before execution manifests can become report eligible. Parent: #2728.

```

## FILE: docs/architecture/report-layer-contract.md
```
# Report Layer Contract (#2729)

The report layer converts execution evidence into bounded human-facing surfaces. It is not a dumping ground for raw outputs and it must not silently promote private/client data into public corpora.

## Levels

| Level | Working name | Contents | Boundary rule |
|---|---|---|---|
| R-L1 | Raw output | logs, CSV/JSON extracts, intermediate figures, model outputs, generated screenshots | Not a deliverable by default; preserve only when evidence or regeneration requires it |
| R-L2 | Evidence bundle | source manifest references, command manifests, validation results, legal scan, checksums, review verdicts | Required for every published claim and client/public handoff |
| R-L3 | Internal report | investigation notes, review packs, operator-only markdown/HTML | May include private context; not public/client-safe without gates |
| R-L4 | Client-facing HTML | sanitized interactive reports, dashboards, demos, HTML-first deliverables | Preferred client deliverable format; requires evidence bundle and sanitization gate |
| R-L5 | Limited PDF | static exports for filing, signature, contractual attachment, or offline delivery | Exception path only; HTML-first remains default; exception reason required |
| R-L6 | Chatbot/query surface | public or private chatbot corpora, query indexes, embeddings, retrieval metadata | Inherits corpus posture and freshness/scope disclosure; cannot be more public than its source corpus without promotion gates |

## Required output residency

Every report artifact declares `output_residency`:

- `public_llm_wiki` — public reusable learning pages or public chatbot corpus.
- `domain_private_corpus` — private/local llm-wiki raw data or internal domain corpus.
- `registered_client_private_corpus` — client/project-private deliverables or source-derived artifacts.
- `ignored_internal_run_artifact` — transient raw output that should not be durable or deliverable by default.
- `no_preserve` — disposable scratch output.

## Published claim contract

Every report-published claim must bind to:

`source_manifest`, `command_manifest`, `validation_result`, `legal_scan`, `checksum`, `review_verdict`, `output_residency`, and `promotion_decision`.

## Report-derived learning

Keyword: report-derived learning.

Report-derived learning is allowed only when routed by output residency. Private/client report observations can become public only after provenance, license, legal, sanitization, and owner-review promotion gates. Otherwise they stay in a private/local corpus or are not preserved.

## HTML-first and PDF-limited policy

Client-facing HTML is the default because it supports interaction, provenance disclosure, and regeneration links. PDF is limited to specific business/legal/offline needs and must carry an exception reason plus the same evidence bundle as HTML.

```

## FILE: docs/architecture/report-output-taxonomy.md
```
# Report Output Taxonomy (#2729)

| Artifact type | Default deliverable? | Preferred format | Default output residency | Notes |
|---|---:|---|---|---|
| raw_output | no | native/log/csv/json | ignored_internal_run_artifact | Preserve only when required for evidence or replay. |
| evidence_bundle | yes | yaml/json/markdown | domain_private_corpus | Required claim binding surface; client-specific bundles use `registered_client_private_corpus`. |
| internal_report | yes, internal only | markdown/html | domain_private_corpus | May include private context. |
| client_facing_html | yes | html | registered_client_private_corpus | Preferred client-facing deliverable. |
| limited_pdf | exception only | pdf | registered_client_private_corpus | Requires exception reason. |
| chatbot_query_surface | conditional | index/embedding/config | domain_private_corpus | Inherits source-corpus posture and must disclose freshness and corpus scope. |
| public_page | conditional | markdown/html | public_llm_wiki | Only sanitized/promoted content. |
| report_derived_learning | conditional | markdown/yaml | domain_private_corpus | Route to public/private/no-preserve based on source and promotion gates; public route uses `public_llm_wiki`. |

```

## FILE: docs/architecture/report-publication-gates.md
```
# Report Publication Gates (#2729)

Before any report artifact is delivered to a client-facing, public, or chatbot/query surface, require:

1. Evidence bundle complete: source manifest, command manifest, validation result, checksum, review verdict, output residency, and promotion decision.
2. Promotion gate set for public or more-public routing: `provenance`, `license`, `legal`, `sanitization`, and `owner-review`.
3. Canonical legal scan: `scripts/legal/legal-sanity-scan.sh --diff-only` using `.legal-deny-list.yaml`.
4. Sanitization gate for client/public surfaces: remove client identifiers, secrets, private repo paths, raw source excerpts, and unapproved proprietary data.
5. Output-residency compatibility: artifact cannot be more public than input/corpus without explicit promotion gates.
6. Chatbot scope/freshness disclosure when an index, embedding store, or query surface is created.

This contract intentionally uses the existing legal scan and does not create another denylist.

```

## FILE: docs/architecture/report-evidence-bundle-schema.md
```
# Report Evidence Bundle Schema

A report evidence bundle is the required sidecar for client-facing HTML, limited PDF, public pages, chatbot/query surfaces, and report-derived learning. It proves every published claim has source, command, validation, legal, checksum, review, residency, and promotion evidence.

See `report-evidence-bundle.schema.yaml` for the machine-readable seed schema.

```

## FILE: docs/architecture/report-evidence-bundle.schema.yaml
```
type: object
additionalProperties: false
required:
  - bundle_id
  - issue
  - artifact_type
  - output_residency
  - published_claims
  - legal_scan
properties:
  bundle_id: {type: string}
  issue: {type: string}
  artifact_type:
    enum:
      - raw_output
      - evidence_bundle
      - internal_report
      - client_facing_html
      - limited_pdf
      - chatbot_query_surface
      - public_page
      - report_derived_learning
  output_residency:
    enum:
      - public_llm_wiki
      - domain_private_corpus
      - registered_client_private_corpus
      - ignored_internal_run_artifact
      - no_preserve
  published_claims:
    type: array
    minItems: 1
    items:
      type: object
      additionalProperties: false
      required:
        - claim_id
        - statement
        - source_class
        - bindings
        - source_manifest
        - command_manifest
        - validation_result
        - legal_scan
        - checksum
        - review_verdict
        - output_residency
        - promotion_decision
        - promotion_gates
        - sanitization_gate
      properties:
        claim_id: {type: string}
        statement: {type: string}
        source_class: {type: string}
        bindings:
          type: array
          minItems: 8
          items:
            enum:
              - source_manifest
              - command_manifest
              - validation_result
              - legal_scan
              - checksum
              - review_verdict
              - output_residency
              - promotion_decision
          allOf:
            - contains: {const: source_manifest}
            - contains: {const: command_manifest}
            - contains: {const: validation_result}
            - contains: {const: legal_scan}
            - contains: {const: checksum}
            - contains: {const: review_verdict}
            - contains: {const: output_residency}
            - contains: {const: promotion_decision}
        source_manifest: {type: string}
        command_manifest: {type: string}
        validation_result: {type: string}
        legal_scan:
          type: object
          additionalProperties: false
          required: [command, result]
          properties:
            command: {type: string}
            result: {type: string}
        checksum: {type: string}
        review_verdict: {type: string}
        output_residency:
          enum:
            - public_llm_wiki
            - domain_private_corpus
            - registered_client_private_corpus
            - ignored_internal_run_artifact
            - no_preserve
        promotion_decision: {type: string}
        promotion_gates:
          type: array
          items:
            enum:
              - provenance
              - license
              - legal
              - sanitization
              - owner-review
        sanitization_gate: {type: string}
      allOf:
        - if:
            properties:
              output_residency:
                const: public_llm_wiki
          then:
            properties:
              promotion_gates:
                allOf:
                  - contains: {const: provenance}
                  - contains: {const: license}
                  - contains: {const: legal}
                  - contains: {const: sanitization}
                  - contains: {const: owner-review}
  legal_scan:
    type: object
    additionalProperties: false
    required: [command, result]
    properties:
      command: {type: string}
      result: {type: string}
allOf:
  - if:
      properties:
        output_residency:
          const: public_llm_wiki
    then:
      properties:
        published_claims:
          items:
            properties:
              promotion_gates:
                allOf:
                  - contains: {const: provenance}
                  - contains: {const: license}
                  - contains: {const: legal}
                  - contains: {const: sanitization}
                  - contains: {const: owner-review}
registry_backing:
  public_llm_wiki: public llm-wiki repository or public website corpus after promotion gates
  domain_private_corpus: private/local llm-wiki raw data or internal domain corpus
  registered_client_private_corpus: client/project-private corpus registered by data-layer source registry
  ignored_internal_run_artifact: transient execution output not intended for durable publication
  no_preserve: scratch output intentionally discarded

```

## FILE: docs/architecture/report-derived-learning-routing.md
```
# Report-Derived Learning Routing (#2729)

| output_residency | Route | Rule |
|---|---|---|
| public_llm_wiki | public llm-wiki or public site corpus | Requires provenance, license, legal, sanitization, and owner-review gates. |
| domain_private_corpus | private/local llm-wiki raw data or internal domain corpus | Allowed for internal reusable learning only when source permission, provenance, legal, sanitization, and owner-review gates are recorded. |
| registered_client_private_corpus | registered client/private corpus | Allowed only inside the owning client/project boundary with source permission, provenance, legal, sanitization, and owner-review gates. |
| ignored_internal_run_artifact | no learning extraction by default | Preserve only as execution evidence. |
| no_preserve | discard | Do not route to a corpus. |

Report-derived learning must carry source-class and citation separation. Private/client raw or readable data cannot route directly into public llm-wiki.

```

## FILE: docs/architecture/report-follow-up-issue-backlog.md
```
# Report Follow-up Issue Backlog (#2729)

These are body/command drafts only. They do not self-approve implementation work.

## report validator

```bash
gh issue create --title "feat(report): implement report evidence bundle validator for #2729" --label enhancement --label domain:workflow --label cat:harness --body-file docs/architecture/follow-up-bodies/report-validator.md
```

Body draft: validate `report-evidence-bundle.schema.yaml`, published claim bindings, output residency, legal scan result, and sanitization gate before publication.

## artifact index

```bash
gh issue create --title "feat(report): build report artifact index by output residency" --label enhancement --label domain:documentation --label cat:documentation --body-file docs/architecture/follow-up-bodies/report-artifact-index.md
```

Body draft: index raw outputs, evidence bundles, HTML deliverables, limited PDFs, chatbots/query surfaces, and report-derived learning by issue/source/output residency.

## publication pipeline

```bash
gh issue create --title "feat(report): enforce publication pipeline gates for #2729" --label enhancement --label domain:workflow --label cat:harness --body-file docs/architecture/follow-up-bodies/report-publication-pipeline.md
```

Body draft: wire content/report generation to `report-publication-gates.md` and fail closed on missing evidence bundle, legal scan, sanitization, or output-residency compatibility.

```

## FILE: tests/architecture/test_execution_layer_contract.py
```
from copy import deepcopy
from pathlib import Path

from jsonschema import Draft202012Validator
import yaml

ROOT = Path(__file__).resolve().parents[2]
ARCH = ROOT / "docs/architecture"
SCHEMA_PATH = ARCH / "execution-manifest.schema.yaml"
FIXTURE_PATH = ROOT / "tests/fixtures/architecture/execution_manifest.yaml"
ROUTING_CASES_PATH = ROOT / "tests/fixtures/architecture/execution_routing_cases.yaml"
DATA_SOURCE_INVENTORY_PATH = ROOT / "tests/fixtures/architecture/data_source_inventory.yaml"
ROUTING_POLICY_PATH = ARCH / "execution-routing-policy-view.md"
ENTRY_INVENTORY_PATH = ARCH / "execution-entry-point-inventory.md"
FOLLOW_UP_BACKLOG_PATH = ARCH / "execution-follow-up-issue-backlog.md"
CONTRACT_PATH = ARCH / "execution-layer-contract.md"
WORKSTATION_REGISTRY_PATH = ROOT / "config/workstations/registry.yaml"

REQUIRED_EXECUTION_LEVELS = {"E-L1", "E-L2", "E-L3", "E-L4"}
REQUIRED_MANIFEST_FIELDS = {
    "manifest_id",
    "issue",
    "source_ids",
    "source_registry_kind",
    "source_registry_ref",
    "input_residency",
    "output_residency",
    "tool",
    "machine",
    "provider_tool",
    "command_manifest",
    "regeneration_command",
    "replay_command",
    "environment_pin",
    "outputs",
    "checksums",
    "test_evidence",
    "legal_scan_evidence",
    "review_artifact_paths",
    "promotion_gates",
    "report_eligible",
}
EVIDENCE_FIELDS = {
    "regeneration_command",
    "replay_command",
    "environment_pin",
    "checksums",
    "test_evidence",
    "legal_scan_evidence",
    "review_artifact_paths",
}
INPUT_RESIDENCY_ENUM = {
    "raw_data",
    "readable_raw_data",
    "owner_repo_checkout",
    "target_repo_checkout",
    "domain_private_corpus",
    "registered_client_private_corpus",
    "public_llm_wiki",
}
OUTPUT_RESIDENCY_ENUM = {
    "public_llm_wiki",
    "domain_private_corpus",
    "registered_client_private_corpus",
    "ignored_internal_run_artifact",
    "no_preserve",
}
REQUIRED_OUTPUT_FIELDS = {"path", "kind", "report_handoff", "output_residency"}
REQUIRED_PUBLIC_PROMOTION_GATES = {"provenance", "license", "legal", "sanitization", "owner-review"}
SOURCE_REGISTRY_KIND_ENUM = {
    "mounted_source_registry",
    "repo_registry",
    "document_index_registry",
    "manual_seed",
    "unavailable",
}
RAW_DATA_FORBIDDEN_KEYS = {"raw_data", "data_dump", "client_payload", "source_text"}
DUPLICATED_MACHINE_TRUTH_FIELDS = {
    "hostname:",
    "tailscale_ip:",
    "os:",
    "roles:",
    "capabilities:",
    "agent_clis:",
    "tools:",
}
NAMED_REPOS = {
    "workspace-hub",
    "digitalmodel",
    "assetutilities",
    "worldenergydata",
    "llm-wiki",
    "aceengineer-website",
    "aceengineer-strategy",
}


def load_yaml(path: Path) -> dict:
    assert path.exists(), f"Missing required file: {path}"
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    assert isinstance(data, dict), f"{path} must contain a YAML mapping"
    return data


def test_execution_levels_are_defined_in_contract():
    text = CONTRACT_PATH.read_text(encoding="utf-8")
    for level in REQUIRED_EXECUTION_LEVELS:
        assert level in text
    assert "does not own raw data" in text
    assert "validation/evidence" in text
    assert "report-layer handoff" in text


def test_execution_manifest_required_fields():
    schema = load_yaml(SCHEMA_PATH)
    manifest = load_yaml(FIXTURE_PATH)
    required = set(schema["required"])
    assert REQUIRED_MANIFEST_FIELDS <= required
    assert REQUIRED_MANIFEST_FIELDS <= set(manifest)


def test_execution_manifest_fixture_validates_against_schema_and_registry():
    schema = load_yaml(SCHEMA_PATH)
    manifest = load_yaml(FIXTURE_PATH)
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(manifest)
    inventory = load_yaml(DATA_SOURCE_INVENTORY_PATH)["sources"]
    source_ids = {row["source_id"] for row in inventory}
    assert set(manifest["source_ids"]) <= source_ids
    assert manifest["source_registry_kind"] in SOURCE_REGISTRY_KIND_ENUM
    assert manifest["source_registry_kind"] != "unavailable"


def test_execution_manifest_fails_closed_for_unavailable_sources_and_public_gates():
    schema = load_yaml(SCHEMA_PATH)
    validator = Draft202012Validator(schema)
    manifest = load_yaml(FIXTURE_PATH)

    unavailable = deepcopy(manifest)
    unavailable["source_registry_kind"] = "unavailable"
    unavailable["source_registry_ref"] = ""
    unavailable["report_eligible"] = True
    assert list(validator.iter_errors(unavailable)), "unavailable registry must not be report eligible"

    public = deepcopy(manifest)
    public["output_residency"] = "public_llm_wiki"
    public["outputs"][0]["output_residency"] = "public_llm_wiki"
    public["promotion_gates"] = ["legal"]
    assert list(validator.iter_errors(public)), "public output must require the full promotion gate set"

    nested_public = deepcopy(manifest)
    nested_public["output_residency"] = "domain_private_corpus"
    nested_public["outputs"][0]["output_residency"] = "public_llm_wiki"
    nested_public["promotion_gates"] = ["legal"]
    assert list(validator.iter_errors(nested_public)), "public output items must require the full promotion gate set"

    no_handoff = deepcopy(manifest)
    no_handoff["report_eligible"] = True
    for output in no_handoff["outputs"]:
        output["report_handoff"] = False
    assert list(validator.iter_errors(no_handoff)), "report eligibility requires at least one report handoff output"


def test_execution_manifest_closed_residency_vocabularies_and_output_schema():
    schema = load_yaml(SCHEMA_PATH)
    manifest = load_yaml(FIXTURE_PATH)
    assert schema["additionalProperties"] is False
    assert set(schema["not"]["required"]) == RAW_DATA_FORBIDDEN_KEYS
    assert set(schema["properties"]["input_residency"]["enum"]) == INPUT_RESIDENCY_ENUM
    assert set(schema["properties"]["output_residency"]["enum"]) == OUTPUT_RESIDENCY_ENUM
    assert manifest["input_residency"] in INPUT_RESIDENCY_ENUM
    assert manifest["output_residency"] in OUTPUT_RESIDENCY_ENUM
    output_item_schema = schema["properties"]["outputs"]["items"]
    assert output_item_schema["additionalProperties"] is False
    assert REQUIRED_OUTPUT_FIELDS <= set(output_item_schema["required"])
    assert set(output_item_schema["properties"]["output_residency"]["enum"]) == OUTPUT_RESIDENCY_ENUM
    for output in manifest["outputs"]:
        assert REQUIRED_OUTPUT_FIELDS <= set(output)
        assert output["output_residency"] in OUTPUT_RESIDENCY_ENUM


def test_execution_manifest_evidence_fields_complete():
    manifest = load_yaml(FIXTURE_PATH)
    for field in EVIDENCE_FIELDS:
        value = manifest[field]
        assert value not in (None, "", [], {}), f"{field} must be non-empty"
    assert manifest["legal_scan_evidence"]["command"] == "scripts/legal/legal-sanity-scan.sh --diff-only"
    assert manifest["review_artifact_paths"], "review artifacts are required for report handoff"


def test_no_execution_direct_publication():
    schema = load_yaml(SCHEMA_PATH)
    manifest = load_yaml(FIXTURE_PATH)
    promotion_gate_schema = schema["properties"]["promotion_gates"]
    assert set(promotion_gate_schema["items"]["enum"]) == REQUIRED_PUBLIC_PROMOTION_GATES
    if manifest["report_eligible"]:
        assert manifest["test_evidence"], "report eligibility requires tests"
        assert manifest["legal_scan_evidence"]["result"] in {"pass", "pending-required-before-publication"}
        assert manifest["review_artifact_paths"], "report eligibility requires adversarial review artifacts"
        assert manifest["output_residency"] != "public_llm_wiki" or REQUIRED_PUBLIC_PROMOTION_GATES <= set(
            manifest["promotion_gates"]
        ), "public output residency requires complete promotion gates"


def test_routing_policy_references_workstation_registry_without_duplicate_truth():
    registry = load_yaml(WORKSTATION_REGISTRY_PATH)
    policy = ROUTING_POLICY_PATH.read_text(encoding="utf-8")
    assert "config/workstations/registry.yaml" in policy
    for machine_id in ["dev-primary", "dev-secondary", "licensed-win-1", "licensed-win-2"]:
        assert machine_id in registry["machines"]
        assert machine_id in policy
    for field in DUPLICATED_MACHINE_TRUTH_FIELDS:
        assert field not in policy, f"routing policy view must not duplicate canonical field {field}"
    for dependency in ["#2119", "#1838", "#2089"]:
        assert dependency in policy
        assert "open dependenc" in policy.lower()


def test_validation_evidence_required_for_report_handoff():
    manifest = load_yaml(FIXTURE_PATH)
    assert manifest["outputs"], "manifest must declare outputs"
    for output in manifest["outputs"]:
        if output.get("report_handoff"):
            assert manifest["command_manifest"]
            assert manifest["regeneration_command"]
            assert manifest["test_evidence"]
            assert manifest["legal_scan_evidence"]
            assert manifest["checksums"]
            assert manifest["review_artifact_paths"]
            assert output["output_residency"] == manifest["output_residency"]


def test_residency_compatibility_matrix():
    cases = load_yaml(ROUTING_CASES_PATH)["cases"]
    assert any(case["expected"] == "reject" for case in cases)
    for case in cases:
        assert case["input_residency"] in INPUT_RESIDENCY_ENUM
        assert case["output_residency"] in OUTPUT_RESIDENCY_ENUM
        more_public = case["output_publicity_rank"] > case["input_publicity_rank"]
        if more_public and not case.get("promotion_gates"):
            assert case["expected"] == "reject", f"{case['case_id']} must fail closed"
        if more_public and case.get("promotion_gates"):
            assert REQUIRED_PUBLIC_PROMOTION_GATES <= set(case["promotion_gates"])
        if case["expected"] == "allow":
            assert case.get("validation_evidence")
            assert case.get("promotion_gates") or not more_public


def test_input_data_boundary_crosswalk():
    manifest = load_yaml(FIXTURE_PATH)
    assert manifest["source_ids"], "execution must reference data-layer source IDs"
    assert manifest["source_registry_kind"] in SOURCE_REGISTRY_KIND_ENUM
    inline_raw_keys = {"raw_data", "data_dump", "client_payload", "source_text"}
    assert not inline_raw_keys & set(manifest), "execution manifest must not own inline raw data"
    assert manifest["source_registry_ref"], "manifest must point to the applicable registry or blocked source issue"


def test_execution_entry_point_inventory_covers_named_repos():
    text = ENTRY_INVENTORY_PATH.read_text(encoding="utf-8")
    for repo in NAMED_REPOS:
        assert f"| {repo} |" in text
    assert "Enumeration command" in text
    assert "unavailable" in text.lower() or "not available" in text.lower()
    assert "client_projects/" not in text, "tracked inventory must not leak client child paths"


def test_follow_up_issue_bundle_present():
    text = FOLLOW_UP_BACKLOG_PATH.read_text(encoding="utf-8")
    for phrase in [
        "gh issue create",
        "execution manifest validator",
        "runtime enforcement",
        "machine/provider routing registry adapter",
        "#2728",
    ]:
        assert phrase in text
    fence_lines = [line.strip() for line in text.splitlines() if line.strip().startswith("```")]
    assert fence_lines.count("```bash") == fence_lines.count("```")
    for body_file in [
        "docs/architecture/follow-up-bodies/execution-manifest-validator.md",
        "docs/architecture/follow-up-bodies/execution-runtime-enforcement.md",
        "docs/architecture/follow-up-bodies/execution-routing-registry-adapter.md",
        "docs/architecture/follow-up-bodies/execution-source-registry-gap.md",
    ]:
        assert (ROOT / body_file).exists(), f"Missing follow-up issue body: {body_file}"

```

## FILE: tests/architecture/test_report_layer_contract.py
```
from copy import deepcopy
from pathlib import Path

from jsonschema import Draft202012Validator
import yaml

ROOT = Path(__file__).resolve().parents[2]
ARCH = ROOT / "docs/architecture"
CONTRACT_PATH = ARCH / "report-layer-contract.md"
TAXONOMY_DOC_PATH = ARCH / "report-output-taxonomy.md"
GATES_PATH = ARCH / "report-publication-gates.md"
EVIDENCE_DOC_PATH = ARCH / "report-evidence-bundle-schema.md"
SCHEMA_PATH = ARCH / "report-evidence-bundle.schema.yaml"
ROUTING_DOC_PATH = ARCH / "report-derived-learning-routing.md"
FOLLOW_UP_BACKLOG_PATH = ARCH / "report-follow-up-issue-backlog.md"
CONTENT_PIPELINE_PATH = ROOT / "docs/content-pipeline/README.md"
EVIDENCE_FIXTURE_PATH = ROOT / "tests/fixtures/architecture/report_evidence_bundle.yaml"
RESIDENCY_CASES_PATH = ROOT / "tests/fixtures/architecture/report_residency_cases.yaml"
TAXONOMY_FIXTURE_PATH = ROOT / "tests/fixtures/architecture/report_output_taxonomy.yaml"

REQUIRED_REPORT_LEVELS = {"R-L1", "R-L2", "R-L3", "R-L4", "R-L5", "R-L6"}
REQUIRED_ARTIFACT_TYPES = {
    "raw_output",
    "evidence_bundle",
    "internal_report",
    "client_facing_html",
    "limited_pdf",
    "chatbot_query_surface",
    "public_page",
    "report_derived_learning",
}
OUTPUT_RESIDENCY_ENUM = {
    "public_llm_wiki",
    "domain_private_corpus",
    "registered_client_private_corpus",
    "ignored_internal_run_artifact",
    "no_preserve",
}
REQUIRED_PUBLIC_PROMOTION_GATES = {"provenance", "license", "legal", "sanitization", "owner-review"}
PUBLISHED_CLAIM_BINDINGS = {
    "source_manifest",
    "command_manifest",
    "validation_result",
    "legal_scan",
    "checksum",
    "review_verdict",
    "output_residency",
    "promotion_decision",
}


def load_yaml(path: Path) -> dict:
    assert path.exists(), f"Missing required file: {path}"
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    assert isinstance(data, dict), f"{path} must contain a YAML mapping"
    return data


def test_report_levels_are_defined_in_contract():
    text = CONTRACT_PATH.read_text(encoding="utf-8")
    for level in REQUIRED_REPORT_LEVELS:
        assert level in text
    assert "report-derived" in text
    assert "output_residency" in text
    assert "HTML-first" in text


def test_raw_outputs_not_deliverables_by_default():
    taxonomy = load_yaml(TAXONOMY_FIXTURE_PATH)["artifacts"]
    raw_rows = [row for row in taxonomy if row["artifact_type"] == "raw_output"]
    assert raw_rows
    for row in raw_rows:
        assert row["deliverable_by_default"] is False
        assert row["default_output_residency"] == "ignored_internal_run_artifact"


def test_html_default_pdf_limited():
    taxonomy = load_yaml(TAXONOMY_FIXTURE_PATH)["artifacts"]
    html = next(row for row in taxonomy if row["artifact_type"] == "client_facing_html")
    pdf = next(row for row in taxonomy if row["artifact_type"] == "limited_pdf")
    assert html["preferred_format"] == "html"
    assert html["deliverable_by_default"] is True
    assert pdf["preferred_format"] == "pdf"
    assert pdf["requires_exception_reason"] is True
    assert pdf["exception_reason"]


def test_report_evidence_bundle_fixture_validates_against_schema():
    schema = load_yaml(SCHEMA_PATH)
    bundle = load_yaml(EVIDENCE_FIXTURE_PATH)
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(bundle)


def test_report_evidence_bundle_fails_closed_for_public_claim_without_full_gates():
    schema = load_yaml(SCHEMA_PATH)
    validator = Draft202012Validator(schema)
    bundle = load_yaml(EVIDENCE_FIXTURE_PATH)
    public = deepcopy(bundle)
    public["output_residency"] = "public_llm_wiki"
    public["published_claims"][0]["output_residency"] = "public_llm_wiki"
    public["published_claims"][0]["promotion_gates"] = ["legal"]
    assert list(validator.iter_errors(public)), "public claims must require the full promotion gate set"

    top_public = deepcopy(bundle)
    top_public["output_residency"] = "public_llm_wiki"
    top_public["published_claims"][0]["output_residency"] = "registered_client_private_corpus"
    top_public["published_claims"][0]["promotion_gates"] = ["legal"]
    assert list(validator.iter_errors(top_public)), "public bundles must require every claim to carry full gates"

    missing_binding = deepcopy(bundle)
    bindings = missing_binding["published_claims"][0]["bindings"]
    bindings.remove("promotion_decision")
    bindings.append("source_manifest")
    assert list(validator.iter_errors(missing_binding)), "claim bindings must include every required evidence binding"


def test_client_public_requires_evidence_bundle():
    bundle = load_yaml(EVIDENCE_FIXTURE_PATH)
    for claim in bundle["published_claims"]:
        bindings = set(claim["bindings"])
        assert PUBLISHED_CLAIM_BINDINGS <= bindings
        assert claim["legal_scan"]["command"] == "scripts/legal/legal-sanity-scan.sh --diff-only"
        assert claim["sanitization_gate"] in {"pass", "required-before-publication"}


def test_chatbot_inherits_corpus_posture():
    cases = load_yaml(RESIDENCY_CASES_PATH)["cases"]
    assert any(case["artifact_type"] == "chatbot_query_surface" for case in cases)
    for case in cases:
        if case["artifact_type"] == "chatbot_query_surface":
            more_public = case["output_publicity_rank"] > case["corpus_publicity_rank"]
            if more_public:
                assert case["expected"] == "reject"
            if case["expected"] == "allow":
                assert case["freshness_disclosure"]
                assert case["corpus_scope_disclosure"]


def test_report_derived_learning_routes_by_output_residency():
    cases = load_yaml(RESIDENCY_CASES_PATH)["cases"]
    routing_text = ROUTING_DOC_PATH.read_text(encoding="utf-8")
    for destination in OUTPUT_RESIDENCY_ENUM:
        assert destination in routing_text
    for case in cases:
        if case["artifact_type"] == "report_derived_learning" and case["expected"] == "allow":
            assert case["output_residency"] in OUTPUT_RESIDENCY_ENUM
            assert case["target_corpus"]
            assert REQUIRED_PUBLIC_PROMOTION_GATES <= set(case["promotion_gates"])


def test_report_taxonomy_seed_artifacts():
    taxonomy = load_yaml(TAXONOMY_FIXTURE_PATH)["artifacts"]
    actual = {row["artifact_type"] for row in taxonomy}
    assert REQUIRED_ARTIFACT_TYPES <= actual
    text = TAXONOMY_DOC_PATH.read_text(encoding="utf-8")
    for artifact_type in REQUIRED_ARTIFACT_TYPES:
        assert artifact_type in text


def test_evidence_bundle_claim_binding():
    schema = load_yaml(SCHEMA_PATH)
    bundle = load_yaml(EVIDENCE_FIXTURE_PATH)
    enum_values = set(schema["properties"]["output_residency"]["enum"])
    assert schema["additionalProperties"] is False
    assert OUTPUT_RESIDENCY_ENUM == enum_values
    assert set(schema["properties"]["artifact_type"]["enum"]) == REQUIRED_ARTIFACT_TYPES
    claim_schema = schema["properties"]["published_claims"]["items"]
    assert claim_schema["additionalProperties"] is False
    assert PUBLISHED_CLAIM_BINDINGS <= set(claim_schema["required"])
    assert "source_class" in claim_schema["required"]
    assert "sanitization_gate" in claim_schema["required"]
    assert "promotion_gates" in claim_schema["required"]
    assert set(claim_schema["properties"]["output_residency"]["enum"]) == OUTPUT_RESIDENCY_ENUM
    assert set(claim_schema["properties"]["promotion_gates"]["items"]["enum"]) == REQUIRED_PUBLIC_PROMOTION_GATES
    for value in OUTPUT_RESIDENCY_ENUM:
        assert value in schema["registry_backing"]
    for claim in bundle["published_claims"]:
        assert claim["output_residency"] in OUTPUT_RESIDENCY_ENUM
        assert PUBLISHED_CLAIM_BINDINGS <= set(claim["bindings"])
        assert claim["source_class"]
        assert claim["promotion_decision"]
        if claim["output_residency"] == "public_llm_wiki":
            assert REQUIRED_PUBLIC_PROMOTION_GATES <= set(claim["promotion_gates"])


def test_publication_gates_use_canonical_legal_scan():
    text = GATES_PATH.read_text(encoding="utf-8")
    assert "scripts/legal/legal-sanity-scan.sh --diff-only" in text
    assert ".legal-deny-list.yaml" in text
    assert "parallel denylist" not in text.lower()
    for gate in REQUIRED_PUBLIC_PROMOTION_GATES:
        assert gate in text


def test_content_pipeline_has_bounded_report_crosslink():
    text = CONTENT_PIPELINE_PATH.read_text(encoding="utf-8")
    assert "docs/architecture/report-publication-gates.md" in text
    assert "report-derived learning" in text


def test_follow_up_issue_backlog_present():
    text = FOLLOW_UP_BACKLOG_PATH.read_text(encoding="utf-8")
    for phrase in [
        "gh issue create",
        "report validator",
        "artifact index",
        "publication pipeline",
        "#2729",
    ]:
        assert phrase in text
    for body_file in [
        "docs/architecture/follow-up-bodies/report-validator.md",
        "docs/architecture/follow-up-bodies/report-artifact-index.md",
        "docs/architecture/follow-up-bodies/report-publication-pipeline.md",
    ]:
        assert (ROOT / body_file).exists(), f"Missing follow-up issue body: {body_file}"

```

## FILE: tests/fixtures/architecture/execution_manifest.yaml
```
manifest_id: exec-2728-contract-seed
issue: '#2728'
source_ids:
  - mnt_workspace_control_plane
  - mnt_local_analysis_repos
source_registry_kind: mounted_source_registry
source_registry_ref: tests/fixtures/architecture/data_source_inventory.yaml
input_residency: owner_repo_checkout
output_residency: domain_private_corpus
tool: architecture contract documentation and pytest validation
machine: dev-primary
provider_tool: hermes
command_manifest:
  working_directory: /mnt/local-analysis/workspace-hub
  command: uv run pytest tests/architecture/test_execution_layer_contract.py -v
regeneration_command: uv run pytest tests/architecture/test_execution_layer_contract.py -v
replay_command: uv run pytest tests/architecture/test_execution_layer_contract.py -v
environment_pin: uv-managed Python from pyproject.toml in workspace-hub
outputs:
  - path: docs/architecture/execution-layer-contract.md
    kind: contract
    report_handoff: true
    output_residency: domain_private_corpus
checksums:
  strategy: compute during closeout or artifact publication
  current_status: pending until final artifact bundle
test_evidence:
  - command: uv run pytest tests/architecture/test_execution_layer_contract.py -v
    expected: pass
legal_scan_evidence:
  command: scripts/legal/legal-sanity-scan.sh --diff-only
  result: pending-required-before-publication
review_artifact_paths:
  - scripts/review/results/2026-05-18-plan-2728-claude.md
  - scripts/review/results/2026-05-18-plan-2728-codex.md
promotion_gates:
  - provenance
  - license
  - legal
  - sanitization
  - owner-review
report_eligible: true

```

## FILE: tests/fixtures/architecture/execution_routing_cases.yaml
```
cases:
  - case_id: private_client_to_public_without_gate
    input_residency: registered_client_private_corpus
    output_residency: public_llm_wiki
    input_publicity_rank: 1
    output_publicity_rank: 4
    promotion_gates: []
    validation_evidence: []
    expected: reject
  - case_id: readable_raw_to_private_report_with_gate
    input_residency: readable_raw_data
    output_residency: domain_private_corpus
    input_publicity_rank: 2
    output_publicity_rank: 2
    promotion_gates: [provenance, license, legal, sanitization, owner-review]
    validation_evidence: [tests, checksums, review]
    expected: allow
  - case_id: public_wiki_to_public_report_with_gate
    input_residency: public_llm_wiki
    output_residency: public_llm_wiki
    input_publicity_rank: 4
    output_publicity_rank: 4
    promotion_gates: [provenance, license, legal, sanitization, owner-review]
    validation_evidence: [tests, checksums, review]
    expected: allow
  - case_id: raw_data_to_internal_artifact
    input_residency: raw_data
    output_residency: ignored_internal_run_artifact
    input_publicity_rank: 1
    output_publicity_rank: 1
    promotion_gates: []
    validation_evidence: [tests, checksums]
    expected: allow

```

## FILE: tests/fixtures/architecture/report_evidence_bundle.yaml
```
bundle_id: report-2729-contract-seed
issue: '#2729'
artifact_type: client_facing_html
output_residency: registered_client_private_corpus
legal_scan:
  command: scripts/legal/legal-sanity-scan.sh --diff-only
  result: required-before-publication
published_claims:
  - claim_id: report-claim-001
    statement: Report claim must be traceable to source, command, validation, legal, checksum, review, residency, and promotion evidence.
    bindings:
      - source_manifest
      - command_manifest
      - validation_result
      - legal_scan
      - checksum
      - review_verdict
      - output_residency
      - promotion_decision
    source_manifest: tests/fixtures/architecture/layer_boundary_matrix.yaml
    command_manifest: tests/fixtures/architecture/execution_manifest.yaml
    validation_result: uv run pytest tests/architecture/test_report_layer_contract.py -v
    legal_scan:
      command: scripts/legal/legal-sanity-scan.sh --diff-only
      result: required-before-publication
    checksum: pending-final-artifact-checksum
    review_verdict: required-before-closeout
    output_residency: registered_client_private_corpus
    promotion_decision: no-public-promotion-without-gates
    promotion_gates:
      - provenance
      - license
      - legal
      - sanitization
      - owner-review
    sanitization_gate: required-before-publication
    source_class: registered_client_private_corpus

```

## FILE: tests/fixtures/architecture/report_output_taxonomy.yaml
```
artifacts:
  - artifact_type: raw_output
    deliverable_by_default: false
    preferred_format: native
    default_output_residency: ignored_internal_run_artifact
    requires_exception_reason: false
    exception_reason: null
  - artifact_type: evidence_bundle
    deliverable_by_default: true
    preferred_format: yaml
    default_output_residency: domain_private_corpus
    requires_exception_reason: false
    exception_reason: null
  - artifact_type: internal_report
    deliverable_by_default: true
    preferred_format: html
    default_output_residency: domain_private_corpus
    requires_exception_reason: false
    exception_reason: null
  - artifact_type: client_facing_html
    deliverable_by_default: true
    preferred_format: html
    default_output_residency: registered_client_private_corpus
    requires_exception_reason: false
    exception_reason: null
  - artifact_type: limited_pdf
    deliverable_by_default: false
    preferred_format: pdf
    default_output_residency: registered_client_private_corpus
    requires_exception_reason: true
    exception_reason: contractual filing, signature package, offline archive, or client-requested static export
  - artifact_type: chatbot_query_surface
    deliverable_by_default: false
    preferred_format: index
    default_output_residency: domain_private_corpus
    requires_exception_reason: false
    exception_reason: null
  - artifact_type: public_page
    deliverable_by_default: false
    preferred_format: markdown
    default_output_residency: public_llm_wiki
    requires_exception_reason: false
    exception_reason: null
  - artifact_type: report_derived_learning
    deliverable_by_default: false
    preferred_format: markdown
    default_output_residency: domain_private_corpus
    requires_exception_reason: false
    exception_reason: null

```

## FILE: tests/fixtures/architecture/report_residency_cases.yaml
```
cases:
  - case_id: private_client_chatbot_to_public_without_promotion
    artifact_type: chatbot_query_surface
    corpus_publicity_rank: 1
    output_publicity_rank: 4
    output_residency: public_llm_wiki
    target_corpus: public chatbot corpus
    freshness_disclosure: true
    corpus_scope_disclosure: true
    promotion_gates: []
    expected: reject
  - case_id: private_chatbot_stays_private_with_disclosure
    artifact_type: chatbot_query_surface
    corpus_publicity_rank: 1
    output_publicity_rank: 1
    output_residency: registered_client_private_corpus
    target_corpus: client-private chatbot corpus
    freshness_disclosure: true
    corpus_scope_disclosure: true
    promotion_gates: []
    expected: allow
  - case_id: public_report_learning_to_public_wiki
    artifact_type: report_derived_learning
    corpus_publicity_rank: 4
    output_publicity_rank: 4
    output_residency: public_llm_wiki
    target_corpus: public llm-wiki
    freshness_disclosure: true
    corpus_scope_disclosure: true
    promotion_gates: [provenance, license, legal, sanitization, owner-review]
    expected: allow
  - case_id: client_report_learning_to_private_corpus
    artifact_type: report_derived_learning
    corpus_publicity_rank: 1
    output_publicity_rank: 1
    output_residency: registered_client_private_corpus
    target_corpus: registered client-private corpus
    freshness_disclosure: true
    corpus_scope_disclosure: true
    promotion_gates: [provenance, license, legal, sanitization, owner-review]
    expected: allow

```

## FILE: docs/architecture/follow-up-bodies/execution-manifest-validator.md
```
# feat(execution): implement execution manifest validator for #2728

Parent: #2728

Build a validator for `docs/architecture/execution-manifest.schema.yaml` that fails closed on:

- missing `source_ids`, `source_registry_kind`, or `source_registry_ref`
- missing command/replay/regeneration metadata
- missing tests, checksums, legal scan evidence, or review artifacts
- inline raw/private payload keys such as `raw_data`, `data_dump`, `client_payload`, or `source_text`
- public or more-public output routing without `provenance`, `license`, `legal`, `sanitization`, and `owner-review` gates

Acceptance criteria:

- validator has TDD coverage for valid and invalid manifests
- validator is wired to architecture validation or pre-publication checks
- validation output identifies the failing field and issue reference

```

## FILE: docs/architecture/follow-up-bodies/execution-routing-registry-adapter.md
```
# feat(execution): add machine/provider routing registry adapter

Parent: #2728

Expose a read-only adapter over `config/workstations/registry.yaml` for execution routing decisions without duplicating workstation truth in architecture docs.

The adapter should support:

- machine/provider capability lookup
- execution residency constraints
- missing-machine fail-closed behavior
- explicit blocked states for unresolved dependencies #2119, #1838, and #2089

Acceptance criteria:

- adapter has TDD coverage for known machines and unknown-machine rejection
- adapter returns structured routing metadata consumable by execution manifests
- architecture docs reference the adapter instead of duplicating machine details
- unresolved dependency states are represented explicitly and cannot be treated as ready

```

## FILE: docs/architecture/follow-up-bodies/execution-runtime-enforcement.md
```
# feat(execution): enforce report handoff gates at runtime

Parent: #2728

Connect execution manifests to report handoff checks so `report_eligible` cannot be asserted unless the manifest includes:

- source IDs and a source registry reference
- command, replay, regeneration, and environment metadata
- checksums for generated outputs
- targeted test evidence
- canonical legal scan evidence
- adversarial review artifact paths
- output-residency compatibility and required promotion gates

Acceptance criteria:

- runtime/check script fails closed on missing evidence
- runtime/check script rejects inline raw/private payload fields
- CI or pre-publication workflow invokes the check before report publication
- tests cover valid, missing-evidence, and invalid-publication cases

```

## FILE: docs/architecture/follow-up-bodies/execution-source-registry-gap.md
```
# feat(execution): block unresolved repo/client/wiki source paths until source registries exist

Parent: #2728

Fail closed on unregistered repo, client, raw-data, and wiki source paths until the source registry work in #2731/#2732 is available.

Execution manifests must not embed raw/private payloads directly. They must reference source IDs and a registry location that can be independently checked.

Acceptance criteria:

- unregistered source paths are rejected before report eligibility
- execution manifests require `source_ids`, `source_registry_kind`, and `source_registry_ref`
- tests cover registered, missing-registry, and inline-raw-data cases
- docs identify #2731/#2732 as the unblockers for full registry-backed source routing

```

## FILE: docs/architecture/follow-up-bodies/report-artifact-index.md
```
# feat(report): build report artifact index by output residency

Parent: #2729

Create a report artifact index that tracks report-layer artifacts by issue, source IDs, artifact type, output residency, and promotion state.

The index should cover:

- raw outputs
- evidence bundles
- internal reports
- client-facing HTML
- limited PDFs
- chatbot/query surfaces
- public pages
- report-derived learning

Acceptance criteria:

- artifact index schema includes source IDs, issue reference, artifact type, output residency, and promotion gates
- index generation has tests or validator coverage
- raw outputs are not marked deliverable by default
- public/client-facing entries require evidence bundle references and legal/sanitization gate status

```

## FILE: docs/architecture/follow-up-bodies/report-publication-pipeline.md
```
# feat(report): enforce publication pipeline gates for #2729

Parent: #2729

Wire content/report generation to `docs/architecture/report-publication-gates.md` and fail closed when publication evidence is incomplete.

Publication must require:

- evidence bundle validation
- canonical legal scan evidence
- sanitization gate evidence
- source/command/checksum/review bindings for published claims
- output-residency compatibility
- explicit promotion decision for public or more-public outputs

Acceptance criteria:

- pipeline gate has TDD coverage for allow/reject cases
- generated HTML/PDF/chatbot/public-page outputs cannot publish without evidence bundle validation
- missing legal scan or sanitization evidence blocks publication
- closeout docs record the validator command and evidence path

```

## FILE: docs/architecture/follow-up-bodies/report-validator.md
```
# feat(report): implement report evidence bundle validator for #2729

Parent: #2729

Validate `docs/architecture/report-evidence-bundle.schema.yaml` and report evidence bundles before publication.

The validator must fail closed on:

- missing published claim bindings
- missing source manifest, command manifest, validation result, legal scan, checksum, review verdict, output residency, or promotion decision
- public or client-facing publication without sanitization and promotion gate evidence
- unknown artifact types or output residency values

Acceptance criteria:

- validator has TDD coverage for valid and invalid evidence bundles
- validator reports the exact failing claim/field
- publication workflows can call the validator before publishing HTML/PDF/chatbot/query surfaces

```
