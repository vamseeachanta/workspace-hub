/**
 * Performance Profiler
 *
 * Comprehensive performance monitoring for test execution including
 * memory usage tracking, CPU profiling, test duration analysis, and resource leak detection.
 */

const EventEmitter = require('events');
const path = require('path');
const fs = require('fs').promises;
const { performance, PerformanceObserver } = require('perf_hooks');
const v8 = require('v8');

class PerformanceProfiler extends EventEmitter {
  constructor(options = {}) {
    super();
    this.options = {
      rootDir: process.cwd(),
      outputDir: '.test-baseline/profiling',
      enableMemoryTracking: true,
      enableCpuProfiling: false,
      enableGcTracking: true,
      enableTimingTracking: true,
      enableResourceTracking: true,
      memoryInterval: 100, // ms
      cpuSampleRate: 1000, // Hz
      detectLeaks: true,
      trackAsyncOps: true,
      ...options
    };

    this.isRunning = false;
    this.startTime = null;
    this.endTime = null;
    this.profiles = {
      memory: [],
      cpu: [],
      timing: [],
      gc: [],
      resources: [],
      leaks: []
    };

    this.observers = new Map();
    this.intervals = new Map();
    this.resourceCounters = new Map();
    this.asyncOps = new Map();
    this.heapSnapshots = [];
  }

  /**
   * Initialize the profiler
   * @returns {Promise<void>}
   */
  async initialize() {
    this.emit('initialization', { status: 'started' });

    try {
      await this._setupOutputDirectory();
      await this._setupObservers();

      this.emit('initialization', { status: 'completed' });
    } catch (error) {
      this.emit('initialization', { status: 'failed', error: error.message });
      throw error;
    }
  }

  /**
   * Start profiling
   * @returns {Promise<void>}
   */
  async startProfiling() {
    if (this.isRunning) {
      throw new Error('Profiler is already running');
    }

    this.isRunning = true;
    this.startTime = performance.now();

    this.emit('profilingStarted', { timestamp: this.startTime });

    try {
      if (this.options.enableMemoryTracking) {
        await this._startMemoryTracking();
      }

      if (this.options.enableCpuProfiling) {
        await this._startCpuProfiling();
      }

      if (this.options.enableGcTracking) {
        await this._startGcTracking();
      }

      if (this.options.enableTimingTracking) {
        await this._startTimingTracking();
      }

      if (this.options.enableResourceTracking) {
        await this._startResourceTracking();
      }

      // Take initial heap snapshot
      if (this.options.detectLeaks) {
        await this._takeHeapSnapshot('start');
      }
    } catch (error) {
      this.isRunning = false;
      throw error;
    }
  }

  /**
   * Stop profiling and generate reports
   * @returns {Promise<Object>}
   */
  async stopProfiling() {
    if (!this.isRunning) {
      throw new Error('Profiler is not running');
    }

    this.endTime = performance.now();
    this.isRunning = false;

    this.emit('profilingStopped', { timestamp: this.endTime });

    try {
      // Stop all tracking
      await this._stopAllTracking();

      // Take final heap snapshot
      if (this.options.detectLeaks) {
        await this._takeHeapSnapshot('end');
        await this._analyzeMemoryLeaks();
      }

      // Generate comprehensive report
      const report = await this._generateReport();

      this.emit('reportGenerated', { report });

      return report;
    } catch (error) {
      this.emit('profilingError', { error: error.message });
      throw error;
    }
  }

  /**
   * Mark the start of a test
   * @param {string} testName - Test name
   * @param {Object} metadata - Additional test metadata
   */
  markTestStart(testName, metadata = {}) {
    if (!this.isRunning) return;

    const timestamp = performance.now();
    const memoryUsage = process.memoryUsage();

    const testMarker = {
      name: testName,
      type: 'test-start',
      timestamp,
      memory: memoryUsage,
      metadata
    };

    this.profiles.timing.push(testMarker);
    this.emit('testStarted', testMarker);
  }

