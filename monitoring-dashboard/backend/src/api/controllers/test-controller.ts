import { Request, Response } from 'express';
import { TestResult, TestResultSchema, ApiResponse } from '@monitoring-dashboard/shared';
import { cacheService } from '../../cache/redis-cache';
import { logger, performanceLogger } from '../../utils/logger';
import { v4 as uuidv4 } from 'uuid';

export class TestController {
  private readonly CACHE_TTL = 300; // 5 minutes
  private tests: Map<string, TestResult> = new Map();

  // Get all tests with optional filtering
  public async getTests(req: Request, res: Response): Promise<void> {
    const perf = performanceLogger.start('getTests');

    try {
      const {
        suite,
        status,
        page = 1,
        limit = 50,
        startDate,
        endDate,
        search
      } = req.query;

      const cacheKey = `tests:${JSON.stringify(req.query)}`;
      const cached = await cacheService.get<TestResult[]>(cacheKey);

      if (cached) {
        perf.end();
        res.json({
          success: true,
          data: {
            tests: cached,
            total: cached.length,
            page: Number(page),
            limit: Number(limit)
          },
          timestamp: new Date().toISOString()
        } as ApiResponse);
        return;
      }

      let filteredTests = Array.from(this.tests.values());

      // Apply filters
      if (suite) {
        filteredTests = filteredTests.filter(test =>
          test.suite.toLowerCase().includes((suite as string).toLowerCase())
        );
      }

      if (status) {
        filteredTests = filteredTests.filter(test => test.status === status);
      }

      if (search) {
        const searchTerm = (search as string).toLowerCase();
        filteredTests = filteredTests.filter(test =>
          test.name.toLowerCase().includes(searchTerm) ||
          test.suite.toLowerCase().includes(searchTerm)
        );
      }

      if (startDate || endDate) {
        filteredTests = filteredTests.filter(test => {
          const testDate = new Date(test.startTime);
          const start = startDate ? new Date(startDate as string) : new Date(0);
          const end = endDate ? new Date(endDate as string) : new Date();
          return testDate >= start && testDate <= end;
        });
      }

      // Sort by start time (newest first)
      filteredTests.sort((a, b) =>
        new Date(b.startTime).getTime() - new Date(a.startTime).getTime()
      );

      // Pagination
      const startIndex = (Number(page) - 1) * Number(limit);
      const paginatedTests = filteredTests.slice(startIndex, startIndex + Number(limit));

      // Cache results
      await cacheService.set(cacheKey, paginatedTests, this.CACHE_TTL);

      perf.end();

      res.json({
        success: true,
        data: {
          tests: paginatedTests,
          total: filteredTests.length,
          page: Number(page),
          limit: Number(limit)
        },
        timestamp: new Date().toISOString()
      } as ApiResponse);

    } catch (error) {
      perf.end();
      logger.error('Error in getTests:', error);
      res.status(500).json({
        success: false,
        error: 'Failed to retrieve tests',
        timestamp: new Date().toISOString()
      } as ApiResponse);
    }
  }

  // Create a new test
  public async createTest(req: Request, res: Response): Promise<void> {
    try {
      const testData = TestResultSchema.parse({
        ...req.body,
        id: req.body.id || uuidv4(),
        startTime: req.body.startTime || new Date().toISOString()
      });

      this.tests.set(testData.id, testData);

      // Invalidate cache
      await this.invalidateTestCache();

      logger.info(`Test created: ${testData.id}`);

      res.status(201).json({
        success: true,
        data: testData,
        timestamp: new Date().toISOString()
      } as ApiResponse);

    } catch (error) {
      logger.error('Error in createTest:', error);
      res.status(400).json({
        success: false,
        error: 'Invalid test data',
        timestamp: new Date().toISOString()
      } as ApiResponse);
    }
  }

