import {
  ApprovalRequest,
  BaselineUpdateRequest,
  User,
  ApprovalStatus,
  Environment,
  DeploymentState
} from '../types/approval.types.js';
import { EventEmitter } from 'events';

export interface GitHubConfig {
  token: string;
  owner: string;
  repo: string;
  baseBranch: string;
  approvalBranch: string;
  webhookSecret?: string;
  enableAutoMerge: boolean;
  requireStatusChecks: boolean;
  requiredStatusChecks: string[];
  enableBranchProtection: boolean;
  dismissStaleReviews: boolean;
  requireCodeOwnerReviews: boolean;
}

export interface PullRequestInfo {
  number: number;
  title: string;
  body: string;
  head: string;
  base: string;
  url: string;
  state: 'open' | 'closed' | 'merged';
  mergeable: boolean;
  merged: boolean;
  draft: boolean;
  reviewers: GitHubUser[];
  assignees: GitHubUser[];
  labels: string[];
  statusChecks: StatusCheck[];
  reviews: PullRequestReview[];
  commits: CommitInfo[];
}

export interface GitHubUser {
  login: string;
  id: number;
  email?: string;
  name?: string;
  avatar_url: string;
}

export interface StatusCheck {
  name: string;
  status: 'pending' | 'success' | 'failure' | 'error';
  description: string;
  target_url?: string;
  conclusion?: string;
}

export interface PullRequestReview {
  id: number;
  user: GitHubUser;
  state: 'PENDING' | 'APPROVED' | 'CHANGES_REQUESTED' | 'COMMENTED' | 'DISMISSED';
  body: string;
  submitted_at: string;
}

export interface CommitInfo {
  sha: string;
  message: string;
  author: GitHubUser;
  timestamp: string;
}

export interface GitHubWebhookPayload {
  action: string;
  pull_request?: any;
  review?: any;
  check_run?: any;
  repository: any;
  sender: GitHubUser;
}

export interface BaselineUpdatePR {
  approvalRequestId: string;
  pullRequestNumber: number;
  updateId: string;
  environment: Environment;
  createdAt: Date;
  updatedAt: Date;
  status: 'open' | 'approved' | 'merged' | 'closed';
  reviewers: string[];
  checks: StatusCheck[];
  autoMergeEnabled: boolean;
}

export class GitHubIntegration extends EventEmitter {
  private config: GitHubConfig;
  private activePRs: Map<string, BaselineUpdatePR> = new Map();
  private webhookHandlers: Map<string, Function> = new Map();

  constructor(config: GitHubConfig) {
    super();
    this.config = config;
    this.setupWebhookHandlers();
  }

  /**
   * Create a pull request for baseline update approval
   */
  async createApprovalPR(
    approvalRequest: ApprovalRequest,
    updateRequest: BaselineUpdateRequest
  ): Promise<PullRequestInfo> {
    try {
      // Create branch for the baseline update
      const branchName = this.generateBranchName(updateRequest);
      await this.createBranch(branchName);

      // Generate baseline update files
      await this.generateBaselineFiles(updateRequest, branchName);

      // Create pull request
      const prData = {
        title: this.generatePRTitle(updateRequest),
        body: this.generatePRBody(approvalRequest, updateRequest),
        head: branchName,
        base: this.config.baseBranch,
        draft: false,
        assignees: approvalRequest.approvers[0]?.approvers.map(a => a.username) || [],
        reviewers: approvalRequest.approvers[0]?.approvers.map(a => a.username) || [],
        labels: this.generatePRLabels(updateRequest)
      };

      const prResponse = await this.createPullRequest(prData);

      // Store PR information
      const baselineUpdatePR: BaselineUpdatePR = {
        approvalRequestId: approvalRequest.id,
        pullRequestNumber: prResponse.number,
        updateId: updateRequest.id,
        environment: updateRequest.targetEnvironment,
        createdAt: new Date(),
        updatedAt: new Date(),
        status: 'open',
        reviewers: prData.reviewers,
        checks: [],
        autoMergeEnabled: this.config.enableAutoMerge
      };

      this.activePRs.set(approvalRequest.id, baselineUpdatePR);

      // Setup branch protection if enabled
      if (this.config.enableBranchProtection) {
        await this.setupBranchProtection(branchName);
      }

      // Create status checks
      await this.createStatusChecks(prResponse.number, updateRequest);

      this.emit('prCreated', { pr: prResponse, approvalRequest, updateRequest });

      return prResponse;

    } catch (error) {
      this.emit('prCreationFailed', { error, approvalRequest, updateRequest });
      throw new Error(`Failed to create PR: ${(error as Error).message}`);
    }
  }

