# CI/CD Integration Points and Workflows

## Integration Overview

The Test Baseline Tracking System integrates seamlessly with major CI/CD platforms through plugins, actions, and webhooks, providing automated quality gates and continuous monitoring of test performance metrics.

## Architecture Integration

```
┌─────────────────────────────────────────────────────────────────┐
│                     CI/CD Integration Layer                     │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌──────────┐│
│  │   GitHub    │  │   GitLab    │  │   Jenkins   │  │   Azure  ││
│  │   Actions   │  │     CI      │  │  Pipeline   │  │ DevOps   ││
│  └─────────────┘  └─────────────┘  └─────────────┘  └──────────┘│
│         │               │               │               │       │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │                 Integration Gateway                        ││
│  └─────────────────────────────────────────────────────────────┘│
│                            │                                   │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │              Pre/Post Commit Hooks                         ││
│  └─────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────┘
```

## 1. GitHub Actions Integration

### GitHub Action Definition
```yaml
# .github/workflows/test-baseline-tracking.yml
name: Test Baseline Tracking

on:
  push:
    branches: [ main, develop, 'feature/*' ]
  pull_request:
    branches: [ main, develop ]
  schedule:
    - cron: '0 2 * * *'  # Daily baseline update

env:
  TBTS_API_URL: ${{ secrets.TBTS_API_URL }}
  TBTS_API_KEY: ${{ secrets.TBTS_API_KEY }}
  TBTS_PROJECT_ID: ${{ secrets.TBTS_PROJECT_ID }}

jobs:
  test-with-baseline-tracking:
    runs-on: ubuntu-latest

    steps:
    - name: Checkout code
      uses: actions/checkout@v4
      with:
        fetch-depth: 0  # Full history for trend analysis

    - name: Setup Node.js
      uses: actions/setup-node@v4
      with:
        node-version: '18'
        cache: 'npm'

    - name: Install dependencies
      run: npm ci

    - name: Setup Test Baseline Tracking
      uses: test-baseline-system/setup-action@v1
      with:
        api-url: ${{ env.TBTS_API_URL }}
        api-key: ${{ env.TBTS_API_KEY }}
        project-id: ${{ env.TBTS_PROJECT_ID }}
        framework: 'jest'
        environment: ${{ github.ref == 'refs/heads/main' && 'production' || 'development' }}

    - name: Run tests with metrics collection
      run: |
        npm test -- --coverage --json --outputFile=test-results.json
      continue-on-error: true

    - name: Collect and analyze metrics
      uses: test-baseline-system/analyze-action@v1
      with:
        test-results-path: 'test-results.json'
        coverage-path: 'coverage/coverage-final.json'
        baseline-comparison: true
        update-baseline: ${{ github.ref == 'refs/heads/main' }}
        gate-type: ${{ github.event_name == 'pull_request' && 'quality_gate' || 'development' }}

    - name: Post results to PR
      if: github.event_name == 'pull_request'
      uses: test-baseline-system/pr-comment-action@v1
      with:
        github-token: ${{ secrets.GITHUB_TOKEN }}
        comparison-results-path: 'tbts-results.json'

    - name: Upload artifacts
      uses: actions/upload-artifact@v4
      if: always()
      with:
        name: test-baseline-results-${{ github.run_id }}
        path: |
          tbts-results.json
          test-results.json
          coverage/

    - name: Quality gate check
      if: github.event_name == 'pull_request'
      run: |
        if [ -f "tbts-gate-result.txt" ]; then
          GATE_RESULT=$(cat tbts-gate-result.txt)
          if [ "$GATE_RESULT" = "failed" ]; then
            echo "Quality gate failed - blocking PR merge"
            exit 1
          elif [ "$GATE_RESULT" = "warning" ]; then
            echo "Quality gate passed with warnings"
            exit 0
          else
            echo "Quality gate passed"
            exit 0
          fi
        else
          echo "No gate result found"
          exit 1
        fi
```

