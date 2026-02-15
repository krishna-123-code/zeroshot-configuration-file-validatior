import React from 'react'
import { BarChart3, TrendingUp, AlertTriangle } from 'lucide-react'

const RiskBreakdown = ({ riskScore }) => {
  if (!riskScore) {
    return (
      <div className="card">
        <h3 className="text-lg font-semibold text-white mb-4">Risk Breakdown</h3>
        <div className="text-center text-gray-400">
          No risk data available
        </div>
      </div>
    )
  }

  const getRiskColor = (score) => {
    if (score >= 80) return 'text-error-400'
    if (score >= 60) return 'text-warning-400'
    if (score >= 40) return 'text-primary-400'
    return 'text-success-400'
  }

  const getRiskBgColor = (score) => {
    if (score >= 80) return 'bg-error-500'
    if (score >= 60) return 'bg-warning-500'
    if (score >= 40) return 'bg-primary-500'
    return 'bg-success-500'
  }

  const stabilityMetrics = riskScore.stability_metrics || {}

  return (
    <div className="card">
      <div className="flex items-center gap-2 mb-4">
        <BarChart3 className="w-5 h-5 text-primary-400" />
        <h3 className="text-lg font-semibold text-white">Risk Breakdown</h3>
      </div>

      {/* Overall Risk Score */}
      <div className="mb-6">
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm text-gray-300">Overall Risk Score</span>
          <span className={`text-lg font-bold ${getRiskColor(riskScore.overall)}`}>
            {riskScore.overall}/100
          </span>
        </div>
        <div className="w-full bg-gray-700 rounded-full h-3">
          <div
            className={`h-3 rounded-full transition-all duration-500 ${getRiskBgColor(riskScore.overall)}`}
            style={{ width: `${riskScore.overall}%` }}
          />
        </div>
      </div>

      {/* Category Breakdown */}
      {riskScore.breakdown && (
        <div className="space-y-4 mb-6">
          <h4 className="text-sm font-medium text-gray-300">Category Breakdown</h4>
          
          {Object.entries(riskScore.breakdown).map(([key, value]) => (
            <div key={key} className="space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-400 capitalize">
                  {key.replace('_', ' ').replace('risk', '')}
                </span>
                <span className={`text-sm font-medium ${getRiskColor(value.score)}`}>
                  {value.score}
                </span>
              </div>
              <div className="w-full bg-gray-700 rounded-full h-2">
                <div
                  className={`h-2 rounded-full transition-all duration-500 ${getRiskBgColor(value.score)}`}
                  style={{ width: `${value.score}%` }}
                />
              </div>
              {value.critical_issues > 0 && (
                <div className="flex items-center gap-1 text-xs text-error-400">
                  <AlertTriangle className="w-3 h-3" />
                  <span>{value.critical_issues} critical issues</span>
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {/* Stability Metrics */}
      {Object.keys(stabilityMetrics).length > 0 && (
        <div className="space-y-4">
          <h4 className="text-sm font-medium text-gray-300 flex items-center gap-2">
            <TrendingUp className="w-4 h-4" />
            Stability Metrics
          </h4>
          
          <div className="grid grid-cols-2 gap-3">
            {Object.entries(stabilityMetrics).map(([key, value]) => (
              <div key={key} className="bg-gray-800 rounded-lg p-3">
                <div className={`text-lg font-bold ${getRiskColor(100 - value)}`}>
                  {value}%
                </div>
                <div className="text-xs text-gray-400 capitalize">
                  {key.replace('_', ' ')}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Issue Counts */}
      {riskScore.issue_counts && (
        <div className="mt-6 pt-4 border-t border-gray-700">
          <h4 className="text-sm font-medium text-gray-300 mb-3">Issue Summary</h4>
          <div className="grid grid-cols-2 gap-3">
            <div className="bg-gray-800 rounded-lg p-3">
              <div className="text-lg font-bold text-white">
                {riskScore.issue_counts.total_issues}
              </div>
              <div className="text-xs text-gray-400">Total Issues</div>
            </div>
            <div className="bg-gray-800 rounded-lg p-3">
              <div className="text-lg font-bold text-error-400">
                {riskScore.issue_counts.total_syntax_errors + 
                 riskScore.issue_counts.total_security_issues}
              </div>
              <div className="text-xs text-gray-400">Critical Issues</div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default RiskBreakdown
