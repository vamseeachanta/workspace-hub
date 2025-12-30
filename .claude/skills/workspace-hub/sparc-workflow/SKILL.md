---
name: sparc-workflow
description: Apply SPARC methodology (Specification, Pseudocode, Architecture, Refinement, Completion) for systematic development. Use for feature development, TDD workflows, and structured problem-solving.
---

# SPARC Workflow Skill

## Overview

SPARC is a systematic methodology for software development that ensures quality through structured phases. Each phase builds on the previous, creating well-documented, well-tested code.

## SPARC Phases

```
┌─────────────────────────────────────────────────────────────────┐
│  S → P → A → R → C                                              │
│                                                                  │
│  Specification → Pseudocode → Architecture → Refinement → Done  │
└─────────────────────────────────────────────────────────────────┘
```

### Phase Overview

| Phase | Focus | Output |
|-------|-------|--------|
| **S**pecification | What to build | Requirements document |
| **P**seudocode | How it works | Algorithm design |
| **A**rchitecture | How it fits | System design |
| **R**efinement | Make it work | Tested implementation |
| **C**ompletion | Make it right | Production-ready code |

## Phase 1: Specification

### Purpose

Define what needs to be built with clear, measurable requirements.

### Process

1. Gather requirements from user prompt
2. Identify acceptance criteria
3. Define scope (in-scope and out-of-scope)
4. Document constraints and assumptions

### Output Template

```markdown
# Feature Specification

## Overview
[One paragraph describing the feature]

## Requirements

### Functional Requirements
1. FR-1: [Requirement]
2. FR-2: [Requirement]
3. FR-3: [Requirement]

### Non-Functional Requirements
1. NFR-1: Performance - [Requirement]
2. NFR-2: Security - [Requirement]
3. NFR-3: Usability - [Requirement]

## Scope

### In Scope
- [Item 1]
- [Item 2]

### Out of Scope
- [Item 1]
- [Item 2]

## Acceptance Criteria
- [ ] AC-1: [Testable criterion]
- [ ] AC-2: [Testable criterion]
- [ ] AC-3: [Testable criterion]

## Constraints
- [Technical constraint]
- [Business constraint]

## Assumptions
- [Assumption 1]
- [Assumption 2]
```

### Specification Checklist

- [ ] All requirements are clear and unambiguous
- [ ] Each requirement is testable
- [ ] Scope is explicitly defined
- [ ] Constraints are documented
- [ ] User stories follow "As a... I want... So that..." format

## Phase 2: Pseudocode

### Purpose

Design the algorithm and logic before implementation.

### Process

1. Break down requirements into logical steps
2. Write language-agnostic pseudocode
3. Identify edge cases
4. Design error handling

### Pseudocode Guidelines

```
FUNCTION process_data(input_data):
    // Validate input
    IF input_data is empty:
        RAISE ValidationError("Input cannot be empty")

    // Initialize result
    result = EMPTY_LIST

    // Process each item
    FOR EACH item IN input_data:
        // Check conditions
        IF item.meets_criteria():
            processed_item = transform(item)
            APPEND processed_item TO result

    RETURN result

FUNCTION transform(item):
    // Apply transformation logic
    new_value = item.value * MULTIPLIER
    RETURN Item(new_value, item.metadata)
```

### Pseudocode Best Practices

1. **Be explicit**: Show all decision points
2. **Include error handling**: Show how errors are managed
3. **Note complexity**: O(n), O(n²), etc.
4. **Identify data structures**: Lists, maps, trees
5. **Show edge cases**: Empty input, single item, maximum size

### Output Template

```markdown
# Pseudocode Design

## Main Algorithm

\`\`\`
FUNCTION main_feature(params):
    [Algorithm steps]
\`\`\`

## Helper Functions

\`\`\`
FUNCTION helper_one(input):
    [Steps]

FUNCTION helper_two(input):
    [Steps]
\`\`\`

## Error Handling

\`\`\`
TRY:
    [Main logic]
CATCH ValidationError:
    [Handle validation]
CATCH ProcessingError:
    [Handle processing]
FINALLY:
    [Cleanup]
\`\`\`

## Edge Cases

| Case | Input | Expected Output |
|------|-------|-----------------|
| Empty | [] | [] |
| Single | [1] | [processed_1] |
| Maximum | [1..10000] | [processed_all] |

## Complexity Analysis

- Time: O(n)
- Space: O(n)
```

## Phase 3: Architecture

### Purpose

Design how the feature fits into the system architecture.

### Process

1. Identify affected components
2. Design interfaces and contracts
3. Plan data flow
4. Consider dependencies

### Architecture Considerations

```markdown
## Component Design

### New Components
- ComponentA: [Purpose]
- ComponentB: [Purpose]

### Modified Components
- ExistingComponent: [Changes needed]

## Interface Design

\`\`\`python
class IProcessor(Protocol):
    def process(self, data: InputData) -> OutputData:
        """Process input and return output."""
        ...

    def validate(self, data: InputData) -> bool:
        """Validate input data."""
        ...
\`\`\`

## Data Flow

\`\`\`
Input → Validator → Processor → Transformer → Output
            ↓            ↓
         Logger       Cache
\`\`\`

## Dependencies

### Internal
- module_a (version ≥ 1.2.0)
- module_b

### External
- library_x (version 2.0.0)

## File Structure

\`\`\`
src/
└── feature_name/
    ├── __init__.py
    ├── processor.py      # Main processing logic
    ├── validator.py      # Input validation
    ├── transformer.py    # Data transformation
    └── models.py         # Data models
\`\`\`
```

