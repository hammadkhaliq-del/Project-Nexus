/**
 * Intelligence Panel - AI Reasoning and Events Display
 */
import React, { useState } from 'react';
import { Brain, Bell, ChevronDown, ChevronUp } from 'lucide-react';
import { AI_ENGINES } from '../utils/constants';
import { formatTime, getSeverityColor, truncate } from '../utils/helpers';

function IntelligencePanel({ events = [], reasoning = [] }) {
  const [activeTab, setActiveTab] = useState('events');
  const [expandedItems, setExpandedItems] = useState(new Set());

  const toggleExpand = (id) => {
    setExpandedItems((prev) => {
      const next = new Set(prev);
      if (next.has(id)) {
        next.delete(id);
      } else {
        next.add(id);
      }
      return next;
    });
  };

  const getEngineInfo = (engineId) => {
    return AI_ENGINES.find((e) => e.id === engineId) || { icon: '🤖', color: '#8b949e' };
  };

  return (
    <div className="bg-[#161b22] rounded-lg border border-[#30363d] h-full flex flex-col">
      {/* Tabs */}
      <div className="flex border-b border-[#30363d]">
        <button
          onClick={() => setActiveTab('events')}
          className={`flex-1 flex items-center justify-center gap-2 px-4 py-3 text-sm font-medium transition-colors ${
            activeTab === 'events'
              ? 'text-[#58a6ff] border-b-2 border-[#58a6ff] bg-[#58a6ff11]'
              : 'text-[#8b949e] hover:text-[#c9d1d9]'
          }`}
        >
          <Bell className="w-4 h-4" />
          Events
          {events.length > 0 && (
            <span className="px-2 py-0.5 text-xs rounded-full bg-[#58a6ff] text-white">
              {events.length}
            </span>
          )}
        </button>
        <button
          onClick={() => setActiveTab('reasoning')}
          className={`flex-1 flex items-center justify-center gap-2 px-4 py-3 text-sm font-medium transition-colors ${
            activeTab === 'reasoning'
              ? 'text-[#a371f7] border-b-2 border-[#a371f7] bg-[#a371f711]'
              : 'text-[#8b949e] hover:text-[#c9d1d9]'
          }`}
        >
          <Brain className="w-4 h-4" />
          AI Reasoning
          {reasoning.length > 0 && (
            <span className="px-2 py-0.5 text-xs rounded-full bg-[#a371f7] text-white">
              {reasoning.length}
            </span>
          )}
        </button>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto p-2">
        {activeTab === 'events' ? (
          <EventsList 
            events={events} 
            expandedItems={expandedItems}
            onToggle={toggleExpand}
          />
        ) : (
          <ReasoningList 
            reasoning={reasoning}
            expandedItems={expandedItems}
            onToggle={toggleExpand}
            getEngineInfo={getEngineInfo}
          />
        )}
      </div>
    </div>
  );
}

function EventsList({ events, expandedItems, onToggle }) {
  if (events.length === 0) {
    return (
      <div className="text-center text-[#8b949e] py-8">
        No events yet
      </div>
    );
  }

  return (
    <div className="space-y-2">
      {[...events]. reverse().map((event, index) => {
        const id = event.id || `event-${index}`;
        const isExpanded = expandedItems.has(id);
        const severityColor = getSeverityColor(event.severity);

        return (
          <div
            key={id}
            className="bg-[#21262d] rounded-md border border-[#30363d] overflow-hidden"
          >
            <button
              onClick={() => onToggle(id)}
              className="w-full flex items-start gap-3 p-3 text-left hover:bg-[#30363d33] transition-colors"
            >
              <div
                className="w-2 h-2 rounded-full mt-1.5 flex-shrink-0"
                style={{ backgroundColor: severityColor }}
              />
              <div className="flex-1 min-w-0">
                <div className="flex items-center justify-between gap-2">
                  <span className="text-sm font-medium text-[#c9d1d9]">
                    {event.title || event.event_type || 'Event'}
                  </span>
                  <span className="text-xs text-[#8b949e] flex-shrink-0">
                    {formatTime(event. timestamp)}
                  </span>
                </div>
                <p className="text-xs text-[#8b949e] mt-1">
                  {isExpanded ? event.description : truncate(event.description, 60)}
                </p>
              </div>
              {isExpanded ?  (
                <ChevronUp className="w-4 h-4 text-[#8b949e] flex-shrink-0" />
              ) : (
                <ChevronDown className="w-4 h-4 text-[#8b949e] flex-shrink-0" />
              )}
            </button>

            {isExpanded && event.data && Object.keys(event.data).length > 0 && (
              <div className="px-3 pb-3 pt-0">
                <div className="bg-[#0d1117] rounded p-2 text-xs font-mono text-[#8b949e]">
                  {JSON.stringify(event.data, null, 2)}
                </div>
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
}

function ReasoningList({ reasoning, expandedItems, onToggle, getEngineInfo }) {
  if (reasoning.length === 0) {
    return (
      <div className="text-center text-[#8b949e] py-8">
        No AI reasoning logs yet
      </div>
    );
  }

  return (
    <div className="space-y-2">
      {[...reasoning].reverse().map((item, index) => {
        const id = item.id || `reasoning-${index}`;
        const isExpanded = expandedItems. has(id);
        const engine = getEngineInfo(item. engine);

        return (
          <div
            key={id}
            className="bg-[#21262d] rounded-md border border-[#30363d] overflow-hidden"
          >
            <button
              onClick={() => onToggle(id)}
              className="w-full flex items-start gap-3 p-3 text-left hover:bg-[#30363d33] transition-colors"
            >
              <span className="text-lg" title={engine.name}>
                {engine. icon}
              </span>
              <div className="flex-1 min-w-0">
                <div className="flex items-center justify-between gap-2">
                  <span 
                    className="text-sm font-medium"
                    style={{ color: engine.color }}
                  >
                    {item.decision || item.decision_type || 'Decision'}
                  </span>
                  <span className="text-xs text-[#8b949e] flex-shrink-0">
                    Tick {item.tick}
                  </span>
                </div>
                <p className="text-xs text-[#8b949e] mt-1">
                  {isExpanded ? item.reasoning : truncate(item.reasoning || item.explanation, 60)}
                </p>
              </div>
              {isExpanded ? (
                <ChevronUp className="w-4 h-4 text-[#8b949e] flex-shrink-0" />
              ) : (
                <ChevronDown className="w-4 h-4 text-[#8b949e] flex-shrink-0" />
              )}
            </button>

            {isExpanded && item. reasoning_steps && item.reasoning_steps.length > 0 && (
              <div className="px-3 pb-3 pt-0">
                <div className="bg-[#0d1117] rounded p-2">
                  <p className="text-xs text-[#8b949e] mb-2">Reasoning Steps:</p>
                  <ol className="list-decimal list-inside text-xs text-[#c9d1d9] space-y-1">
                    {item.reasoning_steps.map((step, i) => (
                      <li key={i}>{step}</li>
                    ))}
                  </ol>
                </div>
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
}

export default IntelligencePanel;