'use client';

import { TabView, Tab } from './TabView';
import { JsonViewer } from './JsonViewer';
import { MarkdownViewer } from './MarkdownViewer';
import { RunResponse, ProgressEvent } from '../store/researchStore';

type ResultsPageProps = {
  result: RunResponse;
  onBackToHome: () => void;
  progressEvents?: ProgressEvent[];
};

export function ResultsPage({ result, onBackToHome, progressEvents = [] }: ResultsPageProps) {
  const tabs: Tab[] = [
    {
      id: 'overview',
      label: 'Overview',
      icon: '📊',
      content: (
        <div className="overview-tab">
          <div className="overview-header">
            <h2>Research Summary</h2>
            <div className="overview-stats">
              <div className="stat-item">
                <span className="stat-label">Session ID</span>
                <span className="stat-value">{result.session_id}</span>
              </div>
              <div className="stat-item">
                <span className="stat-label">Execution Time</span>
                <span className="stat-value">{result.execution_time?.toFixed(2)}s</span>
              </div>
              <div className="stat-item">
                <span className="stat-label">Success</span>
                <span className="stat-value">{result.success ? '✅ Yes' : '❌ No'}</span>
              </div>
              {result.memories_stored && (
                <div className="stat-item">
                  <span className="stat-label">Memories Stored</span>
                  <span className="stat-value">{result.memories_stored}</span>
                </div>
              )}
            </div>
          </div>
          
          <div className="overview-content">
            <div className="overview-section">
              <h3>Final Answer Preview</h3>
              <div className="answer-preview">
                {result.final_answer ? (
                  <p>{result.final_answer.substring(0, 300)}...</p>
                ) : (
                  <p>No final answer available</p>
                )}
              </div>
            </div>
            
            <div className="overview-section">
              <h3>Artifacts Generated</h3>
              <div className="artifacts-list">
                {Object.entries(result.artifacts || {}).map(([type, path]) => (
                  <div key={type} className="artifact-item">
                    <span className="artifact-type">{type.replace('_', ' ')}</span>
                    <span className="artifact-path">{path}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )
    },
    {
      id: 'answer',
      label: 'Final Answer',
      icon: '🎯',
      content: (
        <MarkdownViewer 
          content={result.final_answer || 'No final answer available'} 
          title="Research Answer"
        />
      )
    },
    {
      id: 'metadata',
      label: 'Metadata',
      icon: '🔍',
      content: (
        <JsonViewer 
          data={result.metadata || {}} 
          title="Database Metadata"
        />
      )
    },
    {
      id: 'plan',
      label: 'Strategic Plan',
      icon: '📋',
      content: (
        <JsonViewer 
          data={result.plan || {}} 
          title="Research Strategy"
        />
      )
    },
    {
      id: 'analysis',
      label: 'Analysis Report',
      icon: '📊',
      content: (
        <MarkdownViewer 
          content={result.analysis_report || 'No analysis report available'} 
          title="Meta-Analysis Report"
        />
      )
    },
    {
      id: 'logs',
      label: 'Pipeline Logs',
      icon: '📜',
      content: (
        <div className="logs-viewer">
          <div className="logs-header">
            <h3>Pipeline Execution Logs</h3>
            <button 
              className="logs-copy-btn"
              onClick={async () => {
                try {
                  await navigator.clipboard.writeText(result.logs || '');
                  const button = document.activeElement as HTMLButtonElement;
                  if (button) {
                    const original = button.textContent;
                    button.textContent = '✓ copied';
                    setTimeout(() => button.textContent = original, 1000);
                  }
                } catch (err) {
                  console.error('Failed to copy logs:', err);
                }
              }}
            >
              📋 copy logs
            </button>
          </div>
          <pre className="logs-content">
            {result.logs || 'No logs available'}
          </pre>
        </div>
      )
    },
    {
      id: 'debug',
      label: 'Debug Data',
      icon: '🛠️',
      content: (
        <div className="debug-viewer">
          <div className="debug-section">
            <h3>Complete Result Object</h3>
            <JsonViewer data={result} title="Full Response Data" />
          </div>
          
          {progressEvents.length > 0 && (
            <div className="debug-section">
              <h3>Progress Events Stream ({progressEvents.length} events)</h3>
              <JsonViewer data={progressEvents} title="Real-time Progress Data" />
            </div>
          )}
          
          {result.raw_results && (
            <div className="debug-section">
              <h3>Raw Search Results</h3>
              <JsonViewer data={result.raw_results} title="Memory Search Data" />
            </div>
          )}
          
          <div className="debug-section">
            <h3>Backend Terminal Output</h3>
            <div className="terminal-output">
              <pre>
                {progressEvents.length > 0 
                  ? progressEvents
                      .map(event => {
                        const timestamp = new Date(event.timestamp * 1000).toISOString();
                        return `[${timestamp}] [${event.phase.toUpperCase()}] ${event.status}\n${JSON.stringify(event.data || {}, null, 2)}\n${'='.repeat(80)}`;
                      })
                      .join('\n')
                  : 'No terminal output captured'
                }
              </pre>
            </div>
          </div>
        </div>
      )
    }
  ];

  return (
    <div className="results-page">
      <div className="results-page-header">
        <button className="back-button" onClick={onBackToHome}>
          ← Back to Research
        </button>
        <h1>Research Results</h1>
      </div>
      
      <div style={{ maxWidth: '1400px', margin: '0 auto' }}>
        <TabView tabs={tabs} defaultTab="overview" />
      </div>
    </div>
  );
}
