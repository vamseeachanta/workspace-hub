# OCR Parser Registry Design

> **Issue:** #1643
> **Date:** 2026-04-05
> **Status:** Plan

## 1. Purpose

The OCR Parser Registry manages and tracks all OCR (Optical Character Recognition) operations within the document intelligence pipeline. It provides a centralized system for:
- Registering which parser processed which documents
- Tracking OCR quality metrics and confidence scores
- Managing fallback strategies for low-quality extractions
- Maintaining an audit trail of processing decisions

## 2. Supported Input Types

| Format | Extension | Typical Source | Pre-processing Needed |
|---|---|---|---|
| Scanned PDF (image-based) | `.pdf` | Standards org scanned docs, legacy reports | DPI check, deskew, binarization |
| TIFF images | `.tif`, `.tiff` | High-quality scans, archival documents | Resolution normalization |
| PNG images | `.png` | Screenshots, diagrams, figures | Color mode check |
| JPEG images | `.jpg`, `.jpeg` | Photographs of documents, camera captures | Noise reduction, sharpening |
| DjVu | `.djvu` | Old scanned publications | Format conversion to TIFF |
| BMP | `.bmp` | Raw scanner output | DPI metadata extraction |

## 3. Tesseract Integration Architecture

### 3.1 Core Integration
```python
import pytesseract
from PIL import Image
import subprocess

def run_tesseract(image_path, lang='eng', psm=3, config_extra=''):
    """Run Tesseract OCR with configurable parameters."""
    config = f'--psm {psm} -l {lang} {config_extra}'
    result = subprocess.run(
        ['tesseract', str(image_path), 'stdout', *config.split()],
        capture_output=True, text=True, timeout=120
    )
    return result.stdout, result.stderr
```

### 3.2 Language Packs
- **Primary:** `eng` (English, all documents)
- **Secondary:** `math` (mathematical formulas, equations)
- **Special:** `chi_sim`/`chi_tra` (if Asian-language shipyard docs appear)
- **Installation:** `apt install tesseract-ocr-{lang}`

### 3.3 PSM (Page Segmentation Mode) Selection
| PSM | Mode | Use Case |
|---|---|---|
| 3 | Auto | Standard documents (default) |
| 4 | Single column | Column-formatted reports |
| 6 | Single block | Text blocks, tables |
| 11 | Sparse text | Figures with scattered text |
| 13 | Raw line | Dense line-by-line (equations) |

### 3.4 Quality Parameters
- **DPI threshold:** 300 DPI minimum for good accuracy
- **Binarization:** Otsu's method or adaptive thresholding
- **Deskew:** Auto-rotation detection (±15 degree range)
- **DPI auto-upscale:** If < 300 DPI, scale up 2x before OCR

## 4. Registry Format

### 4.1 Master Registry (YAML)
```yaml
ocr_registry:
  version: "1.0"
  last_updated: "2026-04-05T12:00:00Z"

  parsers:
    - id: tesseract-5
      name: "Tesseract 5.x"
      type: tesseract
      default_config:
        lang: eng
        psm: 3
        dpi_min: 300
      quality_thresholds:
        high: 0.85   # Above: no review needed
        acceptable: 0.70  # Above: OK for pipeline
        low: 0.50    # Below: re-OCR or flag
        fallback: 0.30    # Below: manual review

    - id: google-vision
      name: "Google Cloud Vision API"
      type: cloud_ocr
      cost_per_page: 0.0015
      priority: fallback_for_complex_pages

  processing_log:
    - entry_id: "ocr-2026-0405-00001"
      source_file: "/mnt/ace/O&G-Standards/sname/transaction_12345.pdf"
      parser_id: tesseract-5
      pages_processed: 12
      avg_confidence: 0.923
      min_confidence: 0.741
      status: high_quality
      output_file: "data/ocr-output/sname/transaction_12345-ocr.txt"
      processing_time_s: 8.3
      reprocess_count: 0
      timestamp: "2026-04-05T12:00:00Z"
```

### 4.2 Per-Domain Registry
Each engineering domain maintains its own OCR registry subset:
```
data/ocr/
├── registry.yaml          # Master registry
├── stats/
│   ├── marine.yaml        # Domain-level OCR stats
│   ├── structural.yaml
│   ├── pipeline.yaml
│   └── standards.yaml
├── output/                # Raw OCR text output (organized by source)
└── failed/                # Documents that failed all OCR attempts
```

## 5. Quality Metrics

