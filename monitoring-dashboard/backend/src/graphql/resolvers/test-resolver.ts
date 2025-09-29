import { Resolver, Query, Mutation, Arg, Int, ID } from 'type-graphql';
import { Test, TestInput, TestFilter, TestConnection, PageInfo } from '../types';
import { TestStatus } from '../types';
import { logger } from '../../utils/logger';
import { v4 as uuidv4 } from 'uuid';

@Resolver(() => Test)
export class TestResolver {
  private tests: Map<string, Test> = new Map();

  @Query(() => TestConnection)
  async tests(
    @Arg('filter', () => TestFilter, { nullable: true }) filter?: TestFilter,
    @Arg('page', () => Int, { defaultValue: 1 }) page: number = 1,
    @Arg('limit', () => Int, { defaultValue: 50 }) limit: number = 50
  ): Promise<TestConnection> {
    try {
      let filteredTests = Array.from(this.tests.values());

      // Apply filters
      if (filter) {
        if (filter.suite) {
          filteredTests = filteredTests.filter(test =>
            test.suite.toLowerCase().includes(filter.suite!.toLowerCase())
          );
        }

        if (filter.status) {
          filteredTests = filteredTests.filter(test => test.status === filter.status);
        }

        if (filter.search) {
          const searchTerm = filter.search.toLowerCase();
          filteredTests = filteredTests.filter(test =>
            test.name.toLowerCase().includes(searchTerm) ||
            test.suite.toLowerCase().includes(searchTerm)
          );
        }

        if (filter.startDate || filter.endDate) {
          filteredTests = filteredTests.filter(test => {
            const testDate = test.startTime;
            const start = filter.startDate || new Date(0);
            const end = filter.endDate || new Date();
            return testDate >= start && testDate <= end;
          });
        }
      }

      // Sort by start time (newest first)
      filteredTests.sort((a, b) => b.startTime.getTime() - a.startTime.getTime());

      // Pagination
      const total = filteredTests.length;
      const totalPages = Math.ceil(total / limit);
      const startIndex = (page - 1) * limit;
      const paginatedTests = filteredTests.slice(startIndex, startIndex + limit);

      const pageInfo: PageInfo = {
        page,
        limit,
        total,
        totalPages,
        hasNextPage: page < totalPages,
        hasPrevPage: page > 1
      };

      return {
        nodes: paginatedTests,
        pageInfo
      };

    } catch (error) {
      logger.error('Error in tests resolver:', error);
      throw new Error('Failed to retrieve tests');
    }
  }

  @Query(() => Test, { nullable: true })
  async test(@Arg('id', () => ID) id: string): Promise<Test | null> {
    try {
      return this.tests.get(id) || null;
    } catch (error) {
      logger.error('Error in test resolver:', error);
      throw new Error('Failed to retrieve test');
    }
  }

  @Query(() => [Test])
  async testsBySuite(@Arg('suite') suite: string): Promise<Test[]> {
    try {
      return Array.from(this.tests.values()).filter(test => test.suite === suite);
    } catch (error) {
      logger.error('Error in testsBySuite resolver:', error);
      throw new Error('Failed to retrieve tests by suite');
    }
  }

  @Query(() => [Test])
  async testsByStatus(@Arg('status', () => TestStatus) status: TestStatus): Promise<Test[]> {
    try {
      return Array.from(this.tests.values()).filter(test => test.status === status);
    } catch (error) {
      logger.error('Error in testsByStatus resolver:', error);
      throw new Error('Failed to retrieve tests by status');
    }
  }

  @Mutation(() => Test)
  async createTest(@Arg('input') input: TestInput): Promise<Test> {
    try {
      const test: Test = {
        id: uuidv4(),
        name: input.name,
        suite: input.suite,
        status: input.status,
        duration: input.duration,
        startTime: new Date(),
        endTime: input.status !== TestStatus.RUNNING ? new Date() : undefined,
        error: input.error,
        stackTrace: undefined,
        tags: input.tags
      };

      this.tests.set(test.id, test);

      logger.info(`Test created: ${test.id}`);
      return test;

    } catch (error) {
      logger.error('Error in createTest mutation:', error);
      throw new Error('Failed to create test');
    }
  }