### Custom GitHub Action Implementation
```typescript
// src/setup-action.ts
import * as core from '@actions/core';
import * as github from '@actions/github';
import { TBTSClient } from './tbts-client';

async function run(): Promise<void> {
  try {
    const apiUrl = core.getInput('api-url', { required: true });
    const apiKey = core.getInput('api-key', { required: true });
    const projectId = core.getInput('project-id', { required: true });
    const framework = core.getInput('framework', { required: true });
    const environment = core.getInput('environment') || 'development';

    const client = new TBTSClient(apiUrl, apiKey);

    // Initialize tracking context
    const context = {
      project: projectId,
      branch: github.context.ref.replace('refs/heads/', ''),
      environment,
      commit: github.context.sha,
      buildNumber: github.context.runNumber.toString(),
      framework,
      repository: github.context.repo.repo,
      actor: github.context.actor
    };

    // Register build start
    const trackingId = await client.startTracking(context);

    // Export tracking context for subsequent steps
    core.setOutput('tracking-id', trackingId);
    core.setOutput('context', JSON.stringify(context));

    // Set environment variables for test framework integration
    core.exportVariable('TBTS_TRACKING_ID', trackingId);
    core.exportVariable('TBTS_CONTEXT', JSON.stringify(context));

    core.info(`Test baseline tracking initialized for ${framework} framework`);

  } catch (error) {
    core.setFailed(error instanceof Error ? error.message : 'Unknown error');
  }
}

run();
```

### Analysis Action Implementation
```typescript
// src/analyze-action.ts
import * as core from '@actions/core';
import * as fs from 'fs';
import { TBTSClient } from './tbts-client';
import { MetricsProcessor } from './metrics-processor';

async function run(): Promise<void> {
  try {
    const testResultsPath = core.getInput('test-results-path', { required: true });
    const coveragePath = core.getInput('coverage-path');
    const baselineComparison = core.getBooleanInput('baseline-comparison');
    const updateBaseline = core.getBooleanInput('update-baseline');
    const gateType = core.getInput('gate-type') || 'development';

    const trackingId = process.env.TBTS_TRACKING_ID;
    const context = JSON.parse(process.env.TBTS_CONTEXT || '{}');

    if (!trackingId) {
      throw new Error('TBTS tracking not initialized. Run setup-action first.');
    }

    const client = new TBTSClient(
      process.env.TBTS_API_URL!,
      process.env.TBTS_API_KEY!
    );

    // Process test results
    const processor = new MetricsProcessor(context.framework);

    const testResults = JSON.parse(fs.readFileSync(testResultsPath, 'utf8'));
    const coverageData = coveragePath ? JSON.parse(fs.readFileSync(coveragePath, 'utf8')) : null;

    const metrics = await processor.processResults(testResults, coverageData);

    // Submit metrics to TBTS
    await client.submitMetrics(trackingId, metrics);

    let comparisonResult = null;
    if (baselineComparison) {
      // Perform baseline comparison
      comparisonResult = await client.compareWithBaseline(trackingId, {
        gateType,
        context
      });

      // Save comparison results
      fs.writeFileSync('tbts-results.json', JSON.stringify(comparisonResult, null, 2));

      // Set gate result
      fs.writeFileSync('tbts-gate-result.txt', comparisonResult.summary.overall_result);

      // Set outputs
      core.setOutput('gate-result', comparisonResult.summary.overall_result);
      core.setOutput('blocking-issues', comparisonResult.summary.issues_count.blocking);
      core.setOutput('improvements', comparisonResult.improvements.length);
    }

    if (updateBaseline) {
      await client.updateBaseline(trackingId);
      core.info('Baseline updated successfully');
    }

    // Create summary
    const summary = generateSummary(metrics, comparisonResult);
    core.summary.addRaw(summary);
    await core.summary.write();

  } catch (error) {
    core.setFailed(error instanceof Error ? error.message : 'Unknown error');
  }
}

function generateSummary(metrics: any, comparison: any): string {
  let summary = `## Test Baseline Results\n\n`;

  summary += `### Execution Metrics\n`;
  summary += `- **Total Tests**: ${metrics.execution.total_tests}\n`;
  summary += `- **Pass Rate**: ${metrics.execution.pass_rate_percentage.toFixed(2)}%\n`;
  summary += `- **Execution Time**: ${metrics.execution.total_execution_time_ms}ms\n\n`;

  if (metrics.coverage?.available) {
    summary += `### Coverage Metrics\n`;
    summary += `- **Line Coverage**: ${metrics.coverage.overall.line_coverage.toFixed(2)}%\n`;
    summary += `- **Branch Coverage**: ${metrics.coverage.overall.branch_coverage.toFixed(2)}%\n\n`;
  }

  if (comparison) {
    summary += `### Baseline Comparison\n`;
    summary += `- **Overall Result**: ${comparison.summary.overall_result.toUpperCase()}\n`;
    summary += `- **Blocking Issues**: ${comparison.summary.issues_count.blocking}\n`;
    summary += `- **Warnings**: ${comparison.summary.issues_count.non_blocking}\n`;

    if (comparison.improvements.length > 0) {
      summary += `- **Improvements**: ${comparison.improvements.length}\n`;
    }
  }

  return summary;
}

