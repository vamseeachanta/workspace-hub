---
title: "Technical Safety Analysis Module for WorldEnergyData"
description: "Port and generalize ENIGMA safety analysis codebase into worldenergydata as a configurable safety_analysis module with NLP classification, incident correlation, and time-series feature engineering"
version: "1.0"
module: "safety_analysis"

session:
  id: "harmonic-squishing-acorn"
  agent: "claude-opus-4.5"

review:
  required_iterations: 3
  current_iteration: 0
  status: "pending"
  reviewers:
    openai_codex:
      status: "pending"
      iteration: 0
      feedback: ""
    google_gemini:
      status: "pending"
      iteration: 0
      feedback: ""
  ready_for_next_step: false

status: "draft"
progress: 0

created: "2026-02-01"
updated: "2026-02-01"
target_completion: ""

priority: "high"
tags: [safety, hse, nlp, ml, enigma, observation-cards, incident-analysis]

links:
  spec: ""
  branch: "feature/WRK-072-safety-analysis-module"
  work_item: "WRK-072"
---

# Technical Safety Analysis Module for WorldEnergyData

> **Module**: safety_analysis | **Status**: draft | **Work Item**: WRK-072 | **Created**: 2026-02-01

## Summary

Port the ENIGMA project's safety analysis codebase (NLP classification, incident correlation, feature engineering, hypothesis testing) from `/mnt/github/workspace-hub/client_projects/energy_firm_sd_support/xom/000 ENIGMA/` into a generalized, configurable module at `src/worldenergydata/modules/safety_analysis/`. All client-specific code is abstracted; no Databricks dependency; optional heavy ML deps (torch/transformers) gated behind extras.

---

## Cross-Review Process (MANDATORY)

> **REQUIREMENT**: Minimum **3 review iterations** with OpenAI Codex and Google Gemini before implementation.

### Review Status

| Gate | Status |
|------|--------|
| Iterations (>= 3) | 0/3 |
| OpenAI Codex | pending |
| Google Gemini | pending |
| **Ready** | false |

### Review Log

| Iter | Date | Reviewer | Status | Feedback Summary |
|------|------|----------|--------|------------------|
| 1 | | Codex | Pending | |
| 1 | | Gemini | Pending | |
| 2 | | Codex | Pending | |
| 2 | | Gemini | Pending | |
| 3 | | Codex | Pending | |
| 3 | | Gemini | Pending | |

### Approval Checklist

- [ ] Iteration 1 complete (both reviewers)
- [ ] Iteration 2 complete (both reviewers)
- [ ] Iteration 3 complete (both reviewers)
- [ ] **APPROVED**: Ready for implementation

---

## ENIGMA Source Audit Summary

### Reusability Tiers

| Tier | Components | Score | Action |
|------|-----------|-------|--------|
| **1 (Production-Ready)** | FeatureEngineer (30+ stats/FFT features), BERT_models.py (PyTorch Lightning), tfidf_utils.py | 9/10 | Near-1:1 port |
| **2 (Moderate)** | Hyperopt tuning patterns, classification pipeline, correlation tools, hypothesis tests, incident aggregation | 6-8/10 | Extract & generalize |
| **3 (Refactor)** | Data loading (Databricks/spark.sql), preprocessing (3-contractor schemas), config (hardcoded paths/rigs) | 2-5/10 | Rewrite with abstractions |

### Key ENIGMA Source Files

| File | Lines | Porting Target |
|------|-------|----------------|
| `Lib/sshe_lib_feature_engineering.py` | 145 | `analysis/feature_engineering.py` |
| `Lib/sshe_lib_correlation_tools.py` | ~150 | `analysis/correlation.py` |
| `Lib/tfidf_utils.py` | 60 | `nlp/tfidf_vectorizer.py` + `nlp/text_preprocessing.py` |
| `Models/BERT_models.py` | ~100 | `nlp/bert_pipeline.py` |
| `Experiments/tfidf_models/*.py` | 9 files | `nlp/classification_pipeline.py` |
| `hypothesis_testing/sshe_lib_time_series.py` | 158 | `analysis/time_series.py` |
| `hypothesis_testing/sshe_tests.py` | 1700 | `analysis/statistical_tests.py` (extract stats only) |
| `cod/incident_analysis.py` | 54 | `analysis/incident_aggregation.py` |

---

## Industry Research Context

Key findings informing this design:

