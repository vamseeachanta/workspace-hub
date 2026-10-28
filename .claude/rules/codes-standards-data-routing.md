# Codes and standards — agent rule

## Maintainer ruling (28 Oct 2026)

Source: the maintainer, in the Intake session on 28 Oct 2026, agreeing this text
line by line. His words: "Lift all the impediments. Lift all the blockers. Lift
all the gates for codes and standards. The text, the data sets, etc." and "we can
use originals as quotes and also reproduce in our engineering analysis and
reports - This is how engineering has done." This ruling replaces the earlier
source-and-destination checks, the 27 Oct 2026 direction and every
`extraction_policy: metadata-only` or rights-evidence gate on standards content.

### Internal work: no gates

- Agents read, search, quote and use everything in every code and standard we
  hold: the full text, tables, figures, equations and data sets.
- That covers analysis, checking, calculations, drafting, job specs and private
  data sets.
- No rights checks and no "metadata-only" limit. Legacy `extraction_policy` and
  `raw_copy_allowed` fields do not gate any operation.
- Copies, and tables extracted as data files, may sit in any private repo or on
  the ACE data store (`${ACE_DATA_ROOT}`). They can be copied between them and into job specs.
  Licensed originals may be kept in private Git, with large files in the ACE data store.

### Reports, client deliverables, website and newsletters

- Quote the clauses, equations, acceptance criteria, table values and chart data
  the work uses, citing the standard, edition and clause, table or figure number.
- Rebuild charts and tables rather than pasting scans where possible:
  - clean, interactive charts and well-laid-out tables, labelled
    "Reconstructed from [standard], Figure X";
  - each one checked against the original, with any digitising uncertainty stated.
- Make the codes readable: say plainly what each clause means for the design. The
  aim is that readers understand, are impressed and "make engineering enjoyable
  again".
- Kept out of public repos and pages: the original PDFs, and whole sections,
  chapters or documents.

### CFRs and other regulators

- Every job checks which CFR applies and cites the section. Examples: 30 CFR 250
  for offshore oil and gas; 49 CFR 192/195 for pipelines; 46 CFR and 33 CFR for
  vessels and the coast; CFR clauses that make a code mandatory by reference.
- CFR text is a US government work, so it can be quoted in full.
- The same check covers the other regulators where the work applies: Canada,
  Mexico, Brazil, the UK, Norway, the EU, Australia and others, with the ISO, CEN
  and CSA standards they call up.
- Ongoing background work whenever Codex has capacity: a code-to-regulation
  cross-reference in `llm-wiki` that grows with every job, resolving one region
  after another, and a guide that lets anyone prompting against our repository
  ecosystem find the governing regulation, regulator and standard.

## Placement

The [agent data handling contract](../../docs/architecture/agent-data-handling-contract.md)
governs ownership, retained originals and readiness records.

- Curated interpretation and extracted standards data belong in the private
  `llm-wiki` or the owning private project wiki. Confirm repository visibility
  before a write; a repository name is not proof.
- Qualified computational derivatives belong to the engineering owner and keep
  their source references (standard, edition, clause).
- Client-supplied and measured originals are retained in the owning private
  `data/<dataset>/raw/` with SHA-256 manifest entries and narrow ignore
  exceptions.

### Public-domain federal data (§6)

US government works (CFR text, BSEE, NOAA, NIST and similar federal data) may go
to the public `worldenergydata-wiki` with `visibility: public-federal-data`,
`license: public-domain` and `source_authority:` frontmatter, per
[`wiki-sibling-routing.md`](wiki-sibling-routing.md).

## Calculations

The [calc citation contract](calc-citation-contract.md) remains unchanged. A
citation or accessible wiki page does not establish computational qualification.
Consumers verify source version, criteria, units, freshness and intended-use
evidence. Preserve exact owner-issued catalog IDs rather than inventing
namespaces. Missing or stale evidence remains explicit.

Public-to-private references disclose their access limitation. Use neutral
owner-relative references (`wikis/<domain>/...`) from public repositories.
