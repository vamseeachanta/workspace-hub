---
name: testing-tdd-london-example-1-service-orchestration-test
description: 'Sub-skill of testing-tdd-london: Example 1: Service Orchestration Test
  (+2).'
version: 1.0.0
category: development
type: reference
scripts_exempt: true
---

# Example 1: Service Orchestration Test (+2)

## Example 1: Service Orchestration Test


```typescript
describe('Service Collaboration', () => {
  let mockServiceA: jest.Mocked<ServiceA>;
  let mockServiceB: jest.Mocked<ServiceB>;
  let mockServiceC: jest.Mocked<ServiceC>;
  let orchestrator: ServiceOrchestrator;

  beforeEach(() => {
    mockServiceA = {
      prepare: jest.fn().mockResolvedValue({ data: 'prepared' })
    };
    mockServiceB = {
      process: jest.fn().mockResolvedValue({ result: 'processed' })
    };
    mockServiceC = {
      finalize: jest.fn().mockResolvedValue({ status: 'complete' })
    };

    orchestrator = new ServiceOrchestrator(
      mockServiceA,
      mockServiceB,
      mockServiceC
    );
  });

  it('should coordinate dependencies in correct order', async () => {
    await orchestrator.execute(task);

    // Verify coordination sequence
    expect(mockServiceA.prepare).toHaveBeenCalledBefore(mockServiceB.process);
    expect(mockServiceB.process).toHaveBeenCalledBefore(mockServiceC.finalize);

    // Verify data flow between services
    expect(mockServiceB.process).toHaveBeenCalledWith(
      expect.objectContaining({ data: 'prepared' })
    );
    expect(mockServiceC.finalize).toHaveBeenCalledWith(
      expect.objectContaining({ result: 'processed' })
    );
  });
});
```


## Example 2: Error Handling Verification


```typescript
describe('Error Handling', () => {
  it('should handle repository failure gracefully', async () => {
    const mockRepository = {
      save: jest.fn().mockRejectedValue(new Error('Connection failed'))
    };
    const mockLogger = {
      error: jest.fn()
    };
    const mockRetry = {
      attempt: jest.fn().mockResolvedValue(false)
    };

    const service = new UserService(mockRepository, mockLogger, mockRetry);

    await expect(service.register(userData)).rejects.toThrow('Registration failed');

    // Verify error handling interactions
    expect(mockLogger.error).toHaveBeenCalledWith(
      'Repository save failed',
      expect.objectContaining({ error: expect.any(Error) })
    );
    expect(mockRetry.attempt).toHaveBeenCalledTimes(3);
  });
});
```


## Example 3: Swarm Coordination Testing


```typescript
describe('Swarm Test Coordination', () => {
  let swarmCoordinator: SwarmCoordinator;

  beforeAll(async () => {
    // Signal other swarm agents
    await swarmCoordinator.notifyTestStart('unit-tests');
  });

  afterAll(async () => {
    // Share test results with swarm
    await swarmCoordinator.shareResults(testResults);
  });

  it('should share mock contracts across swarm', () => {
    const sharedMocks = {
      userRepository: createSwarmMock('UserRepository', {
        save: jest.fn(),
        findByEmail: jest.fn()
      }),
      notificationService: createSwarmMock('NotificationService', {
        sendWelcome: jest.fn()
      })
    };

    // Other swarm agents can verify against these contracts
    swarmCoordinator.publishContracts(sharedMocks);
  });
});
```
