import { Router } from 'express';
import { TestController } from './controllers/test-controller';
import { CoverageController } from './controllers/coverage-controller';
import { MetricsController } from './controllers/metrics-controller';
import { AlertController } from './controllers/alert-controller';
import { DashboardController } from './controllers/dashboard-controller';

const router = Router();

// Test routes
const testController = new TestController();
router.get('/tests', testController.getTests.bind(testController));
router.post('/tests', testController.createTest.bind(testController));
router.get('/tests/:id', testController.getTest.bind(testController));
router.put('/tests/:id', testController.updateTest.bind(testController));
router.delete('/tests/:id', testController.deleteTest.bind(testController));
router.get('/tests/suite/:suite', testController.getTestsBySuite.bind(testController));
router.get('/tests/status/:status', testController.getTestsByStatus.bind(testController));

// Coverage routes
const coverageController = new CoverageController();
router.get('/coverage', coverageController.getCoverage.bind(coverageController));
router.post('/coverage', coverageController.uploadCoverage.bind(coverageController));
router.get('/coverage/summary', coverageController.getCoverageSummary.bind(coverageController));
router.get('/coverage/file/:file', coverageController.getFileCoverage.bind(coverageController));
router.get('/coverage/trends', coverageController.getCoverageTrends.bind(coverageController));

// Metrics routes
const metricsController = new MetricsController();
router.get('/metrics', metricsController.getMetrics.bind(metricsController));
router.post('/metrics', metricsController.recordMetric.bind(metricsController));
router.get('/metrics/:type', metricsController.getMetricsByType.bind(metricsController));
router.get('/metrics/trends/:type', metricsController.getMetricTrends.bind(metricsController));
router.get('/metrics/performance', metricsController.getPerformanceMetrics.bind(metricsController));

// Alert routes
const alertController = new AlertController();
router.get('/alerts', alertController.getAlerts.bind(alertController));
router.post('/alerts', alertController.createAlert.bind(alertController));
router.get('/alerts/:id', alertController.getAlert.bind(alertController));
router.put('/alerts/:id/resolve', alertController.resolveAlert.bind(alertController));
router.delete('/alerts/:id', alertController.deleteAlert.bind(alertController));
router.get('/alerts/severity/:severity', alertController.getAlertsBySeverity.bind(alertController));

// Dashboard routes
const dashboardController = new DashboardController();
router.get('/dashboard/summary', dashboardController.getDashboardSummary.bind(dashboardController));
router.get('/dashboard/config', dashboardController.getDashboardConfig.bind(dashboardController));
router.post('/dashboard/config', dashboardController.saveDashboardConfig.bind(dashboardController));
router.get('/dashboard/trends', dashboardController.getTrends.bind(dashboardController));
router.get('/dashboard/realtime', dashboardController.getRealtimeData.bind(dashboardController));

export { router as apiRoutes };