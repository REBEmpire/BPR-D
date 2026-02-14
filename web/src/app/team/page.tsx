/* eslint-disable @typescript-eslint/no-explicit-any */
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import Link from "next/link"
import agentsData from '@/content/agents.json'
import { query } from "@/lib/db"

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

  // Add points to agents
  const agents = (agentsData as any[]).map((agent: any) => ({
    ...agent,
    points: pointsMap[agent.slug] || 0
  }));

  const chief = {
    name: 'The Chief',
    slug: 'chief',
    role: 'Commander',
    points: userPoints,
  };

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
          </CardContent>
        </Card>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {agents.map((agent: any) => (
          <Link href={`/team/${agent.slug}`} key={agent.slug} className="group">
            <Card className="h-full hover:border-primary transition-colors cursor-pointer overflow-hidden flex flex-col">
                <div className="aspect-[9/16] md:aspect-video bg-muted relative overflow-hidden">
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
                        <Badge variant="secondary" className="bg-primary text-primary-foreground hover:bg-primary/90">
                           {agent.points} XP
                        </Badge>
                     </div>
                  </div>
                </div>
              <CardHeader>
                <CardTitle className="capitalize">{agent.name}</CardTitle>
                <Badge variant="outline" className="w-fit">{agent.role}</Badge>
              </CardHeader>
            </Card>
          </Link>
        ))}
      </div>
    </div>
  )
}