  /**
   * Mark the end of a test
   * @param {string} testName - Test name
   * @param {Object} result - Test result
   */
  markTestEnd(testName, result = {}) {
    if (!this.isRunning) return;

    const timestamp = performance.now();
    const memoryUsage = process.memoryUsage();

    // Find corresponding start marker
    const startMarker = [...this.profiles.timing]
      .reverse()
      .find(marker => marker.name === testName && marker.type === 'test-start');

    const duration = startMarker ? timestamp - startMarker.timestamp : 0;

    const testMarker = {
      name: testName,
      type: 'test-end',
      timestamp,
      duration,
      memory: memoryUsage,
      memoryDelta: startMarker ? {
        rss: memoryUsage.rss - startMarker.memory.rss,
        heapUsed: memoryUsage.heapUsed - startMarker.memory.heapUsed,
        heapTotal: memoryUsage.heapTotal - startMarker.memory.heapTotal,
        external: memoryUsage.external - startMarker.memory.external
      } : null,
      result
    };

    this.profiles.timing.push(testMarker);
    this.emit('testCompleted', testMarker);
  }

  /**
   * Get current performance metrics
   * @returns {Object}
   */
  getCurrentMetrics() {
    if (!this.isRunning) {
      return null;
    }

    const currentTime = performance.now();
    const memoryUsage = process.memoryUsage();
    const heapStats = v8.getHeapStatistics();

    return {
      timestamp: currentTime,
      uptime: currentTime - this.startTime,
      memory: {
        process: memoryUsage,
        heap: heapStats,
        usage: {
          heapUsed: (heapStats.used_heap_size / heapStats.heap_size_limit) * 100,
          external: memoryUsage.external
        }
      },
      gc: this._getGcStats(),
      resources: this._getResourceStats()
    };
  }

  /**
   * Analyze performance bottlenecks
   * @returns {Object}
   */
  analyzeBottlenecks() {
    const analysis = {
      slowTests: [],
      memoryIntensive: [],
      gcPressure: [],
      resourceLeaks: [],
      recommendations: []
    };

    // Analyze slow tests
    const testTimings = this.profiles.timing
      .filter(marker => marker.type === 'test-end')
      .sort((a, b) => b.duration - a.duration);

    analysis.slowTests = testTimings.slice(0, 10).map(test => ({
      name: test.name,
      duration: test.duration,
      memoryDelta: test.memoryDelta
    }));

    // Analyze memory-intensive tests
    analysis.memoryIntensive = testTimings
      .filter(test => test.memoryDelta && test.memoryDelta.heapUsed > 10 * 1024 * 1024) // > 10MB
      .slice(0, 10)
      .map(test => ({
        name: test.name,
        memoryDelta: test.memoryDelta,
        duration: test.duration
      }));

    // Analyze GC pressure
    const gcEvents = this.profiles.gc.filter(event => event.kind === 'major');
    if (gcEvents.length > 0) {
      const avgGcTime = gcEvents.reduce((sum, event) => sum + event.duration, 0) / gcEvents.length;
      if (avgGcTime > 50) { // > 50ms average GC time
        analysis.gcPressure.push({
          averageGcTime: avgGcTime,
          majorGcCount: gcEvents.length,
          recommendation: 'High GC pressure detected. Consider reducing object allocations.'
        });
      }
    }

    // Generate recommendations
    analysis.recommendations = this._generateRecommendations(analysis);

    return analysis;
  }

  // Private methods

  async _setupOutputDirectory() {
    const outputDir = path.join(this.options.rootDir, this.options.outputDir);
    await fs.mkdir(outputDir, { recursive: true });

    // Create subdirectories
    const subdirs = ['memory', 'cpu', 'timing', 'gc', 'heap-snapshots'];
    for (const subdir of subdirs) {
      await fs.mkdir(path.join(outputDir, subdir), { recursive: true });
    }
  }

  async _setupObservers() {
    // Performance observer for various metrics
    if (this.options.enableTimingTracking) {
      const obs = new PerformanceObserver((list) => {
        for (const entry of list.getEntries()) {
          this.profiles.timing.push({
            name: entry.name,
            type: entry.entryType,
            timestamp: entry.startTime,
            duration: entry.duration,
            detail: entry.detail || null
          });
        }
      });

      obs.observe({ entryTypes: ['measure', 'mark', 'navigation', 'resource'] });
      this.observers.set('timing', obs);
    }

    // GC observer
    if (this.options.enableGcTracking) {
      const obs = new PerformanceObserver((list) => {
        for (const entry of list.getEntries()) {
          this.profiles.gc.push({
            timestamp: entry.startTime,
            duration: entry.duration,
            kind: entry.detail?.kind || 'unknown',
            flags: entry.detail?.flags || []
          });
        }
      });

      obs.observe({ entryTypes: ['gc'] });
      this.observers.set('gc', obs);
    }
  }

