"""
ABOUTME: Utilities and shared functionality for all Phase 1 modules
ABOUTME: Provides deduplication, consolidation, and common utilities
"""

from .deduplication import (
    DeduplicationAnalyzer,
    UtilitiesConsolidator,
    DuplicateCode,
    ConsolidationOpportunity
)

__all__ = [
    "DeduplicationAnalyzer",
    "UtilitiesConsolidator",
    "DuplicateCode",
    "ConsolidationOpportunity",
]

__version__ = "1.0.0"
