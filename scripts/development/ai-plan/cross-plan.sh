#!/usr/bin/env bash
# ABOUTME: Dispatches parallel plan generation to 3 AI CLIs (Claude, Codex, Gemini).
# ABOUTME: Merges results via structured diff: auto-merge agreed sections, LLM synthesis for divergent.

set -e

# ---------------------------------------------------------------------------
# Colors (matching cross-review-loop.sh)
# ---------------------------------------------------------------------------
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
NC='\033[0m' # No Color

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
MIN_PLAN_BYTES=50        # Minimum bytes for valid plan output (Codex NO_OUTPUT threshold)
MIN_PROVIDERS=2          # Minimum successful plans required for merge
SYNTHESIS_AGENT="claude" # Agent used for synthesizing divergent sections (per D-03)
PLAN_SECTIONS=(objective tasks verification success_criteria)
PROVIDER_TIMEOUT=120     # Per-provider timeout in seconds
DRY_RUN=false
VERBOSE=false
PHASE=""
PROMPT_FILE=""
OUTPUT_FILE=""
TIER="COMPLEX"

# Detect workspace-hub root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"

# ---------------------------------------------------------------------------
# Usage
# ---------------------------------------------------------------------------
usage() {
    echo -e "${CYAN}Cross-Plan — Parallel Multi-AI Plan Generation${NC}"
    echo ""
    echo "Dispatches planning prompts to Claude, Codex, and Gemini in parallel,"
    echo "then merges independently-produced plans via structured diff."
    echo ""
    echo "Usage: $(basename "$0") [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --phase PHASE       Phase number or slug (required)"
    echo "  --prompt FILE       Path to planning prompt file (required)"
    echo "  --output FILE       Path for merged output plan (required)"
    echo "  --tier TIER         Route tier: SIMPLE|STANDARD|COMPLEX|REASONING (default: COMPLEX)"
    echo "  --dry-run           Mock CLI calls, test dispatch + merge logic"
    echo "  --verbose           Show detailed progress"
    echo "  -h, --help          Show help"
    echo ""
    echo "Examples:"
    echo "  $(basename "$0") --phase 1000 --prompt /tmp/plan-prompt.md --output /tmp/merged-plan.md"
    echo "  $(basename "$0") --phase 1000 --prompt /tmp/plan-prompt.md --output /tmp/merged-plan.md --dry-run"
    echo ""
    echo "Requirements:"
    echo "  At least $MIN_PROVIDERS of 3 AI CLIs must be available (claude, codex, gemini)."
    echo "  Plans with fewer than $MIN_PLAN_BYTES bytes are treated as NO_OUTPUT."
    exit 0
}

# ---------------------------------------------------------------------------
# Logging helpers
# ---------------------------------------------------------------------------
log_info()    { echo -e "${BLUE}[INFO]  $1${NC}"; }
log_success() { echo -e "${GREEN}[OK]    $1${NC}"; }
log_warning() { echo -e "${YELLOW}[WARN]  $1${NC}"; }
log_error()   { echo -e "${RED}[ERROR] $1${NC}" >&2; }
log_verbose() { [[ "$VERBOSE" == "true" ]] && echo -e "${MAGENTA}[DEBUG] $1${NC}" || true; }

# ---------------------------------------------------------------------------
# Argument parsing
# ---------------------------------------------------------------------------
parse_args() {
    while [[ $# -gt 0 ]]; do
        case "$1" in
            --phase)
                PHASE="$2"
                shift 2
                ;;
            --prompt)
                PROMPT_FILE="$2"
                shift 2
                ;;
            --output)
                OUTPUT_FILE="$2"
                shift 2
                ;;
            --tier)
                TIER="$2"
                shift 2
                ;;
            --dry-run)
                DRY_RUN=true
                shift
                ;;
            --verbose)
                VERBOSE=true
                shift
                ;;
            -h|--help)
                usage
                ;;
            *)
                log_error "Unknown option: $1"
                echo "Run $(basename "$0") --help for usage."
                exit 1
                ;;
        esac
    done

    # Validate required arguments
    if [[ -z "$PHASE" ]]; then
        log_error "Missing required argument: --phase"
        exit 1
    fi
    if [[ -z "$PROMPT_FILE" ]]; then
        log_error "Missing required argument: --prompt"
        exit 1
    fi
    if [[ ! -f "$PROMPT_FILE" ]]; then
        log_error "Prompt file not found: $PROMPT_FILE"
        exit 1
    fi
    if [[ -z "$OUTPUT_FILE" ]]; then
        log_error "Missing required argument: --output"
        exit 1
    fi
}