## Phase 4: Refinement (TDD)

### Purpose

Implement the feature using Test-Driven Development.

### TDD Cycle

```
┌──────────────┐
│   1. RED     │  Write failing test
└──────┬───────┘
       │
       ▼
┌──────────────┐
│   2. GREEN   │  Write minimal code to pass
└──────┬───────┘
       │
       ▼
┌──────────────┐
│  3. REFACTOR │  Improve code quality
└──────┬───────┘
       │
       └──────────► Repeat
```

### TDD Process

1. **Write Test First**
   ```python
   def test_process_valid_input():
       """Test processing with valid input."""
       processor = Processor()
       result = processor.process([1, 2, 3])
       assert result == [2, 4, 6]
   ```

2. **Run Test (Should Fail)**
   ```bash
   pytest tests/test_processor.py -v
   # Expected: FAILED
   ```

3. **Write Minimal Implementation**
   ```python
   class Processor:
       def process(self, data):
           return [x * 2 for x in data]
   ```

4. **Run Test (Should Pass)**
   ```bash
   pytest tests/test_processor.py -v
   # Expected: PASSED
   ```

5. **Refactor**
   ```python
   class Processor:
       def __init__(self, multiplier: int = 2):
           self.multiplier = multiplier

       def process(self, data: List[int]) -> List[int]:
           return [x * self.multiplier for x in data]
   ```

### Test Categories

```python
# Unit Tests
class TestProcessor:
    def test_process_valid_input(self):
        """Test with valid input."""
        ...

    def test_process_empty_input(self):
        """Test with empty input."""
        ...

    def test_process_invalid_input(self):
        """Test with invalid input raises error."""
        ...

# Integration Tests
class TestProcessorIntegration:
    def test_end_to_end_workflow(self):
        """Test complete workflow."""
        ...

# Performance Tests
class TestProcessorPerformance:
    def test_large_dataset_performance(self):
        """Test performance with large dataset."""
        ...
```

## Phase 5: Completion

### Purpose

Finalize for production: documentation, cleanup, and verification.

### Completion Checklist

```markdown
## Code Quality
- [ ] All tests passing
- [ ] Test coverage ≥ 80%
- [ ] No linting errors
- [ ] Type hints complete
- [ ] Docstrings complete

## Documentation
- [ ] README updated
- [ ] API documentation
- [ ] Usage examples
- [ ] Changelog entry

## Security
- [ ] Input validation
- [ ] Error messages safe
- [ ] No hardcoded secrets
- [ ] Dependencies audited

## Performance
- [ ] Benchmarks run
- [ ] Memory usage checked
- [ ] No N+1 queries
- [ ] Caching implemented (if needed)

## Deployment
- [ ] Configuration documented
- [ ] Migration scripts (if needed)
- [ ] Rollback plan
- [ ] Monitoring in place
```

## Using SPARC with Claude Flow

### Start SPARC Workflow

```bash
npx claude-flow sparc run dev "feature description"
```

### Available Modes

| Mode | Focus |
|------|-------|
| `dev` | Full development cycle |
| `api` | API development |
| `ui` | UI development |
| `test` | Testing focus |
| `refactor` | Code improvement |

### TDD Mode

```bash
npx claude-flow sparc tdd "feature to implement"
```

## SPARC File Locations

```
.agent-os/
├── specs/
│   └── feature-name/
│       ├── spec.md              # Specification
│       ├── tasks.md             # Task breakdown
│       └── sub-specs/
│           ├── pseudocode.md    # Pseudocode
│           ├── architecture.md  # Architecture
│           ├── tests.md         # Test spec
│           └── api-spec.md      # API spec (if applicable)
└── product/
    └── decisions.md             # Decision log
```

## Integration with Agent OS

### Creating a Spec

```bash
# Use the create-spec workflow
# Reference: @~/.agent-os/instructions/create-spec.md
```

### Executing Tasks

```bash
# Use the execute-tasks workflow
# Reference: @~/.agent-os/instructions/execute-tasks.md
```

## Best Practices

### Specification

1. Write requirements from user perspective
2. Make every requirement testable
3. Explicitly define boundaries
4. Get stakeholder approval

### Pseudocode

1. Stay language-agnostic
2. Show all decision branches
3. Include error paths
4. Note time/space complexity

### Architecture

1. Keep components loosely coupled
2. Design for testability
3. Plan for scalability
4. Document dependencies

### Refinement

1. One test per behavior
2. Test edge cases first
3. Keep tests isolated
4. Maintain fast test suite

### Completion

1. Review all checklist items
2. Run full test suite
3. Update documentation
4. Plan deployment

---

## Version History

- **1.0.0** (2024-10-15): Initial release with 5 SPARC phases, TDD integration, Claude Flow support, Agent OS integration
