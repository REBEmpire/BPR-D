'use client';

import { CC_AGENT_LIST } from '@/lib/command-center-agents';

export function CommandHeader() {
  return (
    <header className="h-16 border-b border-purple-500/20 bg-black/40 backdrop-blur-sm flex items-center justify-between px-6">
      <div className="flex items-center gap-4">
        <div className="flex items-center gap-2">
          <span className="text-2xl">🜃</span>
          <h1 className="text-xl font-bold bg-gradient-to-r from-purple-400 via-cyan-400 to-amber-400 bg-clip-text text-transparent">
            BPR&D Command Center
          </h1>
        </div>
        <div className="text-xs text-muted-foreground flex items-center gap-2">
          <span className="opacity-50">🜂🜁🜄🜨</span>
          <span>Transmutation Chamber Active</span>
        </div>
      </div>

      <div className="flex items-center gap-4">
        {/* Agent Status Indicators */}
        <div className="flex items-center gap-2">
          {CC_AGENT_LIST.map((agent) => (
            <div
              key={agent.id}
              className={`flex items-center gap-1 px-2 py-1 rounded-full ${agent.bgColor} ${agent.borderColor} border`}
              title={`${agent.name} - ${agent.role}`}
            >
              <span className="text-sm">{agent.icon}</span>
              <span className={`text-xs font-medium ${agent.color}`}>{agent.name}</span>
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
            </div>
          ))}
        </div>

        {/* Faction Indicator */}
        <div className="flex items-center gap-2 text-xs text-muted-foreground">
          <span className="text-amber-400">🜂 Visionaries</span>
          <span className="text-slate-500">|</span>
          <span className="text-cyan-400">🜁 Truth-Seekers</span>
        </div>
      </div>
    </header>
  );
}
