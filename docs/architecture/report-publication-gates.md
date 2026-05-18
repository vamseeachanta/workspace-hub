# Report Publication Gates (#2729)

Before any report artifact is delivered to a client-facing, public, or chatbot/query surface, require:

1. Evidence bundle complete: source manifest, command manifest, validation result, checksum, review verdict, output residency, and promotion decision.
2. Promotion gate set for public or more-public routing: `provenance`, `license`, `legal`, `sanitization`, and `owner-review`.
3. Canonical legal scan: `scripts/legal/legal-sanity-scan.sh --diff-only` using `.legal-deny-list.yaml`.
4. Sanitization gate for client/public surfaces: remove client identifiers, secrets, private repo paths, raw source excerpts, and unapproved proprietary data.
5. Output-residency compatibility: artifact cannot be more public than input/corpus without explicit promotion gates.
6. Chatbot scope/freshness disclosure when an index, embedding store, or query surface is created.

This contract intentionally uses the existing legal scan and does not create another denylist.
