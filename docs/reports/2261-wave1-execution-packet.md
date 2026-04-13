# Wave 1 (#2261) Execution Packet

Issue
- #2261 — feat(acma-codes): Wave 1 metadata-only wiki sweep — OCIMF (MEG 4), OCIMF, CSA
- URL: https://github.com/vamseeachanta/workspace-hub/issues/2261
- Parent: #2260
- Related blockers/context: #2227, #2245, #2207, #2216

Status
- Approval-safe execution prep only
- Do NOT implement until #2261 moves from `status:plan-review` to approved execution state

## 1. Exact directory inventory targets

Target roots under `/mnt/ace/acma-codes/`:

1. `OCIMF (MEG 4)/`
   - path: `/mnt/ace/acma-codes/OCIMF (MEG 4)`
   - current file count: 59
   - ext mix:
     - pdf: 51
     - docx: 2
     - jpg: 4
     - xlsx: 1
     - db: 1
   - sample files:
     - `Mooring Equipment Guidelines - MEG4.pdf`
     - `Mooring Lines/Mooring Lines-pp96-98.pdf`
     - `OCIMF MEG 4 Tables.xlsx`
     - `OCIMF MEG4 (Working Document).docx`

2. `OCIMF/`
   - path: `/mnt/ace/acma-codes/OCIMF`
   - current file count: 22
   - ext mix:
     - pdf: 20
     - txt: 1
     - xlsx: 1
   - sample files:
     - `OCIMF OVID OVPQ-Master-Full.pdf`
     - `OCIMF - 2008 - Mooring Equipment Guidelines.pdf`
     - `Figures/A10 ... Loaded Tanker.pdf`

3. `CSA/`
   - path: `/mnt/ace/acma-codes/CSA`
   - current file count: 5
   - ext mix:
     - pdf: 5
   - sample files:
     - `276.1-20 marine structures associated with LNG facilities.pdf`
     - `276.2-19 near-shoreline FLNG facilities.pdf`
     - `B625-13 Portable tanks for the transport of dangerous goods.pdf`
     - `CSA 22.1-12.pdf`
     - `Z276.18 LNG Production, storage, and handling.pdf`

## 2. Proposed execution mode

Mode
- Central single-agent execution

Why
- shared metadata/stub generation workflow
- common validation rules
- likely overlap in helper/reporting artifacts
- lower risk than parallel write streams for the first wave

## 3. Proposed path contract for future approved run

Owned paths
- `docs/reports/2261-wave1-*`
- `tmp/acma-wave1-*`
- the exact approved metadata-only wiki/stub output paths once approved
- the exact approved document-index provenance output paths once approved

Read-only paths
- `/mnt/ace/acma-codes/OCIMF (MEG 4)/`
- `/mnt/ace/acma-codes/OCIMF/`
- `/mnt/ace/acma-codes/CSA/`
- `data/document-index/index.jsonl`
- `data/document-index/standards-transfer-ledger.yaml`
- `docs/document-intelligence/standards-codes-provenance-reuse-contract.md`
- `docs/reports/acma-2227-metadata-only-interim.yaml`
- `docs/reports/acma-2227-metadata-only-wiki-stubs.md`

Forbidden paths before approval
- `docs/plans/README.md`
- production wiki content paths
- canonical document-index registry/index files
- any unrelated issue artifacts

## 4. Step-by-step execution checklist for approved run

1. Re-read #2261, #2260, #2227, #2245, #2207, #2216.
2. Inventory all files in the 3 target roots.
3. Split each bucket into document families:
   - parent/manual/guideline
   - figure/appendix fragment
   - spreadsheet/supporting file
   - non-promotable admin/noise
4. Create one normalized inventory manifest with per-file:
   - source path
   - normalized title
   - org
   - likely family
   - ext
   - visible metadata presence
   - blocker status
   - proposed action: stub / merge-into-parent / defer / reject
5. Generate metadata-only stub content for items approved for stub creation.
6. Keep all stubs explicitly marked:
   - `status: blocked-metadata-only`
   - `confidence: low`
   - `source_quality: title-and-metadata-only`
7. For fragment PDFs, prefer merge-into-parent manifests instead of one wiki page per fragment where appropriate.
8. Produce summary report for parent #2260.
9. Validate no clause-level or source-text-grounded claims were introduced.
10. Post completion summary on #2260 and per-issue update on #2261.

## 5. Proposed validation commands

Inventory and sanity
- `python - <<'PY' ... inventory roots ... PY`
- `find '/mnt/ace/acma-codes/OCIMF (MEG 4)' -type f | wc -l`
- `find '/mnt/ace/acma-codes/OCIMF' -type f | wc -l`
- `find '/mnt/ace/acma-codes/CSA' -type f | wc -l`

Metadata checks
- `pdfinfo <file>` for PDFs
- `pdffonts <file>` for suspicious PDFs where needed

Artifact validation
- confirm every generated stub includes:
  - blocked-metadata-only
  - low confidence
  - title-and-metadata-only
- grep/scan for disallowed language such as clause-level assertions

Suggested review checks
- no edits outside approved output paths
- no changes to production index/wiki files unless explicitly approved in-run
- no source-text claims without readable evidence

## 6. Proposed output artifacts for approved run

Recommended execution outputs:
- `docs/reports/2261-wave1-inventory.yaml`
- `docs/reports/2261-wave1-family-map.md`
- `docs/reports/2261-wave1-metadata-stubs.md`
- `docs/reports/2261-wave1-validation.md`
- optional temp scratch/manifests under `tmp/acma-wave1-*`

## 7. Risks / blockers / assumptions

Risks
- Fragment-heavy MEG4/OCIMF directories may cause page explosion if parent-child merge rules are not enforced.
- CSA PDFs remain DRM/encrypted and should remain metadata-only.
- Some filenames may be noisy enough to require manual normalization.

Known blockers carried into Wave 1
- #2227 / #2245 showed source-text extraction remains blocked for key CSA/OCIMF items.
- This wave must not attempt to silently convert metadata-only work into source-text promotion.

Assumptions
- The first approved wave should optimize for accurate inventory + safe stub structure, not volume.
- Parent-centric stub generation is preferable to fragment-per-file wiki proliferation for MEG4 figure sets.

## 8. Exact next step once #2261 is approved

1. Launch the approved execution prompt in a fresh tmux/Claude session.
2. Generate the Wave 1 inventory manifest first.
3. Stop if output path ownership becomes ambiguous; otherwise continue into stub generation and validation.
