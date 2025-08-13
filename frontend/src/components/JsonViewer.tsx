'use client';

import { useState } from 'react';

type JsonViewerProps = {
  data: any;
  title?: string;
};

export function JsonViewer({ data, title }: JsonViewerProps) {
  const [collapsed, setCollapsed] = useState<Set<string>>(new Set());
  
  const toggleCollapse = (path: string) => {
    const newCollapsed = new Set(collapsed);
    if (newCollapsed.has(path)) {
      newCollapsed.delete(path);
    } else {
      newCollapsed.add(path);
    }
    setCollapsed(newCollapsed);
  };

  const copyToClipboard = async () => {
    try {
      await navigator.clipboard.writeText(JSON.stringify(data, null, 2));
      // Simple feedback
      const button = document.activeElement as HTMLButtonElement;
      if (button) {
        const original = button.textContent;
        button.textContent = '✓ copied';
        setTimeout(() => button.textContent = original, 1000);
      }
    } catch (err) {
      console.error('Failed to copy:', err);
    }
  };

  const renderValue = (value: any, path: string = '', depth: number = 0): React.ReactNode => {
    if (value === null) return <span className="json-null">null</span>;
    if (value === undefined) return <span className="json-undefined">undefined</span>;
    
    if (typeof value === 'boolean') {
      return <span className="json-boolean">{value.toString()}</span>;
    }
    
    if (typeof value === 'number') {
      return <span className="json-number">{value}</span>;
    }
    
    if (typeof value === 'string') {
      return <span className="json-string">"{value}"</span>;
    }
    
    if (Array.isArray(value)) {
      const isCollapsed = collapsed.has(path);
      return (
        <div className="json-array">
          <button 
            className="json-toggle"
            onClick={() => toggleCollapse(path)}
          >
            {isCollapsed ? '▶' : '▼'} [{value.length}]
          </button>
          {!isCollapsed && (
            <div className="json-content" style={{ marginLeft: `${depth * 20 + 20}px` }}>
              {value.map((item, index) => (
                <div key={index} className="json-item">
                  <span className="json-index">{index}:</span>
                  {renderValue(item, `${path}[${index}]`, depth + 1)}
                </div>
              ))}
            </div>
          )}
        </div>
      );
    }
    
    if (typeof value === 'object') {
      const keys = Object.keys(value);
      const isCollapsed = collapsed.has(path);
      return (
        <div className="json-object">
          <button 
            className="json-toggle"
            onClick={() => toggleCollapse(path)}
          >
            {isCollapsed ? '▶' : '▼'} {`{${keys.length}}`}
          </button>
          {!isCollapsed && (
            <div className="json-content" style={{ marginLeft: `${depth * 20 + 20}px` }}>
              {keys.map((key) => (
                <div key={key} className="json-item">
                  <span className="json-key">"{key}":</span>
                  {renderValue(value[key], `${path}.${key}`, depth + 1)}
                </div>
              ))}
            </div>
          )}
        </div>
      );
    }
    
    return <span>{String(value)}</span>;
  };

  return (
    <div className="json-viewer">
      <div className="json-header">
        {title && <h3 className="json-title">{title}</h3>}
        <button className="json-copy-btn" onClick={copyToClipboard}>
          📋 copy json
        </button>
      </div>
      <div className="json-content-wrapper">
        {renderValue(data)}
      </div>
    </div>
  );
}