# ---------------------------------------------------------------------------
# Temp directory with cleanup trap
# ---------------------------------------------------------------------------
setup_tmpdir() {
    TMPDIR=$(mktemp -d "/tmp/gsd-cross-plan-XXXXXX")
    trap 'rm -rf "$TMPDIR"' EXIT
    log_verbose "Temp directory: $TMPDIR"
}

# ---------------------------------------------------------------------------
# CLI availability check
# ---------------------------------------------------------------------------
declare -a AVAILABLE_PROVIDERS=()

detect_clis() {
    local count=0

    if [[ "$DRY_RUN" == "true" ]]; then
        # In dry-run mode, assume all providers are available (CLI calls are mocked)
        AVAILABLE_PROVIDERS=(claude codex gemini)
        count=3
        log_info "DRY-RUN: all 3 providers assumed available (CLI calls are mocked)"
        return 0
    fi

    for provider in claude codex gemini; do
        if command -v "$provider" >/dev/null 2>&1; then
            AVAILABLE_PROVIDERS+=("$provider")
            ((count++)) || true
            log_verbose "Found CLI: $provider"
        else
            log_warning "CLI not found: $provider"
        fi
    done

    if [[ $count -lt $MIN_PROVIDERS ]]; then
        log_error "Insufficient AI CLIs available: found $count, need at least $MIN_PROVIDERS"
        log_error "Available: ${AVAILABLE_PROVIDERS[*]:-none}"
        exit 1
    fi

    log_info "Available providers: ${AVAILABLE_PROVIDERS[*]} ($count/3)"
}

# ---------------------------------------------------------------------------
# dispatch_plan() — run a single provider's planning invocation
# ---------------------------------------------------------------------------
dispatch_plan() {
    local provider="$1"
    local tmpdir="$2"
    local prompt_file="$3"
    local output_file="$tmpdir/${provider}-plan.md"
    local err_file="$tmpdir/${provider}-err.log"

    if [[ "$DRY_RUN" == "true" ]]; then
        # Mock output: copy prompt file as plan (simulates a provider that echoes input)
        cp "$prompt_file" "$output_file"
        echo "[DRY-RUN] $provider plan generated ($(date -Iseconds))" > "$err_file"
        return 0
    fi

    # Prompt delivery strategy per provider:
    # - claude: embed file content in -p argument (avoids stdin pipe issues in
    #   background subshells; prefix instruction prevents "---" being parsed as flag)
    # - codex:  pipe via stdin with "-" sentinel (codex explicitly supports this)
    # - gemini: pipe via stdin with -p instruction (gemini -p "val" conflicts
    #   with positional args, so prompt goes through stdin; -p triggers headless mode)
    local plan_instruction="Generate a plan based on the following input. Preserve the XML section tags (objective, tasks, verification, success_criteria)."
    local prompt_content
    prompt_content=$(cat "$prompt_file")

    # Run each provider from /tmp to avoid workspace CLAUDE.md / skills loading
    # overhead — plan generation is a pure-LLM task with no file system context needed.
    case "$provider" in
        claude)
            (cd /tmp && timeout "$PROVIDER_TIMEOUT" claude -p "${plan_instruction}

${prompt_content}" --max-turns 2 </dev/null) > "$output_file" 2>"$err_file"
            ;;
        codex)
            (cd /tmp && echo "$prompt_content" | timeout "$PROVIDER_TIMEOUT" codex exec --skip-git-repo-check -) > "$output_file" 2>"$err_file"
            ;;
        gemini)
            (cd /tmp && echo "$prompt_content" | timeout "$PROVIDER_TIMEOUT" gemini -p "$plan_instruction") > "$output_file" 2>"$err_file"
            # Detect exit-0-on-capacity-error: gemini returns 0 but empty stdout (#1326)
            local _gout_size; _gout_size=$(wc -c < "$output_file" 2>/dev/null || echo 0)
            if [[ $_gout_size -lt $MIN_PLAN_BYTES ]] && grep -qE "RESOURCE_EXHAUSTED|MODEL_CAPACITY_EXHAUSTED|429" "$err_file" 2>/dev/null; then
                log_warning "gemini: capacity exhausted (exit 0 but empty stdout), retrying with gemini-2.5-flash"
                (cd /tmp && echo "$prompt_content" | timeout "$PROVIDER_TIMEOUT" gemini -p "$plan_instruction" -m gemini-2.5-flash) > "$output_file" 2>"$err_file"
            fi
            ;;
        *)
            log_error "Unknown provider: $provider"
            return 1
            ;;
    esac
}

