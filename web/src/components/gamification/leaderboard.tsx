/* eslint-disable @typescript-eslint/no-explicit-any */
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card"
import { query } from "@/lib/db"
import { Badge } from "@/components/ui/badge"
import { Trophy } from "lucide-react"
import { RavenIcon, ProfessorIcon, ShadowIcon } from "@/components/icons/custom-icons"

function getIconForAgent(name: string) {
  if (!name) return null;
  const lower = name.toLowerCase();
  if (lower.includes('grok') || lower.includes('chief')) return <RavenIcon className="h-4 w-4" />;
  if (lower.includes('claude') || lower.includes('professor')) return <ProfessorIcon className="h-4 w-4" />;
  if (lower.includes('abacus') || lower.includes('deep')) return <ShadowIcon className="h-4 w-4" />;
  return null;
}

export async function Leaderboard() {
  let leaders: any[] = [];
  try {
    const res = await query(`
      SELECT name, points, 'agent' as type FROM agents
      UNION ALL
      SELECT name, points, 'user' as type FROM users
      ORDER BY points DESC
      LIMIT 5
    `);
    leaders = res.rows;
  } catch (e) {
    console.warn("Failed to load leaderboard", e);
    // Mock data for demo if DB fails or is empty
    leaders = [
      { name: 'Grok (Chief)', points: 1250, type: 'agent' },
      { name: 'Claude', points: 980, type: 'agent' },
      { name: 'Abacus', points: 850, type: 'agent' },
      { name: 'Gemini', points: 720, type: 'agent' },
      { name: 'User-1', points: 450, type: 'user' }
    ];
  }

  return (
    <Card className="h-full border-primary/20 bg-card/50 backdrop-blur-sm relative overflow-hidden">
      <div className="absolute inset-0 bg-gradient-to-br from-primary/5 via-transparent to-transparent pointer-events-none" />
      <CardHeader className="pb-2 relative z-10">
        <div className="flex items-center gap-2">
            <Trophy className="h-5 w-5 text-primary animate-pulse" />
            <CardTitle className="text-primary tracking-tight">Top Agents</CardTitle>
        </div>
      </CardHeader>
      <CardContent className="relative z-10">
        <ul className="space-y-3 pt-2">
          {leaders.length === 0 ? (
            <li className="text-muted-foreground text-center text-sm py-4">No data available</li>
          ) : (
            leaders.map((leader: any, i: number) => {
               const icon = leader.type === 'agent' ? getIconForAgent(leader.name) : null;
               return (
              <li key={i}
                  className="flex justify-between items-center p-2 rounded-lg bg-background/40 border border-transparent hover:border-primary/20 transition-all duration-300 hover:scale-[1.02] group"
              >
                <div className="flex items-center gap-3">
                  <span className={`font-mono w-6 text-center rounded text-sm ${
                      i === 0 ? 'text-yellow-400 font-bold drop-shadow-[0_0_8px_rgba(250,204,21,0.5)]' :
                      i === 1 ? 'text-zinc-400' :
                      i === 2 ? 'text-amber-600' :
                      'text-muted-foreground'
                  }`}>
                    {i + 1}
                  </span>

                  <div className="flex items-center gap-2">
                      {icon && <span className="text-primary/80 group-hover:text-primary transition-colors">{icon}</span>}
                      <span className="font-medium truncate max-w-[100px] md:max-w-[150px] text-sm group-hover:text-primary transition-colors">
                        {leader.name}
                      </span>
                  </div>

                  {leader.type === 'agent' && (
                    <Badge variant="outline" className="text-[10px] h-4 px-1 border-primary/30 text-primary/70">AI</Badge>
                  )}
                </div>
                <span className="font-mono font-bold text-sm text-primary">{leader.points} XP</span>
              </li>
            )})
          )}
        </ul>
      </CardContent>
    </Card>
  )
}
