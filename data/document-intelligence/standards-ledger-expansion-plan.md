# Standards Ledger Expansion Plan

> **Generated:** 2026-04-05
> **Task:** #1770 - Standards ledger expansion for 9 orgs

---

## 1. Current State & Objective

The `standards-transfer-ledger.yaml` is the authoritative source for tracking the integration of industry standards into the `digitalmodel` ecosystem. However, it is significantly out of sync with the actual files on disk.

-   **Files on Disk:** Over 26,000 standards documents are present in `/mnt/ace/O&G-Standards/` and the newly migrated DDE standards folders.
-   **Ledger Entries:** Only 425 standards are currently tracked in the ledger.

This discrepancy means that the vast majority of our standards library is not formally managed, versioned, or integrated into our automated engineering workflows.

The objective of this plan is to dramatically expand the ledger to include nine key standards organizations, bringing thousands of documents under formal management.

## 2. Target Organizations for Expansion

The following nine organizations have been identified for inclusion in the ledger. Six were recently migrated from the DDE remote drive, and three (SNAME, OnePetro, BSI, Norsok) were already on disk but never added to the ledger.

| Org.    | Full Name                                 | Source                                  | Est. Files | Status          |
| ------- | ----------------------------------------- | --------------------------------------- | ---------- | --------------- |
| **ASME**  | American Society of Mechanical Engineers  | Migrated from DDE                       | 100+       | Not in Ledger   |
| **AWS**   | American Welding Society                  | Migrated from DDE                       | 50+        | Not in Ledger   |
| **NACE**  | National Assoc. of Corrosion Engineers    | Migrated from DDE                       | 80+        | Not in Ledger   |
| **ASCE**  | American Society of Civil Engineers       | Migrated from DDE                       | 70+        | Not in Ledger   |
| **HSE**   | Health & Safety Executive (UK)            | Migrated from DDE                       | 40+        | Not in Ledger   |
| **IEC**   | International Electrotechnical Commission | Migrated from DDE                       | 60+        | Not in Ledger   |
| **SNAME** | Society of Naval Architects & Marine Eng. |`/mnt/ace/O&G-Standards/`                | 145        | Not in Ledger   |
| **OnePetro**| OnePetro                                 |`/mnt/ace/O&G-Standards/`                | 94         | Not in Ledger   |
| **BSI**   | British Standards Institution             |`/mnt/ace/O&G-Standards/`                | 76         | Not in Ledger   |
| **Norsok**| Norsok                                    |`/mnt/ace/O&G-Standards/`                | 9         | Not in Ledger   |

## 3. Implementation Plan

We will use a semi-automated approach to bulk-populate the ledger.

### Step 1: File Inventory Script

A new script, `scripts/data/standards/generate_ledger_candidates.py`, will be created. This script will:

1.  **Scan Directories:** Recursively scan the directories for each of the nine target organizations within `/mnt/ace/O&G-Standards/`.
2.  **Extract Metadata:** For each PDF found, it will attempt to extract the standard's name, number, and edition from the filename. It will use regex patterns tailored to the common naming conventions of each organization (e.g., `ASME-B31.3-2020.pdf`, `NACE_SP0177_2014.pdf`).
3.  **Generate Candidate YAML:** The script will output a YAML file (`standards-ledger-candidates.yaml`) containing a list of candidate entries. Each entry will be a stub, pre-populated with the extracted metadata.

**Candidate YAML Entry Example:**

```yaml
- id: NACE-SP0177-2014
  title: NACE SP0177-2014 - Mitigation of Alternating Current and Lightning Effects on Metallic Structures and Corrosion Control Systems
  org: NACE
  domain: cathodic-protection # Default based on parent folder
  doc_paths:
    - /mnt/ace/O&G-Standards/NACE/NACE_SP0177_2014.pdf
  status: reference # Default status
  wrk_id: null
  repo: digitalmodel
  modules: []
  implemented_at: null
  notes: 'Auto-generated from file scan.'
```

### Step 2: Manual Review and Augmentation

The auto-generated `standards-ledger-candidates.yaml` will be reviewed by an engineer.

1.  **Validation:** The engineer will verify the accuracy of the extracted titles and IDs.
2.  **Domain Assignment:** While the script can assign a default domain based on the organization (e.g., NACE -> cathodic-protection), the engineer will refine these assignments.
3.  **Prioritization:** The engineer can optionally change the `status` from `reference` to `wrk_captured` for high-priority standards, which will flag them for future integration work.

### Step 3: Merging with the Master Ledger

Once the candidate file is reviewed and finalized, a simple script will merge its contents into the main `data/document-index/standards-transfer-ledger.yaml` file, checking for and avoiding the creation of duplicates.

## 4. Expected Outcome

-   The number of standards tracked in the `standards-transfer-ledger.yaml` will increase from 425 to over 1,000.
-   All documents from the nine target organizations will have a corresponding ledger entry, making them visible to the `digitalmodel` management and automation systems.
-   A repeatable, script-driven process will be established for adding new batches of standards to the ledger in the future, reducing manual effort and ensuring consistency.