- **TF-IDF vs BERT tradeoff**: TF-IDF is 50x faster, 90% cheaper, often matches BERT for simpler classification tasks. Design prioritizes TF-IDF path with BERT as optional upgrade.
- **Random Forest proven**: Dominant classifier for safety occurrence reports across literature.
- **Leading indicators**: Observations/near-misses predict incidents via lagged cross-correlation — the core analytical pattern from ENIGMA is well-supported by research.
- **Domain stop words critical**: Safety text is short (~100-150 chars); custom stop words significantly impact classification quality.
- **2025 trends**: BERT + AcciMap frameworks for causal analysis; LLMs emerging for real-time risk assessment but not yet mainstream.

Sources:
- [NLP Application to Safety Occurrence Reports (MDPI)](https://www.mdpi.com/2313-576X/9/2/22)
- [Leading Indicators for Offshore Drillwell Blowout (ScienceDirect)](https://www.sciencedirect.com/science/article/abs/pii/S0957582017300058)
- [NLP + Bayesian Networks for Process Safety Events](https://ideas.repec.org/a/eee/reensy/v241y2024ics0951832023005525.html)
- [LLMs in Oil and Gas Incident Prevention](https://www.capellasolutions.com/blog/from-reactive-to-proactive-llms-in-oil-and-gas-incident-prevention)
- [SafeOCS Industry Safety Data Program (BSEE)](https://safeocs.gov/file/SafeOCS_ISD_Phase-I_Report_v1.Final.7.pdf)

---

## Module Directory Structure

```
src/worldenergydata/modules/safety_analysis/
    __init__.py                          # Module entry point, __all__, __version__
    exceptions.py                        # SafetyAnalysisError hierarchy
    config.py                            # Pydantic settings (env-based)
    constants.py                         # Enums: SeverityLevel, ObservationType, IncidentType
    core/
        __init__.py
        models.py                        # SafetyObservation, SafetyIncident, ClassificationResult
        schemas.py                       # SchemaMapping, SchemaRegistry (configurable column maps)
    data/
        __init__.py
        loaders.py                       # CSV/Parquet/Excel file-based loading
        processors.py                    # ObservationProcessor, IncidentProcessor (ETL)
        config/
            __init__.py
            default_stop_words.yaml      # Configurable domain stop words
            classification_labels.yaml   # Observation types, severity mappings
            model_params.yaml            # Hyperparameter search spaces
    analysis/
        __init__.py
        time_series.py                   # TimeSeriesBuilder, moving averages, gradient
        correlation.py                   # LaggedCrossCorrelation, crosscorr()
        feature_engineering.py           # FeatureEngineer (30+ statistical/FFT features)
        incident_aggregation.py          # Daily counts, hurt index, group-by patterns
        statistical_tests.py             # t-test, ANOVA, chi-square, Pearson/Spearman
        decomposition.py                 # Seasonal decomposition (optional statsmodels)
    nlp/
        __init__.py                      # Optional dependency gating
        text_preprocessing.py            # TextPreprocessor (configurable stop words)
        tfidf_vectorizer.py              # SafetyTfidfVectorizer (fit/transform/save/load)
        classification_pipeline.py       # ClassificationPipeline (RF/XGB/LogReg + hyperopt)
        bert_pipeline.py                 # BertClassificationPipeline (optional torch/transformers)
        model_registry.py                # File-based model save/load/tracking
    adapters/
        __init__.py
        hse_adapter.py                   # HSE module -> SafetyIncident mapping
        marine_safety_adapter.py         # Marine Safety -> SafetyIncident mapping
        pipeline_safety_adapter.py       # Pipeline Safety -> SafetyIncident mapping
        bsee_adapter.py                  # BSEE contextual data integration
    reports/
        __init__.py
        incident_report.py               # Plotly incident trend/severity reports
        correlation_report.py            # Observation-incident correlation plots
        classification_report.py         # Confusion matrix, F1 performance reports
    cli.py                               # Click CLI: load, classify, correlate, report
```

---

## Key Design Decisions

### 1. Schema Abstraction (replaces hardcoded XOM schemas)

```python
class SchemaMapping(BaseModel):
    asset_id_column: str          # Generic for "rig_id" / "facility_id"
    datetime_column: str
    description_column: str
    type_column: Optional[str]
    severity_column: Optional[str]
    type_mapping: Dict[str, str]  # e.g., {"SAFE_*": "safe"}
    id_extraction_regex: Optional[str]
```

Users define mappings in YAML; `data/processors.py` transforms any source to the unified schema.

### 2. Domain Models (Pydantic, validated)

- `SafetyObservation`: asset_id, observed_at, description, observation_type, action_taken, metadata
- `SafetyIncident`: asset_id, occurred_at, incident_type, actual_severity, potential_severity, description, metadata
- `ClassificationResult`: text, predicted_label, confidence, model_name, feature_type
- `CorrelationResult`: asset_id, lag_values, correlation_values, peak_correlation, peak_lag

### 3. Optional Heavy Dependencies

```toml
[project.optional-dependencies]
safety-ml = ["scikit-learn>=1.3.0", "hyperopt>=0.2.7", "xgboost>=2.0.0"]
safety-bert = ["torch>=2.0.0", "transformers>=4.35.0"]
safety-tracking = ["mlflow>=2.9.0"]
```

Gated with try/except imports + `OptionalDependencyError` with install instructions.

### 4. No Databricks / No MLflow by Default

- All `spark.sql()` replaced with `pd.read_csv()`/`pd.read_excel()`
- MLflow replaced with file-based `ModelRegistry` (joblib + JSON metadata)
- MLflow available as optional adapter

---

## Phases

### Phase 1: Foundation — Core Models, Data Layer, Config

**Goal**: Establish the data contract and loading pipeline.

- [ ] Create `exceptions.py` (inherit from `common.exceptions.ModuleError`)
- [ ] Create `constants.py` (SeverityLevel, ObservationType, IncidentType enums)
- [ ] Create `config.py` (AnalysisConfig, NLPConfig, HyperparamConfig via Pydantic)
- [ ] Create YAML config files (`default_stop_words.yaml`, `classification_labels.yaml`, `model_params.yaml`)
- [ ] Create `core/models.py` (SafetyObservation, SafetyIncident, ClassificationResult, CorrelationResult)
- [ ] Create `core/schemas.py` (SchemaMapping, SchemaRegistry)
- [ ] Create `data/loaders.py` (SafetyDataLoader — CSV/Excel/Parquet)
- [ ] Create `data/processors.py` (ObservationProcessor, IncidentProcessor)
- [ ] Create module `__init__.py` with `__all__` re-exports
- [ ] Create test fixtures (sample_observations.csv, sample_incidents.csv)
- [ ] Write tests: test_models, test_schemas, test_loaders, test_processors, test_config, test_exceptions, test_constants

### Phase 2: Analysis Engine — Time Series, Correlation, Feature Engineering

**Goal**: Port the highest-value ENIGMA analytical components.

- [ ] Create `analysis/time_series.py` (TimeSeriesBuilder — port from `sshe_lib_time_series.py`)
- [ ] Create `analysis/correlation.py` (LaggedCrossCorrelation — port from `sshe_lib_correlation_tools.py`)
- [ ] Create `analysis/feature_engineering.py` (FeatureEngineer — near-1:1 port from `sshe_lib_feature_engineering.py`)
- [ ] Create `analysis/incident_aggregation.py` (aggregate_by_time, compute_hurt_index — port from `incident_analysis.py`)
- [ ] Create `analysis/statistical_tests.py` (t-test, ANOVA, chi-square — extract from `sshe_tests.py`)
- [ ] Create `analysis/decomposition.py` (seasonal decomposition — port from `sshe_lib_time_series.py`)
- [ ] Write tests for all analysis components (with known-answer test data)

### Phase 3: NLP & Classification — TF-IDF Pipeline

**Goal**: Core ML classification without heavy dependencies.

- [ ] Create `nlp/text_preprocessing.py` (TextPreprocessor — generalize from `tfidf_utils.py` tfidf_prep())
- [ ] Create `nlp/tfidf_vectorizer.py` (SafetyTfidfVectorizer — wrap sklearn TfidfVectorizer with save/load)
- [ ] Create `nlp/model_registry.py` (file-based model persistence — replace MLflow)
- [ ] Create `nlp/classification_pipeline.py` (ClassificationPipeline — generalize from Experiments/tfidf_models/)
- [ ] Add `scikit-learn` to pyproject.toml dependencies
- [ ] Write tests for all NLP components

### Phase 4: Integration — Adapters, Reports, CLI

**Goal**: Connect safety_analysis to the worldenergydata ecosystem.

- [ ] Create `adapters/hse_adapter.py` (HSEIncident ORM -> SafetyIncident)
- [ ] Create `adapters/marine_safety_adapter.py`
- [ ] Create `adapters/pipeline_safety_adapter.py`
- [ ] Create `adapters/bsee_adapter.py`
- [ ] Create `reports/incident_report.py` (Plotly HTML)
- [ ] Create `reports/correlation_report.py` (Plotly HTML)
- [ ] Create `reports/classification_report.py` (confusion matrix, metrics)
- [ ] Create `cli.py` (Click CLI: load, classify, correlate, report)
- [ ] Register CLI in unified worldenergydata CLI entry point
- [ ] Write tests for adapters, reports, CLI

### Phase 5: BERT Pipeline (Optional)

**Goal**: Deep learning classification path for complex safety text.

- [ ] Create `nlp/bert_pipeline.py` (BertClassificationPipeline — HuggingFace transformers)
- [ ] Gate all torch/transformers imports with try/except
- [ ] Write tests with `@pytest.mark.skipif(not _HAS_BERT)`
- [ ] Update `__init__.py` exports

---

## Critical Files to Modify/Create

| File | Action | Notes |
|------|--------|-------|
| `src/worldenergydata/modules/safety_analysis/**` | CREATE | ~35 new source files |
| `tests/modules/safety_analysis/**` | CREATE | ~20 test files + fixtures |
| `worldenergydata/pyproject.toml` | EDIT | Add scikit-learn dep + optional extras |
| `src/worldenergydata/cli/main.py` | EDIT | Register safety-analysis CLI subcommand |
| `data/config/` (3 YAML files) | CREATE | Stop words, labels, model params |

## Key ENIGMA Files to Reference During Port

| ENIGMA Source | Target | Priority |
|--------------|--------|----------|
| `cod/nlp/sshe_NLP/Lib/sshe_lib_feature_engineering.py` | `analysis/feature_engineering.py` | CRITICAL |
| `cod/nlp/sshe_NLP/Lib/sshe_lib_correlation_tools.py` | `analysis/correlation.py` | CRITICAL |
| `cod/nlp/sshe_NLP/Lib/tfidf_utils.py` | `nlp/text_preprocessing.py` + `nlp/tfidf_vectorizer.py` | CRITICAL |
| `cod/nlp/sshe_NLP/Models/BERT_models.py` | `nlp/bert_pipeline.py` | Phase 5 |
| `cod/nlp/hypothesis_testing/sshe_lib_time_series.py` | `analysis/time_series.py` | HIGH |
| `cod/nlp/hypothesis_testing/sshe_tests.py` | `analysis/statistical_tests.py` | HIGH |
| `cod/incident_analysis.py` | `analysis/incident_aggregation.py` | HIGH |
| `cod/nlp/sshe_NLP/Experiments/tfidf_models/` | `nlp/classification_pipeline.py` | HIGH |
| `cod/nlp/sshe_NLP/PreProcessing/preprocess_obs_cards_cloned.py` | `data/processors.py` | MEDIUM |

---

## Verification Plan

### Per-Phase Testing

```bash
# Phase 1: Foundation
cd /mnt/github/workspace-hub/worldenergydata
uv run pytest tests/modules/safety_analysis/test_models.py tests/modules/safety_analysis/test_schemas.py tests/modules/safety_analysis/test_loaders.py tests/modules/safety_analysis/test_processors.py -v --cov=src/worldenergydata/modules/safety_analysis

# Phase 2: Analysis
uv run pytest tests/modules/safety_analysis/test_feature_engineering.py tests/modules/safety_analysis/test_correlation.py tests/modules/safety_analysis/test_time_series.py -v

# Phase 3: NLP
uv run pytest tests/modules/safety_analysis/test_tfidf_vectorizer.py tests/modules/safety_analysis/test_classification_pipeline.py -v

# Phase 4: Integration
uv run pytest tests/modules/safety_analysis/ -v --cov=src/worldenergydata/modules/safety_analysis --cov-fail-under=80
```

### End-to-End Validation

1. Load sample observation CSV via CLI: `worldenergydata safety-analysis load observations -i sample.csv -s default`
2. Run classification: `worldenergydata safety-analysis classify train -i data.csv --model-type rf`
3. Run correlation analysis: `worldenergydata safety-analysis analyze correlate --obs obs.csv --inc inc.csv`
4. Generate report: `worldenergydata safety-analysis report incidents -i data.csv -o report.html`
5. Verify no ENIGMA-specific code: `grep -r "xom\|enigma\|H&P\|Nabors\|Databricks\|spark.sql" src/worldenergydata/modules/safety_analysis/` returns nothing

### Coverage Target

80%+ overall module coverage, 100% on `core/models.py` and `analysis/feature_engineering.py`.

---

## Progress

| Phase | Status | Notes |
|-------|--------|-------|
| Review Iteration 1 | Pending | |
| Review Iteration 2 | Pending | |
| Review Iteration 3 | Pending | |
| Plan Approved | Pending | |
| Phase 1: Foundation | Pending | |
| Phase 2: Analysis Engine | Pending | |
| Phase 3: NLP & Classification | Pending | |
| Phase 4: Integration | Pending | |
| Phase 5: BERT (Optional) | Pending | |

---

## Session Log

| Date | Session ID | Agent | Notes |
|------|------------|-------|-------|
| 2026-02-01 | harmonic-squishing-acorn | claude-opus-4.5 | Plan created, linked to WRK-072 |
