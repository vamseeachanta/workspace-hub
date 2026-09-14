# Codes and standards data routing — agent rule

The [agent data handling contract](../../docs/architecture/agent-data-handling-contract.md)
governs ownership, retained originals, source-specific rights and readiness.
Private visibility does not grant reproduction, extraction or publication rights.

## Source and destination checks

1. Vendor-licensed standards and codes originals shall never be committed to Git,
   including private repositories. Keep the raw PDF at its licensed location.
   Preserve `raw_copy_allowed: false`, a `sources:` evidence reference, edition,
   source identity and authorized-access evidence. A public receipt must use an
   authorized opaque reference rather than expose a private raw path.
2. Authorized curated interpretation belongs in the private `llm-wiki` or owning
   project wiki. Qualified computational derivatives belong to the engineering
   owner and retain their source references. Confirm actual repository visibility
   before a write; neither a repository name nor historical visibility is proof.
3. Source-specific rights must cover each proposed operation, artifact, destination
   and audience. Retain applicable restrictive metadata such as
   `extraction_policy: metadata-only`. Do not drop restrictions because a wiki is
   private. Unknown rights deny copying or publication; record the gap and request
   the necessary evidence rather than treating private storage as permission.
4. Verbatim clauses, digitized tables, figures and worked examples are not blanket
   permitted categories. Attribution, withdrawn status, public availability or a
   general claim of fair use does not establish the required source-specific rights.
   This rule does not adjudicate licenses.
5. Public-domain or open-license routing requires evidence for the exact edition
   and material, including any private contributions. Only a verified authorized
   public destination may receive permitted content. No agency, publisher, date
   range or standard family is a substitute for that check.
6. Client-supplied and measured originals, excluding vendor-licensed standards,
   shall be retained in the owning private `data/<dataset>/raw/` with SHA-256
   manifest entries and narrow ignore exceptions. If rights, terms or storage
   prevent required retention, ingest acceptance remains blocked pending an owner
   decision; do not silently substitute an external pointer.

## Interpretation, synthetic material and calculations

Synthetic fixtures and original analysis must retain their provenance, limitations
and intended use. Those classifications alone establish neither unrestricted
publication nor engineering readiness; embedded source material retains its rights.
Methodology belongs to the appropriate curated owner subject to the same checks.

The [calc citation contract](calc-citation-contract.md) remains unchanged. A
citation or accessible wiki page does not establish computational qualification.
Consumers must verify source version, criteria, units, rights, freshness and
intended-use evidence. Preserve exact owner-issued catalog IDs rather than
inventing namespaces. Validation must explicitly enable date/time format checks;
a structurally valid evidence claim is not authenticated permission or readiness.
Missing or stale evidence remains explicit.

Public-to-private references must disclose their access limitation. Use neutral
owner-relative references where appropriate; never copy private source payloads
into a public issue, handoff or receipt merely to make a link readable.

Historical ingests are not automatically certified by this rule. Existing corpus
rights and legacy pointers require a separately scoped consumer audit; this
resource-authority slice performs no source ingest, migration or publication.
