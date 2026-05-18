# feat(execution): block unresolved repo/client/wiki source paths until source registries exist

Parent: #2728

Fail closed on unregistered repo, client, raw-data, and wiki source paths until the source registry work in #2731/#2732 is available.

Execution manifests must not embed raw/private payloads directly. They must reference source IDs and a registry location that can be independently checked.

Acceptance criteria:

- unregistered source paths are rejected before report eligibility
- execution manifests require `source_ids`, `source_registry_kind`, and `source_registry_ref`
- tests cover registered, missing-registry, and inline-raw-data cases
- docs identify #2731/#2732 as the unblockers for full registry-backed source routing
