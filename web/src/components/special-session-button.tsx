'use client';

import { useState } from 'react';
import { triggerSpecialSession } from '@/app/actions/special-session';
import { Loader2, Zap } from 'lucide-react';

export function SpecialSessionButton() {
  const [topic, setTopic] = useState('');
  const [status, setStatus] = useState<'idle' | 'loading' | 'success' | 'error'>('idle');
  const [message, setMessage] = useState('');

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!topic.trim()) return;

    setStatus('loading');
    setMessage('');

    const formData = new FormData();
    formData.append('topic', topic);

    try {
      const result = await triggerSpecialSession(formData);

      if (result.error) {
        setStatus('error');
        setMessage(result.error);
      } else {
        setStatus('success');
        setMessage('Session triggered! Check GitHub/Telegram.');
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
        Special Session
      </h2>
      <p className="text-xs text-muted-foreground mb-4">
        Trigger a 4-5 turn deep dive workflow on a specific topic.
      </p>

      <form onSubmit={handleSubmit} className="space-y-3">
        <input
          type="text"
          name="topic"
          value={topic}
          onChange={(e) => setTopic(e.target.value)}
          placeholder="Enter topic (e.g., 'Neuralink update')..."
          className="w-full p-2 rounded bg-background/50 border border-border focus:border-primary focus:ring-1 focus:ring-primary outline-none text-sm"
          disabled={status === 'loading'}
        />

        <button
          type="submit"
          disabled={status === 'loading' || !topic.trim()}
          className="w-full py-2 px-4 rounded bg-primary hover:bg-primary/90 text-primary-foreground font-medium text-sm transition-colors flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {status === 'loading' ? (
            <>
              <Loader2 className="w-4 h-4 animate-spin" />
              Triggering...
            </>
          ) : (
            'Trigger Workflow'
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
