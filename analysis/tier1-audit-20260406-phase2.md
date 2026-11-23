## Phase 2 Adversarial Review -- Complete

Review verdict from 3 agents: **APPROVE with actionable findings.**

### Review findings incorporated:
1. Codex: curves.py broken out into dedicated sub-issue (digitalmodel #483)
2. Gemini: assethold added to Phase 2 refactor order
3. Both: contract compliance check expanded to include .codex/ and .gemini/ adapters

### Sub-issues created:
- **digitalmodel #483:** curves.py decomposition -- https://github.com/vamseeachanta/digitalmodel/issues/483
- **assetutilities #73:** fix tests, audit orphans, decompose -- created in assetutilities repo

### Assetutilities test deep dive -- SURPRISE FINDING

Initial audit reported "2 errors" in test collection. After fixing the import path:

**58 tests actually fail** (not 2 collection errors). All 58 are in the `agent_os` subsystem:

| Test File | Failures | Root Cause |
|-----------|----------|------------|
| test_cross_repository_integration.py | 22 | Implementation changed, tests stale |
| test_integration.py | 18 | Methods missing (get_valid_agent_types, validate_repository) |
| test_cli.py | 11 | Help text mismatches, assertion mismatches |
| test_ai_persistence_system.py | 5 | Async test framework not configured |
| test_cli_integration.py | 2 | Output text mismatches |

**Assessment:** These are NOT quick fixes. The agent_os tests test code that was evolved without corresponding test updates. Fixing requires reading both source and test, and updating one or the other to match. This is a Phase 3 implementation task, not a simple flag flip.

### Updated Refactoring Priority

PRIORITY 1: **assetutilities** -- but the agent_os test failures (58) are a bigger job than anticipated. Split into:
- Fix async marker in pytest.ini (DONE)
- Fix import path in test_ai_persistence_system.py (DONE for --noconftest mode)
- Remaining 51 failures need dedicated sub-task

PRIORITY 2: **digitalmodel** -- curves.py decomposition (dedicated sub-issue #483)

PRIORITY 3: **worldenergydata** -- dependency audit + 5 test failures

PRIORITY 4: **assethold** -- audit needed (depends on assetutilities)

### Files modified in this phase:
- `assetutilities/pytest.ini` -- added asyncio marker
- `assetutilities/tests/modules/agent_os/enhanced_create_specs/unit/test_ai_persistence_system.py` -- fixed hardcoded path
