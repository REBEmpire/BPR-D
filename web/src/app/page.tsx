import { QuestBoard } from "@/components/quest-board"
import Link from "next/link"

export default function Home() {
  return (
    <div className="container mx-auto p-8">
      <h1 className="text-4xl font-bold mb-8">BPR&D Dashboard</h1>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        <div className="space-y-6">
          <QuestBoard />
        </div>
        <div className="bg-muted/50 rounded-lg p-6">
          <h2 className="text-2xl font-bold mb-4">Quick Links</h2>
          <ul className="list-disc list-inside space-y-2">
            <li>
              <Link href="/team" className="hover:underline hover:text-primary transition-colors">
                Review Team Progress
              </Link>
            </li>
            <li>
              <Link href="/projects/ai-comm-hub" className="hover:underline hover:text-primary transition-colors">
                Check n8n Workflow Status
              </Link>
            </li>
            <li>
              <Link href="/research" className="hover:underline hover:text-primary transition-colors">
                Read Latest Research Briefs
              </Link>
            </li>
          </ul>
        </div>
      </div>
    </div>
  )
}
