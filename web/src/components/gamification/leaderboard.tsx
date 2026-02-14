/* eslint-disable @typescript-eslint/no-explicit-any */
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card"
import { query } from "@/lib/db"
import { Badge } from "@/components/ui/badge"
import { Trophy } from "lucide-react"

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
  }

  return (
    <Card className="h-full">
      <CardHeader className="pb-2">
        <div className="flex items-center gap-2">
            <Trophy className="h-5 w-5 text-yellow-500" />
            <CardTitle>Leaderboard</CardTitle>
        </div>
      </CardHeader>
      <CardContent>
        <ul className="space-y-4 pt-4">
          {leaders.length === 0 ? (
            <li className="text-muted-foreground text-center">No data available</li>
          ) : (
            leaders.map((leader: any, i: number) => (
              <li key={i} className="flex justify-between items-center border-b pb-2 last:border-0 last:pb-0">
                <div className="flex items-center gap-3">
                  <span className={`font-mono w-6 text-center rounded ${
                      i === 0 ? 'bg-yellow-500/20 text-yellow-600 dark:text-yellow-400 font-bold' :
                      i === 1 ? 'bg-zinc-400/20 text-zinc-600 dark:text-zinc-400' :
                      i === 2 ? 'bg-amber-700/20 text-amber-700 dark:text-amber-500' :
                      'text-muted-foreground'
                  }`}>
                    {i + 1}
                  </span>
                  <span className="font-medium truncate max-w-[120px] md:max-w-[200px]">{leader.name}</span>
                  {leader.type === 'agent' && <Badge variant="secondary" className="text-[10px] h-4 px-1">AI</Badge>}
                </div>
                <span className="font-mono font-bold">{leader.points} XP</span>
              </li>
            ))
          )}
        </ul>
      </CardContent>
    </Card>
  )
}
