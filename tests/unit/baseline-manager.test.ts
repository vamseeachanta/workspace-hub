/**
 * Unit tests for BaselineManager
 */

import { BaselineManager } from '../../src/baseline/baseline-manager';
import { FileUtils } from '../../src/utils/file-utils';
import { BaselineData, MetricsSnapshot, BaselineConfig } from '../../src/types';
import * as fs from 'fs-extra';
import * as path from 'path';

// Mock FileUtils
jest.mock('../../src/utils/file-utils');
const MockedFileUtils = FileUtils as jest.Mocked<typeof FileUtils>;

describe('BaselineManager', () => {
  let baselineManager: BaselineManager;
  let config: BaselineConfig;
  let tempDir: string;

  beforeEach(async () => {
    tempDir = await fs.mkdtemp(path.join(require('os').tmpdir(), 'baseline-test-'));

    config = {
      storagePath: tempDir,
      retentionPolicy: {
        maxVersions: 5,
        maxAge: 30
      },
      mergeStrategy: 'latest',
      backupEnabled: true,
      backupPath: path.join(tempDir, 'backups')
    };

    baselineManager = new BaselineManager(config);

    // Reset mocks
    jest.clearAllMocks();
  });

  afterEach(async () => {
    await fs.remove(tempDir);
  });

  describe('constructor', () => {
    it('should create instance with valid config', () => {
      expect(baselineManager).toBeInstanceOf(BaselineManager);
    });

    it('should throw error with invalid config', () => {
      expect(() => new BaselineManager(null as any)).toThrow();
    });
  });

  describe('createBaseline', () => {
    const mockSnapshot: MetricsSnapshot = {
      id: 'snapshot-1',
      branch: 'main',
      commit: 'abc123',
      environment: 'production',
      version: '1.0.0',
      tests: {
        results: [],
        summary: {
          total: 10,
          passed: 8,
          failed: 2,
          skipped: 0,
          duration: 1000
        }
      },
      coverage: {
        lines: { total: 100, covered: 80, percentage: 80 },
        functions: { total: 50, covered: 40, percentage: 80 },
        branches: { total: 20, covered: 16, percentage: 80 },
        statements: { total: 100, covered: 80, percentage: 80 },
        files: []
      },
      performance: [],
      metadata: {},
      created: new Date(),
      updated: new Date()
    };

    it('should create baseline from snapshot', async () => {
      MockedFileUtils.writeJsonFile.mockResolvedValue();

      const baseline = await baselineManager.createBaseline('test-baseline', mockSnapshot);

      expect(baseline).toBeDefined();
      expect(baseline.name).toBe('test-baseline');
      expect(baseline.branch).toBe('main');
      expect(baseline.metrics).toEqual(mockSnapshot);
      expect(MockedFileUtils.writeJsonFile).toHaveBeenCalledTimes(1);
    });

    it('should create baseline with options', async () => {
      MockedFileUtils.writeJsonFile.mockResolvedValue();

      const baseline = await baselineManager.createBaseline('test-baseline', mockSnapshot, {
        isDefault: true,
        tags: ['release', 'stable'],
        metadata: { releaseVersion: '1.0.0' }
      });

      expect(baseline.isDefault).toBe(true);
      expect(baseline.tags).toEqual(['release', 'stable']);
      expect(baseline.metadata.releaseVersion).toBe('1.0.0');
    });

    it('should validate snapshot before creating baseline', async () => {
      const invalidSnapshot = { invalid: true } as any;

      await expect(
        baselineManager.createBaseline('test', invalidSnapshot)
      ).rejects.toThrow();
    });
  });

  describe('loadBaseline', () => {
    const mockBaseline: BaselineData = {
      id: 'baseline-1',
      name: 'test-baseline',
      branch: 'main',
      commit: 'abc123',
      environment: 'production',
      version: '1.0.0',
      metrics: {} as MetricsSnapshot,
      isDefault: false,
      tags: [],
      metadata: {},
      created: new Date(),
      updated: new Date()
    };

    it('should load existing baseline', async () => {
      MockedFileUtils.fileExists.mockResolvedValue(true);
      MockedFileUtils.readJsonFile.mockResolvedValue(mockBaseline);

      const loaded = await baselineManager.loadBaseline('baseline-1');

      expect(loaded).toEqual(mockBaseline);
      expect(MockedFileUtils.readJsonFile).toHaveBeenCalledWith(
        path.join(tempDir, 'baseline-1.baseline.json')
      );
    });

    it('should throw error for non-existent baseline', async () => {
      MockedFileUtils.fileExists.mockResolvedValue(false);

      await expect(
        baselineManager.loadBaseline('non-existent')
      ).rejects.toThrow('Baseline not found: non-existent');
    });

    it('should cache loaded baselines', async () => {
      MockedFileUtils.fileExists.mockResolvedValue(true);
      MockedFileUtils.readJsonFile.mockResolvedValue(mockBaseline);

      // Load twice
      await baselineManager.loadBaseline('baseline-1');
      await baselineManager.loadBaseline('baseline-1');

      // Should only read from file once
      expect(MockedFileUtils.readJsonFile).toHaveBeenCalledTimes(1);
    });
  });

  describe('saveBaseline', () => {
    const mockBaseline: BaselineData = {
      id: 'baseline-1',
      name: 'test-baseline',
      branch: 'main',
      commit: 'abc123',
      environment: 'production',
      version: '1.0.0',
      metrics: {} as MetricsSnapshot,
      isDefault: false,
      tags: [],
      metadata: {},
      created: new Date(),
      updated: new Date()
    };

    it('should save baseline to file', async () => {
      MockedFileUtils.fileExists.mockResolvedValue(false);
      MockedFileUtils.writeJsonFile.mockResolvedValue();

      await baselineManager.saveBaseline(mockBaseline);

      expect(MockedFileUtils.writeJsonFile).toHaveBeenCalledWith(
        path.join(tempDir, 'baseline-1.baseline.json'),
        expect.objectContaining({
          id: 'baseline-1',
          name: 'test-baseline'
        })
      );
    });

    it('should create backup when file exists', async () => {
      MockedFileUtils.fileExists.mockResolvedValue(true);
      MockedFileUtils.createBackup.mockResolvedValue('backup-path');
      MockedFileUtils.writeJsonFile.mockResolvedValue();

      await baselineManager.saveBaseline(mockBaseline);

      expect(MockedFileUtils.createBackup).toHaveBeenCalled();
    });

    it('should update timestamp on save', async () => {
      MockedFileUtils.fileExists.mockResolvedValue(false);
      MockedFileUtils.writeJsonFile.mockResolvedValue();

      const originalUpdated = mockBaseline.updated;
      await baselineManager.saveBaseline(mockBaseline);

      expect(mockBaseline.updated).not.toBe(originalUpdated);
    });
  });

  describe('updateBaseline', () => {
    const mockBaseline: BaselineData = {
      id: 'baseline-1',
      name: 'test-baseline',
      branch: 'main',
      commit: 'abc123',
      environment: 'production',
      version: '1.0.0',
      metrics: {} as MetricsSnapshot,
      isDefault: false,
      tags: [],
      metadata: {},
      created: new Date(),
      updated: new Date()
    };

    beforeEach(() => {
      MockedFileUtils.fileExists.mockResolvedValue(true);
      MockedFileUtils.readJsonFile.mockResolvedValue(mockBaseline);
      MockedFileUtils.writeJsonFile.mockResolvedValue();
    });

    it('should update baseline properties', async () => {
      const updates = {
        name: 'updated-name',
        tags: ['updated'],
        metadata: { key: 'value' }
      };

      const updated = await baselineManager.updateBaseline('baseline-1', updates);

      expect(updated.name).toBe('updated-name');
      expect(updated.tags).toEqual(['updated']);
      expect(updated.metadata.key).toBe('value');
      expect(updated.id).toBe('baseline-1'); // Should not change
    });

    it('should preserve creation timestamp', async () => {
      const originalCreated = mockBaseline.created;
      const updates = { name: 'new-name' };

      const updated = await baselineManager.updateBaseline('baseline-1', updates);

      expect(updated.created).toBe(originalCreated);
    });
  });

  describe('listBaselines', () => {
    const mockBaselines: BaselineData[] = [
      {
        id: 'baseline-1',
        name: 'baseline-1',
        branch: 'main',
        commit: 'abc123',
        environment: 'production',
        version: '1.0.0',
        metrics: {} as MetricsSnapshot,
        isDefault: true,
        tags: ['stable'],
        metadata: {},
        created: new Date('2023-01-01'),
        updated: new Date('2023-01-01')
      },
      {
        id: 'baseline-2',
        name: 'baseline-2',
        branch: 'develop',
        commit: 'def456',
        environment: 'staging',
        version: '1.1.0',
        metrics: {} as MetricsSnapshot,
        isDefault: false,
        tags: ['beta'],
        metadata: {},
        created: new Date('2023-01-02'),
        updated: new Date('2023-01-02')
      }
    ];

    beforeEach(() => {
      MockedFileUtils.listFiles.mockResolvedValue([
        'baseline-1.baseline.json',
        'baseline-2.baseline.json'
      ]);
      MockedFileUtils.readJsonFile
        .mockResolvedValueOnce(mockBaselines[0])
        .mockResolvedValueOnce(mockBaselines[1]);
    });

    it('should list all baselines', async () => {
      const baselines = await baselineManager.listBaselines();

      expect(baselines).toHaveLength(2);
      expect(baselines[0].id).toBe('baseline-1');
      expect(baselines[1].id).toBe('baseline-2');
    });

    it('should filter baselines by branch', async () => {
      MockedFileUtils.readJsonFile
        .mockResolvedValueOnce(mockBaselines[0])
        .mockResolvedValueOnce(mockBaselines[1]);

      const baselines = await baselineManager.listBaselines({ branch: 'main' });

      expect(baselines).toHaveLength(1);
      expect(baselines[0].branch).toBe('main');
    });

    it('should filter baselines by environment', async () => {
      MockedFileUtils.readJsonFile
        .mockResolvedValueOnce(mockBaselines[0])
        .mockResolvedValueOnce(mockBaselines[1]);

      const baselines = await baselineManager.listBaselines({ environment: 'staging' });

      expect(baselines).toHaveLength(1);
      expect(baselines[0].environment).toBe('staging');
    });

    it('should sort baselines', async () => {
      MockedFileUtils.readJsonFile
        .mockResolvedValueOnce(mockBaselines[0])
        .mockResolvedValueOnce(mockBaselines[1]);

      const baselines = await baselineManager.listBaselines(
        undefined,
        { field: 'created', order: 'desc' }
      );

      expect(baselines[0].created.getTime()).toBeGreaterThan(
        baselines[1].created.getTime()
      );
    });
  });

  describe('getDefaultBaseline', () => {
    const mockBaseline: BaselineData = {
      id: 'baseline-1',
      name: 'default-baseline',
      branch: 'main',
      commit: 'abc123',
      environment: 'production',
      version: '1.0.0',
      metrics: {} as MetricsSnapshot,
      isDefault: true,
      tags: [],
      metadata: {},
      created: new Date(),
      updated: new Date()
    };

    it('should return default baseline for branch and environment', async () => {
      MockedFileUtils.listFiles.mockResolvedValue(['baseline-1.baseline.json']);
      MockedFileUtils.readJsonFile.mockResolvedValue(mockBaseline);

      const defaultBaseline = await baselineManager.getDefaultBaseline('main', 'production');

      expect(defaultBaseline).toBeDefined();
      expect(defaultBaseline!.isDefault).toBe(true);
      expect(defaultBaseline!.branch).toBe('main');
      expect(defaultBaseline!.environment).toBe('production');
    });

    it('should return null when no default baseline exists', async () => {
      MockedFileUtils.listFiles.mockResolvedValue([]);

      const defaultBaseline = await baselineManager.getDefaultBaseline('main', 'production');

      expect(defaultBaseline).toBeNull();
    });
  });

  describe('setAsDefault', () => {
    const mockBaselines: BaselineData[] = [
      {
        id: 'baseline-1',
        name: 'baseline-1',
        branch: 'main',
        commit: 'abc123',
        environment: 'production',
        version: '1.0.0',
        metrics: {} as MetricsSnapshot,
        isDefault: true,
        tags: [],
        metadata: {},
        created: new Date(),
        updated: new Date()
      },
      {
        id: 'baseline-2',
        name: 'baseline-2',
        branch: 'main',
        commit: 'def456',
        environment: 'production',
        version: '1.1.0',
        metrics: {} as MetricsSnapshot,
        isDefault: false,
        tags: [],
        metadata: {},
        created: new Date(),
        updated: new Date()
      }
    ];

    beforeEach(() => {
      MockedFileUtils.fileExists.mockResolvedValue(true);
      MockedFileUtils.readJsonFile
        .mockResolvedValue(mockBaselines[1]) // For loadBaseline
        .mockResolvedValue([mockBaselines[0], mockBaselines[1]]); // For listBaselines
      MockedFileUtils.writeJsonFile.mockResolvedValue();
      MockedFileUtils.listFiles.mockResolvedValue([
        'baseline-1.baseline.json',
        'baseline-2.baseline.json'
      ]);
    });

    it('should set baseline as default and clear others', async () => {
      await baselineManager.setAsDefault('baseline-2');

      // Should be called to update both baselines
      expect(MockedFileUtils.writeJsonFile).toHaveBeenCalledTimes(2);
    });
  });

  describe('deleteBaseline', () => {
    it('should delete existing baseline', async () => {
      MockedFileUtils.fileExists.mockResolvedValue(true);
      MockedFileUtils.createBackup.mockResolvedValue('backup-path');
      MockedFileUtils.deleteFile.mockResolvedValue();

      await baselineManager.deleteBaseline('baseline-1');

      expect(MockedFileUtils.createBackup).toHaveBeenCalled();
      expect(MockedFileUtils.deleteFile).toHaveBeenCalledWith(
        path.join(tempDir, 'baseline-1.baseline.json')
      );
    });

    it('should throw error for non-existent baseline', async () => {
      MockedFileUtils.fileExists.mockResolvedValue(false);

      await expect(
        baselineManager.deleteBaseline('non-existent')
      ).rejects.toThrow('Baseline not found: non-existent');
    });
  });

  describe('error handling', () => {
    it('should handle file system errors gracefully', async () => {
      MockedFileUtils.fileExists.mockRejectedValue(new Error('File system error'));

      await expect(
        baselineManager.loadBaseline('baseline-1')
      ).rejects.toThrow('File system error');
    });

    it('should handle invalid JSON data', async () => {
      MockedFileUtils.fileExists.mockResolvedValue(true);
      MockedFileUtils.readJsonFile.mockRejectedValue(new Error('Invalid JSON'));

      await expect(
        baselineManager.loadBaseline('baseline-1')
      ).rejects.toThrow();
    });
  });
});