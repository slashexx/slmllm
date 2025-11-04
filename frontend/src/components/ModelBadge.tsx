import './ModelBadge.css'

interface ModelBadgeProps {
  modelType: string
  confidence: number
  fallbackUsed?: boolean
}

function ModelBadge({ modelType, confidence, fallbackUsed }: ModelBadgeProps) {
  const getModelInfo = () => {
    const type = modelType.toLowerCase()
    if (type === 'gemini') {
      return {
        label: 'Gemini',
        color: '#374151',
        bgColor: '#f9fafb',
        icon: '✨'
      }
    } else if (type === 'llm' || type.includes('gpt')) {
      return {
        label: 'LLM',
        color: '#374151',
        bgColor: '#f9fafb',
        icon: '🧠'
      }
    } else if (type === 'slm' || type.includes('llama')) {
      return {
        label: 'SLM',
        color: '#374151',
        bgColor: '#f9fafb',
        icon: '⚡'
      }
    } else {
      return {
        label: 'Error',
        color: '#ef4444',
        bgColor: '#f9fafb',
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
              width: `${confidence * 100}%`
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

