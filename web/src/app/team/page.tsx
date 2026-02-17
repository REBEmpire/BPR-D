/* eslint-disable @typescript-eslint/no-explicit-any */
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import Link from "next/link"
import agentsData from '@/content/agents.json'
import metricsData from '@/content/metrics.json'
import { query } from "@/lib/db"
import fs from 'fs'
import path from 'path'
import AgentStatus from './AgentStatus'
import AgentMetrics, { ChiefMetrics } from './AgentMetrics'

export const dynamic = 'force-dynamic';

export default async function TeamPage() {
  // Fetch points for agents
  let pointsMap: Record<string, number> = {};
  let userPoints = 0;

  try {
    const pointsRes = await query(`SELECT slug, points FROM agents`);
    pointsMap = pointsRes.rows.reduce((acc: any, row: any) => {
      acc[row.slug] = row.points;
      return acc;
    }, {});

    // Fetch user points (assuming single user for now or 'Chief')
    // We haven't seeded 'Chief' yet, so let's just query users table.
    const userRes = await query(`SELECT points FROM users LIMIT 1`);
    if (userRes.rows.length > 0) {
        userPoints = userRes.rows[0].points;
    }
  } catch (err) {
    console.warn('Database error fetching points:', err);
  }

  // Read agent status from production data
  const agentStatusMap: Record<string, { status: string; model: string }> = {};
  try {
    const dataPath = path.join(process.cwd(), 'src/content/production.json');
    if (fs.existsSync(dataPath)) {
      const fileContent = fs.readFileSync(dataPath, 'utf-8');
      const data = JSON.parse(fileContent);
      if (data.teamState?.agentStatus) {
        data.teamState.agentStatus.forEach((agent: any) => {
          const slug = agent.name.toLowerCase();
          agentStatusMap[slug] = {
            status: agent.status,
            model: agent.model
          };
        });
      }
    }
  } catch (err) {
    console.warn('Error reading agent status:', err);
  }

  // Add points and status to agents
  const agents = (agentsData as any[]).map((agent: any) => ({
    ...agent,
    points: pointsMap[agent.slug] || 0,
    status: agentStatusMap[agent.slug]?.status || 'Unknown',
    model: agentStatusMap[agent.slug]?.model || agent.role,
    handoffContent: agent.handoffContent || '',
    activeContent: agent.activeContent || ''
  }));

  const chief = {
    name: 'The Chief',
    slug: 'chief',
    role: 'Commander',
    points: userPoints,
  };

  // Load metrics
  const agentMetrics = (metricsData as any)?.agents || {};
  const russellMetrics = (metricsData as any)?.russell || {};

  return (
    <div className="container mx-auto p-8 max-w-7xl">
      <div className="flex flex-col gap-2 mb-12">
        <h1 className="text-4xl font-bold tracking-tight">BPR&D Team</h1>
        <p className="text-muted-foreground text-lg">
          Active agents and command structure.
        </p>
      </div>

      {/* Chief Card */}
      <div className="mb-12">
        <Card className="bg-gradient-to-r from-primary/10 to-transparent border-primary/20">
          <CardHeader>
             <div className="flex justify-between items-center">
                 <CardTitle className="text-2xl">The Chief</CardTitle>
                 <Badge variant="default" className="text-lg px-3 py-1">
                    Level {Math.floor(chief.points / 100) + 1}
                 </Badge>
             </div>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-4">
                <div className="text-4xl font-mono font-bold">{chief.points}</div>
                <div className="text-sm text-muted-foreground uppercase tracking-wider">Total XP</div>
            </div>
            <div className="mt-4 text-sm text-muted-foreground">
                Next Level: {((Math.floor(chief.points / 100) + 1) * 100) - chief.points} XP needed
            </div>
            {/* Chief Quest Score */}
            <ChiefMetrics metrics={russellMetrics} />
          </CardContent>
        </Card>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {agents.map((agent: any) => {
          const isOperational = agent.status.includes('OPERATIONAL');
          const statusColor = isOperational ? 'text-green-400' : 'text-muted-foreground';
          const statusDot = isOperational ? 'bg-green-400' : 'bg-gray-500';

          return (
            <div key={agent.slug} className="group h-full">
              <Card className="h-full hover:border-primary transition-all duration-300 overflow-hidden flex flex-col holo-border group-hover:shadow-lg group-hover:shadow-primary/20">
                <Link href={`/team/${agent.slug}`} className="block flex-grow-0">
                  <div className="aspect-[9/16] md:aspect-video bg-muted relative overflow-hidden">
                    {/* Status Indicator */}
                    <div className="absolute top-3 right-3 z-10 flex items-center gap-2 px-2 py-1 rounded-full bg-black/60 backdrop-blur-sm">
                      <span className="relative flex h-2 w-2">
                        {isOperational && (
                          <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
                        )}
                        <span className={`relative inline-flex rounded-full h-2 w-2 ${statusDot}`}></span>
                      </span>
                      <span className={`text-xs font-mono font-semibold ${statusColor}`}>
                        {isOperational ? 'ONLINE' : 'PAUSED'}
                      </span>
                    </div>

                    {agent.videoUrl ? (
                      <video
                        src={agent.videoUrl}
                        className="w-full h-full object-cover transition-transform group-hover:scale-105"
                        muted
                        loop
                        autoPlay
                        playsInline
                      />
                    ) : (
                      <div className="w-full h-full flex items-center justify-center text-muted-foreground bg-secondary/20">
                        No Signal
                      </div>
                    )}
                    <div className="absolute bottom-0 w-full bg-gradient-to-t from-black/80 to-transparent p-4 pt-12">
                       <div className="flex justify-between items-end">
                          <Badge variant="secondary" className="bg-primary text-primary-foreground hover:bg-primary/90 neon-pulse">
                             {agent.points} XP
                          </Badge>
                       </div>
                    </div>
                  </div>
                <CardHeader>
                  <CardTitle className="capitalize">{agent.name}</CardTitle>
                  <div className="space-y-2">
                    <Badge variant="outline" className="w-fit">{agent.role}</Badge>
                    {agent.model && (
                      <p className="text-xs text-muted-foreground font-mono">{agent.model}</p>
                    )}
                  </div>
                </CardHeader>
                </Link>

                {/* Agent Performance Metrics */}
                {agentMetrics[agent.slug] && (
                  <AgentMetrics
                    metrics={agentMetrics[agent.slug]}
                    agentName={agent.name}
                  />
                )}

                {/* Agent Status View - Rendered Client Side */}
                <div className="mt-auto">
                    <AgentStatus
                        handoff={agent.handoffContent}
                        active={agent.activeContent}
                    />
                </div>
              </Card>
            </div>
          );
        })}
      </div>
    </div>
  )
}
