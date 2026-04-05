# Mount Drive Resource Audit

> **Generated:** 2026-04-05
> **Task:** #1776 - Mount Drive Resource Audit

---

## 1. Resource Landscape: Local vs. Remote

Our engineering knowledge base is spread across two primary locations: a local, well-structured drive (`/mnt/ace`) and a remote, legacy drive (`/mnt/remote/ace-linux-2/dde`).

### 1.1. Local Drive (`/mnt/ace`)

- **Description:** The primary, actively managed storage for engineering data.
- **Contents:**
    - **`/mnt/ace/O&G-Standards/`**: Main standards library with 26,884 files, semantic search capabilities, and active OCR/indexing.
    - **`/mnt/ace/docs/`**: Over 119 project archives and a massive collection of 38,526 conference papers.
    - **Client Repos:** Active project work for clients like 2H, Doris, and Saipem.
    - **Open-Source Repos:** Clones of key engineering tools like `Capytaine`, `OpenFAST`, and `WEC-Sim`.
- **Status:** Partially indexed by the workspace-hub pipeline (1,033,933 documents). Well-documented in `mount-drive-knowledge-map.md`.

### 1.2. Remote Drive (`/mnt/remote/ace-linux-2/dde`)

- **Description:** A legacy SSHFS mount from `ace-linux-2` containing historical data.
- **Contents:**
    - **`0000 O&G/`**: A legacy standards collection containing critical organizations (**ASME, AWS, NACE, ASCE, IEC**) not found on the local `/mnt/ace` drive.
    - **`documents/`**: Over 99 historical project folders, with partial overlap with the local drive.
    - **`Literature/`**: A large collection of engineering textbooks and industry papers.
    - **`Orcaflex/`**: Unique OrcaFlex models for projects like drilling riser development.
    - **`FreeSpanVIVFatigue/`**: 13 proprietary MATLAB scripts for pipeline VIV fatigue analysis, a candidate for clean-room porting.
- **Status:** **CRITICAL GAP.** This drive is not indexed, not registered in the `mounted-source-registry.yaml`, and its contents are largely invisible to our data intelligence pipelines.

---

## 2. Identified Gaps

Based on the `mount-drive-knowledge-map.md` and `dde-drive-catalog.md`, the following critical gaps have been identified:

1.  **DDE Drive Invisibility:** The entire 2.8 TB remote DDE drive is a black spot. Its unique standards, project files, and literature are not searchable or usable by our automated systems.
2.  **Conference Paper Indexing:** 38,526 high-value conference papers (OMAE, OTC, DOT) on the local drive are not indexed, representing a massive untapped resource of domain knowledge.
3.  **Standards Consolidation:** Critical engineering standards (ASME, NACE, AWS) exist only on the remote DDE drive, creating a fractured and incomplete standards library.
4.  **Cross-Drive Redundancy:** There is a known but unquantified overlap between the project archives on the local and remote drives. A deduplication audit is required to identify unique, valuable files on the DDE drive.

---

## 3. Legal Scan Status

- **Policy:** The `MEMORY.md` file confirms a mandatory policy for legal scans on all document intelligence work, with a specific exclusion for catalogs.
- **Execution:** A search for `legal` across the workspace returns numerous files, including configuration and log files, but **no consolidated legal scan audit report was found.**
- **Assessment:** While the tooling and policy exist, the status of a comprehensive legal scan across the mount drives is **unverified**. It is unclear if a full scan has been performed on `/mnt/ace` or the remote DDE drive. Given the presence of proprietary MATLAB code (`FreeSpanVIVFatigue`) and extensive third-party standards, this is a significant risk.

---

## 4. Bridging Recommendations

To bridge these gaps and integrate our disparate knowledge sources, the following actions are recommended, aligning with the `resource-intelligence-action-plan.md`:

1.  **Register DDE Drive (Immediate):** Add the `dde_standards_remote`, `dde_literature_remote`, and `dde_engineering_remote` sources to `data/document-index/mounted-source-registry.yaml`. This is the first step to making the drive's contents discoverable. (Completed under #1756).

2.  **Migrate Critical Standards (High Priority):** `rsync` the essential standards organizations (ASME, AWS, NACE, ASCE, HSE, IEC) from the remote DDE drive to `/mnt/ace/O&G-Standards/`. This will consolidate our standards library into a single, searchable location. (Completed under #1758).

3.  **Index Conference Papers (High Priority):** Execute the Phase A indexing pipeline on the `/mnt/ace/docs/conferences/` directory to bring all 38,526 papers into the master document index.

4.  **Perform Cross-Drive Deduplication Audit (Medium Priority):** Run a SHA-256 hash-based audit to compare files between `/mnt/ace/docs/` and `/mnt/remote/ace-linux-2/dde/documents/`. The goal is to identify the unique project files on the DDE drive that need to be indexed.

5.  **Conduct Full Legal Sanity Scan (Medium Priority):** Execute the `legal-sanity-scan.sh` script across both `/mnt/ace` and `/mnt/remote/ace-linux-2/dde` and generate a formal audit report. This is crucial to identify and isolate proprietary or legally constrained content *before* it is processed by the indexing pipelines.

6.  **Index Unique DDE Content (Medium Priority):** Once the deduplication audit is complete, run the Phase A indexing pipeline on the list of unique, high-value files and directories on the DDE drive.
