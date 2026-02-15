import React, { useState } from 'react'
import RiskMeter from './RiskMeter'
import IssueSummary from './IssueSummary'
import AIExplanation from './AIExplanation'
import RiskBreakdown from './RiskBreakdown'
import DependencyGraph from './DependencyGraph'
import BestPractices from './BestPractices'
import SecretAlerts from './SecretAlerts'
import SimulationScores from './SimulationScores'
import { AlertTriangle, CheckCircle, Loader2 } from 'lucide-react'

const Dashboard = ({ scanData, isScanning, setActiveTab }) => {
  const [selectedIssue, setSelectedIssue] = useState(null)

  if (isScanning) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-center">
          <Loader2 className="w-12 h-12 text-primary-400 animate-spin mx-auto mb-4" />
          <h3 className="text-xl font-semibold text-white mb-2">Scanning Configuration</h3>
          <p className="text-gray-400">Analyzing your DevOps configuration with AI...</p>
        </div>
      </div>
    )
  }

  if (!scanData) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-center max-w-md">
          <AlertTriangle className="w-12 h-12 text-warning-400 mx-auto mb-4" />
          <h3 className="text-xl font-semibold text-white mb-2">No Scan Data Available</h3>
          <p className="text-gray-400 mb-6">
            Upload your configuration files to start analyzing your DevOps setup.
          </p>
          <button 
            onClick={() => setActiveTab('upload')}
            className="btn-primary"
          >
            Upload Files
          </button>
        </div>
      </div>
    )
  }

  const hasIssues = scanData.issue_counts?.total_issues > 0
  const riskLevel = scanData.risk_score?.risk_level || 'Unknown'

  return (
    <div className="p-6 space-y-6">
      {/* Header with Risk Overview */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white mb-2">Analysis Results</h1>
          <p className="text-gray-400">
            Comprehensive analysis of your DevOps configuration
          </p>
        </div>
        <div className="flex items-center gap-4">
          <div className={`flex items-center gap-2 px-4 py-2 rounded-lg ${
            riskLevel === 'Critical' ? 'bg-error-500/20 text-error-400' :
            riskLevel === 'High' ? 'bg-warning-500/20 text-warning-400' :
            riskLevel === 'Medium' ? 'bg-primary-500/20 text-primary-400' :
            'bg-success-500/20 text-success-400'
          }`}>
            {riskLevel === 'Minimal' ? (
              <CheckCircle className="w-5 h-5" />
            ) : (
              <AlertTriangle className="w-5 h-5" />
            )}
            <span className="font-medium">{riskLevel} Risk</span>
          </div>
        </div>
      </div>

      {/* Main Grid Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column - Risk Meter and Issue Summary */}
        <div className="lg:col-span-1 space-y-6">
          <RiskMeter riskScore={scanData.risk_score} />
          <IssueSummary 
            issues={{
              syntax_errors: scanData.syntax_errors || [],
              security_issues: scanData.security_issues || [],
              logic_conflicts: scanData.logic_conflicts || [],
              secrets_detected: scanData.secrets_detected || []
            }}
            onIssueSelect={setSelectedIssue}
          />
        </div>

        {/* Middle Column - AI Explanation and Risk Breakdown */}
        <div className="lg:col-span-1 space-y-6">
          <AIExplanation 
            explanation={scanData.ai_explanation}
            selectedIssue={selectedIssue}
          />
          <RiskBreakdown riskScore={scanData.risk_score} />
        </div>

        {/* Right Column - Additional Analysis */}
        <div className="lg:col-span-1 space-y-6">
          <SimulationScores scores={scanData.simulation_scores} />
          <SecretAlerts secrets={scanData.secrets_detected || []} />
        </div>
      </div>

      {/* Bottom Section - Dependency Graph and Best Practices */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <DependencyGraph graphData={scanData.dependency_graph} />
        <BestPractices suggestions={scanData.best_practices || []} />
      </div>

      {/* Suggested Fixes Section */}
      {scanData.suggested_fixes && scanData.suggested_fixes.length > 0 && (
        <div className="card">
          <h3 className="text-xl font-semibold text-white mb-4">AI-Generated Fixes</h3>
          <div className="space-y-4">
            {scanData.suggested_fixes.map((fix, index) => (
              <div key={index} className="border border-gray-700 rounded-lg p-4">
                <div className="flex items-start justify-between mb-2">
                  <h4 className="font-medium text-white">{fix.issue_type}</h4>
                  <div className="flex items-center gap-2">
                    <span className={`text-sm px-2 py-1 rounded ${
                      fix.confidence >= 80 ? 'bg-success-500/20 text-success-400' :
                      fix.confidence >= 60 ? 'bg-warning-500/20 text-warning-400' :
                      'bg-error-500/20 text-error-400'
                    }`}>
                      {fix.confidence}% confidence
                    </span>
                  </div>
                </div>
                <p className="text-gray-400 text-sm mb-3">{fix.reason}</p>
                {fix.fix && (
                  <div className="bg-gray-800 rounded p-3">
                    <pre className="text-sm text-gray-300 font-mono overflow-x-auto">
                      {fix.fix}
                    </pre>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

export default Dashboard
