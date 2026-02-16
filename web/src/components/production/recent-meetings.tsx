'use client';

import { useState } from 'react';
import { Calendar, Users, ChevronDown, ChevronUp } from 'lucide-react';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

interface Meeting {
  fileName: string;
  date: string;
  type: string;
  facilitator: string | null;
  attendees: string;
  participants: string[];
  insightsCount: number;
  insights: string[];
  actionItemsCount: number;
  actionItems: Array<{
    assignee: string;
    task: string;
    priority: string;
  }>;
  handoffsCount: number;
  handoffs: Array<{
    to: string;
    task: string;
  }>;
}

interface RecentMeetingsProps {
  meetings: Meeting[];
}

export function RecentMeetings({ meetings }: RecentMeetingsProps) {
  const [expandedMeeting, setExpandedMeeting] = useState<string | null>(null);

  const toggleMeeting = (fileName: string) => {
    setExpandedMeeting(expandedMeeting === fileName ? null : fileName);
  };

  const getPriorityColor = (priority: string) => {
    const p = priority.toLowerCase();
    if (p.includes('high') || p.includes('critical')) return 'destructive';
    if (p.includes('medium')) return 'default';
    return 'secondary';
  };

  if (meetings.length === 0) {
    return (
      <div className="text-center py-12 text-muted-foreground">
        <Calendar className="w-12 h-12 mx-auto mb-4 opacity-50" />
        <p>No meetings recorded yet</p>
        <p className="text-sm mt-2">
          First automated meeting scheduled for Feb 15, 2026 at 07:47 AM PST
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {meetings.slice(0, 5).map((meeting) => (
        <Card key={meeting.fileName} className="glass-card">
          <CardHeader
            className="cursor-pointer hover:bg-primary/5 transition-colors"
            onClick={() => toggleMeeting(meeting.fileName)}
          >
            <div className="flex items-start justify-between">
              <div className="space-y-2 flex-1">
                <CardTitle className="text-lg flex items-center gap-2">
                  <Calendar className="w-4 h-4 text-primary" />
                  {meeting.type}
                </CardTitle>
                <div className="flex flex-wrap gap-2 text-sm text-muted-foreground">
                  <span className="flex items-center gap-1">
                    <Users className="w-3 h-3" />
                    {meeting.participants.length} participants
                  </span>
                  <span>•</span>
                  <span>{meeting.date}</span>
                  {meeting.facilitator && (
                    <>
                      <span>•</span>
                      <span>Led by {meeting.facilitator}</span>
                    </>
                  )}
                </div>
                <div className="flex gap-2 flex-wrap">
                  {meeting.insightsCount > 0 && (
                    <Badge variant="outline" className="text-xs">
                      {meeting.insightsCount} insights
                    </Badge>
                  )}
                  {meeting.actionItemsCount > 0 && (
                    <Badge variant="outline" className="text-xs">
                      {meeting.actionItemsCount} action items
                    </Badge>
                  )}
                  {meeting.handoffsCount > 0 && (
                    <Badge variant="outline" className="text-xs text-primary">
                      {meeting.handoffsCount} handoffs
                    </Badge>
                  )}
                </div>
              </div>
              <button className="text-muted-foreground hover:text-foreground transition-colors">
                {expandedMeeting === meeting.fileName ? (
                  <ChevronUp className="w-5 h-5" />
                ) : (
                  <ChevronDown className="w-5 h-5" />
                )}
              </button>
            </div>
          </CardHeader>

          {expandedMeeting === meeting.fileName && (
            <CardContent className="space-y-6 border-t border-border/50 pt-6">
              {/* Insights */}
              {meeting.insights.length > 0 && (
                <div>
                  <h4 className="font-semibold mb-3 text-sm uppercase tracking-wider text-primary">
                    Key Insights
                  </h4>
                  <ul className="space-y-2">
                    {meeting.insights.map((insight, idx) => (
                      <li key={idx} className="text-sm flex gap-2">
                        <span className="text-primary mt-1">•</span>
                        <span>{insight}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Action Items */}
              {meeting.actionItems.length > 0 && (
                <div>
                  <h4 className="font-semibold mb-3 text-sm uppercase tracking-wider text-primary">
                    Action Items
                  </h4>
                  <div className="space-y-3">
                    {meeting.actionItems.map((item, idx) => (
                      <div
                        key={idx}
                        className="flex items-start gap-3 p-3 rounded-lg bg-secondary/30"
                      >
                        <Badge variant={getPriorityColor(item.priority)}>
                          {item.priority}
                        </Badge>
                        <div className="flex-1">
                          <p className="text-sm font-medium">{item.task}</p>
                          <p className="text-xs text-muted-foreground mt-1">
                            Assigned to: {item.assignee}
                          </p>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Handoffs */}
              {meeting.handoffs.length > 0 && (
                <div>
                  <h4 className="font-semibold mb-3 text-sm uppercase tracking-wider text-primary">
                    Handoffs
                  </h4>
                  <div className="space-y-2">
                    {meeting.handoffs.map((handoff, idx) => (
                      <div
                        key={idx}
                        className="flex items-start gap-2 text-sm p-3 rounded-lg bg-primary/10 border border-primary/20"
                      >
                        <span className="font-semibold text-primary">
                          → {handoff.to}:
                        </span>
                        <span>{handoff.task}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </CardContent>
          )}
        </Card>
      ))}
    </div>
  );
}
