import { Request, Response } from 'express';
import { CoverageData, CoverageDataSchema, ApiResponse } from '@monitoring-dashboard/shared';
import { cacheService } from '../../cache/redis-cache';
import { logger, performanceLogger } from '../../utils/logger';

export class CoverageController {
  private readonly CACHE_TTL = 600; // 10 minutes
  private coverage: Map<string, CoverageData> = new Map();
  private coverageHistory: Array<{ timestamp: string; data: CoverageData[] }> = [];

  // Get coverage data with optional filtering
  public async getCoverage(req: Request, res: Response): Promise<void> {
    const perf = performanceLogger.start('getCoverage');

    try {
      const { file, threshold, sortBy = 'percentage' } = req.query;
      const cacheKey = `coverage:${JSON.stringify(req.query)}`;

      const cached = await cacheService.get<CoverageData[]>(cacheKey);
      if (cached) {
        perf.end();
        res.json({
          success: true,
          data: cached,
          timestamp: new Date().toISOString()
        } as ApiResponse);
        return;
      }

      let coverageData = Array.from(this.coverage.values());

      // Apply filters
      if (file) {
        const searchTerm = (file as string).toLowerCase();
        coverageData = coverageData.filter(cov =>
          cov.file.toLowerCase().includes(searchTerm)
        );
      }

      if (threshold) {
        const thresholdValue = Number(threshold);
        coverageData = coverageData.filter(cov =>
          cov.lines.percentage >= thresholdValue
        );
      }

      // Sort data
      if (sortBy === 'percentage') {
        coverageData.sort((a, b) => b.lines.percentage - a.lines.percentage);
      } else if (sortBy === 'file') {
        coverageData.sort((a, b) => a.file.localeCompare(b.file));
      } else if (sortBy === 'lines') {
        coverageData.sort((a, b) => b.lines.total - a.lines.total);
      }

      // Cache results
      await cacheService.set(cacheKey, coverageData, this.CACHE_TTL);

      perf.end();

      res.json({
        success: true,
        data: coverageData,
        timestamp: new Date().toISOString()
      } as ApiResponse);

    } catch (error) {
      perf.end();
      logger.error('Error in getCoverage:', error);
      res.status(500).json({
        success: false,
        error: 'Failed to retrieve coverage data',
        timestamp: new Date().toISOString()
      } as ApiResponse);
    }
  }

  // Upload new coverage data
  public async uploadCoverage(req: Request, res: Response): Promise<void> {
    try {
      const coverageDataArray = Array.isArray(req.body) ? req.body : [req.body];
      const validatedCoverage: CoverageData[] = [];

      for (const coverage of coverageDataArray) {
        const validatedData = CoverageDataSchema.parse(coverage);
        validatedCoverage.push(validatedData);
        this.coverage.set(validatedData.file, validatedData);
      }

      // Store in history
      this.coverageHistory.push({
        timestamp: new Date().toISOString(),
        data: validatedCoverage
      });

      // Keep only last 100 history entries
      if (this.coverageHistory.length > 100) {
        this.coverageHistory = this.coverageHistory.slice(-100);
      }

      // Invalidate cache
      await this.invalidateCoverageCache();

      logger.info(`Coverage data uploaded for ${validatedCoverage.length} files`);

      res.status(201).json({
        success: true,
        data: {
          filesProcessed: validatedCoverage.length,
          overall: this.calculateOverallCoverage()
        },
        timestamp: new Date().toISOString()
      } as ApiResponse);

    } catch (error) {
      logger.error('Error in uploadCoverage:', error);
      res.status(400).json({
        success: false,
        error: 'Invalid coverage data',
        timestamp: new Date().toISOString()
      } as ApiResponse);
    }
  }

  // Get coverage summary
  public async getCoverageSummary(req: Request, res: Response): Promise<void> {
    try {
      const cacheKey = 'coverage:summary';
      let summary = await cacheService.get<any>(cacheKey);

      if (!summary) {
        const overallCoverage = this.calculateOverallCoverage();
        const totalFiles = this.coverage.size;
        const filesCovered = Array.from(this.coverage.values()).filter(cov => cov.lines.percentage > 0).length;
        const filesFullyCovered = Array.from(this.coverage.values()).filter(cov => cov.lines.percentage === 100).length;

        // Coverage distribution
        const distribution = {
          excellent: 0, // >= 90%
          good: 0,      // 80-89%
          fair: 0,      // 70-79%
          poor: 0       // < 70%
        };

        Array.from(this.coverage.values()).forEach(cov => {
          const percentage = cov.lines.percentage;
          if (percentage >= 90) distribution.excellent++;
          else if (percentage >= 80) distribution.good++;
          else if (percentage >= 70) distribution.fair++;
          else distribution.poor++;
        });

        summary = {
          overall: overallCoverage,
          totalFiles,
          filesCovered,
          filesFullyCovered,
          distribution,
          averagePercentage: totalFiles > 0 ?
            Array.from(this.coverage.values()).reduce((sum, cov) => sum + cov.lines.percentage, 0) / totalFiles : 0
        };

        await cacheService.set(cacheKey, summary, this.CACHE_TTL);
      }

      res.json({
        success: true,
        data: summary,
        timestamp: new Date().toISOString()
      } as ApiResponse);

    } catch (error) {
      logger.error('Error in getCoverageSummary:', error);
      res.status(500).json({
        success: false,
        error: 'Failed to retrieve coverage summary',
        timestamp: new Date().toISOString()
      } as ApiResponse);
    }
  }

