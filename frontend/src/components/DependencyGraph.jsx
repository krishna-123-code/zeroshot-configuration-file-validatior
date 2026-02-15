import React, { useState, useCallback, useRef } from 'react'
import ReactFlow, {
  Background,
  Controls,
  MiniMap,
  useNodesState,
  useEdgesState,
  addEdge,
  MarkerType,
} from 'reactflow'
import 'reactflow/dist/style.css'

const DependencyGraph = ({ graphData }) => {
  const [nodes, setNodes, onNodesChange] = useNodesState([])
  const [edges, setEdges, onEdgesChange] = useEdgesState([])
  const reactFlowWrapper = useRef(null)
  const [reactFlowInstance, setReactFlowInstance] = useState(null)

  // Initialize graph when data changes
  React.useEffect(() => {
    if (graphData && graphData.nodes && graphData.edges) {
      const initialNodes = graphData.nodes.map((node, index) => ({
        id: node.id,
        type: node.type === 'database' ? 'input' : 
              node.type === 'external' ? 'output' : 'default',
        position: node.position || { 
          x: Math.cos(index * 0.5) * 200, 
          y: Math.sin(index * 0.5) * 200 
        },
        data: { 
          label: node.label,
          description: node.description,
          ...node.data
        },
        style: {
          background: getNodeColor(node.type),
          color: '#fff',
          border: '1px solid #222138',
          width: 180,
          height: 60,
          fontSize: '12px'
        }
      }))

      const initialEdges = graphData.edges.map((edge) => ({
        id: edge.id,
        source: edge.source,
        target: edge.target,
        type: 'smoothstep',
        animated: edge.type === 'depends_on',
        markerEnd: {
          type: MarkerType.ArrowClosed,
          color: getEdgeColor(edge.type),
        },
        style: { 
          stroke: getEdgeColor(edge.type),
          strokeWidth: 2
        },
        label: edge.label,
        labelStyle: { 
          fill: '#9ca3af', 
          fontSize: '10px',
          fontWeight: 500
        }
      }))

      setNodes(initialNodes)
      setEdges(initialEdges)
    }
  }, [graphData, setNodes, setEdges])

  const getNodeColor = (type) => {
    const colors = {
      service: '#3b82f6',
      database: '#8b5cf6',
      cache: '#f59e0b',
      api: '#10b981',
      web: '#06b6d4',
      volume: '#6b7280',
      network: '#6b7280',
      external: '#ef4444',
      error: '#ef4444'
    }
    return colors[type] || '#6b7280'
  }

  const getEdgeColor = (type) => {
    const colors = {
      depends_on: '#ef4444',
      volume_mount: '#3b82f6',
      network_connection: '#10b981',
      environment_link: '#f59e0b',
      port_binding: '#8b5cf6'
    }
    return colors[type] || '#6b7280'
  }

  const onConnect = useCallback(
    (params) => setEdges((eds) => addEdge(params, eds)),
    [setEdges]
  )

  const onInit = useCallback((rfi) => {
    setReactFlowInstance(rfi)
  }, [])

  if (!graphData || !graphData.nodes) {
    return (
      <div className="card h-96">
        <h3 className="text-lg font-semibold text-white mb-4">Dependency Graph</h3>
        <div className="flex items-center justify-center h-80">
          <div className="text-center text-gray-400">
            <div className="w-16 h-16 bg-gray-800 rounded-lg mx-auto mb-3 flex items-center justify-center">
              <svg className="w-8 h-8 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
              </svg>
            </div>
            <p>No dependency data available</p>
            <p className="text-sm mt-1">Upload docker-compose.yml to see service dependencies</p>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="card h-96">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-white">Dependency Graph</h3>
        <div className="flex items-center gap-4 text-xs text-gray-400">
          <div className="flex items-center gap-1">
            <div className="w-3 h-3 bg-blue-500 rounded"></div>
            <span>Service</span>
          </div>
          <div className="flex items-center gap-1">
            <div className="w-3 h-3 bg-purple-500 rounded"></div>
            <span>Database</span>
          </div>
          <div className="flex items-center gap-1">
            <div className="w-3 h-3 bg-red-500 rounded"></div>
            <span>External</span>
          </div>
        </div>
      </div>
      
      <div className="h-80 bg-gray-900 rounded-lg border border-gray-700" ref={reactFlowWrapper}>
        <ReactFlow
          nodes={nodes}
          edges={edges}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          onConnect={onConnect}
          onInit={onInit}
          fitView
          attributionPosition="bottom-left"
          style={{ background: '#111827' }}
        >
          <Background color="#374151" gap={16} />
          <Controls 
            className="bg-gray-800 border border-gray-700"
            showInteractive={false}
          />
          <MiniMap 
            className="bg-gray-800"
            nodeColor={(node) => getNodeColor(node.type)}
            maskColor="rgb(17, 24, 39, 0.8)"
          />
        </ReactFlow>
      </div>

      {/* Graph Metrics */}
      {graphData.metrics && (
        <div className="mt-4 pt-4 border-t border-gray-700">
          <div className="grid grid-cols-3 gap-4 text-center">
            <div>
              <div className="text-lg font-bold text-white">
                {graphData.metrics.total_nodes}
              </div>
              <div className="text-xs text-gray-400">Nodes</div>
            </div>
            <div>
              <div className="text-lg font-bold text-white">
                {graphData.metrics.total_edges}
              </div>
              <div className="text-xs text-gray-400">Connections</div>
            </div>
            <div>
              <div className="text-lg font-bold text-white">
                {graphData.metrics.service_count || 0}
              </div>
              <div className="text-xs text-gray-400">Services</div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default DependencyGraph
