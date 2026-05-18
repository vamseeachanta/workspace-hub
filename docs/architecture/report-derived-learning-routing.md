# Report-Derived Learning Routing (#2729)

| output_residency | Route | Rule |
|---|---|---|
| public_llm_wiki | public llm-wiki or public site corpus | Requires provenance, license, legal, sanitization, and owner-review gates. |
| domain_private_corpus | private/local llm-wiki raw data or internal domain corpus | Allowed for internal reusable learning only when source permission, provenance, legal, sanitization, and owner-review gates are recorded. |
| registered_client_private_corpus | registered client/private corpus | Allowed only inside the owning client/project boundary with source permission, provenance, legal, sanitization, and owner-review gates. |
| ignored_internal_run_artifact | no learning extraction by default | Preserve only as execution evidence. |
| no_preserve | discard | Do not route to a corpus. |

Report-derived learning must carry source-class and citation separation. Private/client raw or readable data cannot route directly into public llm-wiki.
