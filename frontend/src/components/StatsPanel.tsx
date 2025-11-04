import './StatsPanel.css'

interface StatsPanelProps {
  stats: {
    totalQueries: number
    llmCount: number
    slmCount: number
    totalCost: number
    avgLatency: number
  }
}

function StatsPanel({ stats }: StatsPanelProps) {
  const llmPercentage = stats.totalQueries > 0 
    ? (stats.llmCount / stats.totalQueries * 100).toFixed(1)
    : '0'
  
  const slmPercentage = stats.totalQueries > 0
    ? (stats.slmCount / stats.totalQueries * 100).toFixed(1)
    : '0'

  return (
    <div className="stats-panel">
      <div className="stats-header">
        <h3>📊 Statistics</h3>
      </div>
      <div className="stats-content">
        <div className="stat-card">
          <div className="stat-icon">💬</div>
          <div className="stat-info">
            <div className="stat-value">{stats.totalQueries}</div>
            <div className="stat-label">Total Queries</div>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon">🧠</div>
          <div className="stat-info">
            <div className="stat-value">{stats.llmCount}</div>
            <div className="stat-label">LLM Usage</div>
            <div className="stat-percentage">{llmPercentage}%</div>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon">⚡</div>
          <div className="stat-info">
            <div className="stat-value">{stats.slmCount}</div>
            <div className="stat-label">SLM Usage</div>
            <div className="stat-percentage">{slmPercentage}%</div>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon">💰</div>
          <div className="stat-info">
            <div className="stat-value">${stats.totalCost.toFixed(6)}</div>
            <div className="stat-label">Total Cost</div>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon">⏱️</div>
          <div className="stat-info">
            <div className="stat-value">{stats.avgLatency.toFixed(2)}s</div>
            <div className="stat-label">Avg Latency</div>
          </div>
        </div>

        <div className="distribution-chart">
          <div className="chart-label">Model Distribution</div>
          <div className="chart-bars">
            <div className="chart-bar llm-bar" style={{ width: `${llmPercentage}%` }}>
              <span className="bar-label">LLM</span>
            </div>
            <div className="chart-bar slm-bar" style={{ width: `${slmPercentage}%` }}>
              <span className="bar-label">SLM</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default StatsPanel

