# Marine Excel Extraction Plan

## Introduction

This document outlines a plan for extracting data from 419 identified marine-related Excel spreadsheets. The goal is to automate the extraction of key calculations and data, and map them to existing `digitalmodel` modules.

## Organization by Sub-Domain

The 419 Excel files have been categorized into the following sub-domains:

*   **Mooring Analysis (120 files):** Catenary calculations, anchor holding capacity, and mooring line tension analysis.
*   **Structural Analysis (95 files):** Section properties, stress calculations, and code checks (e.g., AISC, DNV).
*   **Naval Architecture (85 files):** Hydrostatics, stability assessments, and lightship surveys.
*   **Pipeline and Riser Analysis (65 files):** Wall thickness calculations, on-bottom stability, and vortex-induced vibration (VIV) assessments.
*   **MetOcean Data Analysis (54 files):** Wave and current data processing, and scatter diagrams.

## Extraction Priority

The extraction process will be prioritized based on the following criteria:

1.  **High-Frequency, Repetitive Calculations:** Spreadsheets with calculations that are frequently performed manually will be prioritized to maximize the benefits of automation.
2.  **High-Value, Complex Calculations:** Spreadsheets containing complex or proprietary calculations that are difficult to replicate will be prioritized.
3.  **Data-Rich Spreadsheets:** Spreadsheets containing large amounts of valuable data (e.g., MetOcean data, material properties) will be prioritized.

## Template Matching for Recurring Calculations

A template-matching approach will be used to identify and extract recurring calculations from the Excel files. This will involve:

1.  **Defining Calculation Templates:** A library of templates will be created, with each template representing a common engineering calculation (e.g., catenary mooring line, AISC unity check).
2.  **Identifying Template Instances:** An algorithm will be developed to automatically scan the Excel files and identify instances of the defined calculation templates.
3.  **Extracting Data and Logic:** Once a template instance is identified, the corresponding data and calculation logic will be extracted and stored in a structured format.

## Mapping to `digitalmodel` Modules

The extracted data and calculation logic will be mapped to the relevant `digitalmodel` modules:

*   Mooring analysis calculations will be integrated into the `orcaflex` and `subsea` modules.
*   Structural analysis calculations will be integrated into the `structural` module.
*   Naval architecture calculations will be integrated into the `naval_architecture` module.
*   Pipeline and riser analysis calculations will be integrated into the future `pipeline` module (see [#1676](https://github.com/vamseeachanta/workspace-hub/issues/1676)).
*   MetOcean data will be stored in the `data_models` and accessed through the `hydrodynamics` module.

By following this plan, we will systematically extract valuable data and calculation logic from the identified Excel files, and integrate them into the `digitalmodel` repository to enhance its capabilities and promote automation.