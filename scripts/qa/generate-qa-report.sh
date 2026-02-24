#!/usr/bin/env bash
# =============================================================================
# generate-qa-report.sh
# Generates a self-contained HTML QA report for a WRK work item.
#
# Usage:
#   generate-qa-report.sh --wrk-id WRK-NNN [OPTIONS]
#
# Options:
#   --wrk-id   <id>       WRK item ID (required)
#   --type     <type>     Output type: rao-diffraction|mooring-analysis|mesh|
#                         data-pipeline|calculation|code|generic  (default: generic)
#   --artefacts <paths>   Space-separated list of output artefact paths
#   --out      <file>     Destination HTML file
#                         (default: .claude/state/qa-reports/<WRK-ID>-qa.html)
#   --title    <text>     Report title override
#   --process-log <file>  Path to a process log file to embed (optional)
#
# Exit codes:
#   0   Report written successfully
#   1   Error (missing WRK item, write failure)
# =============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# ---------------------------------------------------------------------------
# Defaults
# ---------------------------------------------------------------------------
WRK_ID=""
OUTPUT_TYPE="generic"
ARTEFACTS_ARR=()
OUT_FILE=""
TITLE_OVERRIDE=""
PROCESS_LOG=""

# ---------------------------------------------------------------------------
# Argument parsing
# ---------------------------------------------------------------------------
while [[ $# -gt 0 ]]; do
    case "$1" in
        --wrk-id)    WRK_ID="$2";          shift 2 ;;
        --type)      OUTPUT_TYPE="$2";     shift 2 ;;
        --artefacts) IFS=' ' read -r -a ARTEFACTS_ARR <<< "$2"; shift 2 ;;
        --out)       OUT_FILE="$2";        shift 2 ;;
        --title)     TITLE_OVERRIDE="$2";  shift 2 ;;
        --process-log) PROCESS_LOG="$2";   shift 2 ;;
        *) echo "Unknown option: $1" >&2; exit 1 ;;
    esac
done

if [[ -z "$WRK_ID" ]]; then
    echo "Error: --wrk-id is required" >&2
    exit 1
fi

# ---------------------------------------------------------------------------
# Resolve WRK item file
# ---------------------------------------------------------------------------
WRK_FILE=""
for dir in pending working blocked done; do
    candidate="$REPO_ROOT/.claude/work-queue/$dir/$WRK_ID.md"
    if [[ -f "$candidate" ]]; then
        WRK_FILE="$candidate"
        break
    fi
done

if [[ -z "$WRK_FILE" ]]; then
    echo "Warning: WRK file not found for $WRK_ID — using placeholder metadata" >&2
    WRK_TITLE="$WRK_ID (file not found)"
    WRK_STATUS="unknown"
    WRK_AREA="unknown"
    WRK_CREATED="unknown"
else
    WRK_TITLE=$(grep "^title:" "$WRK_FILE" | sed 's/^title: //' | head -1)
    WRK_STATUS=$(grep "^status:" "$WRK_FILE" | awk '{print $2}' | head -1)
    WRK_AREA=$(grep "^area:" "$WRK_FILE" | awk '{print $2}' | head -1)
    WRK_CREATED=$(grep "^created:" "$WRK_FILE" | awk '{print $2}' | head -1)
fi

REPORT_TITLE="${TITLE_OVERRIDE:-QA Report — $WRK_ID}"
REPORT_DATE=$(date -u "+%Y-%m-%d %H:%M UTC")

# ---------------------------------------------------------------------------
# Output path
# ---------------------------------------------------------------------------
QA_DIR="$REPO_ROOT/.claude/state/qa-reports"
mkdir -p "$QA_DIR"
OUT_FILE="${OUT_FILE:-$QA_DIR/${WRK_ID}-qa.html}"

