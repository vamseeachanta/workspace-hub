const { BaselineManager } = require('../../src/baseline/baseline-manager');

describe('BaselineManager - Simple Tests', () => {
  it('should import BaselineManager successfully', () => {
    expect(BaselineManager).toBeDefined();
    expect(typeof BaselineManager).toBe('function');
  });

  it('should create an instance with minimal config', () => {
    const config = {
      baselineDirectory: '/tmp/baselines',
      retentionDays: 30
    };

    const manager = new BaselineManager(config);
    expect(manager).toBeInstanceOf(BaselineManager);
  });

  it('should throw error with invalid config', () => {
    expect(() => new BaselineManager(null)).toThrow();
    expect(() => new BaselineManager(undefined)).toThrow();
  });
});