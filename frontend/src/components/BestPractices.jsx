import React, { useState } from 'react'
import { CheckCircle, AlertTriangle, Info, ChevronDown, ChevronUp, Lightbulb } from 'lucide-react'

const BestPractices = ({ suggestions }) => {
  const [expandedSuggestions, setExpandedSuggestions] = useState(new Set())

  if (!suggestions || suggestions.length === 0) {
    return (
      <div className="card">
        <h3 className="text-lg font-semibold text-white mb-4">Best Practices</h3>
        <div className="text-center text-gray-400">
          <CheckCircle className="w-12 h-12 mx-auto mb-3 text-success-400" />
          <p>No best practice violations found</p>
          <p className="text-sm mt-1">Your configuration follows DevOps best practices!</p>
        </div>
      </div>
    )
  }

  const getSeverityIcon = (severity) => {
    switch (severity) {
      case 'critical':
      case 'high':
        return <AlertTriangle className="w-4 h-4 text-error-400" />
      case 'medium':
        return <AlertTriangle className="w-4 h-4 text-warning-400" />
      case 'low':
        return <Info className="w-4 h-4 text-primary-400" />
      default:
        return <Info className="w-4 h-4 text-gray-400" />
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

  const getCategoryIcon = (category) => {
    const icons = {
      security: '🔒',
      optimization: '⚡',
      reliability: '🛡️',
      monitoring: '📊',
      resource_management: '💾',
      configuration: '⚙️',
      consistency: '🔄',
      documentation: '📝',
      organization: '📁'
    }
    return icons[category] || '💡'
  }

  const toggleExpanded = (index) => {
    const newExpanded = new Set(expandedSuggestions)
    if (newExpanded.has(index)) {
      newExpanded.delete(index)
    } else {
      newExpanded.add(index)
    }
    setExpandedSuggestions(newExpanded)
  }

  // Group suggestions by category
  const groupedSuggestions = suggestions.reduce((groups, suggestion, index) => {
    const category = suggestion.category || 'general'
    if (!groups[category]) {
      groups[category] = []
    }
    groups[category].push({ ...suggestion, originalIndex: index })
    return groups
  }, {})

  const categoryOrder = ['security', 'reliability', 'optimization', 'monitoring', 'resource_management', 'configuration', 'consistency', 'documentation', 'organization', 'general']

  return (
    <div className="card">
      <div className="flex items-center gap-2 mb-4">
        <Lightbulb className="w-5 h-5 text-warning-400" />
        <h3 className="text-lg font-semibold text-white">Best Practices Analysis</h3>
      </div>

      {/* Summary Stats */}
      <div className="grid grid-cols-3 gap-3 mb-6">
        <div className="bg-gray-800 rounded-lg p-3 text-center">
          <div className="text-lg font-bold text-error-400">
            {suggestions.filter(s => ['critical', 'high'].includes(s.severity)).length}
          </div>
          <div className="text-xs text-gray-400">Priority Issues</div>
        </div>
        <div className="bg-gray-800 rounded-lg p-3 text-center">
          <div className="text-lg font-bold text-warning-400">
            {suggestions.filter(s => s.severity === 'medium').length}
          </div>
          <div className="text-xs text-gray-400">Medium Priority</div>
        </div>
        <div className="bg-gray-800 rounded-lg p-3 text-center">
          <div className="text-lg font-bold text-primary-400">
            {suggestions.filter(s => s.severity === 'low').length}
          </div>
          <div className="text-xs text-gray-400">Low Priority</div>
        </div>
      </div>

      {/* Suggestions by Category */}
      <div className="space-y-4 max-h-96 overflow-y-auto">
        {categoryOrder
          .filter(category => groupedSuggestions[category])
          .map(category => (
            <div key={category} className="border border-gray-700 rounded-lg overflow-hidden">
              <div className="px-4 py-2 bg-gray-800 border-b border-gray-700">
                <div className="flex items-center gap-2">
                  <span className="text-lg">{getCategoryIcon(category)}</span>
                  <span className="font-medium text-white capitalize">
                    {category.replace('_', ' ')}
                  </span>
                  <span className="text-xs text-gray-400">
                    ({groupedSuggestions[category].length})
                  </span>
                </div>
              </div>
              
              <div className="divide-y divide-gray-700">
                {groupedSuggestions[category].map((suggestion) => {
                  const isExpanded = expandedSuggestions.has(suggestion.originalIndex)
                  
                  return (
                    <div key={suggestion.originalIndex} className="p-3">
                      <div className="flex items-start gap-3">
                        {getSeverityIcon(suggestion.severity)}
                        <div className="flex-1 min-w-0">
                          <div className="flex items-start justify-between gap-2 mb-1">
                            <p className="text-sm text-gray-300 leading-relaxed">
                              {suggestion.message}
                            </p>
                            <span className={getSeverityBadge(suggestion.severity)}>
                              {suggestion.severity}
                            </span>
                          </div>
                          
                          {suggestion.recommendation && (
                            <div className="mt-2">
                              <button
                                onClick={() => toggleExpanded(suggestion.originalIndex)}
                                className="flex items-center gap-1 text-xs text-primary-400 hover:text-primary-300 transition-colors"
                              >
                                {isExpanded ? (
                                  <>
                                    <ChevronUp className="w-3 h-3" />
                                    Hide Recommendation
                                  </>
                                ) : (
                                  <>
                                    <ChevronDown className="w-3 h-3" />
                                    Show Recommendation
                                  </>
                                )}
                              </button>
                              
                              {isExpanded && (
                                <div className="mt-2 p-2 bg-gray-800 rounded border border-gray-700">
                                  <p className="text-xs text-gray-300 leading-relaxed">
                                    💡 {suggestion.recommendation}
                                  </p>
                                  
                                  {/* Additional context */}
                                  {suggestion.service && (
                                    <div className="mt-2 text-xs text-gray-400">
                                      Service: {suggestion.service}
                                    </div>
                                  )}
                                  {suggestion.line && (
                                    <div className="text-xs text-gray-400">
                                      Line: {suggestion.line}
                                    </div>
                                  )}
                                  {suggestion.file && (
                                    <div className="text-xs text-gray-400">
                                      File: {suggestion.file}
                                    </div>
                                  )}
                                </div>
                              )}
                            </div>
                          )}
                        </div>
                      </div>
                    </div>
                  )
                })}
              </div>
            </div>
          ))}
      </div>

      {/* Quick Actions */}
      <div className="mt-4 pt-4 border-t border-gray-700">
        <div className="flex items-center justify-between">
          <p className="text-sm text-gray-400">
            {suggestions.length} best practice suggestions found
          </p>
          <button
            onClick={() => {
              const allExpanded = new Set(suggestions.map((_, index) => index))
              setExpandedSuggestions(allExpanded)
            }}
            className="text-xs text-primary-400 hover:text-primary-300 transition-colors"
          >
            Expand All
          </button>
        </div>
      </div>
    </div>
  )
}

export default BestPractices
