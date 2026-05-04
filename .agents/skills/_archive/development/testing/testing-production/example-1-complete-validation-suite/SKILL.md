---
name: testing-production-example-1-complete-validation-suite
description: 'Sub-skill of testing-production: Example 1: Complete Validation Suite
  (+2).'
version: 1.0.0
category: development
type: reference
scripts_exempt: true
---

# Example 1: Complete Validation Suite (+2)

## Example 1: Complete Validation Suite


```typescript
describe('Production Readiness Validation', () => {
  describe('Implementation Completeness', () => {
    it('should have no mock implementations in production code', async () => {
      const result = await exec(
        'grep -r "mock\\|fake\\|stub" src/ --exclude-dir=__tests__ --exclude="*.test.*"'
      );
      expect(result.stdout).toBe('');
    });

    it('should have no TODO/FIXME in critical paths', async () => {
      const result = await exec('grep -r "TODO\\|FIXME" src/');
      expect(result.stdout).toBe('');
    });

    it('should have no hardcoded test data', async () => {
      const result = await exec(
        'grep -r "test@\\|example\\|localhost" src/ --exclude-dir=__tests__'
      );
      expect(result.stdout).toBe('');
    });
  });

  describe('Environment Configuration', () => {
    it('should have all required environment variables', () => {
      const required = [
        'DATABASE_URL',
        'REDIS_URL',
        'API_KEY',
        'SMTP_HOST',
        'JWT_SECRET'
      ];

      const missing = required.filter(key => !process.env[key]);
      expect(missing).toEqual([]);
    });
  });
});
```


## Example 2: Infrastructure Validation


```typescript
describe('Infrastructure Validation', () => {
  it('should connect to real Redis cache', async () => {
    const cache = new RedisCache({
      host: process.env.REDIS_HOST,
      port: parseInt(process.env.REDIS_PORT || '6379'),
      password: process.env.REDIS_PASSWORD
    });

    await cache.connect();

    // Test cache operations
    await cache.set('validation-key', 'test-value', 300);
    const value = await cache.get('validation-key');
    expect(value).toBe('test-value');

    await cache.delete('validation-key');
    const deleted = await cache.get('validation-key');
    expect(deleted).toBeNull();

    await cache.disconnect();
  });

  it('should send real emails via SMTP', async () => {
    const emailService = new EmailService({
      host: process.env.SMTP_HOST,
      port: parseInt(process.env.SMTP_PORT || '587'),
      auth: {
        user: process.env.SMTP_USER,
        pass: process.env.SMTP_PASS
      }
    });

    const result = await emailService.send({
      to: 'validation-test@example.com',
      subject: 'Production Validation Test',
      body: 'This is a real email sent during validation'
    });

    expect(result.messageId).toBeDefined();
    expect(result.accepted).toContain('validation-test@example.com');
  });
});
```


## Example 3: Performance Validation


```typescript
describe('Performance Validation', () => {
  it('should handle concurrent requests within latency requirements', async () => {
    const apiClient = new APIClient(process.env.API_BASE_URL);
    const concurrentRequests = 100;
    const startTime = Date.now();

    const promises = Array.from({ length: concurrentRequests }, () =>
      apiClient.get('/health')
    );

    const results = await Promise.all(promises);
    const duration = Date.now() - startTime;

    // All requests succeeded
    expect(results.every(r => r.status === 200)).toBe(true);

    // Within 5 seconds for 100 requests
    expect(duration).toBeLessThan(5000);

    // Average response time under 50ms
    const avgResponseTime = duration / concurrentRequests;
    expect(avgResponseTime).toBeLessThan(50);
  });

  it('should maintain performance under sustained load', async () => {
    const apiClient = new APIClient(process.env.API_BASE_URL);
    const duration = 60000; // 1 minute
    const requestsPerSecond = 10;
    const startTime = Date.now();

    let totalRequests = 0;
    let successfulRequests = 0;

    while (Date.now() - startTime < duration) {
      const batchStart = Date.now();
      const batch = Array.from({ length: requestsPerSecond }, () =>
        apiClient.get('/api/users').catch(() => null)
      );

      const results = await Promise.all(batch);
      totalRequests += requestsPerSecond;
      successfulRequests += results.filter(r => r?.status === 200).length;

      // Throttle to maintain rate
      const elapsed = Date.now() - batchStart;
      if (elapsed < 1000) {
        await new Promise(resolve => setTimeout(resolve, 1000 - elapsed));
      }
    }

    const successRate = successfulRequests / totalRequests;
    expect(successRate).toBeGreaterThan(0.95); // 95% success rate
  });
});
```
