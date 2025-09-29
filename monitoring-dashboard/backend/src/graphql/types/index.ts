import { ObjectType, Field, ID, Int, Float, registerEnumType } from 'type-graphql';

// Enums
export enum TestStatus {
  PENDING = 'pending',
  RUNNING = 'running',
  PASSED = 'passed',
  FAILED = 'failed',
  SKIPPED = 'skipped'
}

export enum AlertSeverity {
  LOW = 'low',
  MEDIUM = 'medium',
  HIGH = 'high',
  CRITICAL = 'critical'
}

export enum AlertType {
  REGRESSION = 'regression',
  COVERAGE_DROP = 'coverage_drop',
  PERFORMANCE_DEGRADATION = 'performance_degradation',
  FLAKY_TEST = 'flaky_test',
  ANOMALY = 'anomaly'
}

export enum MetricType {
  DURATION = 'duration',
  MEMORY = 'memory',
  CPU = 'cpu',
  THROUGHPUT = 'throughput'
}

// Register enums with TypeGraphQL
registerEnumType(TestStatus, { name: 'TestStatus' });
registerEnumType(AlertSeverity, { name: 'AlertSeverity' });
registerEnumType(AlertType, { name: 'AlertType' });
registerEnumType(MetricType, { name: 'MetricType' });

// Base types
@ObjectType()
export class Test {
  @Field(() => ID)
  id!: string;

  @Field()
  name!: string;

  @Field()
  suite!: string;

  @Field(() => TestStatus)
  status!: TestStatus;

  @Field(() => Float)
  duration!: number;

  @Field()
  startTime!: Date;

  @Field({ nullable: true })
  endTime?: Date;

  @Field({ nullable: true })
  error?: string;

  @Field({ nullable: true })
  stackTrace?: string;

  @Field(() => [String])
  tags!: string[];
}

@ObjectType()
export class CoverageMetric {
  @Field(() => Int)
  total!: number;

  @Field(() => Int)
  covered!: number;

  @Field(() => Float)
  percentage!: number;
}

@ObjectType()
export class Coverage {
  @Field()
  file!: string;

  @Field(() => CoverageMetric)
  lines!: CoverageMetric;

  @Field(() => CoverageMetric)
  functions!: CoverageMetric;

  @Field(() => CoverageMetric)
  branches!: CoverageMetric;

  @Field(() => CoverageMetric)
  statements!: CoverageMetric;

  @Field(() => [Int])
  uncoveredLines!: number[];
}

@ObjectType()
export class PerformanceMetric {
  @Field(() => ID)
  id!: string;

  @Field()
  timestamp!: Date;

  @Field()
  testSuite!: string;

  @Field(() => MetricType)
  metric!: MetricType;

  @Field(() => Float)
  value!: number;

  @Field()
  unit!: string;
}

@ObjectType()
export class Alert {
  @Field(() => ID)
  id!: string;

  @Field(() => AlertType)
  type!: AlertType;

  @Field(() => AlertSeverity)
  severity!: AlertSeverity;

  @Field()
  title!: string;

  @Field()
  description!: string;

  @Field()
  timestamp!: Date;

  @Field()
  resolved!: boolean;

  @Field({ nullable: true })
  resolvedAt?: Date;
}

// Dashboard types
@ObjectType()
export class TestSummary {
  @Field(() => Int)
  total!: number;

  @Field(() => Int)
  passed!: number;

  @Field(() => Int)
  failed!: number;

  @Field(() => Int)
  skipped!: number;

  @Field(() => Float)
  passRate!: number;

  @Field(() => Float)
  avgDuration!: number;
}

@ObjectType()
export class CoverageSummary {
  @Field(() => Float)
  overall!: number;

  @Field(() => Float)
  lines!: number;

  @Field(() => Float)
  functions!: number;

  @Field(() => Float)
  branches!: number;

  @Field(() => Float)
  statements!: number;

  @Field(() => Int)
  totalFiles!: number;
}

@ObjectType()
export class PerformanceSummary {
  @Field(() => Float)
  avgResponseTime!: number;

  @Field(() => Float)
  p95ResponseTime!: number;

  @Field(() => Float)
  throughput!: number;

