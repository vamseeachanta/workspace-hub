---
name: license-verification-via-crossref-doab-metadata-apis
description: "When a publisher page (Springer, Elsevier, OAPEN handle) is SSO-gated or socket-closing under WebFetch, use CrossRef API for journal articles and DOAB API for open-access books to verify license terms — both zero-auth and authoritative"
metadata: 
  node_type: memory
  type: reference
  originSessionId: 09c433d6-54e9-4f99-8d70-36dcd1ae886b
---

For license-verification work (e.g., llm-wiki [#96](https://github.com/vamseeachanta/llm-wiki/issues/96) defer-row triage), publisher landing pages are often unreachable via direct WebFetch — Springer Nature Link redirects to `idp.springer.com/authorize?...` SSO, OAPEN handle pages socket-close intermittently, Elsevier ScienceDirect requires institutional auth. Retrying the rendered pages burns time without yielding evidence.

**Two zero-auth metadata APIs cover the most common publisher cases:**

1. **CrossRef API for journal articles** — `https://api.crossref.org/works/<DOI>`. Returns JSON including a `message.license` array with each license object carrying `URL` (the CC variant), `content-version` (am/vor), and `start.date-time` (effective date). Example query for the JPEPT 2017 Chandmari article: `curl -sL 'https://api.crossref.org/works/10.1007/s13202-017-0373-8'` → `license[0].URL = "http://creativecommons.org/licenses/by/4.0"`. Authoritative for any DOI deposited at CrossRef (Springer, Wiley, Elsevier OA journals, etc.).

2. **DOAB metadata API for open-access books** — `https://directory.doabooks.org/rest/search?query=<term>&expand=metadata`. Returns JSON with `metadata[]` entries; look for `dc.rights` ("open access"), `publisher.oalicense` (publisher policy quote with CC variant), and `dc.rights.license`. Example query: `curl -sL 'https://directory.doabooks.org/rest/search?query=geology+kuwait&expand=metadata'` → `publisher.oalicense = "Springer Nature books are published under the Creative Commons Attribution 4.0 (CC BY) license"`. DOAB is the federated registry that OAPEN feeds into; using DOAB bypasses OAPEN's handle-page connectivity issues.

**When to use:**
- WebFetch on the publisher's article/book page returns SSO redirect, socket close, or 404 → fall back to the metadata API
- Need legal-grade evidence (license URL + effective date) rather than a WebSearch synthesis claim
- Doing per-row license verification across N candidates (the API is much faster than rendering pages)

**Verification chain for #96 (2026-05-17):** A28 (Springer JPEPT) verified via CrossRef in ~1 sec after Springer SSO blocked direct fetch; A29 (OAPEN Geology of Kuwait) verified via DOAB after 2 OAPEN socket failures. Both yielded definitive CC-BY-4.0 with `creativecommons.org/licenses/by/4.0/` URLs.

**Caveats:**
- CrossRef license records are publisher-deposited; if a publisher doesn't deposit license metadata, the field will be missing — that's a real signal (probably not CC-licensed), not a tool failure
- arXiv has its own per-paper license rendered on the abs page; WebFetch on the arXiv abs URL works reliably (verified for A25 + A26) — no need for metadata API
- For ResearchGate / academic-network platforms: license metadata is not authoritative; always go back to the canonical publisher record
