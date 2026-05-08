import React, { useState, useEffect } from "react";

export default function MediaPanel({ currentMedia, onRelatedClick }) {
  const [activeImageIndex, setActiveImageIndex] = useState(0);

  useEffect(() => {
    setActiveImageIndex(0);
  }, [currentMedia]);

  if (!currentMedia) {
    return (
      <section className="media-panel empty-state">
        <div className="empty-state__content" style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', height: '100%', opacity: 0.5 }}>
          <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1" strokeLinecap="round" strokeLinejoin="round" style={{marginBottom: '16px'}}>
            <rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect>
            <line x1="3" y1="9" x2="21" y2="9"></line>
            <line x1="9" y1="21" x2="9" y2="9"></line>
          </svg>
          <p style={{fontFamily: 'var(--font-display)', fontSize: '1.2rem', color: 'var(--color-text-secondary)'}}>
            Awaiting Data
          </p>
        </div>
      </section>
    );
  }

  const { media, graph_data } = currentMedia;
  const images = media?.images && media.images.length > 0 
    ? media.images 
    : (media?.image_url ? [media.image_url] : []);

  return (
    <section className="media-panel">
      {images.length > 0 && (
        <div className="media-card">
          <div className="media-card__header">Visual Records</div>
          <div className="media-card__body image-section">
            <img 
              src={images[activeImageIndex] || images[0]} 
              alt={graph_data?.landmark || "Landmark"} 
              className="landmark-image"
              onError={(e) => {
                e.target.onerror = null;
                e.target.style.display = "none";
              }}
            />
            {images.length > 1 && (
              <div className="image-gallery-thumbnails">
                {images.map((img, idx) => (
                  <img 
                    key={idx}
                    src={img} 
                    alt={`Thumbnail ${idx}`}
                    className={`gallery-thumb ${idx === activeImageIndex ? 'active' : ''}`}
                    onClick={() => setActiveImageIndex(idx)}
                    onError={(e) => { e.target.style.display = "none"; }}
                  />
                ))}
              </div>
            )}
          </div>
        </div>
      )}

      {media?.audio_url && (
        <div className="media-card">
          <div className="media-card__header">Audio Archive</div>
          <div className="media-card__body audio-section">
            <audio 
              controls 
              key={media.audio_url} 
              src={media.audio_url}
              className="native-audio-player"
            >
              Your browser does not support audio.
            </audio>
          </div>
        </div>
      )}

      {graph_data && graph_data.landmark && (
        <div className="media-card">
          <div className="media-card__header">Relational Graph</div>
          <div className="media-card__body graph-tree">
            
            <div className="graph-tree__root">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{color: 'var(--color-accent)'}}>
                <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"></path>
                <circle cx="12" cy="10" r="3"></circle>
              </svg>
              <span className="graph-tree__label">{graph_data.landmark}</span>
            </div>
            
            <div className="graph-tree__branches">
              {graph_data.style && (
                <div className="graph-tree__node">
                  <span className="graph-tree__line"></span>
                  <span className="graph-tree__tag style">Style: {graph_data.style}</span>
                </div>
              )}
              {graph_data.era && (
                <div className="graph-tree__node">
                  <span className="graph-tree__line"></span>
                  <span className="graph-tree__tag era">Era: {graph_data.era}</span>
                </div>
              )}
              {graph_data.location && (
                <div className="graph-tree__node">
                  <span className="graph-tree__line"></span>
                  <span className="graph-tree__tag location">Loc: {graph_data.location}</span>
                </div>
              )}
            </div>

            {graph_data.related_sites && graph_data.related_sites.length > 0 && (
              <div className="graph-tree__related">
                <p className="graph-tree__related-title" style={{display: 'flex', alignItems: 'center', gap: '6px'}}>
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"></path>
                    <path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"></path>
                  </svg>
                  Connections
                </p>
                <div className="graph-tree__related-list">
                  {graph_data.related_sites.map((site, idx) => (
                    <button 
                      key={idx} 
                      className="graph-tree__related-btn"
                      onClick={() => onRelatedClick(`Select ${site}`)}
                    >
                      {site}
                    </button>
                  ))}
                </div>
              </div>
            )}
            
          </div>
        </div>
      )}
    </section>
  );
}
