import React, { useState } from 'react'
import { AlertTriangle, Shield, GitBranch, Eye, ChevronDown, ChevronUp } from 'lucide-react'

const IssueSummary = ({ issues, onIssueSelect }) => {
  const [expandedCategory, setExpandedCategory] = useState(null)

  if (!issues) {
    return (
      <div className="card">
        <h3 className="text-lg font-semibold text-white mb-4">Issue Summary</h3>
        <div className="text-center text-gray-400">
          No issues found
        </div>
      </div>
    )
  }

  const categories = [
    {
      key: 'syntax_errors',
      label: 'Syntax Errors',
      icon: AlertTriangle,
      color: 'error',
      issues: issues.syntax_errors || []
    },
    {
      key: 'security_issues',
      label: 'Security Issues',
      icon: Shield,
      color: 'error',
      issues: issues.security_issues || []
    },
    {
      key: 'logic_conflicts',
      label: 'Logic Conflicts',
      icon: GitBranch,
      color: 'warning',
      issues: issues.logic_conflicts || []
    },
    {
      key: 'secrets_detected',
      label: 'Secrets Detected',
      icon: Eye,
      color: 'error',
      issues: issues.secrets_detected || []
    }
  ]

  const getSeverityBadge = (severity) => {
    const severityConfig = {
      critical: { class: 'badge-critical', label: 'Critical' },
      high: { class: 'badge-high', label: 'High' },
      medium: { class: 'badge-medium', label: 'Medium' },
      low: { class: 'badge-low', label: 'Low' },
      error: { class: 'badge-critical', label: 'Error' },
      warning: { class: 'badge-high', label: 'Warning' }
    }
    
    const config = severityConfig[severity?.toLowerCase()] || severityConfig.low
    return <span className={config.class}>{config.label}</span>
  }

  const totalIssues = categories.reduce((sum, cat) => sum + cat.issues.length, 0)

  return (
    <div className="card">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-white">Issue Summary</h3>
        <div className="flex items-center gap-2">
          <span className="text-2xl font-bold text-white">{totalIssues}</span>
          <span className="text-sm text-gray-400">Total Issues</span>
        </div>
      </div>

      <div className="space-y-3">
        {categories.map((category) => {
          const Icon = category.icon
          const isExpanded = expandedCategory === category.key
          const hasIssues = category.issues.length > 0

          return (
            <div key={category.key} className="border border-gray-700 rounded-lg overflow-hidden">
              <button
                onClick={() => setExpandedCategory(isExpanded ? null : category.key)}
                className="w-full px-4 py-3 flex items-center justify-between hover:bg-gray-800 transition-colors"
              >
                <div className="flex items-center gap-3">
                  <Icon className={`w-5 h-5 ${
                    category.color === 'error' ? 'text-error-400' : 'text-warning-400'
                  }`} />
                  <span className="font-medium text-white">{category.label}</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className={`px-2 py-1 rounded text-sm font-medium ${
                    hasIssues ? 'bg-error-500/20 text-error-400' : 'bg-success-500/20 text-success-400'
                  }`}>
                    {category.issues.length}
                  </span>
                  {isExpanded ? (
                    <ChevronUp className="w-4 h-4 text-gray-400" />
                  ) : (
                    <ChevronDown className="w-4 h-4 text-gray-400" />
                  )}
                </div>
              </button>

              {isExpanded && hasIssues && (
                <div className="border-t border-gray-700 max-h-60 overflow-y-auto">
                  {category.issues.map((issue, index) => (
                    <div
                      key={index}
                      onClick={() => onIssueSelect?.(issue)}
                      className="px-4 py-3 border-b border-gray-700 last:border-b-0 hover:bg-gray-800 cursor-pointer transition-colors"
                    >
                      <div className="flex items-start justify-between gap-2 mb-1">
                        <p className="text-sm text-gray-300 flex-1">
                          {issue.message || issue.description || 'Unknown issue'}
                        </p>
                        {getSeverityBadge(issue.severity)}
                      </div>
                      <div className="flex items-center gap-2 text-xs text-gray-500">
                        {issue.file && (
                          <span>File: {issue.file}</span>
                        )}
                        {issue.line && (
                          <>
                            <span>•</span>
                            <span>Line: {issue.line}</span>
                          </>
                        )}
                        {issue.service && (
                          <>
                            <span>•</span>
                            <span>Service: {issue.service}</span>
                          </>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )
        })}
      </div>

      {/* Quick Stats */}
      <div className="mt-4 pt-4 border-t border-gray-700">
        <div className="grid grid-cols-2 gap-4">
          <div className="text-center">
            <div className="text-lg font-bold text-error-400">
              {categories.reduce((sum, cat) => 
                sum + cat.issues.filter(i => 
                  ['critical', 'high', 'error'].includes(i.severity?.toLowerCase())
                ).length, 0
              )}
            </div>
            <div className="text-xs text-gray-400">Critical/High</div>
          </div>
          <div className="text-center">
            <div className="text-lg font-bold text-warning-400">
              {categories.reduce((sum, cat) => 
                sum + cat.issues.filter(i => 
                  ['medium', 'warning'].includes(i.severity?.toLowerCase())
                ).length, 0
              )}
            </div>
            <div className="text-xs text-gray-400">Medium</div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default IssueSummary
