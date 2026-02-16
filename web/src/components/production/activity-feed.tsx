import { FileText, Users, Target, Calendar } from 'lucide-react';
import { Badge } from '@/components/ui/badge';
import fs from 'fs';
import path from 'path';

interface Activity {
  type: 'meeting' | 'brief' | 'investigation' | 'handoff';
  title: string;
  description: string;
  timestamp: string;
  agent?: string;
  category?: string;
}

export function ActivityFeed() {
  // Read production data
  let activities: Activity[] = [];

  try {
    const dataPath = path.join(process.cwd(), 'src/content/production.json');
    if (fs.existsSync(dataPath)) {
      const fileContent = fs.readFileSync(dataPath, 'utf-8');
      const data = JSON.parse(fileContent);

      // Convert meetings to activities
      data.meetings?.forEach((meeting: any) => {
        activities.push({
          type: 'meeting',
          title: meeting.type,
          description: `${meeting.participants.length} participants, ${meeting.insightsCount} insights`,
          timestamp: meeting.date,
          agent: meeting.facilitator || 'Team',
        });
      });

      // Add recent research briefs
      data.researchMetrics?.recentBriefs?.slice(0, 5).forEach((brief: any) => {
        activities.push({
          type: 'brief',
          title: brief.title,
          description: `Published in ${brief.category}`,
          timestamp: brief.date,
          category: brief.category,
        });
      });

      // Add investigation milestones
      data.investigationMetrics?.phases?.forEach((phase: any) => {
        if (phase.status.toUpperCase().includes('COMPLETE')) {
          activities.push({
            type: 'investigation',
            title: `${phase.name} Complete`,
            description: `Phase ${phase.number} completed`,
            timestamp: new Date().toISOString().split('T')[0], // Approximate date
          });
        }
      });
    }
  } catch (error) {
    console.error('Error reading activity feed:', error);
  }

  // Sort by timestamp descending
  activities.sort((a, b) => b.timestamp.localeCompare(a.timestamp));

  // Take only recent activities
  activities = activities.slice(0, 10);

  const getActivityIcon = (type: string) => {
    switch (type) {
      case 'meeting':
        return Users;
      case 'brief':
        return FileText;
      case 'investigation':
        return Target;
      default:
        return Calendar;
    }
  };

  const getActivityColor = (type: string) => {
    switch (type) {
      case 'meeting':
        return 'text-cyan-400';
      case 'brief':
        return 'text-purple-400';
      case 'investigation':
        return 'text-primary';
      default:
        return 'text-muted-foreground';
    }
  };

  const formatTimestamp = (timestamp: string) => {
    try {
      const date = new Date(timestamp);
      const now = new Date();
      const diffInSeconds = Math.floor((now.getTime() - date.getTime()) / 1000);

      if (diffInSeconds < 60) return 'Just now';
      if (diffInSeconds < 3600) return `${Math.floor(diffInSeconds / 60)}m ago`;
      if (diffInSeconds < 86400) return `${Math.floor(diffInSeconds / 3600)}h ago`;
      if (diffInSeconds < 604800) return `${Math.floor(diffInSeconds / 86400)}d ago`;

      return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
    } catch {
      return timestamp;
    }
  };

  if (activities.length === 0) {
    return (
      <div className="text-center py-8 text-muted-foreground">
        <Calendar className="w-10 h-10 mx-auto mb-3 opacity-50" />
        <p className="text-sm">No recent activity</p>
      </div>
    );
  }

  return (
    <div className="space-y-1 scan-lines">
      {activities.map((activity, idx) => {
        const Icon = getActivityIcon(activity.type);
        const colorClass = getActivityColor(activity.type);

        return (
          <div
            key={idx}
            className="flex items-start gap-3 p-3 rounded-lg hover:bg-secondary/30 transition-colors group"
          >
            <div className={`p-2 rounded-lg bg-secondary/50 ${colorClass}`}>
              <Icon className="w-4 h-4" />
            </div>

            <div className="flex-1 min-w-0">
              <div className="flex items-start justify-between gap-2">
                <p className="text-sm font-medium truncate">{activity.title}</p>
                <span className="text-xs text-muted-foreground whitespace-nowrap font-mono">
                  {formatTimestamp(activity.timestamp)}
                </span>
              </div>
              <p className="text-xs text-muted-foreground mt-1">
                {activity.description}
              </p>
              {activity.agent && (
                <Badge variant="outline" className="mt-2 text-xs">
                  {activity.agent}
                </Badge>
              )}
            </div>
          </div>
        );
      })}
    </div>
  );
}