run();
```

## 2. GitLab CI Integration

### GitLab CI Configuration
```yaml
# .gitlab-ci.yml
stages:
  - setup
  - test
  - analyze
  - deploy

variables:
  TBTS_API_URL: $TBTS_API_URL
  TBTS_API_KEY: $TBTS_API_KEY
  TBTS_PROJECT_ID: $TBTS_PROJECT_ID

.tbts_setup: &tbts_setup
  - npm install -g @test-baseline-system/cli
  - tbts init --project-id $TBTS_PROJECT_ID --framework jest
  - export TBTS_TRACKING_ID=$(tbts start-tracking --branch $CI_COMMIT_REF_NAME --commit $CI_COMMIT_SHA --environment $ENVIRONMENT)

test:jest:
  stage: test
  image: node:18
  variables:
    ENVIRONMENT: $CI_COMMIT_REF_NAME == "main" ? "production" : "development"
  before_script:
    - npm ci
    - *tbts_setup
  script:
    - npm test -- --coverage --json --outputFile=test-results.json
  after_script:
    - tbts collect-metrics --test-results test-results.json --coverage coverage/coverage-final.json
    - tbts analyze --gate-type quality_gate --output tbts-analysis.json
  artifacts:
    reports:
      junit: test-results.xml
      coverage_report:
        coverage_format: cobertura
        path: coverage/cobertura-coverage.xml
    paths:
      - tbts-analysis.json
      - test-results.json
      - coverage/
    expire_in: 30 days
  coverage: '/All files[^|]*\|[^|]*\s+([\d\.]+)/'

baseline_check:
  stage: analyze
  image: node:18
  dependencies:
    - test:jest
  script:
    - npm install -g @test-baseline-system/cli
    - |
      GATE_RESULT=$(tbts gate-check --analysis-file tbts-analysis.json --gate-type quality_gate)
      echo "Gate result: $GATE_RESULT"

      if [ "$GATE_RESULT" = "failed" ]; then
        echo "Quality gate failed - see analysis for details"
        exit 1
      elif [ "$GATE_RESULT" = "warning" ]; then
        echo "Quality gate passed with warnings"
        exit 0
      else
        echo "Quality gate passed"
        exit 0
      fi
  only:
    - merge_requests
    - main
    - develop

update_baseline:
  stage: analyze
  image: node:18
  dependencies:
    - test:jest
  script:
    - npm install -g @test-baseline-system/cli
    - tbts update-baseline --analysis-file tbts-analysis.json
  only:
    - main
  when: manual
  allow_failure: false
```

### GitLab Merge Request Integration
```javascript
// gitlab-mr-integration.js
const { GitLabAPI } = require('@gitbeaker/node');

class GitLabMRIntegration {
  constructor(config) {
    this.gitlab = new GitLabAPI({
      token: config.gitlabToken,
      host: config.gitlabHost
    });
    this.projectId = config.projectId;
  }

