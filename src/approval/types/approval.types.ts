/**
 * Core types for the approval workflow system
 */

export interface ApprovalRequest {
  id: string;
  title: string;
  description: string;
  type: ApprovalType;
  status: ApprovalStatus;
  priority: ApprovalPriority;
  requester: User;
  approvers: ApprovalStep[];
  currentStep: number;
  baselineUpdate?: BaselineUpdateRequest;
  metadata: Record<string, any>;
  createdAt: Date;
  updatedAt: Date;
  deadline?: Date;
  escalation?: EscalationRule;
  auditTrail: AuditEvent[];
}

export interface ApprovalStep {
  id: string;
  stepNumber: number;
  name: string;
  description?: string;
  approverType: ApproverType;
  approvers: User[];
  requiredApprovals: number;
  status: StepStatus;
  responses: ApprovalResponse[];
  timeout?: number; // minutes
  escalation?: EscalationRule;
  conditions?: ApprovalCondition[];
}

export interface ApprovalResponse {
  id: string;
  stepId: string;
  approver: User;
  decision: ApprovalDecision;
  reason?: string;
  comments?: string;
  timestamp: Date;
  ipAddress?: string;
  metadata?: Record<string, any>;
}

export interface BaselineUpdateRequest {
  id: string;
  targetEnvironment: Environment;
  updateType: UpdateType;
  changes: BaselineChange[];
  impactAssessment: ImpactAssessment;
  rollbackPlan: RollbackPlan;
  validationRules: ValidationRule[];
  deploymentConfig: DeploymentConfig;
}

export interface BaselineChange {
  id: string;
  type: ChangeType;
  component: string;
  before: any;
  after: any;
  risk: RiskLevel;
  testingRequired: boolean;
  dependencies: string[];
}

export interface ImpactAssessment {
  scope: string[];
  riskLevel: RiskLevel;
  affectedUsers: number;
  downtime: number; // minutes
  rollbackTime: number; // minutes
  testingRequired: TestingRequirement[];
  dependencies: string[];
  businessImpact: string;
}

export interface RollbackPlan {
  strategy: RollbackStrategy;
  steps: RollbackStep[];
  triggers: RollbackTrigger[];
  dataRecovery: DataRecoveryPlan;
  estimatedTime: number; // minutes
  validationChecks: string[];
}

export interface RollbackStep {
  id: string;
  order: number;
  description: string;
  command?: string;
  validation: string;
  timeout: number;
  rollbackOnFailure: boolean;
}

export interface ValidationRule {
  id: string;
  name: string;
  type: ValidationType;
  condition: string;
  errorMessage: string;
  severity: Severity;
  blocking: boolean;
}

export interface DeploymentConfig {
  environment: Environment;
  strategy: DeploymentStrategy;
  stages: DeploymentStage[];
  healthChecks: HealthCheck[];
  notifications: NotificationConfig[];
}

export interface User {
  id: string;
  username: string;
  email: string;
  fullName: string;
  role: UserRole;
  permissions: Permission[];
  isActive: boolean;
  timezone: string;
  notificationPreferences: NotificationPreference[];
}

export interface EscalationRule {
  id: string;
  trigger: EscalationTrigger;
  delay: number; // minutes
  action: EscalationAction;
  escalateTo: User[];
  maxEscalations: number;
  notificationTemplate: string;
}

export interface ApprovalCondition {
  id: string;
  type: ConditionType;
  field: string;
  operator: ComparisonOperator;
  value: any;
  logic: LogicOperator;
}

export interface AuditEvent {
  id: string;
  timestamp: Date;
  action: AuditAction;
  user: User;
  details: Record<string, any>;
  ipAddress?: string;
  userAgent?: string;
}

export interface NotificationConfig {
  id: string;
  type: NotificationType;
  channels: NotificationChannel[];
  recipients: User[];
  template: string;
  triggers: NotificationTrigger[];
  frequency: NotificationFrequency;
}

export interface ApprovalTemplate {
  id: string;
  name: string;
  description: string;
  category: TemplateCategory;
  steps: ApprovalStepTemplate[];
  defaultSettings: ApprovalSettings;
  conditions: ApprovalCondition[];
  isActive: boolean;
  version: string;
  createdBy: User;
  createdAt: Date;
  updatedAt: Date;
}

