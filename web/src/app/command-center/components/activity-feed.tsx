'use client';

import { useState, useEffect } from 'react';
import { MessageSquare, Calendar, CheckSquare, FolderKanban, Zap } from 'lucide-react';

interface Activity {
  id: number;
  action_type: string;
  description: string;
  agent_name: string | null;
  created_at: string;
}

const ACTION_ICONS: Record<string, React.ReactNode> = {
  chat: <MessageSquare className="w-4 h-4" />,
  meeting: <Calendar className="w-4 h-4" />,
  task: <CheckSquare className="w-4 h-4" />,
  project: <FolderKanban className="w-4 h-4" />,
  default: <Zap className="w-4 h-4" />
};

const ACTION_COLORS: Record<string, string> = {
  chat: 'text-cyan-400',
  meeting: 'text-amber-400',
  task: 'text-purple-400',
  project: 'text-blue-400',
  default: 'text-slate-400'
};

export function ActivityFeed() {
  const [activities, setActivities] = useState<Activity[]>([]);

  useEffect(() => {
    fetchActivities();
    const interval = setInterval(fetchActivities, 30000);
    return () => clearInterval(interval);
  }, []);

  const fetchActivities = async () => {
    try {
      const res = await fetch('/api/command-center/activity');
      const data = await res.json();
      setActivities(data.activities || []);
    } catch (err) {
      console.error('Failed to fetch activities:', err);
    }
  };

  const formatTime = (dateStr: string) => {
    const date = new Date(dateStr);
    const now = new Date();
    const diff = now.getTime() - date.getTime();
    const mins = Math.floor(diff / 60000);
    const hours = Math.floor(diff / 3600000);
    const days = Math.floor(diff / 86400000);

    if (mins < 1) return 'just now';
    if (mins < 60) return `${mins}m ago`;
    if (hours < 24) return `${hours}h ago`;
    return `${days}d ago`;
  };

  const getIcon = (type: string) => ACTION_ICONS[type] || ACTION_ICONS.default;
  const getColor = (type: string) => ACTION_COLORS[type] || ACTION_COLORS.default;

  return (
    <div className="h-full flex flex-col">
      <div className="p-4 border-b border-purple-500/20">
        <h3 className="font-semibold flex items-center gap-2">
          <Zap className="w-4 h-4 text-cyan-400" />
          Activity Stream
        </h3>
      </div>

      <div className="flex-1 overflow-auto p-4 space-y-3">
        {activities.length === 0 ? (
          <div className="text-center py-8 text-muted-foreground">
            <span className="text-2xl block mb-2">🌸</span>
            <p className="text-sm">No recent activity</p>
          </div>
        ) : (
          activities.map(activity => (
            <div
              key={activity.id}
              className="flex items-start gap-3 p-3 bg-black/20 rounded-lg border border-purple-500/10 hover:border-purple-500/30 transition-colors"
            >
              <div className={`mt-0.5 ${getColor(activity.action_type)}`}>
                {getIcon(activity.action_type)}
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm">{activity.description}</p>
                <div className="flex items-center gap-2 mt-1">
                  {activity.agent_name && (
                    <span className="text-xs text-purple-400">{activity.agent_name}</span>
                  )}
                  <span className="text-xs text-muted-foreground">
                    {formatTime(activity.created_at)}
                  </span>
                </div>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
