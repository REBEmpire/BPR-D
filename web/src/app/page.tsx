import { QuestBoard } from "@/components/quest-board"
import { Leaderboard } from "@/components/gamification/leaderboard"
import Link from "next/link"
import { ArrowRight, ExternalLink } from "lucide-react"

export const dynamic = 'force-dynamic';

export default function Home() {
  return (
    <div className="container mx-auto p-8 max-w-7xl">
      <div className="flex flex-col gap-2 mb-8">
        <h1 className="text-4xl font-bold tracking-tight">BPR&D Dashboard</h1>
        <p className="text-muted-foreground text-lg">
           Operational status and mission objectives.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">

        {/* Main Column: Active Quests & Projects */}
        <div className="lg:col-span-2 space-y-8">
          <section>
            <h2 className="text-2xl font-semibold mb-4 flex items-center gap-2">
              <span>Active Quests</span>
            </h2>
            <QuestBoard />
          </section>

          <section className="bg-muted/30 rounded-xl p-6 border border-border/50">
            <h2 className="text-xl font-semibold mb-4">Quick Access</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
               <Link href="/team" className="flex items-center justify-between p-4 bg-background border rounded-lg hover:border-primary transition-colors group">
                  <span className="font-medium">Review Team Progress</span>
                  <ArrowRight className="h-4 w-4 text-muted-foreground group-hover:translate-x-1 transition-transform" />
               </Link>
               <Link href="/projects" className="flex items-center justify-between p-4 bg-background border rounded-lg hover:border-primary transition-colors group">
                  <span className="font-medium">Project Status</span>
                  <ArrowRight className="h-4 w-4 text-muted-foreground group-hover:translate-x-1 transition-transform" />
               </Link>
               <Link href="/research" className="flex items-center justify-between p-4 bg-background border rounded-lg hover:border-primary transition-colors group">
                  <span className="font-medium">Intelligence Briefs</span>
                  <ArrowRight className="h-4 w-4 text-muted-foreground group-hover:translate-x-1 transition-transform" />
               </Link>
               <Link href="/resources" className="flex items-center justify-between p-4 bg-background border rounded-lg hover:border-primary transition-colors group">
                  <span className="font-medium">Field Resources</span>
                  <ArrowRight className="h-4 w-4 text-muted-foreground group-hover:translate-x-1 transition-transform" />
               </Link>
            </div>
          </section>
        </div>

        {/* Sidebar: Leaderboard */}
        <div className="space-y-6">
           <Leaderboard />

           <div className="bg-primary/5 rounded-xl p-6 border border-primary/20">
              <h3 className="font-semibold text-primary mb-2 flex items-center gap-2">
                <ExternalLink className="h-4 w-4" />
                System Status
              </h3>
              <p className="text-sm text-muted-foreground mb-4">
                All systems nominal. Compliance automation active. Research syncing daily.
              </p>
              <div className="flex items-center gap-2 text-xs font-mono text-muted-foreground">
                 <div className="h-2 w-2 rounded-full bg-green-500 animate-pulse" />
                 <span>Connected to Neural Network</span>
              </div>
           </div>
        </div>
      </div>
    </div>
  )
}
