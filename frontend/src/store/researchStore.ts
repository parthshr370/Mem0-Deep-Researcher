// Simple state management using React Context (no external dependencies)
import { createContext, useContext } from 'react';

export type RunResponse = {
  success: boolean;
  session_id: string;
  execution_time: number;
  artifacts: Record<string, string>;
  final_answer: string;
  metadata?: any;
  plan?: any;
  analysis_report?: string;
  logs?: string;
  memories_stored?: number;
  memories_stored_error?: string;
};

export type ProgressEvent = {
  phase: string;
  status: string;
  timestamp: number;
  data?: any;
};

export type ResearchState = {
  // Current run state
  loading: boolean;
  status: string;
  currentPhase: string;
  progress: number;
  
  // Results
  result: RunResponse | null;
  progressEvents: ProgressEvent[];
  
  // History
  runHistory: Array<{ id: string; question: string; timestamp: number; result: RunResponse }>;
  
  // Settings
  darkMode: boolean;
};

export const initialState: ResearchState = {
  loading: false,
  status: '',
  currentPhase: '',
  progress: 0,
  result: null,
  progressEvents: [],
  runHistory: [],
  darkMode: true,
};

// We'll implement this with useState in the main component
export const ResearchContext = createContext<{
  state: ResearchState;
  setState: (state: Partial<ResearchState>) => void;
} | null>(null);

export const useResearchStore = () => {
  const context = useContext(ResearchContext);
  if (!context) {
    throw new Error('useResearchStore must be used within ResearchProvider');
  }
  return context;
};