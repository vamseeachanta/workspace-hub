# #2227 Issue-Ready Comment Drafts

## Draft A — metadata-only interim note

## Metadata-only interim note for blocked #2227 targets

I was able to collect title-level and PDF/catalog metadata for the three blocked targets, but not readable source text.

### 1) OCIMF-TANDEM-MOORING
- Title: `OCIMF Tandem Mooring and Offloading Guidelines for Conventional Tankers at FPSO Facilities`
- Org: `OCIMF`
- Domain: `marine`
- Local PDF metadata:
  - Pages: `128`
  - Encrypted: `no`
  - Creator/Producer: `Xerox WorkCentre 7655`
  - CreationDate: `2010-03-04`
- Bounded metadata-only summary:
  - `OCIMF guidance focused on tandem mooring and offloading operations involving conventional tankers at FPSO facilities.`

### 2) CSA-Z276.1-20
- Title: `CSA Z276.1-20 Marine Structures Associated with LNG Facilities`
- Org: `CSA`
- Domain: `marine`
- Local PDF metadata:
  - Alternate visible title: `CSA SPE-276.1:20, Design requirements for marine structures associated with LNG facilities (DRMS)`
  - Author: `CSA Group`
  - Pages: `55`
  - Encrypted: `yes (AES / Vitrium-secured)`
- Bounded metadata-only summary:
  - `CSA standard concerning design requirements for marine structures associated with LNG facilities.`

### 3) CSA-Z276.18
- Title: `CSA Z276.18 LNG Production, Storage, and Handling`
- Org: `CSA`
- Domain: `marine`
- Local PDF metadata:
  - Pages: `214`
  - Encrypted: `yes (AES / Vitrium-secured)`
  - descriptive title/subject metadata not exposed in the current file beyond the canonical title
- Bounded metadata-only summary:
  - `CSA standard related to LNG production, storage, and handling operations.`

### Important limitation
These are **metadata-only summaries**, not source-text-grounded summaries. They should be treated as interim placeholders only and must not be used to assert clause-level technical requirements.

### Current status
- `docs/reports/acma-wiki-unblock-2245-handoff.yaml` still reports `ready_for_2227: false`
- `docs/reports/acma-2227-metadata-only-interim.yaml` captures the structured metadata-only handoff
- #2227 remains blocked for full wiki-promotion work until readable source text is available from an authorized/legitimate source

## Draft B — stronger blocker diagnosis

## Stronger blocker diagnosis

I tried both local extraction and online discovery.

Result:
- no legitimate open, non-DRM, fully readable public-web copy surfaced for the 3 target docs
- CSA PDFs appear Vitrium-secured / encrypted
- current machine/toolchain cannot render usable readable content from those CSA files
- OCIMF file is not encrypted, but sampled extraction/rendering here still did not yield usable summary text

Most likely unblock paths:
1. authorized readable access on another machine/platform
2. non-DRM source PDFs
3. manually curated summaries from an authorized readable source

Structured artifact for the metadata-only fallback:
- `docs/reports/acma-2227-metadata-only-interim.yaml`