  @Mutation(() => Test)
  async updateTest(
    @Arg('id', () => ID) id: string,
    @Arg('input') input: Partial<TestInput>
  ): Promise<Test> {
    try {
      const existingTest = this.tests.get(id);

      if (!existingTest) {
        throw new Error('Test not found');
      }

      const updatedTest: Test = {
        ...existingTest,
        ...input,
        id,
        endTime: input.status && input.status !== TestStatus.RUNNING
          ? new Date()
          : existingTest.endTime
      };

      this.tests.set(id, updatedTest);

      logger.info(`Test updated: ${id}`);
      return updatedTest;

    } catch (error) {
      logger.error('Error in updateTest mutation:', error);
      throw new Error('Failed to update test');
    }
  }

  @Mutation(() => Boolean)
  async deleteTest(@Arg('id', () => ID) id: string): Promise<boolean> {
    try {
      const deleted = this.tests.delete(id);

      if (deleted) {
        logger.info(`Test deleted: ${id}`);
      }

      return deleted;

    } catch (error) {
      logger.error('Error in deleteTest mutation:', error);
      throw new Error('Failed to delete test');
    }
  }

  // Utility resolvers for aggregated data
  @Query(() => Int)
  async testCount(
    @Arg('filter', () => TestFilter, { nullable: true }) filter?: TestFilter
  ): Promise<number> {
    try {
      let filteredTests = Array.from(this.tests.values());

      if (filter) {
        // Apply same filtering logic as in tests resolver
        // (Implementation omitted for brevity - would be same as above)
      }

      return filteredTests.length;

    } catch (error) {
      logger.error('Error in testCount resolver:', error);
      throw new Error('Failed to get test count');
    }
  }

  // Add some mock data for demonstration
  constructor() {
    this.addMockData();
  }

  private addMockData(): void {
    const mockTests: Test[] = [
      {
        id: '1',
        name: 'User Authentication Test',
        suite: 'Authentication',
        status: TestStatus.PASSED,
        duration: 1200,
        startTime: new Date(Date.now() - 1000 * 60 * 5),
        endTime: new Date(Date.now() - 1000 * 60 * 4),
        tags: ['auth', 'integration']
      },
      {
        id: '2',
        name: 'Password Reset Flow',
        suite: 'Authentication',
        status: TestStatus.FAILED,
        duration: 800,
        startTime: new Date(Date.now() - 1000 * 60 * 10),
        endTime: new Date(Date.now() - 1000 * 60 * 9),
        error: 'Email service unavailable',
        tags: ['auth', 'email']
      },
      {
        id: '3',
        name: 'API Response Validation',
        suite: 'API',
        status: TestStatus.PASSED,
        duration: 450,
        startTime: new Date(Date.now() - 1000 * 60 * 15),
        endTime: new Date(Date.now() - 1000 * 60 * 14),
        tags: ['api', 'validation']
      },
      {
        id: '4',
        name: 'Database Connection Pool',
        suite: 'Database',
        status: TestStatus.RUNNING,
        duration: 0,
        startTime: new Date(Date.now() - 1000 * 30),
        tags: ['database', 'performance']
      },
      {
        id: '5',
        name: 'UI Component Rendering',
        suite: 'Frontend',
        status: TestStatus.SKIPPED,
        duration: 0,
        startTime: new Date(Date.now() - 1000 * 60 * 20),
        tags: ['ui', 'component']
      }
    ];

    mockTests.forEach(test => {
      this.tests.set(test.id, test);
    });

    logger.info(`Added ${mockTests.length} mock tests`);
  }
}