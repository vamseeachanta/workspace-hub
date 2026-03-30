---
name: testing-production-example-4-security-validation
description: 'Sub-skill of testing-production: Example 4: Security Validation.'
version: 1.0.0
category: development
type: reference
scripts_exempt: true
---

# Example 4: Security Validation

## Example 4: Security Validation


```typescript
describe('Security Validation', () => {
  it('should enforce authentication on protected routes', async () => {
    const response = await request(app)
      .get('/api/protected')
      .expect(401);

    expect(response.body.error).toBe('Authentication required');
  });

  it('should validate and sanitize input', async () => {
    const maliciousInput = '<script>alert("xss")</script>';

    const response = await request(app)
      .post('/api/users')
      .send({ name: maliciousInput })
      .set('Authorization', `Bearer ${validToken}`)
      .expect(400);

    expect(response.body.error).toContain('Invalid input');
  });

  it('should use HTTPS in production', () => {
    if (process.env.NODE_ENV === 'production') {
      expect(process.env.FORCE_HTTPS).toBe('true');
    }
  });

  it('should have proper health check endpoint', async () => {
    const response = await request(app)
      .get('/health')
      .expect(200);

    expect(response.body).toMatchObject({
      status: 'healthy',
      timestamp: expect.any(String),
      uptime: expect.any(Number),
      dependencies: {
        database: 'connected',
        cache: 'connected',
        external_api: 'reachable'
      }
    });
  });
});
```
