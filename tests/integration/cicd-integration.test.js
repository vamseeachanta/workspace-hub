const GitHubIntegration = require('../../src/integrations/github-integration');
const GitLabIntegration = require('../../src/integrations/gitlab-integration');
const JenkinsIntegration = require('../../src/integrations/jenkins-integration');
const CircleCIIntegration = require('../../src/integrations/circleci-integration');
const MockFactory = require('../fixtures/mock-factories');
const nock = require('nock');

describe('CI/CD Integration Tests', () => {
  let mockLogger;
  let mockDatabase;
  
  beforeAll(() => {
    // Disable real HTTP requests
    nock.disableNetConnect();
    nock.enableNetConnect('127.0.0.1');
  });
  
  afterAll(() => {
    nock.restore();
  });
  
  beforeEach(() => {
    mockLogger = createMockLogger();
    mockDatabase = createMockDatabase();
    nock.cleanAll();
  });

  describe('GitHubIntegration', () => {
    let githubIntegration;
    const mockConfig = {
      token: 'ghp_test_token',
      owner: 'test-org',
      repo: 'test-repo'
    };

    beforeEach(() => {
      githubIntegration = new GitHubIntegration({
        config: mockConfig,
        logger: mockLogger,
        database: mockDatabase
      });
    });

    it('should authenticate with GitHub API', async () => {
      const githubAPI = nock('https://api.github.com')
        .get('/user')
        .reply(200, {
          login: 'test-user',
          id: 12345,
          type: 'User'
        });

      const authResult = await githubIntegration.authenticate();

      expect(authResult).toEqual({
        success: true,
        user: {
          login: 'test-user',
          id: 12345,
          type: 'User'
        }
      });
      
      expect(githubAPI.isDone()).toBe(true);
    });

    it('should create status check on pull request', async () => {
      const prNumber = 123;
      const commitSha = 'abc123def456';
      const baselineResult = {
        status: 'success',
        summary: 'All tests passed',
        metrics: {
          passRate: 95.5,
          coverage: { lines: 88.2 }
        }
      };

      const githubAPI = nock('https://api.github.com')
        .post(`/repos/${mockConfig.owner}/${mockConfig.repo}/statuses/${commitSha}`, {
          state: 'success',
          description: 'Baseline comparison passed - 95.5% pass rate, 88.2% coverage',
          context: 'baseline-comparison',
          target_url: expect.stringContaining('/reports/')
        })
        .reply(201, { id: 'status-123' });

      const statusResult = await githubIntegration.createStatusCheck(
        commitSha,
        baselineResult
      );

      expect(statusResult.success).toBe(true);
      expect(statusResult.statusId).toBe('status-123');
      expect(githubAPI.isDone()).toBe(true);
    });

    it('should post comment with comparison results', async () => {
      const prNumber = 123;
      const comparison = MockFactory.createComparison('baseline-1', 'run-1');

      const githubAPI = nock('https://api.github.com')
        .post(`/repos/${mockConfig.owner}/${mockConfig.repo}/issues/${prNumber}/comments`, {
          body: expect.stringContaining('## Baseline Comparison Results')
        })
        .reply(201, { id: 'comment-456' });

      const commentResult = await githubIntegration.postComparisonComment(
        prNumber,
        comparison
      );

      expect(commentResult.success).toBe(true);
      expect(commentResult.commentId).toBe('comment-456');
      expect(githubAPI.isDone()).toBe(true);
    });

    it('should handle GitHub API rate limiting', async () => {
      const githubAPI = nock('https://api.github.com')
        .get('/user')
        .reply(403, {
          message: 'API rate limit exceeded',
          documentation_url: 'https://docs.github.com/rest/overview/resources-in-the-rest-api#rate-limiting'
        }, {
          'X-RateLimit-Limit': '5000',
          'X-RateLimit-Remaining': '0',
          'X-RateLimit-Reset': String(Math.floor(Date.now() / 1000) + 3600)
        });

      await expect(githubIntegration.authenticate())
        .rejects.toThrow('GitHub API rate limit exceeded');

      expect(mockLogger.warn).toHaveBeenCalledWith(
        'GitHub API rate limit exceeded',
        expect.objectContaining({
          resetTime: expect.any(String)
        })
      );
      
      expect(githubAPI.isDone()).toBe(true);
    });

    it('should setup webhook for automated baseline updates', async () => {
      const webhookConfig = {
        url: 'https://baseline-service.example.com/webhook/github',
        events: ['push', 'pull_request'],
        secret: 'webhook-secret'
      };

      const githubAPI = nock('https://api.github.com')
        .post(`/repos/${mockConfig.owner}/${mockConfig.repo}/hooks`, {
          name: 'web',
          active: true,
          events: webhookConfig.events,
          config: {
            url: webhookConfig.url,
            content_type: 'json',
            secret: webhookConfig.secret,
            insecure_ssl: '0'
          }
        })
        .reply(201, {
          id: 'webhook-789',
          url: webhookConfig.url,
          events: webhookConfig.events
        });

      const webhookResult = await githubIntegration.setupWebhook(webhookConfig);

      expect(webhookResult.success).toBe(true);
      expect(webhookResult.webhookId).toBe('webhook-789');
      expect(githubAPI.isDone()).toBe(true);
    });

    it('should process webhook payload', async () => {
      const webhookPayload = {
        action: 'opened',
        pull_request: {
          number: 123,
          head: {
            sha: 'abc123def456',
            ref: 'feature/new-feature'
          },
          base: {
            sha: 'def456ghi789',
            ref: 'main'
          }
        },
        repository: {
          full_name: `${mockConfig.owner}/${mockConfig.repo}`
        }
      };

      mockDatabase.query.mockResolvedValueOnce([
        { id: 'baseline-1', branch: 'main', commit: 'def456ghi789' }
      ]);

      const processResult = await githubIntegration.processWebhook(webhookPayload);

      expect(processResult).toEqual({
        action: 'pr_opened',
        triggerBaseline: true,
        baselineId: 'baseline-1',
        prNumber: 123,
        headSha: 'abc123def456'
      });
    });
  });

  describe('GitLabIntegration', () => {
    let gitlabIntegration;
    const mockConfig = {
      token: 'glpat_test_token',
      projectId: '12345',
      baseUrl: 'https://gitlab.example.com'
    };

    beforeEach(() => {
      gitlabIntegration = new GitLabIntegration({
        config: mockConfig,
        logger: mockLogger,
        database: mockDatabase
      });
    });

    it('should create merge request note with comparison results', async () => {
      const mrIid = 123;
      const comparison = MockFactory.createComparison('baseline-1', 'run-1');

      const gitlabAPI = nock(mockConfig.baseUrl)
        .post(`/api/v4/projects/${mockConfig.projectId}/merge_requests/${mrIid}/notes`, {
          body: expect.stringContaining('## Baseline Comparison Results')
        })
        .reply(201, { id: 'note-456' });

      const noteResult = await gitlabIntegration.createMRNote(mrIid, comparison);

      expect(noteResult.success).toBe(true);
      expect(noteResult.noteId).toBe('note-456');
      expect(gitlabAPI.isDone()).toBe(true);
    });

    it('should update pipeline status', async () => {
      const pipelineId = 789;
      const status = 'success';
      const description = 'Baseline comparison passed';

      const gitlabAPI = nock(mockConfig.baseUrl)
        .put(`/api/v4/projects/${mockConfig.projectId}/pipelines/${pipelineId}/status`, {
          status: status,
          description: description
        })
        .reply(200, { id: pipelineId, status: status });

      const statusResult = await gitlabIntegration.updatePipelineStatus(
        pipelineId,
        status,
        description
      );

      expect(statusResult.success).toBe(true);
      expect(gitlabAPI.isDone()).toBe(true);
    });
  });

  describe('JenkinsIntegration', () => {
    let jenkinsIntegration;
    const mockConfig = {
      url: 'https://jenkins.example.com',
      username: 'jenkins-user',
      token: 'jenkins-token',
      jobName: 'baseline-comparison'
    };

    beforeEach(() => {
      jenkinsIntegration = new JenkinsIntegration({
        config: mockConfig,
        logger: mockLogger
      });
    });

    it('should trigger Jenkins job with parameters', async () => {
      const jobParameters = {
        BASELINE_ID: 'baseline-1',
        COMMIT_SHA: 'abc123def456',
        BRANCH: 'feature/test'
      };

      const jenkinsAPI = nock(mockConfig.url)
        .post(`/job/${mockConfig.jobName}/buildWithParameters`, jobParameters)
        .reply(201, '', {
          'Location': `${mockConfig.url}/queue/item/123/`
        });

      const buildResult = await jenkinsIntegration.triggerJob(jobParameters);

      expect(buildResult.success).toBe(true);
      expect(buildResult.queueItem).toBe('123');
      expect(jenkinsAPI.isDone()).toBe(true);
    });

    it('should get build status', async () => {
      const buildNumber = 456;

      const jenkinsAPI = nock(mockConfig.url)
        .get(`/job/${mockConfig.jobName}/${buildNumber}/api/json`)
        .reply(200, {
          number: buildNumber,
          result: 'SUCCESS',
          building: false,
          duration: 120000,
          timestamp: Date.now() - 120000
        });

      const statusResult = await jenkinsIntegration.getBuildStatus(buildNumber);

      expect(statusResult).toEqual({
        buildNumber: buildNumber,
        result: 'SUCCESS',
        building: false,
        duration: 120000,
        timestamp: expect.any(Number)
      });
      
      expect(jenkinsAPI.isDone()).toBe(true);
    });

    it('should handle Jenkins authentication errors', async () => {
      const jenkinsAPI = nock(mockConfig.url)
        .get(`/job/${mockConfig.jobName}/api/json`)
        .reply(401, { error: 'Invalid credentials' });

      await expect(jenkinsIntegration.getJobInfo())
        .rejects.toThrow('Jenkins authentication failed');

      expect(jenkinsAPI.isDone()).toBe(true);
    });
  });

  describe('CircleCIIntegration', () => {
    let circleCIIntegration;
    const mockConfig = {
      token: 'circle-token',
      projectSlug: 'github/test-org/test-repo'
    };

    beforeEach(() => {
      circleCIIntegration = new CircleCIIntegration({
        config: mockConfig,
        logger: mockLogger
      });
    });

    it('should trigger pipeline with custom parameters', async () => {
      const pipelineParams = {
        branch: 'feature/test',
        parameters: {
          run_baseline_comparison: true,
          baseline_id: 'baseline-1',
          commit_sha: 'abc123def456'
        }
      };

      const circleAPI = nock('https://circleci.com')
        .post(`/api/v2/project/${mockConfig.projectSlug}/pipeline`, {
          branch: pipelineParams.branch,
          parameters: pipelineParams.parameters
        })
        .reply(201, {
          id: 'pipeline-uuid-123',
          number: 789,
          state: 'pending'
        });

      const pipelineResult = await circleCIIntegration.triggerPipeline(pipelineParams);

      expect(pipelineResult.success).toBe(true);
      expect(pipelineResult.pipelineId).toBe('pipeline-uuid-123');
      expect(circleAPI.isDone()).toBe(true);
    });

    it('should get pipeline status and artifacts', async () => {
      const pipelineId = 'pipeline-uuid-123';
      const workflowId = 'workflow-uuid-456';

      const circleAPI = nock('https://circleci.com')
        .get(`/api/v2/pipeline/${pipelineId}/workflow`)
        .reply(200, {
          items: [{
            id: workflowId,
            name: 'build-and-test',
            status: 'success'
          }]
        })
        .get(`/api/v2/workflow/${workflowId}/job`)
        .reply(200, {
          items: [{
            id: 'job-uuid-789',
            name: 'baseline-comparison',
            status: 'success'
          }]
        })
        .get('/api/v2/job/job-uuid-789/artifacts')
        .reply(200, {
          items: [{
            path: 'baseline-report.json',
            url: 'https://artifacts.circleci.com/baseline-report.json'
          }]
        });

      const statusResult = await circleCIIntegration.getPipelineStatus(pipelineId);

      expect(statusResult).toEqual({
        pipelineId: pipelineId,
        status: 'success',
        workflows: expect.arrayContaining([{
          id: workflowId,
          name: 'build-and-test',
          status: 'success'
        }]),
        artifacts: expect.arrayContaining([{
          path: 'baseline-report.json',
          url: 'https://artifacts.circleci.com/baseline-report.json'
        }])
      });
      
      expect(circleAPI.isDone()).toBe(true);
    });
  });

  describe('Integration Workflows', () => {
    it('should coordinate baseline comparison across multiple CI systems', async () => {
      const gitHubIntegration = new GitHubIntegration({
        config: { token: 'gh-token', owner: 'org', repo: 'repo' },
        logger: mockLogger
      });
      
      const jenkinsIntegration = new JenkinsIntegration({
        config: { url: 'https://jenkins.example.com', jobName: 'baseline' },
        logger: mockLogger
      });

      // Mock GitHub webhook payload
      const webhookPayload = {
        action: 'opened',
        pull_request: {
          number: 123,
          head: { sha: 'abc123' }
        }
      };

      // Mock API responses
      nock('https://api.github.com')
        .post('/repos/org/repo/statuses/abc123')
        .reply(201, { id: 'status-123' });

      nock('https://jenkins.example.com')
        .post('/job/baseline/buildWithParameters')
        .reply(201, '', { 'Location': '/queue/item/456/' });

      // Process workflow
      const githubResult = await gitHubIntegration.processWebhook(webhookPayload);
      
      if (githubResult.triggerBaseline) {
        const jenkinsResult = await jenkinsIntegration.triggerJob({
          PR_NUMBER: githubResult.prNumber,
          COMMIT_SHA: githubResult.headSha
        });
        
        expect(jenkinsResult.success).toBe(true);
      }

      expect(githubResult.action).toBe('pr_opened');
    });

    it('should handle CI/CD integration failures gracefully', async () => {
      const integration = new GitHubIntegration({
        config: { token: 'invalid-token', owner: 'org', repo: 'repo' },
        logger: mockLogger
      });

      nock('https://api.github.com')
        .post('/repos/org/repo/statuses/abc123')
        .reply(401, { message: 'Bad credentials' });

      const result = await integration.createStatusCheck('abc123', {
        status: 'success',
        summary: 'Test passed'
      });

      expect(result.success).toBe(false);
      expect(result.error).toContain('Bad credentials');
      expect(mockLogger.error).toHaveBeenCalledWith(
        'Failed to create GitHub status check',
        expect.any(Object)
      );
    });

    it('should retry failed API calls with exponential backoff', async () => {
      const integration = new GitHubIntegration({
        config: { token: 'gh-token', owner: 'org', repo: 'repo', retryAttempts: 3 },
        logger: mockLogger
      });

      // First two attempts fail, third succeeds
      nock('https://api.github.com')
        .get('/user')
        .reply(500, { message: 'Internal Server Error' })
        .get('/user')
        .reply(500, { message: 'Internal Server Error' })
        .get('/user')
        .reply(200, { login: 'test-user' });

      const result = await integration.authenticate();

      expect(result.success).toBe(true);
      expect(result.user.login).toBe('test-user');
      expect(mockLogger.warn).toHaveBeenCalledTimes(2); // Two retry warnings
    });
  });
});