  async postComparisonComment(mergeRequestIid, comparisonResult) {
    const comment = this.formatComparisonComment(comparisonResult);

    // Check for existing comment and update it
    const existingComments = await this.gitlab.MergeRequestNotes.all(
      this.projectId,
      mergeRequestIid
    );

    const existingComment = existingComments.find(
      note => note.body.includes('<!-- TBTS-COMPARISON-RESULT -->')
    );

    if (existingComment) {
      await this.gitlab.MergeRequestNotes.edit(
        this.projectId,
        mergeRequestIid,
        existingComment.id,
        comment
      );
    } else {
      await this.gitlab.MergeRequestNotes.create(
        this.projectId,
        mergeRequestIid,
        comment
      );
    }
  }

  formatComparisonComment(result) {
    const { summary, detailed_analysis, improvements } = result;

    let comment = `<!-- TBTS-COMPARISON-RESULT -->\n`;
    comment += `## 🧪 Test Baseline Comparison\n\n`;

    // Overall result with emoji
    const resultEmoji = {
      'passed': '✅',
      'passed_with_improvements': '🎉',
      'warning': '⚠️',
      'failed': '❌'
    };

    comment += `**Result**: ${resultEmoji[summary.overall_result] || '❓'} ${summary.overall_result.toUpperCase()}\n\n`;

    // Issues summary
    if (summary.issues_count.blocking > 0) {
      comment += `### 🚫 Blocking Issues (${summary.issues_count.blocking})\n`;
      detailed_analysis.threshold_violations.blocking.forEach(issue => {
        comment += `- **${issue.metric}**: ${issue.message}\n`;
      });
      comment += `\n`;
    }

    if (summary.issues_count.non_blocking > 0) {
      comment += `### ⚠️ Warnings (${summary.issues_count.non_blocking})\n`;
      detailed_analysis.threshold_violations.non_blocking.forEach(issue => {
        comment += `- **${issue.metric}**: ${issue.message}\n`;
      });
      comment += `\n`;
    }

    // Improvements
    if (improvements.length > 0) {
      comment += `### 🎯 Improvements (${improvements.length})\n`;
      improvements.forEach(improvement => {
        comment += `- **${improvement.metric}**: ${improvement.type}\n`;
      });
      comment += `\n`;
    }

    // Metrics table
    comment += `### 📊 Key Metrics\n\n`;
    comment += `| Metric | Current | Baseline | Change |\n`;
    comment += `|--------|---------|----------|--------|\n`;

    const keyMetrics = [
      'execution.pass_rate_percentage',
      'coverage.overall.line_coverage',
      'execution.total_execution_time_ms'
    ];

    keyMetrics.forEach(metricPath => {
      const current = this.getMetricValue(result.raw_data.current_metrics, metricPath);
      const baseline = this.getMetricValue(result.raw_data.baseline_metrics, metricPath);

      if (current !== null && baseline !== null) {
        const change = ((current - baseline) / baseline * 100).toFixed(2);
        const changeEmoji = parseFloat(change) > 0 ? '📈' : parseFloat(change) < 0 ? '📉' : '➡️';

        comment += `| ${metricPath.split('.').pop()} | ${current} | ${baseline} | ${changeEmoji} ${change}% |\n`;
      }
    });

    comment += `\n---\n`;
    comment += `*Updated: ${new Date().toISOString()}*`;

    return comment;
  }

