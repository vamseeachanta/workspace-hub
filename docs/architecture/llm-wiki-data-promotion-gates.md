# llm-wiki Data Promotion Gates — Issue #2727

The promotion model is intentionally staged:

```text
inputs → execution → reports/chatbots → curated output learnings → appropriate llm-wiki/corpus tier
```

## Gates

1. **Raw/private llm-wiki staging** — raw/private llm-wiki staging is private by default. It can contain extracted notes, metadata, or candidate learnings from private sources, but not public publication artifacts.
2. **Review and sanitization** — remove client identifiers, raw paths, secrets, licensed text, and unsupported claims. Preserve citations/provenance.
3. **Residency decision** — choose `llm-wiki-private`, `llm-wiki-public`, or report-scoped output based on source class.
4. **Public llm-wiki publication** — only public-safe, license-cleared, cited derivatives may enter the public llm-wiki.
5. **Client/private corpus publication** — client-specific derivatives route to private targets such as `<client-private-wiki-root>`.

## Report and query surfaces

client-facing HTML, limited PDFs, and chatbot surfaces are not automatic data-layer publications. They are downstream report-layer outputs that must carry corpus scope, freshness, and output residency. A chatbot over mixed public/private corpora is private unless every corpus source is public-safe.

## Deny-by-default examples

- Private D-L1 source → public llm-wiki: deny.
- Licensed standards PDF text → public llm-wiki: deny unless only cited, non-reproduced facts are used and legal/source review passes.
- Public BSEE/API metadata → public llm-wiki: allow only after source/license/freshness checks.
- Client raw data → `<client-private-wiki-root>`: allow only as private derivative with access controls and sanitization.

## Related policy references

- `docs/BUSINESS_BRAIN.md`
- `docs/DATA_RESIDENCE_POLICY.md`
- `.legal-deny-list.yaml`