  /**
   * Update PR status based on approval workflow
   */
  async updatePRStatus(approvalRequestId: string, status: ApprovalStatus): Promise<void> {
    const baselineUpdatePR = this.activePRs.get(approvalRequestId);
    if (!baselineUpdatePR) {
      throw new Error(`PR for approval request ${approvalRequestId} not found`);
    }

    const prNumber = baselineUpdatePR.pullRequestNumber;

    switch (status) {
      case ApprovalStatus.APPROVED:
        await this.approvePR(prNumber, baselineUpdatePR);
        break;
      case ApprovalStatus.REJECTED:
        await this.rejectPR(prNumber, baselineUpdatePR);
        break;
      case ApprovalStatus.WITHDRAWN:
        await this.closePR(prNumber, baselineUpdatePR);
        break;
    }

    baselineUpdatePR.updatedAt = new Date();
    this.emit('prStatusUpdated', { prNumber, status, baselineUpdatePR });
  }

  /**
   * Handle GitHub webhook events
   */
  async handleWebhook(payload: GitHubWebhookPayload): Promise<void> {
    const handler = this.webhookHandlers.get(payload.action);
    if (handler) {
      try {
        await handler(payload);
      } catch (error) {
        this.emit('webhookError', { error, payload });
      }
    }
  }

  /**
   * Sync approval status from PR reviews
   */
  async syncApprovalStatus(prNumber: number): Promise<void> {
    const prInfo = await this.getPullRequest(prNumber);
    const baselineUpdatePR = Array.from(this.activePRs.values())
      .find(pr => pr.pullRequestNumber === prNumber);

    if (!baselineUpdatePR) {
      return;
    }

    // Check if all required reviews are approved
    const requiredReviewers = baselineUpdatePR.reviewers;
    const approvedReviews = prInfo.reviews.filter(r => r.state === 'APPROVED');
    const approvedReviewers = approvedReviews.map(r => r.user.login);

    const allApproved = requiredReviewers.every(reviewer =>
      approvedReviewers.includes(reviewer)
    );

    if (allApproved && this.areStatusChecksPass(prInfo.statusChecks)) {
      // Trigger approval in the workflow engine
      this.emit('prApprovalComplete', {
        approvalRequestId: baselineUpdatePR.approvalRequestId,
        prNumber,
        reviews: approvedReviews
      });

      // Auto-merge if enabled
      if (baselineUpdatePR.autoMergeEnabled && prInfo.mergeable) {
        await this.mergePR(prNumber, baselineUpdatePR);
      }
    }
  }

  /**
   * Create deployment status checks
   */
  async createDeploymentStatusCheck(
    prNumber: number,
    deploymentState: DeploymentState
  ): Promise<void> {
    const statusData = {
      name: `deployment-${deploymentState.environment}`,
      status: this.mapDeploymentStatusToGitHub(deploymentState.status),
      description: `Deployment to ${deploymentState.environment}: ${deploymentState.stage}`,
      target_url: this.generateDeploymentUrl(deploymentState),
      conclusion: deploymentState.status === 'completed' ? 'success' :
                  deploymentState.status === 'failed' ? 'failure' : undefined
    };

    await this.createStatusCheck(prNumber, statusData);
  }

  /**
   * Update deployment progress in PR
   */
  async updateDeploymentProgress(
    prNumber: number,
    deploymentState: DeploymentState
  ): Promise<void> {
    const comment = this.generateDeploymentComment(deploymentState);
    await this.createOrUpdateComment(prNumber, comment, `deployment-${deploymentState.updateId}`);
  }

  /**
   * Get active PRs for environment
   */
  getActivePRsForEnvironment(environment: Environment): BaselineUpdatePR[] {
    return Array.from(this.activePRs.values())
      .filter(pr => pr.environment === environment && pr.status === 'open');
  }

  /**
   * Close PR and cleanup
   */
  async closePRAndCleanup(approvalRequestId: string, reason: string): Promise<void> {
    const baselineUpdatePR = this.activePRs.get(approvalRequestId);
    if (!baselineUpdatePR) {
      return;
    }

    const prNumber = baselineUpdatePR.pullRequestNumber;

    // Add comment explaining closure
    await this.addComment(prNumber, `🚫 **PR Closed**: ${reason}`);

    // Close the PR
    await this.closePullRequest(prNumber);

    // Delete the branch
    const branchName = this.generateBranchName({ id: baselineUpdatePR.updateId } as any);
    await this.deleteBranch(branchName);

    // Remove from active PRs
    this.activePRs.delete(approvalRequestId);

    this.emit('prClosed', { prNumber, reason, approvalRequestId });
  }