  getMetricValue(metrics, path) {
    return path.split('.').reduce((obj, key) => obj?.[key], metrics);
  }
}
```

## 3. Jenkins Integration

### Jenkins Pipeline Definition
```groovy
// Jenkinsfile
pipeline {
    agent any

    environment {
        TBTS_API_URL = credentials('tbts-api-url')
        TBTS_API_KEY = credentials('tbts-api-key')
        TBTS_PROJECT_ID = credentials('tbts-project-id')
        NODE_VERSION = '18'
    }

    stages {
        stage('Setup') {
            steps {
                script {
                    // Determine environment based on branch
                    env.ENVIRONMENT = env.BRANCH_NAME == 'main' ? 'production' : 'development'
                    env.GATE_TYPE = env.CHANGE_ID ? 'quality_gate' : 'development'
                }

                // Install Node.js
                nodejs(nodeJSInstallationName: "Node ${NODE_VERSION}") {
                    sh 'npm ci'
                    sh 'npm install -g @test-baseline-system/cli'
                }

                // Initialize TBTS tracking
                script {
                    def trackingId = sh(
                        script: """
                            tbts init --project-id ${TBTS_PROJECT_ID} --framework jest
                            tbts start-tracking \\
                                --branch ${BRANCH_NAME} \\
                                --commit ${GIT_COMMIT} \\
                                --environment ${ENVIRONMENT} \\
                                --build-number ${BUILD_NUMBER}
                        """,
                        returnStdout: true
                    ).trim()

                    env.TBTS_TRACKING_ID = trackingId
                }
            }
        }

        stage('Test') {
            steps {
                nodejs(nodeJSInstallationName: "Node ${NODE_VERSION}") {
                    sh '''
                        npm test -- \\
                            --coverage \\
                            --json \\
                            --outputFile=test-results.json \\
                            --testResultsProcessor=jest-sonar-reporter
                    '''
                }
            }
            post {
                always {
                    // Collect test results
                    publishTestResults testResultsFiles: 'test-results.xml'

                    // Collect coverage
                    publishCoverage adapters: [
                        istanbulCoberturaAdapter('coverage/cobertura-coverage.xml')
                    ], sourceFileResolver: sourceFiles('STORE_LAST_BUILD')
                }
            }
        }

        stage('Baseline Analysis') {
            steps {
                script {
                    // Collect and analyze metrics
                    sh '''
                        tbts collect-metrics \\
                            --test-results test-results.json \\
                            --coverage coverage/coverage-final.json

                        tbts analyze \\
                            --gate-type ${GATE_TYPE} \\
                            --output tbts-analysis.json
                    '''

                    // Read analysis results
                    def analysisResult = readJSON file: 'tbts-analysis.json'

                    // Set build description based on results
                    currentBuild.description = "Gate: ${analysisResult.summary.overall_result}"

                    // Archive results
                    archiveArtifacts artifacts: 'tbts-analysis.json,test-results.json,coverage/**', fingerprint: true

                    // Quality gate decision
                    if (analysisResult.summary.overall_result == 'failed') {
                        error("Quality gate failed - see analysis for details")
                    } else if (analysisResult.summary.overall_result == 'warning') {
                        unstable("Quality gate passed with warnings")
                    }
                }
            }
        }

        stage('Update Baseline') {
            when {
                branch 'main'
            }
            steps {
                sh 'tbts update-baseline --analysis-file tbts-analysis.json'
            }
        }
    }

    post {
        always {
            // Cleanup tracking session
            sh 'tbts end-tracking --tracking-id ${TBTS_TRACKING_ID} || true'
        }

        success {
            script {
                if (env.CHANGE_ID) {
                    // Post PR comment for pull requests
                    def analysisResult = readJSON file: 'tbts-analysis.json'
                    postGitHubComment(analysisResult)
                }
            }
        }

        failure {
            emailext (
                subject: "Test Baseline Failure: ${env.JOB_NAME} - ${env.BUILD_NUMBER}",
                body: """
                    Build failed with test baseline issues.

                    Job: ${env.JOB_NAME}
                    Build: ${env.BUILD_NUMBER}
                    Branch: ${env.BRANCH_NAME}

                    Check the build logs for details: ${env.BUILD_URL}
                """,
                to: "${env.CHANGE_AUTHOR_EMAIL}"
            )
        }
    }
}

def postGitHubComment(analysisResult) {
    def comment = generateMarkdownComment(analysisResult)

    // Use GitHub API to post comment
    withCredentials([string(credentialsId: 'github-token', variable: 'GITHUB_TOKEN')]) {
        sh """
            curl -X POST \\
                -H "Authorization: token ${GITHUB_TOKEN}" \\
                -H "Content-Type: application/json" \\
                -d '{"body": "${comment.replace('\n', '\\n').replace('"', '\\"')}"}' \\
                https://api.github.com/repos/${env.CHANGE_TARGET}/issues/${env.CHANGE_ID}/comments
        """
    }
}
```

### Jenkins Plugin Development
```java
// TestBaselineTrackingPlugin.java
@Extension
public class TestBaselineTrackingBuilder extends Builder implements SimpleBuildStep {

