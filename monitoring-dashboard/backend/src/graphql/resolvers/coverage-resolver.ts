import { Resolver, Query, Mutation, Arg, Float } from 'type-graphql';
import { Coverage, CoverageInput, CoverageSummary } from '../types';
import { logger } from '../../utils/logger';

@Resolver(() => Coverage)
export class CoverageResolver {
  private coverage: Map<string, Coverage> = new Map();

  @Query(() => [Coverage])
  async coverage(
    @Arg('file', { nullable: true }) file?: string,
    @Arg('threshold', () => Float, { nullable: true }) threshold?: number
  ): Promise<Coverage[]> {
    try {
      let coverageData = Array.from(this.coverage.values());

      // Apply filters
      if (file) {
        const searchTerm = file.toLowerCase();
        coverageData = coverageData.filter(cov =>
          cov.file.toLowerCase().includes(searchTerm)
        );
      }

      if (threshold !== undefined) {
        coverageData = coverageData.filter(cov =>
          cov.lines.percentage >= threshold
        );
      }

      // Sort by coverage percentage (highest first)
      coverageData.sort((a, b) => b.lines.percentage - a.lines.percentage);

      return coverageData;

    } catch (error) {
      logger.error('Error in coverage resolver:', error);
      throw new Error('Failed to retrieve coverage data');
    }
  }

  @Query(() => Coverage, { nullable: true })
  async fileCoverage(@Arg('file') file: string): Promise<Coverage | null> {
    try {
      return this.coverage.get(file) || null;
    } catch (error) {
      logger.error('Error in fileCoverage resolver:', error);
      throw new Error('Failed to retrieve file coverage');
    }
  }

  @Query(() => CoverageSummary)
  async coverageSummary(): Promise<CoverageSummary> {
    try {
      const coverageData = Array.from(this.coverage.values());

      if (coverageData.length === 0) {
        return {
          overall: 0,
          lines: 0,
          functions: 0,
          branches: 0,
          statements: 0,
          totalFiles: 0
        };
      }

      // Calculate overall coverage
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

      const linesPercentage = totals.lines.total > 0 ? (totals.lines.covered / totals.lines.total) * 100 : 0;
      const functionsPercentage = totals.functions.total > 0 ? (totals.functions.covered / totals.functions.total) * 100 : 0;
      const branchesPercentage = totals.branches.total > 0 ? (totals.branches.covered / totals.branches.total) * 100 : 0;
      const statementsPercentage = totals.statements.total > 0 ? (totals.statements.covered / totals.statements.total) * 100 : 0;

      // Overall is average of all metrics
      const overall = (linesPercentage + functionsPercentage + branchesPercentage + statementsPercentage) / 4;

      return {
        overall: Math.round(overall * 100) / 100,
        lines: Math.round(linesPercentage * 100) / 100,
        functions: Math.round(functionsPercentage * 100) / 100,
        branches: Math.round(branchesPercentage * 100) / 100,
        statements: Math.round(statementsPercentage * 100) / 100,
        totalFiles: coverageData.length
      };

    } catch (error) {
      logger.error('Error in coverageSummary resolver:', error);
      throw new Error('Failed to calculate coverage summary');
    }
  }

  @Mutation(() => [Coverage])
  async uploadCoverage(@Arg('input', () => [CoverageInput]) input: CoverageInput[]): Promise<Coverage[]> {
    try {
      const uploadedCoverage: Coverage[] = [];

      for (const coverageInput of input) {
        const coverage: Coverage = {
          file: coverageInput.file,
          lines: {
            total: coverageInput.lines.total,
            covered: coverageInput.lines.covered,
            percentage: coverageInput.lines.percentage
          },
          functions: {
            total: coverageInput.functions.total,
            covered: coverageInput.functions.covered,
            percentage: coverageInput.functions.percentage
          },
          branches: {
            total: coverageInput.branches.total,
            covered: coverageInput.branches.covered,
            percentage: coverageInput.branches.percentage
          },
          statements: {
            total: coverageInput.statements.total,
            covered: coverageInput.statements.covered,
            percentage: coverageInput.statements.percentage
          },
          uncoveredLines: coverageInput.uncoveredLines
        };

        this.coverage.set(coverage.file, coverage);
        uploadedCoverage.push(coverage);
      }

      logger.info(`Coverage data uploaded for ${uploadedCoverage.length} files`);
      return uploadedCoverage;

    } catch (error) {
      logger.error('Error in uploadCoverage mutation:', error);
      throw new Error('Failed to upload coverage data');
    }
  }

  @Mutation(() => Boolean)
  async deleteCoverage(@Arg('file') file: string): Promise<boolean> {
    try {
      const deleted = this.coverage.delete(file);

      if (deleted) {
        logger.info(`Coverage data deleted for file: ${file}`);
      }

      return deleted;

    } catch (error) {
      logger.error('Error in deleteCoverage mutation:', error);
      throw new Error('Failed to delete coverage data');
    }
  }

  // Add some mock data for demonstration
  constructor() {
    this.addMockData();
  }

  private addMockData(): void {
    const mockCoverage: Coverage[] = [
      {
        file: 'src/components/Dashboard.tsx',
        lines: { total: 150, covered: 135, percentage: 90.0 },
        functions: { total: 12, covered: 11, percentage: 91.7 },
        branches: { total: 24, covered: 20, percentage: 83.3 },
        statements: { total: 145, covered: 132, percentage: 91.0 },
        uncoveredLines: [45, 67, 89, 123]
      },
      {
        file: 'src/services/api.ts',
        lines: { total: 200, covered: 180, percentage: 90.0 },
        functions: { total: 15, covered: 14, percentage: 93.3 },
        branches: { total: 30, covered: 26, percentage: 86.7 },
        statements: { total: 195, covered: 178, percentage: 91.3 },
        uncoveredLines: [78, 125, 134, 189, 195]
      },
      {
        file: 'src/utils/helpers.ts',
        lines: { total: 80, covered: 65, percentage: 81.3 },
        functions: { total: 8, covered: 7, percentage: 87.5 },
        branches: { total: 16, covered: 12, percentage: 75.0 },
        statements: { total: 75, covered: 62, percentage: 82.7 },
        uncoveredLines: [23, 34, 45, 56, 67, 78]
      },
      {
        file: 'src/components/Chart.tsx',
        lines: { total: 120, covered: 108, percentage: 90.0 },
        functions: { total: 10, covered: 9, percentage: 90.0 },
        branches: { total: 20, covered: 18, percentage: 90.0 },
        statements: { total: 115, covered: 105, percentage: 91.3 },
        uncoveredLines: [45, 78, 89]
      },
      {
        file: 'src/hooks/useWebSocket.ts',
        lines: { total: 60, covered: 42, percentage: 70.0 },
        functions: { total: 5, covered: 4, percentage: 80.0 },
        branches: { total: 12, covered: 8, percentage: 66.7 },
        statements: { total: 58, covered: 40, percentage: 69.0 },
        uncoveredLines: [12, 23, 34, 45, 56, 67, 78, 89, 90, 91]
      }
    ];

    mockCoverage.forEach(coverage => {
      this.coverage.set(coverage.file, coverage);
    });

    logger.info(`Added mock coverage data for ${mockCoverage.length} files`);
  }
}