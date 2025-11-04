import './Tabs.css'

interface TabsProps {
  activeTab: 'router' | 'distill'
  onTabChange: (tab: 'router' | 'distill') => void
}

function Tabs({ activeTab, onTabChange }: TabsProps) {
  return (
    <div className="tabs">
      <button
        className={`tab ${activeTab === 'router' ? 'active' : ''}`}
        onClick={() => onTabChange('router')}
      >
        Router
      </button>
      <button
        className={`tab ${activeTab === 'distill' ? 'active' : ''}`}
        onClick={() => onTabChange('distill')}
      >
        Prompt Distillation
      </button>
    </div>
  )
}

export default Tabs