    private final String apiUrl;
    private final String apiKey;
    private final String projectId;
    private final String framework;
    private final String gateType;

    @DataBoundConstructor
    public TestBaselineTrackingBuilder(String apiUrl, String apiKey, String projectId,
                                      String framework, String gateType) {
        this.apiUrl = apiUrl;
        this.apiKey = apiKey;
        this.projectId = projectId;
        this.framework = framework;
        this.gateType = gateType;
    }

    @Override
    public void perform(Run<?, ?> run, FilePath workspace, Launcher launcher,
                       TaskListener listener) throws InterruptedException, IOException {

        PrintStream logger = listener.getLogger();
        logger.println("Starting Test Baseline Tracking analysis...");

        try {
            // Initialize TBTS client
            TBTSClient client = new TBTSClient(apiUrl, apiKey);

            // Create tracking context
            TrackingContext context = new TrackingContext.Builder()
                .project(projectId)
                .branch(getBranchName(run))
                .commit(getCommitHash(run))
                .buildNumber(String.valueOf(run.getNumber()))
                .framework(framework)
                .build();

            // Start tracking
            String trackingId = client.startTracking(context);

            // Collect metrics from workspace files
            Map<String, Object> metrics = collectMetrics(workspace, framework, logger);

            // Submit metrics
            client.submitMetrics(trackingId, metrics);

            // Perform analysis
            AnalysisResult result = client.analyzeWithBaseline(trackingId, gateType);

            // Save results
            saveResultsToWorkspace(workspace, result);

            // Update build result based on gate decision
            updateBuildResult(run, result, logger);

            logger.println("Test Baseline Tracking completed successfully");

        } catch (Exception e) {
            logger.println("Test Baseline Tracking failed: " + e.getMessage());
            throw new IOException("TBTS analysis failed", e);
        }
    }

    private void updateBuildResult(Run<?, ?> run, AnalysisResult result, PrintStream logger) {
        switch (result.getSummary().getOverallResult()) {
            case "failed":
                run.setResult(Result.FAILURE);
                logger.println("Quality gate FAILED - build marked as failure");
                break;
            case "warning":
                run.setResult(Result.UNSTABLE);
                logger.println("Quality gate passed with WARNINGS - build marked as unstable");
                break;
            case "passed":
            case "passed_with_improvements":
                logger.println("Quality gate PASSED");
                break;
        }
    }

    @Symbol("testBaselineTracking")
    @Extension
    public static final class DescriptorImpl extends BuildStepDescriptor<Builder> {

        @Override
        public boolean isApplicable(Class<? extends AbstractProject> aClass) {
            return true;
        }

        @Override
        public String getDisplayName() {
            return "Test Baseline Tracking Analysis";
        }