  async _startMemoryTracking() {
    const interval = setInterval(() => {
      const memoryUsage = process.memoryUsage();
      const heapStats = v8.getHeapStatistics();

      this.profiles.memory.push({
        timestamp: performance.now(),
        process: memoryUsage,
        heap: heapStats
      });
    }, this.options.memoryInterval);

    this.intervals.set('memory', interval);
  }

  async _startCpuProfiling() {
    if (v8.startProfiling) {
      v8.startProfiling('test-profile', true);
    }
  }

  async _startGcTracking() {
    // GC tracking is handled by the observer
    if (global.gc) {
      // Force garbage collection to get baseline
      global.gc();
    }
  }

  async _startTimingTracking() {
    // Timing tracking is handled by the observer
    performance.mark('profiling-start');
  }

  async _startResourceTracking() {
    // Track various resource usage
    const interval = setInterval(() => {
      const resourceUsage = process.resourceUsage();

      this.profiles.resources.push({
        timestamp: performance.now(),
        userCPUTime: resourceUsage.userCPUTime,
        systemCPUTime: resourceUsage.systemCPUTime,
        maxRSS: resourceUsage.maxRSS,
        sharedMemorySize: resourceUsage.sharedMemorySize,
        unsharedDataSize: resourceUsage.unsharedDataSize,
        unsharedStackSize: resourceUsage.unsharedStackSize,
        minorPageFault: resourceUsage.minorPageFault,
        majorPageFault: resourceUsage.majorPageFault,
        swappedOut: resourceUsage.swappedOut,
        fsRead: resourceUsage.fsRead,
        fsWrite: resourceUsage.fsWrite,
        ipcSent: resourceUsage.ipcSent,
        ipcReceived: resourceUsage.ipcReceived,
        signalsCount: resourceUsage.signalsCount,
        voluntaryContextSwitches: resourceUsage.voluntaryContextSwitches,
        involuntaryContextSwitches: resourceUsage.involuntaryContextSwitches
      });
    }, this.options.memoryInterval * 2); // Sample less frequently

    this.intervals.set('resources', interval);
  }

  async _stopAllTracking() {
    // Stop all intervals
    for (const [name, interval] of this.intervals) {
      clearInterval(interval);
    }
    this.intervals.clear();

    // Disconnect observers
    for (const [name, observer] of this.observers) {
      observer.disconnect();
    }
    this.observers.clear();

    // Stop CPU profiling
    if (v8.stopProfiling && this.options.enableCpuProfiling) {
      const profile = v8.stopProfiling('test-profile');
      if (profile) {
        this.profiles.cpu.push(profile);
      }
    }

    performance.mark('profiling-end');
    performance.measure('total-profiling-time', 'profiling-start', 'profiling-end');
  }

  async _takeHeapSnapshot(label) {
    if (!v8.writeHeapSnapshot) return;

    try {
      const snapshotPath = path.join(
        this.options.rootDir,
        this.options.outputDir,
        'heap-snapshots',
        `${label}-${Date.now()}.heapsnapshot`
      );

      v8.writeHeapSnapshot(snapshotPath);
      this.heapSnapshots.push({ label, path: snapshotPath, timestamp: performance.now() });

      this.emit('heapSnapshotTaken', { label, path: snapshotPath });
    } catch (error) {
      this.emit('heapSnapshotError', { label, error: error.message });
    }
  }

