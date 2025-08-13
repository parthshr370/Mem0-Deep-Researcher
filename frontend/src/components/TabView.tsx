'use client';

import { useState } from 'react';

export type Tab = {
  id: string;
  label: string;
  icon?: string;
  content: React.ReactNode;
};

type TabViewProps = {
  tabs: Tab[];
  defaultTab?: string;
};

export function TabView({ tabs, defaultTab }: TabViewProps) {
  const [activeTab, setActiveTab] = useState(defaultTab || tabs[0]?.id);

  const activeTabContent = tabs.find(tab => tab.id === activeTab)?.content;

  return (
    <div className="tab-view">
      <div className="tab-nav">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            className={`tab-button ${activeTab === tab.id ? 'active' : ''}`}
            onClick={() => setActiveTab(tab.id)}
          >
            {tab.icon && <span className="tab-icon">{tab.icon}</span>}
            <span className="tab-label">{tab.label}</span>
          </button>
        ))}
      </div>
      
      <div className="tab-content">
        {activeTabContent}
      </div>
    </div>
  );
}
