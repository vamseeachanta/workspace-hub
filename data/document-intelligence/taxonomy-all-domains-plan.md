# Plan for Unified Engineering Domain Taxonomy

> **Generated:** 2026-04-05
> **Task:** #1655 - Apply taxonomy classifier to all domains

---

## 1. Objective

The goal is to create a single, unified taxonomy for classifying all engineering documents within the workspace. This will replace ad-hoc, domain-specific classification schemes (like the one for the 'marine' domain) with a consistent, centrally-managed system. This taxonomy will be the backbone for:

-   Automated document routing and classification.
-   Improved search and discovery of technical information.
-   Gap analysis of our knowledge base.
-   Feeding domain-specific documents to specialized AI models and tools.

## 2. Proposed Unified Taxonomy

This taxonomy expands upon the existing ad-hoc `marine` domain classification and incorporates other critical engineering disciplines identified across the workspace. Each domain includes a set of representative keywords and classification criteria.

| Domain              | Sub-domains / Keywords                                                                                                     | Classification Criteria                                                                                                                                  |
| ------------------- | -------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Pipeline**        | `pipeline`, `riser`, `flowline`, `pigging`, `subsea`, `on-bottom stability`, `upheaval buckling`, `flow assurance`, `slugging`, ` flexibles`, `umbilical` | Documents concerning the design, analysis, installation, and operation of subsea and onshore pipelines, risers, and flowlines. Includes fluid transport and integrity management. |
| **Structural**      | `structural`, `fatigue`, `VIV`, `FEA`, `S-N curve`, `SCF`, `hydrodynamics`, `global analysis`, `steel`, `concrete`, `foundation`, `jacket`, `topside` | Documents related to the design and analysis of fixed and floating structures, including strength, fatigue, and dynamic response. Covers both steel and concrete structures. |
| **Materials**       | `materials`, `corrosion`, `welding`, `NDT`, `metallurgy`, `sour service`, `H2S`, `cladding`, `cathodic protection`, `coatings`, `polymers` | Documents focusing on material selection, specification, testing, and degradation. Includes topics on welding procedures, non-destructive testing, and corrosion control. |
| **Process**         | `process`, `P&ID`, `PFD`, `separation`, `gas treating`, `LNG`, `refining`, `distillation`, `heat exchanger`, `pump`, `compressor`, `thermodynamics` | Documents describing hydrocarbon processing facilities, equipment, and chemical processes. Includes process flow diagrams and piping and instrumentation diagrams. |
| **Geotechnical**    | `geotechnical`, `soil`, `foundation`, `pile`, `anchor`, `suction caisson`, `seabed`, `slope stability`, `geohazards`, `spudcan`   | Documents dealing with soil mechanics, foundation design, and seabed interaction. Includes analysis of offshore foundations, anchors, and geohazards.                  |
| **Reservoir**       | `reservoir`, `petroleum`, `EOR`, `drilling`, `well`, `completion`, `simulation`, `permeability`, `porosity`, `hydrocarbon`, `geology` | Documents related to subsurface geology, hydrocarbon reservoirs, drilling and completion technology, and reservoir simulation and management.                         |
| **Naval Arch.** | `naval architecture`, `hydrostatics`, `stability`, `vessel`, `ship`, `FPSO`, `mooring`, `seakeeping`, `RAO`, `model testing` | Documents concerning the design, construction, and operation of marine vessels. Includes topics on stability, seakeeping, mooring, and propulsion.              |

## 3. Implementation Plan

1.  **Centralize Taxonomy Definition:**
    *   Create a single YAML file in `data/document-intelligence/unified-taxonomy.yaml` to store the hierarchy, keywords, and criteria defined above. This will serve as the single source of truth.

2.  **Develop a Unified Classifier Script:**
    *   Create a new script: `scripts/data/doc_intelligence/unified_taxonomy_classifier.py`.
    *   This script will read the `unified-taxonomy.yaml` file.
    *   It will iterate through documents in the master index (`data/document-index/index.jsonl`).
    *   Using the document's summary (from Phase B extraction), it will apply a classification algorithm (e.g., keyword matching, TF-IDF, or a more advanced LLM-based classifier) to assign one or more domain labels.

3.  **Refactor Existing Classifiers:**
    *   Deprecate the existing `scripts/document-intelligence/marine-taxonomy-classifier.py`.
    *   Update any workflows or scripts that depend on the old classifier to use the new unified classifier.

4.  **Testing and Validation:**
    *   Create a corresponding test file `tests/data/doc_intelligence/test_unified_taxonomy_classifier.py`.
    *   The test will load a set of sample document descriptions and assert that the classifier assigns the correct domain labels based on the YAML definition.

5.  **Execution and Reporting:**
    *   The unified classifier will be run as part of the document intelligence pipeline (e.g., as a a new "Phase C2" step).
    *   The script will output a report, similar to `marine-taxonomy-report.md`, but covering all domains. This report will show the distribution of documents across the new taxonomy and highlight any remaining unclassified items.

## 4. Next Steps

-   This plan will be implemented to create the foundational YAML file and the classification script.
-   The initial run will focus on a subset of documents to validate the keyword lists and classification logic.
-   The keywords and criteria will be iteratively refined based on the classification results.