### 5.1 Confidence Scoring
Tesseract provides per-word confidence (0-100). The registry aggregates:
- **avg_confidence:** Mean of all word confidences
- **min_confidence:** Lowest word confidence (indicates problem areas)
- **words_below_threshold:** Count of words below 50% confidence
- **page_status:** High (>85%), Acceptable (70-85%), Low (50-70%), Failed (<50%)

### 5.2 Quality Validation
1. **Dictionary overlap:** What % of words are in standard English engineering dictionary
2. **Character n-gram likelihood:** Statistical anomaly detection for garbled text
3. **Equation detection:** Flag pages with heavy math as requiring special handling
4. **Table structure score:** Assess if tabular structures were preserved

### 5.3 Reporting
Weekly OCR quality report:
- Total pages processed
- Quality distribution (% high/acceptable/low/failed)
- Top 10 worst documents (lowest confidence)
- Re-processing recommendations

## 6. Fallback Strategies

### 6.1 Tier 1: Parameter Tweaking
If initial confidence < 70%:
1. Try PSM 6 (single block) instead of PSM 3
2. Try pre-processing: deskew, binarize, denoise
3. Try upscaling 2x if DPI < 300
4. Retry with different language pack if applicable

### 6.2 Tier 2: Alternative Parser
If Tier 1 fails (still < 50% after all retries):
1. Send to Google Cloud Vision API (higher accuracy, costs money)
2. Compare Cloud Vision output with Tesseract — keep the best result
3. For pages with equations: use Google Vision with `DOCUMENT_TEXT_DETECTION`

### 6.3 Tier 3: Manual Review Flagging
If both parsers fail (< 30% confidence):
1. Flag document in `data/ocr/failed/` manifest
2. Record reason (scanned at 72 DPI, handwritten, non-English, etc.)
3. Queue for manual review or professional OCR service
4. Generate thumbnail for human verification

### 6.4 Fallback Decision Tree
```
Document Scan (300 DPI)
  ├── Confidence >= 85% -> PASS, proceed to extraction
  ├── Confidence 70-84% -> PASS with warning, flag low-quality sections
  ├── Confidence 50-69% -> TIER 1 (retry with adjusted params)
  │     ├── Retry >= 70% -> PASS with warning
  │     └── Retry < 70%  -> TIER 2 (cloud OCR)
  ├── Confidence < 50% -> TIER 2 (cloud OCR)
  │     ├── Cloud >= 50% -> PASS with manual review recommendation
  │     └── Cloud < 50%  -> TIER 3 (manual review)
  └── Cloud < 30% -> Flag as unscannable, manual transcription needed
```

## 7. Pipeline Integration

### 7.1 Integration Points
```
Document Discovery
     |
     v
Type Check (PDF/Image) ──[is text digital]──> Skip OCR, use text extraction
     |
     [is image/scanned]
     v
OCR Parser Registry
     |
     +--> Select parser (Tesseract default)
     |
     v
Pre-processing (DPI check, deskew, binarize)
     |
     v
OCR Execution
     |
     v
Quality Assessment
     |
     ├── pass ──> Add to extraction pipeline
     ├── retry ─> Adjust params, retry (max 3)
     └── fail ──> Escalate to fallback, then manual review
```

### 7.2 Resume Capability
The registry maintains state so OCR jobs can be resumed after interruption:
- Documents with `ocr_completed: true` are skipped on restart
- Failed documents are re-queued with incremented `retry_count`
- Processing checkpoints saved every 100 documents

## 8. Estimated Processing Scale

| Source | Est. Scanned Docs | Est. Pages | Processing Time (Tesseract) |
|---|---|---|---|
| Standards orgs (scanned) | ~15,000 | ~200,000 | ~45 hours |
| Conference proceedings | ~8,000 | ~150,000 | ~35 hours |
| Legacy project reports | ~5,000 | ~100,000 | ~23 hours |
| DDE literature (scanned) | ~2,000 | ~30,000 | ~7 hours |
| **Total** | **~30,000** | **~480,000** | **~110 hours** |

## 9. Implementation Phases

### Phase 1: Parser Setup (Week 1)
- Install and configure Tesseract with language packs
- Build pre-processing pipeline (Pillow, OpenCV)
- Implement registry YAML structure
- Test on sample documents from each source type

### Phase 2: Batch Processing (Week 2-3)
- Process standards orgs (highest priority, most structured)
- Implement quality metrics and fallback logic
- Build processing log with resume capability
- Generate initial quality report

### Phase 3: Cloud Fallback and Scale (Week 4)
- Integrate Google Cloud Vision API as fallback
- Process conference papers and legacy reports
- Build failed document queue and manual review interface
- Generate comprehensive OCR registry for the entire corpus
