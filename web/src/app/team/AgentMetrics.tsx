'use client'

import { useState } from 'react'

type WindowKey = '24h' | '48h' | '7d' | '30d';

interface WindowMetrics {
  costUsd: number;
  costPerHr: number;
  durationMs: number;
  tokens: number;
  sessions: number;
  questScore: number;
  questBreakdown: {
    output: number;
    milestones: number;
    efficiency: number;
    initiative: number;
    total: number;
  };
}

interface AgentMetricsProps {
  metrics: Record<WindowKey, WindowMetrics>;
  agentName: string;
}

const WINDOWS: { key: WindowKey; label: string }[] = [
  { key: '24h', label: '24h' },
  { key: '48h', label: '48h' },
  { key: '7d', label: '1W' },
  { key: '30d', label: '1M' },
];

function formatDuration(ms: number): string {
  if (ms === 0) return '0s';
  if (ms < 1000) return `${ms}ms`;
  if (ms < 60000) return `${(ms / 1000).toFixed(1)}s`;
  if (ms < 3600000) return `${(ms / 60000).toFixed(1)}m`;
  return `${(ms / 3600000).toFixed(1)}h`;
}

function formatCost(cost: number): string {
  if (cost === 0) return '$0.00';
  if (cost < 0.01) return `$${cost.toFixed(4)}`;
  return `$${cost.toFixed(2)}`;
}

function getScoreColor(score: number): string {
  if (score >= 80) return 'text-green-400';
  if (score >= 60) return 'text-cyan-400';
  if (score >= 40) return 'text-yellow-400';
  return 'text-red-400';
}

function getBarColor(score: number): string {
  if (score >= 80) return 'bg-green-400';
  if (score >= 60) return 'bg-cyan-400';
  if (score >= 40) return 'bg-yellow-400';
  return 'bg-red-400';
}

