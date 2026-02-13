import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card"
import { Database, FolderOpen, ScrollText } from "lucide-react"

const RESOURCES = [
  {
    title: "Memories & Sessions",
    description: "Historical context and past session logs.",
    icon: ScrollText,
  },
  {
    title: "Skills & Knowledge",
    description: "Shared skill library and knowledge base.",
    icon: Database,
  },
  {
    title: "Handoffs",
    description: "Active task handoffs and status reports.",
    icon: FolderOpen,
  },
]

export default function ResourcesPage() {
  return (
    <div className="container mx-auto p-8">
      <h1 className="text-4xl font-bold mb-8">Shared Resources</h1>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {RESOURCES.map((res, i) => (
          <Card key={i}>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <res.icon className="h-5 w-5 text-primary" />
                {res.title}
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-muted-foreground">{res.description}</p>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  )
}