  // Get a specific test
  public async getTest(req: Request, res: Response): Promise<void> {
    try {
      const { id } = req.params;
      const cacheKey = `test:${id}`;

      let test = await cacheService.get<TestResult>(cacheKey);

      if (!test) {
        test = this.tests.get(id);
        if (!test) {
          res.status(404).json({
            success: false,
            error: 'Test not found',
            timestamp: new Date().toISOString()
          } as ApiResponse);
          return;
        }

        await cacheService.set(cacheKey, test, this.CACHE_TTL);
      }

      res.json({
        success: true,
        data: test,
        timestamp: new Date().toISOString()
      } as ApiResponse);

    } catch (error) {
      logger.error('Error in getTest:', error);
      res.status(500).json({
        success: false,
        error: 'Failed to retrieve test',
        timestamp: new Date().toISOString()
      } as ApiResponse);
    }
  }

  // Update a test
  public async updateTest(req: Request, res: Response): Promise<void> {
    try {
      const { id } = req.params;
      const existingTest = this.tests.get(id);

      if (!existingTest) {
        res.status(404).json({
          success: false,
          error: 'Test not found',
          timestamp: new Date().toISOString()
        } as ApiResponse);
        return;
      }

      const updatedTest = TestResultSchema.parse({
        ...existingTest,
        ...req.body,
        id,
        endTime: req.body.endTime || (req.body.status !== 'running' ? new Date().toISOString() : undefined)
      });

      this.tests.set(id, updatedTest);

      // Invalidate cache
      await this.invalidateTestCache();
      await cacheService.del(`test:${id}`);

      logger.info(`Test updated: ${id}`);

      res.json({
        success: true,
        data: updatedTest,
        timestamp: new Date().toISOString()
      } as ApiResponse);

    } catch (error) {
      logger.error('Error in updateTest:', error);
      res.status(400).json({
        success: false,
        error: 'Invalid test data',
        timestamp: new Date().toISOString()
      } as ApiResponse);
    }
  }

  // Delete a test
  public async deleteTest(req: Request, res: Response): Promise<void> {
    try {
      const { id } = req.params;

      if (!this.tests.has(id)) {
        res.status(404).json({
          success: false,
          error: 'Test not found',
          timestamp: new Date().toISOString()
        } as ApiResponse);
        return;
      }

      this.tests.delete(id);

      // Invalidate cache
      await this.invalidateTestCache();
      await cacheService.del(`test:${id}`);

      logger.info(`Test deleted: ${id}`);

      res.json({
        success: true,
        data: { deleted: true },
        timestamp: new Date().toISOString()
      } as ApiResponse);

    } catch (error) {
      logger.error('Error in deleteTest:', error);
      res.status(500).json({
        success: false,
        error: 'Failed to delete test',
        timestamp: new Date().toISOString()
      } as ApiResponse);
    }
  }

  // Get tests by suite
  public async getTestsBySuite(req: Request, res: Response): Promise<void> {
    try {
      const { suite } = req.params;
      const tests = Array.from(this.tests.values()).filter(test => test.suite === suite);

      res.json({
        success: true,
        data: tests,
        timestamp: new Date().toISOString()
      } as ApiResponse);

    } catch (error) {
      logger.error('Error in getTestsBySuite:', error);
      res.status(500).json({
        success: false,
        error: 'Failed to retrieve tests by suite',
        timestamp: new Date().toISOString()
      } as ApiResponse);
    }
  }

  // Get tests by status
  public async getTestsByStatus(req: Request, res: Response): Promise<void> {
    try {
      const { status } = req.params;
      const tests = Array.from(this.tests.values()).filter(test => test.status === status);

      res.json({
        success: true,
        data: tests,
        timestamp: new Date().toISOString()
      } as ApiResponse);

    } catch (error) {
      logger.error('Error in getTestsByStatus:', error);
      res.status(500).json({
        success: false,
        error: 'Failed to retrieve tests by status',
        timestamp: new Date().toISOString()
      } as ApiResponse);
    }
  }

  // Utility method to invalidate test-related cache
  private async invalidateTestCache(): Promise<void> {
    try {
      const cacheKeys = await cacheService.keys('tests:*');
      for (const key of cacheKeys) {
        await cacheService.del(key);
      }
    } catch (error) {
      logger.error('Error invalidating test cache:', error);
    }
  }
}