  async _analyzeMemoryLeaks() {
    if (this.heapSnapshots.length < 2) return;

    const startSnapshot = this.heapSnapshots.find(s => s.label === 'start');
    const endSnapshot = this.heapSnapshots.find(s => s.label === 'end');

    if (!startSnapshot || !endSnapshot) return;

    // Basic memory leak detection
    const memoryIncrease = this.profiles.memory.length > 1 ?
      this.profiles.memory[this.profiles.memory.length - 1].process.heapUsed -
      this.profiles.memory[0].process.heapUsed : 0;

    if (memoryIncrease > 50 * 1024 * 1024) { // > 50MB increase
      this.profiles.leaks.push({
        type: 'memory-growth',
        increase: memoryIncrease,
        description: `Heap usage increased by ${(memoryIncrease / 1024 / 1024).toFixed(2)}MB during test run`,
        snapshots: [startSnapshot.path, endSnapshot.path]
      });
    }

    // Analyze GC efficiency
    const gcEvents = this.profiles.gc;
    if (gcEvents.length > 0) {
      const majorGcEvents = gcEvents.filter(event => event.kind === 'major');
      const avgGcTime = majorGcEvents.reduce((sum, event) => sum + event.duration, 0) / majorGcEvents.length;

      if (avgGcTime > 100) { // > 100ms average major GC
        this.profiles.leaks.push({
          type: 'gc-pressure',
          averageGcTime: avgGcTime,
          majorGcCount: majorGcEvents.length,
          description: `High GC pressure detected. Average major GC time: ${avgGcTime.toFixed(2)}ms`
        });
      }
    }
  }

  async _generateReport() {
    const report = {
      summary: {
        startTime: this.startTime,
        endTime: this.endTime,
        duration: this.endTime - this.startTime,
        framework: 'unified'
      },
      memory: this._analyzeMemoryProfile(),
      timing: this._analyzeTimingProfile(),
      gc: this._analyzeGcProfile(),
      resources: this._analyzeResourceProfile(),
      leaks: this.profiles.leaks,
      bottlenecks: this.analyzeBottlenecks(),
      recommendations: []
    };

    // Save detailed profiles
    await this._saveProfiles();

    // Save report
    const reportPath = path.join(
      this.options.rootDir,
      this.options.outputDir,
      'performance-report.json'
    );

    await fs.writeFile(reportPath, JSON.stringify(report, null, 2));

    return report;
  }

  _analyzeMemoryProfile() {
    if (this.profiles.memory.length === 0) return null;

    const memoryData = this.profiles.memory;
    const startMemory = memoryData[0];
    const endMemory = memoryData[memoryData.length - 1];

    return {
      initial: startMemory.process,
      final: endMemory.process,
      peak: {
        heapUsed: Math.max(...memoryData.map(m => m.process.heapUsed)),
        heapTotal: Math.max(...memoryData.map(m => m.process.heapTotal)),
        rss: Math.max(...memoryData.map(m => m.process.rss)),
        external: Math.max(...memoryData.map(m => m.process.external))
      },
      growth: {
        heapUsed: endMemory.process.heapUsed - startMemory.process.heapUsed,
        heapTotal: endMemory.process.heapTotal - startMemory.process.heapTotal,
        rss: endMemory.process.rss - startMemory.process.rss,
        external: endMemory.process.external - startMemory.process.external
      },
      samples: memoryData.length
    };
  }

  _analyzeTimingProfile() {
    const testEvents = this.profiles.timing.filter(event => event.type === 'test-end');

    if (testEvents.length === 0) return null;

    const durations = testEvents.map(test => test.duration);

    return {
      totalTests: testEvents.length,
      totalDuration: durations.reduce((sum, duration) => sum + duration, 0),
      averageDuration: durations.reduce((sum, duration) => sum + duration, 0) / durations.length,
      medianDuration: this._calculateMedian(durations),
      minDuration: Math.min(...durations),
      maxDuration: Math.max(...durations),
      slowestTests: testEvents
        .sort((a, b) => b.duration - a.duration)
        .slice(0, 5)
        .map(test => ({ name: test.name, duration: test.duration }))
    };
  }

  _analyzeGcProfile() {
    if (this.profiles.gc.length === 0) return null;

    const gcEvents = this.profiles.gc;
    const majorGcEvents = gcEvents.filter(event => event.kind === 'major');
    const minorGcEvents = gcEvents.filter(event => event.kind === 'minor');

    return {
      totalEvents: gcEvents.length,
      majorGcEvents: majorGcEvents.length,
      minorGcEvents: minorGcEvents.length,
      totalGcTime: gcEvents.reduce((sum, event) => sum + event.duration, 0),
      averageMajorGcTime: majorGcEvents.length > 0 ?
        majorGcEvents.reduce((sum, event) => sum + event.duration, 0) / majorGcEvents.length : 0,
      averageMinorGcTime: minorGcEvents.length > 0 ?
        minorGcEvents.reduce((sum, event) => sum + event.duration, 0) / minorGcEvents.length : 0,
      longestGc: Math.max(...gcEvents.map(event => event.duration), 0)
    };
  }

