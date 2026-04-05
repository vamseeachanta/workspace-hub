# TDD Fixtures from Worked Examples Plan

## 1. Introduction

We have 279,000 worked examples extracted from our document corpus, available at `data/doc-intelligence/worked_examples.jsonl`. These examples are a valuable resource for creating high-quality test fixtures for the `digitalmodel` repository. This plan outlines the process for curating these examples into a comprehensive set of Test-Driven Development (TDD) fixtures.

## 2. Curation Process

### Step 1: Automated Initial Filtering

- **Objective:** Triage the 279,000 raw examples into a smaller, more manageable set.
- **Method:** Develop a script to parse `worked_examples.jsonl` and filter for examples that have both clear inputs and verifiable outputs. We will prioritize examples with numerical inputs and outputs.
- **Estimated outcome:** A subset of 20,000-30,000 high-potential examples.

### Step 2: Organization by Domain

- **Objective:** Structure the filtered examples for easy use within the `digitalmodel` test suite.
- **Method:** The filtering script will categorize examples by their source document's domain (e.g., `marine`, `structural`, `pipeline`). The output will be a directory structure mirroring the `digitalmodel` domain structure:

```
/tests/fixtures/worked_examples/
├── marine/
│   ├── stability.json
│   └── mooring.json
├── structural/
│   ├── fatigue.json
│   └── buckling.json
└── ...
```

### Step 3: Manual Review and Refinement

- **Objective:** Ensure the quality and accuracy of the curated fixtures.
- **Method:** Domain experts will review the categorized fixtures. This involves:
    - Verifying the correctness of the extracted data.
    - Cleaning up any noise or inconsistencies.
    - Adding metadata (e.g., source document, section) to each fixture.

## 3. Integration with `digitalmodel` Tests

- **Fixture Loading:** A utility function will be created in `digitalmodel/tests/conftest.py` to easily load these JSON fixtures.
- **Test Implementation:** New tests will be written to use these fixtures. The tests will pass the 'input' from the fixture to the relevant `digitalmodel` function and assert that the result matches the 'output' from the fixture.

## 4. Priority Domains

We will prioritize the curation of fixtures for the following high-value domains:

1.  **Marine:** Stability, mooring, and hydrodynamics.
2.  **Structural:** Fatigue, buckling, and fracture mechanics.
3.  **Pipeline:** On-bottom stability and flow assurance.

## 5. Timeline

- **Week 1:** Develop initial filtering and categorization script.
- **Week 2:** Execute script and perform manual review of Marine fixtures.
- **Week 3:** Integrate Marine fixtures into `digitalmodel` and begin review of Structural fixtures.
- **Week 4:** Continue with remaining domains.