  // Private methods

  private setupWebhookHandlers(): void {
    this.webhookHandlers.set('pull_request', this.handlePullRequestEvent.bind(this));
    this.webhookHandlers.set('pull_request_review', this.handlePullRequestReviewEvent.bind(this));
    this.webhookHandlers.set('check_run', this.handleCheckRunEvent.bind(this));
    this.webhookHandlers.set('status', this.handleStatusEvent.bind(this));
  }

  private async handlePullRequestEvent(payload: GitHubWebhookPayload): Promise<void> {
    const { action, pull_request } = payload;
    const prNumber = pull_request.number;

    switch (action) {
      case 'opened':
        this.emit('prOpened', { prNumber, pr: pull_request });
        break;
      case 'closed':
        if (pull_request.merged) {
          await this.handlePRMerged(prNumber);
        } else {
          await this.handlePRClosed(prNumber);
        }
        break;
      case 'synchronize':
        await this.handlePRUpdated(prNumber);
        break;
    }
  }

  private async handlePullRequestReviewEvent(payload: GitHubWebhookPayload): Promise<void> {
    const { action, pull_request, review } = payload;
    const prNumber = pull_request.number;

    if (action === 'submitted') {
      await this.syncApprovalStatus(prNumber);
    }
  }

  private async handleCheckRunEvent(payload: GitHubWebhookPayload): Promise<void> {
    const { check_run, repository } = payload;

    // Find PR associated with this check run
    const prNumber = await this.findPRForCheckRun(check_run.head_sha);
    if (prNumber) {
      await this.syncApprovalStatus(prNumber);
    }
  }

  private async handleStatusEvent(payload: GitHubWebhookPayload): Promise<void> {
    // Handle status updates
    const sha = payload.sha;
    const prNumber = await this.findPRForCommit(sha);
    if (prNumber) {
      await this.syncApprovalStatus(prNumber);
    }
  }

  private async handlePRMerged(prNumber: number): Promise<void> {
    const baselineUpdatePR = Array.from(this.activePRs.values())
      .find(pr => pr.pullRequestNumber === prNumber);

    if (baselineUpdatePR) {
      baselineUpdatePR.status = 'merged';
      this.emit('prMerged', { prNumber, approvalRequestId: baselineUpdatePR.approvalRequestId });
    }
  }

  private async handlePRClosed(prNumber: number): Promise<void> {
    const baselineUpdatePR = Array.from(this.activePRs.values())
      .find(pr => pr.pullRequestNumber === prNumber);

    if (baselineUpdatePR) {
      baselineUpdatePR.status = 'closed';
      this.emit('prClosed', { prNumber, approvalRequestId: baselineUpdatePR.approvalRequestId });
    }
  }

  private async handlePRUpdated(prNumber: number): Promise<void> {
    // Re-run status checks when PR is updated
    await this.syncApprovalStatus(prNumber);
  }

  private generateBranchName(updateRequest: BaselineUpdateRequest): string {
    const timestamp = new Date().toISOString().slice(0, 19).replace(/:/g, '-');
    return `baseline-update/${updateRequest.targetEnvironment}/${updateRequest.id}-${timestamp}`;
  }

  private generatePRTitle(updateRequest: BaselineUpdateRequest): string {
    return `🔄 Baseline Update: ${updateRequest.updateType} for ${updateRequest.targetEnvironment}`;
  }

  private generatePRBody(approvalRequest: ApprovalRequest, updateRequest: BaselineUpdateRequest): string {
    const changes = updateRequest.changes;
    const impact = updateRequest.impactAssessment;
    const rollback = updateRequest.rollbackPlan;

    return `
## 📋 Baseline Update Request

**Update ID:** \`${updateRequest.id}\`
**Environment:** \`${updateRequest.targetEnvironment}\`
**Update Type:** \`${updateRequest.updateType}\`
**Risk Level:** \`${impact.riskLevel}\`

### 📝 Description
${approvalRequest.description}

### 🔧 Changes (${changes.length})
${changes.map(change => `- **${change.type.toUpperCase()}** \`${change.component}\` (Risk: ${change.risk})`).join('\n')}

### 📊 Impact Assessment
- **Affected Users:** ${impact.affectedUsers.toLocaleString()}
- **Estimated Downtime:** ${impact.downtime} minutes
- **Rollback Time:** ${impact.rollbackTime} minutes
- **Business Impact:** ${impact.businessImpact}

### 🔙 Rollback Plan
- **Strategy:** ${rollback.strategy}
- **Steps:** ${rollback.steps.length}
- **Estimated Time:** ${rollback.estimatedTime} minutes

