---
name: sparc-refinement-red-phase-write-failing-tests
description: 'Sub-skill of sparc-refinement: Red Phase - Write Failing Tests (+2).'
version: 1.0.0
category: development
type: reference
scripts_exempt: true
---

# Red Phase - Write Failing Tests (+2)

## Red Phase - Write Failing Tests


```typescript
// Step 1: Write test that defines desired behavior
describe('AuthenticationService', () => {
  let service: AuthenticationService;
  let mockUserRepo: jest.Mocked<UserRepository>;
  let mockCache: jest.Mocked<CacheService>;

  beforeEach(() => {
    mockUserRepo = createMockRepository();
    mockCache = createMockCache();

*See sub-skills for full details.*

## Green Phase - Make Tests Pass


```typescript
// Step 2: Implement minimum code to pass tests
export class AuthenticationService {
  private failedAttempts = new Map<string, number>();
  private readonly MAX_ATTEMPTS = 5;
  private readonly LOCK_DURATION = 15 * 60 * 1000; // 15 minutes

  constructor(
    private userRepo: UserRepository,
    private cache: CacheService,

*See sub-skills for full details.*

## Refactor Phase - Improve Code Quality


```typescript
// Step 3: Refactor while keeping tests green
export class AuthenticationService {
  constructor(
    private userRepo: UserRepository,
    private cache: CacheService,
    private logger: Logger,
    private config: AuthConfig,
    private eventBus: EventBus
  ) {}

*See sub-skills for full details.*
