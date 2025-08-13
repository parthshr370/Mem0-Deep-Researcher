'use client';

import { useState, useCallback, useEffect } from 'react';
import { StatusBar } from '../components/StatusBar';
import { InputForm } from '../components/InputForm';
import { ResultsPanel } from '../components/ResultsPanel';
import { HistorySidebar } from '../components/HistorySidebar';
import { ResultsPage } from '../components/ResultsPage';
import { useResearch, ResearchParams } from '../hooks/useResearch';
import { RunResponse, ProgressEvent, initialState } from '../store/researchStore';
import './globals.css';

export default function HomePage() {
  // State management without external dependencies
  const [state, setState] = useState(initialState);
  const [showResults, setShowResults] = useState(false);

  // Helper functions to update state
  const setLoading = useCallback((loading: boolean) => {
    setState(prev => ({ ...prev, loading }));
  }, []);

  const setStatus = useCallback((status: string) => {
    setState(prev => ({ ...prev, status }));
  }, []);

  const setResult = useCallback((result: RunResponse | null) => {
    setState(prev => ({ ...prev, result }));
    if (result) {
      setShowResults(true);
    }
  }, []);

  const setCurrentPhase = useCallback((currentPhase: string) => {
    setState(prev => ({ ...prev, currentPhase }));
  }, []);

  const setProgress = useCallback((progress: number) => {
    setState(prev => ({ ...prev, progress }));
  }, []);

  const addProgressEvent = useCallback((event: ProgressEvent) => {
    setState(prev => ({
      ...prev,
      progressEvents: [...prev.progressEvents, event]
    }));
  }, []);

  const addToHistory = useCallback((question: string, result: RunResponse) => {
    const newEntry = {
      id: Date.now().toString(),
      question,
      timestamp: Date.now(),
      result
    };
    setState(prev => ({
      ...prev,
      runHistory: [newEntry, ...prev.runHistory.slice(0, 9)] // Keep last 10
    }));
  }, []);

  const reset = useCallback(() => {
    setState(prev => ({
      ...prev,
      loading: false,
      status: '',
      currentPhase: '',
      progress: 0,
      result: null,
      progressEvents: []
    }));
  }, []);

  const toggleDarkMode = useCallback(() => {
    setState(prev => {
      const newDarkMode = !prev.darkMode;
      // Apply dark mode class to document
      if (newDarkMode) {
        document.documentElement.classList.add('dark');
      } else {
        document.documentElement.classList.remove('dark');
      }
      return { ...prev, darkMode: newDarkMode };
    });
  }, []);

  const loadHistoryResult = useCallback((result: RunResponse) => {
    setResult(result);
  }, [setResult]);

  const backToHome = useCallback(() => {
    setShowResults(false);
  }, []);

  // Initialize research hook
  const { runResearch } = useResearch(
    setLoading,
    setStatus,
    setResult,
    setCurrentPhase,
    setProgress,
    addProgressEvent,
    addToHistory,
    reset
  );

  // Load history and dark mode from localStorage on mount
  useEffect(() => {
    try {
      const saved = localStorage.getItem('research-history');
      if (saved) {
        const history = JSON.parse(saved);
        setState(prev => ({ ...prev, runHistory: history }));
      }
      
      // Load dark mode preference
      const savedDarkMode = localStorage.getItem('darkMode');
      if (savedDarkMode !== null) {
        const isDark = savedDarkMode === 'true';
        setState(prev => ({ ...prev, darkMode: isDark }));
        if (isDark) {
          document.documentElement.classList.add('dark');
        }
      }
    } catch (e) {
      console.warn('Failed to load from localStorage');
    }
  }, []);

  // Save history and dark mode to localStorage when they change
  useEffect(() => {
    try {
      localStorage.setItem('research-history', JSON.stringify(state.runHistory));
    } catch (e) {
      console.warn('Failed to save history to localStorage');
    }
  }, [state.runHistory]);

  useEffect(() => {
    try {
      localStorage.setItem('darkMode', state.darkMode.toString());
    } catch (e) {
      console.warn('Failed to save dark mode to localStorage');
    }
  }, [state.darkMode]);

  // Show results page when research is complete
  if (showResults && state.result) {
    return (
      <ResultsPage 
        result={state.result}
        onBackToHome={backToHome}
        progressEvents={state.progressEvents}
      />
    );
  }

  // Show main research interface
  return (
    <div className="main-container">
      <HistorySidebar 
        runHistory={state.runHistory}
        onLoadHistory={loadHistoryResult}
        darkMode={state.darkMode}
        onToggleDarkMode={toggleDarkMode}
      />
      
      <div className="dashboard-grid">
        <div className="app-header">
          <h1 className="app-title">Deep Memory Research</h1>
          <p className="app-subtitle">Run an end-to-end deep research over your mem0 memory silo</p>
        </div>

        {state.loading && (
          <StatusBar 
            loading={state.loading}
            status={state.status}
            currentPhase={state.currentPhase}
            progress={state.progress}
          />
        )}

        <div className="input-card">
          <div className="card-header">
            <h2 className="card-title">Research Configuration</h2>
            <p className="card-description">Configure your deep memory research parameters</p>
          </div>
          <InputForm 
            onRunResearch={runResearch}
            loading={state.loading}
          />
        </div>
        
        {(state.result || state.progressEvents.length > 0) && (
          <div className="results-card">
            <div className="results-header">
              <h2 className="results-title">Research Results</h2>
              {state.result && (
                <div className="results-summary">
                  <span>session: {state.result.session_id}</span>
                  <span>time: {state.result.execution_time?.toFixed(2)}s</span>
                  {state.result.memories_stored && (
                    <span>memories stored: {state.result.memories_stored}</span>
                  )}
                </div>
              )}
            </div>
            <ResultsPanel 
              result={state.result}
              progressEvents={state.progressEvents}
            />
          </div>
        )}

        <footer>
          Backend: FastAPI on http://localhost:8000
        </footer>
      </div>
    </div>
  );
}