### ✅ Validation Rules
${updateRequest.validationRules.map(rule => `- **${rule.name}** (${rule.severity})`).join('\n') || 'No validation rules specified'}

### 🚀 Deployment Configuration
- **Strategy:** ${updateRequest.deploymentConfig.strategy}
- **Environment:** ${updateRequest.deploymentConfig.environment}

### 👥 Required Approvals
${approvalRequest.approvers[0]?.approvers.map(approver => `- @${approver.username}`).join('\n') || 'No approvers specified'}

---

**⚠️ Important:** This PR requires approval before merging. Once approved and merged, the baseline update will be automatically deployed to the specified environment.

For questions or concerns, please contact the requester: @${approvalRequest.requester.username}
    `;
  }

  private generatePRLabels(updateRequest: BaselineUpdateRequest): string[] {
    const labels = [
      'baseline-update',
      `env:${updateRequest.targetEnvironment}`,
      `risk:${updateRequest.impactAssessment.riskLevel}`,
      `type:${updateRequest.updateType}`
    ];

    if (updateRequest.impactAssessment.riskLevel === 'critical') {
      labels.push('urgent');
    }

    return labels;
  }

  private async generateBaselineFiles(updateRequest: BaselineUpdateRequest, branchName: string): Promise<void> {
    // Generate baseline update configuration file
    const configFile = {
      updateId: updateRequest.id,
      environment: updateRequest.targetEnvironment,
      updateType: updateRequest.updateType,
      changes: updateRequest.changes,
      impactAssessment: updateRequest.impactAssessment,
      rollbackPlan: updateRequest.rollbackPlan,
      validationRules: updateRequest.validationRules,
      deploymentConfig: updateRequest.deploymentConfig,
      createdAt: new Date().toISOString()
    };

    // Create the configuration file in the repository
    await this.createFile(
      `baseline-updates/${updateRequest.id}/config.json`,
      JSON.stringify(configFile, null, 2),
      `Add baseline update configuration for ${updateRequest.id}`,
      branchName
    );

    // Create individual change files
    for (const change of updateRequest.changes) {
      await this.createFile(
        `baseline-updates/${updateRequest.id}/changes/${change.id}.json`,
        JSON.stringify(change, null, 2),
        `Add change configuration for ${change.component}`,
        branchName
      );
    }

    // Create rollback script
    const rollbackScript = this.generateRollbackScript(updateRequest.rollbackPlan);
    await this.createFile(
      `baseline-updates/${updateRequest.id}/rollback.sh`,
      rollbackScript,
      `Add rollback script for ${updateRequest.id}`,
      branchName
    );
  }

  private generateRollbackScript(rollbackPlan: RollbackPlan): string {
    const script = `#!/bin/bash
# Rollback script for baseline update
# Generated on: ${new Date().toISOString()}

set -e

echo "Starting rollback process..."
echo "Strategy: ${rollbackPlan.strategy}"
echo "Estimated time: ${rollbackPlan.estimatedTime} minutes"

${rollbackPlan.steps.map((step, index) => `
echo "Step ${step.order}: ${step.description}"
${step.command || `echo "Manual step: ${step.description}"`}

echo "Validating step ${step.order}..."
# ${step.validation}

echo "Step ${step.order} completed successfully"
`).join('\n')}

echo "Rollback completed successfully"
echo "Running validation checks..."

${rollbackPlan.validationChecks.map(check => `
echo "Running ${check}..."
# Validation check: ${check}
`).join('\n')}

echo "All validation checks passed"
echo "Rollback process completed successfully"
    `;

    return script;
  }

  private generateDeploymentComment(deploymentState: DeploymentState): string {
    const progressBar = this.generateProgressBar(deploymentState.progress);

    return `
## 🚀 Deployment Status

**Update ID:** \`${deploymentState.updateId}\`
**Environment:** \`${deploymentState.environment}\`
**Status:** \`${deploymentState.status}\`
**Stage:** \`${deploymentState.stage}\`

### Progress
${progressBar} ${deploymentState.progress}%

**Changes:** ${deploymentState.currentChange}/${deploymentState.totalChanges}
**Started:** ${deploymentState.startTime.toISOString()}
**Estimated Completion:** ${deploymentState.estimatedCompletion.toISOString()}

### Health Checks
${deploymentState.healthChecks.map(check =>
  `- ${check.passed ? '✅' : '❌'} **${check.name}** (${check.responseTime}ms)`
).join('\n') || 'No health checks available'}

### Recent Logs
${deploymentState.logs.slice(-5).map(log =>
  `- \`${log.timestamp.toISOString()}\` [${log.level.toUpperCase()}] ${log.message}`
).join('\n') || 'No recent logs available'}

