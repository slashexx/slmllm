import './Header.css'

function Header() {
  return (
    <header className="header">
      <div className="header-content">
        <div className="header-left">
          <div className="logo">
            <h1>LLM-SLM Router</h1>
          </div>
          <p className="tagline">Intelligent Model Selection</p>
        </div>
        <div className="header-right">
          <div className="status-indicator">
            <span className="status-dot"></span>
            <span>Connected</span>
          </div>
        </div>
      </div>
    </header>
  )
}

export default Header

