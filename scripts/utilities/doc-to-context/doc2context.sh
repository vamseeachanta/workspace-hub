#!/usr/bin/env bash
#
# doc2context.sh - Wrapper script for documentation-to-context converter
# Provides convenient CLI interface and UV environment management
#

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/../../lib/python-resolver.sh"
PYTHON_SCRIPT="$SCRIPT_DIR/src/doc_to_context.py"
REQUIREMENTS="$SCRIPT_DIR/requirements.txt"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Print colored message
print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if UV is installed
check_uv() {
    if ! command -v uv &> /dev/null; then
        print_warn "UV not found. Install with: pip install uv"
        return 1
    fi
    return 0
}

# Setup environment with UV
setup_env() {
    if check_uv; then
        print_info "Setting up environment with UV..."
        cd "$SCRIPT_DIR"

        # Create virtual environment if it doesn't exist
        if [ ! -d ".venv" ]; then
            print_info "Creating virtual environment..."
            uv venv
        fi

        # Install dependencies
        print_info "Installing dependencies..."
        uv pip install -r "$REQUIREMENTS"

        print_info "Environment ready!"
    else
        print_warn "Falling back to pip..."
        ${PYTHON} -m pip install -r "$REQUIREMENTS"
    fi
}

# Check system dependencies
check_system_deps() {
    local missing_deps=()

    # Check Tesseract for OCR
    if ! command -v tesseract &> /dev/null; then
        missing_deps+=("tesseract-ocr (for PDF OCR support)")
    fi

    # Check Poppler for PDF to image conversion
    if ! command -v pdftoppm &> /dev/null; then
        missing_deps+=("poppler-utils (for PDF image conversion)")
    fi

    if [ ${#missing_deps[@]} -gt 0 ]; then
        print_warn "Optional dependencies missing:"
        for dep in "${missing_deps[@]}"; do
            echo "  - $dep"
        done
        echo ""
        echo "Install instructions:"
        echo "  Ubuntu/Debian: sudo apt-get install tesseract-ocr poppler-utils"
        echo "  macOS: brew install tesseract poppler"
        echo ""
    fi
}

# Run the converter
run_converter() {
    if [ -d "$SCRIPT_DIR/.venv" ]; then
        source "$SCRIPT_DIR/.venv/bin/activate"
    fi

    ${PYTHON} "$PYTHON_SCRIPT" "$@"
}

# Main script
main() {
    if [ $# -eq 0 ]; then
        print_error "No input files specified"
        echo ""
        echo "Usage: $0 [options] <input_file(s)>"
        echo ""
        echo "Options:"
        echo "  --setup              Setup environment and install dependencies"
        echo "  --check-deps         Check system dependencies"
        echo "  -o, --output FILE    Output file path"
        echo "  -f, --format FORMAT  Output format (markdown|json)"
        echo "  -b, --batch          Batch mode for multiple files"
        echo ""
        echo "Examples:"
        echo "  $0 document.pdf"
        echo "  $0 report.docx -o context.md"
        echo "  $0 *.pdf -b"
        echo ""
        exit 1
    fi

    # Handle special commands
    case "${1:-}" in
        --setup)
            setup_env
            check_system_deps
            exit 0
            ;;
        --check-deps)
            check_system_deps
            exit 0
            ;;
        --help|-h)
            ${PYTHON} "$PYTHON_SCRIPT" --help
            exit 0
            ;;
    esac

    # Run converter
    run_converter "$@"
}

main "$@"