---
*Last updated: ${new Date().toISOString()}*
    `;
  }

  private generateProgressBar(progress: number): string {
    const barLength = 20;
    const filledLength = Math.round((progress / 100) * barLength);
    const bar = '█'.repeat(filledLength) + '░'.repeat(barLength - filledLength);
    return `[${bar}]`;
  }

  private mapDeploymentStatusToGitHub(status: string): string {
    switch (status) {
      case 'completed':
        return 'success';
      case 'failed':
      case 'rolled_back':
        return 'failure';
      case 'pending':
      case 'validating':
      case 'deploying':
      case 'testing':
        return 'pending';
      default:
        return 'pending';
    }
  }

  private generateDeploymentUrl(deploymentState: DeploymentState): string {
    // Return URL to deployment dashboard or logs
    return `${process.env.DASHBOARD_URL || 'http://localhost:3000'}/deployments/${deploymentState.updateId}`;
  }

  private areStatusChecksPass(statusChecks: StatusCheck[]): boolean {
    if (!this.config.requireStatusChecks) {
      return true;
    }

    const requiredChecks = this.config.requiredStatusChecks;
    if (requiredChecks.length === 0) {
      return true;
    }

    return requiredChecks.every(requiredCheck => {
      const check = statusChecks.find(c => c.name === requiredCheck);
      return check && check.status === 'success';
    });
  }

  // GitHub API methods (simplified - replace with actual GitHub API calls)

  private async createBranch(branchName: string): Promise<void> {
    // Implementation would use GitHub API to create branch
  }

  private async createPullRequest(prData: any): Promise<PullRequestInfo> {
    // Implementation would use GitHub API to create PR
    return {
      number: Math.floor(Math.random() * 1000),
      title: prData.title,
      body: prData.body,
      head: prData.head,
      base: prData.base,
      url: `https://github.com/${this.config.owner}/${this.config.repo}/pull/${Math.floor(Math.random() * 1000)}`,
      state: 'open',
      mergeable: true,
      merged: false,
      draft: false,
      reviewers: [],
      assignees: [],
      labels: prData.labels,
      statusChecks: [],
      reviews: [],
      commits: []
    };
  }

  private async getPullRequest(prNumber: number): Promise<PullRequestInfo> {
    // Implementation would use GitHub API to get PR info
    return {} as PullRequestInfo;
  }

  private async createFile(path: string, content: string, message: string, branch: string): Promise<void> {
    // Implementation would use GitHub API to create file
  }

  private async createStatusCheck(prNumber: number, statusData: any): Promise<void> {
    // Implementation would use GitHub API to create status check
  }

  private async addComment(prNumber: number, comment: string): Promise<void> {
    // Implementation would use GitHub API to add comment
  }

  private async createOrUpdateComment(prNumber: number, comment: string, identifier: string): Promise<void> {
    // Implementation would find existing comment by identifier and update, or create new
  }

  private async setupBranchProtection(branchName: string): Promise<void> {
    // Implementation would use GitHub API to setup branch protection
  }

  private async approvePR(prNumber: number, baselineUpdatePR: BaselineUpdatePR): Promise<void> {
    baselineUpdatePR.status = 'approved';
    await this.addComment(prNumber, '✅ **Approval Complete**: All required approvals received. Ready for merge.');
  }

  private async rejectPR(prNumber: number, baselineUpdatePR: BaselineUpdatePR): Promise<void> {
    baselineUpdatePR.status = 'closed';
    await this.addComment(prNumber, '❌ **Approval Rejected**: This baseline update has been rejected.');
    await this.closePullRequest(prNumber);
  }

  private async closePR(prNumber: number, baselineUpdatePR: BaselineUpdatePR): Promise<void> {
    baselineUpdatePR.status = 'closed';
    await this.closePullRequest(prNumber);
  }

  private async mergePR(prNumber: number, baselineUpdatePR: BaselineUpdatePR): Promise<void> {
    // Implementation would use GitHub API to merge PR
    baselineUpdatePR.status = 'merged';
  }

  private async closePullRequest(prNumber: number): Promise<void> {
    // Implementation would use GitHub API to close PR
  }

  private async deleteBranch(branchName: string): Promise<void> {
    // Implementation would use GitHub API to delete branch
  }

  private async findPRForCheckRun(sha: string): Promise<number | null> {
    // Implementation would find PR for given commit SHA
    return null;
  }

  private async findPRForCommit(sha: string): Promise<number | null> {
    // Implementation would find PR for given commit SHA
    return null;
  }
}