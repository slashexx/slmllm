import { useState, useRef, useEffect } from 'react'
import ChatInterface from './components/ChatInterface'
import Header from './components/Header'
import StatsPanel from './components/StatsPanel'
import './App.css'

interface Message {
  id: string
  prompt: string
  response: string
  modelUsed: string
  decision: {
    model_type: string
    confidence: number
    reason: string
    estimated_cost: number
    estimated_latency: number
  }
  fallbackUsed: boolean
  fallbackReason?: string
  timestamp: Date
}

function App() {
  const [messages, setMessages] = useState<Message[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [stats, setStats] = useState({
    totalQueries: 0,
    llmCount: 0,
    slmCount: 0,
    totalCost: 0,
    avgLatency: 0
  })

  const handleSend = async (prompt: string, priority: string = 'balanced') => {
    if (!prompt.trim() || isLoading) return

    setIsLoading(true)
    const messageId = Date.now().toString()

    try {
      const response = await fetch('/api/query', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          prompt,
          priority,
          use_llm_fallback: true
        })
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const data = await response.json()

      const newMessage: Message = {
        id: messageId,
        prompt,
        response: data.response,
        modelUsed: data.model_used,
        decision: data.decision,
        fallbackUsed: data.fallback_used,
        fallbackReason: data.fallback_reason,
        timestamp: new Date()
      }

      setMessages(prev => [...prev, newMessage])
      
      setStats(prev => ({
        totalQueries: prev.totalQueries + 1,
        llmCount: prev.llmCount + (data.model_used === 'llm' ? 1 : 0),
        slmCount: prev.slmCount + (data.model_used === 'slm' ? 1 : 0),
        totalCost: prev.totalCost + data.decision.estimated_cost,
        avgLatency: (prev.avgLatency * prev.totalQueries + data.decision.estimated_latency) / (prev.totalQueries + 1)
      }))
    } catch (error) {
      console.error('Error:', error)
      const errorMessage: Message = {
        id: messageId,
        prompt,
        response: `Error: ${error instanceof Error ? error.message : 'Failed to get response'}`,
        modelUsed: 'error',
        decision: {
          model_type: 'error',
          confidence: 0,
          reason: 'Request failed',
          estimated_cost: 0,
          estimated_latency: 0
        },
        fallbackUsed: false,
        timestamp: new Date()
      }
      setMessages(prev => [...prev, errorMessage])
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="app">
      <div className="app-container">
        <Header />
        <div className="main-content">
          <ChatInterface 
            messages={messages}
            onSend={handleSend}
            isLoading={isLoading}
          />
          <StatsPanel stats={stats} />
        </div>
      </div>
    </div>
  )
}

export default App

