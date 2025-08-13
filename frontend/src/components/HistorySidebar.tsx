'use client';

import { useState, useEffect } from 'react';
import { RunResponse } from '../store/researchStore';

type HistoryItem = {
  id: string;
  question: string;
  timestamp: number;
  result: RunResponse;
};

type HistorySidebarProps = {
  runHistory: HistoryItem[];
  onLoadHistory: (result: RunResponse) => void;
  darkMode: boolean;
  onToggleDarkMode: () => void;
};

export function HistorySidebar({ 
  runHistory, 
  onLoadHistory, 
  darkMode, 
  onToggleDarkMode 
}: HistorySidebarProps) {
  const [isOpen, setIsOpen] = useState(false);

  const formatDate = (timestamp: number) => {
    return new Date(timestamp).toLocaleString();
  };

  const truncateQuestion = (question: string, maxLength: number = 50) => {
    return question.length > maxLength 
      ? question.substring(0, maxLength) + '...'
      : question;
  };

  return (
    <>
      <button 
        className="sidebar-toggle"
        onClick={() => setIsOpen(!isOpen)}
      >
        {isOpen ? '✕' : '📚'}
      </button>
      
      <div className={`history-sidebar ${isOpen ? 'open' : ''}`}>
        <div className="sidebar-header">
          <h3>Research History</h3>
          <div className="sidebar-controls">
            <button 
              className="theme-toggle"
              onClick={onToggleDarkMode}
              title="Toggle theme"
            >
              {darkMode ? '☀️' : '🌙'}
            </button>
          </div>
        </div>
        
        <div className="history-list">
          {runHistory.length === 0 ? (
            <div className="empty-history">
              No research history yet
            </div>
          ) : (
            runHistory.map((item) => (
              <div 
                key={item.id}
                className="history-item"
                onClick={() => onLoadHistory(item.result)}
              >
                <div className="history-question">
                  {truncateQuestion(item.question)}
                </div>
                <div className="history-meta">
                  <span className="history-date">
                    {formatDate(item.timestamp)}
                  </span>
                  <span className="history-time">
                    {item.result.execution_time?.toFixed(1)}s
                  </span>
                </div>
                <div className="history-status">
                  {item.result.success ? '✅' : '❌'}
                </div>
              </div>
            ))
          )}
        </div>
        
        <div className="sidebar-footer">
          <span className="sidebar-info">
            Click any item to load results
          </span>
        </div>
      </div>
      
      {isOpen && <div className="sidebar-overlay" onClick={() => setIsOpen(false)} />}
    </>
  );
}