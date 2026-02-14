import { QuestBoard } from "@/components/quest-board"
import { Leaderboard } from "@/components/gamification/leaderboard"
import Link from "next/link"
import { ArrowRight, ExternalLink, Activity, Radio, ShieldCheck, Sparkles } from "lucide-react"

export const dynamic = 'force-dynamic';

export default function Home() {
  return (
    <div className="min-h-screen bg-background text-foreground bg-grid-pattern relative overflow-hidden">
      {/* Decorative gradient overlay */}
      <div className="absolute inset-0 bg-gradient-to-b from-background via-transparent to-background pointer-events-none" />

      <main className="container mx-auto p-6 md:p-12 max-w-7xl relative z-10">

        {/* Header Section */}
        <header className="flex flex-col gap-4 mb-12 animate-in slide-in-from-top-4 duration-700 fade-in">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-primary/10 border border-primary/20 w-fit text-primary text-xs font-mono uppercase tracking-wider mb-2">
            <span className="relative flex h-2 w-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-primary opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2 w-2 bg-primary"></span>
            </span>
            System Online
          </div>
          <h1 className="text-5xl md:text-6xl font-black tracking-tighter text-transparent bg-clip-text bg-gradient-to-r from-white via-primary to-purple-400 drop-shadow-[0_0_15px_rgba(0,255,255,0.3)]">
            BPR&D NEXUS
          </h1>
          <p className="text-muted-foreground text-lg md:text-xl max-w-2xl font-light">
             Broad Perspective Research & Development. <span className="text-primary/80">Exploring the fringe, questioning the narrative.</span>
          </p>
        </header>

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">

          {/* Left Column: Active Quests & Navigation (8 cols) */}
          <div className="lg:col-span-8 space-y-10">

            {/* Quests Section */}
            <section className="animate-in slide-in-from-left-4 duration-700 delay-100 fade-in">
              <div className="flex items-center gap-3 mb-6">
                <Sparkles className="h-6 w-6 text-yellow-400" />
                <h2 className="text-3xl font-bold tracking-tight">Active Directives</h2>
              </div>
              <div className="bg-card/30 backdrop-blur-sm border border-border/50 rounded-2xl p-1 shadow-lg shadow-black/20">
                 <QuestBoard />
              </div>
            </section>

            {/* Quick Access Grid */}
            <section className="animate-in slide-in-from-bottom-4 duration-700 delay-200 fade-in">
              <h2 className="text-xl font-semibold mb-6 text-muted-foreground uppercase tracking-widest text-sm">Operational Access</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                 {[
                   { href: "/team", label: "Agent Roster", icon: ShieldCheck, desc: "Review team progress & status" },
                   { href: "/projects", label: "Active Projects", icon: Activity, desc: "Ongoing deep dives & dev work" },
                   { href: "/research", label: "Intelligence Briefs", icon: Radio, desc: "Daily synthesis & analysis" },
                   { href: "/resources", label: "Field Resources", icon: ExternalLink, desc: "Tools, links, and assets" },
                 ].map((item, i) => (
                   <Link key={i} href={item.href}
                         className="group flex flex-col p-5 bg-card/40 border border-primary/10 rounded-xl hover:bg-primary/5 hover:border-primary/40 transition-all duration-300 relative overflow-hidden">
                      <div className="absolute inset-0 bg-gradient-to-r from-transparent via-primary/5 to-transparent translate-x-[-100%] group-hover:translate-x-[100%] transition-transform duration-1000" />
                      <div className="flex items-center justify-between mb-2">
                        <item.icon className="h-6 w-6 text-primary/80 group-hover:text-primary transition-colors" />
                        <ArrowRight className="h-4 w-4 text-muted-foreground group-hover:translate-x-1 group-hover:text-primary transition-all" />
                      </div>
                      <span className="font-bold text-lg group-hover:text-primary transition-colors">{item.label}</span>
                      <span className="text-sm text-muted-foreground">{item.desc}</span>
                   </Link>
                 ))}
              </div>
            </section>
          </div>

          {/* Right Column: Leaderboard & Status (4 cols) */}
          <div className="lg:col-span-4 space-y-8 animate-in slide-in-from-right-4 duration-700 delay-300 fade-in">
             <div className="sticky top-8 space-y-8">

               {/* Leaderboard */}
               <div className="shadow-2xl shadow-primary/5 rounded-xl overflow-hidden ring-1 ring-border">
                  <Leaderboard />
               </div>

               {/* System Status Card */}
               <div className="bg-black/40 backdrop-blur-md rounded-xl p-6 border border-primary/20 relative overflow-hidden">
                  <div className="absolute -right-10 -top-10 h-32 w-32 bg-primary/20 rounded-full blur-3xl pointer-events-none" />

                  <h3 className="font-bold text-primary mb-4 flex items-center gap-2">
                    <Activity className="h-5 w-5" />
                    System Status
                  </h3>

                  <div className="space-y-4">
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-muted-foreground">Neural Link</span>
                      <span className="text-green-400 font-mono text-xs bg-green-400/10 px-2 py-0.5 rounded">STABLE</span>
                    </div>
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-muted-foreground">Encryption</span>
                      <span className="text-primary font-mono text-xs bg-primary/10 px-2 py-0.5 rounded">AES-256</span>
                    </div>
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-muted-foreground">Agent Morale</span>
                      <span className="text-purple-400 font-mono text-xs bg-purple-400/10 px-2 py-0.5 rounded">OPTIMAL</span>
                    </div>
                  </div>

                  <div className="mt-6 pt-4 border-t border-white/5">
                    <p className="text-xs text-muted-foreground font-mono">
                      Latest Sync: ONLINE
                    </p>
                  </div>
               </div>

             </div>
          </div>

        </div>
      </main>
    </div>
  )
}
