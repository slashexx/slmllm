import './ModelBadge.css'

interface ModelBadgeProps {
  modelType: string
  confidence: number
  fallbackUsed?: boolean
}

function ModelBadge({ modelType, confidence, fallbackUsed }: ModelBadgeProps) {
  const getModelInfo = () => {
    const type = modelType.toLowerCase()
    if (type === 'llm' || type.includes('gemini') || type.includes('gpt')) {
      return {
        label: 'LLM',
        color: '#8b5cf6',
        bgColor: 'rgba(139, 92, 246, 0.1)',
        icon: '🧠'
      }
    } else if (type === 'slm' || type.includes('llama')) {
      return {
        label: 'SLM',
        color: '#10b981',
        bgColor: 'rgba(16, 185, 129, 0.1)',
        icon: '⚡'
      }
    } else {
      return {
        label: 'Error',
        color: '#ef4444',
        bgColor: 'rgba(239, 68, 68, 0.1)',
        icon: '❌'
      }
    }
  }

  const modelInfo = getModelInfo()

  return (
    <div className="model-badge-container">
      <div 
        className="model-badge"
        style={{
          backgroundColor: modelInfo.bgColor,
          color: modelInfo.color,
          borderColor: modelInfo.color
        }}
      >
        <span className="model-icon">{modelInfo.icon}</span>
        <span className="model-label">{modelInfo.label}</span>
        {fallbackUsed && (
          <span className="fallback-indicator" title="Fallback was used">
            🔄
          </span>
        )}
      </div>
      <div className="confidence-meter">
        <div className="confidence-bar">
          <div 
            className="confidence-fill"
            style={{
              width: `${confidence * 100}%`,
              backgroundColor: modelInfo.color
            }}
          />
        </div>
        <span className="confidence-text">
          {Math.round(confidence * 100)}% confidence
        </span>
      </div>
    </div>
  )
}

export default ModelBadge

