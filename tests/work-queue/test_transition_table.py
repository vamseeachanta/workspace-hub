"""Tests for generate_transition_table.py — explicit FSM transitions.

TDD: Red → Green for WRK-1187 Enhancement 2.
"""

import sys
from pathlib import Path

import pytest

WORK_QUEUE_DIR = Path(__file__).parent.parent.parent / "scripts" / "work-queue"
if not WORK_QUEUE_DIR.exists():
    pytest.skip("legacy scripts/work-queue/ implementation is not present in this checkout", allow_module_level=True)

sys.path.insert(0, str(WORK_QUEUE_DIR))

from generate_transition_table import (
    load_stage_contracts,
    build_transition_table,
    validate_transition,
)


STAGES_DIR = str(
    Path(__file__).parent.parent.parent / ".claude" / "skills" / "workspace-hub" / "stages"
)


class TestLoadStageContracts:
    """load_stage_contracts reads all 20 stage YAML files."""

    def test_loads_all_20_stages(self):
        contracts = load_stage_contracts(STAGES_DIR)
        assert len(contracts) == 20

    def test_contracts_sorted_by_order(self):
        contracts = load_stage_contracts(STAGES_DIR)
        orders = [c["order"] for c in contracts]
        assert orders == sorted(orders)

    def test_contract_has_required_fields(self):
        contracts = load_stage_contracts(STAGES_DIR)
        for c in contracts:
            assert "order" in c
            assert "name" in c
            assert "human_gate" in c


class TestBuildTransitionTable:
    """build_transition_table produces from→to mappings with guards."""

    def test_produces_19_transitions(self):
        """20 stages → 19 transitions (1→2, 2→3, ..., 19→20)."""
        contracts = load_stage_contracts(STAGES_DIR)
        table = build_transition_table(contracts)
        assert len(table) == 19

    def test_transition_has_from_to(self):
        contracts = load_stage_contracts(STAGES_DIR)
        table = build_transition_table(contracts)
        for t in table:
            assert "from_stage" in t
            assert "to_stage" in t
            assert t["to_stage"] == t["from_stage"] + 1

    def test_human_gate_transitions_marked(self):
        contracts = load_stage_contracts(STAGES_DIR)
        table = build_transition_table(contracts)
        human_gates = [t for t in table if t.get("human_gate")]
        # Stages 1, 5, 7, 17 are human gates → transitions FROM these stages
        human_from = {t["from_stage"] for t in human_gates}
        # Stages 5, 7, 17 are human gates (stage 1 uses scope approval, not gate_file)
        assert {5, 7, 17}.issubset(human_from)

    def test_rollback_targets_present(self):
        contracts = load_stage_contracts(STAGES_DIR)
        table = build_transition_table(contracts)
        for t in table:
            assert "rollback_to" in t
            assert t["rollback_to"] <= t["from_stage"]


class TestValidateTransition:
    """validate_transition checks if a stage→stage move is legal."""

    def test_sequential_transition_allowed(self):
        contracts = load_stage_contracts(STAGES_DIR)
        table = build_transition_table(contracts)
        assert validate_transition(table, from_stage=4, to_stage=5) is True

    def test_skip_transition_blocked(self):
        contracts = load_stage_contracts(STAGES_DIR)
        table = build_transition_table(contracts)
        assert validate_transition(table, from_stage=4, to_stage=7) is False

    def test_backward_transition_blocked(self):
        contracts = load_stage_contracts(STAGES_DIR)
        table = build_transition_table(contracts)
        assert validate_transition(table, from_stage=10, to_stage=5) is False
