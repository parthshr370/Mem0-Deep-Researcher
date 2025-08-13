'use client';

import { useState } from 'react';
import { useResearch, ResearchParams } from '../hooks/useResearch';

type InputFormProps = {
  onRunResearch: (params: ResearchParams) => void;
  loading: boolean;
};

export function InputForm({ onRunResearch, loading }: InputFormProps) {
  const [question, setQuestion] = useState('');
  const [userId, setUserId] = useState('doctor_memory');
  const [maxMemories, setMaxMemories] = useState(100);
  const [maxIterations, setMaxIterations] = useState(5);
  const [storeMemories, setStoreMemories] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    const params: ResearchParams = {
      question: question.trim(),
      user_id: userId.trim() || 'doctor_memory',
      max_memories: maxMemories,
      max_iterations: maxIterations,
      store_memories: storeMemories,
    };
    
    onRunResearch(params);
  };

  return (
    <form onSubmit={handleSubmit}>
      <div className="form-group">
        <label htmlFor="question" className="form-label">
          Research Question
        </label>
        <textarea
          id="question"
          className="form-textarea"
          placeholder="What would you like to research?"
          rows={4}
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          disabled={loading}
          required
        />
      </div>

      <div className="form-options">
        <div className="form-group">
          <label className="form-label">User ID</label>
          <input
            type="text"
            className="form-input"
            value={userId}
            onChange={(e) => setUserId(e.target.value)}
            disabled={loading}
          />
        </div>
        
        <div className="form-group">
          <label className="form-label">
            Max Memories <span className="form-hint">({maxMemories})</span>
          </label>
          <input
            type="range"
            className="form-slider"
            min={10}
            max={1000}
            step={10}
            value={maxMemories}
            onChange={(e) => setMaxMemories(parseInt(e.target.value))}
            disabled={loading}
          />
        </div>
        
        <div className="form-group">
          <label className="form-label">
            Max Iterations <span className="form-hint">({maxIterations})</span>
          </label>
          <input
            type="range"
            className="form-slider"
            min={1}
            max={20}
            value={maxIterations}
            onChange={(e) => setMaxIterations(parseInt(e.target.value))}
            disabled={loading}
          />
        </div>
        
        <div className="form-group checkbox-group">
          <input
            id="store_memories"
            type="checkbox"
            className="form-checkbox"
            checked={storeMemories}
            onChange={(e) => setStoreMemories(e.target.checked)}
            disabled={loading}
          />
          <label htmlFor="store_memories" className="checkbox-label">
            Store Insights Back to Mem0
          </label>
        </div>
      </div>

      <button
        type="submit"
        className="submit-button"
        disabled={loading || !question.trim()}
      >
        {loading ? 'Running Research...' : 'Run Deep Research'}
      </button>
    </form>
  );
}