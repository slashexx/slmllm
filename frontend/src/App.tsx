import { useState } from 'react'
import ChatInterface from './components/ChatInterface'
import DistillInterface from './components/DistillInterface'
import Header from './components/Header'
import StatsPanel from './components/StatsPanel'
import Tabs from './components/Tabs'
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
  const [activeTab, setActiveTab] = useState<'router' | 'distill'>('router')
  const [messages, setMessages] = useState<Message[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [stats, setStats] = useState({
    totalQueries: 0,
    llmCount: 0,
    slmCount: 0,
    totalCost: 0,
    avgLatency: 0
  })

  const API_URL = import.meta.env.VITE_API_URL || 'https://slmllm.vercel.app'

  const handleSend = async (prompt: string, priority: string = 'balanced') => {
    if (!prompt.trim() || isLoading) return

    setIsLoading(true)
    const messageId = Date.now().toString()

    try {
      const response = await fetch(`${API_URL}/api/query`, {
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
      
      const isLLM = data.model_used === 'llm' || data.model_used === 'gemini'
      const isSLM = data.model_used === 'slm'
      
      setStats(prev => ({
        totalQueries: prev.totalQueries + 1,
        llmCount: prev.llmCount + (isLLM ? 1 : 0),
        slmCount: prev.slmCount + (isSLM ? 1 : 0),
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
        <Tabs activeTab={activeTab} onTabChange={setActiveTab} />
        <div className="main-content">
          {activeTab === 'router' ? (
            <ChatInterface 
              messages={messages}
              onSend={handleSend}
              isLoading={isLoading}
            />
          ) : (
            <DistillInterface />
          )}
          <StatsPanel stats={stats} />
        </div>
      </div>
    </div>
  )
}

export default App

