import { ParticleBackground } from '@/components/particle-background';
import { ProductionOverview } from '@/components/production/overview';
import { RecentMeetings } from '@/components/production/recent-meetings';
import { InvestigationProgress } from '@/components/production/investigation-progress';
import { ActivityFeed } from '@/components/production/activity-feed';
import { SpecialSessionButton } from '@/components/special-session-button';
import fs from 'fs';
import path from 'path';

export const dynamic = 'force-dynamic';

export default function DashboardPage() {
  // Read production data
  let productionData = null;
  let lastUpdated = 'Never';

  try {
    const dataPath = path.join(process.cwd(), 'src/content/production.json');
    if (fs.existsSync(dataPath)) {
      const fileContent = fs.readFileSync(dataPath, 'utf-8');
      productionData = JSON.parse(fileContent);
      lastUpdated = new Date(productionData.lastUpdated).toLocaleString('en-US', {
        month: 'short',
        day: 'numeric',
        hour: 'numeric',
        minute: '2-digit',
      });
    }
  } catch (error) {
    console.error('Error reading production data:', error);
  }

  const meetings = productionData?.meetings || [];

  return (
    <div className="min-h-screen bg-background relative overflow-hidden">
      {/* Particle Background - only on desktop */}
      <div className="hidden lg:block">
        <ParticleBackground />
      </div>

      <div className="container mx-auto p-4 sm:p-6 max-w-7xl relative z-10">
        {/* Header */}
        <header className="mb-8 sm:mb-12">
          <h1
            className="text-4xl sm:text-5xl md:text-6xl font-black text-glitch neon-pulse"
            data-text="PRODUCTION DASHBOARD"
          >
            PRODUCTION DASHBOARD
          </h1>
          <p className="text-muted-foreground mt-2 text-sm sm:text-base">
            Real-time AI team activity and output metrics
          </p>
          <div className="mt-2 text-xs font-mono text-primary/60">
            Last sync: {lastUpdated}
          </div>
        </header>

        {/* Metrics Grid */}
        <ProductionOverview />

        {/* Two-column layout */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 sm:gap-8 mt-8 sm:mt-12">
          {/* Left Column: Recent Activity */}
          <div className="lg:col-span-8 space-y-6 sm:space-y-8">
            <section className="glass-card rounded-2xl p-4 sm:p-6 scan-lines">
              <h2 className="text-xl sm:text-2xl font-bold mb-4 sm:mb-6 flex items-center gap-2">
                <span className="text-primary">▸</span>
                Recent Meetings
              </h2>
              <RecentMeetings meetings={meetings} />
            </section>

            <section className="glass-card rounded-2xl p-4 sm:p-6">
              <h2 className="text-xl sm:text-2xl font-bold mb-4 sm:mb-6 flex items-center gap-2">
                <span className="text-primary">▸</span>
                Activity Feed
              </h2>
              <ActivityFeed />
            </section>
          </div>

          {/* Right Column: Status Panels */}
          <div className="lg:col-span-4 space-y-6 sm:space-y-8">
            <SpecialSessionButton />
            <section className="glass-card rounded-2xl p-4 sm:p-6">
              <h2 className="text-lg sm:text-xl font-bold mb-4 sm:mb-6 flex items-center gap-2">
                <span className="text-primary">▸</span>
                Investigation Status
              </h2>
              <InvestigationProgress />
            </section>

            {/* Quick Links */}
            <section className="glass-card rounded-2xl p-4 sm:p-6">
              <h2 className="text-lg sm:text-xl font-bold mb-4 flex items-center gap-2">
                <span className="text-primary">▸</span>
                Quick Access
              </h2>
              <div className="space-y-3">
                <a
                  href="/team"
                  className="block p-3 rounded-lg bg-secondary/30 hover:bg-primary/10 transition-colors text-sm"
                >
                  <span className="font-semibold">Team →</span>
                  <p className="text-xs text-muted-foreground mt-1">
                    View agent profiles and status
                  </p>
                </a>
                <a
                  href="/research"
                  className="block p-3 rounded-lg bg-secondary/30 hover:bg-primary/10 transition-colors text-sm"
                >
                  <span className="font-semibold">Research →</span>
                  <p className="text-xs text-muted-foreground mt-1">
                    Browse all research briefs
                  </p>
                </a>
                <a
                  href="/projects"
                  className="block p-3 rounded-lg bg-secondary/30 hover:bg-primary/10 transition-colors text-sm"
                >
                  <span className="font-semibold">Projects →</span>
                  <p className="text-xs text-muted-foreground mt-1">
                    View active projects
                  </p>
                </a>
              </div>
            </section>
          </div>
        </div>

        {/* Footer Note */}
        <div className="mt-12 text-center text-xs text-muted-foreground font-mono">
          <p>BPR&D Production Dashboard • Built with Next.js & AI Collaboration</p>
        </div>
      </div>
    </div>
  );
}
