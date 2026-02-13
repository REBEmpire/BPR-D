import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card"

export default function SplintermatedPage() {
  return (
    <div className="container mx-auto p-8">
      <h1 className="text-4xl font-bold mb-8">Splintermated</h1>
      <Card>
        <CardHeader>
          <CardTitle>Project Status: Active</CardTitle>
        </CardHeader>
        <CardContent>
          <p>Automated splinter cell research and deployment operations.</p>
          <div className="mt-8 border-t pt-4">
            <h3 className="font-semibold mb-2">Roadmap</h3>
            <ul className="list-disc list-inside text-muted-foreground">
              <li>Phase 1: Concept (Done)</li>
              <li>Phase 2: Prototype (In Progress)</li>
              <li>Phase 3: Deployment</li>
            </ul>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
