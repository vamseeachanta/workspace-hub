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

## Maintainer direction for internal use (27 Oct 2026)

The maintainer authorizes internal reading and engineering interpretation of
standards copies already accessible within the private ecosystem. This direction
permits consulting the source and producing original engineering analysis; it does
not grant blanket permission to extract, reproduce or redistribute source content.
Existing source-specific restrictions take precedence over this general direction:
metadata-only extraction remains metadata-only, and other operations require their
own source-specific rights evidence. Unknown rights do not authorize extraction.

Reading authorization does not grant storage authorization. Copies at a licensed
location may be referenced from private repositories without retaining the original
in Git. The governing contract and descriptor schema remain unchanged: licensed
originals require `licensed_location` and `raw_copy_allowed: false`; `private_git`
is rejected. Any original already retained in Git remains an unresolved storage
exception requiring a separate disposition; internal reading does not certify its
retention. This direction authorizes no copying, migration or deletion of originals.

Public outputs cite clause numbers only, never source text, tables or figures.
Private access does not authorize publication of the copies or their contents.

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
