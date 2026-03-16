---
name: core-tester-performance-testing
description: 'Sub-skill of core-tester: Performance Testing (+1).'
version: 1.0.0
category: coordination
type: reference
scripts_exempt: true
---

# Performance Testing (+1)

## Performance Testing


```typescript
describe('Performance', () => {
  it('should process 1000 items under 100ms', async () => {
    const items = generateItems(1000);

    const start = performance.now();
    await service.processItems(items);
    const duration = performance.now() - start;

    expect(duration).toBeLessThan(100);
  });

  it('should handle memory efficiently', () => {
    const initialMemory = process.memoryUsage().heapUsed;

    // Process large dataset
    processLargeDataset();
    global.gc(); // Force garbage collection

    const finalMemory = process.memoryUsage().heapUsed;
    const memoryIncrease = finalMemory - initialMemory;

    expect(memoryIncrease).toBeLessThan(50 * 1024 * 1024); // <50MB
  });
});
```


## Security Testing


```typescript
describe('Security', () => {
  it('should prevent SQL injection', async () => {
    const maliciousInput = "'; DROP TABLE users; --";

    const response = await request(app)
      .get(`/users?name=${maliciousInput}`);

    expect(response.status).not.toBe(500);
    // Verify table still exists
    const users = await database.query('SELECT * FROM users');
    expect(users).toBeDefined();
  });

  it('should sanitize XSS attempts', () => {
    const xssPayload = '<script>alert("XSS")</script>';
    const sanitized = sanitizeInput(xssPayload);

    expect(sanitized).not.toContain('<script>');
    expect(sanitized).toBe('&lt;script&gt;alert("XSS")&lt;/script&gt;');
  });
});
```
