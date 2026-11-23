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