# ---------------------------------------------------------------------------
# Parallel dispatch with PID tracking
# ---------------------------------------------------------------------------
declare -A PIDS=()
declare -A EXIT_CODES=()
declare -a SUCCESSFUL_PROVIDERS=()

run_parallel_dispatch() {
    echo ""
    echo -e "${CYAN}Dispatching parallel plans to ${#AVAILABLE_PROVIDERS[@]} providers...${NC}"
    echo ""

    for provider in "${AVAILABLE_PROVIDERS[@]}"; do
        dispatch_plan "$provider" "$TMPDIR" "$PROMPT_FILE" &
        PIDS[$provider]=$!
        echo -e "  ${BLUE}Started ${provider} (PID ${PIDS[$provider]})${NC}"
    done

    echo ""
    log_info "Waiting for all providers to complete..."
    echo ""

    for provider in "${!PIDS[@]}"; do
        if wait "${PIDS[$provider]}" 2>/dev/null; then
            EXIT_CODES[$provider]=0
            echo -e "  ${GREEN}${provider} completed successfully${NC}"
        else
            EXIT_CODES[$provider]=$?
            echo -e "  ${YELLOW}${provider} failed (exit ${EXIT_CODES[$provider]})${NC}"
        fi
    done

    echo ""
}

# ---------------------------------------------------------------------------
# Validate provider outputs
# ---------------------------------------------------------------------------
validate_outputs() {
    local valid_count=0

    for provider in "${AVAILABLE_PROVIDERS[@]}"; do
        local plan_file="$TMPDIR/${provider}-plan.md"

        # Check exit code
        if [[ "${EXIT_CODES[$provider]:-1}" -ne 0 ]]; then
            log_warning "$provider: process failed (exit ${EXIT_CODES[$provider]})"
            continue
        fi

        # Check file exists
        if [[ ! -f "$plan_file" ]]; then
            log_warning "$provider: no output file generated"
            continue
        fi

        # Check file size (Codex NO_OUTPUT threshold)
        local file_size
        file_size=$(wc -c < "$plan_file" 2>/dev/null || echo 0)
        if [[ $file_size -lt $MIN_PLAN_BYTES ]]; then
            log_warning "$provider: output too small (${file_size} bytes < ${MIN_PLAN_BYTES} threshold) — treating as NO_OUTPUT"
            continue
        fi

        SUCCESSFUL_PROVIDERS+=("$provider")
        ((valid_count++)) || true
        log_success "$provider: valid plan output (${file_size} bytes)"
    done

    echo ""

    if [[ $valid_count -lt $MIN_PROVIDERS ]]; then
        log_error "Insufficient valid plans: $valid_count successful, need at least $MIN_PROVIDERS"
        log_error "Successful: ${SUCCESSFUL_PROVIDERS[*]:-none}"
        for provider in "${AVAILABLE_PROVIDERS[@]}"; do
            local err_file="$TMPDIR/${provider}-err.log"
            if [[ -f "$err_file" ]] && [[ -s "$err_file" ]]; then
                log_error "  $provider errors: $(head -3 "$err_file")"
            fi
        done
        exit 1
    fi

    log_info "Valid plans: $valid_count/${#AVAILABLE_PROVIDERS[@]} (minimum: $MIN_PROVIDERS)"
}

# ---------------------------------------------------------------------------
# Section extraction functions (per D-04: structured diff pre-filtering)
# ---------------------------------------------------------------------------
extract_section() {
    local file="$1" tag="$2"
    # Extract content between <tag> and </tag>, excluding the tags themselves.
    # Handles both single-line (<tag>content</tag>) and multi-line forms.
    # NOTE: GNU sed range /<start>/,/<end>/ does NOT close when both match
    # the same line, so we detect single-line form first.

    # Check for single-line form: <tag>content</tag> on one line
    local single_line
    single_line=$(grep "<${tag}>.*</${tag}>" "$file" 2>/dev/null || true)
    if [[ -n "$single_line" ]]; then
        echo "$single_line" | sed "s/.*<${tag}>//;s/<\/${tag}>.*//"
        return 0
    fi

    # Multi-line form: extract lines between <tag> and </tag>
    local raw
    raw=$(sed -n "/<${tag}>/,/<\/${tag}>/p" "$file" 2>/dev/null || true)
    if [[ -z "$raw" ]]; then
        return 0
    fi

    # Strip the opening and closing tag lines
    echo "$raw" | sed '1d;$d'
}