# ---------------------------------------------------------------------------
# Collect artefact info
# ---------------------------------------------------------------------------
artefact_rows=""
artefact_count=0
if [[ ${#ARTEFACTS_ARR[@]} -gt 0 ]]; then
    for f in "${ARTEFACTS_ARR[@]}"; do
        artefact_count=$((artefact_count + 1))
        if [[ -f "$f" ]]; then
            size=$(du -sh "$f" 2>/dev/null | awk '{print $1}')
            mtime=$(date -r "$f" "+%Y-%m-%d %H:%M" 2>/dev/null || echo "unknown")
            status_cell='<td class="pass">exists</td>'
        else
            size="—"
            mtime="—"
            status_cell='<td class="fail">missing</td>'
        fi
        rel_path="${f#$REPO_ROOT/}"
        artefact_rows+="<tr><td><code>$rel_path</code></td><td>$size</td>"
        artefact_rows+="<td>$mtime</td>$status_cell</tr>"
    done
fi

if [[ $artefact_count -eq 0 ]]; then
    artefact_rows='<tr><td colspan="4"><em>No artefacts specified</em></td></tr>'
fi

# ---------------------------------------------------------------------------
# Run QA checks and collect results
# ---------------------------------------------------------------------------
qa_rows=""
fail_count=0
warn_count=0
pass_count=0

_qa_row() {
    local level="$1" label="$2" detail="$3"
    qa_rows+="<tr><td class='${level,,}'>[$level]</td>"
    qa_rows+="<td>$label</td><td>$detail</td></tr>"
}

# Check 1: artefact existence
if [[ ${#ARTEFACTS_ARR[@]} -gt 0 ]]; then
    for f in "${ARTEFACTS_ARR[@]}"; do
        if [[ ! -f "$f" ]]; then
            _qa_row "FAIL" "Artefact existence" "Missing: ${f#$REPO_ROOT/}"
            fail_count=$((fail_count + 1))
        elif [[ ! -s "$f" ]]; then
            _qa_row "FAIL" "Artefact non-empty" "Empty file: ${f#$REPO_ROOT/}"
            fail_count=$((fail_count + 1))
        else
            _qa_row "PASS" "Artefact existence" "${f#$REPO_ROOT/}"
            pass_count=$((pass_count + 1))
        fi
    done
else
    _qa_row "WARN" "Artefact existence" "No artefacts provided — cannot verify"
    warn_count=$((warn_count + 1))
fi

# Check 2: NaN / Inf in CSV/text outputs
if [[ ${#ARTEFACTS_ARR[@]} -gt 0 ]]; then
    for f in "${ARTEFACTS_ARR[@]}"; do
        case "${f,,}" in
            *.csv|*.txt|*.tsv)
                if [[ -f "$f" ]] && grep -qiE 'nan|inf|#div|#ref' "$f" 2>/dev/null; then
                    _qa_row "WARN" "NaN/Inf check" \
                        "Suspicious values found in ${f#$REPO_ROOT/}"
                    warn_count=$((warn_count + 1))
                elif [[ -f "$f" ]]; then
                    _qa_row "PASS" "NaN/Inf check" "${f#$REPO_ROOT/} clean"
                    pass_count=$((pass_count + 1))
                fi
                ;;
        esac
    done
fi

# Check 3: unit consistency in CSV headers
if [[ ${#ARTEFACTS_ARR[@]} -gt 0 ]]; then
    for f in "${ARTEFACTS_ARR[@]}"; do
        case "${f,,}" in
            *.csv)
                if [[ -f "$f" ]]; then
                    header_line=$(head -1 "$f" 2>/dev/null || echo "")
                    mixed=$(echo "$header_line" \
                        | grep -oiE '\b(kN|MN|lbf|ton|kg)\b' \
                        | tr '[:upper:]' '[:lower:]' | sort -u | wc -l || echo 0)
                    if [[ "$mixed" -gt 2 ]]; then
                        _qa_row "WARN" "Unit consistency" \
                            "Multiple force units in ${f#$REPO_ROOT/} header"
                        warn_count=$((warn_count + 1))
                    elif [[ -n "$header_line" ]]; then
                        _qa_row "PASS" "Unit consistency" \
                            "${f#$REPO_ROOT/} header OK"
                        pass_count=$((pass_count + 1))
                    fi
                fi
                ;;
        esac
    done
fi

# Check 4: output type specific
case "$OUTPUT_TYPE" in
    rao-diffraction|calculation|mooring-analysis)
        _qa_row "INFO" "SME verification" \
            "Invoke /orcaflex-specialist or /hydrodynamic-analysis manually"
        ;;
    code)
        cov_file=$(find "$REPO_ROOT" -name "coverage.xml" \
            -not -path "*/.git/*" 2>/dev/null | head -1 || echo "")
        if [[ -n "$cov_file" ]]; then
            cov_rate=$(grep -oP 'line-rate="\K[0-9.]+' "$cov_file" \
                | head -1 || echo "0")
            cov_pct=$(awk -v r="$cov_rate" 'BEGIN { printf "%d", r * 100 }' 2>/dev/null || echo "0")
            if [[ "${cov_pct:-0}" -lt 80 ]]; then
                _qa_row "WARN" "Test coverage" "${cov_pct}% < 80% threshold"
                warn_count=$((warn_count + 1))
            else
                _qa_row "PASS" "Test coverage" "${cov_pct}% >= 80%"
                pass_count=$((pass_count + 1))
            fi
        else
            _qa_row "WARN" "Test coverage" "No coverage.xml found"
            warn_count=$((warn_count + 1))
        fi
        ;;
    mesh)
        _qa_row "INFO" "Mesh quality" \
            "Invoke /gmsh-meshing --verify for aspect ratio + watertight check"
        ;;
esac

# Check 5: WRK item has required frontmatter
if [[ -n "$WRK_FILE" ]]; then
    if grep -q "^plan_approved: true" "$WRK_FILE" 2>/dev/null; then
        _qa_row "PASS" "Plan gate" "plan_approved: true present"
        pass_count=$((pass_count + 1))
    else
        _qa_row "WARN" "Plan gate" "plan_approved: true not found in $WRK_ID.md"
        warn_count=$((warn_count + 1))
    fi
fi

# ---------------------------------------------------------------------------
# Determine verdict
# ---------------------------------------------------------------------------
if [[ $fail_count -gt 0 ]]; then
    VERDICT="FAIL"
    VERDICT_CLASS="fail"
    VERDICT_RATIONALE="$fail_count check(s) failed — resolve before marking complete"
elif [[ $warn_count -gt 0 ]]; then
    VERDICT="WARN"
    VERDICT_CLASS="warn"
    VERDICT_RATIONALE="$warn_count warning(s) noted — review before marking complete"
else
    VERDICT="PASS"
    VERDICT_CLASS="pass"
    VERDICT_RATIONALE="All automated checks passed ($pass_count checks)"
fi

# ---------------------------------------------------------------------------
# Process log content
# ---------------------------------------------------------------------------
process_log_html=""
if [[ -n "$PROCESS_LOG" ]] && [[ -f "$PROCESS_LOG" ]]; then
    log_content=$(cat "$PROCESS_LOG" \
        | sed 's/&/\&amp;/g; s/</\&lt;/g; s/>/\&gt;/g')
    process_log_html="<pre>$log_content</pre>"
else
    process_log_html="<p><em>No process log provided. Steps were recorded by the agent.</em></p>"
fi

# ---------------------------------------------------------------------------
# Write HTML report
# ---------------------------------------------------------------------------
cat > "$OUT_FILE" <<HTML
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>${REPORT_TITLE}</title>
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
         background: #f5f5f5; color: #1a1a1a; font-size: 14px; }
  header { background: #1e2a3a; color: #e8edf3; padding: 20px 32px;
           border-bottom: 3px solid #2e7eed; }
  header h1 { font-size: 20px; font-weight: 600; }
  header .meta { font-size: 12px; color: #9ab; margin-top: 4px; }
  main { max-width: 1100px; margin: 24px auto; padding: 0 16px; }
  section { background: #fff; border-radius: 6px; padding: 20px 24px;
            margin-bottom: 20px; box-shadow: 0 1px 4px rgba(0,0,0,.08); }
  h2 { font-size: 15px; font-weight: 600; color: #1e2a3a;
       border-bottom: 1px solid #e0e4ea; padding-bottom: 8px; margin-bottom: 14px; }
  table { width: 100%; border-collapse: collapse; font-size: 13px; }
  th { background: #f0f3f7; text-align: left; padding: 7px 10px;
       font-weight: 600; color: #444; border-bottom: 2px solid #d4dae3; }
  td { padding: 6px 10px; border-bottom: 1px solid #edf0f5; vertical-align: top; }
  tr:last-child td { border-bottom: none; }
  tr:hover td { background: #fafbfd; }
  code { font-family: "SFMono-Regular", Consolas, monospace;
         background: #f0f3f7; padding: 1px 5px; border-radius: 3px;
         font-size: 12px; }
  pre { background: #f5f7fa; border: 1px solid #dde2ea; border-radius: 4px;
        padding: 12px; overflow-x: auto; font-size: 12px; line-height: 1.5; }
  .pass  { color: #1a7f37; font-weight: 600; }
  .warn  { color: #a36200; font-weight: 600; }
  .fail  { color: #c0392b; font-weight: 600; }
  .info  { color: #2e7eed; font-weight: 600; }
  .verdict-box { border-radius: 6px; padding: 16px 24px; margin-top: 4px; }
  .verdict-box.pass { background: #eaf7ec; border-left: 5px solid #1a7f37; }
  .verdict-box.warn { background: #fff8e1; border-left: 5px solid #a36200; }
  .verdict-box.fail { background: #fdf0ef; border-left: 5px solid #c0392b; }
  .verdict-box .badge { font-size: 22px; font-weight: 700; margin-bottom: 6px; }
  .verdict-box .rationale { font-size: 13px; margin-top: 4px; }
  .kv { display: grid; grid-template-columns: 160px 1fr; row-gap: 6px; }
  .kv .k { color: #667; font-weight: 600; font-size: 12px; }
  .kv .v { font-size: 13px; }
</style>
</head>
<body>
<header>
  <h1>${REPORT_TITLE}</h1>
  <div class="meta">${WRK_ID} &nbsp;·&nbsp; Type: ${OUTPUT_TYPE}
    &nbsp;·&nbsp; Generated: ${REPORT_DATE}</div>
</header>
<main>

<!-- Section 1: Inputs -->
<section id="s1">
  <h2>Section 1 — Inputs</h2>
  <div class="kv">
    <span class="k">Work Item</span>  <span class="v">${WRK_ID}</span>
    <span class="k">Title</span>      <span class="v">${WRK_TITLE}</span>
    <span class="k">Status</span>     <span class="v">${WRK_STATUS}</span>
    <span class="k">Area</span>       <span class="v">${WRK_AREA}</span>
    <span class="k">Created</span>    <span class="v">${WRK_CREATED}</span>
    <span class="k">Output Type</span><span class="v">${OUTPUT_TYPE}</span>
    <span class="k">Repo Root</span>  <span class="v"><code>${REPO_ROOT}</code></span>
  </div>
</section>

<!-- Section 2: Process Log -->
<section id="s2">
  <h2>Section 2 — Process Log</h2>
  ${process_log_html}
</section>

<!-- Section 3: Outputs -->
<section id="s3">
  <h2>Section 3 — Output Artefacts</h2>
  <table>
    <thead>
      <tr><th>Path</th><th>Size</th><th>Modified</th><th>Status</th></tr>
    </thead>
    <tbody>
      ${artefact_rows}
    </tbody>
  </table>
</section>

<!-- Section 4: QA Checks -->
<section id="s4">
  <h2>Section 4 — QA Checks</h2>
  <table>
    <thead>
      <tr><th>Level</th><th>Check</th><th>Detail</th></tr>
    </thead>
    <tbody>
      ${qa_rows}
    </tbody>
  </table>
  <p style="margin-top:10px;font-size:12px;color:#667">
    Totals: <span class="pass">PASS ${pass_count}</span> &nbsp;
    <span class="warn">WARN ${warn_count}</span> &nbsp;
    <span class="fail">FAIL ${fail_count}</span>
  </p>
</section>

<!-- Section 5: Verdict -->
<section id="s5">
  <h2>Section 5 — QA Verdict</h2>
  <div class="verdict-box ${VERDICT_CLASS}">
    <div class="badge ${VERDICT_CLASS}">${VERDICT}</div>
    <div class="rationale">${VERDICT_RATIONALE}</div>
  </div>
</section>

</main>
</body>
</html>
HTML

echo "Report written: $OUT_FILE"
echo "Verdict: $VERDICT"

# Exit non-zero on FAIL so callers can gate on exit code
[[ "$VERDICT" == "FAIL" ]] && exit 1 || exit 0
