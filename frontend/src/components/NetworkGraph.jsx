import React, { useEffect, useState } from 'react';

export default function NetworkGraph({ data, onNodeClick, isFullScreen = false }) {
  const [nodes, setNodes] = useState([]);
  const [links, setLinks] = useState([]);
  const size = isFullScreen ? 700 : 340;
  const cx = size / 2;
  const cy = size / 2;

  useEffect(() => {
    if (!data || !data.landmark) return;

    const n = [];
    const l = [];

    // Center
    n.push({ id: 'center', label: data.landmark, type: 'landmark', x: cx, y: cy });

    // Attributes (inner ring)
    const attrs = [];
    if (data.style) attrs.push({ label: data.style, type: 'style' });
    if (data.era) attrs.push({ label: data.era, type: 'era' });
    if (data.location) attrs.push({ label: data.location, type: 'location' });

    const innerR = isFullScreen ? 160 : 95;
    attrs.forEach((attr, i) => {
      const angle = (i / attrs.length) * 2 * Math.PI - Math.PI / 2;
      const x = cx + innerR * Math.cos(angle);
      const y = cy + innerR * Math.sin(angle);
      const id = `a-${i}`;
      n.push({ id, ...attr, x, y });
      l.push({ source: 'center', target: id, dashed: false });
    });

    // Related Sites (outer ring)
    const related = data.related_sites || [];
    const outerR = isFullScreen ? 290 : 150;
    related.forEach((site, i) => {
      const angle = (i / related.length) * 2 * Math.PI - Math.PI / 6;
      const x = cx + outerR * Math.cos(angle);
      const y = cy + outerR * Math.sin(angle);
      const id = `r-${i}`;
      n.push({ id, label: site, type: 'related', x, y });
      l.push({ source: 'center', target: id, dashed: true });
    });

    setNodes(n);
    setLinks(l);
  }, [data, isFullScreen]);

  return (
    <div className="network-graph-container" style={{ maxWidth: `${size}px`, height: `${size}px`, margin: '0 auto' }}>
      <svg width="100%" height="100%" viewBox={`0 0 ${size} ${size}`} style={{ position: 'absolute', inset: 0 }}>
        {links.map((link, i) => {
          const s = nodes.find(n => n.id === link.source);
          const t = nodes.find(n => n.id === link.target);
          if (!s || !t) return null;
          return (
            <line key={i} x1={s.x} y1={s.y} x2={t.x} y2={t.y}
              stroke="rgba(255,255,255,0.18)" strokeWidth="1.5"
              strokeDasharray={link.dashed ? "5,5" : "none"}
              className="graph-link-anim"
              style={{ animationDelay: `${i * 0.08}s` }}
            />
          );
        })}
      </svg>
      {nodes.map((node, i) => (
        <div key={node.id}
          className={`graph-node graph-node--${node.type}`}
          onClick={() => node.type === 'related' && onNodeClick(`Tell me about ${node.label}`)}
          style={{
            position: 'absolute',
            left: `${(node.x / size) * 100}%`,
            top: `${(node.y / size) * 100}%`,
            transform: 'translate(-50%, -50%)',
            animationDelay: `${i * 0.06}s`
          }}
          title={node.label}
        >
          {node.type === 'related' && <span className="graph-node-icon">→</span>}
          {node.label}
        </div>
      ))}
    </div>
  );
}
