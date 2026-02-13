import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card"

export default function DASPage() {
  return (
    <div className="container mx-auto p-8">
      <h1 className="text-4xl font-bold mb-8">Decentralized Arts Studio</h1>
      <Card>
        <CardHeader>
          <CardTitle>Project Status: Planning</CardTitle>
        </CardHeader>
        <CardContent>
          <p>Web3 enabled creative studio infrastructure.</p>
          <div className="mt-8 border-t pt-4">
            <h3 className="font-semibold mb-2">Roadmap</h3>
            <ul className="list-disc list-inside text-muted-foreground">
              <li>Phase 1: Ideation (Done)</li>
              <li>Phase 2: Architecture (Pending)</li>
            </ul>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
