import React from 'react'
import { Shield, AlertTriangle, CheckCircle } from 'lucide-react'

const RiskMeter = ({ riskScore }) => {
  if (!riskScore) {
    return (
      <div className="card">
        <h3 className="text-lg font-semibold text-white mb-4">Risk Assessment</h3>
        <div className="text-center text-gray-400">
          No risk data available
        </div>
      </div>
    )
  }

  const score = riskScore.overall || 0
  const level = riskScore.risk_level || 'Unknown'
  
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

  const getRiskIcon = (score) => {
    if (score >= 60) return AlertTriangle
    return CheckCircle
  }

  const RiskIcon = getRiskIcon(score)

  // Calculate rotation for the meter
  const rotation = (score / 100) * 180 - 90

  return (
    <div className="card">
      <h3 className="text-lg font-semibold text-white mb-4">Risk Assessment</h3>
      
      {/* Circular Risk Meter */}
      <div className="flex flex-col items-center mb-6">
        <div className="relative w-48 h-24 mb-4">
          {/* Background arc */}
          <svg className="absolute inset-0 w-full h-full" viewBox="0 0 200 100">
            <path
              d="M 20 80 A 60 60 0 0 1 180 80"
              fill="none"
              stroke="rgb(55 65 81)"
              strokeWidth="12"
              strokeLinecap="round"
            />
            {/* Risk level arc */}
            <path
              d="M 20 80 A 60 60 0 0 1 180 80"
              fill="none"
              stroke="currentColor"
              strokeWidth="12"
              strokeLinecap="round"
              strokeDasharray={`${(score / 100) * 188.5} 188.5`}
              className={getRiskColor(score)}
              style={{
                transform: `rotate(-90deg)`,
                transformOrigin: '100px 80px'
              }}
            />
          </svg>
          
          {/* Center content */}
          <div className="absolute inset-0 flex flex-col items-center justify-center">
            <div className={`text-3xl font-bold ${getRiskColor(score)}`}>
              {score}
            </div>
            <div className="text-xs text-gray-400">Overall Score</div>
          </div>
        </div>

        {/* Risk Level */}
        <div className={`flex items-center gap-2 px-3 py-1 rounded-full ${getRiskColor(score)} bg-current/10`}>
          <RiskIcon className="w-4 h-4" />
          <span className="font-medium">{level}</span>
        </div>
      </div>

      {/* Risk Breakdown */}
      <div className="space-y-3">
        <h4 className="text-sm font-medium text-gray-300">Risk Breakdown</h4>
        
        {riskScore.breakdown && (
          <div className="space-y-2">
            {Object.entries(riskScore.breakdown).map(([key, value]) => (
              <div key={key} className="flex items-center justify-between">
                <span className="text-sm text-gray-400 capitalize">
                  {key.replace('_', ' ')}
                </span>
                <div className="flex items-center gap-2">
                  <div className="w-20 bg-gray-700 rounded-full h-2">
                    <div
                      className={`h-2 rounded-full ${getRiskBgColor(value.score)}`}
                      style={{ width: `${value.score}%` }}
                    />
                  </div>
                  <span className={`text-sm font-medium ${getRiskColor(value.score)}`}>
                    {value.score}
                  </span>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Recommendations */}
      {riskScore.recommendations && riskScore.recommendations.length > 0 && (
        <div className="mt-4 pt-4 border-t border-gray-700">
          <h4 className="text-sm font-medium text-gray-300 mb-2">Recommendations</h4>
          <ul className="space-y-1">
            {riskScore.recommendations.slice(0, 3).map((rec, index) => (
              <li key={index} className="text-xs text-gray-400 flex items-start gap-2">
                <span className="text-primary-400 mt-1">•</span>
                {rec}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  )
}

export default RiskMeter
