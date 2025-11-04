import { useState, useRef, useEffect } from 'react'
import MessageBubble from './MessageBubble'
import InputArea from './InputArea'
import './ChatInterface.css'

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

interface ChatInterfaceProps {
  messages: Message[]
  onSend: (prompt: string, priority?: string) => void
  isLoading: boolean
}

function ChatInterface({ messages, onSend, isLoading }: ChatInterfaceProps) {
  const messagesEndRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, isLoading])

  return (
    <div className="chat-interface">
      <div className="chat-messages">
        {messages.length === 0 && (
          <div className="welcome-message">
            <div className="welcome-icon">🚀</div>
            <h2>Welcome to LLM-SLM Router</h2>
            <p>Ask anything and watch the system intelligently route your query to the best model</p>
            <div className="welcome-features">
              <div className="feature">
                <span className="feature-icon">⚡</span>
                <span>Automatic model selection</span>
              </div>
              <div className="feature">
                <span className="feature-icon">🎯</span>
                <span>Cost & latency optimization</span>
              </div>
              <div className="feature">
                <span className="feature-icon">🔄</span>
                <span>Smart fallback system</span>
              </div>
            </div>
          </div>
        )}
        {messages.map((message) => (
          <div key={message.id} className="message-pair">
            <MessageBubble
              type="user"
              content={message.prompt}
              timestamp={message.timestamp}
            />
            <MessageBubble
              type="assistant"
              content={message.response}
              modelUsed={message.modelUsed}
              decision={message.decision}
              fallbackUsed={message.fallbackUsed}
              fallbackReason={message.fallbackReason}
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
            <p>Routing to optimal model...</p>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>
      <InputArea onSend={onSend} isLoading={isLoading} />
    </div>
  )
}

export default ChatInterface

