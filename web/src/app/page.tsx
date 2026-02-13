import { QuestBoard } from "@/components/quest-board"

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
            <li>Review Team Progress</li>
            <li>Check n8n Workflow Status</li>
            <li>Read Latest Research Briefs</li>
          </ul>
        </div>
      </div>
    </div>
  )
}
