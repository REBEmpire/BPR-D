import Link from "next/link"
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { ArrowRight } from "lucide-react"

const PROJECTS = [
  {
    id: "splintermated",
    title: "Splintermated",
    description: "Automated splinter cell research and deployment.",
    status: "Active",
    href: "/projects/splintermated",
  },
  {
    id: "decentralized-arts-studio",
    title: "Decentralized Arts Studio",
    description: "Web3 enabled creative studio infrastructure.",
    status: "Planning",
    href: "/projects/decentralized-arts-studio",
  },
  {
    id: "ai-comm-hub",
    title: "AI Communications Hub",
    description: "Central n8n automation and communication relay.",
    status: "Live",
    href: "/projects/ai-comm-hub",
  },
]

export default function ProjectsPage() {
  return (
    <div className="container mx-auto p-8">
      <h1 className="text-4xl font-bold mb-8">Projects</h1>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {PROJECTS.map((project) => (
          <Link key={project.id} href={project.href}>
            <Card className="h-full hover:bg-muted/50 transition-colors cursor-pointer group">
              <CardHeader>
                <div className="flex justify-between items-start">
                  <CardTitle className="group-hover:text-primary transition-colors">{project.title}</CardTitle>
                  <Badge variant={project.status === "Live" ? "default" : "secondary"}>
                    {project.status}
                  </Badge>
                </div>
              </CardHeader>
              <CardContent>
                <CardDescription className="mb-4">{project.description}</CardDescription>
                <div className="flex items-center text-sm font-medium text-primary">
                  View Project <ArrowRight className="ml-2 h-4 w-4" />
                </div>
              </CardContent>
            </Card>
          </Link>
        ))}
      </div>
    </div>
  )
}
