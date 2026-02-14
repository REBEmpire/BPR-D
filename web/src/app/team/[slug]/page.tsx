/* eslint-disable @typescript-eslint/no-explicit-any */
import { getAgent } from "@/lib/agents"
import { query } from "@/lib/db"
import { notFound } from "next/navigation"
import { Badge } from "@/components/ui/badge"
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card"
import { ArrowLeft } from "lucide-react"
import Link from "next/link"

export const dynamic = 'force-dynamic';

interface PageProps {
  params: Promise<{
    slug: string;
  }>
}

export default async function AgentProfile({ params }: PageProps) {
  const { slug } = await params;
  const agent = await getAgent(slug);

  if (!agent) notFound();

  // Fetch stats
  let points = 0;
  let logs: any[] = [];

  try {
    // Get points
    const pointsRes = await query('SELECT points FROM agents WHERE slug = ', [slug]);
    if (pointsRes.rows.length > 0) {
      points = pointsRes.rows[0].points;
    }

    // Get recent logs (quests)
    // Logs join agents on entity_id
    const logsRes = await query(`
      SELECT l.description, l.points, l.timestamp
      FROM logs l
      JOIN agents a ON l.entity_id = a.id
      WHERE a.slug =  AND l.entity_type = 'agent'
      ORDER BY l.timestamp DESC
      LIMIT 10
    `, [slug]);
    logs = logsRes.rows;
  } catch (err) {
    console.warn('DB error:', err);
  }

  return (
    <div className="container mx-auto p-8 max-w-6xl">
       <Link
        href="/team"
        className="group inline-flex items-center gap-2 text-sm font-medium text-muted-foreground hover:text-foreground mb-8 transition-colors no-underline"
      >
        <ArrowLeft className="h-4 w-4 group-hover:-translate-x-1 transition-transform" />
        Back to Team
      </Link>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">

        {/* Left Column: Video & Stats */}
        <div className="lg:col-span-1 space-y-6">
          <Card className="overflow-hidden border-primary/20 bg-muted/5">
            <div className="aspect-[9/16] bg-black relative">
               {agent.videoUrl ? (
                 <video
                   src={agent.videoUrl}
                   className="w-full h-full object-cover"
                   muted
                   loop
                   autoPlay
                   playsInline
                 />
               ) : (
                 <div className="flex items-center justify-center h-full text-muted-foreground">No Video Signal</div>
               )}
            </div>
            <CardContent className="pt-6">
              <div className="text-center">
                <h1 className="text-3xl font-bold capitalize mb-2">{agent.name}</h1>
                <Badge variant="outline" className="mb-6 px-3 py-1 text-sm">{agent.role}</Badge>

                <div className="grid grid-cols-2 gap-4 text-center border-t border-border pt-6">
                  <div>
                    <div className="text-4xl font-mono font-bold text-primary">{points}</div>
                    <div className="text-xs uppercase tracking-widest text-muted-foreground mt-1">XP</div>
                  </div>
                  <div>
                    <div className="text-4xl font-mono font-bold text-primary">{logs.length}</div>
                    <div className="text-xs uppercase tracking-widest text-muted-foreground mt-1">Quests</div>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Right Column: Bio & Logs */}
        <div className="lg:col-span-2 space-y-8">

          {/* Bio */}
          <Card>
            <CardHeader>
               <CardTitle>Dossier</CardTitle>
            </CardHeader>
            <CardContent>
               <div className="prose dark:prose-invert max-w-none prose-sm sm:prose-base prose-headings:mb-2 prose-p:my-3" dangerouslySetInnerHTML={{ __html: agent.bio }} />
            </CardContent>
          </Card>

          {/* Recent Quests */}
          <Card>
            <CardHeader>
              <CardTitle>Recent Activity Log</CardTitle>
            </CardHeader>
            <CardContent>
              <ul className="space-y-0 divide-y divide-border">
                {logs.length === 0 ? (
                  <li className="py-4 text-muted-foreground text-center italic">No quests recorded in the database yet.</li>
                ) : (
                  logs.map((log, i) => (
                    <li key={i} className="flex justify-between items-center py-3 first:pt-0 last:pb-0">
                      <div>
                        <p className="font-medium text-sm md:text-base">{log.description}</p>
                        <p className="text-xs text-muted-foreground font-mono">
                          {new Date(log.timestamp).toLocaleDateString()}
                        </p>
                      </div>
                      <Badge variant="secondary" className="ml-4 whitespace-nowrap">+{log.points} XP</Badge>
                    </li>
                  ))
                )}
              </ul>
            </CardContent>
          </Card>

        </div>
      </div>
    </div>
  )
}