extract_frontmatter() {
    local file="$1"
    # Extract YAML between first --- and second ---
    awk '/^---$/{c++; if(c==2) exit; next} c==1{print}' "$file"
}

# ---------------------------------------------------------------------------
# compare_sections() — categorize sections as AGREED or DIVERGENT
# ---------------------------------------------------------------------------
declare -a AGREED_SECTIONS=()
declare -a DIVERGENT_SECTIONS=()

compare_sections() {
    local diff_threshold=5  # Lines of diff below which sections are considered agreed

    log_info "Comparing plan sections across ${#SUCCESSFUL_PROVIDERS[@]} providers..."
    echo ""

    for section in "${PLAN_SECTIONS[@]}"; do
        log_verbose "Comparing section: $section"

        # Extract the section from each successful provider
        local -a section_files=()
        local extracted_count=0

        for provider in "${SUCCESSFUL_PROVIDERS[@]}"; do
            local plan_file="$TMPDIR/${provider}-plan.md"
            local section_file="$TMPDIR/${provider}-section-${section}.txt"

            extract_section "$plan_file" "$section" > "$section_file"

            if [[ -s "$section_file" ]]; then
                section_files+=("$section_file")
                ((extracted_count++)) || true
            else
                log_verbose "  $provider: no content for <$section>"
            fi
        done

        # Need at least 2 sections to compare
        if [[ $extracted_count -lt 2 ]]; then
            if [[ $extracted_count -eq 1 ]]; then
                log_verbose "  Only 1 provider has <$section>; treating as AGREED (single source)"
                AGREED_SECTIONS+=("$section")
            else
                log_verbose "  No providers have <$section>; skipping"
            fi
            continue
        fi

        # Compare all pairs — if max diff < threshold, treat as AGREED
        local max_diff_lines=0
        local base_file="${section_files[0]}"

        for ((i=1; i<${#section_files[@]}; i++)); do
            local diff_lines
            diff_lines=$(diff "$base_file" "${section_files[$i]}" 2>/dev/null | wc -l || echo 999)
            if [[ $diff_lines -gt $max_diff_lines ]]; then
                max_diff_lines=$diff_lines
            fi
        done

        if [[ $max_diff_lines -lt $diff_threshold ]]; then
            AGREED_SECTIONS+=("$section")
            echo -e "  ${GREEN}$section: AGREED${NC} (diff: $max_diff_lines lines)"
        else
            DIVERGENT_SECTIONS+=("$section")
            echo -e "  ${YELLOW}$section: DIVERGENT${NC} (diff: $max_diff_lines lines)"
        fi
    done

    echo ""
    log_info "Agreed sections: ${#AGREED_SECTIONS[@]}  |  Divergent sections: ${#DIVERGENT_SECTIONS[@]}"
}

# ---------------------------------------------------------------------------
# merge_plans() — auto-merge agreed sections, synthesize divergent ones
# ---------------------------------------------------------------------------
merge_plans() {
    log_info "Merging plans..."
    echo ""

    # Use the first successful provider as the base for frontmatter
    # Prefer Claude if available (synthesis agent per D-03), else first available
    local base_provider="${SUCCESSFUL_PROVIDERS[0]}"
    for p in "${SUCCESSFUL_PROVIDERS[@]}"; do
        if [[ "$p" == "claude" ]]; then
            base_provider="claude"
            break
        fi
    done

    local base_plan="$TMPDIR/${base_provider}-plan.md"
    local merged_file="$TMPDIR/merged-plan.md"

    # Start with frontmatter from the base provider
    local frontmatter
    frontmatter=$(extract_frontmatter "$base_plan")
    if [[ -n "$frontmatter" ]]; then
        {
            echo "---"
            echo "$frontmatter"
            echo "---"
            echo ""
        } > "$merged_file"
    else
        : > "$merged_file"
    fi

    # Process each section
    for section in "${PLAN_SECTIONS[@]}"; do
        local section_content=""

        # Check if this section is agreed or divergent
        local is_agreed=false
        for a in "${AGREED_SECTIONS[@]}"; do
            if [[ "$a" == "$section" ]]; then
                is_agreed=true
                break
            fi
        done

        if [[ "$is_agreed" == "true" ]]; then
            # AGREED: take the base provider's version
            section_content=$(extract_section "$base_plan" "$section")
            log_success "Auto-merged <$section> (agreed across providers)"
        else
            # Check if this section is in DIVERGENT_SECTIONS
            local is_divergent=false
            for d in "${DIVERGENT_SECTIONS[@]}"; do
                if [[ "$d" == "$section" ]]; then
                    is_divergent=true
                    break
                fi
            done

            if [[ "$is_divergent" == "true" ]]; then
                # DIVERGENT: synthesize from all providers
                section_content=$(synthesize_section "$section")
                if [[ -n "$section_content" ]]; then
                    log_success "Synthesized <$section> (divergent — merged via $SYNTHESIS_AGENT)"
                else
                    # Fallback to base provider
                    section_content=$(extract_section "$base_plan" "$section")
                    log_warning "Synthesis failed for <$section>; using ${base_provider}'s version"
                fi
            else
                # Section not found in comparison — take from base if available
                section_content=$(extract_section "$base_plan" "$section")
                if [[ -n "$section_content" ]]; then
                    log_verbose "Section <$section> from base provider (not compared)"
                fi
            fi
        fi

        # Append section to merged file
        if [[ -n "$section_content" ]]; then
            {
                echo "<${section}>"
                echo "$section_content"
                echo "</${section}>"
                echo ""
            } >> "$merged_file"
        fi
    done

    # Copy merged file to output
    cp "$merged_file" "$OUTPUT_FILE"
    log_success "Merged plan written to: $OUTPUT_FILE"
}

# ---------------------------------------------------------------------------
# synthesize_section() — call synthesis agent for a divergent section
# ---------------------------------------------------------------------------
synthesize_section() {
    local section="$1"
    local synthesis_prompt=""

    # Build the synthesis prompt with each provider's version
    synthesis_prompt="You are merging independently-created plan sections for Phase ${PHASE}.

## Section: ${section}

"

    local provider_count=0
    for provider in "${SUCCESSFUL_PROVIDERS[@]}"; do
        local section_file="$TMPDIR/${provider}-section-${section}.txt"
        if [[ -f "$section_file" ]] && [[ -s "$section_file" ]]; then
            local content
            content=$(cat "$section_file")
            synthesis_prompt+="### ${provider}'s version:
${content}

"
            ((provider_count++)) || true
        fi
    done

    # Need at least 2 versions to synthesize
    if [[ $provider_count -lt 2 ]]; then
        log_verbose "Only $provider_count versions for <$section>; skipping synthesis"
        return 1
    fi

    synthesis_prompt+="## Instructions
Synthesize the best version. Prefer:
1. The most specific and actionable version
2. The version with better task decomposition
3. Combined insights where approaches complement
Output ONLY the merged section content (no wrapper tags, no explanation)."

    if [[ "$DRY_RUN" == "true" ]]; then
        # In dry-run mode, return the first provider's version instead of calling LLM
        local first_provider="${SUCCESSFUL_PROVIDERS[0]}"
        local first_section="$TMPDIR/${first_provider}-section-${section}.txt"
        if [[ -f "$first_section" ]]; then
            cat "$first_section"
        fi
        log_verbose "[DRY-RUN] Synthesis for <$section> — using ${first_provider}'s version"
        return 0
    fi

    # Call synthesis agent
    local synthesis_output
    synthesis_output=$(claude -p "$synthesis_prompt" 2>/dev/null) || {
        log_warning "Synthesis agent failed for section <$section>"
        return 1
    }

    # Validate synthesis output
    local output_size=${#synthesis_output}
    if [[ $output_size -lt 10 ]]; then
        log_warning "Synthesis produced empty output for <$section>"
        return 1
    fi

    echo "$synthesis_output"
}

# ---------------------------------------------------------------------------
# check_structure() — validate plan has extractable sections; fallback if not
# ---------------------------------------------------------------------------
check_structure() {
    local needs_full_synthesis=false
    local providers_with_tags=0

    for provider in "${SUCCESSFUL_PROVIDERS[@]}"; do
        local plan_file="$TMPDIR/${provider}-plan.md"
        local tag_count=0

        for section in "${PLAN_SECTIONS[@]}"; do
            if grep -q "<${section}>" "$plan_file" 2>/dev/null; then
                ((tag_count++)) || true
            fi
        done

        if [[ $tag_count -ge 2 ]]; then
            ((providers_with_tags++)) || true
        else
            log_warning "$provider: only $tag_count/${#PLAN_SECTIONS[@]} section tags found (possible malformed output)"
        fi
    done

    if [[ $providers_with_tags -lt 2 ]]; then
        log_warning "Fewer than 2 providers produced well-structured output."
        log_warning "Falling back to full-plan synthesis."
        needs_full_synthesis=true
    fi

    echo "$needs_full_synthesis"
}

# ---------------------------------------------------------------------------
# full_plan_synthesis() — when structured extraction fails, synthesize entire plans
# ---------------------------------------------------------------------------
full_plan_synthesis() {
    log_info "Running full-plan synthesis (structured extraction failed)..."

    local synthesis_prompt="You are merging independently-created plans for Phase ${PHASE}.

"

    for provider in "${SUCCESSFUL_PROVIDERS[@]}"; do
        local plan_file="$TMPDIR/${provider}-plan.md"
        if [[ -f "$plan_file" ]]; then
            local content
            content=$(cat "$plan_file")
            synthesis_prompt+="### ${provider}'s plan:
${content}

"
        fi
    done

    synthesis_prompt+="## Instructions
Synthesize the best plan. Preserve the PLAN.md template format with XML tags
(<objective>, <tasks>, <verification>, <success_criteria>). Prefer:
1. The most specific and actionable version
2. The version with better task decomposition
3. Combined insights where approaches complement
Output the complete merged plan (frontmatter + all sections)."

    if [[ "$DRY_RUN" == "true" ]]; then
        # In dry-run, use the first provider's full plan
        local first_provider="${SUCCESSFUL_PROVIDERS[0]}"
        cp "$TMPDIR/${first_provider}-plan.md" "$OUTPUT_FILE"
        log_verbose "[DRY-RUN] Full synthesis — using ${first_provider}'s plan"
        return 0
    fi

    local result
    result=$(claude -p "$synthesis_prompt" 2>/dev/null) || {
        log_error "Full-plan synthesis failed. Using base provider's plan as-is."
        local base_provider="${SUCCESSFUL_PROVIDERS[0]}"
        cp "$TMPDIR/${base_provider}-plan.md" "$OUTPUT_FILE"
        return 0
    }

    echo "$result" > "$OUTPUT_FILE"
    log_success "Full-plan synthesis complete."
}

# ---------------------------------------------------------------------------
# print_summary() — final status output
# ---------------------------------------------------------------------------
print_summary() {
    local provider_count=${#SUCCESSFUL_PROVIDERS[@]}
    local total_providers=${#AVAILABLE_PROVIDERS[@]}
    local agreed_count=${#AGREED_SECTIONS[@]}
    local divergent_count=${#DIVERGENT_SECTIONS[@]}

    echo ""
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${CYAN} CROSS-PLAN COMPLETE -- Phase ${PHASE}${NC}"
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    echo -e "  ${BLUE}Providers:${NC}     ${provider_count}/${total_providers} successful"
    echo -e "  ${BLUE}Agreed:${NC}        ${agreed_count} sections (auto-merged)"
    echo -e "  ${BLUE}Divergent:${NC}     ${divergent_count} sections (synthesized)"
    echo -e "  ${BLUE}Output:${NC}        ${OUTPUT_FILE}"
    if [[ "$DRY_RUN" == "true" ]]; then
        echo -e "  ${YELLOW}Mode:${NC}          DRY-RUN (no live API calls)"
    fi
    echo ""
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
}

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
main() {
    parse_args "$@"
    setup_tmpdir

    echo ""
    echo -e "${CYAN}Cross-Plan — Phase ${PHASE}${NC}"
    echo -e "${CYAN}Tier: ${TIER}  |  Prompt: ${PROMPT_FILE}${NC}"
    if [[ "$DRY_RUN" == "true" ]]; then
        echo -e "${YELLOW}*** DRY-RUN MODE — no live API calls ***${NC}"
    fi
    echo ""

    # Step 1: Detect available CLIs
    detect_clis

    # Step 2: Dispatch plans in parallel
    run_parallel_dispatch

    # Step 3: Validate outputs
    validate_outputs

    # Step 4: Check structure and decide merge strategy
    local needs_full_synthesis
    needs_full_synthesis=$(check_structure)

    if [[ "$needs_full_synthesis" == "true" ]]; then
        # Fallback: full-plan synthesis
        full_plan_synthesis
    else
        # Step 5: Compare sections
        compare_sections

        # Step 6: Merge (auto-merge agreed, synthesize divergent)
        merge_plans
    fi

    # Step 7: Summary
    print_summary
}

main "$@"