export default function AgentMetrics({ metrics, agentName }: AgentMetricsProps) {
  const [window, setWindow] = useState<WindowKey>('7d');

  const data = metrics?.[window];
  if (!data) return null;

  const breakdown = data.questBreakdown;

  return (
    <div className="p-3 border-t border-border/50 bg-background/50" onClick={(e) => e.preventDefault()}>
      {/* Duration Toggle */}
      <div className="flex gap-1 mb-3">
        {WINDOWS.map((w) => (
          <button
            key={w.key}
            onClick={(e) => {
              e.preventDefault();
              e.stopPropagation();
              setWindow(w.key);
            }}
            className={`px-2 py-0.5 text-[10px] font-mono font-bold rounded-full transition-colors ${
              window === w.key
                ? 'bg-primary text-primary-foreground'
                : 'bg-muted text-muted-foreground hover:bg-muted/80'
            }`}
          >
            {w.label}
          </button>
        ))}
      </div>

      {/* Metrics Grid */}
      <div className="space-y-2">
        {/* $/hr Meter */}
        <div className="flex items-center gap-2">
          <span className="text-[10px] font-mono text-muted-foreground w-10 shrink-0">$/hr</span>
          <div className="flex-1 h-1.5 bg-secondary/30 rounded-full overflow-hidden">
            <div
              className="h-full bg-gradient-to-r from-primary/80 to-primary rounded-full transition-all duration-500"
              style={{ width: `${Math.min((data.costPerHr / 15) * 100, 100)}%` }}
            />
          </div>
          <span className="text-[10px] font-mono font-bold text-primary w-12 text-right">
            {formatCost(data.costPerHr)}
          </span>
        </div>

        {/* Active Time Meter */}
        <div className="flex items-center gap-2">
          <span className="text-[10px] font-mono text-muted-foreground w-10 shrink-0">TIME</span>
          <div className="flex-1 h-1.5 bg-secondary/30 rounded-full overflow-hidden">
            <div
              className="h-full bg-gradient-to-r from-purple-500/80 to-purple-400 rounded-full transition-all duration-500"
              style={{ width: `${Math.min((data.durationMs / 300000) * 100, 100)}%` }}
            />
          </div>
          <span className="text-[10px] font-mono font-bold text-purple-400 w-12 text-right">
            {formatDuration(data.durationMs)}
          </span>
        </div>

        {/* Quest Score */}
        <div className="flex items-center gap-2">
          <span className="text-[10px] font-mono text-muted-foreground w-10 shrink-0">QUEST</span>
          <div className="flex-1 h-1.5 bg-secondary/30 rounded-full overflow-hidden">
            <div
              className={`h-full rounded-full transition-all duration-500 ${getBarColor(data.questScore)}`}
              style={{ width: `${data.questScore}%` }}
            />
          </div>
          <span className={`text-[10px] font-mono font-bold w-12 text-right ${getScoreColor(data.questScore)}`}>
            {data.questScore}
          </span>
        </div>

        {/* Quest Breakdown (collapsed by default, expand on hover) */}
        <div className="group">
          <div className="hidden group-hover:flex gap-1 mt-1 flex-wrap">
            {[
              { key: 'output', label: 'OUT', value: breakdown.output },
              { key: 'milestones', label: 'MIL', value: breakdown.milestones },
              { key: 'efficiency', label: 'EFF', value: breakdown.efficiency },
              { key: 'initiative', label: 'INI', value: breakdown.initiative },
            ].map((dim) => (
              <span
                key={dim.key}
                className={`text-[9px] font-mono px-1.5 py-0.5 rounded bg-muted/50 ${getScoreColor(dim.value)}`}
              >
                {dim.label}:{dim.value}
              </span>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

/**
 * Simplified metrics display for the Chief card (Russell).
 * Shows only Quest Score with breakdown.
 */
export function ChiefMetrics({ metrics }: { metrics: Record<WindowKey, { questScore: number; questBreakdown: { output: number; milestones: number; efficiency: number; initiative: number; total: number } }> }) {
  const [window, setWindow] = useState<WindowKey>('7d');

  const data = metrics?.[window];
  if (!data) return null;

  const breakdown = data.questBreakdown;

  return (
    <div className="mt-4">
      {/* Duration Toggle */}
      <div className="flex gap-1 mb-3">
        {WINDOWS.map((w) => (
          <button
            key={w.key}
            onClick={() => setWindow(w.key)}
            className={`px-2 py-0.5 text-[10px] font-mono font-bold rounded-full transition-colors ${
              window === w.key
                ? 'bg-primary text-primary-foreground'
                : 'bg-muted text-muted-foreground hover:bg-muted/80'
            }`}
          >
            {w.label}
          </button>
        ))}
      </div>

      {/* Quest Score Bar */}
      <div className="flex items-center gap-3">
        <span className="text-sm font-mono text-muted-foreground">Quest Score</span>
        <div className="flex-1 h-2 bg-secondary/30 rounded-full overflow-hidden">
          <div
            className={`h-full rounded-full transition-all duration-500 ${getBarColor(data.questScore)}`}
            style={{ width: `${data.questScore}%` }}
          />
        </div>
        <span className={`text-lg font-mono font-black ${getScoreColor(data.questScore)}`}>
          {data.questScore}
        </span>
      </div>

      {/* Breakdown Pills */}
      <div className="flex gap-1.5 mt-2 flex-wrap">
        {[
          { key: 'output', label: 'Output', value: breakdown.output },
          { key: 'milestones', label: 'Milestones', value: breakdown.milestones },
          { key: 'efficiency', label: 'Efficiency', value: breakdown.efficiency },
          { key: 'initiative', label: 'Initiative', value: breakdown.initiative },
        ].map((dim) => (
          <span
            key={dim.key}
            className={`text-[10px] font-mono px-2 py-0.5 rounded-full bg-muted/50 border border-border/30 ${getScoreColor(dim.value)}`}
          >
            {dim.label}: {dim.value}
          </span>
        ))}
      </div>
    </div>
  );
}
