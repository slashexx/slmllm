import './Tabs.css'

interface TabsProps {
  activeTab: 'router' | 'distill' | 'lora-training'
  onTabChange: (tab: 'router' | 'distill' | 'lora-training') => void
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
      <button
        className={`tab ${activeTab === 'lora-training' ? 'active' : ''}`}
        onClick={() => onTabChange('lora-training')}
      >
        LoRA Training
      </button>
    </div>
  )
}

export default Tabs