export interface ApprovalStepTemplate {
  stepNumber: number;
  name: string;
  description?: string;
  approverType: ApproverType;
  approverRoles: UserRole[];
  requiredApprovals: number;
  timeout?: number;
  escalation?: EscalationRule;
  conditions?: ApprovalCondition[];
}

export interface ApprovalSettings {
  allowParallel: boolean;
  requireAllApprovers: boolean;
  allowDelegation: boolean;
  allowWithdrawal: boolean;
  autoEscalate: boolean;
  notifyOnDecision: boolean;
  auditLevel: AuditLevel;
}

export interface WorkflowMetrics {
  totalRequests: number;
  pendingRequests: number;
  approvedRequests: number;
  rejectedRequests: number;
  expiredRequests: number;
  averageApprovalTime: number;
  approvalRate: number;
  escalationRate: number;
  timeByStep: Record<string, number>;
  userMetrics: Record<string, UserMetrics>;
}

export interface UserMetrics {
  totalRequests: number;
  approvedRequests: number;
  rejectedRequests: number;
  averageResponseTime: number;
  escalations: number;
  delegations: number;
}

// Enums
export enum ApprovalType {
  BASELINE_UPDATE = 'baseline_update',
  CONFIGURATION_CHANGE = 'configuration_change',
  DEPLOYMENT = 'deployment',
  EMERGENCY_CHANGE = 'emergency_change',
  ROLLBACK = 'rollback',
  POLICY_CHANGE = 'policy_change'
}

export enum ApprovalStatus {
  DRAFT = 'draft',
  PENDING = 'pending',
  IN_PROGRESS = 'in_progress',
  APPROVED = 'approved',
  REJECTED = 'rejected',
  WITHDRAWN = 'withdrawn',
  EXPIRED = 'expired',
  ESCALATED = 'escalated'
}

export enum ApprovalPriority {
  LOW = 'low',
  MEDIUM = 'medium',
  HIGH = 'high',
  CRITICAL = 'critical',
  EMERGENCY = 'emergency'
}

export enum ApproverType {
  USER = 'user',
  ROLE = 'role',
  GROUP = 'group',
  AUTO = 'auto'
}

export enum StepStatus {
  PENDING = 'pending',
  IN_PROGRESS = 'in_progress',
  COMPLETED = 'completed',
  SKIPPED = 'skipped',
  FAILED = 'failed',
  EXPIRED = 'expired'
}

export enum ApprovalDecision {
  APPROVE = 'approve',
  REJECT = 'reject',
  DELEGATE = 'delegate',
  REQUEST_INFO = 'request_info'
}

export enum Environment {
  DEVELOPMENT = 'development',
  STAGING = 'staging',
  PRODUCTION = 'production',
  TEST = 'test'
}

export enum UpdateType {
  BASELINE_REFRESH = 'baseline_refresh',
  CONFIGURATION_UPDATE = 'configuration_update',
  SCHEMA_CHANGE = 'schema_change',
  FEATURE_TOGGLE = 'feature_toggle',
  ROLLBACK = 'rollback'
}

export enum ChangeType {
  ADD = 'add',
  MODIFY = 'modify',
  DELETE = 'delete',
  MOVE = 'move'
}

export enum RiskLevel {
  LOW = 'low',
  MEDIUM = 'medium',
  HIGH = 'high',
  CRITICAL = 'critical'
}

export enum RollbackStrategy {
  AUTOMATIC = 'automatic',
  MANUAL = 'manual',
  CONDITIONAL = 'conditional'
}

export enum ValidationType {
  SYNTAX = 'syntax',
  SEMANTIC = 'semantic',
  PERFORMANCE = 'performance',
  SECURITY = 'security',
  BUSINESS = 'business'
}

export enum Severity {
  INFO = 'info',
  WARNING = 'warning',
  ERROR = 'error',
  CRITICAL = 'critical'
}

