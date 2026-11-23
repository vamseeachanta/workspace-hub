/**
 * Mutation Testing Helpers
 * Utilities for analyzing and improving mutation test results
 */

class MutationAnalyzer {
  constructor(mutationReport) {
    this.report = mutationReport;
  }

  /**
   * Analyze mutation testing results
   */
  analyze() {
    return {
      summary: this.generateSummary(),
      weakAreas: this.identifyWeakAreas(),
      suggestions: this.generateSuggestions(),
      trends: this.analyzeTrends()
    };
  }

  /**
   * Generate summary statistics
   */
  generateSummary() {
    const { files } = this.report;
    
    const totalMutants = files.reduce((sum, file) => sum + file.mutants.length, 0);
    const killedMutants = files.reduce((sum, file) => 
      sum + file.mutants.filter(m => m.status === 'Killed').length, 0);
    const survivedMutants = files.reduce((sum, file) => 
      sum + file.mutants.filter(m => m.status === 'Survived').length, 0);
    const timedOutMutants = files.reduce((sum, file) => 
      sum + file.mutants.filter(m => m.status === 'TimedOut').length, 0);
    const noCoverageMutants = files.reduce((sum, file) => 
      sum + file.mutants.filter(m => m.status === 'NoCoverage').length, 0);
    
    const mutationScore = totalMutants > 0 ? (killedMutants / totalMutants) * 100 : 0;
    
    return {
      totalMutants,
      killedMutants,
      survivedMutants,
      timedOutMutants,
      noCoverageMutants,
      mutationScore: Math.round(mutationScore * 100) / 100,
      testStrength: this.calculateTestStrength(killedMutants, totalMutants)
    };
  }

  /**
   * Identify areas with weak mutation testing
   */
  identifyWeakAreas() {
    const { files } = this.report;
    const weakFiles = [];
    
    files.forEach(file => {
      const totalMutants = file.mutants.length;
      const killedMutants = file.mutants.filter(m => m.status === 'Killed').length;
      const mutationScore = totalMutants > 0 ? (killedMutants / totalMutants) * 100 : 0;
      
      if (mutationScore < 80) {
        const survivedMutants = file.mutants.filter(m => m.status === 'Survived');
        
        weakFiles.push({
          file: file.source,
          mutationScore,
          totalMutants,
          survivedMutants: survivedMutants.length,
          problematicMutations: this.analyzeSurvivedMutants(survivedMutants),
          recommendations: this.generateFileRecommendations(file)
        });
      }
    });
    
    return weakFiles.sort((a, b) => a.mutationScore - b.mutationScore);
  }

  /**
   * Analyze survived mutants to understand test weaknesses
   */
  analyzeSurvivedMutants(survivedMutants) {
    const mutationTypes = {};
    const locations = [];
    
    survivedMutants.forEach(mutant => {
      // Group by mutation type
      if (!mutationTypes[mutant.mutatorName]) {
        mutationTypes[mutant.mutatorName] = [];
      }
      mutationTypes[mutant.mutatorName].push(mutant);
      
      // Track locations
      locations.push({
        line: mutant.location.start.line,
        column: mutant.location.start.column,
        originalCode: mutant.originalLines,
        mutatedCode: mutant.mutatedLines,
        mutator: mutant.mutatorName
      });
    });
    
    return {
      byType: Object.keys(mutationTypes).map(type => ({
        type,
        count: mutationTypes[type].length,
        examples: mutationTypes[type].slice(0, 3)
      })),
      locations: locations.slice(0, 10), // Top 10 problematic locations
      patterns: this.identifyPatterns(survivedMutants)
    };
  }