        public FormValidation doCheckApiUrl(@QueryParameter String value) {
            if (Util.fixEmptyAndTrim(value) == null) {
                return FormValidation.error("API URL is required");
            }
            try {
                new URL(value);
                return FormValidation.ok();
            } catch (MalformedURLException e) {
                return FormValidation.error("Invalid URL format");
            }
        }
    }
}
```

## 4. Azure DevOps Integration

### Azure Pipeline Definition
```yaml
# azure-pipelines.yml
trigger:
  branches:
    include:
      - main
      - develop
      - feature/*

pr:
  branches:
    include:
      - main
      - develop

variables:
  - group: test-baseline-system
  - name: nodeVersion
    value: '18.x'

stages:
- stage: Test
  displayName: 'Test and Analysis'
  jobs:
  - job: TestWithBaseline
    displayName: 'Test with Baseline Tracking'
    pool:
      vmImage: 'ubuntu-latest'

    steps:
    - task: NodeTool@0
      inputs:
        versionSpec: $(nodeVersion)
      displayName: 'Install Node.js'

    - script: |
        npm ci
        npm install -g @test-baseline-system/cli
      displayName: 'Install dependencies'

    - script: |
        tbts init --project-id $(TBTS_PROJECT_ID) --framework jest

        # Determine environment
        if [ "$(Build.SourceBranch)" = "refs/heads/main" ]; then
          ENVIRONMENT="production"
        else
          ENVIRONMENT="development"
        fi

        # Start tracking
        TRACKING_ID=$(tbts start-tracking \
          --branch $(Build.SourceBranchName) \
          --commit $(Build.SourceVersion) \
          --environment $ENVIRONMENT \
          --build-number $(Build.BuildNumber))

        echo "##vso[task.setvariable variable=TBTS_TRACKING_ID]$TRACKING_ID"
        echo "##vso[task.setvariable variable=ENVIRONMENT]$ENVIRONMENT"
      displayName: 'Initialize Test Baseline Tracking'
      env:
        TBTS_API_URL: $(TBTS_API_URL)
        TBTS_API_KEY: $(TBTS_API_KEY)

    - script: |
        npm test -- --coverage --json --outputFile=$(Agent.TempDirectory)/test-results.json
      displayName: 'Run tests'
      continueOnError: true

    - script: |
        tbts collect-metrics \
          --test-results $(Agent.TempDirectory)/test-results.json \
          --coverage coverage/coverage-final.json

        # Determine gate type
        if [ "$(Build.Reason)" = "PullRequest" ]; then
          GATE_TYPE="quality_gate"
        else
          GATE_TYPE="development"
        fi

        tbts analyze \
          --gate-type $GATE_TYPE \
          --output $(Agent.TempDirectory)/tbts-analysis.json

        echo "##vso[task.setvariable variable=GATE_TYPE]$GATE_TYPE"
      displayName: 'Analyze metrics'
      env:
        TBTS_API_URL: $(TBTS_API_URL)
        TBTS_API_KEY: $(TBTS_API_KEY)

    - task: PublishTestResults@2
      inputs:
        testResultsFormat: 'JUnit'
        testResultsFiles: '$(Agent.TempDirectory)/test-results.xml'
        mergeTestResults: true
      displayName: 'Publish test results'
      condition: always()

    - task: PublishCodeCoverageResults@1
      inputs:
        codeCoverageTool: 'Cobertura'
        summaryFileLocation: 'coverage/cobertura-coverage.xml'
      displayName: 'Publish coverage results'
      condition: always()

    - script: |
        GATE_RESULT=$(tbts gate-check --analysis-file $(Agent.TempDirectory)/tbts-analysis.json --gate-type $(GATE_TYPE))
        echo "Gate result: $GATE_RESULT"

        if [ "$GATE_RESULT" = "failed" ]; then
          echo "##vso[task.logissue type=error]Quality gate failed"
          echo "##vso[task.complete result=Failed;]Quality gate failed - see analysis for details"
        elif [ "$GATE_RESULT" = "warning" ]; then
          echo "##vso[task.logissue type=warning]Quality gate passed with warnings"
          echo "##vso[task.complete result=SucceededWithIssues;]Quality gate passed with warnings"
        else
          echo "Quality gate passed"
        fi
      displayName: 'Quality gate check'
      condition: and(succeeded(), eq(variables['Build.Reason'], 'PullRequest'))

    - script: |
        tbts update-baseline --analysis-file $(Agent.TempDirectory)/tbts-analysis.json
      displayName: 'Update baseline'
      condition: and(succeeded(), eq(variables['Build.SourceBranch'], 'refs/heads/main'))

    - task: PublishBuildArtifacts@1
      inputs:
        pathToPublish: '$(Agent.TempDirectory)/tbts-analysis.json'
        artifactName: 'baseline-analysis'
      displayName: 'Publish analysis results'
      condition: always()

    - script: |
        tbts end-tracking --tracking-id $(TBTS_TRACKING_ID)
      displayName: 'Cleanup tracking'
      condition: always()
```

This comprehensive CI/CD integration provides seamless automation across major platforms while maintaining flexibility for custom workflows and requirements.