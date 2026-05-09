import React from 'react';

export default function AboutPanel({ onClose }) {
  return (
    <div className="about-modal-overlay" onClick={onClose}>
      <div className="about-modal" onClick={e => e.stopPropagation()}>
        <button className="about-modal__close" onClick={onClose}>
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <line x1="18" y1="6" x2="6" y2="18"></line>
            <line x1="6" y1="6" x2="18" y2="18"></line>
          </svg>
        </button>
        
        <div className="about-modal__content">
          <h2 className="about-modal__title">Bengaluru Heritage Explorer</h2>
          <p className="about-modal__subtitle">A Multi-Modal Hybrid Graph RAG System for Bengaluru's Architectural Heritage</p>
          
          <div className="about-modal__stats">
            <div className="about-stat">
              <div className="about-stat__num">13</div>
              <div className="about-stat__label">Landmarks</div>
            </div>
            <div className="about-stat">
              <div className="about-stat__num">39</div>
              <div className="about-stat__label">Graph Nodes</div>
            </div>
            <div className="about-stat">
              <div className="about-stat__num">61</div>
              <div className="about-stat__label">Graph Edges</div>
            </div>
            <div className="about-stat">
              <div className="about-stat__num">1000+</div>
              <div className="about-stat__label">Years of History</div>
            </div>
          </div>

          <div className="about-modal__grid">
            <div className="about-card">
              <h3>🔍 Hybrid RAG Pipeline</h3>
              <p>Combines <strong>Vector Search</strong> (ChromaDB + SentenceTransformers) with <strong>Knowledge Graph Traversal</strong> (NetworkX) to create a "super-context" for the LLM — richer than either method alone.</p>
            </div>
            
            <div className="about-card">
              <h3>🧠 Grounded LLM Generation</h3>
              <p>Powered by <strong>Llama 3.3 70B</strong> via Groq. Every answer is strictly grounded in our curated knowledge base of 13 Bengaluru heritage landmarks — no hallucinations.</p>
            </div>
            
            <div className="about-card">
              <h3>🎙️ Multi-Modal I/O</h3>
              <p><strong>3 input modes</strong>: text, voice (Groq Whisper), image upload (CLIP). <strong>4 output modes</strong>: text, images, audio guides (gTTS), and interactive knowledge graphs.</p>
            </div>
            
            <div className="about-card">
              <h3>⚡ Production Architecture</h3>
              <p>FastAPI backend with service-layer pattern, dependency injection, and lifespan model loading. Fully <strong>Dockerized</strong> with health checks and persistent volumes.</p>
            </div>
          </div>
          
          <div className="about-modal__footer">
            <p>Built with React · FastAPI · ChromaDB · NetworkX · Groq</p>
          </div>
        </div>
      </div>
    </div>
  );
}
