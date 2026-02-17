'use client'

import { useState } from 'react'
import ReactMarkdown from 'react-markdown'

export default function AgentStatus({ handoff, active }: { handoff: string, active: string }) {
  const [showHandoff, setShowHandoff] = useState(true);

  return (
    <div className="mt-2 p-3 border-t border-border/50 bg-background/50" onClick={(e) => e.preventDefault()}>
      <div className="flex gap-2 mb-2">
        <button
          onClick={(e) => {
            e.preventDefault();
            e.stopPropagation();
            setShowHandoff(true);
          }}
          className={`px-3 py-1 text-xs font-medium rounded-full transition-colors ${showHandoff ? 'bg-primary text-primary-foreground' : 'bg-muted text-muted-foreground hover:bg-muted/80'}`}
        >
          Handoff
        </button>
        <button
          onClick={(e) => {
            e.preventDefault();
            e.stopPropagation();
            setShowHandoff(false);
          }}
          className={`px-3 py-1 text-xs font-medium rounded-full transition-colors ${!showHandoff ? 'bg-primary text-primary-foreground' : 'bg-muted text-muted-foreground hover:bg-muted/80'}`}
        >
          Active Context
        </button>
      </div>

      <div className="h-48 overflow-y-auto rounded-md border border-border/50 bg-muted/30 p-3 text-xs leading-relaxed scrollbar-thin scrollbar-thumb-primary/20 hover:scrollbar-thumb-primary/40 text-muted-foreground/80 prose prose-xs prose-invert max-w-none [&_table]:w-full [&_table]:text-xs [&_th]:px-2 [&_th]:py-1 [&_th]:text-left [&_th]:border-b [&_th]:border-border/50 [&_td]:px-2 [&_td]:py-1 [&_td]:border-b [&_td]:border-border/30">
        <ReactMarkdown>
          {showHandoff ? (handoff || "No handoff instructions available.") : (active || "No active context available.")}
        </ReactMarkdown>
      </div>
    </div>
  )
}
