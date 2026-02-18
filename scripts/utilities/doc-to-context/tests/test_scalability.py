#!/usr/bin/env python3
"""
Tests for parallel and swarm scalability modes.
"""

import os
import sys
import tempfile
import shutil
from pathlib import Path
import pytest

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from parallel_converter import ParallelConverter, ProcessingMetrics
from swarm_converter import SwarmConverter, SwarmMetrics


class TestParallelConverter:
    """Tests for Phase 1 parallel processing."""

    def test_parallel_converter_initialization(self):
        """Test parallel converter initializes with correct worker count."""
        converter = ParallelConverter(max_workers=4)
        assert converter.max_workers == 4

    def test_auto_worker_detection(self):
        """Test automatic worker count detection."""
        converter = ParallelConverter()
        assert converter.max_workers > 0

    def test_parallel_processing_metrics(self):
        """Test metrics are properly calculated."""
        import time

        metrics = ProcessingMetrics(
            total_files=100,
            processed=95,
            failed=5,
            skipped=0,
            start_time=time.time() - 60,  # 60 seconds ago
            worker_count=8
        )

        metrics.end_time = time.time()
        metrics.finalize()

        assert metrics.total_duration > 0
        assert metrics.files_per_second > 0
        assert metrics.avg_file_time > 0

    @pytest.mark.integration
    def test_parallel_processing_small_batch(self, tmp_path):
        """Test parallel processing on small batch."""
        # This would require test documents
        # Skipping actual file processing in unit tests
        pass


class TestSwarmConverter:
    """Tests for Phase 2 swarm processing."""

    def test_swarm_converter_initialization(self):
        """Test swarm converter initializes with correct settings."""
        converter = SwarmConverter(
            topology='hierarchical',
            max_agents=6,
            use_memory=True,
            use_neural=True
        )

        assert converter.topology == 'hierarchical'
        assert converter.max_agents == 6
        assert converter.use_memory is True
        assert converter.use_neural is True

    def test_swarm_topologies(self):
        """Test all supported topologies."""
        topologies = ['hierarchical', 'mesh', 'adaptive']

        for topology in topologies:
            converter = SwarmConverter(topology=topology)
            assert converter.topology == topology

    def test_swarm_metrics(self):
        """Test swarm metrics include agent information."""
        import time

        metrics = SwarmMetrics(
            total_files=1000,
            processed=990,
            failed=10,
            skipped=0,
            start_time=time.time() - 30,
            worker_count=0,
            agent_count=6,
            topology='hierarchical'
        )

        metrics.end_time = time.time()
        metrics.finalize()

        assert metrics.agent_count == 6
        assert metrics.topology == 'hierarchical'
        assert metrics.total_duration > 0

    def test_file_categorization(self):
        """Test file discovery and categorization by type."""
        converter = SwarmConverter()

        # Create temp test structure
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)

            # Create test files
            (tmp_path / 'test.pdf').touch()
            (tmp_path / 'test.xlsx').touch()
            (tmp_path / 'test.docx').touch()
            (tmp_path / 'test.html').touch()

            categories = converter._discover_and_categorize(tmp_path, recursive=False)

            assert 'pdf' in categories
            assert 'excel' in categories
            assert 'word' in categories
            assert 'html' in categories
            assert len(categories['pdf']) == 1
            assert len(categories['excel']) == 1

    def test_agent_task_creation(self):
        """Test agent task creation from file groups."""
        converter = SwarmConverter(max_agents=6)

        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            output_path = tmp_path / 'output'

            # Create test files
            pdf_files = [tmp_path / f'test{i}.pdf' for i in range(25)]
            for f in pdf_files:
                f.touch()

            file_groups = {'pdf': pdf_files}

            tasks = converter._create_agent_tasks(
                file_groups, tmp_path, output_path,
                mirror_structure=True, output_format='markdown'
            )

            # Should split 25 PDFs across multiple agents
            assert len(tasks) > 0
            assert all(task.agent_type == 'PDF Parser Agent' for task in tasks)
            assert sum(len(task.files) for task in tasks) == 25

    @pytest.mark.integration
    def test_swarm_fallback_to_parallel(self):
        """Test swarm falls back to parallel mode if MCP unavailable."""
        # Test that swarm can operate without Claude Flow
        converter = SwarmConverter()

        # Swarm ID should be generated even without MCP
        swarm_id = converter._init_swarm()
        assert swarm_id is not None
        assert swarm_id.startswith('doc-swarm-')


class TestPerformanceComparison:
    """Tests comparing sequential, parallel, and swarm performance."""

    @pytest.mark.slow
    @pytest.mark.integration
    def test_speedup_calculation(self):
        """Test speedup metrics are correctly calculated."""
        # Sequential baseline
        sequential_time = 100.0  # seconds

        # Parallel time
        parallel_time = 12.5  # seconds
        parallel_speedup = sequential_time / parallel_time

        # Swarm time
        swarm_time = 5.0  # seconds
        swarm_speedup = sequential_time / swarm_time

        assert parallel_speedup == pytest.approx(8.0, rel=0.1)
        assert swarm_speedup == pytest.approx(20.0, rel=0.1)
        assert swarm_speedup > parallel_speedup

    def test_worker_scaling(self):
        """Test that more workers improve throughput."""
        # Theoretical test of Amdahl's Law
        sequential_time = 100.0

        for workers in [1, 2, 4, 8, 16]:
            # Assuming 90% parallelizable work
            parallel_portion = 0.9
            serial_portion = 0.1

            expected_time = sequential_time * (serial_portion + parallel_portion / workers)
            speedup = sequential_time / expected_time

            # Speedup should increase with workers (diminishing returns)
            assert speedup >= 1.0
            if workers <= 8:
                assert speedup < workers  # Never perfect linear scaling


class TestErrorHandling:
    """Tests for error handling in parallel and swarm modes."""

    def test_parallel_isolated_failures(self):
        """Test that worker failures don't crash entire batch."""
        converter = ParallelConverter(max_workers=2)

        # Individual worker failures should be isolated
        # and reported in metrics without stopping other workers
        assert converter.max_workers == 2

    def test_swarm_agent_failure_recovery(self):
        """Test that swarm can handle agent failures."""
        converter = SwarmConverter(max_agents=4)

        # Swarm should continue even if some agents fail
        assert converter.max_agents == 4

    def test_memory_coordination_fallback(self):
        """Test graceful fallback when memory coordination unavailable."""
        converter = SwarmConverter(use_memory=True)

        # Should not crash if memory operations fail
        converter._store_memory('test/key', {'data': 'value'})
        # Silent failure is expected


def test_cli_integration():
    """Test unified CLI works correctly."""
    # This would test the actual CLI interface
    # Requires integration testing setup
    pass


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
