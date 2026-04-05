# Large Workbook Streaming Plan

## Introduction

This document outlines a plan to process four large Excel workbooks (over 15MB) that were skipped by the initial extraction pipeline. These workbooks are:

*   `SO-01-23-111_DP_Capability_Analysis.xlsx` (25 MB)
*   `GOM_Mooring_Design_Criteria.xlsx` (18 MB)
*   `FPSO_Riser_Fatigue_Analysis_Results.xlsx` (32 MB)
*   `Subsea_Field_Layout_and_Architecture.xlsx` (21 MB)

## Streaming Mode Approach

A streaming mode approach, using a library like `openpyxl` with its `read_only` and `lazy` modes, will be employed to handle these large files. This approach will allow us to read and process the workbooks worksheet by worksheet, and cell by cell, without loading the entire file into memory. This will prevent out-of-memory errors and enable efficient processing of the large datasets.

## Memory-Efficient Extraction

The extraction process will be designed to be memory-efficient:

*   **Iterative Processing:** Data will be read and processed in chunks, rather than all at once.
*   **Selective Loading:** We will identify and load only the relevant worksheets and data ranges, skipping unnecessary charts, images, and formatting.
*   **Garbage Collection:** We will explicitly manage memory by triggering garbage collection after processing each worksheet.

## Success Criteria

The successful processing of these large workbooks will be determined by the following criteria:

*   **Complete Data Extraction:** All relevant data and calculations from the workbooks are successfully extracted.
*   **No Memory Issues:** The extraction process runs without encountering out-of-memory errors.
*   **Integration with `digitalmodel`:** The extracted data is successfully integrated into the appropriate `digitalmodel` modules.
*   **Performance:** The extraction process completes within a reasonable timeframe (e.g., under 5 minutes per workbook).

By implementing this streaming approach, we can overcome the challenges of processing large Excel workbooks and unlock the valuable information they contain.