'use client';

import { MessageSquare, Calendar, CheckSquare, FolderKanban } from 'lucide-react';
import type { ViewType } from '../page';

interface CommandSidebarProps {
  activeView: ViewType;
  setActiveView: (view: ViewType) => void;
}

const NAV_ITEMS: { id: ViewType; label: string; icon: React.ReactNode; color: string }[] = [
  { id: 'chat', label: 'Agent Chat', icon: <MessageSquare className="w-5 h-5" />, color: 'text-cyan-400' },
  { id: 'meetings', label: 'Meetings', icon: <Calendar className="w-5 h-5" />, color: 'text-amber-400' },
  { id: 'tasks', label: 'Tasks', icon: <CheckSquare className="w-5 h-5" />, color: 'text-purple-400' },
  { id: 'projects', label: 'Projects', icon: <FolderKanban className="w-5 h-5" />, color: 'text-blue-400' }
];

export function CommandSidebar({ activeView, setActiveView }: CommandSidebarProps) {
  return (
    <aside className="w-64 border-r border-purple-500/20 bg-black/40 backdrop-blur-sm flex flex-col">
      <div className="p-4 border-b border-purple-500/20">
        <div className="flex items-center gap-2">
          <span className="text-xl">⚗️</span>
          <span className="text-sm font-semibold text-purple-300">Operations</span>
        </div>
      </div>

      <nav className="flex-1 p-4 space-y-2">
        {NAV_ITEMS.map((item) => (
          <button
            key={item.id}
            onClick={() => setActiveView(item.id)}
            className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg transition-all ${
              activeView === item.id
                ? `bg-white/10 ${item.color} border border-current/30`
                : 'text-slate-400 hover:text-white hover:bg-white/5'
            }`}
          >
            {item.icon}
            <span className="font-medium">{item.label}</span>
          </button>
        ))}
      </nav>

      <div className="p-4 border-t border-purple-500/20">
        <div className="text-xs text-muted-foreground space-y-1">
          <div className="flex items-center justify-between">
            <span>Transmutation</span>
            <span className="text-emerald-400">Active</span>
          </div>
          <div className="flex items-center justify-between">
            <span>Agents Online</span>
            <span className="text-cyan-400">4/4</span>
          </div>
        </div>
      </div>
    </aside>
  );
}
