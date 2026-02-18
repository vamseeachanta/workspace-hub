#!/bin/bash
# Quick Start Examples for Doc2Context

echo "========================================"
echo "Doc2Context - Quick Start Examples"
echo "========================================"
echo ""

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DOC_CONVERTER="$SCRIPT_DIR/../scripts/doc-converter"

# Example 1: Single file
echo "Example 1: Convert single PDF file"
echo "-----------------------------------"
echo "Command:"
echo "  $DOC_CONVERTER document.pdf -o output.context.md"
echo ""

# Example 2: Directory with parallel processing
echo "Example 2: Process directory with parallel mode (8-20x speedup)"
echo "---------------------------------------------------------------"
echo "Command:"
echo "  $DOC_CONVERTER /docs -o /output --mode parallel --recursive"
echo ""
echo "Features:"
echo "  ✅ Auto-detects CPU cores"
echo "  ✅ Real-time progress tracking"
echo "  ✅ 8-20x faster than sequential"
echo ""

# Example 3: Swarm mode
echo "Example 3: Process with AI swarm orchestration (20-50x speedup)"
echo "----------------------------------------------------------------"
echo "Command:"
echo "  $DOC_CONVERTER /docs -o /output --mode swarm --recursive"
echo ""
echo "Features:"
echo "  ✅ Intelligent batching by file type"
echo "  ✅ Specialized agents (PDF, Excel, Word, HTML)"
echo "  ✅ Memory coordination across agents"
echo "  ✅ 20-50x faster than sequential"
echo ""

# Example 4: Benchmark
echo "Example 4: Compare all modes"
echo "-----------------------------"
echo "Command:"
echo "  $DOC_CONVERTER /docs -o /output --mode benchmark --recursive"
echo ""
echo "Output:"
echo "  📊 Performance comparison of all three modes"
echo "  🏆 Automatic recommendation for your workload"
echo ""

# Example 5: Advanced options
echo "Example 5: Advanced swarm options"
echo "----------------------------------"
echo "Commands:"
echo ""
echo "  # Mesh topology (fault-tolerant)"
echo "  $DOC_CONVERTER /docs -o /output --mode swarm \\"
echo "    --topology mesh --max-agents 10 --recursive"
echo ""
echo "  # Adaptive topology (dynamic)"
echo "  $DOC_CONVERTER /docs -o /output --mode swarm \\"
echo "    --topology adaptive --recursive"
echo ""
echo "  # Without neural learning (faster)"
echo "  $DOC_CONVERTER /docs -o /output --mode swarm \\"
echo "    --no-neural --recursive"
echo ""

echo "========================================"
echo "For detailed help:"
echo "  $DOC_CONVERTER --help"
echo "  $DOC_CONVERTER --help-parallel"
echo "  $DOC_CONVERTER --help-swarm"
echo "========================================"
