import React from 'react'
import { Shield, Clock, CheckCircle, AlertTriangle } from 'lucide-react'

const Header = ({ activeTab, scanData }) => {
  const getRiskLevelColor = (score) => {
    if (score >= 80) return 'text-error-400'
    if (score >= 60) return 'text-warning-400'
    if (score >= 40) return 'text-primary-400'
    return 'text-success-400'
  }

  const getRiskLevelText = (score) => {
    if (score >= 80) return 'Critical'
    if (score >= 60) return 'High'
    if (score >= 40) return 'Medium'
    return 'Low'
  }

  const getLastScanTime = () => {
    if (!scanData) return 'No scan performed'
    return new Date().toLocaleTimeString()
  }

  return (
    <header className="bg-gray-800 border-b border-gray-700 px-6 py-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <h2 className="text-2xl font-bold text-white capitalize">
            {activeTab.replace('-', ' ')}
          </h2>
          {scanData && (
            <div className="flex items-center gap-2">
              <div className={`flex items-center gap-1 px-3 py-1 rounded-full bg-gray-700/50 ${getRiskLevelColor(scanData.risk_score?.overall || 0)}`}>
                <Shield className="w-4 h-4" />
                <span className="text-sm font-medium">
                  {getRiskLevelText(scanData.risk_score?.overall || 0)} Risk
                </span>
              </div>
            </div>
          )}
        </div>

        <div className="flex items-center gap-6">
          {scanData && (
            <div className="flex items-center gap-4 text-sm">
              <div className="flex items-center gap-2 text-gray-400">
                <Clock className="w-4 h-4" />
                <span>Last scan: {getLastScanTime()}</span>
              </div>
              
              <div className="flex items-center gap-4">
                <div className="flex items-center gap-1">
                  <CheckCircle className="w-4 h-4 text-success-400" />
                  <span className="text-gray-300">
                    {scanData.issue_counts?.total_issues || 0} Issues
                  </span>
                </div>
                
                {scanData.risk_score?.overall >= 60 && (
                  <div className="flex items-center gap-1">
                    <AlertTriangle className="w-4 h-4 text-warning-400" />
                    <span className="text-warning-400">
                      Action Required
                    </span>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      </div>
    </header>
  )
}

export default Header
