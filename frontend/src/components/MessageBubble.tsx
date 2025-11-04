import ModelBadge from './ModelBadge'
import './MessageBubble.css'

interface MessageBubbleProps {
  type: 'user' | 'assistant'
  content: string
  modelUsed?: string
  decision?: {
    model_type: string
    confidence: number
    reason: string
    estimated_cost: number
    estimated_latency: number
  }
  fallbackUsed?: boolean
  fallbackReason?: string
  timestamp: Date
}

function MessageBubble({ 
  type, 
  content, 
  modelUsed, 
  decision, 
  fallbackUsed,
  fallbackReason,
  timestamp 
}: MessageBubbleProps) {
  const isUser = type === 'user'

  return (
    <div className={`message-bubble ${isUser ? 'user' : 'assistant'}`}>
      <div className="message-content">
        <div className="message-text">{content}</div>
        {!isUser && decision && (
          <div className="message-metadata">
            <ModelBadge 
              modelType={modelUsed || decision.model_type}
              confidence={decision.confidence}
              fallbackUsed={fallbackUsed}
            />
            <div className="decision-details">
              <div className="detail-item">
                <span className="detail-label">Reason:</span>
                <span className="detail-value">{decision.reason}</span>
              </div>
              {fallbackUsed && fallbackReason && (
                <div className="detail-item fallback">
                  <span className="detail-label">Fallback:</span>
                  <span className="detail-value">{fallbackReason}</span>
                </div>
              )}
              <div className="detail-row">
                <div className="detail-item small">
                  <span className="detail-label">Cost:</span>
                  <span className="detail-value">${decision.estimated_cost.toFixed(6)}</span>
                </div>
                <div className="detail-item small">
                  <span className="detail-label">Latency:</span>
                  <span className="detail-value">{decision.estimated_latency.toFixed(2)}s</span>
                </div>
              </div>
            </div>
          </div>
        )}
        <div className="message-time">
          {timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
        </div>
      </div>
    </div>
  )
}

export default MessageBubble

