import React from "react";

export default function Sidebar({ isOpen, sessions, activeSessionId, onSelectSession, onNewSession, onDeleteSession }) {
  if (!isOpen) return null;

  return (
    <div className="sidebar">
      <button className="sidebar__new-btn" onClick={onNewSession}>
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{marginRight: '8px'}}>
          <line x1="12" y1="5" x2="12" y2="19"></line>
          <line x1="5" y1="12" x2="19" y2="12"></line>
        </svg>
        New Session
      </button>

      <div className="sidebar__session-list">
        {sessions.map(session => (
          <div 
            key={session.id} 
            className={`sidebar__session ${session.id === activeSessionId ? 'active' : ''}`}
            onClick={() => onSelectSession(session.id)}
          >
            <span className="sidebar__session-title">{session.title}</span>
            <button 
              className="sidebar__session-delete"
              onClick={(e) => {
                e.stopPropagation();
                onDeleteSession(session.id);
              }}
              title="Delete Session"
            >
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <polyline points="3 6 5 6 21 6"></polyline>
                <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
              </svg>
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}
