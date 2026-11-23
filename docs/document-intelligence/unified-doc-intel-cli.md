# Unified Document Intelligence CLI Design

## Overview
This document proposes a single, unified Command Line Interface (CLI) tool for document intelligence operations within the ACE Engineer workspace. The CLI consolidates functionality from existing scripts in `scripts/` and `data/` directories into a cohesive tool with intuitive subcommands.

## Existing Functionality Analysis
Current document intelligence capabilities are scattered across:
- **scripts/data/doc-intelligence/**: Core extraction, indexing, and querying
- **scripts/document-intelligence/**: Specialized processors (OCR, classifiers, etc.)
- **scripts/utilities/doc-to-context/**: Document conversion utilities
- **scripts/data/document-index/**: Registry and classification systems

Key existing tools include:
- `extract-document.py`: Single document extraction with manifest generation
- `build-doc-intelligence.py`: Federated index building from manifests
- `query-doc-intelligence.py`: Searching across extracted content
- `deep-extract.py`: Advanced extraction with table/curve handling
- Various classifiers and processors for specific document types

## Proposed Unified CLI Architecture

### Design Principles
1. **Consistency**: Uniform interface patterns across all subcommands
2. **Discoverability**: Clear help system with examples
3. **Composability**: Subcommands work together in pipelines
4. **Extensibility**: Easy addition of new document types and operations
5. **Backward Compatibility**: Maintain access to existing functionality
6. **Performance**: Leverage parallel processing where appropriate

### Core Subcommands
The unified CLI will provide six primary subcommands:

1. **scan** - Discover and inventory documents
2. **index** - Build searchable indexes from extracted content
3. **extract** - Extract structured content from documents
4. **classify** - Categorize documents by type and domain
5. **summarize** - Generate summaries and extract key information
6. **audit** - Quality assurance and validation of processed documents

### Interface Design

#### Global Options
```
Usage: doc-intel [OPTIONS] SUBCOMMAND [ARGS]...

Options:
  --version           Show version and exit
  -v, --verbose       Enable verbose logging
  -q, --quiet         Suppress non-essential output
  --config FILE       Path to configuration file
  --workspace DIR     Workspace root directory (default: auto-detect)
  --output-format FMT Output format (json, yaml, table, text) [default: table]
  --help              Show this message and exit
```

#### Subcommand: scan
Discover documents in specified paths or registries.

```
Usage: doc-intel scan [OPTIONS] [PATH]...

Arguments:
  PATH  Paths to scan (default: current directory)

Options:
  -r, --recursive           Scan directories recursively
  -g, --glob PATTERN        File glob pattern (default: *)
  --exclude-glob PATTERN    Exclude files matching pattern
  --from-registry           Scan using document registry instead of filesystem
  --registry FILE           Path to registry file (default: data/document-index/online-resource-registry.yaml)
  --max-depth DEPTH         Maximum directory recursion depth
  --follow-symlinks         Follow symbolic links
  --print0                  Output null-terminated paths (for xargs -0)
```

#### Subcommand: index
Build or update searchable indexes from document manifests or extracted content.

```
Usage: doc-intel index [OPTIONS] [SOURCE]...

Arguments:
  SOURCE  Source of extracted content (manifests, extracted dir) [default: data/doc-intelligence/manifests]

Options:
  --manifest-dir DIR        Directory containing *.manifest.yaml files
  --output-dir DIR          Where to write JSONL indexes [default: data/doc-intelligence]
  --force                   Rebuild all indexes, ignoring checksums
  --dry-run                 Scan only, don't write any files
  --verbose                 Print per-manifest/record details
  --jobs N                  Number of parallel jobs [default: CPU count]
  --types TYPE1,TYPE2       Specific content types to index (tables, curves, definitions, etc.)
  --update                  Update existing indexes incrementally
  --validate                Validate index integrity after building
```

#### Subcommand: extract
Extract structured content from documents using appropriate parsers.

```
Usage: doc-intel extract [OPTIONS] INPUT... OUTPUT

Arguments:
  INPUT   Input document(s) to extract from
  OUTPUT  Output directory or file for extracted content

Options:
  --parser PARSE          Specific parser to use (auto-detected if not specified)
                          Available: pdf, docx, html, xml, txt, csv, xlsx, etc.
  --preserve-structure    Maintain original document structure in output
  --extract-tables        Extract tables as CSV/JSON
  --extract-curves        Extract digitizable curves/data points
  --extract-equations     Extract and convert equations to LaTeX/Python
  --extract-definitions   Extract terminology and definitions
  --extract-procedures    Extract step-by-step procedures
  --extract-references    Extract bibliographic references and citations
  --language CODE         Document language for OCR/processing (default: en)
  --ocr                   Force OCR for text-extraction resistant documents
  --pages RANGE           Page range to process (e.g., 1-10, 5, 15-)
  --dpi INTEGER           DPI for rasterization (default: 150)
  --preserve-images       Extract embedded images
  --output-format FMT     Output format: yaml, json, markdown, xml [default: yaml]
  --single-file           Combine all extractions into single output file
  --zip-output            Compress output directory into ZIP archive
```

#### Subcommand: classify
Categorize documents by type, domain, and relevance.

```
Usage: doc-intel classify [OPTIONS] INPUT...

Arguments:
  INPUT   Input document(s) or extracted content to classify

Options:
  --model MODEL           Classification model to use
                          Available: doc-type, domain, relevance, language, risk-level
  --threshold FLOAT       Confidence threshold for classification [default: 0.7]
  --multi-label           Allow multiple labels per document
  --explain               Provide explanation for classification decisions
  --train                 Train/new model from labeled examples
  --training-data DIR     Directory with labeled training examples
  --save-model PATH       Path to save trained model
  --load-model PATH       Path to load pre-trained model
  --output-format FMT     Output format: json, yaml, csv, table [default: table]
  --label-as FIELD        Output classification results to specific field
  --hierarchical          Use hierarchical classification (e.g., doc.type.subtype)
```

#### Subcommand: summarize
Generate summaries and extract key information from documents.

```
Usage: doc-intel summarize [OPTIONS] INPUT...

Arguments:
  INPUT   Input document(s) or extracted content to summarize

Options:
  --type TYPE             Summary type: abstract, tl;dr, key-points, metadata, entities
                          [default: key-points]
  --length LENGTH         Target length: brief, standard, detailed [default: standard]
  --format FMT            Output format: paragraph, bullets, table, json [default: bullets]
  --focus FOCUS           Focus areas: methods, results, conclusions, specifications
  --entity-types TYPES    Entity types to extract: person, org, location, date, number
  --extract-keywords      Extract keywords and key phrases
  --extract-acronyms      Extract and expand acronyms/abbreviations
  --reading-level         Estimate reading level and complexity
  --language-detect       Detect and report document language
  --compare               Compare multiple documents for similarities/differences
  --reference-doc PATH    Reference document for comparison-based summarization
  --output-format FMT     Output format: json, yaml, text, markdown [default: markdown]
```

#### Subcommand: audit
Validate and quality-check processed documents and extracted content.

```
Usage: doc-intel audit [OPTIONS] [TARGET]...

Arguments:
  TARGET  What to audit: extracted-content, indexes, classifications, summaries
          [default: extracted-content]

Options:
  --standard STD          Audit against specific standard:
                          Available: completeness, accuracy, consistency, freshness
  --check-duplicates      Check for duplicate documents or content
  --check-broken-links    Validate internal and external links
  --check-ocr-quality     Assess OCR confidence and text quality
  --check-table-integrity Validate extracted table structure and data
  --check-manifests       Validate manifest.yaml files for required fields
  --check-index-consistency Verify index correctness against source
  --threshold FLOAT       Minimum acceptable score [default: 0.8]
  --generate-report       Generate detailed audit report
  --report-format FMT     Report format: html, pdf, markdown, json [default: html]
  --fix-auto              Automatically fix correctable issues
  --fix-interactive       Prompt before applying fixes
  --exclude PATTERN       Exclude files matching pattern from audit
  --only PATTERN          Only audit files matching pattern
```

### Implementation Plan

#### Phase 1: Foundation (Weeks 1-2)
1. **Core Framework**
   - Create `doc-intel` entry point with argparse structure
   - Implement global options and workspace detection
   - Design plugin architecture for subcommands
   - Create base classes for subcommand implementations

2. **Scan Subcommand**
   - Implement filesystem scanning with glob patterns
   - Add registry-based scanning capability
   - Create output formatters (table, json, yaml, text)
   - Add recursive and depth-limiting options

#### Phase 2: Core Operations (Weeks 3-4)
3. **Extract Subcommand**
   - Integrate existing parsers from `scripts/data/doc_intelligence/parsers/`
   - Wrapper around `extract-document.py` functionality
   - Add table, curve, and equation extraction options
   - Implement OCR fallback with Tesseract/Docling

4. **Index Subcommand**
   - Refactor `build-doc-intelligence.py` functionality
   - Add incremental update capability
   - Implement validation checks
   - Create dry-run and force rebuild options

#### Phase 3: Advanced Features (Weeks 5-6)
5. **Classify Subcommand**
   - Integrate existing classifiers from `scripts/document-intelligence/`
   - Support for doc-type, domain, and relevance classification
   - Add model training and persistence capabilities
   - Implement confidence scoring and explanations

6. **Summarize Subcommand**
   - Leverage existing text processing capabilities
   - Implement multiple summary types (abstract, key-points, etc.)
   - Add entity extraction and keyword identification
   - Create comparison and reference-based summarization

#### Phase 4: Quality Assurance (Weeks 7-8)
7. **Audit Subcommand**
   - Implement completeness, accuracy, and consistency checks
   - Add duplicate detection and link validation
   - Create OCR quality and table integrity validation
   - Generate detailed reports with auto-fix capabilities

#### Phase 5: Integration and Polish (Weeks 9-10)
8. **Backward Compatibility**
   - Ensure all existing scripts remain functional
   - Create compatibility aliases or wrappers
   - Document migration path from old to new CLI
   - Add deprecation warnings where appropriate

9. **Testing and Documentation**
   - Comprehensive unit and integration tests
   - User guide with examples and use cases
   - Developer guide for extending the CLI
   - Performance benchmarks and optimization tips

### Technical Architecture

#### Core Components
```
doc-intel/
├── __init__.py
├── main.py                 # Entry point and argument parsing
├── core/
│   ├── workspace.py        # Workspace detection and configuration
│   ├── output.py           # Formatting and output handling
│   └── plugins.py          # Plugin architecture for subcommands
├── subcommands/
│   ├── scan.py
│   ├── index.py
│   ├── extract.py
│   ├── classify.py
│   ├── summarize.py
│   └── audit.py
├── parsers/                # Document parser registry and adapters
│   ├── base.py
│   ├── pdf.py
│   ├── docx.py
│   ├── html.py
│   └── ...
├── classifiers/            # Classification models and trainers
├── summarizers/            # Summarization algorithms
└── auditors/               # Audit checks and validators
```

#### Data Flow
1. **Scan** → Discovers files and creates inventory
2. **Extract** → Processes files, creates manifests and extracted content
3. **Index** → Builds searchable indexes from manifests
4. **Classify** → Categorizes documents and content
5. **Summarize** → Generates summaries from extracted/content
6. **Audit** → Validates quality at any stage

#### Configuration
- Configuration file: `~/.config/doc-intel/config.yaml` or `.doc-intel.yml` in workspace
- Supports environment variable overrides: `DOCINTEL_*`
- Workspace-specific configuration in `.doc-intel/` directory

### Migration Strategy

#### Compatibility Layer
- Provide wrapper scripts that map old command patterns to new CLI
- Example: `extract-document.py` → `doc-intel extract [options]`
- Maintain existing script locations during transition period
- Add deprecation warnings to old scripts pointing to new CLI

#### Data Format Compatibility
- Maintain existing manifest.yaml format
- Preserve JSONL index formats for backward compatibility
- Ensure extracted content structure remains consistent
- Provide conversion utilities for any format changes

### Benefits

#### For Users
- **Unified Interface**: One tool to learn instead of many scattered scripts
- **Discoverability**: Tab completion and helpful error messages
- **Consistency**: Uniform options and behavior across operations
- **Power**: Access to advanced features through intuitive subcommands
- **Reliability**: Standardized error handling and logging

#### For Developers
- **Extensibility**: Clear plugin architecture for adding new capabilities
- **Maintainability**: Centralized codebase vs. scattered scripts
- **Testing**: Unified test framework for all functionality
- **Documentation**: Single source of truth for CLI usage
- **Performance**: Shared infrastructure and optimizations

### Open Questions and Considerations

1. **Parser Selection**: Should we use existing parsers or evaluate new libraries like Docling?
2. **OCR Strategy**: Tesseract vs. Docling vs. commercial APIs for OCR needs
3. **Classification Models**: Scikit-learn vs. transformers vs. rule-based approaches
4. **Storage Backend**: File-based indexes vs. SQLite vs. full search engine (Elasticsearch)
5. **Extensibility Model**: Python plugins vs. external commands vs. microservices
6. **Configuration Format**: YAML vs. TOML vs. JSON for configuration files
7. **Progress Reporting**: tqdm vs. custom progress bars vs. structured logging
8. **Error Handling**: Exceptions vs. return codes vs. structured error objects

### Recommendation
Proceed with implementation using existing proven components where possible, prioritizing:
1. Leveraging current parser implementations
2. Maintaining manifest and index format compatibility
3. Using incremental development with frequent integration
4. Focusing on user experience and discoverability
5. Ensuring backward compatibility during transition

## Conclusion
The unified document intelligence CLI will significantly improve the usability and maintainability of document processing capabilities within the ACE Engineer workspace. By consolidating fragmented scripts into a coherent tool with intuitive subcommands, we reduce cognitive overhead, enable powerful workflows, and create a foundation for future enhancements. The proposed design balances innovation with practicality, building on existing investments while providing a clear path forward.