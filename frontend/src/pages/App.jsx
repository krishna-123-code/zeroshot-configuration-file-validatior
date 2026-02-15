import React, { useState } from 'react'
import Sidebar from '../components/Sidebar'
import Dashboard from '../components/Dashboard'
import Upload from '../components/Upload'
import Report from '../components/Report'
import AIAssistant from '../components/AIAssistant'
import Header from '../components/Header'

function App() {
  const [activeTab, setActiveTab] = useState('dashboard')
  const [scanData, setScanData] = useState(null)
  const [isScanning, setIsScanning] = useState(false)

  const renderContent = () => {
    switch (activeTab) {
      case 'dashboard':
        return <Dashboard scanData={scanData} isScanning={isScanning} setActiveTab={setActiveTab} />
      case 'upload':
        return <Upload setScanData={setScanData} isScanning={isScanning} setIsScanning={setIsScanning} setActiveTab={setActiveTab} />
      case 'report':
        return <Report scanData={scanData} />
      case 'ai-assistant':
        return <AIAssistant scanData={scanData} />
      default:
        return <Dashboard scanData={scanData} isScanning={isScanning} setActiveTab={setActiveTab} />
    }
  }

  return (
    <div className="min-h-screen bg-gray-900 flex">
      <Sidebar activeTab={activeTab} setActiveTab={setActiveTab} />
      <div className="flex-1 flex flex-col">
        <Header activeTab={activeTab} scanData={scanData} />
        <main className="flex-1 overflow-auto">
          {renderContent()}
        </main>
      </div>
    </div>
  )
}

export default App
