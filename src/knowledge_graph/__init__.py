"""
ABOUTME: Domain Knowledge Graph — WRK-183
ABOUTME: Graph-based concept taxonomy linking engineering domains for transitive skill discovery
"""

from .graph_engine import KnowledgeGraph, GraphNode, GraphEdge, SkillSuggestion
from .taxonomy_loader import TaxonomyLoader
from .session_advisor import SessionAdvisor
from .visualizer import GraphVisualizer

__all__ = [
    "KnowledgeGraph",
    "GraphNode",
    "GraphEdge",
    "SkillSuggestion",
    "TaxonomyLoader",
    "SessionAdvisor",
    "GraphVisualizer",
]

__version__ = "1.0.0"
