#!/bin/bash
# Example: Benchmark all processing modes

echo "========================================"
echo "Doc2Context Performance Benchmark"
echo "========================================"
echo ""

# Check if test directory provided
if [ -z "$1" ]; then
    echo "Usage: $0 <test_directory>"
    echo ""
    echo "Example:"
    echo "  $0 /path/to/test/documents"
    exit 1
fi

TEST_DIR="$1"
OUTPUT_BASE="/tmp/doc2context_benchmark"

# Validate test directory
if [ ! -d "$TEST_DIR" ]; then
    echo "❌ Error: Directory not found: $TEST_DIR"
    exit 1
fi

# Count files
FILE_COUNT=$(find "$TEST_DIR" -type f \( -name "*.pdf" -o -name "*.docx" -o -name "*.xlsx" -o -name "*.html" \) | wc -l)

echo "📊 Test Configuration:"
echo "   Input Directory: $TEST_DIR"
echo "   Documents Found: $FILE_COUNT"
echo "   CPU Cores: $(nproc)"
echo ""

if [ "$FILE_COUNT" -lt 10 ]; then
    echo "⚠️  Warning: Small batch size ($FILE_COUNT files)"
    echo "   Parallel overhead may not show benefits"
    echo "   Consider using a larger test set (50+ files)"
    echo ""
fi

# Create output directory
mkdir -p "$OUTPUT_BASE"

echo "Starting benchmark..."
echo ""

# Run benchmark
cd "$(dirname "$0")/.." || exit 1

./scripts/doc-converter "$TEST_DIR" \
    -o "$OUTPUT_BASE" \
    --mode benchmark \
    --recursive \
    --mirror-structure

echo ""
echo "========================================"
echo "Benchmark Complete!"
echo "========================================"
echo ""
echo "Results saved to: $OUTPUT_BASE"
echo ""
echo "Compare outputs:"
echo "  Sequential: $OUTPUT_BASE""_sequential/"
echo "  Parallel:   $OUTPUT_BASE""_parallel/"
echo "  Swarm:      $OUTPUT_BASE""_swarm/"
