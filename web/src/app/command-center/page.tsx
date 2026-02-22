'use client';

import { useState } from 'react';
import { CommandHeader } from './components/command-header';
import { CommandSidebar } from './components/command-sidebar';
import { ChatInterface } from './components/chat-interface';
import { MeetingControl } from './components/meeting-control';
import { TaskDashboard } from './components/task-dashboard';
import { ProjectsOverview } from './components/projects-overview';
import { ActivityFeed } from './components/activity-feed';

export type ViewType = 'chat' | 'meetings' | 'tasks' | 'projects';

export default function CommandCenterPage() {
  const [activeView, setActiveView] = useState<ViewType>('chat');

  const renderMainContent = () => {
    switch (activeView) {
      case 'chat':
        return <ChatInterface />;
      case 'meetings':
        return <MeetingControl />;
      case 'tasks':
        return <TaskDashboard />;
      case 'projects':
        return <ProjectsOverview />;
      default:
        return <ChatInterface />;
    }
  };

  return (
    <div className="min-h-screen bg-[hsl(270,50%,5%)] text-white">
      {/* Alchemical ambient effects */}
      <div className="fixed inset-0 pointer-events-none overflow-hidden">
        <div className="absolute top-0 left-1/4 w-96 h-96 bg-purple-500/5 rounded-full blur-3xl animate-pulse" />
        <div className="absolute bottom-0 right-1/4 w-96 h-96 bg-cyan-500/5 rounded-full blur-3xl animate-pulse delay-1000" />
      </div>

      <div className="relative z-10 flex h-screen">
        {/* Sidebar */}
        <CommandSidebar activeView={activeView} setActiveView={setActiveView} />

        {/* Main Content */}
        <div className="flex-1 flex flex-col overflow-hidden">
          <CommandHeader />
          
          <div className="flex-1 flex overflow-hidden">
            {/* Main Area */}
            <div className="flex-1 p-6 overflow-auto">
              {renderMainContent()}
            </div>

            {/* Activity Feed */}
            <div className="w-80 border-l border-purple-500/20 bg-black/20">
              <ActivityFeed />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
