---
name: testing-tdd-london-london-vs-chicago-school
description: 'Sub-skill of testing-tdd-london: London vs Chicago School (+2).'
version: 1.0.0
category: development
type: reference
scripts_exempt: true
---

# London vs Chicago School (+2)

## London vs Chicago School


| Aspect | London (Mockist) | Chicago (Classicist) |
|--------|------------------|----------------------|
| Focus | Behavior/Interactions | State |
| Isolation | Mock all collaborators | Use real objects |
| Direction | Outside-in | Inside-out |
| Test What | HOW objects talk | WHAT objects produce |
| Coupling | To implementation | To behavior |

## Outside-In Development Flow


```
Acceptance Test (failing)
    |
    v
Controller Test (failing)
    |
    v
Service Test (failing)
    |
    v
Repository Test (failing)
    |
    v
Implement (make tests pass from bottom up)
```

## Mock Types


```typescript
// Stub: Returns canned responses
const stubRepo = { findById: jest.fn().mockResolvedValue(user) };

// Mock: Verifies interactions
const mockNotifier = { send: jest.fn() };
// Later: expect(mockNotifier.send).toHaveBeenCalledWith(expectedArgs);

// Spy: Wraps real object, records calls
const spyLogger = jest.spyOn(logger, 'info');
```
