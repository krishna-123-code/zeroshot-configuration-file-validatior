import React, { useState } from 'react'
import { Bot, MessageCircle, Loader2, ChevronDown, ChevronUp } from 'lucide-react'
import { explainIssue } from '../utils/api'

const AIExplanation = ({ explanation, selectedIssue }) => {
  const [isExplaining, setIsExplaining] = useState(false)
  const [detailedExplanation, setDetailedExplanation] = useState('')
  const [isExpanded, setIsExpanded] = useState(false)

  const handleExplainIssue = async () => {
    if (!selectedIssue) return

    setIsExplaining(true)
    try {
      const result = await explainIssue(
        selectedIssue.message || selectedIssue.description,
        {
          file: selectedIssue.file,
          line: selectedIssue.line,
          service: selectedIssue.service,
          type: selectedIssue.type
        }
      )
      setDetailedExplanation(result.explanation)
      setIsExpanded(true)
    } catch (error) {
      setDetailedExplanation(`Failed to get explanation: ${error.message}`)
      setIsExpanded(true)
    } finally {
      setIsExplaining(false)
    }
  }

  return (
    <div className="card">
      <div className="flex items-center gap-2 mb-4">
        <Bot className="w-5 h-5 text-primary-400" />
        <h3 className="text-lg font-semibold text-white">AI Analysis</h3>
      </div>

      {/* General AI Explanation */}
      {explanation && (
        <div className="mb-4">
          <div className="flex items-center justify-between mb-2">
            <h4 className="text-sm font-medium text-gray-300">Root Cause Analysis</h4>
          </div>
          <div className="bg-gray-800 rounded-lg p-3">
            <p className="text-sm text-gray-300 leading-relaxed">
              {explanation}
            </p>
          </div>
        </div>
      )}

      {/* Selected Issue Explanation */}
      {selectedIssue && (
        <div className="border-t border-gray-700 pt-4">
          <div className="flex items-center justify-between mb-3">
            <h4 className="text-sm font-medium text-gray-300">Selected Issue</h4>
            <button
              onClick={() => setIsExpanded(!isExpanded)}
              className="text-gray-400 hover:text-white transition-colors"
            >
              {isExpanded ? (
                <ChevronUp className="w-4 h-4" />
              ) : (
                <ChevronDown className="w-4 h-4" />
              )}
            </button>
          </div>

          <div className="bg-gray-800 rounded-lg p-3 mb-3">
            <p className="text-sm font-medium text-white mb-1">
              {selectedIssue.message || selectedIssue.description}
            </p>
            <div className="flex items-center gap-2 text-xs text-gray-400">
              {selectedIssue.file && <span>File: {selectedIssue.file}</span>}
              {selectedIssue.line && <span>• Line: {selectedIssue.line}</span>}
              {selectedIssue.severity && (
                <span className={`px-2 py-0.5 rounded ${
                  selectedIssue.severity === 'critical' ? 'bg-error-500/20 text-error-400' :
                  selectedIssue.severity === 'high' ? 'bg-warning-500/20 text-warning-400' :
                  selectedIssue.severity === 'medium' ? 'bg-primary-500/20 text-primary-400' :
                  'bg-success-500/20 text-success-400'
                }`}>
                  {selectedIssue.severity}
                </span>
              )}
            </div>
          </div>

          <button
            onClick={handleExplainIssue}
            disabled={isExplaining}
            className="btn-secondary w-full flex items-center justify-center gap-2"
          >
            {isExplaining ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                Getting AI Explanation...
              </>
            ) : (
              <>
                <MessageCircle className="w-4 h-4" />
                Explain This Issue
              </>
            )}
          </button>

          {isExpanded && detailedExplanation && (
            <div className="mt-3 bg-gray-800 rounded-lg p-3">
              <h5 className="text-sm font-medium text-primary-400 mb-2">AI Explanation</h5>
              <p className="text-sm text-gray-300 leading-relaxed whitespace-pre-wrap">
                {detailedExplanation}
              </p>
            </div>
          )}
        </div>
      )}

      {/* AI Confidence Scores */}
      {selectedIssue && selectedIssue.confidence !== undefined && (
        <div className="mt-4 pt-4 border-t border-gray-700">
          <h4 className="text-sm font-medium text-gray-300 mb-2">AI Confidence</h4>
          <div className="flex items-center gap-3">
            <div className="flex-1">
              <div className="flex items-center justify-between mb-1">
                <span className="text-xs text-gray-400">Detection Confidence</span>
                <span className="text-xs text-gray-300">{selectedIssue.confidence}%</span>
              </div>
              <div className="w-full bg-gray-700 rounded-full h-2">
                <div
                  className={`h-2 rounded-full ${
                    selectedIssue.confidence >= 80 ? 'bg-success-500' :
                    selectedIssue.confidence >= 60 ? 'bg-warning-500' :
                    'bg-error-500'
                  }`}
                  style={{ width: `${selectedIssue.confidence}%` }}
                />
              </div>
            </div>
          </div>
        </div>
      )}

      {/* AI Insights */}
      {!selectedIssue && !explanation && (
        <div className="text-center py-8">
          <Bot className="w-12 h-12 text-gray-600 mx-auto mb-3" />
          <p className="text-gray-400 text-sm">
            Select an issue to get detailed AI-powered explanation
          </p>
        </div>
      )}
    </div>
  )
}

export default AIExplanation
