import React from 'react'
import { Activity, Cpu, HardDrive, Network, Clock } from 'lucide-react'

const SimulationScores = ({ scores }) => {
  if (!scores) {
    return (
      <div className="card">
        <h3 className="text-lg font-semibold text-white mb-4">Deployment Simulation</h3>
        <div className="text-center text-gray-400">
          <Activity className="w-12 h-12 mx-auto mb-3 text-gray-600" />
          <p>No simulation data available</p>
        </div>
      </div>
    )
  }

  const getScoreColor = (score) => {
    if (score >= 85) return 'text-success-400'
    if (score >= 70) return 'text-warning-400'
    if (score >= 50) return 'text-primary-400'
    return 'text-error-400'
  }

  const getScoreBgColor = (score) => {
    if (score >= 85) return 'bg-success-500'
    if (score >= 70) return 'bg-warning-500'
    if (score >= 50) return 'bg-primary-500'
    return 'bg-error-500'
  }

  const getReadinessColor = (readiness) => {
    if (readiness >= 85) return 'text-success-400'
    if (readiness >= 70) return 'text-warning-400'
    if (readiness >= 50) return 'text-primary-400'
    return 'text-error-400'
  }

  const getReadinessBadge = (readiness) => {
    if (readiness >= 85) return 'bg-success-500/20 text-success-400 border border-success-500/30'
    if (readiness >= 70) return 'bg-warning-500/20 text-warning-400 border border-warning-500/30'
    if (readiness >= 50) return 'bg-primary-500/20 text-primary-400 border border-primary-500/30'
    return 'bg-error-500/20 text-error-400 border border-error-500/30'
  }

  return (
    <div className="card">
      <div className="flex items-center gap-2 mb-4">
        <Activity className="w-5 h-5 text-primary-400" />
        <h3 className="text-lg font-semibold text-white">Deployment Simulation</h3>
      </div>

      {/* Overall Readiness */}
      <div className="mb-6">
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm text-gray-300">Overall Readiness</span>
          <span className={`text-lg font-bold ${getReadinessColor(scores.overall_readiness)}`}>
            {scores.overall_readiness}%
          </span>
        </div>
        <div className="w-full bg-gray-700 rounded-full h-3">
          <div
            className={`h-3 rounded-full transition-all duration-500 ${getScoreBgColor(scores.overall_readiness)}`}
            style={{ width: `${scores.overall_readiness}%` }}
          />
        </div>
        {scores.deployment_predictions && (
          <div className="mt-2">
            <span className={`px-2 py-1 rounded-full text-xs font-medium ${getReadinessBadge(scores.overall_readiness)}`}>
              {scores.deployment_predictions.recommendation}
            </span>
          </div>
        )}
      </div>

      {/* Core Metrics */}
      <div className="space-y-4 mb-6">
        <div className="grid grid-cols-1 gap-3">
          <div className="bg-gray-800 rounded-lg p-3">
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center gap-2">
                <Cpu className="w-4 h-4 text-primary-400" />
                <span className="text-sm text-gray-300">Build Stability</span>
              </div>
              <span className={`text-sm font-bold ${getScoreColor(scores.build_stability)}`}>
                {scores.build_stability}%
              </span>
            </div>
            <div className="w-full bg-gray-700 rounded-full h-2">
              <div
                className={`h-2 rounded-full ${getScoreBgColor(scores.build_stability)}`}
                style={{ width: `${scores.build_stability}%` }}
              />
            </div>
          </div>

          <div className="bg-gray-800 rounded-lg p-3">
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center gap-2">
                <Network className="w-4 h-4 text-primary-400" />
                <span className="text-sm text-gray-300">Runtime Stability</span>
              </div>
              <span className={`text-sm font-bold ${getScoreColor(scores.runtime_stability)}`}>
                {scores.runtime_stability}%
              </span>
            </div>
            <div className="w-full bg-gray-700 rounded-full h-2">
              <div
                className={`h-2 rounded-full ${getScoreBgColor(scores.runtime_stability)}`}
                style={{ width: `${scores.runtime_stability}%` }}
              />
            </div>
          </div>

          <div className="bg-gray-800 rounded-lg p-3">
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center gap-2">
                <HardDrive className="w-4 h-4 text-primary-400" />
                <span className="text-sm text-gray-300">Security Posture</span>
              </div>
              <span className={`text-sm font-bold ${getScoreColor(scores.security_posture)}`}>
                {scores.security_posture}%
              </span>
            </div>
            <div className="w-full bg-gray-700 rounded-full h-2">
              <div
                className={`h-2 rounded-full ${getScoreBgColor(scores.security_posture)}`}
                style={{ width: `${scores.security_posture}%` }}
              />
            </div>
          </div>
        </div>
      </div>

      {/* Deployment Predictions */}
      {scores.deployment_predictions && (
        <div className="mb-6">
          <h4 className="text-sm font-medium text-gray-300 mb-3">Deployment Predictions</h4>
          <div className="grid grid-cols-2 gap-3">
            <div className="bg-gray-800 rounded-lg p-3">
              <div className="text-lg font-bold text-success-400">
                {scores.deployment_predictions.build_success_probability}%
              </div>
              <div className="text-xs text-gray-400">Build Success</div>
            </div>
            <div className="bg-gray-800 rounded-lg p-3">
              <div className="text-lg font-bold text-primary-400">
                {scores.deployment_predictions.deployment_success_probability}%
              </div>
              <div className="text-xs text-gray-400">Deployment Success</div>
            </div>
            <div className="bg-gray-800 rounded-lg p-3">
              <div className="text-lg font-bold text-warning-400">
                {scores.deployment_predictions.performance_issues_probability}%
              </div>
              <div className="text-xs text-gray-400">Performance Issues</div>
            </div>
            <div className="bg-gray-800 rounded-lg p-3">
              <div className="text-lg font-bold text-error-400">
                {scores.deployment_predictions.security_incident_probability}%
              </div>
              <div className="text-xs text-gray-400">Security Risk</div>
            </div>
          </div>
        </div>
      )}

      {/* Resource Estimates */}
      {scores.resource_estimates && (
        <div className="mb-6">
          <h4 className="text-sm font-medium text-gray-300 mb-3">Resource Estimates</h4>
          <div className="grid grid-cols-2 gap-3">
            <div className="bg-gray-800 rounded-lg p-3">
              <div className="text-lg font-bold text-white">
                {scores.resource_estimates.cpu_cores}
              </div>
              <div className="text-xs text-gray-400">CPU Cores</div>
            </div>
            <div className="bg-gray-800 rounded-lg p-3">
              <div className="text-lg font-bold text-white">
                {scores.resource_estimates.memory_gb}
              </div>
              <div className="text-xs text-gray-400">Memory (GB)</div>
            </div>
            <div className="bg-gray-800 rounded-lg p-3">
              <div className="text-lg font-bold text-white">
                {scores.resource_estimates.storage_gb}
              </div>
              <div className="text-xs text-gray-400">Storage (GB)</div>
            </div>
            <div className="bg-gray-800 rounded-lg p-3">
              <div className="text-lg font-bold text-white">
                {scores.resource_estimates.network_bandwidth}
              </div>
              <div className="text-xs text-gray-400">Network</div>
            </div>
          </div>
        </div>
      )}

      {/* Deployment Timeline */}
      {scores.deployment_timeline && (
        <div className="mb-6">
          <h4 className="text-sm font-medium text-gray-300 mb-3">Deployment Timeline</h4>
          <div className="bg-gray-800 rounded-lg p-3">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm text-gray-300">Total Estimated Time</span>
              <div className="flex items-center gap-2">
                <Clock className="w-4 h-4 text-primary-400" />
                <span className="text-sm font-bold text-white">
                  {scores.deployment_timeline.total_time_minutes} min
                </span>
              </div>
            </div>
            <div className="space-y-2">
              {scores.deployment_timeline.phases.map((phase, index) => (
                <div key={index} className="flex items-center justify-between text-xs">
                  <span className="text-gray-400">{phase.name}</span>
                  <span className="text-gray-300">{phase.estimated_time} min</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Risk Factors */}
      {scores.risk_factors && scores.risk_factors.length > 0 && (
        <div>
          <h4 className="text-sm font-medium text-gray-300 mb-3">Risk Factors</h4>
          <div className="space-y-2">
            {scores.risk_factors.slice(0, 3).map((risk, index) => (
              <div key={index} className="bg-gray-800 rounded-lg p-2">
                <div className="flex items-center gap-2">
                  <div className={`w-2 h-2 rounded-full ${
                    risk.severity === 'critical' ? 'bg-error-400' :
                    risk.severity === 'high' ? 'bg-warning-400' :
                    risk.severity === 'medium' ? 'bg-primary-400' :
                    'bg-success-400'
                  }`} />
                  <span className="text-xs text-gray-300">{risk.description}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

export default SimulationScores
