# Canonical client review projections

The private client repository owns the authoritative record. This bounded adapter renders Space Markdown, dashboard HTML and an identical HTML index from one committed JSON record. It does not implement an ingestion service or automatic synchronization.

Use existing client-wiki registry, source-rights, audience and coordination controls before selecting a record. Git origin matching proves repository identity only; it does not prove private visibility or authorize publication. A branch commit receipt does not imply merge or client release.

The record contains schema, client, owner_repository, title, checked_at, coverage, hold, sections and common_resources. The synthetic test fixture documents the exact shape. The normalized record determines the content version, including coverage and hold. Common resources appear as the final compact bullet.

Run the module with the existing environment through uv run, without dependency installation. Build arguments are: build OWNER_RECORD --owner-root OWNER_ROOT --out NEW_OWNER_DIRECTORY. Feedback arguments are: feedback OWNER_RECORD SAVED_JSON --owner-root OWNER_ROOT --out NEW_OWNER_PROPOSAL_JSON.

Both outputs must stay inside the verified owning repository. Existing destinations, linked paths and Git metadata paths are rejected. The build writes record.json, space.md, dashboard.html, index.html and a final hash manifest. A partial directory without the manifest is not an accepted bundle.

Reuse an existing PDF renderer with an isolated browser profile and sandbox enabled. Do not download a browser or dependencies automatically. After rendering dashboard.pdf, record_pdf checks actual page count, canonical text, content version, link labels and hyperlink targets before writing a new receipt. verify_bundle re-extracts the PDF rather than trusting that receipt alone.

Review Save and Load are explicit user actions. Save creates version-bound JSON; the UI does not assert disk persistence or autosave. Loading stale, duplicate-field or invalid JSON preserves current entries. Replacing unsaved entries requires confirmation. The feedback CLI returns a proposed change inside the owner repository and does not apply factual edits or commit them.

Before publication, use verify_bundle with for_publication=True and the expected owning repository. Held records, unbound ownership and changed source commits fail this technical gate. Passing it does not grant audience or source authorization. Publish only to an authorized new destination with hash readback; update Space through guarded native operations that preserve user edits and instructions. Claim matching surfaces only after actual readback.
