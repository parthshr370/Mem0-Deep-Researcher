'use client';

import { useState } from 'react';
import { RunResponse, ProgressEvent } from '../store/researchStore';

type AccordionItemProps = {
  title: string;
  content: string;
  defaultOpen?: boolean;
  type?: 'json' | 'markdown' | 'text';
};

function AccordionItem({ title, content, defaultOpen = false, type = 'text' }: AccordionItemProps) {
  const [isOpen, setIsOpen] = useState(defaultOpen);

  const formatContent = (content: string, type: string) => {
    if (!content) return 'no content available';
    
    if (type === 'json') {
      try {
        const parsed = typeof content === 'string' ? JSON.parse(content) : content;
        return JSON.stringify(parsed, null, 2);
      } catch {
        return content;
      }
    }
    
    return content;
  };

  const copyToClipboard = async () => {
    try {
      await navigator.clipboard.writeText(content);
      // Simple feedback - could add toast later
      const button = document.activeElement as HTMLButtonElement;
      if (button) {
        const originalText = button.textContent;
        button.textContent = '✓ copied';
        setTimeout(() => {
          button.textContent = originalText;
        }, 1000);
      }
    } catch (err) {
      console.error('Failed to copy:', err);
    }
  };

  return (
    <div className="accordion-item">
      <button 
        className={`accordion-header ${isOpen ? 'open' : ''}`}
        onClick={() => setIsOpen(!isOpen)}
      >
        <span className="accordion-title">{title}</span>
        <span className="accordion-icon">{isOpen ? '−' : '+'}</span>
      </button>
      
      {isOpen && (
        <div className="accordion-content">
          <div className="content-toolbar">
            <span className="content-type">{type}</span>
            <button className="copy-button" onClick={copyToClipboard}>
              📋 copy
            </button>
          </div>
          <pre className={`content-pre ${type}`}>
            {formatContent(content, type)}
          </pre>
        </div>
      )}
    </div>
  );
}

type ResultsPanelProps = {
  result: RunResponse | null;
  progressEvents: ProgressEvent[];
};

export function ResultsPanel({ result, progressEvents }: ResultsPanelProps) {
  if (!result && progressEvents.length === 0) {
    return null;
  }

  return (
    <div className="accordion">
        {result?.final_answer && (
          <AccordionItem
            title="Final Answer"
            content={result.final_answer}
            defaultOpen={true}
            type="markdown"
          />
        )}
        
        {result?.metadata && (
          <AccordionItem
            title="Database Metadata"
            content={JSON.stringify(result.metadata, null, 2)}
            type="json"
          />
        )}
        
        {result?.plan && (
          <AccordionItem
            title="Strategic Plan"
            content={JSON.stringify(result.plan, null, 2)}
            type="json"
          />
        )}
        
        {result?.analysis_report && (
          <AccordionItem
            title="Analysis Report"
            content={result.analysis_report}
            type="markdown"
          />
        )}
        
        {/* Raw Terminal Output */}
        <AccordionItem
          title="🖥️ Terminal Output & Debug Logs"
          content={
            progressEvents.length > 0 
              ? progressEvents
                  .map(event => {
                    const timestamp = new Date(event.timestamp * 1000).toLocaleTimeString();
                    return `[${timestamp}] [${event.phase.toUpperCase()}] ${event.status}\n${JSON.stringify(event.data || {}, null, 2)}\n${'='.repeat(80)}`;
                  })
                  .join('\n')
              : result?.logs || 'No debug output available'
          }
          type="text"
          defaultOpen={false}
        />

        {/* Complete JSON Response */}
        {result && (
          <AccordionItem
            title="🔍 Complete JSON Response"
            content={JSON.stringify(result, null, 2)}
            type="json" 
            defaultOpen={false}
          />
        )}

        {/* Raw Results Data */}
        {result?.raw_results && (
          <AccordionItem
            title="📊 Raw Search Results" 
            content={JSON.stringify(result.raw_results, null, 2)}
            type="json"
            defaultOpen={false}
          />
        )}

        {(result?.logs || progressEvents.length > 0) && (
          <AccordionItem
            title="Pipeline Logs"
            content={
              result?.logs || 
              progressEvents
                .map(event => `[${event.phase}] ${event.status}: ${JSON.stringify(event.data || {})}`)
                .join('\n')
            }
            type="text"
          />
        )}
      </div>
  );
}