export enum DeploymentStrategy {
  ROLLING = 'rolling',
  BLUE_GREEN = 'blue_green',
  CANARY = 'canary',
  RECREATE = 'recreate'
}

export enum UserRole {
  ADMIN = 'admin',
  APPROVER = 'approver',
  REVIEWER = 'reviewer',
  DEVELOPER = 'developer',
  OPERATOR = 'operator',
  VIEWER = 'viewer'
}

export enum Permission {
  READ = 'read',
  WRITE = 'write',
  APPROVE = 'approve',
  ADMIN = 'admin',
  DEPLOY = 'deploy',
  ROLLBACK = 'rollback'
}

export enum EscalationTrigger {
  TIMEOUT = 'timeout',
  NO_RESPONSE = 'no_response',
  MANUAL = 'manual',
  CONDITION = 'condition'
}

export enum EscalationAction {
  NOTIFY = 'notify',
  REASSIGN = 'reassign',
  AUTO_APPROVE = 'auto_approve',
  AUTO_REJECT = 'auto_reject'
}

export enum ConditionType {
  FIELD_VALUE = 'field_value',
  TIME_RANGE = 'time_range',
  USER_ROLE = 'user_role',
  ENVIRONMENT = 'environment',
  RISK_LEVEL = 'risk_level'
}

export enum ComparisonOperator {
  EQUALS = 'equals',
  NOT_EQUALS = 'not_equals',
  GREATER_THAN = 'greater_than',
  LESS_THAN = 'less_than',
  CONTAINS = 'contains',
  IN = 'in',
  NOT_IN = 'not_in'
}

export enum LogicOperator {
  AND = 'and',
  OR = 'or',
  NOT = 'not'
}

export enum AuditAction {
  CREATE = 'create',
  UPDATE = 'update',
  APPROVE = 'approve',
  REJECT = 'reject',
  DELEGATE = 'delegate',
  ESCALATE = 'escalate',
  WITHDRAW = 'withdraw',
  VIEW = 'view',
  EXPORT = 'export'
}

export enum NotificationType {
  EMAIL = 'email',
  SMS = 'sms',
  SLACK = 'slack',
  WEBHOOK = 'webhook',
  IN_APP = 'in_app'
}

export enum NotificationChannel {
  EMAIL = 'email',
  SMS = 'sms',
  SLACK = 'slack',
  TEAMS = 'teams',
  WEBHOOK = 'webhook',
  PUSH = 'push'
}

export enum NotificationTrigger {
  REQUEST_CREATED = 'request_created',
  APPROVAL_REQUIRED = 'approval_required',
  DECISION_MADE = 'decision_made',
  ESCALATED = 'escalated',
  REMINDER = 'reminder',
  COMPLETED = 'completed'
}

export enum NotificationFrequency {
  IMMEDIATE = 'immediate',
  HOURLY = 'hourly',
  DAILY = 'daily',
  WEEKLY = 'weekly'
}

export enum TemplateCategory {
  BASELINE = 'baseline',
  DEPLOYMENT = 'deployment',
  CONFIGURATION = 'configuration',
  EMERGENCY = 'emergency',
  CUSTOM = 'custom'
}

export enum AuditLevel {
  MINIMAL = 'minimal',
  STANDARD = 'standard',
  DETAILED = 'detailed',
  COMPREHENSIVE = 'comprehensive'
}

export interface TestingRequirement {
  type: string;
  description: string;
  mandatory: boolean;
  estimatedTime: number;
}

export interface RollbackTrigger {
  condition: string;
  threshold: number;
  action: string;
}

export interface DataRecoveryPlan {
  strategy: string;
  backupLocation: string;
  recoveryTime: number;
  validationSteps: string[];
}

export interface DeploymentStage {
  name: string;
  environment: Environment;
  approvals: string[];
  gates: string[];
  rollbackOn: string[];
}

export interface HealthCheck {
  name: string;
  endpoint: string;
  timeout: number;
  retries: number;
  expectedStatus: number;
}

export interface NotificationPreference {
  channel: NotificationChannel;
  enabled: boolean;
  triggers: NotificationTrigger[];
  quietHours?: {
    start: string;
    end: string;
    timezone: string;
  };
}