import { useState } from 'react'
import MessageBubble from './MessageBubble'
import InputArea from './InputArea'
import './ChatInterface.css'

interface DistillMessage {
  id: string
  originalPrompt: string
  refinedPrompt: string
  response: string
  modelUsed: string
  distillationUsed: boolean
  timestamp: Date
}

function DistillInterface() {
  const [messages, setMessages] = useState<DistillMessage[]>([])
  const [isLoading, setIsLoading] = useState(false)

  const handleSend = async (prompt: string) => {
    if (!prompt.trim() || isLoading) return

    setIsLoading(true)
    const messageId = Date.now().toString()

    try {
      const response = await fetch('/api/distill', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ prompt })
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const data = await response.json()

      const newMessage: DistillMessage = {
        id: messageId,
        originalPrompt: data.original_prompt,
        refinedPrompt: data.refined_prompt,
        response: data.response,
        modelUsed: data.model_used,
        distillationUsed: data.distillation_used,
        timestamp: new Date()
      }

      setMessages(prev => [...prev, newMessage])
    } catch (error) {
      console.error('Error:', error)
      const errorMessage: DistillMessage = {
        id: messageId,
        originalPrompt: prompt,
        refinedPrompt: prompt,
        response: `Error: ${error instanceof Error ? error.message : 'Failed to get response'}`,
        modelUsed: 'error',
        distillationUsed: false,
        timestamp: new Date()
      }
      setMessages(prev => [...prev, errorMessage])
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="chat-interface">
      <div className="chat-messages">
        {messages.length === 0 && (
          <div className="welcome-message">
            <div className="welcome-icon">⚗️</div>
            <h2>Prompt Distillation</h2>
            <p>Your prompt will be refined by SLM first, then processed by LLM for optimal results</p>
          </div>
        )}
        {messages.map((message) => (
          <div key={message.id} className="message-pair">
            <MessageBubble
              type="user"
              content={message.originalPrompt}
              timestamp={message.timestamp}
            />
            <div className={`refined-prompt-container ${!message.distillationUsed ? 'distillation-skipped' : ''}`}>
              <div className="refined-prompt-label">
                {message.distillationUsed ? '⚡ SLM Refined Prompt' : '⚠️ Using Original Prompt (Distillation Failed)'}
              </div>
              <div className="refined-prompt-content">{message.refinedPrompt}</div>
            </div>
            <MessageBubble
              type="assistant"
              content={message.response}
              modelUsed={message.modelUsed}
              decision={{
                model_type: message.modelUsed,
                confidence: 0.9,
                reason: message.distillationUsed ? `Refined prompt processed by ${message.modelUsed.toUpperCase()}` : "Direct processing",
                estimated_cost: 0,
                estimated_latency: 0
              }}
              fallbackUsed={false}
              timestamp={message.timestamp}
            />
          </div>
        ))}
        {isLoading && (
          <div className="loading-message">
            <div className="loading-dots">
              <span></span>
              <span></span>
              <span></span>
            </div>
            <p>Refining prompt with SLM, then processing with LLM...</p>
          </div>
        )}
      </div>
      <InputArea onSend={handleSend} isLoading={isLoading} showPriority={false} />
    </div>
  )
}

export default DistillInterface

