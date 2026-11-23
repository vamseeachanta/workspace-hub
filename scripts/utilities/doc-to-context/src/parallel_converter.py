#!/usr/bin/env python3
"""
Parallel Document to Context Converter (Phase 1)
High-performance parallel processing using multiprocessing worker pool.
"""

import os
import sys
import json
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass, asdict
import multiprocessing as mp
from concurrent.futures import ProcessPoolExecutor, as_completed
import argparse

# Import base converter
from doc_to_context import DocumentToContextConverter, DocumentContent


@dataclass
class ProcessingMetrics:
    """Performance metrics for parallel processing."""
    total_files: int
    processed: int
    failed: int
    skipped: int
    start_time: float
    end_time: Optional[float] = None
    worker_count: int = 0
    files_per_second: float = 0.0
    total_duration: float = 0.0
    avg_file_time: float = 0.0
    speedup_factor: float = 1.0

    def finalize(self):
        """Calculate final metrics."""
        if self.end_time:
            self.total_duration = self.end_time - self.start_time
            if self.total_duration > 0:
                self.files_per_second = self.processed / self.total_duration
            if self.processed > 0:
                self.avg_file_time = self.total_duration / self.processed


class ParallelConverter:
    """
    Phase 1: Parallel document converter using worker pool.
    Provides 8-20x speedup on multi-core machines.
    """

    def __init__(self, max_workers: Optional[int] = None):
        """
        Initialize parallel converter.

        Args:
            max_workers: Number of worker processes (None = CPU count)
        """
        self.max_workers = max_workers or mp.cpu_count()
        self.converter = DocumentToContextConverter()
        self.metrics = None

    def process_directory(self,
                         input_dir: str,
                         output_dir: str,
                         recursive: bool = False,
                         mirror_structure: bool = True,
                         create_index: bool = True,
                         output_format: str = 'markdown',
                         batch_size: int = 100) -> ProcessingMetrics:
        """
        Process directory with parallel workers.

        Args:
            input_dir: Source directory
            output_dir: Output directory
            recursive: Process subdirectories
            mirror_structure: Preserve directory structure
            create_index: Generate index.json
            output_format: 'markdown' or 'json'
            batch_size: Files per batch for progress tracking

        Returns:
            ProcessingMetrics with performance data
        """
        input_path = Path(input_dir)
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        # Discover all files
        print(f"🔍 Discovering documents in {input_dir}...", file=sys.stderr)
        files = self._discover_files(input_path, recursive)

        if not files:
            print("❌ No documents found", file=sys.stderr)
            return ProcessingMetrics(0, 0, 0, 0, time.time(), time.time())

        print(f"📊 Found {len(files)} documents", file=sys.stderr)
        print(f"⚡ Using {self.max_workers} parallel workers", file=sys.stderr)

        # Initialize metrics
        self.metrics = ProcessingMetrics(
            total_files=len(files),
            processed=0,
            failed=0,
            skipped=0,
            start_time=time.time(),
            worker_count=self.max_workers
        )

        # Prepare work items
        work_items = []
        for file_path in files:
            output_file = self._get_output_path(
                file_path, input_path, output_path,
                mirror_structure, output_format
            )
            work_items.append((str(file_path), str(output_file), output_format))

        # Process in parallel
        results = []
        failed_files = []

        print(f"\n🚀 Processing {len(work_items)} files in parallel...\n", file=sys.stderr)

        with ProcessPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all tasks
            future_to_file = {
                executor.submit(self._process_file_worker, item): item
                for item in work_items
            }

            # Track progress
            completed = 0
            for future in as_completed(future_to_file):
                work_item = future_to_file[future]
                completed += 1

                try:
                    result = future.result()
                    if result['success']:
                        results.append(result)
                        self.metrics.processed += 1
                        status = "✅"
                    else:
                        failed_files.append((work_item[0], result.get('error', 'Unknown error')))
                        self.metrics.failed += 1
                        status = "❌"

                    # Progress update
                    progress = (completed / len(work_items)) * 100
                    print(f"{status} [{completed}/{len(work_items)}] ({progress:.1f}%) - {Path(work_item[0]).name}",
                          file=sys.stderr)

                except Exception as e:
                    failed_files.append((work_item[0], str(e)))
                    self.metrics.failed += 1
                    print(f"❌ [{completed}/{len(work_items)}] ERROR - {Path(work_item[0]).name}: {e}",
                          file=sys.stderr)

        # Finalize metrics
        self.metrics.end_time = time.time()
        self.metrics.finalize()

        # Create index
        if create_index and results:
            self._create_index(results, output_path)

        # Print summary
        self._print_summary(failed_files)

        return self.metrics

    @staticmethod
    def _process_file_worker(work_item: Tuple[str, str, str]) -> Dict:
        """
        Worker function for processing single file.
        Must be static for multiprocessing pickle support.

        Args:
            work_item: (input_file, output_file, format)

        Returns:
            Result dictionary with success status and metadata
        """
        input_file, output_file, output_format = work_item

        try:
            # Create converter instance in worker
            converter = DocumentToContextConverter()

            # Ensure output directory exists
            Path(output_file).parent.mkdir(parents=True, exist_ok=True)

            # Convert document
            content = converter.convert(input_file, output_file, output_format)

            return {
                'success': True,
                'source': input_file,
                'output': output_file,
                'format': content.metadata.format,
                'size_bytes': content.metadata.size_bytes,
                'page_count': content.metadata.page_count,
                'checksum': content.metadata.checksum
            }

        except Exception as e:
            return {
                'success': False,
                'source': input_file,
                'error': str(e)
            }

    def _discover_files(self, input_path: Path, recursive: bool) -> List[Path]:
        """Discover all processable files."""
        supported_extensions = {'.pdf', '.docx', '.xlsx', '.xlsm', '.html', '.htm'}
        pattern = '**/*' if recursive else '*'

        files = []
        for file_path in input_path.glob(pattern):
            if file_path.is_file() and file_path.suffix.lower() in supported_extensions:
                files.append(file_path)

        return sorted(files)  # Sort for consistent ordering

    def _get_output_path(self,
                        file_path: Path,
                        input_root: Path,
                        output_root: Path,
                        mirror_structure: bool,
                        output_format: str) -> Path:
        """Determine output file path."""
        if mirror_structure:
            relative_path = file_path.relative_to(input_root)
            output_dir = output_root / relative_path.parent
            output_dir.mkdir(parents=True, exist_ok=True)
        else:
            output_dir = output_root

        if output_format == 'markdown':
            return output_dir / f"{file_path.stem}.context.md"
        else:
            return output_dir / f"{file_path.stem}.json"

    def _create_index(self, results: List[Dict], output_path: Path):
        """Create searchable index file."""
        index = {
            'generated': datetime.now().isoformat(),
            'total_documents': len(results),
            'total_size_bytes': sum(r.get('size_bytes', 0) for r in results),
            'processing_metrics': asdict(self.metrics),
            'documents': results
        }

        index_file = output_path / '_index.json'
        with open(index_file, 'w', encoding='utf-8') as f:
            json.dump(index, f, indent=2, ensure_ascii=False)

        print(f"\n📋 Index created: {index_file}", file=sys.stderr)

    def _print_summary(self, failed_files: List[Tuple[str, str]]):
        """Print processing summary."""
        print("\n" + "="*70, file=sys.stderr)
        print("⚡ PARALLEL PROCESSING COMPLETE", file=sys.stderr)
        print("="*70, file=sys.stderr)

        print(f"Total files:       {self.metrics.total_files}", file=sys.stderr)
        print(f"✅ Processed:      {self.metrics.processed}", file=sys.stderr)
        print(f"❌ Failed:         {self.metrics.failed}", file=sys.stderr)
        print(f"⏭️  Skipped:        {self.metrics.skipped}", file=sys.stderr)
        print(f"\n⏱️  Duration:       {self.metrics.total_duration:.2f}s", file=sys.stderr)
        print(f"🚀 Throughput:     {self.metrics.files_per_second:.2f} files/sec", file=sys.stderr)
        print(f"👷 Workers:        {self.metrics.worker_count}", file=sys.stderr)
        print(f"📊 Avg file time:  {self.metrics.avg_file_time:.2f}s", file=sys.stderr)

        # Calculate estimated speedup vs sequential
        sequential_estimate = self.metrics.avg_file_time * self.metrics.total_files
        if self.metrics.total_duration > 0:
            speedup = sequential_estimate / self.metrics.total_duration
            print(f"⚡ Speedup:        {speedup:.1f}x (vs sequential)", file=sys.stderr)

        if failed_files:
            print(f"\n❌ Failed files:", file=sys.stderr)
            for file_path, error in failed_files[:10]:  # Show first 10
                print(f"  - {Path(file_path).name}: {error}", file=sys.stderr)
            if len(failed_files) > 10:
                print(f"  ... and {len(failed_files) - 10} more", file=sys.stderr)

        print("="*70 + "\n", file=sys.stderr)


