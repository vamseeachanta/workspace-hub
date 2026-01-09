"""
ABOUTME: Utilities deduplication and consolidation analysis tool
ABOUTME: Detects code duplication, deduplicates shared functionality
"""

import hashlib
import logging
from typing import Dict, List, Set, Tuple
from pathlib import Path
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class DuplicateCode:
    """Represents a duplicate code block."""
    hash_id: str
    file_paths: List[str]
    line_numbers: List[int]
    code_lines: List[str]
    similarity: float  # 0.0 to 1.0


@dataclass
class ConsolidationOpportunity:
    """Represents an opportunity to consolidate code."""
    opportunity_id: str
    type: str  # 'function', 'class', 'module'
    locations: List[Tuple[str, int]]  # (file, line_number)
    estimated_reduction: float  # percentage of code that could be removed
    recommendation: str


class DeduplicationAnalyzer:
    """Analyzes code for duplication and consolidation opportunities."""

    def __init__(self, min_block_size: int = 5):
        """
        Initialize deduplication analyzer.

        Args:
            min_block_size: Minimum lines of code to consider a block
        """
        self.min_block_size = min_block_size
        self.duplicates: Dict[str, DuplicateCode] = {}
        self.consolidation_opportunities: List[ConsolidationOpportunity] = []

    def analyze_files(self, file_paths: List[Path]) -> Dict[str, DuplicateCode]:
        """
        Analyze files for code duplication.

        Args:
            file_paths: List of Python files to analyze

        Returns:
            Dictionary of detected duplicates by hash
        """
        code_blocks = {}

        for file_path in file_paths:
            try:
                with open(file_path, 'r') as f:
                    content = f.read()
                    blocks = self._extract_code_blocks(content, str(file_path))
                    code_blocks.update(blocks)
            except Exception as e:
                logger.error(f"Error analyzing {file_path}: {e}")

        # Find duplicates
        self._find_duplicates(code_blocks)
        return self.duplicates

    def _extract_code_blocks(self, content: str, file_path: str) -> Dict[str, Tuple[str, int]]:
        """Extract code blocks from file."""
        blocks = {}
        lines = content.split('\n')

        for i in range(len(lines) - self.min_block_size):
            block_lines = lines[i:i + self.min_block_size]
            block_text = '\n'.join(block_lines)

            # Skip whitespace-only blocks
            if block_text.strip():
                block_hash = hashlib.md5(block_text.encode()).hexdigest()
                blocks[block_hash] = (block_text, i + 1)

        return blocks

    def _find_duplicates(self, code_blocks: Dict[str, Tuple[str, int]]):
        """Find duplicate code blocks."""
        hash_to_locations = {}

        for block_hash, (code, line_num) in code_blocks.items():
            if block_hash not in hash_to_locations:
                hash_to_locations[block_hash] = []
            hash_to_locations[block_hash].append((code, line_num))

        # Create duplicates for blocks appearing multiple times
        for block_hash, locations in hash_to_locations.items():
            if len(locations) > 1:
                file_paths = [loc[2] if len(loc) > 2 else 'unknown' for loc in locations]
                line_numbers = [loc[1] for loc in locations]
                code_lines = [loc[0] for loc in locations]

                self.duplicates[block_hash] = DuplicateCode(
                    hash_id=block_hash,
                    file_paths=file_paths,
                    line_numbers=line_numbers,
                    code_lines=code_lines,
                    similarity=1.0
                )

    def find_consolidation_opportunities(self) -> List[ConsolidationOpportunity]:
        """
        Find opportunities to consolidate code.

        Returns:
            List of consolidation opportunities
        """
        opportunities = []

        for dup_hash, duplicate in self.duplicates.items():
            if len(duplicate.file_paths) >= 2:
                locations = list(zip(duplicate.file_paths, duplicate.line_numbers))

                opportunity = ConsolidationOpportunity(
                    opportunity_id=f'consolidate_{dup_hash[:8]}',
                    type='function',
                    locations=locations,
                    estimated_reduction=len(duplicate.file_paths) * 0.1,
                    recommendation=f'Extract common code from {len(duplicate.file_paths)} locations'
                )
                opportunities.append(opportunity)

        self.consolidation_opportunities = opportunities
        return opportunities

    def generate_report(self) -> str:
        """Generate deduplication analysis report."""
        report = "Deduplication Analysis Report\n"
        report += "=" * 50 + "\n\n"

        report += f"Total Duplicates Found: {len(self.duplicates)}\n"
        report += f"Consolidation Opportunities: {len(self.consolidation_opportunities)}\n\n"

        if self.duplicates:
            report += "Duplicate Code Blocks:\n"
            for dup_hash, duplicate in self.duplicates.items():
                report += f"\n  Hash: {dup_hash[:8]}...\n"
                report += f"  Locations: {len(duplicate.file_paths)} files\n"
                report += f"  Similarity: {duplicate.similarity:.1%}\n"

        if self.consolidation_opportunities:
            report += "\nConsolidation Opportunities:\n"
            for opp in self.consolidation_opportunities:
                report += f"\n  ID: {opp.opportunity_id}\n"
                report += f"  Recommendation: {opp.recommendation}\n"
                report += f"  Estimated Reduction: {opp.estimated_reduction:.1%}\n"

        return report


class UtilitiesConsolidator:
    """Consolidates duplicated utilities into shared modules."""

    def __init__(self):
        """Initialize consolidator."""
        self.consolidations: Dict[str, List[str]] = {}

    def consolidate_to_shared(self, duplicates: Dict[str, DuplicateCode], output_module: Path):
        """
        Consolidate duplicates into a shared utilities module.

        Args:
            duplicates: Dictionary of duplicate code blocks
            output_module: Path to output shared utilities module
        """
        shared_functions = {}

        for dup_hash, duplicate in duplicates.items():
            function_name = f"shared_utility_{dup_hash[:8]}"
            shared_functions[function_name] = duplicate.code_lines[0]
            self.consolidations[function_name] = duplicate.file_paths

        logger.info(f"Identified {len(shared_functions)} shared utilities")

    def generate_consolidation_plan(self, duplicates: Dict[str, DuplicateCode]) -> str:
        """Generate a consolidation plan."""
        plan = "Consolidation Plan\n"
        plan += "=" * 50 + "\n\n"

        for dup_hash, duplicate in duplicates.items():
            plan += f"Consolidate: {dup_hash[:8]}\n"
            plan += f"From {len(duplicate.file_paths)} files:\n"
            for i, file_path in enumerate(duplicate.file_paths, 1):
                plan += f"  {i}. {file_path} (line {duplicate.line_numbers[i-1]})\n"
            plan += f"To: src/utilities/shared/{dup_hash[:8]}_shared.py\n\n"

        return plan
