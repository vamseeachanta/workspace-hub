"""Tests for the schema registry."""

import pytest

from coordination.schemas._registry import get_schema_for_file, SCHEMA_REGISTRY
from coordination.schemas.reflect_state import ReflectState
from coordination.schemas.learnings import LearningsFile
from coordination.schemas.work_queue import WorkQueueState
from coordination.schemas.cc_user_insights import CCUserInsights


@pytest.mark.unit
class TestSchemaRegistry:
    def test_reflect_state_lookup(self):
        assert get_schema_for_file("reflect-state.yaml") is ReflectState
        assert get_schema_for_file("reflect-state.yml") is ReflectState
        assert get_schema_for_file("reflect-state") is ReflectState

    def test_learnings_lookup(self):
        assert get_schema_for_file("learnings.yaml") is LearningsFile
        assert get_schema_for_file("learnings") is LearningsFile

    def test_state_lookup(self):
        assert get_schema_for_file("state.yaml") is WorkQueueState
        assert get_schema_for_file("state") is WorkQueueState

    def test_cc_user_insights_lookup(self):
        assert get_schema_for_file("cc-user-insights.yaml") is CCUserInsights
        assert get_schema_for_file("cc-user-insights") is CCUserInsights

    def test_full_path_lookup(self):
        assert get_schema_for_file("/some/path/to/reflect-state.yaml") is ReflectState
        assert get_schema_for_file(".claude/state/learnings.yaml") is LearningsFile

    def test_unknown_file_returns_none(self):
        assert get_schema_for_file("unknown.yaml") is None
        assert get_schema_for_file("nonexistent") is None

    def test_registry_has_all_schemas(self):
        # Each schema should have at least 3 entries (stem, .yaml, .yml)
        schemas = {ReflectState, LearningsFile, WorkQueueState, CCUserInsights}
        registry_schemas = set(SCHEMA_REGISTRY.values())
        assert schemas == registry_schemas