  _analyzeResourceProfile() {
    if (this.profiles.resources.length === 0) return null;

    const resourceData = this.profiles.resources;
    const startResource = resourceData[0];
    const endResource = resourceData[resourceData.length - 1];

    return {
      cpuTime: {
        user: endResource.userCPUTime - startResource.userCPUTime,
        system: endResource.systemCPUTime - startResource.systemCPUTime
      },
      memory: {
        maxRSS: Math.max(...resourceData.map(r => r.maxRSS))
      },
      io: {
        reads: endResource.fsRead - startResource.fsRead,
        writes: endResource.fsWrite - startResource.fsWrite
      },
      contextSwitches: {
        voluntary: endResource.voluntaryContextSwitches - startResource.voluntaryContextSwitches,
        involuntary: endResource.involuntaryContextSwitches - startResource.involuntaryContextSwitches
      },
      pageFaults: {
        minor: endResource.minorPageFault - startResource.minorPageFault,
        major: endResource.majorPageFault - startResource.majorPageFault
      }
    };
  }

  _getGcStats() {
    const gcEvents = this.profiles.gc;
    const recentGc = gcEvents.slice(-10); // Last 10 GC events

    return {
      recentEvents: recentGc.length,
      recentTotalTime: recentGc.reduce((sum, event) => sum + event.duration, 0),
      lastMajorGc: gcEvents.filter(event => event.kind === 'major').slice(-1)[0] || null
    };
  }

  _getResourceStats() {
    const resourceData = this.profiles.resources;
    if (resourceData.length === 0) return null;

    const latest = resourceData[resourceData.length - 1];
    return {
      cpuTime: {
        user: latest.userCPUTime,
        system: latest.systemCPUTime
      },
      memory: latest.maxRSS,
      io: {
        reads: latest.fsRead,
        writes: latest.fsWrite
      }
    };
  }

  _calculateMedian(values) {
    const sorted = [...values].sort((a, b) => a - b);
    const middle = Math.floor(sorted.length / 2);

    if (sorted.length % 2 === 0) {
      return (sorted[middle - 1] + sorted[middle]) / 2;
    } else {
      return sorted[middle];
    }
  }

  _generateRecommendations(analysis) {
    const recommendations = [];

    // Memory recommendations
    if (analysis.memoryIntensive.length > 0) {
      recommendations.push({
        type: 'memory',
        severity: 'medium',
        message: `${analysis.memoryIntensive.length} tests are using significant memory. Consider optimizing data structures or mocking large objects.`,
        tests: analysis.memoryIntensive.map(t => t.name)
      });
    }

    // Performance recommendations
    if (analysis.slowTests.length > 0) {
      const slowThreshold = 5000; // 5 seconds
      const verySlow = analysis.slowTests.filter(t => t.duration > slowThreshold);

      if (verySlow.length > 0) {
        recommendations.push({
          type: 'performance',
          severity: 'high',
          message: `${verySlow.length} tests are taking longer than ${slowThreshold}ms. Consider optimizing or parallelizing these tests.`,
          tests: verySlow.map(t => t.name)
        });
      }
    }

    // GC recommendations
    if (analysis.gcPressure.length > 0) {
      recommendations.push({
        type: 'gc',
        severity: 'medium',
        message: 'High garbage collection pressure detected. Consider reducing object allocations and reusing objects where possible.',
        details: analysis.gcPressure
      });
    }

    return recommendations;
  }

  async _saveProfiles() {
    const outputDir = path.join(this.options.rootDir, this.options.outputDir);

    // Save individual profile data
    for (const [profileType, data] of Object.entries(this.profiles)) {
      if (data.length > 0) {
        const profilePath = path.join(outputDir, `${profileType}-profile.json`);
        await fs.writeFile(profilePath, JSON.stringify(data, null, 2));
      }
    }
  }
}

module.exports = PerformanceProfiler;