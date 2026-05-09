export default function Header({ onToggleSidebar, onToggleAbout, currentEra }) {
  return (
    <header className="header">
      <div className="header__left">
        <button className="header__menu-btn" onClick={onToggleSidebar} title="Toggle Sidebar">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <line x1="3" y1="12" x2="21" y2="12"></line>
            <line x1="3" y1="6" x2="21" y2="6"></line>
            <line x1="3" y1="18" x2="21" y2="18"></line>
          </svg>
        </button>
        <div>
          <h1 className="header__title">Bengaluru Heritage Explorer</h1>
          <p className="header__subtitle">Multi-Modal Hybrid Graph RAG</p>
        </div>
      </div>
      <div className="header__right">
        {currentEra && (
          <span className="header__era-badge">{currentEra}</span>
        )}
        <button className="header__about-btn" onClick={onToggleAbout}>
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <circle cx="12" cy="12" r="10"></circle>
            <line x1="12" y1="16" x2="12" y2="12"></line>
            <line x1="12" y1="8" x2="12.01" y2="8"></line>
          </svg>
          About
        </button>
      </div>
    </header>
  );
}
