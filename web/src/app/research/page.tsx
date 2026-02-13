import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { FileText } from "lucide-react"

const TOPICS = [
  "Ancient Religions & Lost Civilizations",
  "Corruption Investigation",
  "Extraterrestrial",
  "Great Works & Writing",
  "High Tech",
  "History & Archaeology",
  "Norse Mythology",
  "Open Lanes",
  "Permaculture",
]

export default function ResearchPage() {
  return (
    <div className="container mx-auto p-8">
      <h1 className="text-4xl font-bold mb-8">Research Programs</h1>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {TOPICS.map((topic, i) => (
          <Card key={i} className="hover:bg-muted/50 transition-colors">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <FileText className="h-5 w-5 text-muted-foreground" />
                {topic}
              </CardTitle>
            </CardHeader>
            <CardContent>
              <Badge variant="outline">Active Research</Badge>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  )
}