  @Field(() => Float)
  errorRate!: number;
}

@ObjectType()
export class AlertSummary {
  @Field(() => Int)
  total!: number;

  @Field(() => Int)
  critical!: number;

  @Field(() => Int)
  high!: number;

  @Field(() => Int)
  medium!: number;

  @Field(() => Int)
  low!: number;

  @Field(() => Int)
  resolved!: number;

  @Field(() => Int)
  unresolved!: number;
}

@ObjectType()
export class DashboardSummary {
  @Field(() => TestSummary)
  tests!: TestSummary;

  @Field(() => CoverageSummary)
  coverage!: CoverageSummary;

  @Field(() => PerformanceSummary)
  performance!: PerformanceSummary;

  @Field(() => AlertSummary)
  alerts!: AlertSummary;
}

// Trend analysis types
@ObjectType()
export class TrendDataPoint {
  @Field()
  timestamp!: Date;

  @Field(() => Float)
  value!: number;
}

@ObjectType()
export class TrendData {
  @Field()
  metric!: string;

  @Field()
  period!: string;

  @Field(() => [TrendDataPoint])
  data!: TrendDataPoint[];
}

// Pagination types
@ObjectType()
export class PageInfo {
  @Field(() => Int)
  page!: number;

  @Field(() => Int)
  limit!: number;

  @Field(() => Int)
  total!: number;

  @Field(() => Int)
  totalPages!: number;

  @Field()
  hasNextPage!: boolean;

  @Field()
  hasPrevPage!: boolean;
}

@ObjectType()
export class TestConnection {
  @Field(() => [Test])
  nodes!: Test[];

  @Field(() => PageInfo)
  pageInfo!: PageInfo;
}

@ObjectType()
export class AlertConnection {
  @Field(() => [Alert])
  nodes!: Alert[];

  @Field(() => PageInfo)
  pageInfo!: PageInfo;
}

// Input types for mutations
import { InputType } from 'type-graphql';

@InputType()
export class TestInput {
  @Field()
  name!: string;

  @Field()
  suite!: string;

  @Field(() => TestStatus)
  status!: TestStatus;

  @Field(() => Float)
  duration!: number;

  @Field({ nullable: true })
  error?: string;

  @Field(() => [String], { defaultValue: [] })
  tags!: string[];
}

@InputType()
export class CoverageInput {
  @Field()
  file!: string;

  @Field(() => CoverageMetricInput)
  lines!: CoverageMetricInput;

  @Field(() => CoverageMetricInput)
  functions!: CoverageMetricInput;

  @Field(() => CoverageMetricInput)
  branches!: CoverageMetricInput;

  @Field(() => CoverageMetricInput)
  statements!: CoverageMetricInput;

  @Field(() => [Int], { defaultValue: [] })
  uncoveredLines!: number[];
}

@InputType()
export class CoverageMetricInput {
  @Field(() => Int)
  total!: number;

  @Field(() => Int)
  covered!: number;

  @Field(() => Float)
  percentage!: number;
}

@InputType()
export class MetricInput {
  @Field()
  testSuite!: string;

  @Field(() => MetricType)
  metric!: MetricType;

  @Field(() => Float)
  value!: number;

  @Field()
  unit!: string;
}

@InputType()
export class AlertInput {
  @Field(() => AlertType)
  type!: AlertType;

  @Field(() => AlertSeverity)
  severity!: AlertSeverity;

  @Field()
  title!: string;

  @Field()
  description!: string;
}

// Filter input types
@InputType()
export class TestFilter {
  @Field({ nullable: true })
  suite?: string;

  @Field(() => TestStatus, { nullable: true })
  status?: TestStatus;

  @Field({ nullable: true })
  startDate?: Date;

  @Field({ nullable: true })
  endDate?: Date;

  @Field({ nullable: true })
  search?: string;
}

@InputType()
export class AlertFilter {
  @Field(() => AlertSeverity, { nullable: true })
  severity?: AlertSeverity;

  @Field(() => AlertType, { nullable: true })
  type?: AlertType;

  @Field({ nullable: true })
  resolved?: boolean;

  @Field({ nullable: true })
  startDate?: Date;

  @Field({ nullable: true })
  endDate?: Date;
}