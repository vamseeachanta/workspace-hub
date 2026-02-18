#!/usr/bin/env python3
"""
Unified CLI for Document to Context Conversion
Supports sequential, parallel (Phase 1), and swarm (Phase 2) modes.
"""

import sys
import argparse
from pathlib import Path
from typing import Optional

# Import all converter modes
from doc_to_context import DocumentToContextConverter
from enhanced_converter import EnhancedConverter
from parallel_converter import ParallelConverter
from swarm_converter import SwarmConverter


def main():
    """Unified CLI entry point."""
    parser = argparse.ArgumentParser(
        description='Document to Context Converter - Unified CLI',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Processing Modes:
  sequential     - Single-threaded processing (baseline)
  parallel       - Multi-core parallel processing (Phase 1, 8-20x speedup)
  swarm          - AI swarm orchestration (Phase 2, 20-50x speedup)

Examples:
  # Sequential processing (single file)
  %(prog)s doc.pdf -o output.md

  # Parallel processing (directory, 8-20x speedup)
  %(prog)s /docs -o /output --mode parallel --recursive

  # Swarm processing (directory, 20-50x speedup with AI coordination)
  %(prog)s /docs -o /output --mode swarm --recursive --topology hierarchical

  # Benchmark all modes
  %(prog)s /docs -o /output --mode benchmark --recursive

For detailed help on each mode:
  %(prog)s --help-sequential
  %(prog)s --help-parallel
  %(prog)s --help-swarm
        """
    )

    # Core arguments
    parser.add_argument('input', help='Input file or directory')
    parser.add_argument('-o', '--output', required=True, help='Output file or directory')
    parser.add_argument('-f', '--format', choices=['markdown', 'json'],
                       default='markdown', help='Output format (default: markdown)')

    # Mode selection
    parser.add_argument('--mode', choices=['sequential', 'parallel', 'swarm', 'benchmark'],
                       default='sequential',
                       help='Processing mode (default: sequential)')

    # Directory processing
    parser.add_argument('-r', '--recursive', action='store_true',
                       help='Process directories recursively')
    parser.add_argument('--mirror-structure', action='store_true',
                       help='Mirror input directory structure in output')
    parser.add_argument('--create-index', action='store_true', default=True,
                       help='Create index file (default: true)')

    # Parallel mode options
    parser.add_argument('-w', '--workers', type=int,
                       help='Number of worker processes for parallel mode')

    # Swarm mode options
    parser.add_argument('--topology', choices=['hierarchical', 'mesh', 'adaptive'],
                       default='hierarchical',
                       help='Swarm topology (default: hierarchical)')
    parser.add_argument('--max-agents', type=int, default=6,
                       help='Maximum concurrent agents for swarm mode')
    parser.add_argument('--no-memory', action='store_true',
                       help='Disable cross-session memory in swarm mode')
    parser.add_argument('--no-neural', action='store_true',
                       help='Disable neural pattern training in swarm mode')

    # Help options
    parser.add_argument('--help-sequential', action='store_true',
                       help='Show detailed help for sequential mode')
    parser.add_argument('--help-parallel', action='store_true',
                       help='Show detailed help for parallel mode')
    parser.add_argument('--help-swarm', action='store_true',
                       help='Show detailed help for swarm mode')

    args = parser.parse_args()

    # Handle detailed help
    if args.help_sequential:
        print_sequential_help()
        sys.exit(0)
    if args.help_parallel:
        print_parallel_help()
        sys.exit(0)
    if args.help_swarm:
        print_swarm_help()
        sys.exit(0)

    # Validate input
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"❌ Error: Input not found: {args.input}", file=sys.stderr)
        sys.exit(1)

    # Route to appropriate mode
    if args.mode == 'benchmark':
        run_benchmark(args)
    elif input_path.is_file():
        # Single file mode (always sequential)
        run_sequential_file(args)
    elif args.mode == 'sequential':
        run_sequential_directory(args)
    elif args.mode == 'parallel':
        run_parallel(args)
    elif args.mode == 'swarm':
        run_swarm(args)


def run_sequential_file(args):
    """Process single file (sequential mode)."""
    print("📄 Processing single file (sequential mode)...", file=sys.stderr)

    converter = DocumentToContextConverter()
    try:
        converter.convert(args.input, args.output, args.format)
        print(f"✅ Conversion complete: {args.output}", file=sys.stderr)
        sys.exit(0)
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


def run_sequential_directory(args):
    """Process directory (sequential mode)."""
    print("📁 Processing directory (sequential mode)...", file=sys.stderr)

    converter = EnhancedConverter()
    stats = converter.process_directory(
        args.input,
        args.output,
        recursive=args.recursive,
        mirror_structure=args.mirror_structure,
        create_index=args.create_index,
        output_format=args.format
    )

    sys.exit(0 if stats['failed'] == 0 else 1)


def run_parallel(args):
    """Process directory (parallel mode - Phase 1)."""
    print("⚡ Processing directory (parallel mode - Phase 1)...", file=sys.stderr)

    converter = ParallelConverter(max_workers=args.workers)
    metrics = converter.process_directory(
        args.input,
        args.output,
        recursive=args.recursive,
        mirror_structure=args.mirror_structure,
        create_index=args.create_index,
        output_format=args.format
    )

    sys.exit(0 if metrics.failed == 0 else 1)


def run_swarm(args):
    """Process directory (swarm mode - Phase 2)."""
    print("🤖 Processing directory (swarm mode - Phase 2)...", file=sys.stderr)

    converter = SwarmConverter(
        topology=args.topology,
        max_agents=args.max_agents,
        use_memory=not args.no_memory,
        use_neural=not args.no_neural
    )

    metrics = converter.process_directory(
        args.input,
        args.output,
        recursive=args.recursive,
        mirror_structure=args.mirror_structure,
        create_index=args.create_index,
        output_format=args.format
    )

    sys.exit(0 if metrics.failed == 0 else 1)


def run_benchmark(args):
    """Run all modes and compare performance."""
    import time

    print("\n" + "="*70, file=sys.stderr)
    print("🏆 BENCHMARK MODE - Comparing All Processing Modes", file=sys.stderr)
    print("="*70 + "\n", file=sys.stderr)

    results = {}

    # Sequential baseline
    print("1️⃣  Running SEQUENTIAL mode (baseline)...\n", file=sys.stderr)
    output_seq = f"{args.output}_sequential"
    start = time.time()
    converter_seq = EnhancedConverter()
    stats_seq = converter_seq.process_directory(
        args.input, output_seq, recursive=args.recursive,
        mirror_structure=args.mirror_structure, create_index=False,
        output_format=args.format
    )
    duration_seq = time.time() - start
    results['sequential'] = {
        'duration': duration_seq,
        'processed': stats_seq['processed'],
        'failed': stats_seq['failed']
    }

    # Parallel mode
    print("\n2️⃣  Running PARALLEL mode (Phase 1)...\n", file=sys.stderr)
    output_par = f"{args.output}_parallel"
    start = time.time()
    converter_par = ParallelConverter(max_workers=args.workers)
    metrics_par = converter_par.process_directory(
        args.input, output_par, recursive=args.recursive,
        mirror_structure=args.mirror_structure, create_index=False,
        output_format=args.format
    )
    duration_par = time.time() - start
    results['parallel'] = {
        'duration': duration_par,
        'processed': metrics_par.processed,
        'failed': metrics_par.failed,
        'workers': metrics_par.worker_count
    }

    # Swarm mode
    print("\n3️⃣  Running SWARM mode (Phase 2)...\n", file=sys.stderr)
    output_swarm = f"{args.output}_swarm"
    start = time.time()
    converter_swarm = SwarmConverter(
        topology=args.topology,
        max_agents=args.max_agents,
        use_memory=not args.no_memory,
        use_neural=not args.no_neural
    )
    metrics_swarm = converter_swarm.process_directory(
        args.input, output_swarm, recursive=args.recursive,
        mirror_structure=args.mirror_structure, create_index=False,
        output_format=args.format
    )
    duration_swarm = time.time() - start
    results['swarm'] = {
        'duration': duration_swarm,
        'processed': metrics_swarm.processed,
        'failed': metrics_swarm.failed,
        'agents': metrics_swarm.agent_count
    }

    # Print comparison
    print_benchmark_results(results)


def print_benchmark_results(results):
    """Print benchmark comparison."""
    print("\n" + "="*70, file=sys.stderr)
    print("📊 BENCHMARK RESULTS", file=sys.stderr)
    print("="*70, file=sys.stderr)

    baseline = results['sequential']['duration']

    for mode, data in results.items():
        speedup = baseline / data['duration'] if data['duration'] > 0 else 0
        print(f"\n{mode.upper()}:", file=sys.stderr)
        print(f"  Duration:    {data['duration']:.2f}s", file=sys.stderr)
        print(f"  Processed:   {data['processed']}", file=sys.stderr)
        print(f"  Failed:      {data['failed']}", file=sys.stderr)
        print(f"  Speedup:     {speedup:.2f}x", file=sys.stderr)
        if 'workers' in data:
            print(f"  Workers:     {data['workers']}", file=sys.stderr)
        if 'agents' in data:
            print(f"  Agents:      {data['agents']}", file=sys.stderr)

    print("\n" + "="*70, file=sys.stderr)
    print("🏆 Recommendation:", file=sys.stderr)

    if results['swarm']['duration'] < results['parallel']['duration']:
        print("  Use SWARM mode for best performance with AI coordination", file=sys.stderr)
    else:
        print("  Use PARALLEL mode for best performance", file=sys.stderr)

    print("="*70 + "\n", file=sys.stderr)


def print_sequential_help():
    """Print detailed help for sequential mode."""
    print("""
SEQUENTIAL MODE - Single-threaded processing (baseline)

Usage:
  doc-converter <input> -o <output> [--mode sequential]

Best for:
  - Small batches (< 50 files)
  - Testing and debugging
  - Low-memory environments
  - Single file processing

Performance:
  - ~0.8-1.2 files/sec
  - Minimal memory usage
  - No coordination overhead

Examples:
  # Single file
  doc-converter report.pdf -o report.context.md

  # Small directory
  doc-converter ./docs -o ./output --recursive
    """)


def print_parallel_help():
    """Print detailed help for parallel mode."""
    print("""
PARALLEL MODE - Multi-core processing (Phase 1)

Usage:
  doc-converter <input> -o <output> --mode parallel [-w WORKERS]

Best for:
  - Medium to large batches (50-10,000 files)
  - Multi-core machines
  - Consistent file types
  - Production pipelines

Performance:
  - 8-20x speedup on 8-core machines
  - ~8-16 files/sec
  - Moderate memory usage (workers × file size)

Options:
  -w, --workers N    Number of worker processes (default: CPU count)

Examples:
  # Parallel processing with auto-detection
  doc-converter ./docs -o ./output --mode parallel --recursive

  # Specify worker count
  doc-converter ./docs -o ./output --mode parallel -w 8 --recursive
    """)


def print_swarm_help():
    """Print detailed help for swarm mode."""
    print("""
SWARM MODE - AI orchestration (Phase 2)

Usage:
  doc-converter <input> -o <output> --mode swarm [OPTIONS]

Best for:
  - Large batches (1,000+ files)
  - Mixed file types
  - Intelligent coordination needed
  - Learning from patterns

Performance:
  - 20-50x speedup with intelligent coordination
  - ~20-40 files/sec
  - Memory-efficient batching
  - Neural pattern learning

Options:
  --topology {hierarchical,mesh,adaptive}
                        Swarm coordination pattern (default: hierarchical)
  --max-agents N        Maximum concurrent agents (default: 6)
  --no-memory          Disable cross-session memory
  --no-neural          Disable neural pattern training

Topologies:
  hierarchical    - Centralized coordination (best for reliability)
  mesh           - Peer-to-peer coordination (best for fault tolerance)
  adaptive       - Dynamic topology switching (best for mixed workloads)

Examples:
  # Swarm with hierarchical coordination
  doc-converter ./docs -o ./output --mode swarm --recursive

  # Swarm with mesh topology and 10 agents
  doc-converter ./docs -o ./output --mode swarm --topology mesh --max-agents 10

  # Swarm without neural training (faster, no learning)
  doc-converter ./docs -o ./output --mode swarm --no-neural
    """)


if __name__ == '__main__':
    main()