  /**
   * Identify patterns in survived mutants
   */
  identifyPatterns(survivedMutants) {
    const patterns = [];
    
    // Check for error handling patterns
    const errorHandlingMutants = survivedMutants.filter(m => 
      m.originalLines.includes('throw') || 
      m.originalLines.includes('catch') ||
      m.originalLines.includes('Error')
    );
    
    if (errorHandlingMutants.length > 0) {
      patterns.push({
        type: 'error_handling',
        description: 'Error handling code is not properly tested',
        count: errorHandlingMutants.length,
        recommendation: 'Add tests that verify error conditions and exception handling'
      });
    }
    
    // Check for boundary condition patterns
    const boundaryMutants = survivedMutants.filter(m => 
      m.mutatorName === 'ConditionalExpression' ||
      m.mutatorName === 'EqualityOperator'
    );
    
    if (boundaryMutants.length > 0) {
      patterns.push({
        type: 'boundary_conditions',
        description: 'Boundary conditions and edge cases are not thoroughly tested',
        count: boundaryMutants.length,
        recommendation: 'Add tests for edge cases, null values, and boundary conditions'
      });
    }
    
    // Check for arithmetic patterns
    const arithmeticMutants = survivedMutants.filter(m => 
      m.mutatorName === 'ArithmeticOperator'
    );
    
    if (arithmeticMutants.length > 0) {
      patterns.push({
        type: 'arithmetic_operations',
        description: 'Arithmetic operations are not properly validated',
        count: arithmeticMutants.length,
        recommendation: 'Add tests that verify calculation results and mathematical operations'
      });
    }
    
    return patterns;
  }

  /**
   * Generate recommendations for improving mutation score
   */
  generateSuggestions() {
    const suggestions = [];
    const summary = this.generateSummary();
    
    if (summary.mutationScore < 70) {
      suggestions.push({
        priority: 'high',
        category: 'test_coverage',
        title: 'Critical: Low Mutation Score',
        description: `Mutation score of ${summary.mutationScore}% is below acceptable threshold`,
        actions: [
          'Review and improve test coverage for core functionality',
          'Add tests for error conditions and edge cases',
          'Verify that tests actually validate expected behavior'
        ]
      });
    }
    
    if (summary.noCoverageMutants > summary.totalMutants * 0.1) {
      suggestions.push({
        priority: 'high',
        category: 'code_coverage',
        title: 'High Number of Uncovered Code',
        description: `${summary.noCoverageMutants} mutants have no test coverage`,
        actions: [
          'Increase line and branch coverage',
          'Add tests for unused code paths',
          'Remove dead code if not needed'
        ]
      });
    }
    
    if (summary.survivedMutants > summary.totalMutants * 0.2) {
      suggestions.push({
        priority: 'medium',
        category: 'test_quality',
        title: 'Many Mutants Survived',
        description: `${summary.survivedMutants} mutants survived testing`,
        actions: [
          'Review tests that cover survived mutants',
          'Add more specific assertions',
          'Test behavior changes, not just execution'
        ]
      });
    }
    
    return suggestions;
  }

  /**
   * Generate file-specific recommendations
   */
  generateFileRecommendations(file) {
    const recommendations = [];
    const survivedMutants = file.mutants.filter(m => m.status === 'Survived');
    
    // Analyze mutant types
    const mutantTypes = {};
    survivedMutants.forEach(mutant => {
      mutantTypes[mutant.mutatorName] = (mutantTypes[mutant.mutatorName] || 0) + 1;
    });
    
    // Generate specific recommendations based on mutant types
    Object.entries(mutantTypes).forEach(([type, count]) => {
      switch (type) {
        case 'ConditionalExpression':
          recommendations.push(`Add tests for both true and false branches of conditions (${count} issues)`);
          break;
        case 'ArithmeticOperator':
          recommendations.push(`Verify arithmetic calculations with specific expected values (${count} issues)`);
          break;
        case 'EqualityOperator':
          recommendations.push(`Test equality comparisons with various input values (${count} issues)`);
          break;
        case 'LogicalOperator':
          recommendations.push(`Test logical operations with different boolean combinations (${count} issues)`);
          break;
        case 'StringLiteral':
          recommendations.push(`Verify string operations and transformations (${count} issues)`);
          break;
        default:
          recommendations.push(`Review tests for ${type} mutations (${count} issues)`);
      }
    });
    
    return recommendations;
  }

  /**
   * Calculate test strength based on mutation results
   */
  calculateTestStrength(killedMutants, totalMutants) {
    if (totalMutants === 0) return 'unknown';
    
    const score = (killedMutants / totalMutants) * 100;
    
    if (score >= 95) return 'excellent';
    if (score >= 85) return 'good';
    if (score >= 70) return 'adequate';
    if (score >= 50) return 'weak';
    return 'poor';
  }

  /**
   * Analyze trends if historical data is available
   */
  analyzeTrends() {
    // This would be implemented with historical mutation test data
    return {
      scoreChange: null,
      newWeakAreas: [],
      improvedAreas: [],
      recommendation: 'Run mutation testing regularly to track trends'
    };
  }

