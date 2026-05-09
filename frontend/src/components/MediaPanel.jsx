import React, { useState, useEffect } from "react";
import NetworkGraph from "./NetworkGraph";

export default function MediaPanel({ currentMedia, onRelatedClick }) {
  const [activeImageIndex, setActiveImageIndex] = useState(0);
  const [fullScreenMedia, setFullScreenMedia] = useState(null);

  useEffect(() => {
    setActiveImageIndex(0);
    setFullScreenMedia(null);
  }, [currentMedia]);

  if (!currentMedia) {
    return (
      <section className="media-panel empty-state">
        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', height: '100%', opacity: 0.4, gap: '12px' }}>
          <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1" strokeLinecap="round" strokeLinejoin="round">
            <rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect>
            <line x1="3" y1="9" x2="21" y2="9"></line>
            <line x1="9" y1="21" x2="9" y2="9"></line>
          </svg>
          <p style={{ fontFamily: 'var(--display)', fontSize: '1.05rem', color: 'var(--text2)' }}>Awaiting Query</p>
          <p style={{ fontSize: '.78rem', color: 'var(--text3)' }}>Image, audio & graph appear here</p>
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
      {/* Landmark Info Bar */}
      {graph_data && graph_data.landmark && (
        <div className="landmark-info">
          <div className="landmark-info__name">{graph_data.landmark}</div>
          <div className="landmark-info__tags">
            {graph_data.style && <span className="landmark-info__tag landmark-info__tag--style">{graph_data.style}</span>}
            {graph_data.era && <span className="landmark-info__tag landmark-info__tag--era">{graph_data.era}</span>}
            {graph_data.location && <span className="landmark-info__tag landmark-info__tag--location">{graph_data.location}</span>}
          </div>
        </div>
      )}

      {/* Image */}
      {images.length > 0 && (
        <div className="media-card">
          <div className="media-card__header">
            <span>Visual Records</span>
            <button className="expand-btn" onClick={() => setFullScreenMedia('image')} title="Full Screen">⤢</button>
          </div>
          <div className="media-card__body image-section">
            <img 
              src={images[activeImageIndex] || images[0]} 
              alt={graph_data?.landmark || "Landmark"} 
              className="landmark-image"
              onClick={() => setFullScreenMedia('image')}
              onError={(e) => { e.target.onerror = null; e.target.style.display = "none"; }}
            />
            {images.length > 1 && (
              <div className="image-gallery-thumbnails">
                {images.map((img, idx) => (
                  <img key={idx} src={img} alt={`View ${idx + 1}`}
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

      {/* Audio */}
      {media?.audio_url && (
        <div className="media-card">
          <div className="media-card__header"><span>Audio Guide</span></div>
          <div className="media-card__body">
            <audio controls key={media.audio_url} src={media.audio_url} className="native-audio-player">
              Your browser does not support audio.
            </audio>
          </div>
        </div>
      )}

      {/* Knowledge Graph */}
      {graph_data && graph_data.landmark && (
        <div className="media-card">
          <div className="media-card__header">
            <span>Knowledge Graph</span>
            <button className="expand-btn" onClick={() => setFullScreenMedia('graph')} title="Full Screen">⤢</button>
          </div>
          <div className="media-card__body" style={{ padding: '8px', overflow: 'hidden' }}>
            <NetworkGraph data={graph_data} onNodeClick={onRelatedClick} />
          </div>
        </div>
      )}

      {/* Fullscreen Image */}
      {fullScreenMedia === 'image' && (
        <div className="fullscreen-overlay" onClick={() => setFullScreenMedia(null)}>
          <button className="fullscreen-close" onClick={() => setFullScreenMedia(null)}>✕</button>
          <img src={images[activeImageIndex] || images[0]} className="fullscreen-img-content" onClick={e => e.stopPropagation()} alt="Fullscreen" />
        </div>
      )}

      {/* Fullscreen Graph */}
      {fullScreenMedia === 'graph' && (
        <div className="fullscreen-overlay" onClick={() => setFullScreenMedia(null)}>
          <button className="fullscreen-close" onClick={() => setFullScreenMedia(null)}>✕</button>
          <div className="fullscreen-graph-content" onClick={e => e.stopPropagation()}>
            <NetworkGraph data={graph_data} onNodeClick={(q) => { setFullScreenMedia(null); onRelatedClick(q); }} isFullScreen={true} />
          </div>
        </div>
      )}
    </section>
  );
}
