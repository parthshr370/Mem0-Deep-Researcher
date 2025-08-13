import { useCallback } from 'react';
import { RunResponse, ProgressEvent } from '../store/researchStore';

export type ResearchParams = {
  question: string;
  user_id?: string;
  max_memories?: number;
  max_iterations?: number;
  store_memories?: boolean;
};

export function useResearch(
  setLoading: (loading: boolean) => void,
  setStatus: (status: string) => void,
  setResult: (result: RunResponse | null) => void,
  setCurrentPhase: (phase: string) => void,
  setProgress: (progress: number) => void,
  addProgressEvent: (event: ProgressEvent) => void,
  addToHistory: (question: string, result: RunResponse) => void,
  reset: () => void
) {
  const runResearch = useCallback(async (params: ResearchParams) => {
    if (!params.question?.trim()) {
      setStatus('Please enter a research question');
      return;
    }

    reset();
    setLoading(true);
    setStatus('Starting Pipeline...');

    try {
      // Try streaming first, fallback to regular API
      const streamResponse = await fetch('http://localhost:8000/api/research/stream', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          question: params.question.trim(),
          user_id: params.user_id || 'doctor_memory',
          max_memories: params.max_memories || 100,
          max_iterations: params.max_iterations || 5,
          store_memories: params.store_memories || false,
        }),
      });

      if (streamResponse.ok && streamResponse.body) {
        // Handle streaming response
        const reader = streamResponse.body.getReader();
        const decoder = new TextDecoder();

        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          const chunk = decoder.decode(value);
          const lines = chunk.split('\n').filter(line => line.trim());

          for (const line of lines) {
            if (line.startsWith('data: ')) {
              try {
                const data = JSON.parse(line.slice(6));
                
                // Filter out heartbeat messages from display
                if (data.phase !== 'heartbeat') {
                  addProgressEvent(data);
                }

                // Update progress based on phase (ignore heartbeat)
                if (data.phase !== 'heartbeat') {
                  const phaseOrder = ['metadata', 'planning', 'research', 'analysis', 'complete'];
                  const currentIndex = phaseOrder.indexOf(data.phase);
                  if (currentIndex >= 0) {
                    const progressPercent = ((currentIndex + 1) / phaseOrder.length) * 100;
                    setProgress(Math.min(progressPercent, 100));
                    setCurrentPhase(data.phase);
                  }

                  if (data.phase === 'complete') {
                    setResult(data.data);
                    setStatus('Research Complete');
                    setLoading(false);
                    addToHistory(params.question, data.data);
                  } else if (data.phase === 'error') {
                    throw new Error(data.data?.error || 'Pipeline failed');
                  }
                }
              } catch (e) {
                console.warn('Failed to parse SSE data:', line);
              }
            }
          }
        }
      } else {
        // Fallback to regular API
        const response = await fetch('http://localhost:8000/api/research/run', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            question: params.question.trim(),
            user_id: params.user_id || 'doctor_memory',
            max_memories: params.max_memories || 100,
            max_iterations: params.max_iterations || 5,
            store_memories: params.store_memories || false,
          }),
        });

        if (!response.ok) {
          const error = await response.json().catch(() => ({}));
          throw new Error(error.detail || 'Pipeline failed');
        }

        const result = await response.json() as RunResponse;
        setResult(result);
        setStatus('Research Complete');
        setProgress(100);
        addToHistory(params.question, result);
      }
    } catch (error: any) {
      console.error('Research failed:', error);
      setStatus(`Error: ${error.message}`);
    } finally {
      setLoading(false);
    }
  }, [setLoading, setStatus, setResult, setCurrentPhase, setProgress, addProgressEvent, addToHistory, reset]);

  const cancelResearch = useCallback(() => {
    reset();
    setStatus('Cancelled');
  }, [reset, setStatus]);

  return {
    runResearch,
    cancelResearch
  };
}