import React from 'react'
import { 
  Upload, 
  Shield, 
  FileText, 
  Bot, 
  BarChart3,
  Home,
  Activity
} from 'lucide-react'

const Sidebar = ({ activeTab, setActiveTab }) => {
  const menuItems = [
    { id: 'dashboard', label: 'Dashboard', icon: Home },
    { id: 'upload', label: 'Upload & Scan', icon: Upload },
    { id: 'report', label: 'Report', icon: FileText },
    { id: 'ai-assistant', label: 'AI Assistant', icon: Bot },
  ]

  return (
    <div className="w-64 bg-gray-800 border-r border-gray-700 p-4">
      <div className="mb-8">
        <div className="flex items-center gap-3 mb-2">
          <div className="w-10 h-10 bg-primary-600 rounded-lg flex items-center justify-center">
            <Shield className="w-6 h-6 text-white" />
          </div>
          <div>
            <h1 className="text-xl font-bold text-white">ZeroGuard AI</h1>
            <p className="text-xs text-gray-400">DevOps Intelligence</p>
          </div>
        </div>
      </div>

      <nav className="space-y-2">
        {menuItems.map((item) => {
          const Icon = item.icon
          return (
            <button
              key={item.id}
              onClick={() => setActiveTab(item.id)}
              className={`sidebar-item w-full text-left ${
                activeTab === item.id ? 'active' : ''
              }`}
            >
              <Icon className="w-5 h-5" />
              <span className="font-medium">{item.label}</span>
            </button>
          )
        })}
      </nav>

      <div className="mt-auto pt-8">
        <div className="card">
          <div className="flex items-center gap-2 mb-2">
            <Activity className="w-4 h-4 text-primary-400" />
            <span className="text-sm font-medium text-gray-300">System Status</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 bg-success-400 rounded-full animate-pulse"></div>
            <span className="text-xs text-gray-400">All systems operational</span>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Sidebar
