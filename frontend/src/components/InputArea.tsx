import { useState, KeyboardEvent } from 'react'
import './InputArea.css'

interface InputAreaProps {
  onSend: (prompt: string, priority?: string) => void
  isLoading: boolean
  showPriority?: boolean
}

function InputArea({ onSend, isLoading, showPriority = true }: InputAreaProps) {
  const [prompt, setPrompt] = useState('')
  const [priority, setPriority] = useState('balanced')

  const handleSend = () => {
    if (prompt.trim() && !isLoading) {
      onSend(prompt, priority)
      setPrompt('')
    }
  }

  const handleKeyPress = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  return (
    <div className="input-area">
      {showPriority && (
        <div className="priority-selector">
          <label>Priority:</label>
          <div className="priority-buttons">
            <button
              className={priority === 'cost' ? 'active' : ''}
              onClick={() => setPriority('cost')}
              disabled={isLoading}
            >
              💰 Cost
            </button>
            <button
              className={priority === 'balanced' ? 'active' : ''}
              onClick={() => setPriority('balanced')}
              disabled={isLoading}
            >
              ⚖️ Balanced
            </button>
            <button
              className={priority === 'speed' ? 'active' : ''}
              onClick={() => setPriority('speed')}
              disabled={isLoading}
            >
              ⚡ Speed
            </button>
          </div>
        </div>
      )}
      <div className="input-container">
        <textarea
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Ask anything..."
          rows={3}
          disabled={isLoading}
          className="input-field"
        />
        <button
          onClick={handleSend}
          disabled={!prompt.trim() || isLoading}
          className="send-button"
        >
          {isLoading ? (
            <div className="button-loader"></div>
          ) : (
            <>
              <span>Send</span>
              <span className="send-icon">→</span>
            </>
          )}
        </button>
      </div>
    </div>
  )
}

export default InputArea