  // Get coverage for a specific file
  public async getFileCoverage(req: Request, res: Response): Promise<void> {
    try {
      const { file } = req.params;
      const decodedFile = decodeURIComponent(file);

      const coverageData = this.coverage.get(decodedFile);

      if (!coverageData) {
        res.status(404).json({
          success: false,
          error: 'Coverage data not found for file',
          timestamp: new Date().toISOString()
        } as ApiResponse);
        return;
      }

      res.json({
        success: true,
        data: coverageData,
        timestamp: new Date().toISOString()
      } as ApiResponse);

    } catch (error) {
      logger.error('Error in getFileCoverage:', error);
      res.status(500).json({
        success: false,
        error: 'Failed to retrieve file coverage',
        timestamp: new Date().toISOString()
      } as ApiResponse);
    }
  }

  // Get coverage trends
  public async getCoverageTrends(req: Request, res: Response): Promise<void> {
    try {
      const { period = 'day', limit = 30 } = req.query;
      const cacheKey = `coverage:trends:${period}:${limit}`;

      let trends = await cacheService.get<any>(cacheKey);

      if (!trends) {
        const limitNum = Number(limit);
        const recentHistory = this.coverageHistory.slice(-limitNum);

        trends = recentHistory.map(entry => ({
          timestamp: entry.timestamp,
          overall: this.calculateOverallCoverageForData(entry.data),
          totalFiles: entry.data.length,
          averagePercentage: entry.data.length > 0 ?
            entry.data.reduce((sum, cov) => sum + cov.lines.percentage, 0) / entry.data.length : 0
        }));

        await cacheService.set(cacheKey, trends, this.CACHE_TTL);
      }

      res.json({
        success: true,
        data: trends,
        timestamp: new Date().toISOString()
      } as ApiResponse);

    } catch (error) {
      logger.error('Error in getCoverageTrends:', error);
      res.status(500).json({
        success: false,
        error: 'Failed to retrieve coverage trends',
        timestamp: new Date().toISOString()
      } as ApiResponse);
    }
  }

  // Calculate overall coverage from current data
  private calculateOverallCoverage(): CoverageData {
    return this.calculateOverallCoverageForData(Array.from(this.coverage.values()));
  }

  // Calculate overall coverage from specific data
  private calculateOverallCoverageForData(coverageData: CoverageData[]): CoverageData {
    if (coverageData.length === 0) {
      return {
        file: 'overall',
        lines: { total: 0, covered: 0, percentage: 0 },
        functions: { total: 0, covered: 0, percentage: 0 },
        branches: { total: 0, covered: 0, percentage: 0 },
        statements: { total: 0, covered: 0, percentage: 0 },
        uncoveredLines: []
      };
    }

    const totals = coverageData.reduce(
      (acc, coverage) => ({
        lines: {
          total: acc.lines.total + coverage.lines.total,
          covered: acc.lines.covered + coverage.lines.covered
        },
        functions: {
          total: acc.functions.total + coverage.functions.total,
          covered: acc.functions.covered + coverage.functions.covered
        },
        branches: {
          total: acc.branches.total + coverage.branches.total,
          covered: acc.branches.covered + coverage.branches.covered
        },
        statements: {
          total: acc.statements.total + coverage.statements.total,
          covered: acc.statements.covered + coverage.statements.covered
        }
      }),
      {
        lines: { total: 0, covered: 0 },
        functions: { total: 0, covered: 0 },
        branches: { total: 0, covered: 0 },
        statements: { total: 0, covered: 0 }
      }
    );

    return {
      file: 'overall',
      lines: {
        ...totals.lines,
        percentage: totals.lines.total > 0 ? (totals.lines.covered / totals.lines.total) * 100 : 0
      },
      functions: {
        ...totals.functions,
        percentage: totals.functions.total > 0 ? (totals.functions.covered / totals.functions.total) * 100 : 0
      },
      branches: {
        ...totals.branches,
        percentage: totals.branches.total > 0 ? (totals.branches.covered / totals.branches.total) * 100 : 0
      },
      statements: {
        ...totals.statements,
        percentage: totals.statements.total > 0 ? (totals.statements.covered / totals.statements.total) * 100 : 0
      },
      uncoveredLines: []
    };
  }

  // Utility method to invalidate coverage-related cache
  private async invalidateCoverageCache(): Promise<void> {
    try {
      const cacheKeys = await cacheService.keys('coverage:*');
      for (const key of cacheKeys) {
        await cacheService.del(key);
      }
    } catch (error) {
      logger.error('Error invalidating coverage cache:', error);
    }
  }
}