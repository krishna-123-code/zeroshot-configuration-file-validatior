import React, { useState } from 'react'
import { Eye, EyeOff, AlertTriangle, Shield, Copy, Check } from 'lucide-react'

const SecretAlerts = ({ secrets }) => {
  const [showSecrets, setShowSecrets] = useState({})
  const [copiedSecrets, setCopiedSecrets] = useState({})

  if (!secrets || secrets.length === 0) {
    return (
      <div className="card">
        <h3 className="text-lg font-semibold text-white mb-4">Secret Detection</h3>
        <div className="text-center text-gray-400">
          <Shield className="w-12 h-12 mx-auto mb-3 text-success-400" />
          <p>No secrets detected</p>
          <p className="text-sm mt-1">Your configuration appears to be secure</p>
        </div>
      </div>
    )
  }

  const toggleSecretVisibility = (index) => {
    setShowSecrets(prev => ({
      ...prev,
      [index]: !prev[index]
    }))
  }

  const copyToClipboard = async (text, index) => {
    try {
      await navigator.clipboard.writeText(text)
      setCopiedSecrets(prev => ({
        ...prev,
        [index]: true
      }))
      setTimeout(() => {
        setCopiedSecrets(prev => ({
          ...prev,
          [index]: false
        }))
      }, 2000)
    } catch (err) {
      console.error('Failed to copy:', err)
    }
  }

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

  const getSecretTypeIcon = (type) => {
    const icons = {
      'aws_access_key': '🔑',
      'aws_secret_key': '🗝️',
      'github_token': '🐙',
      'github_pat': '🐙',
      'jwt_token': '🎫',
      'api_key_generic': '🔐',
      'password': '🔒',
      'token': '🎟️',
      'private_key': '📋',
      'database_url': '🗄️',
      'connection_string': '🔗',
      'slack_token': '💬',
      'slack_webhook': '🪝',
      'google_api_key': '🔍',
      'heroku_api_key': '🟣',
      'mailgun_key': '📧',
      'twilio_key': '📞',
      'stripe_key': '💳',
      'docker_hub_token': '🐳',
      'npm_token': '📦',
      'ssh_key': '🔑',
      'high_entropy_string': '🎲'
    }
    return icons[type] || '🔐'
  }

  const highConfidenceSecrets = secrets.filter(s => s.confidence >= 80)
  const aiConfirmedSecrets = secrets.filter(s => s.ai_confirmed)

  return (
    <div className="card">
      <div className="flex items-center gap-2 mb-4">
        <Eye className="w-5 h-5 text-warning-400" />
        <h3 className="text-lg font-semibold text-white">Secret Detection</h3>
      </div>

      {/* Alert Summary */}
      <div className="grid grid-cols-2 gap-3 mb-4">
        <div className="bg-error-500/10 border border-error-500/30 rounded-lg p-3">
          <div className="flex items-center gap-2 text-error-400">
            <AlertTriangle className="w-4 h-4" />
            <span className="font-medium">{highConfidenceSecrets.length}</span>
          </div>
          <div className="text-xs text-gray-400">High Confidence</div>
        </div>
        <div className="bg-warning-500/10 border border-warning-500/30 rounded-lg p-3">
          <div className="flex items-center gap-2 text-warning-400">
            <Shield className="w-4 h-4" />
            <span className="font-medium">{aiConfirmedSecrets.length}</span>
          </div>
          <div className="text-xs text-gray-400">AI Confirmed</div>
        </div>
      </div>

      {/* Secrets List */}
      <div className="space-y-3 max-h-80 overflow-y-auto">
        {secrets.map((secret, index) => (
          <div key={index} className="border border-gray-700 rounded-lg p-3">
            <div className="flex items-start justify-between mb-2">
              <div className="flex items-center gap-2">
                <span className="text-lg">{getSecretTypeIcon(secret.secret_type)}</span>
                <div>
                  <span className="font-medium text-white capitalize">
                    {secret.secret_type.replace('_', ' ')}
                  </span>
                  {secret.ai_confirmed && (
                    <span className="ml-2 text-xs bg-success-500/20 text-success-400 px-2 py-0.5 rounded">
                      AI Confirmed
                    </span>
                  )}
                </div>
              </div>
              <div className="flex items-center gap-2">
                <span className={getSeverityBadge(secret.severity)}>
                  {secret.severity}
                </span>
                <span className={`text-xs ${getSeverityColor(secret.severity)}`}>
                  {secret.confidence}%
                </span>
              </div>
            </div>

            {/* Secret Value */}
            <div className="mb-2">
              <div className="flex items-center gap-2 mb-1">
                <span className="text-xs text-gray-400">Detected Value:</span>
                <button
                  onClick={() => toggleSecretVisibility(index)}
                  className="text-xs text-primary-400 hover:text-primary-300 transition-colors flex items-center gap-1"
                >
                  {showSecrets[index] ? (
                    <>
                      <EyeOff className="w-3 h-3" />
                      Hide
                    </>
                  ) : (
                    <>
                      <Eye className="w-3 h-3" />
                      Show
                    </>
                  )}
                </button>
                <button
                  onClick={() => copyToClipboard(secret.raw_value, index)}
                  className="text-xs text-primary-400 hover:text-primary-300 transition-colors flex items-center gap-1"
                >
                  {copiedSecrets[index] ? (
                    <>
                      <Check className="w-3 h-3" />
                      Copied!
                    </>
                  ) : (
                    <>
                      <Copy className="w-3 h-3" />
                      Copy
                    </>
                  )}
                </button>
              </div>
              <div className="bg-gray-800 rounded p-2 font-mono text-xs break-all">
                {showSecrets[index] ? secret.raw_value : secret.secret_value}
              </div>
            </div>

            {/* Context */}
            {secret.context && (
              <div className="mb-2">
                <span className="text-xs text-gray-400">Context:</span>
                <div className="bg-gray-800 rounded p-2 font-mono text-xs mt-1">
                  {secret.context}
                </div>
              </div>
            )}

            {/* Location Info */}
            <div className="flex items-center gap-3 text-xs text-gray-400">
              {secret.file && (
                <span>File: {secret.file}</span>
              )}
              {secret.line && (
                <>
                  <span>•</span>
                  <span>Line: {secret.line}</span>
                </>
              )}
              {secret.scanner && (
                <>
                  <span>•</span>
                  <span>Scanner: {secret.scanner}</span>
                </>
              )}
            </div>
          </div>
        ))}
      </div>

      {/* Security Recommendations */}
      <div className="mt-4 pt-4 border-t border-gray-700">
        <h4 className="text-sm font-medium text-gray-300 mb-2">Security Recommendations</h4>
        <ul className="space-y-1 text-xs text-gray-400">
          <li className="flex items-start gap-2">
            <span className="text-error-400 mt-1">•</span>
            Remove hardcoded secrets from configuration files
          </li>
          <li className="flex items-start gap-2">
            <span className="text-error-400 mt-1">•</span>
            Use environment variables or secret management services
          </li>
          <li className="flex items-start gap-2">
            <span className="text-error-400 mt-1">•</span>
            Rotate exposed credentials immediately
          </li>
          <li className="flex items-start gap-2">
            <span className="text-error-400 mt-1">•</span>
            Add .env files to .gitignore
          </li>
        </ul>
      </div>
    </div>
  )
}

export default SecretAlerts
