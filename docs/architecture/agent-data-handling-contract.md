# Agent data handling contract

Scope: [initiative 3606](https://github.com/vamseeachanta/workspace-hub/issues/3606),
resource-authority slice. This contract is an authored authority, not installed
enforcement. A valid descriptor is an evidence claim, not permission or proof.

## Existing authorities and discovery

Reuse `llm-wiki:data/data-source-catalog.yml` for source identities and
`llm-wiki:data/domain-database-index.yml` for domain/consumer relationships.
These owner-relative references resolve in the existing sibling checkout; do not
create a replacement wiki when a reference or configured root is unavailable.
Read known metadata paths before broad searches. Record coverage gaps: zero
matches in a partially available index does not establish source absence.

Preserve catalog-issued source IDs and owner-issued dataset IDs exactly, including
bare slugs; do not invent a namespace or substitute a renamed identity. Catalog
authority and owner context establish their scope.

Each dataset has one authoritative owner. A derived artifact has its own owner
and retains its source relationships; a catalog entry is not a copy of the data.

| Artifact responsibility | Authoritative owner |
|---|---|
| Public-source collection | `worldenergydata`, where the collection contract applies |
| Authorized curated interpretation | Private `llm-wiki` or the owning private project wiki |
| Qualified computational references and calculations | Engineering owner, including `digitalmodel` |
| Client-supplied or measured originals | Owning private project repository |
| Catalogs, discovery maps and workflow policy | Existing metadata owner; hub coordinates references |

Table 1. Ownership follows artifact responsibility; public origin alone does not reassign derivatives.

The reference `digitalmodel:data/dataset-allocation-ledger.json` remains unresolved
in the inspected checkout. `digitalmodel:config/data_sources.yaml` declares
computational dependencies and is not an equivalent allocation ledger. Do not
invent owner records, redirect this pointer or establish another registry here.

The [intelligence operating model](../document-intelligence/llm-wiki-resource-doc-intelligence-operating-model.md)
remains the layer authority. Under the
[provenance contract](../document-intelligence/standards-codes-provenance-reuse-contract.md),
L2 owns provenance and L3 inherits it. Preserve the existing statuses
`gap | indexed | summarized | extracted | promoted | superseded | unreachable`.
They describe processing, not computational readiness. Logical D-L publication
surfaces in the [data layer contract](data-layer-contract.md) do not establish
the visibility or entitlement of an actual repository.

## Original retention, rights and publication

Client-supplied and measured originals shall be committed to the owning private
repository under `data/<dataset>/raw/`, beside extracted outputs. The dataset
manifest shall identify each retained original with a SHA-256 digest, source,
version and extraction relationship. Add a narrow `.gitignore` exception for the
required original, including ignored parent directories where necessary; verify
the actual file is tracked. A path, extraction, reproducible pipeline, archive
format or regenerated download does not replace the original received evidence.

Vendor-licensed standards and codes are the exclusion: original PDFs shall never
be committed, including to private Git. Keep the PDF at its licensed location and
record a `sources:` reference, edition and authorized-access evidence. Retain
`raw_copy_allowed: false` for these originals. Derivatives require source-specific
rights for the proposed extraction, destination and audience; unknown rights
deny copying and publication. Private visibility, citations, anonymization,
synthetic labels or claims of original analysis do not grant source rights.

If rights, terms or storage limits prevent required private-original retention,
ingest acceptance remains blocked pending an explicit owner decision. Do not
silently substitute off-repository storage or weaken the licensed-original
exclusion. The [residence policy](../DATA_RESIDENCE_POLICY.md) regeneration and
size rules apply only after this required-original exception is evaluated.

For original-retention observations, `storage.retention_status` is `retained`
or `required_pending`. Pending records expose blocked ingest; they do not satisfy
retention, and cannot claim ready. Retained originals require private Git, a raw
SHA-256 and narrow ignore evidence. `<dataset>` is one path segment in this
private-project convention, not the public-collection directory layout.
The sole raw-manifest reference is `manifest.locator` with `manifest.revision`;
no second storage manifest pointer is needed. Licensed originals carry
`storage.raw_copy_allowed: false`, and cannot carry Git raw-copy metadata.
Their edition is `resource.source_version`; `rights.evidence_ref` locates the
authorized-access and rights record.

Storage, ownership, transformation rights and publication authorization are
separate decisions. Public destinations require source-specific rights and
audience approval, including private contributions embedded in public sources.
Restricted locators, credentials and raw private payloads do not belong in public
receipts. Use authorized opaque evidence references and private owner manifests.
Saving locally does not establish backup, Git tracking or publication; verify
each claimed disposition separately by reading the saved artifact back.

## Descriptor v1 and qualification

The [resource descriptor schema](../../config/schemas/resource-descriptor-v1.schema.json)
describes a task-scoped observation, not a dataset-allocation registry. Fields
`resource` and `stable_projection` use the same twelve-field shape. `resource`
is the normalized observed metadata; the projection must equal those normalized
fields. Original legacy identity text belongs only in `identity_evidence`.

New document identities use `sha256:` plus 64 lowercase hexadecimal characters.
Exactly 64 bare hexadecimal characters may be normalized on read, with a warning
and original evidence retained. Ambiguous bare 32-hex is unverified; never infer
MD5. Explicit `md5:` plus 32 hex remains legacy read-only, not a new-writer form.
This stricter qualification does not rewrite the parent's compatibility history.
Sidecar OCR does not change source identity; rewritten source bytes do. Source
identity and derived-output integrity hashes must retain their distinct scopes.

Required observation groups include owner-relative manifest locator/revision,
rights evidence and allowed operations/destinations, access status, timestamps,
source vintage, freshness criterion, qualification evidence and limitations.
`readiness_status` is `unverified | partial | ready | unavailable`.
A `ready` claim requires known catalog identity, source-specific rights, available
access, qualified units, governing intended-use criterion and inspection evidence.
Catalog presence or a promoted summary alone is insufficient. Validators shall enable format assertions with `jsonschema[format-nongpl]`
(or an equivalent RFC3339 checker); missing format support is a validation error.
Schema validation
cannot verify catalog membership, permission, timestamp ordering, current expiry,
field equality or evidence integrity; the live consumer must verify those facts.

`source_vintage` is distinct from retrieval/verification time. Refreshing a stale
observation does not qualify the source. Compare RFC3339 instants: source_vintage
<= observed_at <= as_of; verified_at and rights.checked_at <= as_of; both rights
and freshness valid_until > as_of. A future observation is not current evidence. Unreachable sources may retain useful
limited-purpose derivatives, with limitations, but cannot bypass current rights,
access, intended-use or freshness checks. Unknown required dependencies deny reuse.

Unknown scalar evidence uses `{"state":"unknown","reason":"..."}`;
inapplicable identity/unit evidence uses
`{"state":"not_applicable","reason":"..."}`. Reasons must be nonempty.
True zero is numerical, outside this string-valued projection; it is not unknown.
Inapplicable values cannot replace content digests or rights evidence. The separate
`digest_scope` literals `unknown` and `not-applicable` deny content-bearing reuse.

## Stable projection and shared conformance contract

The projection contains exactly `source_id`, `dataset_id`, `doc_key`, `owner_repo`,
`source_version`, `content_digest`, `digest_scope`, `derived_from`, `units`,
`intended_use`, `criteria_revision`, `rights_revision`. Strings carry substantive
versions, not timestamp-only refresh events. A content digest is `sha256:` plus
64 lowercase hex; scope is `source-bytes` or `canonical-json` for reusable content.

`derived_from` is a sorted unique set of canonical owner-scoped identifiers or
namespaced document keys. No filesystem paths or nested objects are allowed.
An empty array means established absence of recorded derivation; unknown lineage
must be represented explicitly and denies reuse. Units map field identifiers to
exact strings or permitted sentinels. `"1"` means dimensionless. No unit conversion,
alias rewriting, case folding or Unicode normalization occurs during hashing.

Canonical JSON uses UTF-8, sorted object keys, compact separators, unescaped
Unicode (`ensure_ascii=False`) and rejects non-finite values (`allow_nan=False`).
Duplicate object keys are rejected before parsing loses them. Projection numeric
leaves are rejected. Ordered observation arrays retain order; set arrays
(`derived_from`, rights operations/destinations) must be sorted and unique.

`resource_descriptor_sha256` hashes the complete normalized descriptor observation
including its projection, with neither output hash embedded in that observation.
`resource_stable_sha256` hashes only the stable projection. A changed observation
time changes the first digest, not the second. Changed rights/source/criteria
revision or failed current eligibility invalidates affected reuse.

The sole planned production canonicalizer is workflow-owned
`scripts/governance/workflow_receipt.py`; it is not implemented by this slice.
Receipt fields include `resource_descriptor_schema`, both digests and an authorized
evidence locator. The workflow owns its full operation/code/environment/criteria
reuse key and integrity checks. Persistence is outside both first slices.
Equality produces at most a candidate pending independent live validation;
caller-supplied references cannot authenticate approval, rights or access.

Schema `x-conformance` vectors are synthetic literal inputs, expected projections,
digest constants or rejection outcomes. They cover key order, timestamps, Unicode,
units, derivation ordering/duplicates, unknowns, inapplicable/forbidden sentinels,
missing digests, legacy identity normalization and observation/projection mismatch.
`as_of` fixes comparison time for expiry cases. `schema_valid` records structural
validity only; `expected` describes future semantic comparison, never live readiness.
Parse-level duplicate-key and non-finite rejection cases will be workflow-owned
raw-string fixtures, outside this parsed-JSON literal set. They must not be
misrepresented as covered by these vectors.
The resource tests validate vector shape; workflow tests must compute agreement
with these same literals through the sole production canonicalizer.

A mismatch halts cross-plan acceptance. Compare canonical bytes, constants and
implementation before assigning the defect. The resource owner corrects constants
within its approved transaction and repeats checks/review; a closed transaction
or expanded scope requires a bounded correction plan. Never relax workflow tests
or edit the resource schema outside the workflow's write boundary. Structural
acceptance of this predecessor does not claim production digest agreement.
