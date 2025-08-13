'use client';

type StatusBarProps = {
  loading: boolean;
  status: string;
  currentPhase: string;
  progress: number;
};

const phaseLabels: Record<string, string> = {
  metadata: 'Analyzing Database',
  planning: 'Creating Strategy', 
  research: 'Deep Research',
  analysis: 'Meta-Analysis',
  complete: 'Complete',
  error: 'Error'
};

const phaseIcons: Record<string, string> = {
  metadata: '🔍',
  planning: '📋',
  research: '🧠', 
  analysis: '📊',
  complete: '✅',
  error: '❌'
};

const phaseDescriptions: Record<string, string> = {
  metadata: 'Scanning memory database for relevant information',
  planning: 'Generating strategic research approach based on available data',
  research: 'Executing deep research iterations using ReAct methodology', 
  analysis: 'Synthesizing findings into comprehensive analysis report',
  complete: 'Research pipeline completed successfully',
  error: 'An error occurred during research execution'
};

const getEstimatedTimeRemaining = (phase: string, progress: number): string => {
  const phaseTimings = {
    metadata: 15,
    planning: 30, 
    research: 180,
    analysis: 45,
    complete: 0,
    error: 0
  };
  
  const remainingPhases = ['metadata', 'planning', 'research', 'analysis'];
  const currentIndex = remainingPhases.indexOf(phase);
  
  if (currentIndex === -1) return '~0s';
  
  let totalRemaining = 0;
  for (let i = currentIndex; i < remainingPhases.length; i++) {
    const phaseTime = phaseTimings[remainingPhases[i] as keyof typeof phaseTimings];
    if (i === currentIndex) {
      totalRemaining += phaseTime * (1 - progress / 100);
    } else {
      totalRemaining += phaseTime;
    }
  }
  
  return totalRemaining > 60 ? `~${Math.ceil(totalRemaining / 60)}min` : `~${Math.ceil(totalRemaining)}s`;
};

export function StatusBar({ loading, status, currentPhase, progress }: StatusBarProps) {
  if (!loading && !status) {
    return null;
  }

  const estimatedTime = loading ? getEstimatedTimeRemaining(currentPhase, progress) : '';

  return (
    <div className="status-bar-enhanced">
      <div className="status-content-enhanced">
        {/* Phase indicator with context */}
        <div className="phase-section">
          {loading && (
            <div className="phase-indicator">
              <div className="spinner-enhanced" />
              <div className="phase-info-enhanced">
                <div className="phase-title">
                  <span className="phase-icon">{phaseIcons[currentPhase] || '⏳'}</span>
                  <span className="phase-label">{phaseLabels[currentPhase] || currentPhase}</span>
                  <span className="phase-time">{estimatedTime}</span>
                </div>
                <div className="phase-description">
                  {phaseDescriptions[currentPhase] || status}
                </div>
              </div>
            </div>
          )}
        </div>
        
        {/* Centered progress section */}
        <div className="progress-section">
          {loading && (
            <div className="progress-enhanced">
              <div className="progress-labels">
                <span className="progress-current">
                  {Math.round(progress)}% complete
                </span>
                <span className="progress-status">
                  {status || `${phaseLabels[currentPhase] || currentPhase}...`}
                </span>
              </div>
              <div className="progress-track">
                <div 
                  className="progress-fill-enhanced" 
                  style={{ width: `${progress}%` }}
                />
              </div>
            </div>
          )}
        </div>
        
        {/* Research context section */}
        <div className="context-section">
          <div className="research-context">
            <span className="context-label">Research Depth</span>
            <span className="context-indicator">
              {currentPhase === 'research' ? '🧠 Deep Analysis' : 
               currentPhase === 'analysis' ? '📊 Synthesis' :
               currentPhase === 'planning' ? '🎯 Strategizing' :
               currentPhase === 'metadata' ? '🔍 Exploring' : '⚡ Processing'}
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}