  /**
   * Generate detailed report
   */
  generateDetailedReport() {
    const analysis = this.analyze();
    
    return {
      timestamp: new Date().toISOString(),
      mutationTesting: {
        summary: analysis.summary,
        weakAreas: analysis.weakAreas,
        suggestions: analysis.suggestions,
        fileDetails: this.getFileDetails()
      },
      recommendations: {
        immediate: analysis.suggestions.filter(s => s.priority === 'high'),
        planned: analysis.suggestions.filter(s => s.priority === 'medium'),
        optional: analysis.suggestions.filter(s => s.priority === 'low')
      },
      nextSteps: this.generateNextSteps(analysis)
    };
  }

  /**
   * Get detailed information for each file
   */
  getFileDetails() {
    return this.report.files.map(file => {
      const mutants = file.mutants;
      const killed = mutants.filter(m => m.status === 'Killed').length;
      const survived = mutants.filter(m => m.status === 'Survived').length;
      const noCoverage = mutants.filter(m => m.status === 'NoCoverage').length;
      const timedOut = mutants.filter(m => m.status === 'TimedOut').length;
      
      return {
        file: file.source,
        mutationScore: mutants.length > 0 ? (killed / mutants.length) * 100 : 0,
        mutants: {
          total: mutants.length,
          killed,
          survived,
          noCoverage,
          timedOut
        },
        hotspots: this.identifyHotspots(file)
      };
    });
  }

  /**
   * Identify mutation hotspots in a file
   */
  identifyHotspots(file) {
    const survivedMutants = file.mutants.filter(m => m.status === 'Survived');
    const lineGroups = {};
    
    survivedMutants.forEach(mutant => {
      const line = mutant.location.start.line;
      if (!lineGroups[line]) {
        lineGroups[line] = [];
      }
      lineGroups[line].push(mutant);
    });
    
    return Object.entries(lineGroups)
      .filter(([line, mutants]) => mutants.length >= 2)
      .map(([line, mutants]) => ({
        line: parseInt(line),
        mutantCount: mutants.length,
        types: [...new Set(mutants.map(m => m.mutatorName))],
        severity: mutants.length >= 3 ? 'high' : 'medium'
      }));
  }

  /**
   * Generate actionable next steps
   */
  generateNextSteps(analysis) {
    const steps = [];
    
    if (analysis.summary.mutationScore < 80) {
      steps.push({
        step: 1,
        action: 'Focus on highest impact areas',
        description: 'Start with files that have the lowest mutation scores',
        files: analysis.weakAreas.slice(0, 3).map(area => area.file)
      });
    }
    
    if (analysis.summary.noCoverageMutants > 0) {
      steps.push({
        step: 2,
        action: 'Improve code coverage',
        description: 'Add tests for uncovered code paths',
        target: `Reduce no-coverage mutants from ${analysis.summary.noCoverageMutants} to 0`
      });
    }
    
    steps.push({
      step: steps.length + 1,
      action: 'Review survived mutants',
      description: 'Analyze each survived mutant and improve corresponding tests',
      target: 'Achieve 90%+ mutation score'
    });
    
    return steps;
  }
}

module.exports = {
  MutationAnalyzer,
  
  // Helper function to run mutation analysis
  analyzeMutationReport: (reportPath) => {
    const fs = require('fs');
    const report = JSON.parse(fs.readFileSync(reportPath, 'utf8'));
    const analyzer = new MutationAnalyzer(report);
    return analyzer.generateDetailedReport();
  },
  
  // Helper to compare mutation reports
  compareMutationReports: (currentReport, previousReport) => {
    const currentAnalyzer = new MutationAnalyzer(currentReport);
    const previousAnalyzer = new MutationAnalyzer(previousReport);
    
    const currentSummary = currentAnalyzer.generateSummary();
    const previousSummary = previousAnalyzer.generateSummary();
    
    return {
      scoreChange: currentSummary.mutationScore - previousSummary.mutationScore,
      mutantChange: currentSummary.totalMutants - previousSummary.totalMutants,
      improvementAreas: [], // Files with improved scores
      regressionAreas: [], // Files with decreased scores
      trend: currentSummary.mutationScore > previousSummary.mutationScore ? 'improving' : 'declining'
    };
  }
};
