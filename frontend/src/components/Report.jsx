import React, { useState } from 'react'
import { Download, FileText, Calendar, Filter, Search, ChevronDown, ChevronUp } from 'lucide-react'

const Report = ({ scanData }) => {
  const [expandedSections, setExpandedSections] = useState(new Set(['summary']))
  const [filter, setFilter] = useState('all')
  const [searchTerm, setSearchTerm] = useState('')

  if (!scanData) {
    return (
      <div className="p-6">
        <div className="flex items-center justify-center h-96">
          <div className="text-center">
            <FileText className="w-12 h-12 text-gray-600 mx-auto mb-4" />
            <h3 className="text-xl font-semibold text-white mb-2">No Report Available</h3>
            <p className="text-gray-400">
              Upload and scan configuration files to generate a detailed report.
            </p>
          </div>
        </div>
      </div>
    )
  }

  const toggleSection = (section) => {
    const newExpanded = new Set(expandedSections)
    if (newExpanded.has(section)) {
      newExpanded.delete(section)
    } else {
      newExpanded.add(section)
    }
    setExpandedSections(newExpanded)
  }

  const exportReport = () => {
    const reportData = {
      timestamp: new Date().toISOString(),
      scan_data: scanData
    }
    
    const blob = new Blob([JSON.stringify(reportData, null, 2)], {
      type: 'application/json'
    })
    
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `zeroguard-report-${new Date().toISOString().split('T')[0]}.json`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
  }

  const filterIssues = (issues) => {
    if (filter === 'all') return issues
    return issues.filter(issue => issue.severity === filter)
  }

  const searchIssues = (issues) => {
    if (!searchTerm) return issues
    return issues.filter(issue => 
      (issue.message && issue.message.toLowerCase().includes(searchTerm.toLowerCase())) ||
      (issue.description && issue.description.toLowerCase().includes(searchTerm.toLowerCase())) ||
      (issue.file && issue.file.toLowerCase().includes(searchTerm.toLowerCase()))
    )
  }

  const allIssues = [
    ...(scanData.syntax_errors || []),
    ...(scanData.security_issues || []),
    ...(scanData.logic_conflicts || []),
    ...(scanData.secrets_detected || [])
  ]

  const filteredIssues = searchIssues(filterIssues(allIssues))

  const getSeverityColor = (severity) => {
    switch (severity) {
      case 'critical': return 'text-error-400'
      case 'high': return 'text-error-400'
      case 'medium': return 'text-warning-400'
      case 'low': return 'text-primary-400'
      default: return 'text-gray-400'
    }
  }

  const getSeverityBadge = (severity) => {
    const badges = {
      critical: 'badge-critical',
      high: 'badge-high',
      medium: 'badge-medium',
      low: 'badge-low'
    }
    return badges[severity] || 'badge-low'
  }

  return (
    <div className="p-6 max-w-6xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-3xl font-bold text-white mb-2">Security Analysis Report</h1>
          <div className="flex items-center gap-4 text-sm text-gray-400">
            <div className="flex items-center gap-2">
              <Calendar className="w-4 h-4" />
              <span>{new Date().toLocaleDateString()}</span>
            </div>
            <div className="flex items-center gap-2">
              <FileText className="w-4 h-4" />
              <span>{allIssues.length} Issues Found</span>
            </div>
          </div>
        </div>
        <button
          onClick={exportReport}
          className="btn-primary flex items-center gap-2"
        >
          <Download className="w-4 h-4" />
          Export Report
        </button>
      </div>

      {/* Filters and Search */}
      <div className="card mb-6">
        <div className="flex flex-col lg:flex-row gap-4">
          <div className="flex-1">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
              <input
                type="text"
                placeholder="Search issues..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="input-field pl-10 w-full"
              />
            </div>
          </div>
          <div className="flex items-center gap-2">
            <Filter className="w-4 h-4 text-gray-400" />
            <select
              value={filter}
              onChange={(e) => setFilter(e.target.value)}
              className="input-field"
            >
              <option value="all">All Issues</option>
              <option value="critical">Critical</option>
              <option value="high">High</option>
              <option value="medium">Medium</option>
              <option value="low">Low</option>
            </select>
          </div>
        </div>
      </div>

      {/* Executive Summary */}
      <div className="card mb-6">
        <button
          onClick={() => toggleSection('summary')}
          className="w-full flex items-center justify-between text-left"
        >
          <h2 className="text-xl font-semibold text-white">Executive Summary</h2>
          {expandedSections.has('summary') ? (
            <ChevronUp className="w-5 h-5 text-gray-400" />
          ) : (
            <ChevronDown className="w-5 h-5 text-gray-400" />
          )}
        </button>

        {expandedSections.has('summary') && (
          <div className="mt-4 space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div className="bg-gray-800 rounded-lg p-4 text-center">
                <div className={`text-2xl font-bold ${getSeverityColor(scanData.risk_score?.risk_level)}`}>
                  {scanData.risk_score?.overall || 0}
                </div>
                <div className="text-sm text-gray-400">Risk Score</div>
                <div className={`text-xs mt-1 ${getSeverityColor(scanData.risk_score?.risk_level)}`}>
                  {scanData.risk_score?.risk_level || 'Unknown'} Risk
                </div>
              </div>
              <div className="bg-gray-800 rounded-lg p-4 text-center">
                <div className="text-2xl font-bold text-error-400">
                  {scanData.issue_counts?.total_syntax_errors || 0}
                </div>
                <div className="text-sm text-gray-400">Syntax Errors</div>
              </div>
              <div className="bg-gray-800 rounded-lg p-4 text-center">
                <div className="text-2xl font-bold text-warning-400">
                  {scanData.issue_counts?.total_security_issues || 0}
                </div>
                <div className="text-sm text-gray-400">Security Issues</div>
              </div>
              <div className="bg-gray-800 rounded-lg p-4 text-center">
                <div className="text-2xl font-bold text-primary-400">
                  {scanData.issue_counts?.total_secrets || 0}
                </div>
                <div className="text-sm text-gray-400">Secrets Detected</div>
              </div>
            </div>

            {scanData.ai_explanation && (
              <div className="bg-gray-800 rounded-lg p-4">
                <h3 className="text-sm font-medium text-primary-400 mb-2">AI Analysis Summary</h3>
                <p className="text-sm text-gray-300 leading-relaxed">
                  {scanData.ai_explanation}
                </p>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Issues Breakdown */}
      <div className="card mb-6">
        <button
          onClick={() => toggleSection('issues')}
          className="w-full flex items-center justify-between text-left"
        >
          <h2 className="text-xl font-semibold text-white">Issues Breakdown ({filteredIssues.length})</h2>
          {expandedSections.has('issues') ? (
            <ChevronUp className="w-5 h-5 text-gray-400" />
          ) : (
            <ChevronDown className="w-5 h-5 text-gray-400" />
          )}
        </button>

        {expandedSections.has('issues') && (
          <div className="mt-4">
            {filteredIssues.length === 0 ? (
              <div className="text-center py-8 text-gray-400">
                No issues found matching your criteria
              </div>
            ) : (
              <div className="space-y-3">
                {filteredIssues.map((issue, index) => (
                  <div key={index} className="border border-gray-700 rounded-lg p-4">
                    <div className="flex items-start justify-between mb-2">
                      <h4 className="font-medium text-white flex-1">
                        {issue.message || issue.description || 'Unknown Issue'}
                      </h4>
                      <span className={getSeverityBadge(issue.severity)}>
                        {issue.severity}
                      </span>
                    </div>
                    <div className="flex items-center gap-4 text-xs text-gray-400 mb-2">
                      {issue.file && <span>File: {issue.file}</span>}
                      {issue.line && <span>Line: {issue.line}</span>}
                      {issue.service && <span>Service: {issue.service}</span>}
                      {issue.type && <span>Type: {issue.type}</span>}
                    </div>
                    {issue.recommendation && (
                      <div className="bg-gray-800 rounded p-2">
                        <p className="text-xs text-gray-300">
                          <strong>Recommendation:</strong> {issue.recommendation}
                        </p>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>

      {/* Best Practices */}
      {scanData.best_practices && scanData.best_practices.length > 0 && (
        <div className="card mb-6">
          <button
            onClick={() => toggleSection('best_practices')}
            className="w-full flex items-center justify-between text-left"
          >
            <h2 className="text-xl font-semibold text-white">Best Practices ({scanData.best_practices.length})</h2>
            {expandedSections.has('best_practices') ? (
              <ChevronUp className="w-5 h-5 text-gray-400" />
            ) : (
              <ChevronDown className="w-5 h-5 text-gray-400" />
            )}
          </button>

          {expandedSections.has('best_practices') && (
            <div className="mt-4 space-y-3">
              {scanData.best_practices.map((practice, index) => (
                <div key={index} className="border border-gray-700 rounded-lg p-4">
                  <div className="flex items-start justify-between mb-2">
                    <h4 className="font-medium text-white flex-1">{practice.message}</h4>
                    <span className={getSeverityBadge(practice.severity)}>
                      {practice.severity}
                    </span>
                  </div>
                  <p className="text-sm text-gray-300">{practice.recommendation}</p>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Suggested Fixes */}
      {scanData.suggested_fixes && scanData.suggested_fixes.length > 0 && (
        <div className="card">
          <button
            onClick={() => toggleSection('fixes')}
            className="w-full flex items-center justify-between text-left"
          >
            <h2 className="text-xl font-semibold text-white">AI-Generated Fixes ({scanData.suggested_fixes.length})</h2>
            {expandedSections.has('fixes') ? (
              <ChevronUp className="w-5 h-5 text-gray-400" />
            ) : (
              <ChevronDown className="w-5 h-5 text-gray-400" />
            )}
          </button>

          {expandedSections.has('fixes') && (
            <div className="mt-4 space-y-4">
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
                  <p className="text-sm text-gray-300 mb-3">{fix.reason}</p>
                  {fix.fix && (
                    <div className="bg-gray-900 rounded p-3">
                      <pre className="text-sm text-gray-300 font-mono overflow-x-auto">
                        {fix.fix}
                      </pre>
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  )
}

export default Report
