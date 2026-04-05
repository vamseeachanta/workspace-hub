# Marine Subdomain Taxonomy and Classification Strategy

> **Generated:** 2026-04-05
> **Task:** #1653 - Marine subdomain taxonomy to reduce unclassified under 10%

---

## 1. Problem Statement

The 'Marine' domain is a broad category that encompasses a wide range of engineering disciplines. Currently, of the approximately 32,000 documents classified as 'Marine', a significant portion (**33%**) remains in a generic, unclassified bucket. This lack of granularity hinders effective knowledge retrieval and expert system routing. The objective is to create a detailed subdomain taxonomy to classify this content and reduce the 'unclassified' count to below 10%.

## 2. Marine Subdomain Taxonomy

The following nine subdomains provide a comprehensive breakdown of the marine engineering field. For each, we provide an estimated document count (out of the ~10,560 currently unclassified), representative keywords, and clear classification criteria.

| Subdomain           | Est. Count | Keywords                                                                                                               | Classification Criteria                                                                                                                         |
| ------------------- | ---------- | ---------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------- |
| **Hydrodynamics**   | 2,000      | `hydrodynamics`, `diffraction`, `radiation`, `wave`, `current`, `seakeeping`, `RAO`, `potential flow`, `CFD`, `model test`, `AQWA` | Documents focused on the interaction of waves and currents with floating or fixed structures. Includes potential flow and CFD analysis, and model testing. |
| **Mooring**           | 1,800      | `mooring`, `catenary`, `turret`, `spread mooring`, `anchor`, `hawser`, `fairlead`, `static`, `dynamic`, `OrcaFlex`, `MoorPy`   | Documents related to the design and analysis of mooring systems for floating vessels, from static catenary calculations to dynamic time-domain simulations. |
| **Risers & Umbilicals** | 1,500      | `riser`, `umbilical`, `flowline`, `flexible`, `steel catenary riser (SCR)`, `top tensioned riser (TTR)`, `dynamic`, `cross-section` | Documents concerning the design, analysis, and components of risers and umbilicals used to transport fluids and provide control to subsea wells. |
| **VIV & Fatigue**   | 1,200      | `VIV (Vortex-Induced Vibrations)`, `fatigue`, `S-N curve`, `rainflow counting`, `inline`, `cross-flow`, `suppression`, `strakes` | Documents focused on the analysis and mitigation of vortex-induced vibrations and the resulting fatigue damage on slender structures like risers and pipelines. |
| **Installation**      | 1,000      | `installation`, `vessel`, `crane`, `lifting`, `rigging`, `deployment`, `SURF`, `heavy lift`, `J-Lay`, `S-Lay`, `float-over`  | Documents describing the methods, equipment, and procedures for installing offshore structures, subsea hardware, and pipelines.                     |
| **Marine Operations** | 900        | `marine operations`, `logistics`, `SIMOPS`, `towing`, `station keeping`, `DP (Dynamic Positioning)`, `ROV`, `procedures` | Documents related to the planning and execution of offshore activities, including vessel movements, simultaneous operations, and ROV interventions.       |
| **Vessels & Floaters** | 800        | `vessel`, `ship`, `FPSO`, `SPAR`, `TLP`, `semi-submersible`, `naval architecture`, `stability`, `hydrostatics`, `ballast`  | Documents detailing the design, characteristics, and systems of offshore vessels and floating platforms. Covers general naval architecture aspects. |
| **Subsea & Pipelines**| 800        | `subsea`, `pipeline`, `PLET`, `manifold`, `tie-in`, `on-bottom stability`, `buckling`, `trenching`, `burial`            | Documents focused on seabed hardware, pipeline design, and subsea field layout. Differentiated from 'Risers' by its focus on elements on the seabed. |
| **Other**             | 560        | `metocean`, `surveys`, `acoustics`, `ice`, `regulatory`, `DP system`, `power generation`                                 | Documents that cover supporting topics or specialized niches within the marine domain that do not fit neatly into the other categories.             |

## 3. Classification Strategy

A multi-pass keyword-based approach will be used to classify the ~10,560 unclassified marine documents.

1.  **Script Implementation:**
    *   The logic will be integrated into the new `scripts/data/doc_intelligence/unified_taxonomy_classifier.py`.
    *   The classifier will first identify all documents with the top-level 'Marine' classification.
    *   It will then specifically target those documents that do *not* have a subdomain assigned.

2.  **Keyword Matching Algorithm:**
    *   The script will load the subdomain keywords from the `unified-taxonomy.yaml` file.
    *   For each unclassified document's summary text, it will perform a keyword search.
    *   A simple scoring system will be used: each keyword hit increments the score for its corresponding subdomain.
    *   The document will be assigned to the subdomain with the highest score, provided the score exceeds a minimum threshold (e.g., at least 2 keyword hits).

3.  **Handling Ambiguity:**
    *   Some documents may contain keywords from multiple subdomains (e.g., a riser analysis document might mention both `riser` and `fatigue`).
    *   In the initial implementation, the document can be assigned multiple subdomain labels if their scores are close (e.g., within 20% of each other). This allows for cross-categorization.
    *   A manual review of a sample of multi-label documents will be performed to refine the keyword lists and reduce ambiguity.

4.  **Iterative Refinement:**
    *   The classification process is not a one-time event. After the initial pass, a report will be generated showing the new distribution.
    *   The remaining unclassified documents (expected to be < 10%) will be manually reviewed.
    *   Based on this review, the keyword lists in `unified-taxonomy.yaml` will be updated to capture more documents or to resolve classification conflicts.
    *   The classifier will be re-run until the number of unclassified documents is acceptably low.

## 4. Expected Outcome

-   At least 9,500 of the 10,560 currently unclassified marine documents will be assigned to one of the nine subdomains.
-   The percentage of unclassified marine documents will be reduced from 33% to **less than 10%**.
-   The `unified-taxonomy.yaml` will be a mature, validated resource for marine domain classification.
-   Search and retrieval of marine-specific information will be significantly improved.
