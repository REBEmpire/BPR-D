'use client';

import { useState } from 'react';
import { triggerSpecialSession } from '@/app/actions/special-session';
import { Loader2, Zap } from 'lucide-react';

const AGENTS = [
  { id: 'grok', label: 'Grok', role: 'Chief / Manager' },
  { id: 'claude', label: 'Claude', role: 'Strategist' },
  { id: 'gemini', label: 'Gemini', role: 'Developer' },
  { id: 'abacus', label: 'Abacus', role: 'Innovator' },
] as const;

export function SpecialSessionButton() {
  const [topic, setTopic] = useState('');
  const [selectedAgents, setSelectedAgents] = useState<Set<string>>(
    new Set(['grok', 'claude', 'gemini', 'abacus'])
  );
  const [numRounds, setNumRounds] = useState(4);
  const [status, setStatus] = useState<'idle' | 'loading' | 'success' | 'error'>('idle');
  const [message, setMessage] = useState('');

  function toggleAgent(agentId: string) {
    setSelectedAgents((prev) => {
      const next = new Set(prev);
      if (next.has(agentId)) {
        // Don't allow deselecting all agents
        if (next.size <= 1) return prev;
        next.delete(agentId);
      } else {
        next.add(agentId);
      }
      return next;
    });
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!topic.trim() || selectedAgents.size === 0) return;

    setStatus('loading');
    setMessage('');

    const formData = new FormData();
    formData.append('topic', topic);
    formData.append('participants', Array.from(selectedAgents).join(','));
    formData.append('num_rounds', String(numRounds));

    try {
      const result = await triggerSpecialSession(formData);

      if (result.error) {
        setStatus('error');
        setMessage(result.error);
      } else {
        setStatus('success');
        setMessage(`Fire Team launched! ${selectedAgents.size} agents, ${numRounds} rounds. Check GitHub/Telegram.`);
        setTopic('');
        setTimeout(() => setStatus('idle'), 5000);
      }
    } catch (err) {
      setStatus('error');
      setMessage('An unexpected error occurred');
    }
  }

  return (
    <div className="glass-card rounded-2xl p-4 sm:p-6 mb-6 sm:mb-8 border border-primary/20 bg-primary/5">
      <h2 className="text-lg sm:text-xl font-bold mb-4 flex items-center gap-2 text-primary">
        <Zap className="w-5 h-5" />
        Fire Team Meeting
      </h2>
      <p className="text-xs text-muted-foreground mb-4">
        Launch a focused team session with configurable agents and rounds (2-13).
      </p>

      <form onSubmit={handleSubmit} className="space-y-4">
        {/* Topic / Agenda */}
        <div>
          <label className="block text-xs font-medium text-muted-foreground mb-1">
            Agenda / Topic
          </label>
          <input
            type="text"
            name="topic"
            value={topic}
            onChange={(e) => setTopic(e.target.value)}
            placeholder="e.g., 'Implement hybrid search in discovery.py'"
            className="w-full p-2 rounded bg-background/50 border border-border focus:border-primary focus:ring-1 focus:ring-primary outline-none text-sm"
            disabled={status === 'loading'}
          />
        </div>

        {/* Agent Selection */}
        <div>
          <label className="block text-xs font-medium text-muted-foreground mb-2">
            Participants
          </label>
          <div className="grid grid-cols-2 gap-2">
            {AGENTS.map((agent) => {
              const isSelected = selectedAgents.has(agent.id);
              return (
                <button
                  key={agent.id}
                  type="button"
                  onClick={() => toggleAgent(agent.id)}
                  disabled={status === 'loading'}
                  className={`flex items-center gap-2 p-2 rounded border text-xs transition-colors text-left ${
                    isSelected
                      ? 'border-primary bg-primary/10 text-primary'
                      : 'border-border bg-background/30 text-muted-foreground hover:border-primary/50'
                  } disabled:opacity-50`}
                >
                  <span
                    className={`w-3 h-3 rounded-sm border flex-shrink-0 flex items-center justify-center ${
                      isSelected ? 'bg-primary border-primary' : 'border-muted-foreground'
                    }`}
                  >
                    {isSelected && (
                      <svg className="w-2 h-2 text-primary-foreground" viewBox="0 0 12 12" fill="none">
                        <path d="M2 6l3 3 5-5" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                      </svg>
                    )}
                  </span>
                  <span className="flex flex-col leading-tight">
                    <span className="font-medium">{agent.label}</span>
                    <span className="text-[10px] text-muted-foreground">{agent.role}</span>
                  </span>
                </button>
              );
            })}
          </div>
        </div>

        {/* Round Count */}
        <div>
          <label className="block text-xs font-medium text-muted-foreground mb-1">
            Rounds: <span className="text-primary font-bold">{numRounds}</span>
          </label>
          <input
            type="range"
            min={2}
            max={13}
            value={numRounds}
            onChange={(e) => setNumRounds(parseInt(e.target.value, 10))}
            disabled={status === 'loading'}
            className="w-full accent-primary"
          />
          <div className="flex justify-between text-[10px] text-muted-foreground mt-0.5">
            <span>2 (quick)</span>
            <span>7 (standard)</span>
            <span>13 (deep)</span>
          </div>
        </div>

        {/* Submit */}
        <button
          type="submit"
          disabled={status === 'loading' || !topic.trim() || selectedAgents.size === 0}
          className="w-full py-2 px-4 rounded bg-primary hover:bg-primary/90 text-primary-foreground font-medium text-sm transition-colors flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {status === 'loading' ? (
            <>
              <Loader2 className="w-4 h-4 animate-spin" />
              Launching...
            </>
          ) : (
            <>
              <Zap className="w-4 h-4" />
              Launch Fire Team ({selectedAgents.size} agents, {numRounds} rounds)
            </>
          )}
        </button>
      </form>

      {message && (
        <div className={`mt-3 text-xs p-2 rounded ${
          status === 'success' ? 'bg-green-500/10 text-green-400' : 'bg-red-500/10 text-red-400'
        }`}>
          {message}
        </div>
      )}
    </div>
  );
}