def main():
    """CLI entry point for parallel converter."""
    parser = argparse.ArgumentParser(
        description='Parallel Document to Context Converter (Phase 1)'
    )

    parser.add_argument('input', help='Input directory')
    parser.add_argument('-o', '--output', required=True, help='Output directory')
    parser.add_argument('-f', '--format', choices=['markdown', 'json'],
                       default='markdown', help='Output format')
    parser.add_argument('-r', '--recursive', action='store_true',
                       help='Process subdirectories')
    parser.add_argument('--mirror-structure', action='store_true',
                       help='Mirror input directory structure')
    parser.add_argument('--create-index', action='store_true', default=True,
                       help='Create index.json file')
    parser.add_argument('-w', '--workers', type=int,
                       help='Number of worker processes (default: CPU count)')
    parser.add_argument('--batch-size', type=int, default=100,
                       help='Batch size for progress tracking')

    args = parser.parse_args()

    # Create parallel converter
    converter = ParallelConverter(max_workers=args.workers)

    # Process directory
    metrics = converter.process_directory(
        args.input,
        args.output,
        recursive=args.recursive,
        mirror_structure=args.mirror_structure,
        create_index=args.create_index,
        output_format=args.format,
        batch_size=args.batch_size
    )

    # Exit with appropriate code
    sys.exit(0 if metrics.failed == 0 else 1)


if __name__ == '__main__':
    main()
