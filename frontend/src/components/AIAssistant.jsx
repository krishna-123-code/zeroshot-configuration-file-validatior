import React, { useState, useRef, useEffect } from 'react'
import { Bot, Send, User, Loader2, Copy, Check } from 'lucide-react'
import { explainIssue } from '../utils/api'

const AIAssistant = ({ scanData }) => {
  const [messages, setMessages] = useState([
    {
      id: 1,
      type: 'assistant',
      content: 'Hello! I\'m your AI DevOps assistant. I can help you understand security issues, best practices, and provide recommendations for your configuration. What would you like to know?'
    }
  ])
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [copiedMessage, setCopiedMessage] = useState(null)
  const messagesEndRef = useRef(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const handleSendMessage = async () => {
    if (!input.trim() || isLoading) return

    const userMessage = {
      id: Date.now(),
      type: 'user',
      content: input.trim()
    }

    setMessages(prev => [...prev, userMessage])
    setInput('')
    setIsLoading(true)

    try {
      let response = null

      // Check if this is a question about a specific issue
      if (scanData && (input.toLowerCase().includes('issue') || input.toLowerCase().includes('problem'))) {
        // Try to find relevant issues from scan data
        const allIssues = [
          ...(scanData.syntax_errors || []),
          ...(scanData.security_issues || []),
          ...(scanData.logic_conflicts || []),
          ...(scanData.secrets_detected || [])
        ]

        if (allIssues.length > 0) {
          const mostCritical = allIssues
            .filter(issue => ['critical', 'high'].includes(issue.severity))
            .slice(0, 3)

          if (mostCritical.length > 0) {
            const issue = mostCritical[0]
            response = await explainIssue(
              issue.message || issue.description,
              {
                file: issue.file,
                line: issue.line,
                service: issue.service,
                type: issue.type
              }
            )
          }
        }
      }

      // If no specific response, provide a general helpful response
      if (!response) {
        response = await generateGeneralResponse(input, scanData)
      }

      const assistantMessage = {
        id: Date.now() + 1,
        type: 'assistant',
        content: response.explanation || response
      }

      setMessages(prev => [...prev, assistantMessage])
    } catch (error) {
      const errorMessage = {
        id: Date.now() + 1,
        type: 'assistant',
        content: `I apologize, but I encountered an error while processing your request: ${error.message}. Please try rephrasing your question.`
      }
      setMessages(prev => [...prev, errorMessage])
    } finally {
      setIsLoading(false)
    }
  }

  const generateGeneralResponse = async (question, data) => {
    const lowerQuestion = question.toLowerCase()
    
    // Provide contextual responses based on available data
    if (lowerQuestion.includes('risk') || lowerQuestion.includes('score')) {
      return {
        explanation: `Based on the analysis, your configuration has a risk score of ${data?.risk_score?.overall || 'N/A'} (${data?.risk_score?.risk_level || 'Unknown'} risk level). This is determined by analyzing syntax errors, security issues, logic conflicts, and detected secrets. ${data?.risk_score?.recommendations?.slice(0, 2).join(' ') || ''}`
      }
    }

    if (lowerQuestion.includes('security') || lowerQuestion.includes('vulnerability')) {
      const securityIssues = data?.security_issues?.length || 0
      return {
        explanation: `I found ${securityIssues} security issues in your configuration. ${securityIssues > 0 ? 'The main concerns include ' + data?.security_issues?.slice(0, 2).map(i => i.message).join(', ') + '. ' : 'No critical security issues were detected. '} It's recommended to address high-severity issues first and implement proper secret management.`
      }
    }

    if (lowerQuestion.includes('secret') || lowerQuestion.includes('credential')) {
      const secrets = data?.secrets_detected?.length || 0
      return {
        explanation: `I detected ${secrets} potential secrets in your configuration. ${secrets > 0 ? 'These include ' + data?.secrets_detected?.slice(0, 2).map(s => s.secret_type).join(', ') + '. ' : 'No secrets were detected. '} For security, remove hardcoded secrets and use environment variables or a secret management system.`
      }
    }

    if (lowerQuestion.includes('best practice') || lowerQuestion.includes('recommendation')) {
      const practices = data?.best_practices?.length || 0
      return {
        explanation: `I identified ${practices} best practice recommendations. ${practices > 0 ? 'Key areas for improvement include ' + data?.best_practices?.slice(0, 2).map(p => p.category).join(', ') + '. ' : 'Your configuration follows best practices well. '} Following these recommendations will improve security, maintainability, and performance.`
      }
    }

    if (lowerQuestion.includes('deploy') || lowerQuestion.includes('deployment')) {
      return {
        explanation: `The deployment simulation shows ${data?.simulation_scores?.overall_readiness || 'N/A'}% overall readiness. Build stability is ${data?.simulation_scores?.build_stability || 'N/A'}%, runtime stability is ${data?.simulation_scores?.runtime_stability || 'N/A'}%, and security posture is ${data?.simulation_scores?.security_posture || 'N/A'}%. ${data?.simulation_scores?.deployment_predictions?.recommendation || ''}`
      }
    }

    // Default response
    return {
      explanation: `I can help you with questions about your DevOps configuration analysis. I can explain specific issues, provide security recommendations, suggest best practices, or help with deployment concerns. Feel free to ask about any aspect of your configuration analysis.`
    }
  }

  const copyMessage = (content, messageId) => {
    navigator.clipboard.writeText(content)
    setCopiedMessage(messageId)
    setTimeout(() => setCopiedMessage(null), 2000)
  }

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSendMessage()
    }
  }

  const quickQuestions = [
    "What's my overall risk level?",
    "What are the main security issues?",
    "How can I improve my configuration?",
    "What deployment issues should I fix?",
    "Explain the best practices recommendations"
  ]

  return (
    <div className="flex flex-col h-full p-6">
      <div className="flex items-center gap-2 mb-4">
        <Bot className="w-5 h-5 text-primary-400" />
        <h2 className="text-xl font-semibold text-white">AI Assistant</h2>
      </div>

      {/* Quick Questions */}
      {messages.length === 1 && (
        <div className="mb-4">
          <p className="text-sm text-gray-400 mb-3">Quick questions:</p>
          <div className="flex flex-wrap gap-2">
            {quickQuestions.map((question, index) => (
              <button
                key={index}
                onClick={() => setInput(question)}
                className="text-xs bg-gray-800 hover:bg-gray-700 text-gray-300 px-3 py-1 rounded-full transition-colors"
              >
                {question}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Messages */}
      <div className="flex-1 overflow-y-auto mb-4 space-y-4">
        {messages.map((message) => (
          <div
            key={message.id}
            className={`flex items-start gap-3 ${
              message.type === 'user' ? 'justify-end' : 'justify-start'
            }`}
          >
            {message.type === 'assistant' && (
              <div className="w-8 h-8 bg-primary-600 rounded-full flex items-center justify-center flex-shrink-0">
                <Bot className="w-4 h-4 text-white" />
              </div>
            )}
            
            <div
              className={`max-w-lg px-4 py-3 rounded-lg ${
                message.type === 'user'
                  ? 'bg-primary-600 text-white'
                  : 'bg-gray-800 text-gray-100'
              }`}
            >
              <p className="text-sm leading-relaxed whitespace-pre-wrap">
                {message.content}
              </p>
              <button
                onClick={() => copyMessage(message.content, message.id)}
                className="mt-2 flex items-center gap-1 text-xs opacity-60 hover:opacity-100 transition-opacity"
              >
                {copiedMessage === message.id ? (
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

            {message.type === 'user' && (
              <div className="w-8 h-8 bg-gray-700 rounded-full flex items-center justify-center flex-shrink-0">
                <User className="w-4 h-4 text-gray-300" />
              </div>
            )}
          </div>
        ))}
        
        {isLoading && (
          <div className="flex items-start gap-3">
            <div className="w-8 h-8 bg-primary-600 rounded-full flex items-center justify-center">
              <Bot className="w-4 h-4 text-white" />
            </div>
            <div className="bg-gray-800 px-4 py-3 rounded-lg">
              <div className="flex items-center gap-2">
                <Loader2 className="w-4 h-4 text-primary-400 animate-spin" />
                <span className="text-sm text-gray-300">Thinking...</span>
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="flex gap-2">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Ask about your configuration..."
          className="flex-1 input-field"
          disabled={isLoading}
        />
        <button
          onClick={handleSendMessage}
          disabled={!input.trim() || isLoading}
          className="btn-primary px-4 py-2 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {isLoading ? (
            <Loader2 className="w-4 h-4 animate-spin" />
          ) : (
            <Send className="w-4 h-4" />
          )}
        </button>
      </div>

      {/* Context Info */}
      {scanData && (
        <div className="mt-4 text-xs text-gray-500 text-center">
          I have access to your latest scan results and can provide context-aware assistance.
        </div>
      )}
    </div>
  )
}

export default AIAssistant
