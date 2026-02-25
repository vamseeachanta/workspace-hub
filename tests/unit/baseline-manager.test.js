const { BaselineManager } = require('../../src/baseline/baseline-manager');
const MockFactory = require('../fixtures/mock-factories');
const { sampleBaseline, sampleTestResults, edgeCases } = require('../fixtures/baseline-data');

describe('BaselineManager', () => {
  let baselineManager;
  let mockDatabase;
  let mockLogger;
  let mockMetrics;

  beforeEach(() => {
    mockDatabase = {
      create: jest.fn(),
      findById: jest.fn(),
      update: jest.fn(),
      delete: jest.fn(),
      list: jest.fn()
    };

    mockLogger = {
      info: jest.fn(),
      warn: jest.fn(),
      error: jest.fn(),
      debug: jest.fn()
    };

    mockMetrics = {
      increment: jest.fn(),
      timing: jest.fn(),
      histogram: jest.fn()
    };

    const config = {
      database: mockDatabase,
      logger: mockLogger,
      metrics: mockMetrics,
      baselineDirectory: '/tmp/baselines',
      retentionDays: 30
    };

    baselineManager = new BaselineManager(config);
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  describe('constructor', () => {
    it('should initialize with required dependencies', () => {
      expect(baselineManager).toBeInstanceOf(BaselineManager);
      expect(baselineManager.database).toBe(mockDatabase);
      expect(baselineManager.logger).toBe(mockLogger);
      expect(baselineManager.metrics).toBe(mockMetrics);
    });

    it('should throw error when required dependencies are missing', () => {
      expect(() => new BaselineManager({})).toThrow('Database is required');
      expect(() => new BaselineManager({ database: mockDatabase })).toThrow('Logger is required');
    });

    it('should use default metrics if not provided', () => {
      const manager = new BaselineManager({ database: mockDatabase, logger: mockLogger });
      expect(manager.metrics).toBeDefined();
    });
  });

  describe('createBaseline', () => {
    it('should create a new baseline with valid data', async () => {
      const baselineData = MockFactory.createBaseline();
      const expectedId = 'baseline-123';
      
      mockDatabase.query.mockResolvedValueOnce({ insertId: expectedId });
      mockDatabase.query.mockResolvedValueOnce([{ ...baselineData, id: expectedId }]);

      const result = await baselineManager.createBaseline(baselineData);

      expect(result).toEqual(expect.objectContaining({
        id: expectedId,
        name: baselineData.name,
        status: 'active'
      }));
      expect(mockDatabase.query).toHaveBeenCalledTimes(2);
      expect(mockMetrics.increment).toHaveBeenCalledWith('baseline.created');
      expect(mockLogger.info).toHaveBeenCalledWith(
        'Baseline created successfully',
        expect.objectContaining({ baselineId: expectedId })
      );
    });

    it('should validate required fields before creation', async () => {
      const invalidData = { name: '', projectId: null };

      await expect(baselineManager.createBaseline(invalidData))
        .rejects.toThrow('Name is required');
      
      expect(mockDatabase.query).not.toHaveBeenCalled();
      expect(mockLogger.error).toHaveBeenCalledWith(
        'Baseline creation failed: validation error',
        expect.any(Object)
      );
    });

    it('should handle database errors gracefully', async () => {
      const baselineData = MockFactory.createBaseline();
      const dbError = new Error('Database connection failed');
      
      mockDatabase.query.mockRejectedValueOnce(dbError);

      await expect(baselineManager.createBaseline(baselineData))
        .rejects.toThrow('Failed to create baseline');
      
      expect(mockLogger.error).toHaveBeenCalledWith(
        'Database error during baseline creation',
        expect.objectContaining({ error: dbError.message })
      );
      expect(mockMetrics.increment).toHaveBeenCalledWith('baseline.creation_failed');
    });

    it('should sanitize input data', async () => {
      const maliciousData = {
        name: '<script>alert("xss")</script>',
        description: 'DROP TABLE baselines;',
        projectId: 'project-1'
      };
      
      mockDatabase.query.mockResolvedValueOnce({ insertId: 'baseline-123' });
      mockDatabase.query.mockResolvedValueOnce([{ id: 'baseline-123' }]);

      await baselineManager.createBaseline(maliciousData);

      const createCall = mockDatabase.query.mock.calls[0];
      expect(createCall[1]).toEqual(expect.objectContaining({
        name: '&lt;script&gt;alert(&quot;xss&quot;)&lt;/script&gt;',
        description: 'DROP TABLE baselines;' // SQL injection handled by parameterized queries
      }));
    });
  });

  describe('getBaseline', () => {
    it('should retrieve baseline by ID', async () => {
      const baseline = MockFactory.createBaseline();
      mockDatabase.query.mockResolvedValueOnce([baseline]);

      const result = await baselineManager.getBaseline(baseline.id);

      expect(result).toEqual(baseline);
      expect(mockDatabase.query).toHaveBeenCalledWith(
        'SELECT * FROM baselines WHERE id = ? AND deleted_at IS NULL',
        [baseline.id]
      );
    });

    it('should return null for non-existent baseline', async () => {
      mockDatabase.query.mockResolvedValueOnce([]);

      const result = await baselineManager.getBaseline('non-existent');

      expect(result).toBeNull();
      expect(mockLogger.debug).toHaveBeenCalledWith(
        'Baseline not found',
        { baselineId: 'non-existent' }
      );
    });

    it('should handle database errors', async () => {
      const dbError = new Error('Query failed');
      mockDatabase.query.mockRejectedValueOnce(dbError);

      await expect(baselineManager.getBaseline('baseline-123'))
        .rejects.toThrow('Failed to retrieve baseline');
      
      expect(mockLogger.error).toHaveBeenCalledWith(
        'Database error during baseline retrieval',
        expect.objectContaining({ error: dbError.message })
      );
    });

    it('should validate baseline ID format', async () => {
      await expect(baselineManager.getBaseline(''))
        .rejects.toThrow('Invalid baseline ID');
      
      await expect(baselineManager.getBaseline(null))
        .rejects.toThrow('Invalid baseline ID');
      
      await expect(baselineManager.getBaseline(123))
        .rejects.toThrow('Invalid baseline ID');
    });
  });

  describe('updateBaseline', () => {
    it('should update baseline with valid data', async () => {
      const baselineId = 'baseline-123';
      const updateData = {
        name: 'Updated Baseline',
        description: 'Updated description',
        thresholds: MockFactory.createThresholds()
      };
      
      mockDatabase.query.mockResolvedValueOnce({ affectedRows: 1 });
      mockDatabase.query.mockResolvedValueOnce([{ ...updateData, id: baselineId }]);

      const result = await baselineManager.updateBaseline(baselineId, updateData);

      expect(result).toEqual(expect.objectContaining(updateData));
      expect(mockDatabase.query).toHaveBeenCalledWith(
        expect.stringContaining('UPDATE baselines SET'),
        expect.arrayContaining([baselineId])
      );
      expect(mockMetrics.increment).toHaveBeenCalledWith('baseline.updated');
    });

    it('should not update non-existent baseline', async () => {
      mockDatabase.query.mockResolvedValueOnce({ affectedRows: 0 });

      await expect(baselineManager.updateBaseline('non-existent', { name: 'New Name' }))
        .rejects.toThrow('Baseline not found or no changes made');
    });

    it('should prevent updating immutable fields', async () => {
      const updateData = {
        id: 'new-id',
        createdAt: '2024-01-01T00:00:00Z',
        projectId: 'different-project'
      };

      await expect(baselineManager.updateBaseline('baseline-123', updateData))
        .rejects.toThrow('Cannot update immutable fields');
    });

    it('should validate update data', async () => {
      const invalidData = {
        name: '',
        thresholds: { passRate: { min: 150 } } // Invalid percentage
      };

      await expect(baselineManager.updateBaseline('baseline-123', invalidData))
        .rejects.toThrow('Validation failed');
    });
  });

  describe('deleteBaseline', () => {
    it('should soft delete baseline', async () => {
      const baselineId = 'baseline-123';
      mockDatabase.query.mockResolvedValueOnce({ affectedRows: 1 });

      await baselineManager.deleteBaseline(baselineId);

      expect(mockDatabase.query).toHaveBeenCalledWith(
        'UPDATE baselines SET deleted_at = NOW(), status = ? WHERE id = ?',
        ['deleted', baselineId]
      );
      expect(mockMetrics.increment).toHaveBeenCalledWith('baseline.deleted');
      expect(mockLogger.info).toHaveBeenCalledWith(
        'Baseline deleted successfully',
        { baselineId }
      );
    });

    it('should handle deletion of non-existent baseline', async () => {
      mockDatabase.query.mockResolvedValueOnce({ affectedRows: 0 });

      await expect(baselineManager.deleteBaseline('non-existent'))
        .rejects.toThrow('Baseline not found');
    });

    it('should prevent deletion of active baselines with dependencies', async () => {
      const baselineId = 'baseline-123';
      mockDatabase.query.mockResolvedValueOnce([{ count: 5 }]); // Has comparisons

      await expect(baselineManager.deleteBaseline(baselineId, { force: false }))
        .rejects.toThrow('Cannot delete baseline with active dependencies');
    });

    it('should allow forced deletion', async () => {
      const baselineId = 'baseline-123';
      mockDatabase.transaction.mockImplementation(async (callback) => {
        return await callback(mockDatabase);
      });
      mockDatabase.query.mockResolvedValue({ affectedRows: 1 });

      await baselineManager.deleteBaseline(baselineId, { force: true });

      expect(mockDatabase.transaction).toHaveBeenCalled();
      expect(mockLogger.warn).toHaveBeenCalledWith(
        'Force deleting baseline with dependencies',
        { baselineId }
      );
    });
  });

  describe('listBaselines', () => {
    it('should list baselines with default pagination', async () => {
      const baselines = [
        MockFactory.createBaseline(),
        MockFactory.createBaseline(),
        MockFactory.createBaseline()
      ];
      
      mockDatabase.query.mockResolvedValueOnce([{ total: 3 }]);
      mockDatabase.query.mockResolvedValueOnce(baselines);

      const result = await baselineManager.listBaselines();

      expect(result).toEqual({
        baselines,
        pagination: {
          page: 1,
          limit: 20,
          total: 3,
          totalPages: 1
        }
      });
    });

    it('should filter baselines by project', async () => {
      const projectId = 'project-1';
      mockDatabase.query.mockResolvedValueOnce([{ total: 2 }]);
      mockDatabase.query.mockResolvedValueOnce([]);

      await baselineManager.listBaselines({ projectId });

      expect(mockDatabase.query).toHaveBeenCalledWith(
        expect.stringContaining('WHERE project_id = ?'),
        expect.arrayContaining([projectId])
      );
    });

    it('should sort baselines by specified field', async () => {
      mockDatabase.query.mockResolvedValueOnce([{ total: 1 }]);
      mockDatabase.query.mockResolvedValueOnce([]);

      await baselineManager.listBaselines({ 
        sortBy: 'created_at',
        sortOrder: 'DESC'
      });

      expect(mockDatabase.query).toHaveBeenCalledWith(
        expect.stringContaining('ORDER BY created_at DESC'),
        expect.any(Array)
      );
    });

    it('should validate pagination parameters', async () => {
      await expect(baselineManager.listBaselines({ page: 0 }))
        .rejects.toThrow('Page must be greater than 0');
      
      await expect(baselineManager.listBaselines({ limit: 0 }))
        .rejects.toThrow('Limit must be greater than 0');
      
      await expect(baselineManager.listBaselines({ limit: 1001 }))
        .rejects.toThrow('Limit cannot exceed 1000');
    });
  });

  describe('validateBaseline', () => {
    it('should validate correct baseline data', () => {
      const validBaseline = MockFactory.createBaseline();
      
      expect(() => baselineManager.validateBaseline(validBaseline))
        .not.toThrow();
    });

    it('should reject baseline with missing required fields', () => {
      const invalidBaseline = { description: 'Missing name and project' };
      
      expect(() => baselineManager.validateBaseline(invalidBaseline))
        .toThrow('Name is required');
    });

    it('should validate threshold values', () => {
      const invalidThresholds = {
        ...MockFactory.createBaseline(),
        thresholds: {
          passRate: { min: 150, max: 200 }, // Invalid percentages
          coverage: { lines: { min: -10 } }
        }
      };
      
      expect(() => baselineManager.validateBaseline(invalidThresholds))
        .toThrow('Invalid threshold values');
    });

    it('should validate metrics structure', () => {
      const invalidMetrics = {
        ...MockFactory.createBaseline(),
        metrics: {
          testCount: 'not-a-number',
          passRate: 150
        }
      };
      
      expect(() => baselineManager.validateBaseline(invalidMetrics))
        .toThrow('Invalid metrics structure');
    });
  });

  describe('edge cases', () => {
    it('should handle empty baseline data', async () => {
      const emptyBaseline = edgeCases.emptyBaseline;
      
      expect(() => baselineManager.validateBaseline(emptyBaseline))
        .not.toThrow();
    });

    it('should handle extreme metric values', async () => {
      const extremeBaseline = edgeCases.extremeValues;
      
      expect(() => baselineManager.validateBaseline(extremeBaseline))
        .not.toThrow();
    });

    it('should reject invalid data types', async () => {
      const invalidBaseline = edgeCases.invalidData;
      
      expect(() => baselineManager.validateBaseline(invalidBaseline))
        .toThrow();
    });

    it('should handle concurrent access', async () => {
      const baselineData = MockFactory.createBaseline();
      mockDatabase.query.mockResolvedValue({ insertId: 'baseline-123' });
      
      const promises = Array(10).fill(null).map(() => 
        baselineManager.createBaseline(baselineData)
      );
      
      // Should not throw errors due to race conditions
      await expect(Promise.all(promises)).resolves.toBeDefined();
    });

    it('should handle very long field values', async () => {
      const longName = 'x'.repeat(1000);
      const baselineData = MockFactory.createBaseline({ name: longName });
      
      expect(() => baselineManager.validateBaseline(baselineData))
        .toThrow('Name exceeds maximum length');
    });
  });

  describe('performance', () => {
    it('should handle large result sets efficiently', async () => {
      const largeResultSet = Array(1000).fill(null).map(() => 
        MockFactory.createBaseline()
      );
      
      mockDatabase.query.mockResolvedValueOnce([{ total: 1000 }]);
      mockDatabase.query.mockResolvedValueOnce(largeResultSet);
      
      const startTime = Date.now();
      await baselineManager.listBaselines({ limit: 1000 });
      const endTime = Date.now();
      
      // Should complete within reasonable time
      expect(endTime - startTime).toBeLessThan(1000);
    });

    it('should cache frequently accessed baselines', async () => {
      const baseline = MockFactory.createBaseline();
      mockDatabase.query.mockResolvedValue([baseline]);
      
      // First call
      await baselineManager.getBaseline(baseline.id);
      // Second call - should use cache
      await baselineManager.getBaseline(baseline.id);
      
      // Database should only be called once due to caching
      expect(mockDatabase.query).toHaveBeenCalledTimes(1);
    });
  });
});
